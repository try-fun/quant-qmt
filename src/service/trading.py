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
# ȫ��
# StockAccount�����õڶ�������ָ���˺����ͣ��绦��ͨ��'HUGANGTONG'�����ͨ��'SHENGANGTONG'
# 2034258 31700004664001
acc = StockAccount('2034258', 'STOCK')
xt_trader = None
stock_code = '603077.SH'
is_buy = False


def interact():
    """ִ�к����replģʽ"""
    import code
    code.InteractiveConsole(locals=globals()).interact()
# ����ص�


'''
��ָ������bitmap�����׽��
'''


def on_quote(data):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data)

    '''
    {'603077.SH': [{'time': 1753166004000, 'lastPrice': 1.9000000000000001, 'open': 1.8900000000000001, 'high': 1.9000000000000001, 'low': 1.84, 'lastClose': 1.8800000000000001, 'amount': 311544182.0, 'volume': 1663470, 'pvolume': 166347027, 'stockStatus': 3, 'openInt': 13, 'transactionNum': 29434, 'lastSettlementPrice': 0.0, 'settlementPrice': 0.0, 'pe': 0.0, 'askPrice': [1.9000000000000001, 1.9100000000000001, 1.92, 1.93, 1.94], 'bidPrice': [1.8900000000000001, 1.8800000000000001, 1.87, 1.86, 1.85], 'askVol': [18620, 54770, 51248, 25995, 15600], 'bidVol': [32664, 54719, 30109, 32028, 46927], 'volRatio': 0.0, 'speed1Min': 0.0, 'speed5Min': 0.0}]}
    '''
    # ��ǰ�ɼ�
    # ������λС��
    current_price = round(data[stock_code][0]['lastPrice'], 2)
    print(f"{stock_code} ��ǰ�۸� {current_price}")

    # ���� bitmap
    # ��
    # ��
    # bitmap [1.1.1.1.1]
    # global is_buy
    # if current_price <= 1.89 and not is_buy:
    #     # ����۸�
    #     buy_price = 1.89
    #     # �������� 100��������
    #     buy_vol = 100
    #     # ʹ��ָ�����µ����ӿڷ��ض�����ţ������������ڳ��������Լ���ѯί��״̬
    #     print("order using the fix price:")
    #     fix_result_order_id = xt_trader.order_stock(
    #         acc, stock_code, xtconstant.STOCK_BUY, buy_vol, xtconstant.FIX_PRICE, buy_price, '', '��ע���Զ�����100��')
    #     print(fix_result_order_id)
    #     is_buy = True
    #     # ����ί��
    #     orders = xt_trader.query_stock_orders(acc)
    #     update_order(orders)


class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        ���ӶϿ�
        :return:
        """
        print("connection lost")

    def on_stock_order(self, order):
        """
        ί�лر�����
        :param order: XtOrder����
        :return:
        """
        '''
        xtconstant.ORDER_UNREPORTED	48	δ��
        xtconstant.ORDER_WAIT_REPORTING	49	����
        xtconstant.ORDER_REPORTED	50	�ѱ�
        xtconstant.ORDER_REPORTED_CANCEL	51	�ѱ�����
        xtconstant.ORDER_PARTSUCC_CANCEL	52	���ɴ���
        xtconstant.ORDER_PART_CANCEL	53	�������Ѿ���һ���ֳɽ���ʣ�µ��Ѿ�������
        xtconstant.ORDER_CANCELED	54	�ѳ�
        xtconstant.ORDER_PART_SUCC	55	���ɣ��Ѿ���һ���ֳɽ���ʣ�µĴ��ɽ���
        xtconstant.ORDER_SUCCEEDED	56	�ѳ�
        xtconstant.ORDER_JUNK	57	�ϵ�
        xtconstant.ORDER_UNKNOWN	255	δ֪
        '''
        # ����״̬��������˵����ӳ��
        status_map = {
            xtconstant.ORDER_UNREPORTED: "δ��",
            xtconstant.ORDER_WAIT_REPORTING: "����",
            xtconstant.ORDER_REPORTED: "�ѱ�",
            xtconstant.ORDER_REPORTED_CANCEL: "�ѱ�����",
            xtconstant.ORDER_PARTSUCC_CANCEL: "���ɴ���",
            xtconstant.ORDER_PART_CANCEL: "����",
            xtconstant.ORDER_CANCELED: "�ѳ�",
            xtconstant.ORDER_PART_SUCC: "����",
            xtconstant.ORDER_SUCCEEDED: "�ѳ�",
            xtconstant.ORDER_JUNK: "�ϵ�",
            xtconstant.ORDER_UNKNOWN: "δ֪",
        }
        status_desc = status_map.get(order.order_status, "δ֪״̬")
        print("on order callback:")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ����ID: {order.order_id}, ��Ʊ����: {order.stock_code}, ״̬: {status_desc}, ϵͳID: {order.order_sysid}")

    def on_stock_trade(self, trade):
        """
        �ɽ��䶯����
        :param trade: XtTrade����
        :return:
        """
        print("on trade callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} �˺�ID: {trade.account_id}, ��Ʊ����: {trade.stock_code}, ����ID: {trade.order_id}")

    def on_order_error(self, order_error):
        """
        ί��ʧ������
        :param order_error:XtOrderError ����
        :return:
        """
        print("on order_error callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ����ID: {order_error.order_id}, ����ID: {order_error.error_id}, ������Ϣ: {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        """
        ����ʧ������
        :param cancel_error: XtCancelError ����
        :return:
        """
        print("on cancel_error callback")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ����ID: {cancel_error.order_id}, ����ID: {cancel_error.error_id}, ������Ϣ: {cancel_error.error_msg}")

    def on_order_stock_async_response(self, response):
        """
        �첽�µ��ر�����
        :param response: XtOrderResponse ����
        :return:
        """
        print("on_order_stock_async_response")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} �˺�ID: {response.account_id}, ����ID: {response.order_id}, ���: {response.seq}")

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus ����
        :return:
        """
        print("on_account_status")
        # ����״̬��������˵����ӳ��
        status_map = {
            xtconstant.ACCOUNT_STATUS_INVALID: "��Ч",
            xtconstant.ACCOUNT_STATUS_OK: "����",
            xtconstant.ACCOUNT_STATUS_WAITING_LOGIN: "������",
            xtconstant.ACCOUNT_STATUSING: "��½��",
            xtconstant.ACCOUNT_STATUS_FAIL: "ʧ��",
            xtconstant.ACCOUNT_STATUS_INITING: "��ʼ����",
            xtconstant.ACCOUNT_STATUS_CORRECTING: "����ˢ��У����",
            xtconstant.ACCOUNT_STATUS_CLOSED: "���̺�",
            xtconstant.ACCOUNT_STATUS_ASSIS_FAIL: "��͸�����ӶϿ�",
            xtconstant.ACCOUNT_STATUS_DISABLEBYSYS: "ϵͳͣ�ã�����ʹ��-��������ޣ�",
            xtconstant.ACCOUNT_STATUS_DISABLEBYUSER: "�û�ͣ�ã�����ʹ�ã�",
        }
        status_desc = status_map.get(status.status, "δ֪״̬")
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} �˺�ID: {status.account_id}, ����: {status.account_type}, ״̬��: {status.status}, ״̬: {status_desc}")


def main():
    print("�������׿ͻ���")
    # pathΪmini qmt�ͻ��˰�װĿ¼��userdata_mini·��
    path = 'C:\\mqt\\userdata_mini'
    # ����session id �������� ͬʱ���еĲ��Բ����ظ�
    session_id = int(time.time())
    global xt_trader
    xt_trader = XtQuantTrader(path, session_id)
    # �������׻ص�����󣬲��������ջص�
    callback = MyXtQuantTraderCallback()
    xt_trader.register_callback(callback)
    # ���������߳�
    xt_trader.start()
    # �����������ӣ�����0��ʾ���ӳɹ�
    connect_result = xt_trader.connect()
    print(connect_result)
    # �Խ��׻ص����ж��ģ����ĺ�����յ��������ƣ�����0��ʾ���ĳɹ�
    subscribe_result = xt_trader.subscribe(acc)
    print(subscribe_result)
    if subscribe_result == 0:
        print("�����������ӳɹ�")
    else:
        print("������������ʧ��")
        return

    # ȡ�˺���Ϣ
    account_info = xt_trader.query_stock_asset(acc)
    # ȡ�����ʽ�
    available_cash = account_info.m_dCash

    print(acc.account_id, '�����ʽ�', available_cash)
    update_account(account_info)  # �����˺���Ϣ

    # ����ί��
    orders = xt_trader.query_stock_orders(acc)
    update_order(orders)

    # # ���³ɽ�
    trades = xt_trader.query_stock_trades(acc)
    update_trade(trades)

    # ��ѯ�������еĳֲ�
    positions = xt_trader.query_stock_positions(acc)
    update_position(positions)

    # ���ĵ�Ʒ���б�
    xtdata.subscribe_quote(stock_code, 'tick', callback=on_quote)

    # �����̣߳����ս�������
    xt_trader.run_forever()
    # ���ʹ��vscode pycharm�ȱ��ر༭�� ���Խ��뽻��ģʽ ������� ������һ�е�run_foreverע�͵� ���򲻻�ִ�е����
    # interact()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Program exited with error: {e}")
