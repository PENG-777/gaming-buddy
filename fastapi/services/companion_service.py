"""
陪玩师业务层

companion 与 companion_game / companion_service 两张关联表在同一事务中维护(参照 role_service 模式):
games/services 为 None 不动作关联, 传空数组才清空; 主游戏冗余字段(main_game_id/main_rank)
由 games[0] 自动同步, 便于列表筛选与展示。

companion 通过 user_id 硬关联 user 表: 新增陪玩师时同事务创建关联用户(用户名=昵称,
初始密码 DEFAULT_USER_PASSWORD, 同步性别/头像); 修改昵称/性别/头像同步到关联用户;
删除陪玩师连带删除关联用户(数据库外键 ON DELETE CASCADE 自动清理各自关联记录)。
"""
# 第三方: SQLAlchemy 列表达式(关联表重建在事务内直接使用 delete)
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, eq_if, like_if, paginate, row_to_dict, where_if,
)
from models.entities import (  # 项目内: ORM 实体
    Companion, CompanionGame, CompanionOrder, CompanionService, Follow, GameCategory, ServiceItem, User,
)
from schemas.body import CompanionBody, CompanionGameItem, CompanionServiceItem  # 项目内: 陪玩师请求体
from services.role_service import COMPANION_ROLE_ID  # 项目内: 陪玩师角色ID

# 陪玩师关联用户的初始密码(新增陪玩师时同步创建登录账号)
DEFAULT_USER_PASSWORD = "123456"

# 陪玩师查询列(outer join game_category 取主游戏名, label 与 row_to_dict 转换键一一对应)
_COMPANION_COLS = (
    Companion.companion_id, Companion.user_id, Companion.nick_name, Companion.gender, Companion.age, Companion.city,
    Companion.avatar, Companion.voice, Companion.price, Companion.intro, Companion.tags,
    Companion.certified, Companion.status, Companion.main_game_id, Companion.main_rank,
    Companion.create_time, GameCategory.game_name.label("main_game_name"),
)


def _distinct_games(games: list[CompanionGameItem] | None) -> list[CompanionGameItem]:
    """过滤无 gameId 的项并按 gameId 去重(联合主键防冲突, 保留先出现的)

    参数: games 请求体携带的擅长游戏列表(可空)
    """
    seen: set[int] = set()  # 已出现的游戏ID
    result: list[CompanionGameItem] = []  # 去重结果
    for g in games or []:
        if g.gameId is None or g.gameId in seen:  # 无ID或重复直接跳过
            continue
        seen.add(g.gameId)
        result.append(g)
    return result


def _distinct_services(services: list[CompanionServiceItem] | None) -> list[CompanionServiceItem]:
    """过滤无 serviceId 的项并按 serviceId 去重(联合主键防冲突, 保留先出现的)

    参数: services 请求体携带的服务项目列表(可空)
    """
    seen: set[int] = set()  # 已出现的服务项目ID
    result: list[CompanionServiceItem] = []  # 去重结果
    for s in services or []:
        if s.serviceId is None or s.serviceId in seen:  # 无ID或重复直接跳过
            continue
        seen.add(s.serviceId)
        result.append(s)
    return result


def _base_query(companion_id: int | None, nick_name: str | None, gender: int | None,
                main_game_id: int | None, certified: int | None, status: int | None):
    """构造陪玩师基础查询(outer join 主游戏名 + 动态条件, 供列表/分页/详情复用)"""
    stmt = select(*_COMPANION_COLS).outerjoin(GameCategory, Companion.main_game_id == GameCategory.game_id)  # 左连接主游戏
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        eq_if(Companion.companion_id, companion_id),
        like_if(Companion.nick_name, nick_name),
        eq_if(Companion.gender, gender),
        eq_if(Companion.main_game_id, main_game_id),
        eq_if(Companion.certified, certified),
        eq_if(Companion.status, status),
    )
    return stmt.order_by(Companion.companion_id)  # 按陪玩师ID排序


def select_companion_page(db: Session, page_num: int, page_size: int,
                          nick_name: str | None = None, gender: int | None = None,
                          main_game_id: int | None = None, certified: int | None = None,
                          status: int | None = None) -> tuple[int, list[dict]]:
    """分页查询陪玩师列表(含主游戏名)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / nick_name 昵称模糊(可选) /
          gender 性别(可选) / main_game_id 主游戏(可选) / certified 认证状态(可选) / status 状态(可选)
    """
    stmt = _base_query(None, nick_name, gender, main_game_id, certified, status)  # 复用基础查询
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def select_user_companion_all(db: Session) -> list[dict]:
    """查询全部启用陪玩师(含擅长游戏/服务项目/订单与关注统计, 供用户端一次拉全量本地筛选)

    统计列后端聚合: 累计接单(非取消订单数)/平均评分(已评价订单, 无评价默认 5.0)/评价数/粉丝数
    """
    rows = db.execute(_base_query(None, None, None, None, None, 0)).all()  # 仅启用陪玩师
    companions = [row_to_dict(r) for r in rows]  # 主表字段 -> camelCase 字典
    if not companions:
        return []
    ids = [c["companionId"] for c in companions]  # 全部陪玩师ID
    order_stats = {  # 陪玩师ID -> 订单统计行(一次 group by 全量聚合, 累计接单 + 已评价均分/条数)
        r.companion_id: r for r in db.execute(
            select(
                CompanionOrder.companion_id,
                func.count().label("order_count"),
                func.avg(CompanionOrder.review_rating).label("avg_rating"),
                func.count(CompanionOrder.review_rating).label("review_count"),
            )
            .where(CompanionOrder.companion_id.in_(ids), CompanionOrder.status != "cancelled")
            .group_by(CompanionOrder.companion_id)
        ).all()
    }
    fans_map = dict(db.execute(  # 陪玩师ID -> 粉丝数(关注表一次 group by 全量聚合)
        select(Follow.companion_id, func.count()).where(Follow.companion_id.in_(ids)).group_by(Follow.companion_id)
    ).all())
    for c in companions:  # 填充统计列(未接单补 0, 无评价默认 5.0 分)
        st = order_stats.get(c["companionId"])
        c["orderCount"] = st.order_count if st else 0
        c["rating"] = round(float(st.avg_rating), 1) if st and st.avg_rating is not None else 5.0
        c["reviewCount"] = st.review_count if st else 0
        c["fans"] = fans_map.get(c["companionId"], 0)
    games_map: dict[int, list[dict]] = {}  # 陪玩师ID -> 擅长游戏列表
    stmt = (
        select(CompanionGame.companion_id, CompanionGame.game_id, GameCategory.game_name, CompanionGame.game_rank)
        .join(GameCategory, CompanionGame.game_id == GameCategory.game_id)  # 内连接游戏分类
        .where(CompanionGame.companion_id.in_(ids), GameCategory.status == 0)  # 仅启用的游戏
        .order_by(CompanionGame.companion_id, CompanionGame.game_id)
    )
    for r in db.execute(stmt).all():  # 一次查出全部关联游戏再按陪玩师分组(避免 N+1)
        games_map.setdefault(r.companion_id, []).append(
            {"gameId": r.game_id, "gameName": r.game_name, "gameRank": r.game_rank})
    services_map: dict[int, list[dict]] = {}  # 陪玩师ID -> 服务项目列表
    stmt = (
        select(CompanionService.companion_id, CompanionService.service_id, ServiceItem.service_name,
               CompanionService.price, CompanionService.description)
        .join(ServiceItem, CompanionService.service_id == ServiceItem.service_id)  # 内连接服务项目
        .where(CompanionService.companion_id.in_(ids), ServiceItem.status == 0)  # 仅启用的服务
        .order_by(CompanionService.companion_id, CompanionService.service_id)
    )
    for r in db.execute(stmt).all():  # 一次查出全部关联服务再按陪玩师分组
        services_map.setdefault(r.companion_id, []).append(
            {"serviceId": r.service_id, "serviceName": r.service_name, "price": r.price, "description": r.description})
    for c in companions:  # 填充关联列表(无关联时为空数组)
        c["games"] = games_map.get(c["companionId"], [])
        c["services"] = services_map.get(c["companionId"], [])
    return companions


def select_companion_games(db: Session, companion_id: int) -> list[dict]:
    """查询陪玩师擅长游戏列表(join game_category 取游戏名)

    参数: db 请求级 Session / companion_id 陪玩师ID
    """
    stmt = (
        select(CompanionGame.game_id, GameCategory.game_name, CompanionGame.game_rank)
        .join(GameCategory, CompanionGame.game_id == GameCategory.game_id)  # 内连接游戏分类
        .where(CompanionGame.companion_id == companion_id)
        .order_by(CompanionGame.game_id)  # 按游戏ID稳定排序
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # [{gameId, gameName, gameRank}]


def select_companion_services(db: Session, companion_id: int) -> list[dict]:
    """查询陪玩师服务项目列表(join service_item 取服务名)

    参数: db 请求级 Session / companion_id 陪玩师ID
    """
    stmt = (
        select(CompanionService.service_id, ServiceItem.service_name, CompanionService.price, CompanionService.description)
        .join(ServiceItem, CompanionService.service_id == ServiceItem.service_id)  # 内连接服务项目
        .where(CompanionService.companion_id == companion_id)
        .order_by(CompanionService.service_id)  # 按服务项目ID稳定排序
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # [{serviceId, serviceName, price, description}]


def get_companion_by_id(db: Session, companion_id: int) -> dict | None:
    """按陪玩师ID查询详情(含擅长游戏与服务项目)

    参数: db 请求级 Session / companion_id 陪玩师ID; 无记录返回 None
    """
    row = db.execute(_base_query(companion_id, None, None, None, None, None)).first()  # 按主键查第一条
    if not row:
        return None  # 无记录返回 None
    data = row_to_dict(row)  # 主表字段 -> camelCase 字典
    data["games"] = select_companion_games(db, companion_id)  # 填充擅长游戏
    data["services"] = select_companion_services(db, companion_id)  # 填充服务项目
    return data


def name_exists(db: Session, nick_name: str | None, exclude_id: int | None = None) -> bool:
    """陪玩师昵称是否已存在(exclude_id 用于更新时排除自身)

    参数: db 请求级 Session / nick_name 待查重昵称 / exclude_id 排除的陪玩师ID(可选)
    """
    if not nick_name:  # 空昵称不参与查重(必填校验由路由层负责)
        return False
    stmt = select(Companion.companion_id).where(Companion.nick_name == nick_name)  # 按昵称查ID
    if exclude_id is not None:  # 更新场景排除自身
        stmt = stmt.where(Companion.companion_id != exclude_id)
    return db.scalar(stmt) is not None  # 查到即存在


def get_companion_user_id(db: Session, companion_id: int) -> int | None:
    """查询陪玩师关联的用户ID(陪玩师不存在或存量数据未回填时返回 None)

    参数: db 会话 / companion_id 陪玩师ID
    """
    return db.scalar(select(Companion.user_id).where(Companion.companion_id == companion_id))  # 单列查询


def insert_companion(db: Session, body: CompanionBody) -> int:
    """新增陪玩师 + 关联用户 + 游戏关联 + 服务关联(事务保证原子性)

    参数: db 请求级 Session / body 陪玩师请求体(games/services 为关联列表); 返回受影响行数
    """
    games = _distinct_games(body.games)  # 游戏列表去重
    services = _distinct_services(body.services)  # 服务列表去重
    fields = body_fields(body, skip=("companionId", "games", "services"))  # 请求体 -> 数据库列
    if games:  # 主游戏冗余字段从 games[0] 同步
        fields["main_game_id"] = games[0].gameId
        fields["main_rank"] = games[0].gameRank
    user = User(user_name=body.nickName, password=DEFAULT_USER_PASSWORD,  # 同步创建关联用户(用户名=昵称)
                sex=body.gender, avatar=body.avatar,  # 性别/头像从陪玩师同步
                role_id=COMPANION_ROLE_ID)  # 归属陪玩师角色
    db.add(user)  # 加入会话(未提交)
    db.flush()  # 回填自增主键
    fields["user_id"] = user.user_id  # 陪玩师关联新建用户
    companion = Companion(**fields)  # 构造陪玩师实体
    db.add(companion)  # 加入会话(未提交)
    db.flush()  # 回填自增主键
    if games:  # 批量插入擅长游戏关联
        db.add_all([CompanionGame(companion_id=companion.companion_id, game_id=g.gameId, game_rank=g.gameRank) for g in games])
    if services:  # 批量插入服务项目关联
        db.add_all([CompanionService(companion_id=companion.companion_id, service_id=s.serviceId,
                                     price=s.price if s.price is not None else 0, description=s.description) for s in services])
    db.commit()  # 主表 + 两张关联表同一事务一次性提交(保证原子性)
    return 1


def update_companion(db: Session, body: CompanionBody) -> int:
    """修改陪玩师 + 先删后插两张关联表(事务保证原子性)

    参数: db 请求级 Session / body 陪玩师请求体(companionId 必填; games/services None 不动作/[] 清空/有值重建);
    返回受影响行数(重建关联时取关联数)。
    games/services 为 None 时不动作对应关联(保持原数据), 传空数组才清空;
    传了 games 时主游戏冗余字段(main_game_id/main_rank)以 games[0] 为准同步。
    """
    if body.companionId is None:  # 缺少主键无法定位记录
        return 0
    games = _distinct_games(body.games)  # 游戏列表去重
    services = _distinct_services(body.services)  # 服务列表去重
    fields = body_fields(body, skip=("companionId", "games", "services"))  # 提取非 null 字段
    if games:  # 传了游戏列表才同步主游戏冗余字段
        fields["main_game_id"] = games[0].gameId
        fields["main_rank"] = games[0].gameRank
    if not fields and body.games is None and body.services is None:  # 无可更新字段也未传关联, 无事可做
        return 0
    if fields:  # 有可更新字段才执行更新
        db.execute(update(Companion).where(Companion.companion_id == body.companionId).values(**fields))  # 更新陪玩师本身
    rows = 1  # 默认影响行数: 陪玩师本身 1 行
    if body.games is not None:  # 传了 games 才重建游戏关联(None 不动作, [] 清空)
        db.execute(delete(CompanionGame).where(CompanionGame.companion_id == body.companionId))  # 先删除旧的关联
        if games:
            db.add_all([CompanionGame(companion_id=body.companionId, game_id=g.gameId, game_rank=g.gameRank) for g in games])  # 再插入新关联
            rows = len(games)  # 影响行数取关联记录数
    if body.services is not None:  # 传了 services 才重建服务关联(None 不动作, [] 清空)
        db.execute(delete(CompanionService).where(CompanionService.companion_id == body.companionId))  # 先删除旧的关联
        if services:
            db.add_all([CompanionService(companion_id=body.companionId, service_id=s.serviceId,
                                         price=s.price if s.price is not None else 0, description=s.description) for s in services])  # 再插入新关联
    user_id = get_companion_user_id(db, body.companionId)  # 关联用户ID(存量未回填时为 None)
    if user_id is not None:  # 有关联用户才同步(昵称/性别/头像仅传了才更新)
        user_fields: dict = {}  # 用户侧同步字段
        if body.nickName is not None:  # 昵称 -> 用户名
            user_fields["user_name"] = body.nickName
        if body.gender is not None:  # 性别同步
            user_fields["sex"] = body.gender
        if body.avatar is not None:  # 头像同步
            user_fields["avatar"] = body.avatar
        if user_fields:  # 同事务更新关联用户
            db.execute(update(User).where(User.user_id == user_id).values(**user_fields))
    db.commit()  # 更新 + 删旧 + 插新 + 用户同步 同一事务一次性提交
    return rows


def delete_companion_by_ids(db: Session, companion_ids: list[int]) -> int:
    """删除陪玩师 + 连带删除关联用户(同一事务, 外键 ON DELETE CASCADE 自动清理各自关联记录)

    参数: db 请求级 Session / companion_ids 陪玩师ID列表; 返回受影响行数
    """
    user_ids = db.scalars(  # 这批陪玩师的关联用户ID(过滤存量未回填的 NULL)
        select(Companion.user_id).where(Companion.companion_id.in_(companion_ids), Companion.user_id.is_not(None))
    ).all()
    rows = db.execute(delete(Companion).where(Companion.companion_id.in_(companion_ids))).rowcount  # 删陪玩师(级联清两张关联表等)
    if user_ids:  # 有关联用户才删除(级联清其钱包流水/关注/优惠券/打赏记录)
        db.execute(delete(User).where(User.user_id.in_(user_ids)))
    db.commit()  # 两张主表同一事务一次性提交
    return rows