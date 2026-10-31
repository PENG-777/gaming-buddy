"""
ORM 实体（字段与 fast.sql 表结构一一对应）
"""
from datetime import datetime, date  # 标准库: 日期时间类型

# 第三方: SQLAlchemy 列类型与数据库函数
from sqlalchemy import DateTime, Integer, String, func, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column  # 第三方: 2.0 类型化声明映射

from core.database import Base  # 项目内: ORM 声明基类


class User(Base):
    """用户表 user"""
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column("user_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_name: Mapped[str] = mapped_column("user_name", String(50))  # 用户名(重复由业务层校验)
    sex: Mapped[int | None] = mapped_column("sex", Integer, nullable=True)  # 性别(可空)
    avatar: Mapped[str | None] = mapped_column("avatar", String(255), nullable=True)  # 头像 URL(可空)
    password: Mapped[str] = mapped_column("password", String(255))  # 密码(明文存储)
    role_id: Mapped[int] = mapped_column("role_id", Integer, nullable=False, server_default="2")  # 角色ID, 默认 2(普通用户)
    balance: Mapped[int] = mapped_column("balance", Integer, nullable=False, server_default="0")  # 钱包余额, 元
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class Role(Base):
    """角色表 role"""
    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column("role_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    role_name: Mapped[str] = mapped_column("role_name", String(255))  # 角色名称
    role_sort: Mapped[int] = mapped_column("role_sort", Integer, nullable=False)  # 显示顺序
    remark: Mapped[str | None] = mapped_column("remark", String(500), nullable=True)  # 备注(可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class Menu(Base):
    """菜单表 menu"""
    __tablename__ = "menu"

    menu_id: Mapped[int] = mapped_column("menu_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    menu_name: Mapped[str] = mapped_column("menu_name", String(100))  # 菜单名称
    parent_id: Mapped[int | None] = mapped_column("parent_id", Integer, nullable=True,
                                                  server_default="0")  # 父菜单ID, 0 表示顶级
    menu_sort: Mapped[int] = mapped_column("menu_sort", Integer, nullable=False)  # 显示顺序
    path: Mapped[str | None] = mapped_column("path", String(255), nullable=True)  # 路由地址(可空)
    component: Mapped[str | None] = mapped_column("component", String(255), nullable=True)  # 组件路径(可空)
    menu_type: Mapped[str] = mapped_column("menu_type", String(10))  # 菜单类型: M 目录 / C 菜单
    icon: Mapped[str | None] = mapped_column("icon", String(100), nullable=True)  # 图标名称(可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class RoleMenu(Base):
    """角色菜单关联表 role_menu"""
    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column("role_id", Integer, primary_key=True)  # 角色ID(联合主键)
    menu_id: Mapped[int] = mapped_column("menu_id", Integer, primary_key=True)  # 菜单ID(联合主键)


class GameCategory(Base):
    """
    游戏分类表 game_category
    """
    __tablename__ = "game_category"

    game_id: Mapped[int] = mapped_column("game_id", Integer, primary_key=True, autoincrement=True)  # 主键ID, ID自增(唯一标识)
    game_name: Mapped[str] = mapped_column("game_name", String(50))  # 游戏名称(重复由逻辑层进行校验)
    image: Mapped[str | None] = mapped_column("image", String(255), nullable=True)  # 游戏图片URL(可空)
    tags: Mapped[str | None] = mapped_column("tags", String(255), nullable=True)  # 标签, 逗号分隔(可空)
    description: Mapped[str | None] = mapped_column("description", String(255), nullable=True)  # 描述(可空)
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态(0启用 1停用)
    game_sort: Mapped[int] = mapped_column("game_sort", Integer, nullable=False, server_default="0")  # 显示顺序
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class ServiceItem(Base):
    """
    服务项目表 service_item
    """
    __tablename__ = "service_item"

    service_id: Mapped[int] = mapped_column("service_id", Integer, primary_key=True, autoincrement=True)  # 主键ID, ID自增(唯一标识)
    service_name: Mapped[str] = mapped_column("service_name", String(50))  # 服务名称(重复由逻辑层进行校验)
    image: Mapped[str | None] = mapped_column("image", String(255), nullable=True)  # 服务图片URL(可空)
    description: Mapped[str | None] = mapped_column("description", String(255), nullable=True)  # 描述(可空)
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态(0启用 1停用)
    service_sort: Mapped[int] = mapped_column("service_sort", Integer, nullable=False, server_default="0")  # 显示顺序
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间

class Companion(Base):
    """陪玩师表 companion"""
    __tablename__ = "companion"

    companion_id: Mapped[int] = mapped_column("companion_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int | None] = mapped_column("user_id", Integer, nullable=True)  # 关联用户ID(user表, 新增陪玩师时同步创建并回填)
    nick_name: Mapped[str] = mapped_column("nick_name", String(50))  # 昵称(重复由业务层校验)
    gender: Mapped[int] = mapped_column("gender", Integer, nullable=False, server_default="0")  # 性别: 0 男 / 1 女
    age: Mapped[int | None] = mapped_column("age", Integer, nullable=True)  # 年龄(可空)
    city: Mapped[str | None] = mapped_column("city", String(50), nullable=True)  # 城市(可空)
    avatar: Mapped[str | None] = mapped_column("avatar", String(255), nullable=True)  # 头像 URL(可空)
    voice: Mapped[str | None] = mapped_column("voice", String(50), nullable=True)  # 声线(可空)
    price: Mapped[int | None] = mapped_column("price", Integer, nullable=True)  # 起步价, 元/小时(可空)
    intro: Mapped[str | None] = mapped_column("intro", String(500), nullable=True)  # 个人简介(可空)
    tags: Mapped[str | None] = mapped_column("tags", String(255), nullable=True)  # 标签, 逗号分隔(可空)
    certified: Mapped[int] = mapped_column("certified", Integer, nullable=False, server_default="0")  # 认证状态: 0 未认证 / 1 已认证
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 启用 / 1 停用
    main_game_id: Mapped[int | None] = mapped_column("main_game_id", Integer, nullable=True)  # 主游戏ID(game_category, 由 games[0] 同步)
    main_rank: Mapped[str | None] = mapped_column("main_rank", String(50), nullable=True)  # 主游戏段位(由 games[0] 同步)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class CompanionGame(Base):
    """陪玩师游戏关联表 companion_game"""
    __tablename__ = "companion_game"

    companion_id: Mapped[int] = mapped_column("companion_id", Integer, primary_key=True)  # 陪玩师ID(联合主键)
    game_id: Mapped[int] = mapped_column("game_id", Integer, primary_key=True)  # 游戏ID(联合主键)
    game_rank: Mapped[str | None] = mapped_column("game_rank", String(50), nullable=True)  # 段位(可空)


class CompanionService(Base):
    """陪玩师服务关联表 companion_service"""
    __tablename__ = "companion_service"

    companion_id: Mapped[int] = mapped_column("companion_id", Integer, primary_key=True)  # 陪玩师ID(联合主键)
    service_id: Mapped[int] = mapped_column("service_id", Integer, primary_key=True)  # 服务项目ID(联合主键)
    price: Mapped[int] = mapped_column("price", Integer, nullable=False, server_default="0")  # 该服务价格, 元/小时
    description: Mapped[str | None] = mapped_column("description", String(255), nullable=True)  # 该服务说明(可空)


class Banner(Base):
    """首页轮播图表 banner"""
    __tablename__ = "banner"

    banner_id: Mapped[int] = mapped_column("banner_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    title: Mapped[str] = mapped_column("title", String(50))  # 标题
    subtitle: Mapped[str | None] = mapped_column("subtitle", String(100), nullable=True)  # 副标题(可空)
    tag: Mapped[str | None] = mapped_column("tag", String(20), nullable=True)  # 标签角标文字(可空)
    image: Mapped[str | None] = mapped_column("image", String(255), nullable=True)  # 轮播图片 URL(/profile/upload/.., 可空, 缺失时前端回退纯色)
    bg_color: Mapped[str | None] = mapped_column("bg_color", String(10), nullable=True)  # 回退背景色(如 #fff3e8, 可空)
    fg_color: Mapped[str | None] = mapped_column("fg_color", String(10), nullable=True)  # 回退前景色(按钮底色/文字色, 可空)
    link_text: Mapped[str | None] = mapped_column("link_text", String(20), nullable=True)  # 按钮文字(可空)
    link_url: Mapped[str | None] = mapped_column("link_url", String(255), nullable=True)  # 跳转地址(站内路由, 可空)
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 启用 / 1 停用
    banner_sort: Mapped[int] = mapped_column("banner_sort", Integer, nullable=False, server_default="0")  # 显示顺序(小的在前)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class WalletTransaction(Base):
    """钱包流水表 wallet_transaction"""
    __tablename__ = "wallet_transaction"

    tx_id: Mapped[int] = mapped_column("tx_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user)
    type: Mapped[str] = mapped_column("type", String(20))  # 类型: recharge 充值 / consume 消费 / refund 退款 / reward 打赏 / adjust 人工调整
    amount: Mapped[int] = mapped_column("amount", Integer)  # 变动金额, 元(正数收入负数支出)
    balance_after: Mapped[int] = mapped_column("balance_after", Integer)  # 变动后余额, 元(对账用)
    note: Mapped[str | None] = mapped_column("note", String(255), nullable=True)  # 备注(可空)
    operator: Mapped[str | None] = mapped_column("operator", String(50), nullable=True)  # 操作人(人工调整记录管理员名, 用户自行为空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 时间, 默认数据库当前时间


class Coupon(Base):
    """优惠券表 coupon"""
    __tablename__ = "coupon"

    coupon_id: Mapped[int] = mapped_column("coupon_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    coupon_name: Mapped[str] = mapped_column("coupon_name", String(50))  # 券名称(重复由业务层校验)
    amount: Mapped[int] = mapped_column("amount", Integer)  # 面额, 元
    threshold: Mapped[int] = mapped_column("threshold", Integer, nullable=False, server_default="0")  # 使用门槛, 元: 0 无门槛 / >0 满减门槛
    valid_days: Mapped[int] = mapped_column("valid_days", Integer, nullable=False, server_default="1")  # 领取后有效天数
    per_limit: Mapped[int] = mapped_column("per_limit", Integer, nullable=False, server_default="1")  # 每人限领次数
    total_count: Mapped[int] = mapped_column("total_count", Integer, nullable=False, server_default="0")  # 发放总量: 0 不限量
    description: Mapped[str | None] = mapped_column("description", String(255), nullable=True)  # 说明(可空)
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 启用 / 1 停用
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class UserCoupon(Base):
    """用户优惠券表 user_coupon(领取记录)"""
    __tablename__ = "user_coupon"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user)
    coupon_id: Mapped[int] = mapped_column("coupon_id", Integer)  # 优惠券ID(coupon)
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 未使用 / 1 已使用(过期为动态判定)
    receive_time: Mapped[datetime | None] = mapped_column(
        "receive_time", DateTime, server_default=func.now()
    )  # 领取时间, 默认数据库当前时间
    expire_time: Mapped[datetime | None] = mapped_column("expire_time", DateTime, nullable=True)  # 过期时间, 领取时间+有效天数(可空)
    use_time: Mapped[datetime | None] = mapped_column("use_time", DateTime, nullable=True)  # 使用时间(可空)


class CompanionOrder(Base):
    """陪玩订单表 companion_order"""
    __tablename__ = "companion_order"

    order_id: Mapped[int] = mapped_column("order_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    order_no: Mapped[str] = mapped_column("order_no", String(30))  # 订单号(GB开头, 唯一)
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 下单用户ID(user)
    companion_id: Mapped[int] = mapped_column("companion_id", Integer)  # 陪玩师ID(companion)
    service_id: Mapped[int] = mapped_column("service_id", Integer)  # 服务项目ID(service_item, 定位companion_service价格)
    service_name: Mapped[str] = mapped_column("service_name", String(50))  # 服务名称(下单时快照)
    price: Mapped[int] = mapped_column("price", Integer)  # 服务单价, 元/小时(下单时快照)
    hours: Mapped[int] = mapped_column("hours", Integer)  # 服务时长, 小时(1-5)
    service_date: Mapped[date] = mapped_column("service_date", Date)  # 预约服务日期
    start_hour: Mapped[int] = mapped_column("start_hour", Integer)  # 开始时段(10-22整点)
    note: Mapped[str | None] = mapped_column("note", String(100), nullable=True)  # 需求备注(可空)
    user_coupon_id: Mapped[int | None] = mapped_column("user_coupon_id", Integer, nullable=True)  # 使用的用户优惠券记录ID(user_coupon, 可空)
    coupon_name: Mapped[str | None] = mapped_column("coupon_name", String(50), nullable=True)  # 优惠券名称(下单时快照, 可空)
    coupon_amount: Mapped[int] = mapped_column("coupon_amount", Integer, nullable=False, server_default="0")  # 优惠金额, 元
    gross_amount: Mapped[int] = mapped_column("gross_amount", Integer)  # 订单原价, 元(单价*时长)
    amount: Mapped[int] = mapped_column("amount", Integer)  # 实付金额, 元(原价-优惠)
    pay_method: Mapped[str | None] = mapped_column("pay_method", String(10), nullable=True)  # 支付方式: balance 余额 / wechat 微信 / alipay 支付宝(待支付为空)
    status: Mapped[str] = mapped_column("status", String(20), nullable=False, server_default="pending")  # 状态: pending 待支付 / booked 待开始 / ongoing 进行中 / completed 已完成 / refunding 退款中 / cancelled 已取消
    pay_time: Mapped[datetime | None] = mapped_column("pay_time", DateTime, nullable=True)  # 支付时间(可空)
    start_time: Mapped[datetime | None] = mapped_column("start_time", DateTime, nullable=True)  # 服务开始时间(可空)
    end_time: Mapped[datetime | None] = mapped_column("end_time", DateTime, nullable=True)  # 服务完成时间(可空)
    cancel_reason: Mapped[str | None] = mapped_column("cancel_reason", String(100), nullable=True)  # 取消原因(可空)
    review_rating: Mapped[int | None] = mapped_column("review_rating", Integer, nullable=True)  # 评价星级: 1-5(未评价为空)
    review_tags: Mapped[str | None] = mapped_column("review_tags", String(100), nullable=True)  # 评价标签, 逗号分隔(可空)
    review_content: Mapped[str | None] = mapped_column("review_content", String(255), nullable=True)  # 评价内容(可空)
    review_time: Mapped[datetime | None] = mapped_column("review_time", DateTime, nullable=True)  # 评价时间(可空)
    review_reply: Mapped[str | None] = mapped_column("review_reply", String(255), nullable=True)  # 平台回复内容(可空, 重复回复覆盖更新)
    review_reply_time: Mapped[datetime | None] = mapped_column("review_reply_time", DateTime, nullable=True)  # 平台回复时间(可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 下单时间, 默认数据库当前时间


class Complaint(Base):
    """订单投诉表 complaint"""
    __tablename__ = "complaint"

    complaint_id: Mapped[int] = mapped_column("complaint_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    order_id: Mapped[int] = mapped_column("order_id", Integer)  # 订单ID(companion_order, 每单限投诉一次, uk_order_id 兜底)
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 投诉用户ID(user, 与订单下单人一致)
    complaint_type: Mapped[str] = mapped_column("complaint_type", String(20))  # 投诉类型: 服务态度差 / 迟到未提供服务 / 技术水平与描述不符 / 诱导私下交易 / 言语不当 / 其他问题
    content: Mapped[str] = mapped_column("content", String(200))  # 投诉内容
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 处理状态: 0 待处理 / 1 已处理
    handle_result: Mapped[str | None] = mapped_column("handle_result", String(20), nullable=True)  # 处理结果(可空): 警告陪玩师 / 全额退款 / 驳回投诉 / 其他
    reply: Mapped[str | None] = mapped_column("reply", String(500), nullable=True)  # 处理说明(可空)
    handle_time: Mapped[datetime | None] = mapped_column("handle_time", DateTime, nullable=True)  # 处理时间(可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 提交时间, 默认数据库当前时间


class Gift(Base):
    """打赏礼物表 gift"""
    __tablename__ = "gift"

    gift_id: Mapped[int] = mapped_column("gift_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    gift_name: Mapped[str] = mapped_column("gift_name", String(50))  # 礼物名称(重复由业务层校验)
    image: Mapped[str | None] = mapped_column("image", String(255), nullable=True)  # 礼物图片 URL(/profile/upload/.., 可空)
    price: Mapped[int] = mapped_column("price", Integer)  # 价格, 元
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 启用 / 1 停用
    gift_sort: Mapped[int] = mapped_column("gift_sort", Integer, nullable=False, server_default="0")  # 显示顺序
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间



class Reward(Base):
    """用户打赏记录表 reward"""
    __tablename__ = "reward"

    reward_id: Mapped[int] = mapped_column("reward_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 打赏用户ID(user)
    companion_id: Mapped[int] = mapped_column("companion_id", Integer)  # 陪玩师ID(companion)
    gift_name: Mapped[str] = mapped_column("gift_name", String(50))  # 礼物名称(打赏时快照)
    gift_image: Mapped[str | None] = mapped_column("gift_image", String(255), nullable=True)  # 礼物图片 URL(打赏时快照, 可空)
    amount: Mapped[int] = mapped_column("amount", Integer)  # 打赏金额, 元(打赏时快照)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 打赏时间, 默认数据库当前时间


class Follow(Base):
    """用户关注表 follow"""
    __tablename__ = "follow"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user)
    companion_id: Mapped[int] = mapped_column("companion_id", Integer)  # 陪玩师ID(companion)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 关注时间, 默认数据库当前时间


class Notice(Base):
    """平台公告表 notice"""
    __tablename__ = "notice"

    notice_id: Mapped[int] = mapped_column("notice_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    title: Mapped[str] = mapped_column("title", String(100))  # 公告标题
    notice_type: Mapped[str] = mapped_column("notice_type", String(10), nullable=False, server_default="活动")  # 公告类型: 保障 / 活动 / 上新 / 安全
    content: Mapped[str] = mapped_column("content", String(1000))  # 公告正文
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 发布 / 1 撤下
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 发布时间, 默认数据库当前时间

class Faq(Base):
    """帮助中心FAQ表 faq"""
    __tablename__ = "faq"

    faq_id: Mapped[int] = mapped_column("faq_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    category: Mapped[str] = mapped_column("category", String(10), nullable=False, server_default="新手指南")  # 所属分组: 新手指南 / 下单支付 / 服务保障
    question: Mapped[str] = mapped_column("question", String(200))  # 问题标题
    answer: Mapped[str] = mapped_column("answer", String(1000))  # 答案正文
    sort: Mapped[int] = mapped_column("sort", Integer, nullable=False, server_default="0")  # 组内排序, 小的在前
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 状态: 0 显示 / 1 隐藏
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间


class Feedback(Base):
    """意见反馈表 feedback"""
    __tablename__ = "feedback"

    feedback_id: Mapped[int] = mapped_column("feedback_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 提交用户ID(user)
    feedback_type: Mapped[str] = mapped_column("feedback_type", String(10))  # 反馈类型: 功能建议 / 体验问题 / 内容举报 / 其他
    content: Mapped[str] = mapped_column("content", String(200))  # 反馈内容
    status: Mapped[int] = mapped_column("status", Integer, nullable=False, server_default="0")  # 处理状态: 0 待处理 / 1 已处理
    reply: Mapped[str | None] = mapped_column("reply", String(500), nullable=True)  # 处理回复(可空)
    reply_time: Mapped[datetime | None] = mapped_column("reply_time", DateTime, nullable=True)  # 回复时间(可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 提交时间, 默认数据库当前时间


class ServiceConversation(Base):
    """官方客服会话表 service_conversation"""
    __tablename__ = "service_conversation"

    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user, 一人一会话, uk_conv_user 兜底)
    last_message: Mapped[str | None] = mapped_column("last_message", String(500), nullable=True)  # 最后一条消息(快照, 列表展示用, 可空)
    user_unread: Mapped[int] = mapped_column("user_unread", Integer, nullable=False, server_default="0")  # 用户未读数(客服回复+1, 用户读取清零)
    last_time: Mapped[datetime | None] = mapped_column("last_time", DateTime, nullable=True)  # 最后消息时间(列表排序用, 可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间



class ServiceMessage(Base):
    """官方客服消息表 service_message"""
    __tablename__ = "service_message"

    message_id: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer)  # 会话ID(service_conversation)
    sender_type: Mapped[int] = mapped_column("sender_type", Integer, nullable=False, server_default="0")  # 发送方: 0 用户 / 1 客服
    content: Mapped[str] = mapped_column("content", String(1000))  # 消息内容
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 发送时间, 默认数据库当前时间


class PrivateConversation(Base):
    """用户私聊会话表 private_conversation(用户 <-> 陪玩师, 一对一会话)"""
    __tablename__ = "private_conversation"

    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user, 发起私聊的普通用户)
    companion_id: Mapped[int] = mapped_column("companion_id", Integer)  # 陪玩师ID(companion, uk_pc_user_companion 兜底)
    last_message: Mapped[str | None] = mapped_column("last_message", String(500), nullable=True)  # 最后一条消息(快照, 列表展示用, 可空)
    user_unread: Mapped[int] = mapped_column("user_unread", Integer, nullable=False, server_default="0")  # 用户未读数(陪玩师回复+1, 用户读取清零)
    companion_unread: Mapped[int] = mapped_column("companion_unread", Integer, nullable=False, server_default="0")  # 陪玩师未读数(用户发言+1, 陪玩师读取清零; 管理员查看不动)
    last_time: Mapped[datetime | None] = mapped_column("last_time", DateTime, nullable=True)  # 最后消息时间(列表排序用, 可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间



class PrivateMessage(Base):
    """用户私聊消息表 private_message"""
    __tablename__ = "private_message"

    message_id: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer)  # 会话ID(private_conversation)
    sender_type: Mapped[int] = mapped_column("sender_type", Integer, nullable=False, server_default="0")  # 发送方: 0 用户 / 1 陪玩师
    content: Mapped[str] = mapped_column("content", String(1000))  # 消息内容
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 发送时间, 默认数据库当前时间


class AgentConversation(Base):
    """AI 助手会话表 agent_conversation"""
    __tablename__ = "agent_conversation"

    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    user_id: Mapped[int] = mapped_column("user_id", Integer)  # 用户ID(user)
    scene: Mapped[str] = mapped_column("scene", String(20))  # 场景: user 用户端助手 / analyst 经营分析
    title: Mapped[str | None] = mapped_column("title", String(100), nullable=True, server_default="新对话")  # 会话标题(首轮自动命名, 可空)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间
    update_time: Mapped[datetime | None] = mapped_column(
        "update_time", DateTime, server_default=func.now(), onupdate=func.now()
    )  # 最后活跃时间, 行更新时自动刷新


class AgentMessage(Base):
    """AI 助手消息表 agent_message"""
    __tablename__ = "agent_message"

    message_id: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    conversation_id: Mapped[int] = mapped_column("conversation_id", Integer)  # 会话ID(agent_conversation)
    role: Mapped[str] = mapped_column("role", String(20))  # 角色: user 用户 / assistant 助手
    agent_name: Mapped[str | None] = mapped_column("agent_name", String(50), nullable=True)  # 应答 Agent 名(assistant 消息记录主要贡献者, 可空)
    content: Mapped[str] = mapped_column("content", Text)  # 消息内容(markdown)
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 发送时间, 默认数据库当前时间


class AgentConfig(Base):
    """Agent 配置表 agent_config(启停/提示词/温度, 管理页可编辑)"""
    __tablename__ = "agent_config"

    agent_id: Mapped[int] = mapped_column("agent_id", Integer, primary_key=True, autoincrement=True)  # 主键, 自增
    agent_key: Mapped[str] = mapped_column("agent_key", String(50))  # Agent 标识(supervisor_user/recommendation_agent 等)
    agent_name: Mapped[str] = mapped_column("agent_name", String(50))  # 显示名称
    scene: Mapped[str] = mapped_column("scene", String(20))  # 归属场景: user 用户端助手 / analyst 经营分析
    description: Mapped[str | None] = mapped_column("description", String(500), nullable=True)  # 职责描述(管理页展示, 可空)
    prompt: Mapped[str] = mapped_column("prompt", Text)  # 系统提示词(管理页可编辑, 下次对话生效)
    tools: Mapped[str | None] = mapped_column("tools", String(500), nullable=True)  # 工具清单(只读展示, 代码注册决定, 可空)
    temperature: Mapped[float] = mapped_column("temperature", Numeric(3, 2), nullable=False, server_default="0.30")  # 采样温度(0-1)
    enabled: Mapped[int] = mapped_column("enabled", Integer, nullable=False, server_default="0")  # 状态: 0 启用 / 1 停用
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # 创建时间, 默认数据库当前时间
    update_time: Mapped[datetime | None] = mapped_column(
        "update_time", DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间, 行更新时自动刷新