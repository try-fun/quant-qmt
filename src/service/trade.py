# coding=gbk
from xtquant.xtpythonclient import XtTrade
import datetime
from src.db.trade_model import TradeModel


def update_trade(trades):
    """
    同步成交记录至数据库
    :param trades: XtTrade 对象列表或单个 XtTrade
    """
    if not trades:
        return
    if not isinstance(trades, list):
        trades = [trades]

    for trade in trades:
        model = TradeModel.objects(traded_id=trade.traded_id).first()
        if model is None:
            model = TradeModel()
            model.create_time = datetime.datetime.now()

        model.account_type = trade.account_type
        model.account_id = trade.account_id
        model.stock_code = trade.stock_code
        model.order_type = trade.order_type
        model.traded_id = trade.traded_id
        model.traded_time = trade.traded_time
        model.traded_price = trade.traded_price
        model.traded_volume = trade.traded_volume
        model.traded_amount = trade.traded_amount
        model.order_id = trade.order_id
        model.order_sysid = trade.order_sysid
        model.strategy_name = trade.strategy_name
        model.order_remark = trade.order_remark
        model.update_time = datetime.datetime.now()
        model.save()
