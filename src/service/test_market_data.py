# coding=gbk
"""
测试 get_market_data_ex 功能
"""

import datetime
from xtquant import xtdata


def test_get_market_data_ex():
    """
    测试 get_market_data_ex 的各种用法
    """
    # 测试股票代码
    test_stock = "000001.SZ"

    print(f"=== 测试股票: {test_stock} ===")

    # 获取当前日期
    today = datetime.datetime.now().strftime('%Y%m%d')
    print(f"当前日期: {today}")

    # 测试1：获取当日分时数据
    print("\n1. 测试获取当日分时数据:")
    try:
        minute_data = xtdata.get_market_data_ex(
            field_list=['close', 'open', 'high', 'low', 'volume'],
            stock_list=[test_stock],
            period='1m',
            start_time=today + '0930',
            end_time=today + '1500',
            count=5  # 获取最近5条数据
        )

        if minute_data and len(minute_data) > 0:
            print(f"获取到 {len(minute_data)} 个字段的数据")
            for i, field_data in enumerate(minute_data):
                if len(field_data) > 0:
                    print(f"字段 {i}: 最新值 = {field_data[-1]}")
        else:
            print("未获取到分时数据")

    except Exception as e:
        print(f"获取分时数据失败: {e}")

    # 测试2：获取当日日线数据
    print("\n2. 测试获取当日日线数据:")
    try:
        daily_data = xtdata.get_market_data_ex(
            field_list=['close', 'open', 'high', 'low', 'volume'],
            stock_list=[test_stock],
            period='1d',
            start_time=today,
            end_time=today,
            count=1
        )

        if daily_data and len(daily_data) > 0:
            print(f"获取到 {len(daily_data)} 个字段的日线数据")
            for i, field_data in enumerate(daily_data):
                if len(field_data) > 0:
                    print(f"字段 {i}: 值 = {field_data[-1]}")
        else:
            print("未获取到日线数据")

    except Exception as e:
        print(f"获取日线数据失败: {e}")

    # 测试3：获取历史数据
    print("\n3. 测试获取历史数据:")
    try:
        start_date = (datetime.datetime.now() -
                      datetime.timedelta(days=5)).strftime('%Y%m%d')

        historical_data = xtdata.get_market_data_ex(
            field_list=['close'],
            stock_list=[test_stock],
            period='1d',
            start_time=start_date,
            end_time=today,
            count=5
        )

        if historical_data and len(historical_data) > 0 and len(historical_data[0]) > 0:
            print(f"获取到 {len(historical_data[0])} 天的历史收盘价:")
            for i, price in enumerate(historical_data[0]):
                print(f"第 {i+1} 天: {price}")
        else:
            print("未获取到历史数据")

    except Exception as e:
        print(f"获取历史数据失败: {e}")

    # 测试4：测试价格获取函数
    print("\n4. 测试价格获取函数:")
    try:
        from src.stock.trander.trading_demo import get_current_price

        current_price = get_current_price(test_stock)
        print(f"获取到的当前价格: {current_price}")

    except Exception as e:
        print(f"测试价格获取函数失败: {e}")


def test_multiple_stocks():
    """
    测试多只股票的数据获取
    """
    test_stocks = ["000001.SZ", "000002.SZ", "600000.SH"]

    print(f"\n=== 测试多只股票: {test_stocks} ===")

    today = datetime.datetime.now().strftime('%Y%m%d')

    try:
        # 获取多只股票的收盘价
        multi_data = xtdata.get_market_data_ex(
            field_list=['close'],
            stock_list=test_stocks,
            period='1d',
            start_time=today,
            end_time=today,
            count=1
        )

        if multi_data and len(multi_data) > 0:
            print(f"获取到 {len(multi_data[0])} 只股票的数据:")
            for i, price in enumerate(multi_data[0]):
                if i < len(test_stocks):
                    print(f"{test_stocks[i]}: {price}")
        else:
            print("未获取到多只股票数据")

    except Exception as e:
        print(f"获取多只股票数据失败: {e}")


if __name__ == '__main__':
    # 初始化xtdata
    try:
        xtdata.download_sector_data()
        print("xtdata初始化成功")
    except Exception as e:
        print(f"xtdata初始化失败: {e}")

    # 运行测试
    test_get_market_data_ex()
    test_multiple_stocks()
