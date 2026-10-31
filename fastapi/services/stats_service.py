"""
平台统计业务层(用户端首页 + 管理端看板)

- 入驻陪玩师数: companion 表"启用"状态计数
- 累计成交订单/累计服务时长: companion_order 表已成交口径(非待支付且非取消)计数与时长求和
- 服务好评率: 4/5 星评价数占已评价订单比例, 无评价返回 None(前端展示 --)
- 管理端看板: 指标卡(总营收/订单/今日订单/用户/陪玩师/好评率) + 订单状态分布/游戏订单分布/热门服务 TOP5/评价星级分布
"""
from datetime import date  # 标准库: 今日订单统计日期

from sqlalchemy import case, func, select  # 第三方: SQLAlchemy 列表达式/聚合函数
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from models.entities import Companion, CompanionOrder, GameCategory, User  # 项目内: ORM 实体

# 已成交口径: 排除待支付与已取消(待开始/进行中/已完成/退款中均视为已成交)
_DEAL_STATUSES = ("booked", "ongoing", "completed", "refunding")

# 订单状态 -> 中文标签(看板状态饼图, 按订单生命周期排序)
_STATUS_LABELS = {
    "pending": "待支付",
    "booked": "待开始",
    "ongoing": "进行中",
    "completed": "已完成",
    "refunding": "退款中",
    "cancelled": "已取消",
}


def get_platform_stats(db: Session) -> dict:
    """聚合平台统计数据(陪玩师数/成交订单/服务时长/好评率, 返回 camelCase 字典)

    参数: db 请求级 Session(公开接口直调)
    """
    companion_count = db.scalar(
        select(func.count()).select_from(Companion).where(Companion.status == 0)
    ) or 0  # 启用陪玩师数

    order_count = db.scalar(
        select(func.count())
        .select_from(CompanionOrder)
        .where(CompanionOrder.status.in_(_DEAL_STATUSES))
    ) or 0  # 已成交订单数

    service_hours = db.scalar(
        select(func.coalesce(func.sum(CompanionOrder.hours), 0))
        .where(CompanionOrder.status.in_(_DEAL_STATUSES))
    ) or 0  # 累计服务时长(小时)

    total_reviews, good_reviews = db.execute(
        select(
            func.count(CompanionOrder.review_rating),  # 已评价订单数(星级非空)
            func.sum(case((CompanionOrder.review_rating >= 4, 1), else_=0)),  # 4/5 星好评数
        )
    ).one()  # 无 group_by 的整表聚合恒返回一行
    praise_rate = round(good_reviews / total_reviews * 100, 1) if total_reviews else None  # 无评价返回 None

    return {
        "companionCount": companion_count,
        "orderCount": order_count,
        "serviceHours": int(service_hours),  # Decimal -> int(小时为整数)
        "praiseRate": float(praise_rate) if praise_rate is not None else None,  # Decimal -> float
    }


def get_admin_dashboard(db: Session) -> dict:
    """管理端首页看板数据聚合(指标卡 + 状态/游戏分布 + 热门服务 TOP5 + 星级分布, 返回 camelCase 字典)

    参数: db 请求级 Session; 看板各分布只保留有数据的项(空项前端不渲染)
    """
    # —— 指标卡 ——
    total_revenue = db.scalar(
        select(func.coalesce(func.sum(CompanionOrder.amount), 0))
        .where(CompanionOrder.status.in_(_DEAL_STATUSES))
    ) or 0  # 总营收: 成交口径实付合计

    order_count = db.scalar(select(func.count()).select_from(CompanionOrder)) or 0  # 全部订单数
    today_order_count = db.scalar(
        select(func.count())
        .select_from(CompanionOrder)
        .where(func.date(CompanionOrder.create_time) == date.today())
    ) or 0  # 今日新增订单数(按下单日期)
    user_count = db.scalar(select(func.count()).select_from(User)) or 0  # 注册用户数
    companion_count = db.scalar(
        select(func.count()).select_from(Companion).where(Companion.status == 0)
    ) or 0  # 启用陪玩师数

    total_reviews, good_reviews = db.execute(
        select(
            func.count(CompanionOrder.review_rating),  # 已评价订单数(星级非空)
            func.sum(case((CompanionOrder.review_rating >= 4, 1), else_=0)),  # 4/5 星好评数
        )
    ).one()  # 无 group_by 的整表聚合恒返回一行
    praise_rate = round(good_reviews / total_reviews * 100, 1) if total_reviews else None  # 无评价返回 None

    # —— 订单状态分布(只保留有数据的状态, 按生命周期顺序展示) ——
    status_count_map = dict(
        db.execute(
            select(CompanionOrder.status, func.count()).group_by(CompanionOrder.status)
        ).all()
    )
    status_dist = [  # 按生命周期顺序输出且有数据的状态
        {"name": label, "value": status_count_map[code]}
        for code, label in _STATUS_LABELS.items()  # 字典保持定义顺序(生命周期序)
        if status_count_map.get(code)  # 无数据的状态不输出
    ]

    # —— 游戏订单分布(成交口径, 订单->陪玩师主游戏->游戏分类) ——
    game_dist = [  # 游戏名 + 订单数(倒序)
        {"name": game_name, "value": count}
        for game_name, count in db.execute(
            select(GameCategory.game_name, func.count())
            .select_from(CompanionOrder)
            .join(Companion, Companion.companion_id == CompanionOrder.companion_id)  # 订单 -> 陪玩师
            .join(GameCategory, GameCategory.game_id == Companion.main_game_id)  # 陪玩师 -> 主游戏分类
            .where(CompanionOrder.status.in_(_DEAL_STATUSES))  # 仅成交口径订单
            .group_by(GameCategory.game_name)  # 按游戏名分组
            .order_by(func.count().desc())  # 订单数降序
        ).all()
    ]

    # —— 热门服务 TOP5(成交口径, 按订单数降序) ——
    service_top = [  # 服务名 + 订单数(倒序)
        {"name": service_name, "value": count}
        for service_name, count in db.execute(
            select(CompanionOrder.service_name, func.count())  # 按下单时服务名快照统计
            .where(CompanionOrder.status.in_(_DEAL_STATUSES))  # 仅成交口径订单
            .group_by(CompanionOrder.service_name)  # 按服务名分组
            .order_by(func.count().desc())  # 订单数降序
            .limit(5)  # 只取前 5
        ).all()
    ]

    # —— 评价星级分布(1-5 星补齐缺失为 0) ——
    rating_map = dict(
        db.execute(
            select(CompanionOrder.review_rating, func.count())
            .where(CompanionOrder.review_rating.is_not(None))
            .group_by(CompanionOrder.review_rating)
        ).all()
    )
    rating_dist = [  # 1-5 星全部输出(无数据的星级补 0)
        {"name": f"{star}星", "value": rating_map.get(star, 0)} for star in range(1, 6)
    ]

    return {  # 看板整体字典(指标卡 + 四个分布)
        "totalRevenue": int(total_revenue),
        "orderCount": order_count,
        "todayOrderCount": today_order_count,
        "userCount": user_count,
        "companionCount": companion_count,
        "praiseRate": float(praise_rate) if praise_rate is not None else None,  # Decimal -> float
        "statusDist": status_dist,  # 订单状态分布(饼图)
        "gameDist": game_dist,  # 游戏订单分布(饼图)
        "serviceTop": service_top,  # 热门服务 TOP5(柱图)
        "ratingDist": rating_dist,  # 评价星级分布(柱图)
    }