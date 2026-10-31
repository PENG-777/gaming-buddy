"""
通用工具函数

除日期工具外, 还沉淀了各业务模块通用的泛型工具:
- 键名转换: snake_to_camel / camel_to_snake
- 行转换: row_to_dict(数据库行 -> camelCase 字典)
- 请求体转换: body_fields(请求体 -> 数据库列字典, 仅非 null 字段)
- 查询条件工厂: eq_if / like_if / between_if(值非空才生成条件) + where_if(条件拼接)
- 分页与 CRUD: paginate / insert_row / update_by_pk / delete_by_pks
- 路由辅助: split_ids(删除接口的 "1,2,3" 路径参数解析)

新增业务模块时优先复用这些函数, service 内只写真正有业务差异的部分。
"""
import re  # 标准库: 正则表达式(camelCase 键名转换)
from datetime import datetime  # 标准库: 日期时间类型与字符串解析

from pydantic import BaseModel  # 第三方: 请求体模型基类(类型标注)
from sqlalchemy import delete, func, select, update  # 第三方: 通用 CRUD/计数列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

# 统一日期输出格式
DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def fmt_dt(value) -> str | None:
    """datetime -> 'yyyy-MM-dd HH:mm:ss' 字符串"""
    if value is None:  # 可空列的空值原样返回
        return None
    if isinstance(value, str):  # 已是字符串则无需转换
        return value
    return value.strftime(DT_FORMAT)  # datetime 按统一格式输出


def parse_dt(value: str | None) -> datetime | None:
    """'yyyy-MM-dd HH:mm:ss' 字符串 -> datetime, 解析失败返回 None"""
    if not value:  # 空字符串/None 直接放弃解析
        return None
    for pattern in (DT_FORMAT, "%Y-%m-%d"):  # 依次尝试: 完整时间格式 -> 纯日期格式
        try:
            return datetime.strptime(value, pattern)  # 匹配成功立即返回
        except ValueError:
            continue  # 当前格式不匹配, 尝试下一个
    return None  # 所有格式均失败, 返回 None


# ==================== 键名转换 ====================

def snake_to_camel(key: str) -> str:
    """snake_case -> camelCase(user_name -> userName)"""
    head, *rest = key.split("_")  # 按下划线拆分(首段保留原样)
    return head + "".join(w.capitalize() for w in rest)  # 首段 + 后续段首字母大写拼接


def camel_to_snake(key: str) -> str:
    """camelCase -> snake_case(userName -> user_name)"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()  # 大写字母前插下划线(首字母除外)后转小写


# ==================== 行 / 请求体转换 ====================

def row_to_dict(row, extra: dict | None = None) -> dict:
    """数据库行 -> camelCase 字典(datetime 值自动格式化为统一日期字符串)

    extra 用于补充映射不出来的占位字段或 join 计算列, 如 role 的 menuIds、menu 的 children。
    """
    d: dict = {}  # 结果字典
    for k, v in dict(row._mapping).items():  # 遍历行的 列名->值 映射
        d[snake_to_camel(k)] = fmt_dt(v) if isinstance(v, datetime) else v  # 键转 camelCase, datetime 统一格式
    if extra:  # 有附加字段则合并(不覆盖已转换的同名列)
        d.update(extra)
    return d

def entity_to_dict(obj, extra: dict | None = None) -> dict:
    """
    ORM实体 -> camelCase 字典(datetime 值自动格式化为统一日期字符串)
    """
    from sqlalchemy import inspect
    d: dict = {}  # 结果字典
    for attr in inspect(type(obj)).mapper.column_attrs:  # 遍历实体的列属性
        v = getattr(obj, attr.key) # 属性当前值
        d[snake_to_camel(attr.key)] = fmt_dt(v) if isinstance(v, datetime) else v  # 键转 camelCase, datetime 统一格式
    if extra: # 如果有附加字段就合并
        d.update(extra)
    return d


# 参与日期解析的请求体字段(camelCase): 字符串 -> datetime, 新增日期字段在此登记
_DATE_FIELDS = {"createTime", "updateTime"}


def body_fields(body: BaseModel, skip: tuple = ()) -> dict:
    """Pydantic 请求体 -> 数据库列字典(仅非 null 字段, 键转 snake_case)

    skip 填不需要写入数据库的字段名(主键、非列字段如 menuIds 等)。
    """
    fields: dict = {}  # 结果字典
    for key, value in body.model_dump(exclude_none=True).items():  # 只遍历非 null 字段
        if key in skip:  # 跳过主键等不写入数据库的字段
            continue
        if key in _DATE_FIELDS:  # 日期字段特判: 字符串 -> datetime
            dt = parse_dt(value)  # 解析失败返回 None
            if dt is not None:  # 解析成功才写入
                fields[camel_to_snake(key)] = dt
        else:
            fields[camel_to_snake(key)] = value  # 其余字段键转 snake_case 后原样写入
    return fields


# ==================== 查询条件工厂 ====================

def eq_if(col, value):
    """值非 None 时生成等值条件, 否则返回 None(配合列表推导过滤空条件)"""
    return col == value if value is not None and value != "" else None


def like_if(col, value: str | None):
    """值非空字符串时生成模糊条件, 否则返回 None(配合列表推导过滤空条件)"""
    return col.like(f"%{value}%") if value else None


def between_if(col, begin, end):
    """范围条件工厂: begin/end 至少一个非空才生成闭区间条件, 否则返回 None

    适用于日期范围筛选(如 createTime between '2026-01-01' and '2026-12-31'),
    只传 begin 时下界生效, 只传 end 时上界生效。
    """
    if begin is None and end is None:  # 两端都为空不生成条件
        return None
    return col.between(begin, end)  # SQLAlchemy 的 between 对 None 端自动开放


def where_if(stmt, *conds):
    """过滤掉 None 条件后拼接 where; 无有效条件时原样返回 stmt

    配合 eq_if/like_if/between_if 使用, 一行完成动态条件拼接:
        stmt = where_if(stmt, eq_if(User.user_id, user_id), like_if(User.user_name, user_name))
    """
    valid = [c for c in conds if c is not None]  # 只保留非空条件
    return stmt.where(*valid) if valid else stmt  # 有条件才拼 where


# ==================== 通用分页 / CRUD ====================

def paginate(db: Session, stmt, page_num: int, page_size: int) -> tuple[int, list]:
    """count + offset/limit 分页, 返回 (总条数, 当前页行列表)

    stmt 需已拼好 join/where/order_by; 计数时自动去掉排序。
    内部对页码/页大小做防护: 页码最小 1, 页大小范围 [1, 500], 避免 offset 为负报错或一次拉爆内存。
    """
    page_num = max(1, page_num)  # 页码下限防护(0/负数会导致 offset 为负触发 SQL 报错)
    page_size = min(max(1, page_size), 500)  # 页大小下限 1, 上限 500(防止 pageSize 传超大值拖库)
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0  # 去掉排序后子查询计数
    rows = db.execute(stmt.offset((page_num - 1) * page_size).limit(page_size)).all()  # 跳过前 (页码-1)*页大小 条
    return total, list(rows)


def insert_row(db: Session, model, fields: dict) -> int:
    """单条单表插入(直接提交), 返回受影响行数。多表事务请勿使用(会中途提交)。"""
    db.add(model(**fields))  # 构造实体加入会话
    db.commit()  # 单条单表写操作直接提交
    return 1


def update_by_pk(db: Session, model, pk_col, pk_value, fields: dict) -> int:
    """按主键动态更新非 null 字段(直接提交), 返回受影响行数"""
    fields = {k: v for k, v in fields.items() if v is not None}  # 过滤 null 值(动态更新)
    if not fields:  # 无可更新字段直接返回
        return 0
    result = db.execute(update(model).where(pk_col == pk_value).values(**fields))  # 按主键更新非空列
    db.commit()  # 提交事务
    return result.rowcount


def delete_by_pks(db: Session, model, pk_col, ids: list) -> int:
    """按主键批量删除(直接提交), 返回受影响行数"""
    result = db.execute(delete(model).where(pk_col.in_(ids)))  # 按ID批量删除
    db.commit()  # 提交事务
    return result.rowcount


# ==================== 路由辅助 ====================

def split_ids(raw: str) -> list[int]:
    """删除接口的路径参数解析: "1,2,3" -> [1, 2, 3]

    容忍空串与多余逗号; 含非数字片段时抛 ValueError(由全局异常处理器兜底)。
    """
    return [int(x) for x in raw.split(",") if x.strip()]  # 逐段去空白后转整数
