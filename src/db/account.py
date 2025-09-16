# coding=gbk
from mongoengine import StringField, IntField, FloatField, DateTimeField
from src.db.base_model import BaseModel


# 资产
class AccountModel(BaseModel):
    meta = {'collection': 'tb_account'}
    # 账号类型
    account_type = IntField()
    # 资金账号
    account_id = StringField()
    # 可用金额
    cash = FloatField()
    # 冻结金额
    frozen_cash = FloatField()
    # 持仓市值
    market_value = FloatField()
    # 总资产
    total_asset = FloatField()
    # 创建时间
    create_time = DateTimeField()
    # 更新时间
    update_time = DateTimeField()
