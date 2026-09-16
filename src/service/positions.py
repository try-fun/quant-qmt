# coding=gbk
from xtquant.xtpythonclient import XtPosition
import datetime
from src.db.position_model import PositionModel


def update_position(positions):
    """
    同步持仓信息至数据库
    :param positions: XtPosition 对象列表或单个 XtPosition
    """
    if not positions:
        return
    if not isinstance(positions, list):
        positions = [positions]

    for position in positions:
        model = PositionModel.objects(stock_code=position.stock_code).first()
        if model is None:
            model = PositionModel()
            model.create_time = datetime.datetime.now()

        model.account_type = position.account_type
        model.account_id = position.account_id
        model.stock_code = position.stock_code
        model.volume = position.volume
        model.can_use_volume = position.can_use_volume
        model.open_price = position.open_price
        model.market_value = position.market_value
        model.frozen_volume = position.frozen_volume
        model.on_road_volume = position.on_road_volume
        model.yesterday_volume = position.yesterday_volume
        model.update_time = datetime.datetime.now()
        model.save()
