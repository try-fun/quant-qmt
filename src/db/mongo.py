# coding=gbk

from mongoengine import connect
from src.config.config import get_mongodb_cfg


def init_mongodb():
    cfg = get_mongodb_cfg()
    connect(db=cfg.database, host=cfg.host, port=cfg.port,
            username=cfg.username, password=cfg.password)
    print(f"数据库连接成功: {cfg.database}")
