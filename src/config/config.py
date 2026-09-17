# coding=gbk
import configparser
import os
from dataclasses import dataclass


@dataclass
class AccountCfg:
    stock_account: str


@dataclass
class QMTCfg:
    userdata_mini_path: str


def get_config():
    # 尝试读取默认配置文件
    config_file = [
        "config-dev.ini",
        "config.ini",
        "config/config-dev.ini",
        "config/config.ini",
        "src/config/config-dev.ini",
        "src/config/config.ini",
        "../config/config-dev.ini",
        "../config/config.ini",
        "../../config/config-dev.ini",
        "../../config/config.ini",
        "../../../config/config-dev.ini",
        "../../../config/config.ini",
        "../../../../config/config-dev.ini",
        "../../../../config/config.ini",
    ]
    for file in config_file:
        if os.path.exists(file):
            # 尝试使用gb2312、gbk、utf-8编码读取配置文件
            for encoding in ["gb2312", "gbk", "utf-8"]:
                try:
                    with open(file, "r", encoding=encoding) as f:
                        print("读取配置文件:", file)
                        config = configparser.ConfigParser(interpolation=None)
                        config.read(file, encoding=encoding)
                        if config:
                            return config
                except Exception as e:
                    print(f"读取配置文件 {file} 时出错 (编码: {encoding}): {e}")
                    continue
    raise Exception("config file not found")


_account_cfg = None
_qmt_cfg = None


def get_account_cfg():
    global _account_cfg
    if _account_cfg is None:
        config = get_config()
        _account_cfg = AccountCfg(
            stock_account=config.get("account", "stock_account").strip("\"")
        )
    return _account_cfg


def get_qmt_cfg():
    global _qmt_cfg
    if _qmt_cfg is None:
        config = get_config()
        _qmt_cfg = QMTCfg(
            userdata_mini_path=config.get("qmt", "userdata_mini_path").strip("\"")
        )
    return _qmt_cfg


if __name__ == "__main__":
    account_cfg = get_account_cfg()
    print("Account Config:")
    print(f"Stock Account: {account_cfg.stock_account}")

    qmt_cfg = get_qmt_cfg()
    print("QMT Config:")
    print(f"Userdata Mini Path: {qmt_cfg.userdata_mini_path}")
