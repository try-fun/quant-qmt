# coding=gbk
"""
成交记录服务：同步与持久化成交记录至本地 JSON 文件
"""
import datetime
from typing import Union, List, Dict, Any
from src.service.storage import save_json, load_json

TRADES_FILE = "data/trades.json"


def update_trade(trades: Union[Any, List[Any]], file_path: str = TRADES_FILE) -> bool:
    """
    同步并幂等更新成交记录至本地 JSON 文件

    Args:
        trades: XtTrade 对象列表或单个 XtTrade
        file_path (str): 目标 JSON 文件路径，默认 data/trades.json

    Returns:
        bool: 是否持久化成功
    """
    if trades is None:
        return False

    if not isinstance(trades, list):
        trades = [trades]

    existing_trades = load_json(file_path, default=[])
    # 构建 traded_id 到记录的索引映射（保持原有顺序）
    trade_dict = {}
    trade_list = []
    for item in existing_trades:
        tid = item.get("traded_id")
        if tid is not None:
            trade_dict[tid] = item
            trade_list.append(item)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for trade in trades:
        traded_id = getattr(trade, "traded_id", None)
        if traded_id is None or str(traded_id).strip() == "":
            continue

        traded_id_str = str(traded_id)
        stock_code = str(getattr(trade, "stock_code", ""))
        trade_entry = {
            "traded_id": traded_id_str,
            "order_id": int(getattr(trade, "order_id", 0)),
            "order_sysid": str(getattr(trade, "order_sysid", "")),
            "account_id": str(getattr(trade, "account_id", "")),
            "account_type": int(getattr(trade, "account_type", 0)),
            "stock_code": stock_code,
            "order_type": int(getattr(trade, "order_type", 0)),
            "traded_price": round(float(getattr(trade, "traded_price", 0.0)), 2),
            "traded_volume": int(getattr(trade, "traded_volume", 0)),
            "traded_amount": round(float(getattr(trade, "traded_amount", 0.0)), 2),
            "traded_time": getattr(trade, "traded_time", 0),
            "strategy_name": str(getattr(trade, "strategy_name", "")),
            "order_remark": str(getattr(trade, "order_remark", "")),
            "update_time": now_str
        }

        if traded_id_str in trade_dict:
            # 更新已有成交记录，保留原有 create_time
            existing_entry = trade_dict[traded_id_str]
            trade_entry["create_time"] = existing_entry.get("create_time", now_str)
            existing_entry.update(trade_entry)
        else:
            # 新增成交记录
            trade_entry["create_time"] = now_str
            trade_dict[traded_id_str] = trade_entry
            trade_list.append(trade_entry)

    return save_json(file_path, trade_list)


def get_trades(file_path: str = TRADES_FILE) -> List[Dict[str, Any]]:
    """
    从本地 JSON 读取全部成交记录列表

    Args:
        file_path (str): 目标 JSON 文件路径

    Returns:
        List[Dict[str, Any]]: 成交记录列表
    """
    return load_json(file_path, default=[])
