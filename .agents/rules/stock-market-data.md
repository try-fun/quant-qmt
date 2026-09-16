# 行情数据获取与订阅规范 (`xtdata`)

## 1. 标的代码命名规范
- 上海证券交易所：后缀 `.SH`（例如：`600000.SH`, `600519.SH`）
- 深圳证券交易所：后缀 `.SZ`（例如：`000001.SZ`, `300750.SZ`）
- 北京证券交易所：后缀 `.BJ`（例如：`830000.BJ`）

## 2. 支持周期类型
- Tick 级：`'tick'`
- 分钟级：`'1m'`, `'5m'`, `'15m'`, `'30m'`, `'60m'`
- 日线级：`'1d'`

## 3. 常用接口调用范式
1. **历史数据下载与读取**：
   - 必须先调用 `xtdata.download_history_data(stock_code, period, start_time, end_time)` 下载至本地缓存；
   - 再使用 `xtdata.get_market_data_ex()` 读取结构化数据。
2. **实时行情订阅**：
   - 使用 `seq = xtdata.subscribe_quote(stock_code, period='tick', callback=on_quote)` 订阅；
   - 在程序退出前调用 `xtdata.unsubscribe_quote(seq)` 注销订阅。
