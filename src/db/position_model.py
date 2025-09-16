# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel

'''
account_type	int	�˺����ͣ��μ������ֵ�
account_id	str	�ʽ��˺�
stock_code	str	֤ȯ����
volume	int	�ֲ�����
can_use_volume	int	��������
open_price	float	���ּ�
market_value	float	��ֵ
frozen_volume	int	��������
on_road_volume	int	��;�ɷ�
yesterday_volume	int	��ҹӵ��
avg_price	float	�ɱ���
direction	int	��շ��򣬹�Ʊ�����ã��μ������ֵ�


'''

# �ֲ�


class PositionModel(BaseModel):
    meta = {'collection': 'tb_position'}
    # �˺�����
    account_type = IntField()
    # �ʽ��˺�
    account_id = StringField()
    # ֤ȯ����
    stock_code = StringField()
    # �ֲ�����
    volume = IntField()
    # ��������
    can_use_volume = IntField()
    # ���ּ�
    open_price = FloatField()
    # ��ֵ
    market_value = FloatField()
    # ��������
    frozen_volume = IntField()
    # ��;�ɷ�
    on_road_volume = IntField()
    # ��ҹӵ��
    yesterday_volume = IntField()
    # ����ʱ��
    create_time = DateTimeField()
    # ����ʱ��
    update_time = DateTimeField()
