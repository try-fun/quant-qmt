# coding=gbk
"""
资金账户服务：同步与持久化账户资产信息至本地 JSON 文件
"""
import datetime
from src.service.storage import save_json, load_json

ACCOUNT_FILE = "data/account.json"


def update_account(account_info, file_path: str = ACCOUNT_FILE) -> bool:
    """
    更新并持久化资金账户资产信息至本地 JSON

    Args:
        account_info: XtAsset 对象或包含资产属性的对象
        file_path (str): 目标 JSON 文件路径，默认 data/account.json

    Returns:
        bool: 是否持久化成功
    """
    if account_info is None:
        return False

    account_id = str(getattr(account_info, "account_id", ""))
    account_type = int(getattr(account_info, "account_type", 0))
    cash = float(getattr(account_info, "cash", getattr(account_info, "m_dCash", 0.0)))
    frozen_cash = float(getattr(account_info, "frozen_cash", getattr(account_info, "m_dFrozenCash", 0.0)))
    market_value = float(getattr(account_info, "market_value", getattr(account_info, "m_dMarketValue", 0.0)))
    total_asset = float(getattr(account_info, "total_asset", getattr(account_info, "m_dTotalAsset", 0.0)))

    data = {
        "account_id": account_id,
        "account_type": account_type,
        "cash": round(cash, 2),
        "frozen_cash": round(frozen_cash, 2),
        "market_value": round(market_value, 2),
        "total_asset": round(total_asset, 2),
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return save_json(file_path, data)


def get_account(file_path: str = ACCOUNT_FILE) -> dict:
    """
    从本地 JSON 读取最新资金账户资产快照

    Args:
        file_path (str): 目标 JSON 文件路径

    Returns:
        dict: 资金账户信息字典
    """
    return load_json(file_path, default={})
