# coding=gbk
"""
A股多因子共振与布林带策略 - 盘后选股器
每日 15:10 后运行，实现全市场基础过滤、三大技术指标共振初筛以及强势股精选 (Top 20)
"""
import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIR))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import json
import datetime
from typing import List, Dict, Any
import pandas as pd
from xtquant import xtdata
from src.strategy.factors import check_three_resonance, compute_boll


def filter_basic_safety(stock_list: List[str]) -> List[str]:
    """
    基础安全与流动性过滤：
    1. 剔除 ST, *ST, 退市标的
    2. 剔除上市不足 30 天的次新股

    Args:
        stock_list (List[str]): 待筛选股票代码列表

    Returns:
        List[str]: 通过基础过滤的股票代码列表
    """
    valid_stocks = []
    now = datetime.datetime.now()

    for code in stock_list:
        detail = xtdata.get_instrument_detail(code)
        if not detail:
            continue

        # 1. 剔除 ST 与 退市股
        name = detail.get('InstrumentName', '')
        if 'ST' in name or '退' in name or '*ST' in name:
            continue

        # 2. 剔除上市不足 30 日次新股
        open_date_str = str(detail.get('OpenDate', ''))
        if open_date_str and len(open_date_str) >= 8:
            try:
                open_date = datetime.datetime.strptime(open_date_str[:8], '%Y%m%d')
                if (now - open_date).days < 30:
                    continue
            except Exception:
                pass

        valid_stocks.append(code)

    return valid_stocks


def screen_resonance_pool(valid_stocks: List[str], max_pool_size: int = 200) -> List[Dict[str, Any]]:
    """
    三大技术指标共振筛选（均量金叉 + RSI突破 + OBV金叉）及流动性过滤

    Args:
        valid_stocks (List[str]): 股票列表
        max_pool_size (int): 初选池最大容量，默认200只

    Returns:
        List[Dict[str, Any]]: 初选共振股票池数据列表
    """
    if not valid_stocks:
        return []

    # 1. 批量下载最近60个交易日日K线
    start_date = (datetime.datetime.now() - datetime.timedelta(days=120)).strftime('%Y%m%d')
    print(f">> 正在下载/同步 {len(valid_stocks)} 只标的日线行情 (首次下载约需1~2分钟，请稍候)...")
    try:
        xtdata.download_history_data2(valid_stocks, period='1d', start_time=start_date)
        print(">> 日线历史行情下载完成，开始批量读取与计算技术因子...")
    except Exception as e:
        print(f"下载历史日线数据提示/警告: {e}")

    # 2. 批量读取K线数据
    kline_dict = xtdata.get_market_data_ex(
        field_list=['close', 'volume', 'amount'],
        stock_list=valid_stocks,
        period='1d',
        count=60
    )

    print(">> 正在计算三大指标共振 (均量金叉 + RSI>55突破 + OBV金叉)...")
    resonance_list = []
    for code in valid_stocks:
        df = kline_dict.get(code)
        if df is None or len(df) < 40:
            continue

        # 过滤日均成交额 < 1亿元 (以最近20日均值为准)
        recent_20_amount = df['amount'].iloc[-20:].mean()
        if recent_20_amount < 1.0e8:
            continue

        # 校验三指标共振
        if not check_three_resonance(df):
            continue

        close = df['close'].iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ret_5d = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1.0) if len(df) >= 6 else 0.0

        # 获取流通市值信息
        detail = xtdata.get_instrument_detail(code) or {}
        name = detail.get('InstrumentName', '')
        float_volume = detail.get('FloatVolume', 0)
        float_market_cap = float_volume * close if float_volume > 0 else 0.0
        turnover_rate = (df['volume'].iloc[-1] / float_volume * 100.0) if float_volume > 0 else 0.0

        resonance_list.append({
            'code': code,
            'name': name,
            'close': round(close, 2),
            'ma20': round(ma20, 2),
            'ret_5d': ret_5d,
            'amount_20d_avg': recent_20_amount,
            'float_market_cap': float_market_cap,
            'turnover_rate': turnover_rate
        })

    # 若入围超过 max_pool_size，按近5日涨幅与成交额排序截断取前 max_pool_size 只
    if len(resonance_list) > max_pool_size:
        resonance_list = sorted(resonance_list, key=lambda x: x['ret_5d'], reverse=True)[:max_pool_size]

    return resonance_list


def select_strong_stocks(resonance_pool: List[Dict[str, Any]], max_select: int = 20) -> List[Dict[str, Any]]:
    """
    强势股二次精选（标准优先级）：
    1. 收盘价站上 20 日均线 (Close > MA20)
    2. 近 5 日涨幅 > 0
    3. 换手率介于 3% ~ 10% (若换手率数据有效)
    4. 流通市值介于 100亿 ~ 3000亿元 (若流通市值数据有效)

    Args:
        resonance_pool (List[Dict[str, Any]]): 初选共振股票池
        max_select (int): 精选目标数量，默认20只

    Returns:
        List[Dict[str, Any]]: 精选的Top N强势买入标的
    """
    candidates = []

    for item in resonance_pool:
        # 条件1: Close > MA20
        if item['close'] <= item['ma20']:
            continue

        # 条件2: 近5日涨幅 > 0
        if item['ret_5d'] <= 0:
            continue

        # 条件3: 换手率 3% ~ 10% (若具备换手率数据时进行过滤)
        tr = item.get('turnover_rate', 0.0)
        if tr > 0 and (tr < 3.0 or tr > 10.0):
            continue

        # 条件4: 流通市值 100亿 ~ 3000亿 (若具备市值数据时进行过滤)
        cap = item.get('float_market_cap', 0.0)
        if cap > 0 and (cap < 1.0e10 or cap > 3.0e11):
            continue

        candidates.append(item)

    # 排序规则：按近5日涨幅降序排列
    candidates = sorted(candidates, key=lambda x: x['ret_5d'], reverse=True)
    return candidates[:max_select]


def run_daily_selection(save_path: str = 'data/target_pool.json') -> List[Dict[str, Any]]:
    """
    执行完整的每日盘后选股流程，并持久化结果到文件

    Args:
        save_path (str): 目标池保存路径

    Returns:
        List[Dict[str, Any]]: 最终精选买入标的列表
    """
    today_str = datetime.datetime.now().strftime('%Y%m%d')
    print("==================================================")
    print(f"[{today_str}] 启动盘后选股流程 (三指标共振 + 强势股精选)")
    print("==================================================")

    # 1. 获取沪深A股全市场标的
    all_stocks = xtdata.get_stock_list_in_sector('沪深A股')
    print(f"1. 全市场标的总数: {len(all_stocks)} 只")

    # 2. 基础安全与流动性过滤
    valid_stocks = filter_basic_safety(all_stocks)
    print(f"2. 基础过滤后标的数: {len(valid_stocks)} 只")

    # 3. 三指标共振筛选
    resonance_pool = screen_resonance_pool(valid_stocks, max_pool_size=200)
    print(f"3. 三指标共振初选标的数: {len(resonance_pool)} 只")

    # 4. 强势股精选 Top 20
    top_targets = select_strong_stocks(resonance_pool, max_select=20)
    print(f"4. 最终精选买入标的 (Top {len(top_targets)}):")
    for idx, item in enumerate(top_targets, start=1):
        print(f"   [{idx:02d}] {item['code']} {item['name']} | 收盘: {item['close']} | MA20: {item['ma20']} | 5日涨幅: {item['ret_5d']*100:.2f}%")

    # 5. 持久化存储
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
    payload = {
        'date': today_str,
        'count': len(top_targets),
        'targets': top_targets,
        'target_codes': [item['code'] for item in top_targets]
    }
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"5. 选股结果已保存至: {save_path}")
    return top_targets


if __name__ == "__main__":
    run_daily_selection()
