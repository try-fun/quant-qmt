# coding=gbk
from mongoengine import StringField, IntField, FloatField, DateTimeField
from src.db.base_model import BaseModel


# �ʲ�
class AccountModel(BaseModel):
    meta = {'collection': 'tb_account'}
    # �˺�����
    account_type = IntField()
    # �ʽ��˺�
    account_id = StringField()
    # ���ý��
    cash = FloatField()
    # ������
    frozen_cash = FloatField()
    # �ֲ���ֵ
    market_value = FloatField()
    # ���ʲ�
    total_asset = FloatField()
    # ����ʱ��
    create_time = DateTimeField()
    # ����ʱ��
    update_time = DateTimeField()
