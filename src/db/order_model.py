# coding=gbk
from mongoengine import StringField, IntField, FloatField, BooleanField, DateTimeField
from src.db.base_model import BaseModel


'''
account_type	int	�˺����ͣ��μ������ֵ�
account_id	str	�ʽ��˺�
stock_code	str	֤ȯ���룬����"600000.SH"
order_id	int	�������
order_sysid	str	��̨��ͬ���
order_time	int	����ʱ��
order_type	int	ί�����ͣ��μ������ֵ�
order_volume	int	ί������
price_type	int	�������ͣ����ֶ��ڷ���ʱΪ��̨�������ͣ����ȼ����µ������price_type��ö��ֵ��һ������һ�����μ������ֵ�
price	float	ί�м۸�
traded_volume	int	�ɽ�����
traded_price	float	�ɽ�����
order_status	int	ί��״̬���μ������ֵ�
status_msg	str	ί��״̬��������ϵ�ԭ��
strategy_name	str	��������
order_remark	str	ί�б�ע����� 24 ��Ӣ���ַ�
direction	int	��շ��򣬹�Ʊ�����ã��μ������ֵ�
offset_flag	int	���ײ������ô��ֶ����ֹ�Ʊ�������ڻ�����ƽ�֣���Ȩ�����ȣ��μ������ֵ�


'''

# ί�е�


class OrderModel(BaseModel):
    meta = {'collection': 'tb_order'}
    # �˺�����
    account_type = IntField()
    # �ʽ��˺�
    account_id = StringField()
    # ֤ȯ����
    stock_code = StringField()
    # �������
    order_id = IntField()
    # ��̨��ͬ���
    order_sysid = StringField()
    # ����ʱ��
    order_time = IntField()
    # ί������
    order_type = IntField()
    # ί������
    order_volume = IntField()
    # ��������
    price_type = IntField()
    # ί�м۸�
    price = FloatField()
    # �ɽ�����
    traded_volume = IntField()
    # �ɽ�����
    traded_price = FloatField()
    # ί��״̬
    order_status = IntField()
    # ί��״̬����
    status_msg = StringField()
    # ��������
    strategy_name = StringField()
    # ί�б�ע
    order_remark = StringField()
    # ����ʱ��
    create_time = DateTimeField()
    # ����ʱ��
    update_time = DateTimeField()
