"""
实体请求体（用户 / 角色 / 菜单）

全部字段可选, 更新时只处理请求中实际出现且非 null 的字段(动态更新)。
字段约束(max_length/ge/le)与数据库列宽一致, 超长/越界在参数层直接拦截。
"""
from typing import Optional  # 标准库: 可空类型标注

from pydantic import BaseModel, ConfigDict, Field  # 第三方: 请求体模型基类与配置/字段约束


class UserBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    userId: Optional[int] = None  # 用户ID(更新时定位记录)
    userName: Optional[str] = Field(None, max_length=50)  # 用户名(与表列宽一致)
    sex: Optional[int] = Field(None, ge=0, le=1)  # 性别(0男 1女)
    avatar: Optional[str] = Field(None, max_length=255)  # 头像 URL
    password: Optional[str] = Field(None, max_length=100)  # 密码
    roleId: Optional[int] = None  # 角色 ID
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class RoleBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    roleId: Optional[int] = None  # 角色ID(更新时定位记录)
    roleName: Optional[str] = Field(None, max_length=255)  # 角色名称(与表列宽一致)
    roleSort: Optional[int] = None  # 显示顺序
    remark: Optional[str] = Field(None, max_length=500)  # 备注(与表列宽一致)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)
    menuIds: Optional[list[int]] = None  # 授权菜单ID列表(维护 role_menu 关联)


class MenuBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    menuId: Optional[int] = None  # 菜单ID(更新时定位记录)
    menuName: Optional[str] = Field(None, max_length=100)  # 菜单名称(与表列宽一致)
    parentId: Optional[int] = None  # 父菜单ID(0 表示顶级)
    menuSort: Optional[int] = None  # 显示顺序
    path: Optional[str] = Field(None, max_length=255)  # 路由地址(与表列宽一致)
    component: Optional[str] = Field(None, max_length=255)  # 组件路径(与表列宽一致)
    menuType: Optional[str] = Field(None, max_length=10)  # 菜单类型: M 目录 / C 菜单
    icon: Optional[str] = Field(None, max_length=100)  # 图标名称(与表列宽一致)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class GameBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    gameId: Optional[int] = None  # 游戏ID(更新时定位记录)
    gameName: Optional[str] = Field(None, max_length=50)  # 游戏名称
    image: Optional[str] = Field(None, max_length=255)  # 游戏图片 URL(与表列宽一致)
    tags: Optional[str] = Field(None, max_length=255)  # 标签, 逗号分隔(与表列宽一致)
    description: Optional[str] = Field(None, max_length=255)  # 描述(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    gameSort: Optional[int] = None  # 显示顺序
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class ServiceItemBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    serviceId: Optional[int] = None  # 服务ID(更新时定位记录)
    serviceName: Optional[str] = Field(None, max_length=50)  # 服务名称
    image: Optional[str] = Field(None, max_length=255)  # 服务图片 URL(与表列宽一致)
    description: Optional[str] = Field(None, max_length=255)  # 描述(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    serviceSort: Optional[int] = None  # 显示顺序
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class CompanionGameItem(BaseModel):
    """擅长游戏关联项(陪玩师表单子项)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    gameId: Optional[int] = None  # 游戏ID(game_category)
    gameRank: Optional[str] = Field(None, max_length=50)  # 段位(与表列宽一致)


class CompanionServiceItem(BaseModel):
    """服务项目关联项(陪玩师表单子项)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    serviceId: Optional[int] = None  # 服务项目ID(service_item)
    price: Optional[int] = Field(None, ge=0)  # 该服务价格, 元/小时
    description: Optional[str] = Field(None, max_length=255)  # 该服务说明(与表列宽一致)


class CompanionBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    companionId: Optional[int] = None  # 陪玩师ID(更新时定位记录)
    nickName: Optional[str] = Field(None, max_length=50)  # 昵称(与表列宽一致)
    gender: Optional[int] = Field(None, ge=0, le=1)  # 性别(0男 1女)
    age: Optional[int] = Field(None, ge=1, le=120)  # 年龄
    city: Optional[str] = Field(None, max_length=50)  # 城市(与表列宽一致)
    avatar: Optional[str] = Field(None, max_length=255)  # 头像 URL(与表列宽一致)
    voice: Optional[str] = Field(None, max_length=50)  # 声线(与表列宽一致)
    price: Optional[int] = Field(None, ge=0)  # 起步价, 元/小时
    intro: Optional[str] = Field(None, max_length=500)  # 个人简介(与表列宽一致)
    tags: Optional[str] = Field(None, max_length=255)  # 标签, 逗号分隔(与表列宽一致)
    certified: Optional[int] = Field(None, ge=0, le=1)  # 认证状态(0未认证 1已认证)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    mainGameId: Optional[int] = None  # 主游戏ID(有 games 时以 games[0] 为准同步)
    mainRank: Optional[str] = Field(None, max_length=50)  # 主游戏段位(有 games 时以 games[0] 为准同步)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)
    games: Optional[list[CompanionGameItem]] = None  # 擅长游戏列表(None 不动作关联, 空数组清空)
    services: Optional[list[CompanionServiceItem]] = None  # 服务项目列表(None 不动作关联, 空数组清空)


class BannerBody(BaseModel):
    """首页轮播图请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    bannerId: Optional[int] = None  # 轮播图ID(更新时定位记录)
    title: Optional[str] = Field(None, max_length=50)  # 标题(与表列宽一致)
    subtitle: Optional[str] = Field(None, max_length=100)  # 副标题(与表列宽一致)
    tag: Optional[str] = Field(None, max_length=20)  # 标签角标文字(与表列宽一致)
    image: Optional[str] = Field(None, max_length=255)  # 轮播图片 URL(上传返回, 可空)
    bgColor: Optional[str] = Field(None, max_length=10)  # 回退背景色(如 #fff3e8)
    fgColor: Optional[str] = Field(None, max_length=10)  # 回退前景色(按钮底色/文字色)
    linkText: Optional[str] = Field(None, max_length=20)  # 按钮文字(与表列宽一致)
    linkUrl: Optional[str] = Field(None, max_length=255)  # 跳转地址(站内路由, 与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    bannerSort: Optional[int] = Field(None, ge=0)  # 显示顺序(小的在前)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class WalletRechargeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    amount: Optional[int] = Field(None, ge=1, le=100000)  # 充值金额, 元(正整数)
    payMethod: Optional[str] = Field(None, max_length=20)  # 支付方式(alipay支付宝 wechat微信支付)


class WalletChangeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    amount: Optional[int] = Field(None, ge=-100000, le=100000)  # 变动金额, 元(正数收入负数支出, 不为 0)
    type: Optional[str] = Field(None, max_length=20)  # 类型(consume消费 refund退款 reward打赏)
    note: Optional[str] = Field(None, max_length=255)  # 备注(与表列宽一致)


class WalletAdjustBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    userId: Optional[int] = None  # 被调整用户ID
    amount: Optional[int] = Field(None, ge=-100000, le=100000)  # 调整金额, 元(正数增加负数扣减, 不为 0)
    note: Optional[str] = Field(None, max_length=255)  # 调整原因(必填, 与表列宽一致)


class CouponBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    couponId: Optional[int] = None  # 优惠券ID(更新时定位记录)
    couponName: Optional[str] = Field(None, max_length=50)  # 券名称(与表列宽一致)
    amount: Optional[int] = Field(None, ge=1)  # 面额, 元(正整数)
    threshold: Optional[int] = Field(None, ge=0)  # 使用门槛, 元: 0 无门槛 / >0 满减门槛
    validDays: Optional[int] = Field(None, ge=1)  # 领取后有效天数
    perLimit: Optional[int] = Field(None, ge=1)  # 每人限领次数
    totalCount: Optional[int] = Field(None, ge=0)  # 发放总量: 0 不限量
    description: Optional[str] = Field(None, max_length=255)  # 说明(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class OrderCreateBody(BaseModel):
    """用户端下单请求体(价格/金额由后端查 companion_service 定价, 不接受前端传价)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    companionId: Optional[int] = None  # 陪玩师ID(companion)
    serviceId: Optional[int] = None  # 服务项目ID(service_item)
    date: Optional[str] = Field(None, max_length=10)  # 预约服务日期('yyyy-MM-dd')
    startHour: Optional[int] = Field(None, ge=0, le=23)  # 开始时段(0-23整点)
    hours: Optional[int] = Field(None, ge=1, le=5)  # 服务时长, 小时(1-5)
    note: Optional[str] = Field(None, max_length=100)  # 需求备注(可空)
    userCouponId: Optional[int] = None  # 使用的用户优惠券记录ID(可空, 不用券)


class OrderPayBody(BaseModel):
    """用户端订单支付请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    orderNo: Optional[str] = Field(None, max_length=30)  # 订单号(定位订单)
    payMethod: Optional[str] = Field(None, max_length=10)  # 支付方式: balance 余额 / wechat 微信 / alipay 支付宝


class OrderCancelBody(BaseModel):
    """订单取消请求体(用户端按 orderNo 取消自己的订单, 管理端按 orderId 代取消)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    orderNo: Optional[str] = Field(None, max_length=30)  # 订单号(用户端取消用)
    orderId: Optional[int] = None  # 订单ID(管理端代取消用)
    cancelReason: Optional[str] = Field(None, max_length=100)  # 取消原因(可空, 管理端缺省为"管理员取消")


class OrderReviewBody(BaseModel):
    """用户端订单评价请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    orderNo: Optional[str] = Field(None, max_length=30)  # 订单号(定位订单)
    rating: Optional[int] = Field(None, ge=1, le=5)  # 星级(1-5)
    tags: Optional[str] = Field(None, max_length=100)  # 评价标签, 逗号分隔(可空)
    content: Optional[str] = Field(None, max_length=255)  # 评价内容(可空)


class ReviewReplyBody(BaseModel):
    """管理端评价回复请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    orderId: Optional[int] = None  # 订单ID(定位已评价订单)
    reply: Optional[str] = Field(None, max_length=255)  # 回复内容(与表列宽一致)


class ComplaintBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    complaintId: Optional[int] = None  # 投诉ID(管理端处理时定位记录)
    orderNo: Optional[str] = Field(None, max_length=30)  # 订单号(用户端发起投诉时定位订单)
    complaintType: Optional[str] = Field(None, max_length=20)  # 投诉类型(服务态度差/迟到未提供服务/技术水平与描述不符/诱导私下交易/言语不当/其他问题)
    content: Optional[str] = Field(None, max_length=200)  # 投诉内容(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 处理状态(0待处理 1已处理)
    handleResult: Optional[str] = Field(None, max_length=20)  # 处理结果(警告陪玩师/全额退款/驳回投诉/其他)
    reply: Optional[str] = Field(None, max_length=500)  # 处理说明(与表列宽一致)


class GiftBody(BaseModel):
    """打赏礼物请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    giftId: Optional[int] = None  # 礼物ID(更新时定位记录)
    giftName: Optional[str] = Field(None, max_length=50)  # 礼物名称(与表列宽一致)
    image: Optional[str] = Field(None, max_length=255)  # 礼物图片 URL(上传返回, 可空)
    price: Optional[int] = Field(None, ge=1)  # 价格, 元(正整数)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)
    giftSort: Optional[int] = Field(None, ge=0)  # 显示顺序(小的在前)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)



class RewardBody(BaseModel):
    """用户打赏请求体(金额与礼物信息由后端查 gift 表定价, 不接受前端传快照)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    rewardId: Optional[int] = None  # 打赏ID(占位, 打赏为新增操作)
    companionId: Optional[int] = None  # 陪玩师ID(companion)
    giftId: Optional[int] = None  # 礼物ID(gift)
    createTime: Optional[str] = None  # 打赏时间(占位, 走数据库默认值)


class FollowBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    id: Optional[int] = None  # 记录ID(更新时定位记录)
    userId: Optional[int] = None  # 用户ID(用户端操作时以后端登录用户为准)
    companionId: Optional[int] = None  # 陪玩师ID(companion)
    createTime: Optional[str] = None  # 关注时间('yyyy-MM-dd HH:mm:ss' 字符串)


class NoticeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    noticeId: Optional[int] = None  # 公告ID(更新时定位记录)
    title: Optional[str] = Field(None, max_length=100)  # 公告标题(与表列宽一致)
    noticeType: Optional[str] = Field(None, max_length=10)  # 公告类型(保障/活动/上新/安全)
    content: Optional[str] = Field(None, max_length=1000)  # 公告正文(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0发布 1撤下)
    createTime: Optional[str] = None  # 发布时间('yyyy-MM-dd HH:mm:ss' 字符串)

class FaqBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    faqId: Optional[int] = None  # 问题ID(更新时定位记录)
    category: Optional[str] = Field(None, max_length=10)  # 所属分组(新手指南/下单支付/服务保障)
    question: Optional[str] = Field(None, max_length=200)  # 问题标题(与表列宽一致)
    answer: Optional[str] = Field(None, max_length=1000)  # 答案正文(与表列宽一致)
    sort: Optional[int] = None  # 组内排序(小的在前)
    status: Optional[int] = Field(None, ge=0, le=1)  # 状态(0显示 1隐藏)
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)


class FeedbackBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    feedbackId: Optional[int] = None  # 反馈ID(更新时定位记录)
    userId: Optional[int] = None  # 提交用户ID(用户端提交时以后端登录用户为准)
    feedbackType: Optional[str] = Field(None, max_length=10)  # 反馈类型(功能建议/体验问题/内容举报/其他)
    content: Optional[str] = Field(None, max_length=200)  # 反馈内容(与表列宽一致)
    status: Optional[int] = Field(None, ge=0, le=1)  # 处理状态(0待处理 1已处理)
    reply: Optional[str] = Field(None, max_length=500)  # 处理回复(与表列宽一致)
    replyTime: Optional[str] = None  # 回复时间('yyyy-MM-dd HH:mm:ss' 字符串)


class AgentConfigBody(BaseModel):
    """Agent 配置更新请求体(仅允许改描述/提示词/温度/启停)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    description: Optional[str] = Field(None, max_length=500)  # 职责描述(与表列宽一致)
    prompt: Optional[str] = None  # 系统提示词(text 列, 不限长)
    temperature: Optional[float] = Field(None, ge=0, le=1)  # 采样温度(0-1)
    enabled: Optional[int] = Field(None, ge=0, le=1)  # 状态(0启用 1停用)


class AgentChatBody(BaseModel):
    """AI 助手对话请求体(SSE 流式接口)"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    conversationId: Optional[int] = None  # 会话ID(可空, 为空时新建会话)
    content: str = Field(..., min_length=1, max_length=2000)  # 用户消息(必填)