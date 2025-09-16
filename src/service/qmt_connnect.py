# coding=gbk
import asyncio
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant, xtdata
import time
import datetime
from src.config.config import get_account_cfg, get_qmt_cfg
from src.service.account import update_account

# ��ʼ���˺���Ϣ
acc = None
xt_trader = None


def init_account():
    stock_account = get_account_cfg().stock_account
    if not stock_account:
        raise ValueError("stock_account is ����Ϊ��")

    print(f"��ʼ�������˺�: {stock_account}")
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
    ��ȡ��Ʊ��ǰʱ�����¼۸�
    ʹ�� get_market_data_ex ��ȡʵʱ�۸�
    """
    try:
        # ��ȡ��ǰ����
        today = datetime.datetime.now().strftime('%Y%m%d')

        download_one_stock_data(stock_code, 'tick', today, '', 1)

        # ʹ�� get_market_data_ex ��ȡ��ǰʱ�����¼۸�
        market_data = xtdata.get_market_data_ex(
            field_list=['lastPrice'],  # ���¼�
            stock_list=[stock_code],  # ��Ʊ�����б�
            period='tick',  # 1��������
            start_time=today,  # ����ʱ��
            end_time='',  # ����ʱ��
            count=1  # ��ȡ����1������
        )

        if market_data and stock_code in market_data and len(market_data[stock_code]) > 0:
            # ��ȡ���¼۸�
            current_price = market_data[stock_code]['lastPrice'].iloc[-1]
            print(f"��Ʊ {stock_code} ��ǰ�۸�: {current_price}")
            return current_price
        else:
            print(f"�޷���ȡ��Ʊ {stock_code} �ĵ�ǰ�۸�����")
            return 0

    except Exception as e:
        print(f"��ȡ��Ʊ {stock_code} ��ǰ�۸�ʱ��������: {e}")
        return 0


def validate_buy_price(stock_code, buy_price, pre_close):
    """
    ��֤����۸��Ƿ����
    """
    if buy_price <= 0:
        return False, "�۸���Ч"

    if pre_close and pre_close > 0:
        # ���۸��Ƿ��ں���Χ�ڣ�ǰ���̼۵ġ�10%��
        price_change_ratio = abs(buy_price - pre_close) / pre_close
        if price_change_ratio > 0.1:
            return False, f"�۸�仯����: {price_change_ratio:.2%}"

    return True, "�۸����"


'''
��ָ������bitmap�����׽��
'''


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


# �滻Ϊ async �汾����Ǩ�������߼�


async def exec_buy():
    while True:
        print("exec_buy....")
        try:
            # ��ѯ����is_buy=True�Ĺ�Ʊ
            buy_signals = StockModel.list_by({'is_buy': True})

            if buy_signals:
                print(f"�ҵ� {len(buy_signals)} �������ź�")

                for stock in buy_signals:
                    try:
                        print(
                            f"���������ź�: {stock.code} - {stock.instrument_name}")

                        # ��ȡ��ǰ���¼۸�
                        try:
                            # ʹ��xtdata��ȡʵʱ�۸�
                            current_price = get_current_price(stock.code)
                            if current_price <= 0:
                                print(f"��Ʊ {stock.code} �޷���ȡʵʱ�۸�ʹ��ǰ���̼�")
                                buy_price = stock.pre_close if stock.pre_close else 0
                            else:
                                buy_price = current_price
                                print(f"��Ʊ {stock.code} ��ǰ�۸�: {buy_price}")
                        except Exception as e:
                            print(f"��ȡ��Ʊ {stock.code} ʵʱ�۸�ʧ��: {e}��ʹ��ǰ���̼�")
                            buy_price = stock.pre_close if stock.pre_close else 0

                        # ��֤����۸�
                        # is_valid, message = validate_buy_price(
                        #     stock.code, buy_price, stock.pre_close)
                        # if not is_valid:
                        #     print(f"��Ʊ {stock.code} {message}������")
                        #     continue

                        # �������� 1�� = 1000��
                        buy_vol = 1000

                        # ʹ��ָ�����µ����ӿڷ��ض�����ţ������������ڳ��������Լ���ѯί��״̬
                        print(
                            f"�µ�����: {stock.code}, �۸�: {buy_price}, ����: {buy_vol}")
                        fix_result_order_id = xt_trader.order_stock(
                            acc, stock.code, xtconstant.STOCK_BUY, buy_vol, xtconstant.FIX_PRICE, buy_price, '', f'��ע���Զ�����{stock.instrument_name}')
                        print(f"����ID: {fix_result_order_id}")

                        # ��is_buy���ΪFalse�������ظ�����
                        StockModel.update_by(
                            {'code': stock.code}, {'is_buy': False})
                        print(f"�Ѹ��� {stock.code} ������״̬ΪFalse")

                    except Exception as e:
                        print(f"�����Ʊ {stock.code} ʱ��������: {e}")
                        continue
            else:
                print("��ǰû�������ź�")

        except Exception as e:
            print(f"��ѯ�����ź�ʱ��������: {e}")

        await asyncio.sleep(1)  # ��ѯ���

# ͬ���˺���Ϣ


async def sync_account_info():
    ''' �ʲ�XtAsset
    ����	����	ע��
    account_type	int	�˺����ͣ��μ������ֵ�
    account_id	str	�ʽ��˺�
    cash	float	���ý��
    frozen_cash	float	������
    market_value	float	�ֲ���ֵ
    total_asset	float	���ʲ�
    '''
    while True:
        print("sync_account_info....")
        try:
            stock_asset = xt_trader.query_stock_asset(acc)
            print(f"�ֲ���Ϣ: {stock_asset.account_type}")
            print(f"�ֲ���Ϣ: {stock_asset.account_id}")
            print(f"���ý��: {stock_asset.cash}")
            print(f"������: {stock_asset.frozen_cash}")
            print(f"�ֲ���ֵ: {stock_asset.market_value}")
            print(f"���ʲ�: {stock_asset.total_asset}")
            update_account(stock_asset)

        except Exception as e:
            print(f"��ȡ�˺���Ϣʱ��������: {e}")

        await asyncio.sleep(1)  # ��ѯ���


async def main():
    print("��ʼ����QMT�ͻ���...")

    qmt_path = get_qmt_cfg().userdata_mini_path
    if not qmt_path:
        raise ValueError("userdata_mini_path is ����Ϊ��")

    session_id = int(time.time())  # ����session id �������� ͬʱ���еĲ��Բ����ظ�

    # *********************************************************************************************************
    # ��ʼ�����׿ͻ��� ��������������
    # *********************************************************************************************************
    global xt_trader
    xt_trader = XtQuantTrader(qmt_path, session_id)

    callback = MyXtQuantTraderCallback()  # �������׻ص�����󣬲��������ջص�
    xt_trader.register_callback(callback)
    xt_trader.start()  # ���������߳�
    connect_result = xt_trader.connect()  # �����������ӣ�����0��ʾ���ӳɹ�

    if connect_result == 0:
        print("��QMT�������������ӳɹ�")
    else:
        print("��QMT��������������ʧ��:", connect_result)
        return

    init_account()  # ��ʼ�������˺�
    subscribe_result = xt_trader.subscribe(
        acc)  # �Խ��׻ص����ж��ģ����ĺ�����յ��������ƣ�����0��ʾ���ĳɹ�

    if subscribe_result == 0:
        print("�Խ��׻ص����ж��ĳɹ�")
    else:
        print("�Խ��׻ص����ж���ʧ��:", subscribe_result)
        return

    # *********************************************************************************************************
    # ҵ�����
    # *********************************************************************************************************
    loop = asyncio.get_running_loop()
    run_forever_task = loop.run_in_executor(
        None, xt_trader.run_forever)  # ���������߳�

    # ����ִ�� xt_trader.run_forever �� exec_buy
    # buy_task = asyncio.create_task(exec_buy())
    account_task = asyncio.create_task(sync_account_info())
    await asyncio.gather(run_forever_task, account_task)  # �ȴ������������


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Program exited with error: {e}")
