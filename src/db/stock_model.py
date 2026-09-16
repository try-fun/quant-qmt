# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel


class StockModel(BaseModel):
    meta = {'collection': 'tb_stock'}
    # 股票代码
    code = StringField()
    # 交易所ID
    exchange_id = StringField()
    # 合约代码
    instrument_id = StringField()
    # 证券名称
    instrument_name = StringField()
    # 上市日期
    open_date = StringField()
    # 退市日期
    expire_date = IntField()
    # 前收盘价
    pre_close = FloatField()
    # 结算价
    settlement_price = FloatField()
    # 涨停价
    up_stop_price = FloatField()
    # 跌停价
    down_stop_price = FloatField()
    # 流通股本
    float_volume = FloatField()
    # 总股本
    total_volume = FloatField()
    # 证券状态
    instrument_status = IntField()
    # 是否交易
    is_trading = BooleanField()

    # 是否已买入
    is_buy = BooleanField()

    # 创建时间
    create_time = DateTimeField()
    # 更新时间
    update_time = StringField()


if __name__ == '__main__':
    # 增加
    user = StockModel.add({'name': 'Tom', 'age': 25})
    print(user.to_json())
    # 更新
    StockModel.update(user.id, {'age': 26})
    # 查询列表
    users = StockModel.list()
    # 条件查询
    users_named_tom = StockModel.list_by({'name': 'Tom'})
    # 分页
    page_data = StockModel.page(page=1, page_size=2)
    print(page_data)
    # 删除
    # StockModel.delete(str(user.id))
