# MiniQMT (xtquant) 开发与 Agent 操作指南

本文档为参与本项目（MiniQMT 量化交易系统）开发的 **AI Agent** 与 **开发者** 提供权威指导与统一规范。在进行任何代码编写、重构、策略实现或问题排查前，必须严格遵守本文档所列出的规范与约束。

---

## 1. 项目定位与架构总览

### 1.1 项目简介
本项目是基于迅投 **MiniQMT (xtquant)** 原生 Python SDK 构建的 A 股量化交易与行情数据管理系统。主要功能包括：
- **实时与历史行情数据获取**：基于 `xtquant.xtdata` 提供多周期（Tick、1m、5m、1d 等）行情订阅与历史数据落盘。
- **实盘/模拟交易接入**：基于 `xtquant.xttrader` 实现委托下单、撤单、资产查询、持仓监控及异步回调处理。
- **本地轻量数据持久化**：采用原子化 JSON 文件（`data/*.json`）实现账户资产、委托订单、成交明细、持仓股票以及盘后选股目标池的持久化与直观查看。

### 1.2 目录结构规范

```text
qmt/
├── README.md              # 项目简要说明与官方文档索引
├── Makefile               # 项目常用构建与清理命令 (make clean 等)
├── requirements.txt       # Python 依赖清单
├── AGENTS.md              # 本规范文档 (AI Agent & 开发者操作指南)
├── data/                  # 本地 JSON 数据持久化目录
│   ├── target_pool.json   # 每日盘后选股目标池
│   ├── account.json       # 资金账户资产最新快照
│   ├── positions.json     # 当前持仓股票明细列表
│   ├── orders.json        # 委托订单历史与状态记录
│   └── trades.json        # 实际成交明细记录
└── src/
    ├── __init__.py
    ├── main.py            # 主程序入口 (选股/实盘交易/数据下载等)
    ├── config/            # 配置管理模块
    │   ├── __init__.py
    │   ├── config.py      # 配置读取单例类与 Dataclass 映射
    │   ├── config.ini     # 生产/默认配置文件 (不得提交敏感凭据)
    │   └── config-dev.ini # 本地开发测试配置文件
    ├── strategy/          # 策略与风控执行引擎
    │   ├── __init__.py
    │   ├── factors.py     # 技术指标与多因子共振计算 (KDJ, RSI, MACD, BOLL 等)
    │   ├── screener.py    # 每日盘后选股器 (全市场初筛 + Top 20 精选)
    │   └── executor.py    # 盘中交易与持仓风控执行引擎 (开盘建仓 + 止盈止损)
    └── service/           # 业务逻辑与 MiniQMT 交互服务
        ├── __init__.py
        ├── storage.py     # JSON 原子安全读写底层工具
        ├── qmt_connnect.py# QMT 客户端连接、账号初始化、数据下载
        ├── trading.py     # 核心交易事件循环、行情回调与交易决策示例
        ├── stock.py       # 股票价格获取与行情监控工具
        ├── account.py     # 资金账户信息 JSON 同步
        ├── order.py       # 委托订单信息 JSON 幂等同步
        ├── positions.py   # 持仓信息 JSON 同步
        ├── trade.py       # 成交回报信息 JSON 幂等同步
        └── test_market_data.py # 行情数据测试脚本
```

---

## 2. MiniQMT 核心开发红线与硬性约束

### 2.1 文件编码规范（⚠️ 最高优先级）
- **必须在所有 Python 源码文件的第一行声明**：
  ```python
  # coding=gbk
  ```
- **原因**：MiniQMT 底层 C++ 接口以及 Windows 运行环境默认采用 GBK/GB2312 编码。若缺少声明或编码混杂，会导致中文注释、备注信息（如 `order_remark`）、回调消息在与 QMT 客户端传输时出现乱码甚至崩溃。
- **Agent 约束**：新建或编辑任何 `.py` 文件时，必须保持 `# coding=gbk` 首行，并确保包含中文注释的内容可被 GBK 正常编解码。

### 2.2 MiniQMT 客户端依赖与运行前置条件
1. **独立客户端**：MiniQMT 不支持纯无头（Headless）运行，必须在 Windows 环境（或通过远程桌面/Windows 虚拟机）预先启动 MiniQMT 客户端并完成交易账号登录。
2. **UserData 路径**：必须在 `config.ini` / `config-dev.ini` 中正确配置 `userdata_mini_path`，指向客户端安装目录下的 `userdata_mini` 文件夹（例如 `C:\mqt\userdata_mini`）。
3. **Session ID 唯一性**：每次实例化 `XtQuantTrader` 时，`session_id` 必须是全局唯一整数（通常使用 `int(time.time())`），避免同台机器上多个策略进程冲突。

### 2.3 交易与风控安全规则（⚠️ 实盘生命线）
- **买卖数量合规**：
  - A 股主板、创业板、科创板普通买入必须为 **100 股（1 手）的整数倍**；
  - 卖出若持仓不足 100 股（零股），必须一次性全部卖出。
- **价格类型与精度**：
  - 股票价格必须保留 **2 位小数**（使用 `round(price, 2)`）；
  - 下单必须显式指定价格类型常量（例如限价 `xtconstant.FIX_PRICE`，最新价 `xtconstant.LATEST_PRICE` 等）。
- **防重复下单（Idempotency & Throttling）**：
  - 必须维护本地订单防重状态（如 `is_buy` 标志、订单状态机或冷却时间戳），严禁在行情高频 Tick 推送中短时间内对同一标的重复无节制发送买入/卖出指令。
- **异步回调与非阻塞原则**：
  - 在 `on_quote` 行情回调与 `on_stock_order` / `on_stock_trade` 交易回调中，**严禁执行高耗时同步阻塞操作**（如网络请求或密集型数学运算），以避免堵塞 QMT 底层通信队列。
- **凭证安全**：
  - 严禁将资金账号、密码等敏感信息硬编码到代码或 Git 提交中。所有敏感参数必须通过配置文件或环境变量加载。

---

## 3. MiniQMT (xtquant) 标准化开发范式

### 3.1 交易连接与完整生命周期

```python
# coding=gbk
import time
from xtquant import xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from src.config.config import get_account_cfg, get_qmt_cfg

class MyTradingCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("警告: 与 MiniQMT 客户端连接断开!")

    def on_stock_order(self, order):
        print(f"委托回报 -> 订单ID: {order.order_id}, 股票: {order.stock_code}, 状态: {order.order_status}")

    def on_stock_trade(self, trade):
        print(f"成交回报 -> 订单ID: {trade.order_id}, 成交价: {trade.traded_price}, 成交量: {trade.traded_volume}")

    def on_order_error(self, order_error):
        print(f"下单失败 -> 订单ID: {order_error.order_id}, 错误: {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        print(f"撤单失败 -> 订单ID: {cancel_error.order_id}, 错误: {cancel_error.error_msg}")

    def on_account_status(self, status):
        print(f"账号状态变动 -> 账号: {status.account_id}, 状态码: {status.status}")

def start_trader():
    # 1. 获取配置与创建账户对象
    qmt_cfg = get_qmt_cfg()
    account_cfg = get_account_cfg()
    acc = StockAccount(account_cfg.stock_account, "STOCK")

    # 2. 实例化交易客户端 (唯一 Session ID)
    session_id = int(time.time())
    xt_trader = XtQuantTrader(qmt_cfg.userdata_mini_path, session_id)

    # 3. 注册回调对象
    callback = MyTradingCallback()
    xt_trader.register_callback(callback)

    # 4. 启动后台通信线程
    xt_trader.start()

    # 5. 建立客户端连接 (0 为成功)
    connect_result = xt_trader.connect()
    if connect_result != 0:
        raise ConnectionError(f"MiniQMT 连接失败，返回值: {connect_result}")

    # 6. 订阅交易账号推送 (0 为成功)
    subscribe_result = xt_trader.subscribe(acc)
    if subscribe_result != 0:
        raise RuntimeError(f"资金账号订阅失败，返回值: {subscribe_result}")

    print("MiniQMT 交易连接与订阅成功")
    return xt_trader, acc
```

### 3.2 委托下单与撤单标准模板

```python
# coding=gbk
from xtquant import xtconstant

def buy_stock_fix_price(xt_trader, acc, stock_code: str, price: float, volume: int, strategy_name: str = "DefaultStrategy"):
    """
    限价买入股票
    """
    # 校验价格与数量
    if volume <= 0 or volume % 100 != 0:
        raise ValueError(f"买入股数必须为 100 的正整数倍: {volume}")
    price = round(price, 2)

    order_id = xt_trader.order_stock(
        account=acc,
        stock_code=stock_code,
        order_type=xtconstant.STOCK_BUY,
        order_volume=volume,
        price_type=xtconstant.FIX_PRICE,
        price=price,
        strategy_name=strategy_name,
        order_remark=f"买入_{stock_code}_{volume}股"
    )
    return order_id

def cancel_order(xt_trader, acc, order_id: int):
    """
    根据订单编号撤单
    """
    cancel_result = xt_trader.cancel_order_stock(acc, order_id)
    return cancel_result  # 0 为成功，-1 为失败
```

### 3.3 行情数据获取与订阅 (`xtdata`)

```python
# coding=gbk
from xtquant import xtdata

def subscribe_market_quote(stock_code: str, callback_fn):
    """
    订阅实时 Tick / 分钟行情
    标的代码规范: 000001.SZ, 600000.SH, 830000.BJ
    """
    seq = xtdata.subscribe_quote(stock_code, period="tick", callback=callback_fn)
    return seq

def fetch_history_data(stock_code: str, period: str = "1d", start_time: str = "20240101", end_time: str = ""):
    """
    下载并读取历史行情
    """
    # 先下载到本地缓存
    xtdata.download_history_data(stock_code, period=period, start_time=start_time, end_time=end_time)
    # 读取市场数据
    data = xtdata.get_market_data_ex(
        field_list=["time", "open", "high", "low", "close", "volume", "amount"],
        stock_list=[stock_code],
        period=period,
        start_time=start_time,
        end_time=end_time
    )
    return data.get(stock_code)
```

---

## 4. 本地 JSON 数据持久化规范

### 4.1 持久化分层与存储设计
- 所有数据落盘统一存放于 `data/` 目录。
- 采用 `src/service/storage.py` 中的 `save_json`（基于原子替换 `os.replace`）与 `load_json` 实现安全无损读写。

### 4.2 核心数据文件说明

| 文件路径 | 对应数据模型 | 对应 QMT 对象 / 概念 | 关键字段说明 |
| :--- | :--- | :--- | :--- |
| `data/account.json` | 资金账户快照 | `XtAsset` (资金账户) | `account_id`, `account_type`, `cash`, `frozen_cash`, `market_value`, `total_asset`, `update_time` |
| `data/positions.json` | 持仓明细列表 | `XtPosition` (持仓) | `stock_code`, `volume`, `can_use_volume`, `open_price`, `market_value`, `yesterday_volume` |
| `data/orders.json` | 委托订单记录 | `XtOrder` (委托订单) | `order_id`, `order_sysid`, `stock_code`, `order_type`, `order_volume`, `price`, `order_status`, `create_time` |
| `data/trades.json` | 成交明细记录 | `XtTrade` (成交明细) | `traded_id`, `order_id`, `stock_code`, `traded_price`, `traded_volume`, `traded_amount`, `create_time` |
| `data/target_pool.json` | 盘后选股标的池 | 策略选股产物 | `date`, `count`, `targets`, `target_codes` |

### 4.3 同步更新幂等性准则
在 `service/` 中实现同步函数（`update_order`, `update_position`, `update_trade`, `update_account`）时，**必须满足幂等性**：
1. 优先根据业务唯一键（如 `order_id`、`traded_id`、`stock_code`）检索已有记录；
2. 若记录存在则更新变动字段，保留初次创建的 `create_time`，并更新 `update_time`；
3. 若记录不存在则新增记录追加到列表中。

---

## 5. 常见状态常量速查手册

### 5.1 订单状态 (`order.order_status`)
| 状态常量 (`xtconstant`) | 状态码 | 中文说明 | 处理建议 |
| :--- | :--- | :--- | :--- |
| `ORDER_UNREPORTED` | 48 | 未报 | 刚提交，等待处理 |
| `ORDER_WAIT_REPORTING` | 49 | 待报 | 正在上报柜台 |
| `ORDER_REPORTED` | 50 | 已报 | 已报送交易所，等待撮合 |
| `ORDER_REPORTED_CANCEL` | 51 | 已报待撤 | 正在撤单流程中 |
| `ORDER_PARTSUCC_CANCEL` | 52 | 部成待撤 | 部分成交且剩余正在撤单 |
| `ORDER_PART_CANCEL` | 53 | 部撤 | 部分成交，剩余已成功撤单 (终态) |
| `ORDER_CANCELED` | 54 | 已撤 | 全部成功撤单 (终态) |
| `ORDER_PART_SUCC` | 55 | 部成 | 部分成交，剩余仍挂单等待撮合 |
| `ORDER_SUCCEEDED` | 56 | 已成 | 全部撮合成交 (终态) |
| `ORDER_JUNK` | 57 | 废单 | 柜台校验失败拒绝 (终态) |
| `ORDER_UNKNOWN` | 255 | 未知 | 异常状态，需查询核对 |

### 5.2 账号状态 (`status.status`)
| 状态常量 (`xtconstant`) | 状态码 | 中文说明 |
| :--- | :--- | :--- |
| `ACCOUNT_STATUS_INVALID` | -1 | 无效 |
| `ACCOUNT_STATUS_OK` | 0 | 正常可用 |
| `ACCOUNT_STATUS_WAITING_LOGIN` | 1 | 连接中 |
| `ACCOUNT_STATUSING` | 2 | 登录中 |
| `ACCOUNT_STATUS_FAIL` | 3 | 失败 |
| `ACCOUNT_STATUS_INITING` | 4 | 初始化中 |
| `ACCOUNT_STATUS_CORRECTING` | 5 | 数据刷新校正中 |
| `ACCOUNT_STATUS_CLOSED` | 6 | 收盘后 |

### 5.3 交易方向与报价类型
- **买卖方向**：
  - `xtconstant.STOCK_BUY` (23): 股票买入
  - `xtconstant.STOCK_SELL` (24): 股票卖出
- **报价类型**：
  - `xtconstant.FIX_PRICE` (11): 限价单（指定价格）
  - `xtconstant.LATEST_PRICE` (5): 最新价单

---

## 6. AI Agent 协作与开发行为准则

当 AI Agent 在此代码库中执行任务时，必须遵守以下操作步骤与设计规范：

1. **新建与修改文件规范**：
   - 必须确保所有 Python 文件第一行包含 `# coding=gbk`。
   - 所有函数与方法必须补充标准 Type Hints 与中文 Docstring 说明。
   - 保持现有注释与逻辑的完整性，严禁破坏已有的字段映射与持久化逻辑。
2. **配置与连接管理规范**：
   - 禁止在业务代码中硬编码 IP、密码、账号或本地绝对路径。
   - 统一通过 `src.config.config` 读取 `AccountCfg`、`QMTCfg`。
3. **数据操作规范**：
   - 统一使用 `src.service` 下的 `update_account`、`update_position`、`update_order`、`update_trade` 与 `storage.py` 进行持久化，确保增改操作幂等。
4. **测试与日常运维规范**：
   - 使用 `service/test_market_data.py` 进行行情接口验证与调试。
   - 定期执行 `make clean` 清除 `__pycache__` 与编译临时缓存。
5. **Python 运行与虚拟环境规范**：
   - 虚拟环境激活路径：`source /Users/zhouyi/workplace/python/quant/qmt/.venv/bin/activate`
   - Python 解释器直接路径：`/Users/zhouyi/workplace/python/quant/qmt/.venv/bin/python`
   - 运行任何脚本、执行依赖管理或测试时，必须使用此虚拟环境。
