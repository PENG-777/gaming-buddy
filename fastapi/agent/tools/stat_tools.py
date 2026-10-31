"""
管理端经营分析 Agent 预置统计工具（指标查询 Agent 专用）

覆盖高频经营指标: 看板总览/订单趋势/陪玩师排行/投诉统计/用户增长,
查询为 select 列表达式 + 聚合(风格对齐 stats_service), 口径与其保持一致:
- 成交口径: 订单 status 属于 booked/ongoing/completed/refunding(排除待支付与已取消)
- 营收口径: 成交订单 amount 实付合计
"""
import json  # 标准库: 结果序列化
from datetime import date, timedelta  # 标准库: 日期运算(趋势区间)

from langchain_core.tools import tool  # 第三方: 工具装饰器
from sqlalchemy import case, func, select  # 第三方: 列表达式/聚合函数

from core.database import SessionLocal  # 项目内: Session 工厂
from models.entities import Companion, CompanionOrder, Complaint, User  # 项目内: ORM 实体
from services import stats_service  # 项目内: 统计业务层(看板复用)

# 成交口径状态(与 stats_service._DEAL_STATUSES 一致)
_DEAL_STATUSES = ("booked", "ongoing", "completed", "refunding")


def _dumps(data) -> str:
    """结果序列化为 JSON 字符串

    参数: data 任意可序列化对象(dict/list); default=str 兼容 datetime 等非原生类型
    """
    return json.dumps(data, ensure_ascii=False, default=str)  # 中文不转义, 日期自动转字符串


def build_stat_tools() -> list:
    """指标查询 Agent 工具集(管理端专用, 无需绑定用户)"""

    @tool
    def get_dashboard_overview() -> str:
        """获取经营看板总览: 总营收/订单总数/今日订单/注册用户/启用陪玩师/好评率 + 订单状态分布/游戏订单分布/热门服务TOP5/评价星级分布。适合回答"整体经营情况如何"类问题。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            data = stats_service.get_admin_dashboard(db)  # 复用看板统计口径
        data["statusDist"] = data.get("statusDist") or []  # 空分布兑底为空列表
        return _dumps(data)  # 整体序列化返回

    @tool
    def get_order_trend(days: int = 7) -> str:
        """按天统计近 N 天订单趋势(天数范围 1-90, 默认 7)。返回每天的订单数/成交订单数/成交金额(元), 含合计。适合分析订单量与营收变化趋势。"""
        days = max(1, min(int(days), 90))  # 天数防护: 下限 1, 上限 90
        begin = date.today() - timedelta(days=days - 1)  # 起始日期(含当天共 days 天)
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            rows = db.execute(
                select(
                    func.date(CompanionOrder.create_time).label("d"),  # 下单日期(截断到天)
                    func.count().label("total_orders"),  # 当日全部订单数
                    func.sum(case((CompanionOrder.status.in_(_DEAL_STATUSES), 1), else_=0)).label("deal_orders"),  # 当日成交订单数
                    func.sum(case((CompanionOrder.status.in_(_DEAL_STATUSES), CompanionOrder.amount), else_=0)).label("revenue"),  # 当日成交金额(实付合计)
                )
                .where(func.date(CompanionOrder.create_time) >= begin)  # 仅统计窗口内
                .group_by("d").order_by("d")  # 按天分组并升序(时间轴顺序)
            ).all()
        trend = [  # 行转字典(camelCase 键, 供 LLM 直接解读)
            {"date": str(r.d), "totalOrders": int(r.total_orders),
             "dealOrders": int(r.deal_orders or 0), "revenue": int(r.revenue or 0)}
            for r in rows
        ]
        return _dumps({
            "days": days,  # 实际统计天数(防护后)
            "trend": trend,  # 逐日明细
            "summary": {  # 窗口合计
                "totalOrders": sum(t["totalOrders"] for t in trend),
                "dealOrders": sum(t["dealOrders"] for t in trend),
                "revenue": sum(t["revenue"] for t in trend),
            },
        })

    @tool
    def get_companion_ranking(top_n: int = 10) -> str:
        """陪玩师业绩排行(TOP N, 默认 10, 最大 50): 按成交订单数降序, 含成交金额/平均评分/粉丝数。适合"哪些陪玩师最受欢迎/营收最高"类问题。"""
        top_n = max(1, min(int(top_n), 50))  # 名次防护: 下限 1, 上限 50
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            rows = db.execute(
                select(
                    Companion.companion_id, Companion.nick_name, Companion.gender,  # 陪玩师基础信息列
                    Companion.main_rank, Companion.status,
                    func.count().label("order_count"),  # 成交订单数(排序依据)
                    func.sum(CompanionOrder.amount).label("revenue"),  # 成交金额合计
                    func.avg(CompanionOrder.review_rating).label("avg_rating"),  # 平均评价星级(未评价订单不计入)
                )
                .select_from(CompanionOrder)  # 以订单表为主表(无成交订单的陪玩师不进榜)
                .join(Companion, CompanionOrder.companion_id == Companion.companion_id)  # 关联陪玩师基础信息
                .where(CompanionOrder.status.in_(_DEAL_STATUSES))  # 仅统计成交口径订单
                .group_by(Companion.companion_id, Companion.nick_name, Companion.gender,
                          Companion.main_rank, Companion.status)  # 按陪玩师分组(非聚合列需全部列出)
                .order_by(func.count().desc())  # 按成交订单数降序
                .limit(top_n)  # 只取前 N 名
            ).all()
        ranking = [  # 行转带名次的字典列表
            {
                "rank": i + 1, "companionId": r.companion_id, "nickName": r.nick_name,
                "gender": "女" if r.gender == 1 else "男", "mainRank": r.main_rank,
                "enabled": r.status == 0, "dealOrders": int(r.order_count),  # status 0 启用 1 停用
                "revenue": int(r.revenue or 0),
                "avgRating": round(float(r.avg_rating), 1) if r.avg_rating is not None else None,  # 无评价时为 None
            }
            for i, r in enumerate(rows)
        ]
        return _dumps(ranking)

    @tool
    def get_complaint_stats() -> str:
        """投诉统计: 总数/待处理数/已处理数 + 按投诉类型分布 + 按处理结果分布。适合"投诉处理情况/客诉压力"类问题。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            total = db.scalar(select(func.count()).select_from(Complaint)) or 0  # 投诉总数
            pending = db.scalar(  # 待处理数(status 0 待处理 1 已处理)
                select(func.count()).select_from(Complaint).where(Complaint.status == 0)
            ) or 0
            by_type = [  # 按投诉类型分组计数
                {"type": t, "count": c}
                for t, c in db.execute(
                    select(Complaint.complaint_type, func.count()).group_by(Complaint.complaint_type)
                ).all()
            ]
            by_result = [  # 按处理结果分组计数(仅统计已出结果的投诉)
                {"result": r, "count": c}
                for r, c in db.execute(
                    select(Complaint.handle_result, func.count())
                    .where(Complaint.handle_result.is_not(None))
                    .group_by(Complaint.handle_result)
                ).all()
            ]
        return _dumps({
            "total": int(total), "pending": int(pending), "handled": int(total) - int(pending),  # 已处理 = 总数 - 待处理
            "byType": by_type, "byResult": by_result,
        })

    @tool
    def get_user_growth(days: int = 7) -> str:
        """按天统计近 N 天新注册用户数(天数范围 1-90, 默认 7), 含合计。适合分析用户增长趋势。"""
        days = max(1, min(int(days), 90))  # 天数防护: 下限 1, 上限 90
        begin = date.today() - timedelta(days=days - 1)  # 起始日期(含当天共 days 天)
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            rows = db.execute(
                select(func.date(User.create_time).label("d"), func.count().label("cnt"))  # 注册日期(截到天) + 当日新增数
                .where(func.date(User.create_time) >= begin)  # 仅统计窗口内
                .group_by("d").order_by("d")  # 按天分组并升序(时间轴顺序)
            ).all()
        growth = [{"date": str(r.d), "newUsers": int(r.cnt)} for r in rows]  # 逐日明细
        return _dumps({"days": days, "growth": growth,  # 实际天数 + 逐日新增
                       "summary": {"newUsers": sum(g["newUsers"] for g in growth)}})  # 窗口合计

    return [get_dashboard_overview, get_order_trend, get_companion_ranking, get_complaint_stats, get_user_growth]