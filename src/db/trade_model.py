# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel

'''
account_type    int     账号类型，参见数据字典
account_id      str     资金账号
stock_code      str     证券代码
order_type      int     委托类型，参见数据字典
traded_id       str     成交编号
traded_time     int     成交时间
traded_price    float   成交均价
traded_volume   int     成交数量
traded_amount   float   成交金额
order_id        int     订单编号
order_sysid     str     柜台合同编号
strategy_name   str     策略名称
order_remark    str     委托备注，最多 24 个英文字符
direction       int     多空方向，股票不适用
offset_flag     int     开平标志，股票不适用
'''


# 成交记录模型
class TradeModel(BaseModel):
    meta = {'collection': 'tb_trade'}
    # 账号类型
    account_type = IntField()
    # 资金账号
    account_id = StringField()
    # 证券代码
    stock_code = StringField()
    # 委托类型
    order_type = IntField()
    # 成交编号
    traded_id = StringField()
    # 成交时间
    traded_time = IntField()
    # 成交均价
    traded_price = FloatField()
    # 成交数量
    traded_volume = IntField()
    # 成交金额
    traded_amount = FloatField()
    # 订单编号
    order_id = IntField()
    # 柜台合同编号
    order_sysid = StringField()
    # 策略名称
    strategy_name = StringField()
    # 委托备注
    order_remark = StringField()
    # 创建时间
    create_time = DateTimeField()
    # 更新时间
    update_time = DateTimeField()
