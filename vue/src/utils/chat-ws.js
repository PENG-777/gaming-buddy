/**
 * WebSocket 客户端封装(官方客服 + 用户私聊实时通道, 用户端与管理端共用)
 *
 * - 地址: 协议随页面自动升级(http->ws / https->wss); 开发环境走 vite 代理
 *   (VITE_APP_BASE_API=/base 且代理已开 ws:true), 生产同域直连, 两环境统一
 * - token 经 query 参数传给后端(浏览器 WS 无法携带 Authorization 请求头)
 * - 心跳 25s 一次; 断线指数退避重连(1s 起步、30s 封顶), 首次连接与重连成功都会触发
 *   onOpen(调用方据此重拉 REST 历史, 天然覆盖离线消息补偿)
 * - 后端关闭码 4401(未登录)/4403(非管理员)不重连, 认证失败重连无意义
 * - 多通道并行: 官方客服用默认单例(connectChatWs), 用户私聊用 createChatWs()
 *   独立实例(各自心跳/重连互不干扰); disconnectChatWs 断开全部实例(登出用)
 */
import { getToken } from '@/utils/auth'

/** 构造 WS 完整地址 */
const wsUrl = (endpoint) => {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${location.host}${import.meta.env.VITE_APP_BASE_API}${endpoint}?token=${getToken() || ''}`
}

// 全部活跃实例(登出时统一断开)
const instances = []

/**
 * 创建独立 WS 客户端实例(多通道并行: 官方客服/用户私聊各持一个)
 * @returns {{connect: Function, disconnect: Function, send: Function, isOpen: Function}}
 */
export function createChatWs() {
  let socket = null          // 当前连接
  let heartbeatTimer = null  // 心跳定时器
  let reconnectTimer = null  // 重连定时器
  let retries = 0            // 连续失败次数(计算退避间隔)
  let manualClosed = false   // 主动关闭标志(主动关闭不再重连)
  let currentEndpoint = ''   // 当前端点(重连复用)
  let handlers = {}          // 回调集合 { onMessage, onOpen, onClose }

  const instance = { connect, disconnect, send, isOpen }  // 对外实例接口
  instances.push(instance)   // 登记(登出统一断开)
  return instance

  function clearTimers() {
    if (heartbeatTimer) { clearInterval(heartbeatTimer); heartbeatTimer = null }
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
  }

  /* 25s 心跳: 保持连接活跃, 便于两端及时感知断线 */
  function startHeartbeat() {
    clearInterval(heartbeatTimer)
    heartbeatTimer = setInterval(() => {
      if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: 'ping' }))
    }, 25000)
  }

  /* 建立连接(端点相同则复用, 变化则先断旧重建) */
  function open() {
    clearTimers()
    socket = new WebSocket(wsUrl(currentEndpoint))
    socket.onopen = () => {
      retries = 0
      startHeartbeat()
      handlers.onOpen && handlers.onOpen()
    }
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handlers.onMessage && handlers.onMessage(data)
      } catch (e) { /* 非 JSON 帧忽略 */ }
    }
    socket.onclose = (event) => {
      clearTimers()
      handlers.onClose && handlers.onClose()
      if (manualClosed) return                      // 主动关闭: 不重连
      if (event.code === 4401 || event.code === 4403) return  // 认证失败: 重连无意义
      const delay = Math.min(1000 * 2 ** retries, 30000)       // 指数退避: 1s, 2s, 4s ... 30s 封顶
      retries += 1
      reconnectTimer = setTimeout(open, delay)
    }
    socket.onerror = () => { /* 交给 onclose 统一处理重连 */ }
  }

  /**
   * 连接 WS(幂等: 已连接同一端点直接返回)
   * @param {string} endpoint 如 '/ws/chat'(客服用户端) / '/ws/privateChat'(私聊用户端)
   * @param {object} callbacks { onMessage, onOpen, onClose }
   */
  function connect(endpoint, callbacks = {}) {
    handlers = callbacks
    if (manualClosed || currentEndpoint !== endpoint || !socket || socket.readyState !== WebSocket.OPEN) {
      // 主动关闭后重连/端点变化/无可用连接: 断旧重建
      manualClosed = false
      currentEndpoint = endpoint
      retries = 0
      if (socket) { try { socket.close() } catch (e) { /* 忽略 */ } }
      open()
    }
  }

  /** 主动断开(登出/离开页面用), 停止心跳与重连 */
  function disconnect() {
    manualClosed = true
    clearTimers()
    if (socket) { try { socket.close() } catch (e) { /* 忽略 */ } }
    socket = null
  }

  /** 发送 JSON 帧; 连接未就绪返回 false(调用方提示或丢弃) */
  function send(data) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return false
    socket.send(JSON.stringify(data))
    return true
  }

  /** 当前是否处于已连接状态(页面据此展示在线状态/禁用输入) */
  function isOpen() {
    return !!socket && socket.readyState === WebSocket.OPEN
  }
}

// 默认实例: 官方客服通道(用户端 /ws/chat 与管理端 /ws/adminChat 共用, 单例语义与旧版一致)
const defaultWs = createChatWs()

/**
 * 连接客服 WS(幂等: 已连接同一端点直接返回)
 * @param {string} endpoint '/ws/chat'(用户端) 或 '/ws/adminChat'(管理端)
 * @param {object} callbacks { onMessage, onOpen, onClose }
 */
export const connectChatWs = defaultWs.connect

/** 发送 JSON 帧到客服通道; 连接未就绪返回 false(调用方提示或丢弃) */
export const sendChatWs = defaultWs.send

/** 客服通道是否处于已连接状态(页面据此展示在线状态/禁用输入) */
export const isChatWsOpen = defaultWs.isOpen

/** 主动断开全部通道(登出用), 停止各实例心跳与重连 */
export function disconnectChatWs() {
  instances.forEach(i => i.disconnect())
}