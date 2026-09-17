# coding=gbk
"""
持仓服务：同步与持久化持仓股票信息至本地 JSON 文件
"""
import datetime
from typing import Union, List, Dict, Any
from src.service.storage import save_json, load_json

POSITIONS_FILE = "data/positions.json"


def update_position(positions: Union[Any, List[Any]], file_path: str = POSITIONS_FILE) -> bool:
    """
    同步并持久化持仓列表至本地 JSON

    Args:
        positions: XtPosition 对象列表或单个 XtPosition
        file_path (str): 目标 JSON 文件路径，默认 data/positions.json

    Returns:
        bool: 是否持久化成功
    """
    if positions is None:
        return False

    if not isinstance(positions, list):
        positions = [positions]

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = []

    for pos in positions:
        stock_code = getattr(pos, "stock_code", "")
        if not stock_code:
            continue

        records.append({
            "stock_code": stock_code,
            "account_id": str(getattr(pos, "account_id", "")),
            "account_type": int(getattr(pos, "account_type", 0)),
            "volume": int(getattr(pos, "volume", 0)),
            "can_use_volume": int(getattr(pos, "can_use_volume", 0)),
            "open_price": round(float(getattr(pos, "open_price", 0.0)), 2),
            "market_value": round(float(getattr(pos, "market_value", 0.0)), 2),
            "frozen_volume": int(getattr(pos, "frozen_volume", 0)),
            "on_road_volume": int(getattr(pos, "on_road_volume", 0)),
            "yesterday_volume": int(getattr(pos, "yesterday_volume", 0)),
            "update_time": now_str
        })

    return save_json(file_path, records)


def get_positions(file_path: str = POSITIONS_FILE) -> List[Dict[str, Any]]:
    """
    从本地 JSON 读取当前持仓列表

    Args:
        file_path (str): 目标 JSON 文件路径

    Returns:
        List[Dict[str, Any]]: 持仓列表
    """
    return load_json(file_path, default=[])
