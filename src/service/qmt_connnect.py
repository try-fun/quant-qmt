# coding=gbk
import asyncio
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant, xtdata
import time
import datetime
from src.config.config import get_account_cfg, get_qmt_cfg
from src.service.account import update_account

# 初始化账号信息
acc = None
xt_trader = None


def init_account():
    stock_account = get_account_cfg().stock_account
    if not stock_account:
        raise ValueError("stock_account is 不能为空")

    print(f"初始化交易账号: {stock_account}")
    global acc
    acc = StockAccount(stock_account, 'STOCK')


def download_one_stock_data(stock: str, period='1d', start_date='', end_date='', count=1):

    import string

    if [i for i in ["d", "w", "mon", "q", "y",] if i in period]:
        period = "1d"
    elif "m" in period:
        numb = period.translate(str.maketrans("", "", string.ascii_letters))
        if int(numb) < 5:
            period = "1m"
        else:
            period = "5m"
    elif "tick" == period:
        pass
    else:
        raise KeyboardInterrupt("download stock data error")

    xtdata.download_history_data(stock, period, start_date, end_date)
    print(f"download {stock} {period} {start_date}~{end_date} success")


def get_current_price(stock_code):
    """
    获取股票当前时刻最新价格
    使用 get_market_data_ex 获取实时价格
    """
    try:
        # 获取当前日期
        today = datetime.datetime.now().strftime('%Y%m%d')

        download_one_stock_data(stock_code, 'tick', today, '', 1)

        # 使用 get_market_data_ex 获取当前时刻最新价格
        market_data = xtdata.get_market_data_ex(
            field_list=['lastPrice'],  # 最新价
            stock_list=[stock_code],  # 股票代码列表
            period='tick',  # 1分钟周期
            start_time=today,  # 开盘时间
            end_time='',  # 收盘时间
            count=1  # 获取最新1条数据
        )

        if market_data and stock_code in market_data and len(market_data[stock_code]) > 0:
            # 获取最新价格
            current_price = market_data[stock_code]['lastPrice'].iloc[-1]
            print(f"股票 {stock_code} 当前价格: {current_price}")
            return current_price
        else:
            print(f"无法获取股票 {stock_code} 的当前价格数据")
            return 0

    except Exception as e:
        print(f"获取股票 {stock_code} 当前价格时发生错误: {e}")
        return 0


def validate_buy_price(stock_code, buy_price, pre_close):
    """
    验证买入价格是否合理
    """
    if buy_price <= 0:
        return False, "价格无效"

    if pre_close and pre_close > 0:
        # 检查价格是否在合理范围内（前收盘价的±10%）
        price_change_ratio = abs(buy_price - pre_close) / pre_close
        if price_change_ratio > 0.1:
            return False, f"价格变化过大: {price_change_ratio:.2%}"

    return True, "价格合理"


'''
将指标生成bitmap推理交易结果
'''


class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        print("connection lost")

    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        '''
        xtconstant.ORDER_UNREPORTED	48	未报
        xtconstant.ORDER_WAIT_REPORTING	49	待报
        xtconstant.ORDER_REPORTED	50	已报
        xtconstant.ORDER_REPORTED_CANCEL	51	已报待撤
        xtconstant.ORDER_PARTSUCC_CANCEL	52	部成待撤
        xtconstant.ORDER_PART_CANCEL	53	部撤（已经有一部分成交，剩下的已经撤单）
        xtconstant.ORDER_CANCELED	54	已撤
        xtconstant.ORDER_PART_SUCC	55	部成（已经有一部分成交，剩下的待成交）
        xtconstant.ORDER_SUCCEEDED	56	已成
        xtconstant.ORDER_JUNK	57	废单
        xtconstant.ORDER_UNKNOWN	255	未知
        '''
        # 定义状态码与中文说明的映射
        status_map = {
            xtconstant.ORDER_UNREPORTED: "未报",
            xtconstant.ORDER_WAIT_REPORTING: "待报",
            xtconstant.ORDER_REPORTED: "已报",
            xtconstant.ORDER_REPORTED_CANCEL: "已报待撤",
            xtconstant.ORDER_PARTSUCC_CANCEL: "部成待撤",
            xtconstant.ORDER_PART_CANCEL: "部撤",
            xtconstant.ORDER_CANCELED: "已撤",
            xtconstant.ORDER_PART_SUCC: "部成",
            xtconstant.ORDER_SUCCEEDED: "已成",
            xtconstant.ORDER_JUNK: "废单",
            xtconstant.ORDER_UNKNOWN: "未知",
        }
        status_desc = status_map.get(order.order_status, "未知状态")
        print("on order callback:")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 订单ID: {order.order_id}, 股票代码: {order.stock_code}, 状态: {status_desc}, 系统ID: {order.order_sysid}")

    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        print("on trade callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 账号ID: {trade.account_id}, 股票代码: {trade.stock_code}, 订单ID: {trade.order_id}")

    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        print("on order_error callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 订单ID: {order_error.order_id}, 错误ID: {order_error.error_id}, 错误信息: {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print("on cancel_error callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 订单ID: {cancel_error.order_id}, 错误ID: {cancel_error.error_id}, 错误信息: {cancel_error.error_msg}")

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print("on_order_stock_async_response")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 账号ID: {response.account_id}, 订单ID: {response.order_id}, 序号: {response.seq}")

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus 对象
        :return:
        """
        print("on_account_status")
        # 定义状态码与中文说明的映射
        status_map = {
            xtconstant.ACCOUNT_STATUS_INVALID: "无效",
            xtconstant.ACCOUNT_STATUS_OK: "正常",
            xtconstant.ACCOUNT_STATUS_WAITING_LOGIN: "连接中",
            xtconstant.ACCOUNT_STATUSING: "登陆中",
            xtconstant.ACCOUNT_STATUS_FAIL: "失败",
            xtconstant.ACCOUNT_STATUS_INITING: "初始化中",
            xtconstant.ACCOUNT_STATUS_CORRECTING: "数据刷新校正中",
            xtconstant.ACCOUNT_STATUS_CLOSED: "收盘后",
            xtconstant.ACCOUNT_STATUS_ASSIS_FAIL: "穿透副链接断开",
            xtconstant.ACCOUNT_STATUS_DISABLEBYSYS: "系统停用（总线使用-密码错误超限）",
            xtconstant.ACCOUNT_STATUS_DISABLEBYUSER: "用户停用（总线使用）",
        }
        status_desc = status_map.get(status.status, "未知状态")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 账号ID: {status.account_id}, 类型: {status.account_type}, 状态码: {status.status}, 状态: {status_desc}")


# 替换为 async 版本，并迁移买入逻辑


async def exec_buy():
    while True:
        print("exec_buy....")
        try:
            # 查询所有is_buy=True的股票
            buy_signals = StockModel.list_by({'is_buy': True})

            if buy_signals:
                print(f"找到 {len(buy_signals)} 个买入信号")

                for stock in buy_signals:
                    try:
                        print(
                            f"处理买入信号: {stock.code} - {stock.instrument_name}")

                        # 获取当前最新价格
                        try:
                            # 使用xtdata获取实时价格
                            current_price = get_current_price(stock.code)
                            if current_price <= 0:
                                print(f"股票 {stock.code} 无法获取实时价格，使用前收盘价")
                                buy_price = stock.pre_close if stock.pre_close else 0
                            else:
                                buy_price = current_price
                                print(f"股票 {stock.code} 当前价格: {buy_price}")
                        except Exception as e:
                            print(f"获取股票 {stock.code} 实时价格失败: {e}，使用前收盘价")
                            buy_price = stock.pre_close if stock.pre_close else 0

                        # 验证买入价格
                        # is_valid, message = validate_buy_price(
                        #     stock.code, buy_price, stock.pre_close)
                        # if not is_valid:
                        #     print(f"股票 {stock.code} {message}，跳过")
                        #     continue

                        # 买入数量 1手 = 1000股
                        buy_vol = 1000

                        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
                        print(
                            f"下单买入: {stock.code}, 价格: {buy_price}, 数量: {buy_vol}")
                        fix_result_order_id = xt_trader.order_stock(
                            acc, stock.code, xtconstant.STOCK_BUY, buy_vol, xtconstant.FIX_PRICE, buy_price, '', f'备注：自动买入{stock.instrument_name}')
                        print(f"订单ID: {fix_result_order_id}")

                        # 将is_buy标记为False，避免重复买入
                        StockModel.update_by(
                            {'code': stock.code}, {'is_buy': False})
                        print(f"已更新 {stock.code} 的买入状态为False")

                    except Exception as e:
                        print(f"处理股票 {stock.code} 时发生错误: {e}")
                        continue
            else:
                print("当前没有买入信号")

        except Exception as e:
            print(f"查询买入信号时发生错误: {e}")

        await asyncio.sleep(1)  # 轮询间隔

# 同步账号信息


async def sync_account_info():
    ''' 资产XtAsset
    属性	类型	注释
    account_type	int	账号类型，参见数据字典
    account_id	str	资金账号
    cash	float	可用金额
    frozen_cash	float	冻结金额
    market_value	float	持仓市值
    total_asset	float	总资产
    '''
    while True:
        print("sync_account_info....")
        try:
            stock_asset = xt_trader.query_stock_asset(acc)
            print(f"持仓信息: {stock_asset.account_type}")
            print(f"持仓信息: {stock_asset.account_id}")
            print(f"可用金额: {stock_asset.cash}")
            print(f"冻结金额: {stock_asset.frozen_cash}")
            print(f"持仓市值: {stock_asset.market_value}")
            print(f"总资产: {stock_asset.total_asset}")
            update_account(stock_asset)

        except Exception as e:
            print(f"获取账号信息时发生错误: {e}")

        await asyncio.sleep(1)  # 轮询间隔


async def main():
    print("开始启动QMT客户端...")

    qmt_path = get_qmt_cfg().userdata_mini_path
    if not qmt_path:
        raise ValueError("userdata_mini_path is 不能为空")

    session_id = int(time.time())  # 生成session id 整数类型 同时运行的策略不能重复

    # *********************************************************************************************************
    # 初始化交易客户端 并建立交易连接
    # *********************************************************************************************************
    global xt_trader
    xt_trader = XtQuantTrader(qmt_path, session_id)

    callback = MyXtQuantTraderCallback()  # 创建交易回调类对象，并声明接收回调
    xt_trader.register_callback(callback)
    xt_trader.start()  # 启动交易线程
    connect_result = xt_trader.connect()  # 建立交易连接，返回0表示连接成功

    if connect_result == 0:
        print("与QMT服务器建立连接成功")
    else:
        print("与QMT服务器建立连接失败:", connect_result)
        return

    init_account()  # 初始化交易账号
    subscribe_result = xt_trader.subscribe(
        acc)  # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功

    if subscribe_result == 0:
        print("对交易回调进行订阅成功")
    else:
        print("对交易回调进行订阅失败:", subscribe_result)
        return

    # *********************************************************************************************************
    # 业务操作
    # *********************************************************************************************************
    loop = asyncio.get_running_loop()
    run_forever_task = loop.run_in_executor(
        None, xt_trader.run_forever)  # 启动交易线程

    # 并发执行 xt_trader.run_forever 和 exec_buy
    # buy_task = asyncio.create_task(exec_buy())
    account_task = asyncio.create_task(sync_account_info())
    await asyncio.gather(run_forever_task, account_task)  # 等待两个任务完成


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Program exited with error: {e}")
