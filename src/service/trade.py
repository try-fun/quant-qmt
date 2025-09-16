# coding=gbk
from xtquant.xtpythonclient import XtTrade
import datetime
from src.db.trade_model import TradeModel

# 更新交易记录


def update_trade(trades: XtTrade):

    # 取账号信息
    for trade in trades:
        model = TradeModel.objects(traded_id=trade.traded_id).first()
        if model is None:
            model = TradeModel()
            model.create_time = datetime.datetime.now()

        # 更新交易记录
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
