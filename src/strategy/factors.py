# coding=gbk
"""
A股多因子共振与布林带策略 - 技术因子计算工具
包含均量金叉、RSI(14)、OBV(30)金叉、BOLL(20,2)等技术指标计算
"""
from typing import Tuple
import numpy as np
import pandas as pd


def compute_vol_ma_cross(vol_series: pd.Series, short_period: int = 5, long_period: int = 38) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算成交量均线及其金叉信号

    Args:
        vol_series (pd.Series): 成交量序列
        short_period (int): 短期均量周期，默认5日
        long_period (int): 长期均量周期，默认38日

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: (ma_vol_short, ma_vol_long, is_golden_cross)
    """
    ma_short = vol_series.rolling(window=short_period, min_periods=short_period).mean()
    ma_long = vol_series.rolling(window=long_period, min_periods=long_period).mean()

    # 当日短期 > 长期 且 前一日短期 <= 长期
    is_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
    return ma_short, ma_long, is_cross


def compute_rsi(close_series: pd.Series, period: int = 14) -> pd.Series:
    """
    计算相对强弱指标 RSI

    Args:
        close_series (pd.Series): 收盘价序列
        period (int): 计算周期，默认14日

    Returns:
        pd.Series: RSI指标序列 (0~100)
    """
    delta = close_series.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    # 采用标准简单移动平均（SMA）平滑
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def compute_obv(close_series: pd.Series, vol_series: pd.Series, ma_period: int = 30) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算能量潮 OBV 及其均线与金叉信号

    Args:
        close_series (pd.Series): 收盘价序列
        vol_series (pd.Series): 成交量序列
        ma_period (int): OBV移动平均周期，默认30日

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: (obv, ma_obv, is_golden_cross)
    """
    direction = np.sign(close_series.diff().fillna(0.0))
    # 若涨跌幅为0，则方向为0
    obv = (direction * vol_series).cumsum()
    ma_obv = obv.rolling(window=ma_period, min_periods=ma_period).mean()

    # 当日OBV > MAOBV 且 前一日OBV <= MAOBV
    is_cross = (obv > ma_obv) & (obv.shift(1) <= ma_obv.shift(1))
    return obv, ma_obv, is_cross


def compute_boll(close_series: pd.Series, n: int = 20, k: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带 BOLL 指标 (中轨 MID, 上轨 UP, 下轨 LOW)

    Args:
        close_series (pd.Series): 收盘价序列
        n (int): 均线与标准差计算周期，默认20日
        k (float): 标准差倍数，默认2.0

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: (mid, up, low)
    """
    mid = close_series.rolling(window=n, min_periods=n).mean()
    std = close_series.rolling(window=n, min_periods=n).std(ddof=0)
    up = mid + k * std
    low = mid - k * std
    return mid, up, low


def check_three_resonance(df: pd.DataFrame) -> bool:
    """
    检查是否满足三大技术指标共振：
    1. 5日均量线上穿38日均量线
    2. 14日RSI上穿55
    3. OBV线上穿30日OBV均线

    Args:
        df (pd.DataFrame): 包含 'close' 与 'volume' 字段的日线行情数据 (行数建议 >= 40)

    Returns:
        bool: 是否满足三指标共振
    """
    if df is None or len(df) < 40:
        return False

    close_series = df['close']
    vol_series = df['volume']

    # 1. 均量线金叉
    _, _, vol_cross = compute_vol_ma_cross(vol_series, 5, 38)
    if not vol_cross.iloc[-1]:
        return False

    # 2. RSI(14) 上穿 55
    rsi = compute_rsi(close_series, 14)
    rsi_cross = (rsi.iloc[-1] > 55.0) and (rsi.iloc[-2] <= 55.0)
    if not rsi_cross:
        return False

    # 3. OBV(30) 金叉
    _, _, obv_cross = compute_obv(close_series, vol_series, 30)
    if not obv_cross.iloc[-1]:
        return False

    return True
