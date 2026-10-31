"""
统一响应构建

- 普通响应: {code, msg, ...}  code=200 成功 / code=500 失败, HTTP 状态码恒为 200
- 分页响应: {total, rows, code, msg}
- 需要附加字段时用关键字参数附加
"""
from typing import Any  # 标准库: 任意类型标注


def ajax_success(msg: str = "操作成功", **extra: Any) -> dict:
    r = {"code": 200, "msg": msg}  # 成功响应基础结构
    r.update(extra)  # 合并关键字附加字段(如 token)
    return r


def ajax_success_data(data: Any, msg: str = "操作成功", **extra: Any) -> dict:
    r = {"code": 200, "msg": msg}  # 成功响应基础结构
    if data is not None:  # 数据非空才携带 data 字段
        r["data"] = data
    r.update(extra)  # 合并关键字附加字段
    return r


def ajax_error(msg: str = "操作失败", **extra: Any) -> dict:
    r = {"code": 500, "msg": msg}  # 业务失败: HTTP 仍为 200, 前端按 code 提示
    r.update(extra)  # 合并关键字附加字段
    return r


def to_ajax(rows: int, msg: str = "操作成功") -> dict:
    """根据数据库受影响行数判断操作是否成功"""
    return ajax_success(msg) if rows > 0 else ajax_error()  # 受影响行数>0 视为成功, 否则失败


def page_data(rows: list, total: int, msg: str = "查询列表成功") -> dict:
    """分页列表响应"""
    return {"total": total, "rows": rows, "code": 200, "msg": msg}  # 前端表格约定结构: 总数+当前页数据
