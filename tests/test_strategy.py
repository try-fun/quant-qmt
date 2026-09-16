# coding=gbk
"""
A股多因子共振与布林带策略 - 离线单元测试
验证指标计算、选股过滤与风控逻辑
"""
import unittest
import numpy as np
import pandas as pd
from src.strategy.factors import (
    compute_vol_ma_cross,
    compute_rsi,
    compute_obv,
    compute_boll,
    check_three_resonance
)
from src.strategy.screener import select_strong_stocks


class TestStrategyFactors(unittest.TestCase):
    """测试因子计算模块"""

    def setUp(self):
        # 构造模拟测试行情数据 (50天)
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=50, freq='B')
        prices = 10.0 + np.cumsum(np.random.randn(50) * 0.2)
        volumes = np.random.randint(10000, 50000, size=50)

        self.df = pd.DataFrame({
            'close': prices,
            'volume': volumes,
            'amount': prices * volumes
        }, index=dates)

    def test_compute_vol_ma_cross(self):
        """测试均量线金叉计算"""
        ma_short, ma_long, cross = compute_vol_ma_cross(self.df['volume'], 5, 38)
        self.assertEqual(len(ma_short), len(self.df))
        self.assertEqual(len(ma_long), len(self.df))
        self.assertIsInstance(cross, pd.Series)

    def test_compute_rsi(self):
        """测试 RSI 计算"""
        rsi = compute_rsi(self.df['close'], period=14)
        self.assertEqual(len(rsi), len(self.df))
        # RSI 必须在 0 到 100 之间（非 NaN 部分）
        valid_rsi = rsi.dropna()
        self.assertTrue((valid_rsi >= 0).all() and (valid_rsi <= 100).all())

    def test_compute_obv(self):
        """测试 OBV 及均线计算"""
        obv, ma_obv, cross = compute_obv(self.df['close'], self.df['volume'], 30)
        self.assertEqual(len(obv), len(self.df))
        self.assertEqual(len(ma_obv), len(self.df))
        self.assertIsInstance(cross, pd.Series)

    def test_compute_boll(self):
        """测试布林带 (MID, UP, LOW) 计算"""
        mid, up, low = compute_boll(self.df['close'], n=20, k=2.0)
        self.assertEqual(len(mid), len(self.df))
        valid_idx = ~mid.isna()
        # 上轨 >= 中轨 >= 下轨
        self.assertTrue((up[valid_idx] >= mid[valid_idx]).all())
        self.assertTrue((mid[valid_idx] >= low[valid_idx]).all())

    def test_select_strong_stocks(self):
        """测试强势股筛选"""
        mock_pool = [
            {'code': '000001.SZ', 'name': '平安银行', 'close': 12.0, 'ma20': 11.0, 'ret_5d': 0.05, 'turnover_rate': 4.0, 'float_market_cap': 2.0e10},
            {'code': '000002.SZ', 'name': '万科A', 'close': 8.0, 'ma20': 9.0, 'ret_5d': 0.02, 'turnover_rate': 5.0, 'float_market_cap': 3.0e10},  # Close < MA20 排除
            {'code': '600519.SH', 'name': '贵州茅台', 'close': 1800.0, 'ma20': 1700.0, 'ret_5d': -0.01, 'turnover_rate': 2.0, 'float_market_cap': 2.0e12},  # ret_5d < 0 排除
            {'code': '600000.SH', 'name': '浦发银行', 'close': 10.0, 'ma20': 9.5, 'ret_5d': 0.08, 'turnover_rate': 6.0, 'float_market_cap': 5.0e10},
        ]

        strong = select_strong_stocks(mock_pool, max_select=20)
        codes = [item['code'] for item in strong]
        self.assertIn('000001.SZ', codes)
        self.assertIn('600000.SH', codes)
        self.assertNotIn('000002.SZ', codes)
        self.assertNotIn('600519.SH', codes)


if __name__ == '__main__':
    unittest.main()
