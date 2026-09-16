# coding=gbk
"""
A股多因子共振与布林带策略 - 盘中交易与持仓风控执行引擎
负责开盘补齐持仓、盘中实时监控、-7%硬止损、+15%/+30%分档止盈与动态保本、布林带中下轨出场
"""
import os
import json
import time
import datetime
from typing import Dict, Any, Optional
from xtquant import xtconstant, xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

from src.strategy.factors import compute_boll
from src.service.stock import get_realtime_price
from src.service.order import update_order
from src.service.positions import update_position
from src.service.trade import update_trade
from src.service.account import update_account
from src.config.config import get_qmt_cfg, get_account_cfg


class StrategyCallback(XtQuantTraderCallback):
    """交易回调处理类"""

    def on_disconnected(self):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 警告: 与 MiniQMT 客户端连接断开!")

    def on_stock_order(self, order):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 委托回报 -> 订单ID: {order.order_id}, 股票: {order.stock_code}, 状态: {order.order_status}, 描述: {order.status_msg}")
        try:
            update_order(order)
        except Exception as e:
            print(f"同步订单数据库失败: {e}")

    def on_stock_trade(self, trade):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 成交回报 -> 订单ID: {trade.order_id}, 股票: {trade.stock_code}, 成交价: {trade.traded_price}, 成交量: {trade.traded_volume}")
        try:
            update_trade(trade)
        except Exception as e:
            print(f"同步成交数据库失败: {e}")

    def on_order_error(self, order_error):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 委托下单失败 -> 订单ID: {order_error.order_id}, 错误信息: {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 撤单失败 -> 订单ID: {cancel_error.order_id}, 错误信息: {cancel_error.error_msg}")

    def on_account_status(self, status):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 账号状态变动 -> 账号: {status.account_id}, 状态码: {status.status}")


class BollRiskExecutor:
    """
    布林带持仓管理与风控执行引擎
    """

    def __init__(
        self,
        xt_trader: Optional[XtQuantTrader] = None,
        acc: Optional[StockAccount] = None,
        max_positions: int = 20,
        single_pos_ratio: float = 0.05,
        target_pool_path: str = 'data/target_pool.json'
    ):
        """
        初始化执行引擎

        Args:
            xt_trader (Optional[XtQuantTrader]): MiniQMT 客户端对象
            acc (Optional[StockAccount]): 证券资金账户
            max_positions (int): 最大持仓数量，默认20只
            single_pos_ratio (float): 单票建仓比例上限，默认5% (0.05)
            target_pool_path (str): 盘后选股候选池文件路径
        """
        self.xt_trader = xt_trader
        self.acc = acc
        self.max_positions = max_positions
        self.single_pos_ratio = single_pos_ratio
        self.target_pool_path = target_pool_path

        # 内存风控状态表：stock_code -> { 'cost_price': float, 'tp_stage': int, 'stop_price': float, 'last_order_time': float }
        # tp_stage: 0=未止盈, 1=已止盈1/2(15%), 2=已止盈3/4(30%)
        self.risk_states: Dict[str, Dict[str, Any]] = {}
        # 委托防重冷却时间（秒）
        self.order_cooldown_seconds = 10.0

    def connect_and_init(self):
        """连接 MiniQMT 客户端并初始化账户"""
        qmt_cfg = get_qmt_cfg()
        account_cfg = get_account_cfg()

        self.acc = StockAccount(account_cfg.stock_account, 'STOCK')
        session_id = int(time.time())
        self.xt_trader = XtQuantTrader(qmt_cfg.userdata_mini_path, session_id)

        callback = StrategyCallback()
        self.xt_trader.register_callback(callback)
        self.xt_trader.start()

        connect_res = self.xt_trader.connect()
        if connect_res != 0:
            raise ConnectionError(f"MiniQMT 客户端连接失败，错误码: {connect_res}")

        sub_res = self.xt_trader.subscribe(self.acc)
        if sub_res != 0:
            raise RuntimeError(f"资金账户订阅失败，错误码: {sub_res}")

        print(f"MiniQMT 连接与资金账户订阅成功: {self.acc.account_id}")

    def execute_morning_open_buying(self):
        """
        09:30 开盘执行建仓逻辑：根据盘后目标池补足空缺仓位至 max_positions (<=20)
        """
        if not os.path.exists(self.target_pool_path):
            print(f"[开盘买入] 未找到选股池文件: {self.target_pool_path}，跳过开盘建仓")
            return

        with open(self.target_pool_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        target_codes = data.get('target_codes', [])
        if not target_codes:
            print("[开盘买入] 选股目标池为空，无需建仓")
            return

        # 1. 查询当前持仓与资产
        positions = self.xt_trader.query_stock_positions(self.acc)
        try:
            update_position(positions)
        except Exception:
            pass

        held_codes = {p.stock_code for p in positions if p.volume > 0}
        vacant_count = self.max_positions - len(held_codes)

        if vacant_count <= 0:
            print(f"[开盘买入] 当前持仓已有 {len(held_codes)} 只，持仓已满 (上限 {self.max_positions} 只)，跳过开盘买入")
            return

        asset_info = self.xt_trader.query_stock_asset(self.acc)
        if not asset_info:
            print("[开盘买入] 查询账户资产失败，跳过买入")
            return

        try:
            update_account(asset_info)
        except Exception:
            pass

        total_asset = asset_info.total_asset
        available_cash = asset_info.cash
        target_cash_per_stock = total_asset * self.single_pos_ratio

        print(f"[开盘买入] 当前持仓 {len(held_codes)} 只，空缺仓位 {vacant_count} 只，总资产: {total_asset:.2f}，可用现金: {available_cash:.2f}")
        print(f"[开盘买入] 单票目标配置金额: {target_cash_per_stock:.2f}")

        bought_count = 0
        for code in target_codes:
            if code in held_codes:
                continue
            if bought_count >= vacant_count:
                break
            if available_cash < 5000.0:
                print("[开盘买入] 可用资金不足，终止建仓")
                break

            cur_price = get_realtime_price(code)
            if cur_price <= 0:
                print(f"[开盘买入] 标的 {code} 无法获取有效实时价格，跳过")
                continue

            # 计算整百股数量
            alloc_cash = min(target_cash_per_stock, available_cash)
            volume = int((alloc_cash / cur_price) // 100) * 100
            if volume < 100:
                print(f"[开盘买入] 标的 {code} 计算股数不足1手 (100股)，跳过")
                continue

            order_price = round(cur_price, 2)
            order_id = self.xt_trader.order_stock(
                account=self.acc,
                stock_code=code,
                order_type=xtconstant.STOCK_BUY,
                order_volume=volume,
                price_type=xtconstant.FIX_PRICE,
                price=order_price,
                strategy_name="ResonanceBoll",
                order_remark=f"开盘买入_{code}_{volume}股"
            )

            print(f"[开盘买入] 下单成功 -> 标的: {code}, 股数: {volume}, 限价: {order_price}, 订单ID: {order_id}")
            available_cash -= (volume * order_price)
            bought_count += 1
            time.sleep(0.2)  # 轻微延时避免密集冲刷柜台

    def check_and_execute_risk_control(self):
        """
        盘中实时轮询执行持仓风控与布林带策略：
        1. -7% 固定硬止损
        2. +15% / +30% 分档止盈与动态保本/止损线上移
        3. 布林带跌破中轨/下轨出场
        """
        positions = self.xt_trader.query_stock_positions(self.acc)
        if not positions:
            return

        now_ts = time.time()

        for pos in positions:
            if pos.volume <= 0 or pos.can_use_volume <= 0:
                continue

            code = pos.stock_code
            can_use_vol = pos.can_use_volume
            cost_price = pos.open_price if pos.open_price > 0 else pos.avg_price

            cur_price = get_realtime_price(code)
            if cur_price <= 0 or cost_price <= 0:
                continue

            # 检查委托防重冷却
            state = self.risk_states.get(code)
            if state is None:
                state = {
                    'cost_price': cost_price,
                    'tp_stage': 0,
                    'stop_price': round(cost_price * (1.0 - 0.07), 2),  # 初始硬止损 -7%
                    'last_order_time': 0.0
                }
                self.risk_states[code] = state

            if now_ts - state.get('last_order_time', 0.0) < self.order_cooldown_seconds:
                continue

            profit_ratio = (cur_price - cost_price) / cost_price

            # =========================================================================
            # 1. 固定止损 / 动态止损检查
            # =========================================================================
            if cur_price <= state['stop_price']:
                print(f"[风控触发-止损] {code} 触发止损 (现价: {cur_price} <= 止损线: {state['stop_price']})，立即清仓！")
                self.xt_trader.order_stock(
                    account=self.acc,
                    stock_code=code,
                    order_type=xtconstant.STOCK_SELL,
                    order_volume=can_use_vol,
                    price_type=xtconstant.LATEST_PRICE,
                    price=0,
                    strategy_name="ResonanceBoll",
                    order_remark="硬止损清仓"
                )
                state['last_order_time'] = now_ts
                self.risk_states.pop(code, None)
                continue

            # =========================================================================
            # 2. 分档止盈与动态保本调整
            # =========================================================================
            # 2.1 第一档止盈 (+15%)
            if profit_ratio >= 0.15 and state['tp_stage'] == 0:
                sell_vol = int((can_use_vol * 0.5) // 100) * 100
                if sell_vol == 0:
                    sell_vol = can_use_vol  # 若不足200股则全卖
                print(f"[风控触发-止盈1] {code} 盈利达 15% (当前收益: {profit_ratio*100:.2f}%)，卖出 1/2 仓位 ({sell_vol}股)")
                self.xt_trader.order_stock(
                    account=self.acc,
                    stock_code=code,
                    order_type=xtconstant.STOCK_SELL,
                    order_volume=sell_vol,
                    price_type=xtconstant.LATEST_PRICE,
                    price=0,
                    strategy_name="ResonanceBoll",
                    order_remark="第一止盈卖出1/2"
                )
                state['tp_stage'] = 1
                state['stop_price'] = round(cost_price * 1.03, 2)  # 止损线上调至 成本+3% (保本)
                state['last_order_time'] = now_ts
                print(f"[动态风控] {code} 止损线上调至保本价: {state['stop_price']}")
                continue

            # 2.2 第二档止盈 (+30%)
            elif profit_ratio >= 0.30 and state['tp_stage'] == 1:
                sell_vol = int((can_use_vol * 0.5) // 100) * 100
                if sell_vol == 0:
                    sell_vol = can_use_vol
                print(f"[风控触发-止盈2] {code} 盈利达 30% (当前收益: {profit_ratio*100:.2f}%)，再卖出 1/2 仓位 ({sell_vol}股)")
                self.xt_trader.order_stock(
                    account=self.acc,
                    stock_code=code,
                    order_type=xtconstant.STOCK_SELL,
                    order_volume=sell_vol,
                    price_type=xtconstant.LATEST_PRICE,
                    price=0,
                    strategy_name="ResonanceBoll",
                    order_remark="第二止盈卖出1/2"
                )
                state['tp_stage'] = 2
                state['stop_price'] = round(cost_price * 1.10, 2)  # 止损线上调至 成本+10% (锁定核心利润)
                state['last_order_time'] = now_ts
                print(f"[动态风控] {code} 止损线上调至锁定利润价: {state['stop_price']}")
                continue

            # =========================================================================
            # 3. 布林带 (BOLL) 持仓管理与出场
            # =========================================================================
            kline_data = xtdata.get_market_data_ex(
                field_list=['close'],
                stock_list=[code],
                period='1d',
                count=30
            )
            df = kline_data.get(code)
            if df is not None and len(df) >= 20:
                mid_s, up_s, low_s = compute_boll(df['close'], 20, 2.0)
                mid_val = mid_s.iloc[-1]
                low_val = low_s.iloc[-1]

                # 3.1 跌破下轨 -> 清仓离场
                if cur_price < low_val:
                    print(f"[布林破位-下轨] {code} 跌破下轨 (现价: {cur_price} < 下轨: {low_val:.2f})，清仓全部持仓 ({can_use_vol}股)")
                    self.xt_trader.order_stock(
                        account=self.acc,
                        stock_code=code,
                        order_type=xtconstant.STOCK_SELL,
                        order_volume=can_use_vol,
                        price_type=xtconstant.LATEST_PRICE,
                        price=0,
                        strategy_name="ResonanceBoll",
                        order_remark="布林跌破下轨清仓"
                    )
                    state['last_order_time'] = now_ts
                    self.risk_states.pop(code, None)
                    continue

                # 3.2 跌破中轨
                if cur_price < mid_val:
                    if state['tp_stage'] >= 1:
                        # 已进入分档止盈跟踪状态的剩余底仓，跌破中轨全部止盈
                        print(f"[布林止盈-中轨] {code} 止盈跟踪底仓跌破中轨 (现价: {cur_price} < 中轨: {mid_val:.2f})，全部卖出 ({can_use_vol}股)")
                        self.xt_trader.order_stock(
                            account=self.acc,
                            stock_code=code,
                            order_type=xtconstant.STOCK_SELL,
                            order_volume=can_use_vol,
                            price_type=xtconstant.LATEST_PRICE,
                            price=0,
                            strategy_name="ResonanceBoll",
                            order_remark="跌破中轨清底仓"
                        )
                        state['last_order_time'] = now_ts
                        self.risk_states.pop(code, None)
                    else:
                        # 正常持仓跌破中轨，减仓 1/2
                        sell_vol = int((can_use_vol * 0.5) // 100) * 100
                        if sell_vol > 0:
                            print(f"[布林减仓-中轨] {code} 跌破中轨 (现价: {cur_price} < 中轨: {mid_val:.2f})，减仓 1/2 ({sell_vol}股)")
                            self.xt_trader.order_stock(
                                account=self.acc,
                                stock_code=code,
                                order_type=xtconstant.STOCK_SELL,
                                order_volume=sell_vol,
                                price_type=xtconstant.LATEST_PRICE,
                                price=0,
                                strategy_name="ResonanceBoll",
                                order_remark="布林跌破中轨减半"
                            )
                            state['last_order_time'] = now_ts

    def run_trading_loop(self, poll_interval: int = 5):
        """
        盘中交易事件循环

        Args:
            poll_interval (int): 轮询检查时间间隔（秒），默认5秒
        """
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 启动盘中交易与风控监控循环...")
        print("按 Ctrl+C 终止运行")

        # 启动时执行一次开盘买入（如果在开盘时段）
        self.execute_morning_open_buying()

        try:
            while True:
                now = datetime.datetime.now()
                # 仅在 A 股交易时段执行风控 (09:30 - 11:30, 13:00 - 15:00)
                is_morning = datetime.time(9, 30) <= now.time() <= datetime.time(11, 30)
                is_afternoon = datetime.time(13, 0) <= now.time() <= datetime.time(15, 0)

                if is_morning or is_afternoon:
                    self.check_and_execute_risk_control()

                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\n盘中交易监控循环已停止")


if __name__ == "__main__":
    executor = BollRiskExecutor()
    executor.connect_and_init()
    executor.run_trading_loop()
