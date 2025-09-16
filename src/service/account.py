# coding=gbk
from xtquant.xtpythonclient import XtAsset
import datetime
from src.db.account import AccountModel


def update_account(account_info: XtAsset):

    # 取账号信息
    model = AccountModel.objects(account_id=account_info.account_id).first()
    if model is None:
        model = AccountModel()
        model.create_time = datetime.datetime.now()

    model.account_id = account_info.account_id
    model.account_type = account_info.account_type
    model.cash = account_info.cash
    model.frozen_cash = account_info.frozen_cash
    model.market_value = account_info.market_value
    model.total_asset = account_info.total_asset
    model.update_time = datetime.datetime.now()
    return model.save()
