import time
from stock.strategy.download import download_all_stock_data


def main():
    # 1. download stock data of today
    start_date = time.strftime('%Y%m%d')
    end_date = ""
    download_all_stock_data("1d", start_date, end_date)


if __name__ == "__main__":
    main()
