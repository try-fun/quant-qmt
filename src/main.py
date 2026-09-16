# coding=gbk
"""
量化交易系统主入口 (MiniQMT xtquant)
支持命令行快速触发盘后选股器、盘中持仓风控执行引擎或单标的行情下载
"""
import sys
import argparse
import datetime
from src.strategy.screener import run_daily_selection
from src.strategy.executor import BollRiskExecutor
from src.service.qmt_connnect import download_one_stock_data


def main():
    parser = argparse.ArgumentParser(description="MiniQMT 量化交易系统调度入口")
    parser.add_argument(
        "--mode",
        choices=["screen", "trade", "download", "all"],
        default="screen",
        help="运行模式: screen(盘后选股), trade(盘中交易与风控), download(下载日线), all(全流程)"
    )
    parser.add_argument("--stock", type=str, default="000001.SZ", help="股票标的代码，默认 000001.SZ")
    parser.add_argument("--period", type=str, default="1d", help="K线周期，默认 1d")

    args = parser.parse_args()

    print("==================================================")
    print(f"[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 启动模式: {args.mode}")
    print("==================================================")

    if args.mode == "screen":
        print(">> 执行盘后选股器 (三指标共振 + 强势股精选)...")
        targets = run_daily_selection()
        print(f">> 选股完成，共精选 {len(targets)} 只标的。")

    elif args.mode == "trade":
        print(">> 启动盘中交易与持仓风控执行引擎...")
        executor = BollRiskExecutor()
        executor.connect_and_init()
        executor.run_trading_loop(poll_interval=5)

    elif args.mode == "download":
        start_date = datetime.datetime.now().strftime("%Y%m%d")
        print(f">> 下载股票 {args.stock} 的 {args.period} 行情数据...")
        download_one_stock_data(args.stock, args.period, start_date, "")

    elif args.mode == "all":
        print(">> 运行全流程：先执行盘后选股，随后启动交易引擎...")
        run_daily_selection()
        executor = BollRiskExecutor()
        executor.connect_and_init()
        executor.run_trading_loop(poll_interval=5)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序退出，异常信息: {e}")
