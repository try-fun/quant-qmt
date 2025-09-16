# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel


class StockModel(BaseModel):
    meta = {'collection': 'tb_stock'}
    # ��Ʊ����
    code = StringField()
    # ������ID
    exchange_id = StringField()
    # ��Ʊ����
    instrument_id = StringField()
    # ��Ʊ����
    instrument_name = StringField()
    # ��������
    open_date = StringField()
    # ��������
    expire_date = IntField()
    # ǰ���̼�
    pre_close = FloatField()
    # �����
    settlement_price = FloatField()
    # ��ͣ��
    up_stop_price = FloatField()
    # ��ͣ��
    down_stop_price = FloatField()
    # ��ͨ��ֵ
    float_volume = FloatField()
    # ����ֵ
    total_volume = FloatField()
    # ��Ʊ״̬
    instrument_status = IntField()
    # �Ƿ���
    is_trading = BooleanField()

    # �Ƿ�����
    is_buy = BooleanField()

    # ����ʱ��
    create_time = DateTimeField()
    # ����ʱ��
    update_time = StringField()


if __name__ == '__main__':
    # ����
    user = StockModel.add({'name': 'Tom', 'age': 25})
    print(user.to_json())
    # ����
    StockModel.update(user.id, {'age': 26})
    # ��ѯ����
    users = StockModel.list()
    # ������ѯ
    users_named_tom = StockModel.list_by({'name': 'Tom'})
    # ��ҳ
    page_data = StockModel.page(page=1, page_size=2)
    print(page_data)
    # ɾ��
    # StockModel.delete(str(user.id))
