"""
用户打赏业务层
"""
from datetime import datetime  # 标准库: 日期时间类型

from sqlalchemy import select, update  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    between_if, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Companion, Gift, Reward, User, WalletTransaction  # 项目内: 打赏相关 ORM 实体

# 管理端查询列(join user 取打赏用户名, join companion 取陪玩师昵称/头像, 转换键一一对应)
_REWARD_COLS = (
    Reward.reward_id, User.user_name,
    Reward.companion_id, Companion.nick_name, Companion.avatar,
    Reward.gift_name, Reward.gift_image, Reward.amount, Reward.create_time,
)


def select_reward_page(db: Session, page_num: int, page_size: int,
                       user_name: str | None = None, nick_name: str | None = None,
                       gift_name: str | None = None,
                       begin_time: datetime | None = None, end_time: datetime | None = None,
                       companion_id: int | None = None
                       ) -> tuple[int, list[dict]]:
    """
    分页查询打赏记录
    """
    stmt = select(*_REWARD_COLS).select_from(Reward)
    stmt = stmt.join(User, Reward.user_id == User.user_id)  # 内连接用户表
    stmt = stmt.join(Companion, Reward.companion_id == Companion.companion_id)  # 内连接陪玩师表
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(User.user_name, user_name),
        like_if(Companion.nick_name, nick_name),
        like_if(Reward.gift_name, gift_name),
        between_if(Reward.create_time, begin_time, end_time),
        eq_if(Reward.companion_id, companion_id),  # 陪玩师数据范围(仅看自己)
    )
    stmt = stmt.order_by(Reward.reward_id.desc())  # 根据打赏ID倒序排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def delete_reward_by_ids(db: Session, reward_ids: list[int]) -> int:
    """
    批量删除打赏记录
    """
    return delete_by_pks(db, Reward, Reward.reward_id, reward_ids)


def send_reward(db: Session, user_id: int, companion_id: int, gift_id: int) -> tuple[str | None, int | None]:
    """
    用户打赏
    """
    gift = db.scalar(
        select(Gift).where(Gift.gift_id == gift_id, Gift.status == 0)
    )
    if gift is None:
        return "礼物不存在或已下架", None
    companion = db.execute(
        select(Companion.companion_id, Companion.nick_name)
        .where(Companion.companion_id == companion_id, Companion.status == 0)
    ).first()
    if companion is None:
        return "陪玩师不存在或已被停用", None
    balance = db.scalar(select(User.balance).where(User.user_id == user_id))  # 用户打赏前的余额
    if balance < gift.price:
        return "余额不足", None
    balance_after = balance - gift.price  # 变动后的余额
    db.execute(update(User).where(User.user_id == user_id).values(balance=balance_after))  # 将该用户的余额修改为变动后的余额
    db.add(WalletTransaction(
        user_id=user_id, type="reward", amount=-gift.price,
        balance_after=balance_after, note=f"打赏{companion.nick_name} · 送出{gift.gift_name}",
        create_time=datetime.now(),
    ))
    db.add(Reward(  # 写入打赏记录(礼物名称/图片/金额存快照)
        user_id=user_id, companion_id=companion_id,
        gift_name=gift.gift_name, gift_image=gift.image,
        amount=gift.price, create_time=datetime.now(),
    ))
    db.commit()
    return None, balance_after
