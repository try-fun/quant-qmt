# GBK 文件编码规范（⚠️ 最高优先级）

## 1. 核心约束
- **必须在所有 Python 源码文件的第一行声明**：
  ```python
  # coding=gbk
  ```
- **所有 Python 源码文件必须以 GBK 编码格式保存**。

## 2. 约束原因
MiniQMT (xtquant) 底层为 Windows C++ 动态链接库，默认采用 GBK/GB2312 编码。
若 Python 文件声明了 `# coding=gbk` 却以 UTF-8 格式保存且包含中文，会导致 Python 解释器直接报语法错误（`SyntaxError: 'gbk' codec can't decode byte ...`）无法启动；若缺少声明，则与客户端通信时备注和中文消息会出现乱码。

## 3. Agent 行为准则
1. 新建或编辑任何 `.py` 文件时，必须保持 `# coding=gbk` 首行声明。
2. 写入或保存文件时，必须显式指定 `encoding='gbk'`。
3. 定期使用 `py_compile` 进行全库编码与语法编译检查。
