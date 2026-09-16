# coding=gbk
import time
from src.service.qmt_connnect import download_one_stock_data


def main():
    # 1. 下载今日标的数据
    start_date = time.strftime('%Y%m%d')
    end_date = ""
    download_one_stock_data("000001.SZ", "1d", start_date, end_date)


if __name__ == "__main__":
    main()
