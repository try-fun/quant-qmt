# coding=gbk
"""
委托订单服务：同步与持久化委托订单至本地 JSON 文件
"""
import datetime
from typing import Union, List, Dict, Any
from src.service.storage import save_json, load_json

ORDERS_FILE = "data/orders.json"


def update_order(orders: Union[Any, List[Any]], file_path: str = ORDERS_FILE) -> bool:
    """
    同步并幂等更新委托订单至本地 JSON 文件

    Args:
        orders: XtOrder 对象列表或单个 XtOrder
        file_path (str): 目标 JSON 文件路径，默认 data/orders.json

    Returns:
        bool: 是否持久化成功
    """
    if orders is None:
        return False

    if not isinstance(orders, list):
        orders = [orders]

    existing_orders = load_json(file_path, default=[])
    # 构建 order_id 到记录的索引映射（保持原有顺序）
    order_dict = {}
    order_list = []
    for item in existing_orders:
        oid = item.get("order_id")
        if oid is not None:
            order_dict[oid] = item
            order_list.append(item)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for order in orders:
        order_id = getattr(order, "order_id", None)
        if order_id is None:
            continue

        stock_code = str(getattr(order, "stock_code", ""))
        order_entry = {
            "order_id": order_id,
            "order_sysid": str(getattr(order, "order_sysid", "")),
            "account_id": str(getattr(order, "account_id", "")),
            "account_type": int(getattr(order, "account_type", 0)),
            "stock_code": stock_code,
            "order_type": int(getattr(order, "order_type", 0)),
            "order_volume": int(getattr(order, "order_volume", 0)),
            "price_type": int(getattr(order, "price_type", 0)),
            "price": round(float(getattr(order, "price", 0.0)), 2),
            "traded_volume": int(getattr(order, "traded_volume", 0)),
            "traded_price": round(float(getattr(order, "traded_price", 0.0)), 2),
            "order_status": int(getattr(order, "order_status", 0)),
            "status_msg": str(getattr(order, "status_msg", "")),
            "strategy_name": str(getattr(order, "strategy_name", "")),
            "order_remark": str(getattr(order, "order_remark", "")),
            "order_time": getattr(order, "order_time", 0),
            "update_time": now_str
        }

        if order_id in order_dict:
            # 更新已有订单，保留原有 create_time
            existing_entry = order_dict[order_id]
            order_entry["create_time"] = existing_entry.get("create_time", now_str)
            existing_entry.update(order_entry)
        else:
            # 新增订单
            order_entry["create_time"] = now_str
            order_dict[order_id] = order_entry
            order_list.append(order_entry)

    return save_json(file_path, order_list)


def get_orders(file_path: str = ORDERS_FILE) -> List[Dict[str, Any]]:
    """
    从本地 JSON 读取全部委托订单列表

    Args:
        file_path (str): 目标 JSON 文件路径

    Returns:
        List[Dict[str, Any]]: 委托订单列表
    """
    return load_json(file_path, default=[])
