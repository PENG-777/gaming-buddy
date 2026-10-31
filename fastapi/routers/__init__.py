"""
路由聚合注册

新增业务模块(如 student)时: 在 routers/ 下新建模块文件, 然后只在下方 ALL_ROUTERS
列表中追加一行 import 与一项注册即可, main.py 无需改动。
"""
from routers import (auth, file, index, menu, profile, role, user, game, service_item,
                     companion, banner, wallet, coupon, order, review, complaint, gift,
                     reward, follow, notice, faq, feedback, chat, private_chat, agent)  # 项目内: 各模块路由

# 全部模块路由器(按注册顺序排列; 新增模块在此追加)
ALL_ROUTERS = [
    index.router,  # 首页(公开)
    auth.router,  # 登录/注册/登出
    user.router,  # 用户管理
    profile.router,  # 个人中心
    role.router,  # 角色管理
    menu.router,  # 菜单管理
    game.router,  # 游戏分类管理
    service_item.router, # 服务项目管理
    companion.router, # 陪玩师管理
    banner.router, # 轮播图管理
    wallet.router, # 钱包管理与流水管理
    coupon.router, # 优惠券管理
    order.router, # 订单管理
    review.router, # 评价管理
    complaint.router, # 投诉管理
    gift.router, # 礼物管理
    reward.router, # 打赏管理
    follow.router, # 关注管理
    notice.router, # 公告管理
    faq.router, # 帮助中心管理
    feedback.router, # 意见反馈管理
    chat.router, # 意见反馈管理
    private_chat.router, # 私聊消息
    agent.router, # AI助手
    file.router,  # 文件上传
]
