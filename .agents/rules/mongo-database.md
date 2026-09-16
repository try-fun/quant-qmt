# MongoDB 数据持久化与 Model 规范

## 1. 模型与基类规范
- 所有数据模型必须定义在 `src/db/` 目录下，并继承 `src.db.base_model.BaseModel`。
- 数据库连接配置统一通过 `src.config.config.get_mongodb_cfg()` 获取，由 `src/db/mongo.py` 的 `init_mongodb()` 统一初始化。

## 2. 核心集合对应关系
| 集合名称 (`collection`) | 模型类 (`Model`) | 对应 QMT 数据结构 | 主键/唯一键 |
| :--- | :--- | :--- | :--- |
| `tb_account` | `AccountModel` | `XtAsset` (资金账户) | `account_id` |
| `tb_position` | `PositionModel` | `XtPosition` (持仓明细) | `stock_code` |
| `tb_order` | `OrderModel` | `XtOrder` (委托订单) | `order_id` |
| `tb_trade` | `TradeModel` | `XtTrade` (成交明细) | `traded_id` |
| `tb_stock` | `StockModel` | 证券基础信息元数据 | `code` |

## 3. 同步幂等性准则
所有持久化函数（`update_account`, `update_order`, `update_position`, `update_trade`）必须保证幂等：
1. 优先根据主键检索已存在记录；
2. 若存在则更新变动字段及 `update_time`；
3. 若不存在则创建新对象，赋 `create_time` 与 `update_time` 后入库。
