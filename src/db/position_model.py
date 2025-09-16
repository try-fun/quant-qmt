# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel

'''
account_type	int	账号类型，参见数据字典
account_id	str	资金账号
stock_code	str	证券代码
volume	int	持仓数量
can_use_volume	int	可用数量
open_price	float	开仓价
market_value	float	市值
frozen_volume	int	冻结数量
on_road_volume	int	在途股份
yesterday_volume	int	昨夜拥股
avg_price	float	成本价
direction	int	多空方向，股票不适用；参见数据字典


'''

# 持仓


class PositionModel(BaseModel):
    meta = {'collection': 'tb_position'}
    # 账号类型
    account_type = IntField()
    # 资金账号
    account_id = StringField()
    # 证券代码
    stock_code = StringField()
    # 持仓数量
    volume = IntField()
    # 可用数量
    can_use_volume = IntField()
    # 开仓价
    open_price = FloatField()
    # 市值
    market_value = FloatField()
    # 冻结数量
    frozen_volume = IntField()
    # 在途股份
    on_road_volume = IntField()
    # 昨夜拥股
    yesterday_volume = IntField()
    # 创建时间
    create_time = DateTimeField()
    # 更新时间
    update_time = DateTimeField()
