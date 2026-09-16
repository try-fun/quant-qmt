# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel

'''
account_type    int     账号类型，参见数据字典
account_id      str     资金账号
stock_code      str     证券代码，例如"600000.SH"
order_id        int     订单编号
order_sysid     str     柜台合同编号
order_time      int     报单时间
order_type      int     委托类型，参见数据字典
order_volume    int     委托数量
price_type      int     报价类型，参见数据字典
price           float   委托价格
traded_volume   int     成交数量
traded_price    float   成交均价
order_status    int     委托状态，参见数据字典
status_msg      str     委托状态描述，如废单原因
strategy_name   str     策略名称
order_remark    str     委托备注，最多 24 个英文字符
direction       int     多空方向，股票不适用
offset_flag     int     开平标志，股票不适用
'''


# 委托订单模型
class OrderModel(BaseModel):
    meta = {'collection': 'tb_order'}
    # 账号类型
    account_type = IntField()
    # 资金账号
    account_id = StringField()
    # 证券代码
    stock_code = StringField()
    # 订单编号
    order_id = IntField()
    # 柜台合同编号
    order_sysid = StringField()
    # 报单时间
    order_time = IntField()
    # 委托类型
    order_type = IntField()
    # 委托数量
    order_volume = IntField()
    # 报价类型
    price_type = IntField()
    # 委托价格
    price = FloatField()
    # 成交数量
    traded_volume = IntField()
    # 成交均价
    traded_price = FloatField()
    # 委托状态
    order_status = IntField()
    # 委托状态描述
    status_msg = StringField()
    # 策略名称
    strategy_name = StringField()
    # 委托备注
    order_remark = StringField()
    # 创建时间
    create_time = DateTimeField()
    # 更新时间
    update_time = DateTimeField()
