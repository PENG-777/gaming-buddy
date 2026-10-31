/**
 * AI 助手 API（SSE 流式对话 + 会话管理 + Agent 配置管理）
 *
 * 对话接口为 POST + text/event-stream(EventSource 不支持 POST),
 * 用 fetch + ReadableStream 手写 SSE 解析; 会话/配置接口走统一 axios 实例。
 */
import request from '@/utils/request'
import { getToken } from '@/utils/auth'

// ==================== SSE 流式对话 ====================

/**
 * 发起 SSE 对话流
 * @param scene 'user' 用户端助手 | 'analyst' 管理端经营分析
 * @param payload { conversationId?: number, content: string }
 * @param onEvent 事件回调: ('status'|'token'|'done'|'error'|'end', data)
 *                  status: {agent, tool, msg} 进度(工具调用/Agent 移交)
 *                  token:  {content} 增量文本(打字机)
 *                  done:   {conversationId, messageId, title} 结束
 *                  error:  {msg} 异常; end: 流关闭
 * @returns abort 中断函数(切换会话/卸载时调用)
 */
export function chatStream(scene, payload, onEvent) {
  const base = import.meta.env.VITE_APP_BASE_API || ''
  const url = base + (scene === 'analyst' ? '/agent/analysis/chat' : '/agent/chat')
  const controller = new AbortController()

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + getToken(),
      'repeatSubmit': 'false', // 流式对话自行控制发送频率
    },
    body: JSON.stringify(payload),
    signal: controller.signal,
  }).then(async (res) => {
    if (!res.ok) { // 参数/权限类业务异常(HTTP 500 + {code, msg})
      let msg = 'AI 服务连接失败'
      try {
        const body = await res.json()
        msg = body.msg || msg
      } catch (e) { /* 非 JSON 响应保持默认文案 */ }
      onEvent('error', { msg })
      onEvent('end', {})
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let sep // 按空行切分事件块(SSE 帧以空行结尾)
      while ((sep = buffer.indexOf('\n\n')) !== -1) {
        const block = buffer.slice(0, sep)
        buffer = buffer.slice(sep + 2)
        let event = ''
        let data = ''
        for (const line of block.split('\n')) {
          if (line.startsWith('event: ')) event = line.slice(7).trim()
          else if (line.startsWith('data: ')) data += line.slice(6)
          // ": ping" 注释心跳行忽略
        }
        if (event && data) {
          try {
            onEvent(event, JSON.parse(data))
          } catch (e) { /* 忽略解析失败的残包 */ }
        }
      }
    }
    onEvent('end', {})
  }).catch((e) => {
    if (e.name === 'AbortError') return // 主动中断不算错误
    onEvent('error', { msg: 'AI 服务连接异常' })
    onEvent('end', {})
  })
  return () => controller.abort()
}

// ==================== 会话管理(REST) ====================

// 我的会话列表(scene: user/analyst, 按活跃时间倒序)
export function listConversations(scene) {
  return request({ url: '/agent/conversations', method: 'get', params: { scene } })
}

// 按会话查全部历史消息
export function listMessages(conversationId) {
  return request({ url: `/agent/conversations/${conversationId}/messages`, method: 'get' })
}

// 删除会话及其全部消息
export function deleteConversation(conversationId) {
  return request({ url: `/agent/conversations/${conversationId}`, method: 'delete' })
}

// ==================== Agent 配置管理(REST, 仅管理员) ====================

// 全部 Agent 配置(含近 30 天调用次数)
export function listAgentConfigs() {
  return request({ url: '/agent/config/list', method: 'get' })
}

// 更新 Agent 配置(描述/提示词/温度/启停, 下次对话生效)
export function updateAgentConfig(agentId, data) {
  return request({ url: `/agent/config/${agentId}`, method: 'put', data })
}