/**
 * 用户端业务状态 Store
 * 管理: 余额(后端 user.balance, loadWallet 拉取)/订单(后端 companion_order)/关注/优惠券/会话/我的评价
 * 收支明细不再本地维护, 钱包页直连接口分页拉取(wallet_transaction)
 * 会话: 私聊(陪玩师)与官方客服均走后端(private_chat + WS 实时收发/REST 历史兕底,
 *       陪玩师在管理端"私聊消息"工作台回复)
 * 资料: 昵称/性别落库 user 表(PUT /system/user/profile), 不再本地持久化
 * 持久化: 无本地缓存, 全部业务数据(余额/订单/关注/会话等)均以后端为准
 * 订单状态机(后端事务保证): pending 待支付 -> booked 待开始 -> ongoing 进行中 -> completed 已完成(可评价一次)
 *             pending/booked 可取消; 用户取消已支付订单 -> refunding(管理端确认退款后余额/优惠券原路退回)
 */
import { defineStore } from 'pinia'
import useUserStore from './userStore.js'
import { receiveCoupon, selectMyCouponList } from '@/api/biz/coupon.js'
import { getMyWallet, rechargeWallet } from '@/api/biz/wallet.js'
import { selectEnabledGiftList } from '@/api/biz/gift.js'
import { sendReward } from '@/api/biz/reward.js'
import { selectMyFollowList, toggleFollow as toggleFollowApi } from '@/api/biz/follow.js'
import {
  createOrder as createOrderApi, payOrder as payOrderApi, cancelMyOrder,
  finishOrder as finishOrderApi, reviewOrder as reviewOrderApi,
  selectMyOrder, selectMyOrderList, selectMyOrderCounters, selectMyReviews,
} from '@/api/biz/order.js'
import { insertComplaint as insertComplaintApi } from '@/api/biz/complaint.js'
import { getMyConversation, markChatRead } from '@/api/biz/chat.js'
import { getMyPrivateConversations, openCompanionConversation } from '@/api/biz/privateChat.js'
import { updateProfile as updateProfileApi } from '@/api/system/user.js'
import { connectChatWs, sendChatWs, createChatWs } from '@/utils/chat-ws.js'
import { fmtMinute, fmtDate, serviceIconOf } from '@/views/userPage/utils'

/** 新用户初始优惠券: 已对接后端, 新用户无预置券, 由 loadCoupons 拉取领取记录 */

let msgSeed = 100  // 本地临时消息 id 种子(发送方本地即时显示用, 后端消息以 messageId 为准)

/** 后端私聊会话行 -> 前端会话结构(messages 打开时拉取, 列表预览用 lastMessage) */
const mapPrivateConv = (row) => ({
  id: `c_${row.companionId}`,          // 会话 id(路由直达/列表定位统一用它)
  type: 'companion',
  companionId: row.companionId,
  companionName: row.companionName || '',
  companionAvatar: row.companionAvatar || '',
  messages: [],                        // 打开会话时由 ensureConversation 拉取
  unread: row.userUnread || 0,
  lastMessage: row.lastMessage || '',
  lastTime: (row.lastTime || '').slice(11, 16),
})

/** 后端私聊消息 -> 前端消息结构 */
const mapPrivateMsg = (m) => ({
  id: m.messageId,
  from: m.senderType === 1 ? 'other' : 'me',
  content: m.content,
  time: (m.createTime || '').slice(11, 16),
})

/** 后端订单行 -> 前端展示结构(字段名对齐原 mock, 页面零成本切换) */
const mapOrder = (row) => ({
  id: row.orderNo,                    // 订单号(路由/操作定位统一用它)
  orderNo: row.orderNo,
  companionId: row.companionId,
  companionName: row.nickName,
  avatar: row.avatar || '',
  serviceName: row.serviceName,
  serviceIcon: serviceIconOf(row.serviceName),
  serviceId: row.serviceId,
  price: row.price,
  hours: row.hours,
  date: row.serviceDate,
  startHour: row.startHour,
  note: row.note || '',
  couponId: row.userCouponId,
  couponName: row.couponName || '',
  couponAmount: row.couponAmount || 0,
  gross: row.grossAmount,
  amount: row.amount,
  payMethod: row.payMethod,
  status: row.status,
  createdAt: row.createTime || '',
  payAt: row.payTime || '',
  startAt: row.startTime || '',
  endAt: row.endTime || '',
  cancelReason: row.cancelReason || '',
  review: row.reviewRating ? {
    rating: row.reviewRating,
    tags: row.reviewTags ? row.reviewTags.split(',').filter(Boolean) : [],
    content: row.reviewContent || '',
    time: row.reviewTime || '',
    reply: row.reviewReply || '',      // 平台回复(管理端评价管理回复, 可空)
  } : null,
  complaint: row.complaintId ? {          // 订单详情接口附带的投诉信息(每单限一条)
    id: row.complaintId,
    type: row.complaintType,
    status: row.complaintStatus,          // 0 处理中 / 1 已处理
    result: row.handleResult || '',
    reply: row.complaintReply || '',
    time: row.complaintTime || '',
    handleTime: row.handleTime || '',
  } : null,
})

const useBizStore = defineStore('biz', {
  state: () => ({
    loaded: false,
    activeConvId: '',      // 消息页当前停留的会话 id(实时推送时判断未读)
    privateWs: null,       // 私聊 WS 独立实例(与客服通道并行, 断线自动重连)
    balance: 0,            // 钱包余额(loadWallet 从后端拉取, 不本地持久化)
    orders: [],            // 我的订单(loadOrders 从后端拉取, 不本地持久化)
    orderCounters: {},     // 各状态订单数量(loadCounters 从后端拉取, 供 Tab 角标/个人中心)
    follows: [],           // 关注的陪玩师 id(后端 follow, loadFollows 拉取, 不再本地持久化)
    gifts: [],             // 启用礼物(后端 gift, loadGifts 拉取, 不再本地持久化)
    coupons: [],           // 持有的优惠券(后端 user_coupon, loadCoupons 拉取, 不再本地持久化)
    conversations: [],     // 会话列表(私聊与官方客服均来自后端, 不本地持久化)
    serviceOnline: false,  // 官方客服 WS 连接状态(断线时输入禁用)
    reviews: [],           // 我发出的评价(loadReviews 从后端拉取, 不本地持久化)
  }),

  getters: {
    /** 消息未读总数(会话) */
    unreadTotal(state) {
      return state.conversations.reduce((s, c) => s + (c.unread || 0), 0)
    },
    /** 当前可用优惠券(未过期) */
    usableCoupons(state) {
      const today = fmtDate()
      return state.coupons.filter(c => c.status === 'usable' && c.expireAt >= today)
    },
    /** 消息会话(不含客服倒序) */
    sortedConversations(state) {
      return [...state.conversations].sort((a, b) => (b.lastTime > a.lastTime ? 1 : -1))
    },
  },

  actions: {
    /** 初始化加载: 全部业务数据以后端为准(布局 onMounted 调用) */
    load() {
      this.loadWallet()        // 余额以服务端为准
      this.loadFollows()       // 关注以服务端为准
      this.loadOrders()        // 订单以服务端为准(旧缓存中的订单数据不再恢复)
      this.loadCounters()      // 各状态订单计数
      this.loadReviews()       // 我的评价以服务端为准
      this.loadServiceConv()   // 官方客服会话(后端拉取)
      this.loadPrivateConvs()  // 私聊会话(后端拉取)
      this.startServiceWs()    // 官方客服 WS 实时通道(断线自动重连)
      this.startPrivateWs()    // 私聊 WS 实时通道(陪玩师回复实时推送)
      this.loaded = true
    },

    /* ---------- 资料(后端 user 表) ---------- */
    /**
     * 修改个人资料(昵称/性别落库 user 表, 后端动态更新+改名查重; "保密"不下发性别, 库中保留原值)
     * 成功后刷新 userStore(顶栏昵称/头像同步); 返回 false 表示失败(失败原因已由拦截器提示)
     */
    async updateProfile({ userName, sex }) {
      const body = {}
      if (userName != null && userName.trim()) body.userName = userName.trim()
      if (sex === 0 || sex === 1) body.sex = sex
      try {
        await updateProfileApi(body)
      } catch (e) {
        return false  // 失败原因(如"用户名已存在")已由拦截器提示
      }
      await useUserStore().getInfo()  // 落库成功刷新顶栏昵称/头像与本地快照
      return true
    },

    /* ---------- 关注(后端 follow) ---------- */
    isFollow(id) { return this.follows.includes(Number(id)) },
    /** 拉取我的关注 id 列表(以服务端为准) */
    loadFollows() {
      return selectMyFollowList().then(res => {
        this.follows = (res.data || []).map(r => Number(r.companionId))
      }).catch(() => { /* 未登录/网络异常由拦截器统一提示, 沿用上次列表 */ })
    },
    /** 关注/取关切换(后端切换, 成功后同步本地 id 列表); 返回 true 已关注 / false 已取消 / null 失败 */
    async toggleFollow(id) {
      id = Number(id)
      const followed = this.isFollow(id)
      try {
        await toggleFollowApi({ companionId: id })
      } catch (e) {
        return null  // 失败原因已由拦截器提示, 状态不变
      }
      if (followed) {
        const i = this.follows.indexOf(id)
        if (i >= 0) this.follows.splice(i, 1)
      } else {
        this.follows.unshift(id)
      }
      return !followed
    },

    /* ---------- 钱包(后端 user.balance + wallet_transaction) ---------- */
    /** 拉取钱包余额(以服务端为准) */
    async loadWallet() {
      try {
        const res = await getMyWallet()
        this.balance = res.data?.balance ?? 0
      } catch (e) { /* 未登录/网络异常由拦截器统一提示, 沿用上次余额 */ }
    },
    /** 余额充值(后端入账, 模拟支付成功); 返回 false 表示失败(原因已由拦截器提示) */
    async recharge(amount, method = 'alipay') {
      try {
        await rechargeWallet({ amount, payMethod: method })
      } catch (e) {
        return false
      }
      await this.loadWallet()
      return true
    },
    /* ---------- 打赏(后端 gift 定价 + reward 落库) ---------- */
    /** 拉取启用礼物列表(后端行 -> 前端展示结构 {id, name, image, price}) */
    loadGifts() {
      return selectEnabledGiftList().then(res => {
        this.gifts = (res.data || []).map(r => ({
          id: r.giftId,        // 礼物ID(打赏接口传它, 金额以后端定价为准)
          name: r.giftName,
          image: r.image,
          price: r.price,
        }))
      }).catch(() => { /* 未登录/网络异常由拦截器统一提示, 沿用上次列表 */ })
    },
    /** 打赏礼物(后端一次事务扣款+写流水+写打赏记录, 私聊会话内发送礼物消息); 返回 false 表示余额不足或失败 */
    async sendGift(companionId, gift) {
      if (this.balance < gift.price) return false
      try {
        await sendReward({ companionId, giftId: gift.id })
      } catch (e) {
        return false  // 失败原因已由拦截器提示
      }
      await this.loadWallet()
      // 礼物消息走私聊 WS 真实落库(陪玩师工作台可见); 通道未就绪时静默跳过(礼物已入账)
      let conv = this.conversations.find(c => c.type === 'companion' && c.companionId === Number(companionId))
      if (!conv) conv = await this.ensureConversation(companionId)
      if (conv && this.privateWs && this.privateWs.send({ type: 'chat', companionId: conv.companionId, content: `[送出礼物] ${gift.name}` })) {
        conv.messages.push({ id: ++msgSeed, from: 'me', content: `[送出礼物] ${gift.name}`, time: fmtMinute() })
        conv.lastMessage = `[送出礼物] ${gift.name}`
        conv.lastTime = fmtMinute()
      }
      return true
    },

    /* ---------- 优惠券(后端 user_coupon) ---------- */
    /** 拉取我的优惠券(后端行 -> 前端展示结构, 过期态按 expireTime 动态判定) */
    loadCoupons() {
      return selectMyCouponList().then(res => {
        const today = fmtDate()
        this.coupons = (res.data || []).map(r => ({
          id: r.id,                       // user_coupon 记录ID(下单/核销/返还均用它)
          templateId: r.couponId,         // 优惠券设置ID
          name: r.couponName,
          kind: r.threshold > 0 ? 'full' : 'free',
          amount: r.amount,
          threshold: r.threshold,
          status: r.status === 1 ? 'used'
            : (r.expireTime || '').slice(0, 10) < today ? 'expired' : 'usable',
          receivedAt: (r.receiveTime || '').slice(0, 10),
          expireAt: (r.expireTime || '').slice(0, 10),
          usedAt: (r.useTime || '').slice(0, 10),
        }))
      })
    },

    /** 领取优惠券(后端校验限领/限量, 失败提示由响应拦截器统一弹出) */
    async claimCoupon(couponId) {
      try {
        await receiveCoupon(couponId)
        await this.loadCoupons()
        return { ok: true }
      } catch (e) {
        return { ok: false }
      }
    },
    /** 下单校验用: 券是否满足订单金额门槛 */
    couponUsable(coupon, amount) {
      return coupon.status === 'usable' && coupon.expireAt >= fmtDate() && amount >= coupon.threshold
    },

    /* ---------- 订单(后端 companion_order) ---------- */
    /** 拉取我的订单(status 为空查全部; 页面 Tab 切换调用) */
    loadOrders(status = null) {
      return selectMyOrderList({ pageNum: 1, pageSize: 100, status: status || undefined })
        .then(res => { this.orders = (res.rows || []).map(mapOrder) })
        .catch(() => { /* 未登录/网络异常由拦截器统一提示, 沿用上次列表 */ })
    },

    /** 拉取各状态订单计数(供 Tab 角标/个人中心) */
    loadCounters() {
      return selectMyOrderCounters().then(res => { this.orderCounters = res.data || {} })
        .catch(() => { /* 沿用上次计数 */ })
    },

    /** 拉取我发出的评价 */
    loadReviews() {
      return selectMyReviews().then(res => { this.reviews = res.data || [] })
        .catch(() => { /* 沿用上次列表 */ })
    },

    /** 按订单号拉取我的订单详情(映射为展示结构, 订单不存在返回 null) */
    async fetchOrder(orderNo) {
      try {
        const res = await selectMyOrder(orderNo)
        return res.data ? mapOrder(res.data) : null
      } catch (e) {
        return null  // 失败原因已由拦截器统一提示
      }
    },

    /**
     * 创建订单(后端事务校验/定价, 成功返回待支付订单号)
     * payload: { companionId, serviceId, date, startHour, hours, note, userCouponId }
     */
    async createOrder(payload) {
      try {
        const res = await createOrderApi(payload)
        await Promise.all([this.loadOrders(), this.loadCounters()])
        return { ok: true, orderNo: res.orderNo }
      } catch (e) {
        return { ok: false, msg: '' }  // 失败原因已由拦截器统一提示
      }
    },

    /** 支付订单(后端事务: 余额扣款+流水+券核销; 微信/支付宝模拟支付)
     *  order 传订单行对象(含 companionId/date/startHour 供会话消息)或订单号字符串 */
    async payOrder(order, method) {
      const o = typeof order === 'string' ? this.orders.find(x => x.orderNo === order) : order
      if (!o || !o.orderNo) return { ok: false, msg: '订单不存在' }
      try {
        await payOrderApi({ orderNo: o.orderNo, payMethod: method })
      } catch (e) {
        return { ok: false, msg: '' }  // 失败原因已由拦截器统一提示
      }
      if (method === 'balance') await this.loadWallet()   // 余额以后端为准
      if (o.couponId) await this.loadCoupons()             // 券核销状态以后端为准
      await Promise.all([this.loadOrders(), this.loadCounters()])
      return { ok: true, msg: '支付成功' }
    },

    /** 取消订单(后端: 待支付直接取消; 已支付进入退款审核, 管理端确认后原路退回) */
    async cancelOrder(orderNo, reason) {
      try {
        await cancelMyOrder({ orderNo, cancelReason: reason })
      } catch (e) {
        return { ok: false, msg: '' }  // 失败原因已由拦截器统一提示
      }
      await Promise.all([this.loadOrders(), this.loadCounters()])
      return { ok: true, msg: '订单已取消' }
    },

    /** 确认完成(进行中 -> 已完成) */
    async finishOrder(orderNo) {
      try {
        await finishOrderApi(orderNo)
      } catch (e) {
        return { ok: false, msg: '' }
      }
      await this.loadOrders()
      return { ok: true, msg: '服务已完成' }
    },

    /** 提交评价(已完成订单, 仅未评价时可评) */
    async reviewOrder(orderNo, { rating, tags, content }) {
      try {
        await reviewOrderApi({ orderNo, rating, tags: tags.join(','), content })
      } catch (e) {
        return { ok: false, msg: '' }  // 失败原因已由拦截器统一提示
      }
      await Promise.all([this.loadOrders(), this.loadReviews()])
      return { ok: true, msg: '评价成功' }
    },

    /** 投诉(后端校验订单归属/状态/每单限一次, 管理端处理结果在订单详情附带返回) */
    async complain(orderNo, type, content) {
      try {
        await insertComplaintApi({ orderNo, complaintType: type, content })
      } catch (e) {
        return { ok: false, msg: '' }  // 失败原因已由拦截器提示
      }
      await this.loadOrders()
      return { ok: true, msg: '投诉已提交, 客服将尽快处理' }
    },

    /* ---------- 会话 / 消息 ---------- */
    /* ---------- 官方客服(后端 + WS 实时) ---------- */
    /** 拉取我的客服会话+历史(以后端为准, 幂等替换; 不动后端未读数, 打开会话时才清) */
    loadServiceConv() {
      return getMyConversation().then(res => {
        const { conversation, messages } = res.data || {}
        if (!conversation) return
        const conv = {
          id: 'service', type: 'service', companionId: 0,
          messages: (messages || []).map(m => ({
            id: m.messageId,
            from: m.senderType === 1 ? 'other' : 'me',
            content: m.content,
            time: (m.createTime || '').slice(11, 16),
          })),
          unread: conversation.userUnread || 0,
          lastTime: (conversation.lastTime || '').slice(11, 16),
        }
        const i = this.conversations.findIndex(c => c.id === 'service')
        if (i >= 0) this.conversations.splice(i, 1, conv)
        else this.conversations.push(conv)
      }).catch(() => { /* 未登录/网络异常由拦截器统一提示, 沿用上次会话 */ })
    },

    /** 建立/复用客服 WS 连接(客服回复实时推送; 首连/重连成功自动重拉历史补偿离线消息) */
    startServiceWs() {
      connectChatWs('/ws/chat', {
        onOpen: () => { this.serviceOnline = true; this.loadServiceConv() },
        onClose: () => { this.serviceOnline = false },
        onMessage: (data) => {
          if (data.type === 'message') this.onServiceMessage(data.message)
        },
      })
    },

    /** WS 推送处理: 客服新消息入会话(未停留在该会话时累计未读) */
    onServiceMessage(msg) {
      if (!msg || msg.senderType !== 1) return  // 我方消息本地已即时显示, 不重复处理
      let conv = this.conversations.find(c => c.id === 'service')
      if (!conv) {
        conv = { id: 'service', type: 'service', companionId: 0, messages: [], unread: 0, lastTime: '' }
        this.conversations.push(conv)
      }
      conv.messages.push({ id: msg.messageId, from: 'other', content: msg.content, time: (msg.createTime || '').slice(11, 16) })
      conv.lastTime = (msg.createTime || '').slice(11, 16)
      // 若当前未停留在客服会话, 累加未读(与私聊推送同逻辑)
      if (this.activeConvId !== 'service') conv.unread = (conv.unread || 0) + 1
    },

    /* ---------- 私聊(后端 + WS 实时, 陪玩师在管理端工作台回复) ---------- */
    /** 拉取我的私聊会话列表(以后端为准, 幂等替换私聊部分并保留客服会话) */
    loadPrivateConvs() {
      return getMyPrivateConversations().then(res => {
        const privateConvs = (res.data || []).map(mapPrivateConv)
        this.conversations = [
          ...privateConvs,
          ...this.conversations.filter(c => c.type === 'service'),
        ]
      }).catch(() => { /* 未登录/网络异常由拦截器统一提示, 沿用上次列表 */ })
    },

    /** 建立私聊 WS 连接(陪玩师回复实时推送; 重连成功自动重拉会话列表补偿离线消息) */
    startPrivateWs() {
      if (!this.privateWs) this.privateWs = createChatWs()
      this.privateWs.connect('/ws/privateChat', {
        onOpen: () => { this.loadPrivateConvs() },
        onMessage: (data) => {
          if (data.type === 'message') this.onPrivateMessage(data.conversation, data.message)
        },
      })
    },

    /** WS 推送处理: 陪玩师回复入会话(未停留在该会话时累计未读) */
    onPrivateMessage(brief, msg) {
      if (!msg || msg.senderType !== 1) return  // 我方消息本地已即时显示, 不重复处理
      const convId = `c_${brief.companionId}`
      let conv = this.conversations.find(c => c.id === convId)
      if (!conv) {
        conv = mapPrivateConv(brief)  // 列表拉取前收到的新会话, 由推送概要现场建
        this.conversations.push(conv)
      }
      conv.companionName = brief.companionName || conv.companionName
      conv.companionAvatar = brief.companionAvatar || conv.companionAvatar
      conv.lastMessage = msg.content
      conv.lastTime = (msg.createTime || '').slice(11, 16)
      conv.messages.push({ id: msg.messageId, from: 'other', content: msg.content, time: (msg.createTime || '').slice(11, 16) })
      // 若当前未停留在该会话(页面通过 activeConvId 告知), 累加未读
      if (this.activeConvId !== convId) conv.unread = (conv.unread || 0) + 1
    },

    /** 打开与某陪玩师的会话(get_or_create + 全部历史 + 清我的未读; 详情页"聊一聊"/列表打开用), 返回会话或 null */
    async ensureConversation(companionId) {
      companionId = Number(companionId)
      try {
        const res = await openCompanionConversation(companionId)
        const { conversation, messages } = res.data || {}
        if (!conversation) return null
        const conv = mapPrivateConv(conversation)
        conv.messages = (messages || []).map(mapPrivateMsg)
        const i = this.conversations.findIndex(c => c.id === conv.id)
        if (i >= 0) this.conversations.splice(i, 1, conv)
        else this.conversations.push(conv)
        return conv
      } catch (e) {
        return null  // 失败原因已由拦截器提示
      }
    },

    /** 发送消息: 官方客服/私聊均走 WS(对端实时接收), 本地立即显示我方消息。返回 false 表示通道未就绪 */
    sendMsg(convId, content) {
      const conv = this.conversations.find(c => c.id === convId)
      if (!conv || !content.trim()) return true
      if (conv.type === 'service') {
        // WS 发送, 本地立即显示我方消息(后端只推管理端, 免去回推去重)
        if (!sendChatWs({ type: 'chat', content: content.trim() })) return false
      } else {
        // 私聊 WS 发送(后端推陪玩师工作台+监管管理员), 本地立即显示
        if (!this.privateWs || !this.privateWs.send({ type: 'chat', companionId: conv.companionId, content: content.trim() })) return false
      }
      conv.messages.push({ id: ++msgSeed, from: 'me', content: content.trim(), time: fmtMinute() })
      conv.lastMessage = content.trim()
      conv.lastTime = fmtMinute()
      return true
    },

    markConvRead(convId) {
      const conv = this.conversations.find(c => c.id === convId)
      if (convId === 'service') {
        if (conv && conv.unread) conv.unread = 0
        markChatRead().catch(() => {})  // 客服未读数同步清零(后端)
        return
      }
      // 私聊: 有未读时重拉该会话(后端顺带清零未读, 并补齐离线消息)
      if (conv && conv.companionId && conv.unread) this.ensureConversation(conv.companionId)
    },
  },
})

export default useBizStore