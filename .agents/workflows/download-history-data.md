# 历史行情数据下载与落盘工作流 (Download History Data)

当需要下载或更新股票的历史行情（日线/分钟线/Tick）时，执行此工作流：

## 步骤 1：确认下载参数
- **标的列表**：单个标的（如 `'000001.SZ'`）或行业板块股票池。
- **数据周期**：`'1d'` (日线), `'1m'` (1分钟), `'5m'` (5分钟), `'tick'` (逐笔)。
- **时间范围**：`start_time` (格式 `'YYYYMMDD'`)，`end_time` (留空代表至最新)。

## 步骤 2：调用下载接口
在 `src/main.py` 或脚本中调用：
```python
# coding=gbk
from src.service.qmt_connnect import download_one_stock_data

# 下载指定标的
download_one_stock_data(stock="000001.SZ", period="1d", start_date="20240101", end_date="")
```

## 步骤 3：验证数据完整性
运行 `src/service/test_market_data.py` 验证数据已成功落盘至本地 MiniQMT 缓存并可正常被 `get_market_data_ex` 检索。
