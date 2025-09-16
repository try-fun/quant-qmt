# coding=gbk
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant, xtdata
import time
import datetime
from src.stock.trander.account import update_account
from src.stock.trander.order import update_order
from src.stock.trander.trade import update_trade
from src.stock.trander.positions import update_position
# 全局
# StockAccount可以用第二个参数指定账号类型，如沪港通传'HUGANGTONG'，深港通传'SHENGANGTONG'
# 2034258 31700004664001
acc = StockAccount('2034258', 'STOCK')
xt_trader = None
stock_code = '603077.SH'
is_buy = False


def interact():
    """执行后进入repl模式"""
    import code
    code.InteractiveConsole(locals=globals()).interact()
# 行情回调


'''
将指标生成bitmap推理交易结果
'''


def on_quote(data):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data)

    '''
    {'603077.SH': [{'time': 1753166004000, 'lastPrice': 1.9000000000000001, 'open': 1.8900000000000001, 'high': 1.9000000000000001, 'low': 1.84, 'lastClose': 1.8800000000000001, 'amount': 311544182.0, 'volume': 1663470, 'pvolume': 166347027, 'stockStatus': 3, 'openInt': 13, 'transactionNum': 29434, 'lastSettlementPrice': 0.0, 'settlementPrice': 0.0, 'pe': 0.0, 'askPrice': [1.9000000000000001, 1.9100000000000001, 1.92, 1.93, 1.94], 'bidPrice': [1.8900000000000001, 1.8800000000000001, 1.87, 1.86, 1.85], 'askVol': [18620, 54770, 51248, 25995, 15600], 'bidVol': [32664, 54719, 30109, 32028, 46927], 'volRatio': 0.0, 'speed1Min': 0.0, 'speed5Min': 0.0}]}
    '''
    # 当前股价
    # 保留两位小数
    current_price = round(data[stock_code][0]['lastPrice'], 2)
    print(f"{stock_code} 当前价格： {current_price}")

    # 根据 bitmap
    # 买
    # 卖
    # bitmap [1.1.1.1.1]
    # global is_buy
    # if current_price <= 1.89 and not is_buy:
    #     # 买入价格
    #     buy_price = 1.89
    #     # 买入数量 100的整数倍
    #     buy_vol = 100
    #     # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
    #     print("order using the fix price:")
    #     fix_result_order_id = xt_trader.order_stock(
    #         acc, stock_code, xtconstant.STOCK_BUY, buy_vol, xtconstant.FIX_PRICE, buy_price, '', '备注：自动买入100股')
    #     print(fix_result_order_id)
    #     is_buy = True
    #     # 更新委托
    #     orders = xt_trader.query_stock_orders(acc)
    #     update_order(orders)


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


def main():
    print("启动交易客户端")
    # path为mini qmt客户端安装目录下userdata_mini路径
    path = 'C:\\mqt\\userdata_mini'
    # 生成session id 整数类型 同时运行的策略不能重复
    session_id = int(time.time())
    global xt_trader
    xt_trader = XtQuantTrader(path, session_id)
    # 创建交易回调类对象，并声明接收回调
    callback = MyXtQuantTraderCallback()
    xt_trader.register_callback(callback)
    # 启动交易线程
    xt_trader.start()
    # 建立交易连接，返回0表示连接成功
    connect_result = xt_trader.connect()
    print(connect_result)
    # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
    subscribe_result = xt_trader.subscribe(acc)
    print(subscribe_result)
    if subscribe_result == 0:
        print("建立交易连接成功")
    else:
        print("建立交易连接失败")
        return

    # 取账号信息
    account_info = xt_trader.query_stock_asset(acc)
    # 取可用资金
    available_cash = account_info.m_dCash

    print(acc.account_id, '可用资金', available_cash)
    update_account(account_info)  # 更新账号信息

    # 更新委托
    orders = xt_trader.query_stock_orders(acc)
    update_order(orders)

    # # 更新成交
    trades = xt_trader.query_stock_trades(acc)
    update_trade(trades)

    # 查询当日所有的持仓
    positions = xt_trader.query_stock_positions(acc)
    update_position(positions)

    # 订阅的品种列表
    xtdata.subscribe_quote(stock_code, 'tick', callback=on_quote)

    # 阻塞线程，接收交易推送
    xt_trader.run_forever()
    # 如果使用vscode pycharm等本地编辑器 可以进入交互模式 方便调试 （把上一行的run_forever注释掉 否则不会执行到这里）
    # interact()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Program exited with error: {e}")
