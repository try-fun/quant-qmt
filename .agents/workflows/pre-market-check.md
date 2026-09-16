# 盘前准备与环境自检 SOP (Pre-Market Check)

当准备运行量化交易策略或进行盘前自检时，按照以下步骤依次执行：

## 步骤 1：客户端与环境检查
1. 确认 Windows 虚拟机 / 实体机上的 MiniQMT (迅投) 客户端已启动并完成交易登录。
2. 确认 `src/config/config.ini` 中的 `userdata_mini_path` 路径正确指向客户端的 `userdata_mini` 文件夹。

## 步骤 2：数据库连通性自检
1. 检查 MongoDB 实例已启动并可正常连接。
2. 运行配置校验：
   ```bash
   python -c "from src.config.config import get_mongodb_cfg, get_account_cfg; print('MongoDB:', get_mongodb_cfg().host); print('Account:', get_account_cfg().stock_account)"
   ```

## 步骤 3：交易连接与账户状态核验
1. 初始化 `XtQuantTrader` 并建立连接（`connect() == 0`）。
2. 订阅交易账号推送（`subscribe(acc) == 0`）。
3. 调用 `query_stock_asset()` 同步初始资金到 `tb_account`。
4. 调用 `query_stock_positions()` 同步初始持仓到 `tb_position`。

## 步骤 4：清理临时缓存
在策略启动前执行：
```bash
make clean
```
