"""
钱包业务层
"""
from datetime import datetime  # 日期时间类型的标准库
from sqlalchemy import select, func, update, between
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if, insert_row, update_by_pk, between_if,
)
from models.entities import WalletTransaction, User

# 用户端可用的变动类型白名单
USER_CHANGE_TYPES = ("consume", "refund", "reward")

# 累计充值子查询
_TOTAL_RECHARGE = (
    select(func.coalesce(func.sum(WalletTransaction.amount), 0))
    .where(WalletTransaction.user_id == User.user_id, WalletTransaction.type == 'recharge')
    .scalar_subquery()
    .label("total_recharge")
)

# 累计支出子查询(负数流水取绝对值求和: 消费/打赏/人工扣减)
_TOTAL_EXPENSE = (
    select(func.coalesce(func.sum(func.abs(WalletTransaction.amount)), 0))
    .where(WalletTransaction.user_id == User.user_id, WalletTransaction.amount < 0)
    .scalar_subquery()
    .label("total_expense")
)

# 最近变动时间子查询
_LAST_TIME = (
    select(func.max(WalletTransaction.create_time))
    .where(WalletTransaction.user_id == User.user_id)
    .scalar_subquery()
    .label("last_time")
)

# 用户余额查询列
_WALLET_COLS = (
    User.user_id, User.user_name, User.avatar, User.balance,
    _TOTAL_RECHARGE, _TOTAL_EXPENSE, _LAST_TIME
)

# 流水查询列
_TX_COLS = (
    WalletTransaction.tx_id, User.user_name, User.avatar, WalletTransaction.type,
    WalletTransaction.amount, WalletTransaction.balance_after, WalletTransaction.note,
    WalletTransaction.operator, WalletTransaction.create_time
)


def select_wallet_page(db: Session, page_num: int, page_size: int,
                       user_name: str | None = None) -> tuple[int, list[dict]]:
    """
    分页查询用户余额列表
    """
    stmt = select(*_WALLET_COLS).select_from(User)  # 显式指定主表
    stmt = where_if(stmt, like_if(User.user_name, user_name))  # 拼接动态条件
    stmt = stmt.order_by(User.user_id)  # 根据用户ID正序排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def select_tx_page(db: Session, page_num: int, page_size: int,
                   user_name: str | None = None, tx_type: str | None = None,
                   user_id: int | None = None,
                   begin_time: datetime | None = None, end_time: datetime | None = None) -> tuple[int, list[dict]]:
    """
    分页查询钱包流水列表
    """
    stmt = select(*_TX_COLS).select_from(WalletTransaction)  # 显式指定主表
    stmt = stmt.join(User, WalletTransaction.user_id == User.user_id)  # 内连接用户表
    stmt = where_if(
        stmt,
        like_if(User.user_name, user_name),
        eq_if(WalletTransaction.type, tx_type),
        eq_if(WalletTransaction.user_id, user_id),
        between_if(WalletTransaction.create_time, begin_time, end_time),
    )
    stmt = stmt.order_by(WalletTransaction.tx_id.desc())  # 根据流水ID倒序排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_balance(db: Session, user_id: int) -> int | None:
    """
    查询用户余额
    """
    return db.scalar(select(User.balance).where(User.user_id == user_id))  # 单值查询


def do_change(db: Session, user_id: int, amount: int, tx_type: str,
              note: str | None = None, operator: str | None = None) -> tuple[str | None, int | None]:
    """
    钱包变动核心事件: 校验用户/金额/余额是否充足 -> 更新余额 -> 写流水
    """
    balance = db.scalar(select(User.balance).where(User.user_id == user_id))
    if balance is None:  # 查不到余额表示用户不存在
        return "用户不存在", None
    if not amount or amount == 0:
        return "变动金额不能为0", None
    if amount < 0 and balance + amount < 0:
        return "余额不足", None
    balance_after = balance + amount  # 变动后的余额
    db.execute(update(User).where(User.user_id == user_id).values(balance=balance_after))  # 更新该用户的余额
    db.add(WalletTransaction(
        user_id=user_id, type=tx_type, amount=amount,
        balance_after=balance_after, note=note, operator=operator,
        create_time=datetime.now()
    ))
    db.commit()  # 在同一事务内完成提交
    return None, balance_after


def recharge(db: Session, user_id: int, amount: int, pay_method: str | None = None) -> tuple[str | None, int | None]:
    """
    充值入账
    """
    method_name = {"alipay": "支付宝", "wechat": "微信支付"}.get(pay_method or "", "快捷充值")  # 如果是未知支付方式, 用快捷充值四个字兜底
    return do_change(db, user_id, amount, "recharge", note=f"余额充值({method_name})")


def change(db: Session, user_id: int, amount: int, tx_type: str, note: str | None = None) -> tuple[
    str | None, int | None]:
    """
    用户端通用变动(订单支付/打赏/退款联动)
    """
    if tx_type not in USER_CHANGE_TYPES:  # 如果变动类型不是白名单的其中之一
        return "不支持的变动类型", None
    return do_change(db, user_id, amount, tx_type, note)


def adjust_wallet(db: Session, user_id: int, amount: int,
                  note: str, operator: str | None = None) -> tuple[str | None, int | None]:
    """
    管理端人工调账
    """
    return do_change(db, user_id, amount, "adjust", note=note, operator=operator)
