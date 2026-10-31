"""
用户端 AI 助手工具（推荐 / 订单 / 问答 三组）

- 工厂函数以闭包绑定登录用户 ID: user_id 不进入工具签名, LLM 无法伪造, 杜绝越权查他人数据
- 每个工具内部开 SessionLocal 短会话(Agent 执行跨越请求生命周期, 不占用请求级 Session)
- 工具 docstring 即 LLM 看到的用途说明, 返回 JSON 字符串(超长截断保护上下文)
"""
import json  # 标准库: 结果序列化

from langchain_core.tools import tool  # 第三方: 工具装饰器(由签名生成调用 schema)

from core.database import SessionLocal  # 项目内: Session 工厂
from services import (  # 项目内: 业务层
    companion_service, coupon_service, faq_service, game_service, notice_service, order_service, wallet_service,
)

# 单个工具返回给 LLM 的最大字符数(防止超长结果撑爆模型上下文)
_MAX_RESULT_CHARS = 10000

# 订单状态 -> 中文标签(与 stats_service 口径一致, 供 LLM 解读)
_STATUS_ZH = {
    "pending": "待支付", "booked": "待开始", "ongoing": "进行中",
    "completed": "已完成", "refunding": "退款中", "cancelled": "已取消",
}


def _dumps(data) -> str:
    """结果序列化为 JSON 字符串, 超长截断

    参数: data 任意可序列化对象(dict/list); default=str 兼容 datetime 等非原生类型
    """
    text = json.dumps(data, ensure_ascii=False, default=str)  # 中文不转义, 日期自动转字符串
    if len(text) > _MAX_RESULT_CHARS:  # 超长截断保护 LLM 上下文
        return text[:_MAX_RESULT_CHARS] + "\n...(结果过长已截断)"
    return text


def _zh_status(status: str) -> str:
    """订单状态码转中文标签

    参数: status 订单状态码(如 booked); 未知状态码原样返回
    """
    return _STATUS_ZH.get(status, status)


# ==================== 陪玩推荐 Agent 工具(无需绑定用户) ====================

def build_recommendation_tools() -> list:
    """陪玩推荐 Agent 工具集: 筛选陪玩师 / 陪玩师详情 / 游戏分类列表"""

    @tool
    def search_companions(game_name: str | None = None, max_price: int | None = None,
                          min_rating: float | None = None, gender: int | None = None,
                          keyword: str | None = None) -> str:
        """按条件筛选陪玩师, 至少给出一个条件。参数: game_name 擅长游戏名(模糊匹配); max_price 每小时价格上限(元); min_rating 最低评分(1-5); gender 性别(0男 1女); keyword 昵称/标签/简介关键词。返回最匹配的前 8 位(昵称/性别/年龄/城市/段位/价格/评分/接单数/粉丝数/标签/擅长游戏)。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            companions = companion_service.select_user_companion_all(db)  # 用户端可见的启用陪玩师(含统计列)
        matched = []  # 命中全部筛选条件的陪玩师
        for c in companions:  # 全量已含统计列, 内存过滤(量级小)
            if gender is not None and c.get("gender") != gender:  # 性别不符
                continue
            if max_price is not None and (c.get("price") is None or c["price"] > max_price):  # 超价或未定价
                continue
            if min_rating is not None and (c.get("rating") or 0) < min_rating:  # 评分不足(无评分视为 0)
                continue
            if game_name:  # 游戏条件: 主游戏或任一擅长游戏命中即可
                names = [g.get("gameName") or "" for g in c.get("games", [])]  # 擅长游戏名列表
                if not any(game_name in n for n in names) and game_name not in (c.get("mainGameName") or ""):
                    continue
            if keyword:  # 关键词命中昵称/标签/简介任一即保留
                blob = f"{c.get('nickName') or ''} {c.get('tags') or ''} {c.get('intro') or ''}"  # 拼接可搜文本
                if keyword not in blob:
                    continue
            matched.append(c)  # 通过全部非空条件, 加入结果
        matched.sort(key=lambda c: (-float(c.get("rating") or 0), -int(c.get("orderCount") or 0)))  # 评分降序, 同分接单多者优先
        result = [  # 输出精简字段(前 8 位, 供 LLM 组织推荐话术)
            {
                "companionId": c.get("companionId"), "nickName": c.get("nickName"),
                "gender": "女" if c.get("gender") == 1 else "男", "age": c.get("age"),
                "city": c.get("city"), "mainGameName": c.get("mainGameName"),
                "mainRank": c.get("mainRank"), "price": c.get("price"),
                "rating": c.get("rating"), "orderCount": c.get("orderCount"),
                "fans": c.get("fans"), "tags": c.get("tags"),
                "games": [g.get("gameName") for g in c.get("games", [])][:4],
            }
            for c in matched[:8]  # 只取排序后前 8 位
        ]
        return _dumps({"total": len(matched), "companions": result})  # 命中总数 + 精选列表

    @tool
    def get_companion_detail(companion_id: int) -> str:
        """按陪玩师ID查询详情(基础信息/擅长游戏及段位/在售服务项目及价格/接单与评分统计)。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            companions = companion_service.select_user_companion_all(db)  # 复用用户端列表查询(含详情聚合字段)
        target = next((c for c in companions if c.get("companionId") == companion_id), None)  # 按 ID 定位目标
        if target is None:
            return _dumps({"error": "陪玩师不存在或已停用"})  # 不存在/已停用统一提示
        return _dumps({
            "companionId": target.get("companionId"), "nickName": target.get("nickName"),
            "gender": "女" if target.get("gender") == 1 else "男", "age": target.get("age"),
            "city": target.get("city"), "voice": target.get("voice"),
            "intro": target.get("intro"), "tags": target.get("tags"),
            "certified": "已认证" if target.get("certified") == 1 else "未认证",
            "rating": target.get("rating"), "orderCount": target.get("orderCount"),
            "fans": target.get("fans"),
            "games": target.get("games", []),
            "services": target.get("services", []),
        })

    @tool
    def list_games() -> str:
        """查询平台全部启用游戏分类(游戏名/标签/简介), 用于向用户介绍可选游戏或辅助筛选。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            games = game_service.select_game_list(db, status=0)  # 仅启用状态(0)的游戏
        return _dumps([  # 精简字段输出
            {"gameId": g.get("gameId"), "gameName": g.get("gameName"),
             "tags": g.get("tags"), "description": g.get("description")}
            for g in games
        ])

    return [search_companions, get_companion_detail, list_games]


# ==================== 订单助手 Agent 工具(闭包绑定 user_id) ====================

def build_order_tools(user_id: int) -> list:
    """订单助手 Agent 工具集: 全部数据以闭包内的 user_id 过滤, 仅返回本人数据"""

    @tool
    def query_my_orders(status: str | None = None, limit: int = 10) -> str:
        """查询当前用户自己的订单列表。status 可选值: pending 待支付 / booked 待开始 / ongoing 进行中 / completed 已完成 / refunding 退款中 / cancelled 已取消, 不传查全部; limit 最多返回条数(默认 10)。返回订单号/陪玩师/服务/金额/状态/预约时间。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            # 分页仅取第 1 页, 条数防护 1~20(闭包 user_id 限定本人数据)
            _, rows = order_service.select_my_orders(db, user_id, status, 1, max(1, min(int(limit), 20)))
        return _dumps([  # 行转精简字段(状态码转中文)
            {
                "orderNo": r.get("orderNo"), "companionName": r.get("nickName"),
                "serviceName": r.get("serviceName"), "hours": r.get("hours"),
                "amount": r.get("amount"), "status": _zh_status(r.get("status") or ""),
                "serviceDate": r.get("serviceDate"), "startHour": r.get("startHour"),
                "createTime": r.get("createTime"),
            }
            for r in rows
        ])

    @tool
    def get_order_detail(order_no: str) -> str:
        """按订单号查询当前用户自己的订单详情(仅本人订单可见, 含金额明细/支付方式/时间线/投诉处理进度)。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            order = order_service.get_my_order(db, user_id, order_no)  # 闭包 user_id 限定仅本人订单
        if order is None:
            return _dumps({"error": "订单不存在或不属于当前用户"})  # 不存在/非本人统一提示(不泄露他人订单存在性)
        keep = ("orderNo", "companionName", "serviceName", "price", "hours", "serviceDate", "startHour",  # 订单基础信息字段
                "couponName", "couponAmount", "grossAmount", "amount", "payMethod", "status", "note",  # 金额与支付字段
                "payTime", "startTime", "endTime", "cancelReason", "createTime",  # 时间线字段
                "complaintType", "complaintStatus", "handleResult", "complaintReply")  # 投诉处理进度字段
        return _dumps({k: order.get(k) for k in keep if order.get(k) is not None})  # 只保留非空字段输出

    @tool
    def query_my_coupons() -> str:
        """查询当前用户自己的优惠券列表(券名/面额/使用门槛/状态/过期时间, 自动区分可用/已使用/已过期)。"""
        from datetime import datetime as _dt  # 局部导入: 过期态判定
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            coupons = coupon_service.select_my_coupons(db, user_id)  # 闭包 user_id 限定本人券
        now = _dt.now()  # 当前时刻(与过期时间字符串同格式比较)
        result = []  # 带状态标签的券列表
        for c in coupons:
            if c.get("status") == 1:  # 状态 1 已使用
                state = "已使用"
            elif c.get("expireTime") and str(c.get("expireTime")) < now.strftime("%Y-%m-%d %H:%M:%S"):
                state = "已过期"  # 未使用但已超过过期时间
            else:
                state = "可用"  # 未使用且未过期(含无过期时间)
            result.append({  # 精简字段输出
                "couponName": c.get("couponName"), "amount": c.get("amount"),
                "threshold": c.get("threshold"), "state": state,
                "expireTime": c.get("expireTime"),
            })
        return _dumps(result)

    @tool
    def get_wallet_summary() -> str:
        """查询当前用户自己的钱包概览(余额/各状态订单计数)。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            balance = wallet_service.get_balance(db, user_id)  # 闭包 user_id 查本人余额(元)
            counters = order_service.count_my_orders(db, user_id)  # 各状态订单计数
        return _dumps({
            "balance": balance if balance is not None else 0,  # 无余额记录视为 0 元
            "orderCounts": {_zh_status(k): v for k, v in counters.items()},  # 状态码转中文标签
        })

    return [query_my_orders, get_order_detail, query_my_coupons, get_wallet_summary]


# ==================== 平台问答 Agent 工具(无需绑定用户) ====================

def build_faq_tools() -> list:
    """平台问答 Agent 工具集: FAQ 检索 + 最新公告"""

    @tool
    def search_faq(keyword: str | None = None) -> str:
        """检索平台帮助中心 FAQ(问题模糊匹配, 不传关键词返回全部)。覆盖下单流程/支付方式/服务保障/退款规则/投诉流程等, 回答平台规则类问题必须先调用本工具。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            _, rows = faq_service.select_faq_page(db, 1, 20, keyword=keyword, status=0)  # 仅显示中(0)的 FAQ, 取前 20 条
        return _dumps([  # 精简字段输出
            {"category": r.get("category"), "question": r.get("question"), "answer": r.get("answer")}
            for r in rows
        ])

    @tool
    def list_notices(limit: int = 5) -> str:
        """查询平台最新发布的公告(标题/类型/正文摘要, 默认 5 条)。涉及活动优惠/保障升级/新区上线等问题时调用。"""
        with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
            notices = notice_service.select_published_notices(db)  # 已发布公告(按时间倒序)
        return _dumps([  # 精简字段输出
            {"title": n.get("title"), "noticeType": n.get("noticeType"),
             "content": (n.get("content") or "")[:200], "createTime": n.get("createTime")}
            for n in notices[:max(1, min(int(limit), 10))]
        ])

    return [search_faq, list_notices]