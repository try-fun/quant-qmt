# coding=gbk
from xtquant.xtpythonclient import XtOrder
import datetime
from src.db.order_model import OrderModel


def update_order(orders):
    """
    同步委托订单信息至数据库
    :param orders: XtOrder 对象列表或单个 XtOrder
    """
    if not orders:
        return
    if not isinstance(orders, list):
        orders = [orders]

    for order in orders:
        model = OrderModel.objects(order_id=order.order_id).first()
        if model is None:
            model = OrderModel()
            model.create_time = datetime.datetime.now()

        model.account_id = order.account_id
        model.account_type = order.account_type
        model.stock_code = order.stock_code
        model.order_id = order.order_id
        model.order_sysid = order.order_sysid
        model.order_time = order.order_time
        model.order_type = order.order_type
        model.order_volume = order.order_volume
        model.price_type = order.price_type
        model.price = order.price
        model.traded_volume = order.traded_volume
        model.traded_price = order.traded_price
        model.order_status = order.order_status
        model.status_msg = order.status_msg
        model.strategy_name = order.strategy_name
        model.order_remark = order.order_remark
        model.update_time = datetime.datetime.now()
        model.save()
