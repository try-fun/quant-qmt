# coding=gbk
"""
JSON 持久化工具模块
提供安全的原子写入与容错读取功能
"""
import json
import os
from typing import Any


def load_json(file_path: str, default: Any = None) -> Any:
    """
    安全读取 JSON 文件内容

    Args:
        file_path (str): 目标文件路径
        default (Any): 文件不存在或解析失败时的默认返回值

    Returns:
        Any: 解析后的 Python 对象或默认值
    """
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"读取 JSON 文件 {file_path} 失败: {e}")
        return default


def save_json(file_path: str, data: Any) -> bool:
    """
    原子安全写入 JSON 文件，防止并发写入或异常中断损坏文件

    Args:
        file_path (str): 目标文件路径
        data (Any): 待写入的数据

    Returns:
        bool: 写入是否成功
    """
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        temp_path = f"{file_path}.tmp_{os.getpid()}"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        print(f"写入 JSON 文件 {file_path} 失败: {e}")
        return False
