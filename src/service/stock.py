# coding=gbk
"""
实时价格获取示例：使用 get_market_data_ex 获取股票当前时刻最新价格
"""
from xtquant import xtdata
import datetime
import time

'''
获取股票相关信息
1. 获取股票实时价格
'''


def get_realtime_price(stock_code):
    """
    获取股票实时价格

    Args:
        stock_code (str): 股票代码，如 '000001.SZ'

    Returns:
        float: 股票实时价格
    """
    today = datetime.datetime.now().strftime('%Y%m%d')

    # 使用1分钟周期获取实时价格
    market_data = xtdata.get_market_data_ex(
        field_list=['close'],
        stock_list=[stock_code],
        period='1m',  # 1分钟周期
        start_time=today + '0930',  # 开盘时间
        end_time=today + '1500',  # 收盘时间
        count=1  # 获取最新1条数据
    )

    if market_data and stock_code in market_data and len(market_data[stock_code]) > 0:
        return market_data[stock_code]['close'].iloc[-1]
    return 0


def monitor_price(stock_code, interval=5):
    """
    持续监控股票价格

    Args:
        stock_code (str): 股票代码
        interval (int): 监控间隔（秒）
    """
    print(f"开始监控股票 {stock_code} 的实时价格，间隔 {interval} 秒")
    print("按 Ctrl+C 停止监控")

    try:
        while True:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            price = get_realtime_price(stock_code)

            if price > 0:
                print(f"[{current_time}] {stock_code}: {price}")
            else:
                print(f"[{current_time}] {stock_code}: 无法获取价格")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n监控已停止")


def get_multiple_realtime_prices(stock_codes):
    """
    批量获取多个股票的实时价格

    Args:
        stock_codes (list): 股票代码列表

    Returns:
        dict: 股票代码和价格的字典
    """
    today = datetime.datetime.now().strftime('%Y%m%d')

    market_data = xtdata.get_market_data_ex(
        field_list=['close'],
        stock_list=stock_codes,
        period='1m',
        start_time=today + '0930',
        end_time=today + '1500',
        count=1
    )

    prices = {}
    for stock_code in stock_codes:
        if market_data and stock_code in market_data and len(market_data[stock_code]) > 0:
            prices[stock_code] = market_data[stock_code]['close'].iloc[-1]
        else:
            prices[stock_code] = 0

    return prices


if __name__ == "__main__":
    # 示例1：获取单个股票实时价格
    print("=== 获取单个股票实时价格 ===")
    price = get_realtime_price('000001.SZ')
    print(f"平安银行实时价格: {price}")

    # 示例2：批量获取多个股票实时价格
    print("\n=== 批量获取多个股票实时价格 ===")
    stock_list = ['000001.SZ', '600519.SH', '002878.SZ']
    prices = get_multiple_realtime_prices(stock_list)

    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] 实时价格汇总:")
    for code, price in prices.items():
        print(f"  {code}: {price}")

    # 示例3：持续监控价格（可选）
    # print("\n=== 开始价格监控 ===")
    # monitor_price('000001.SZ', interval=10)
