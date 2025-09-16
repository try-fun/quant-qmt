# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel

'''
account_type	int	�˺����ͣ��μ������ֵ�
account_id	str	�ʽ��˺�
stock_code	str	֤ȯ����
order_type	int	ί�����ͣ��μ������ֵ�
traded_id	str	�ɽ����
traded_time	int	�ɽ�ʱ��
traded_price	float	�ɽ�����
traded_volume	int	�ɽ�����
traded_amount	float	�ɽ����
order_id	int	�������
order_sysid	str	��̨��ͬ���
strategy_name	str	��������
order_remark	str	ί�б�ע����� 24 ��Ӣ���ַ�(
direction	int	��շ��򣬹�Ʊ�����ã��μ������ֵ�
offset_flag	int	���ײ������ô��ֶ����ֹ�Ʊ�������ڻ�����ƽ�֣���Ȩ�����ȣ��μ������ֵ�

'''

# �ɽ�


class TradeModel(BaseModel):
    meta = {'collection': 'tb_trade'}
    # �˺�����
    account_type = IntField()
    # �ʽ��˺�
    account_id = StringField()
    # ֤ȯ����
    stock_code = StringField()
    # ί������
    order_type = IntField()
    # �ɽ����
    traded_id = StringField()
    # �ɽ�ʱ��
    traded_time = IntField()
    # �ɽ�����
    traded_price = FloatField()
    # �ɽ�����
    traded_volume = IntField()
    # �ɽ����
    traded_amount = FloatField()
    # �������
    order_id = IntField()
    # ��̨��ͬ���
    order_sysid = StringField()
    # ��������
    strategy_name = StringField()
    # ί�б�ע
    order_remark = StringField()
    # ����ʱ��
    create_time = DateTimeField()
    # ����ʱ��
    update_time = DateTimeField()
