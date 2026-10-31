<template>
  <div class="app-container h-[calc(100vh-120px)] min-h-[560px] flex gap-4">
    <!-- 左侧: 会话列表 -->
    <div class="w-[264px] flex-shrink-0 bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden">
      <div class="p-3 border-b border-gray-100">
        <button @click="newConversation" :disabled="sending"
                class="w-full h-9 rounded-lg text-sm font-medium text-white flex items-center justify-center gap-1.5 transition-colors"
                :class="sending ? 'bg-gray-300 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新建分析
        </button>
      </div>
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div v-if="conversations.length === 0" class="py-10 text-center text-sm text-gray-400">暂无分析会话</div>
        <div v-for="c in conversations" :key="c.conversationId" @click="switchConversation(c)"
             class="group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors"
             :class="c.conversationId === conversationId ? 'bg-[var(--color-primary-bg)]' : 'hover:bg-gray-50'">
          <svg class="w-4 h-4 flex-shrink-0" :class="c.conversationId === conversationId ? 'text-[var(--color-primary)]' : 'text-gray-400'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="flex-1 truncate text-sm" :class="c.conversationId === conversationId ? 'text-[var(--color-primary)] font-medium' : 'text-gray-700'">{{ c.title }}</span>
          <button @click.stop="removeConversation(c)" class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all" title="删除会话">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
          </button>
        </div>
      </div>
      <div class="p-3 border-t border-gray-100 text-[11px] text-gray-400 leading-5">
        AI 经营分析师 · 指标查询 / NL2SQL 双 Agent 模式, 数据口径与经营看板一致
      </div>
    </div>

    <!-- 右侧: 对话区 -->
    <div class="flex-1 bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden">
      <!-- 标题栏 -->
      <div class="flex items-center gap-2.5 px-5 h-[56px] border-b border-gray-100 flex-shrink-0">
        <div class="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
          <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-gray-800 leading-tight">AI 经营分析</p>
          <p class="text-[11px] text-gray-400 leading-tight">用自然语言查询经营数据, 支持 markdown 表格与经营建议</p>
        </div>
      </div>

      <!-- 消息区 -->
      <div ref="msgBoxRef" class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
        <div v-if="messages.length === 0" class="pt-8">
          <p class="text-center text-sm text-gray-500">您好, 我是经营分析师。试试下面的快捷问题:</p>
          <div class="grid grid-cols-2 gap-2.5 max-w-2xl mx-auto mt-5">
            <button v-for="q in QUICK_QUESTIONS" :key="q" @click="sendMessage(q)" :disabled="sending"
                    class="px-4 py-3 rounded-xl border border-gray-200 bg-white text-left text-[13px] text-gray-700
                           hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-bg)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {{ q }}
            </button>
          </div>
        </div>

        <template v-for="(m, i) in messages" :key="i">
          <div v-if="m.role === 'user'" class="flex justify-end">
            <div class="max-w-[75%] px-4 py-2.5 rounded-2xl rounded-tr-md text-white text-sm leading-relaxed whitespace-pre-wrap break-words bg-[var(--color-primary)]">{{ m.content }}</div>
          </div>
          <div v-else class="flex justify-start">
            <div class="max-w-[85%]">
              <!-- Agent 工具调用链(移交/工具调用逐步追加, 正文输出后自动折叠) -->
              <div v-if="m.steps && m.steps.length" class="mb-1.5 bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
                <button @click="m.showSteps = !m.showSteps"
                        class="w-full flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-gray-500 hover:text-gray-700 transition-colors">
                  <svg class="w-3 h-3 flex-shrink-0 transition-transform" :class="m.showSteps ? 'rotate-90' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                  <span>执行过程 · {{ m.steps.length }} 步</span>
                </button>
                <div v-show="m.showSteps" class="px-2.5 pb-2 pt-1.5 space-y-1 border-t border-gray-100">
                  <div v-for="(s, si) in m.steps" :key="si" class="flex items-start gap-1.5 text-[11px] leading-5">
                    <svg v-if="si === m.steps.length - 1 && !m.content" class="w-3 h-3 mt-1 animate-spin flex-shrink-0 text-gray-400" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-40"/>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                    </svg>
                    <span v-else class="w-3.5 h-3.5 mt-[3px] flex-shrink-0 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center text-[9px] font-medium leading-none">{{ si + 1 }}</span>
                    <span class="text-gray-500 break-all">{{ s.msg }}</span>
                  </div>
                </div>
              </div>
              <div v-if="m.content" class="px-4 py-3 rounded-2xl rounded-tl-md bg-gray-50 border border-gray-200 text-gray-800 text-sm leading-relaxed md-body" v-html="m.html"></div>
              <div v-else-if="!(m.steps && m.steps.length)" class="px-4 py-3.5 rounded-2xl rounded-tl-md bg-gray-50 border border-gray-200 inline-flex items-center gap-1.5">
                <span class="dot-flashing"></span><span class="dot-flashing" style="animation-delay:0.15s"></span><span class="dot-flashing" style="animation-delay:0.3s"></span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 输入区 -->
      <div class="px-5 pt-3 pb-4 border-t border-gray-100 flex-shrink-0">
        <div class="flex items-end gap-2">
          <textarea v-model="input" rows="1" @keydown.enter.exact.prevent="sendMessage()"
                    placeholder="输入经营分析问题, 例如: 近 30 天哪个游戏品类营收最高？"
                    class="flex-1 max-h-32 px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-sm text-gray-800
                           placeholder:text-gray-400 outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
          <button @click="sendMessage()" :disabled="sending || !input.trim()"
                  class="h-10 px-5 rounded-xl text-sm font-medium text-white flex items-center gap-1.5 transition-colors flex-shrink-0"
                  :class="sending || !input.trim() ? 'bg-gray-300 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
            <svg v-if="!sending" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
            {{ sending ? '分析中' : '发送' }}
          </button>
        </div>
        <p class="mt-2 text-[11px] text-gray-400 text-center">数据由 AI 从经营数据库实时查询生成, 请以各管理页面数据为准</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'
import { chatStream, listConversations, listMessages, deleteConversation } from '@/api/agent/agent.js'
import { renderMarkdown } from '@/utils/markdown.js'

const conversations = ref([])        // 会话列表
const conversationId = ref(null)     // 当前会话ID
const messages = ref([])             // 消息列表 [{role, content, html, steps, showSteps}]
const input = ref('')                // 输入框
const sending = ref(false)           // 发送中
const msgBoxRef = ref(null)          // 消息滚动容器
let abortFn = null                   // 流中断函数

// 快捷问题
const QUICK_QUESTIONS = [
  '近 7 天订单量和营收趋势如何？',
  '陪玩师业绩排行榜 TOP10',
  '投诉处理情况分析',
  '近 30 天用户增长情况',
]

onMounted(() => loadConversations())
onBeforeUnmount(() => {
  stopTyper() // 清理打字机定时器
  if (abortFn) abortFn()
})

// 加载会话列表
const loadConversations = () => {
  listConversations('analyst').then((res) => {
    conversations.value = res.data || []
  })
}

// 切换会话
const switchConversation = (c) => {
  if (sending.value || c.conversationId === conversationId.value) return
  conversationId.value = c.conversationId
  listMessages(c.conversationId).then((res) => {
    messages.value = (res.data || []).map((m) => ({
      role: m.role, content: m.content,
      html: m.role === 'assistant' ? renderMarkdown(m.content) : '',
    }))
    scrollToBottom()
  })
}

// 删除会话
const removeConversation = (c) => {
  ElMessageBox.confirm(`确定删除会话「${c.title}」吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
  }).then(() => {
    deleteConversation(c.conversationId).then(() => {
      conversations.value = conversations.value.filter((x) => x.conversationId !== c.conversationId)
      if (conversationId.value === c.conversationId) newConversation()
      ElMessage.success('删除成功')
    })
  }).catch(() => {})
}

// 新建会话(发送时后端创建)
const newConversation = () => {
  if (sending.value) return
  conversationId.value = null
  messages.value = []
}

// 发送消息(SSE 流式)
// 打字机: 后端 token 可能高速到达(deepseek-flash 生成快, 每秒上百 token),
// 到达即渲染会一帧内全部蹦出; 改为缓冲 + 匀速消费, 平滑逐字显示
// 基础速度约 28 字/秒(35ms/字), 积压时逐级加速至最高约 114 字/秒避免长回答拖音
let typerTimer = null
const TYPE_INTERVAL = 35  // ms/次

const startTyper = (reply) => {
  if (typerTimer) return
  typerTimer = setInterval(() => {
    if (!reply.buffer) {  // 缓冲消费完(或流中段暂空)停止, 下个 token 再启动
      stopTyper()
      return
    }
    const step = reply.buffer.length >= 240 ? 4 : reply.buffer.length >= 120 ? 2 : 1  // 积压逐级加速
    reply.content += reply.buffer.slice(0, step)
    reply.buffer = reply.buffer.slice(step)
    reply.html = renderMarkdown(reply.content)
    scrollToBottom()
  }, TYPE_INTERVAL)
}

const stopTyper = () => {
  if (typerTimer) { clearInterval(typerTimer); typerTimer = null }
}

const flushTyper = (reply) => {  // 流结束时立即补完剩余缓冲
  stopTyper()
  if (reply.buffer) {
    reply.content += reply.buffer
    reply.buffer = ''
    reply.html = renderMarkdown(reply.content)
  }
}

const sendMessage = (preset) => {
  const content = (preset || input.value).trim()
  if (!content || sending.value) return
  input.value = ''
  messages.value.push({ role: 'user', content })
  // reply 需为 reactive: SSE 回调/打字机闭包直接修改其字段, 普通对象会绕过
  // Proxy 的 set 拦截导致视图不更新(流式输出与进度全部失活)
  const reply = reactive({ role: 'assistant', content: '', html: '', buffer: '', steps: [], showSteps: true })
  messages.value.push(reply)
  sending.value = true
  scrollToBottom()

  abortFn = chatStream('analyst', { conversationId: conversationId.value, content }, (event, data) => {
    if (event === 'status') {
      reply.steps.push({ agent: data.agent, tool: data.tool, msg: data.msg }) // 调用链逐步追加
      scrollToBottom()
    } else if (event === 'token') {
      if (data.reset) { // supervisor 移交子 Agent, 清空前一段中间输出(调用链保留)
        reply.buffer = ''
        reply.content = ''
        reply.html = ''
      } else {
        reply.showSteps = false // 正文开始输出, 调用链自动折叠(可手动展开)
        reply.buffer = (reply.buffer || '') + data.content // 仅入缓冲, 打字机匀速消费
        startTyper(reply)
      }
    } else if (event === 'done') {
      conversationId.value = data.conversationId
      loadConversations()
    } else if (event === 'error') {
      if (!reply.content) {
        reply.content = data.msg || 'AI 服务异常, 请稍后重试'
        reply.html = `<p style="color:#e8746b">${reply.content}</p>`
      }
      ElMessage.error(data.msg || 'AI 服务异常')
    } else if (event === 'end') {
      flushTyper(reply) // 补完剩余缓冲再结束
      sending.value = false
      abortFn = null
      scrollToBottom()
    }
  })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight
  })
}
</script>

<style scoped>
/* 思考中三点闪烁 */
.dot-flashing {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: dot-flash 1s infinite ease-in-out;
}
@keyframes dot-flash {
  0%, 60%, 100% { transform: scale(1); opacity: 0.5; }
  30% { transform: scale(1.35); opacity: 1; }
}

/* AI 回复 markdown 样式 */
.md-body :deep(p) { margin: 0.35em 0; }
.md-body :deep(p:first-child) { margin-top: 0; }
.md-body :deep(p:last-child) { margin-bottom: 0; }
.md-body :deep(ul), .md-body :deep(ol) { padding-left: 1.2em; margin: 0.35em 0; }
.md-body :deep(li) { margin: 0.2em 0; }
.md-body :deep(strong) { color: var(--color-primary); }
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3), .md-body :deep(h4) {
  font-size: 1em; font-weight: 700; color: #1f2d3d; margin: 0.6em 0 0.3em;
}
.md-body :deep(table) { border-collapse: collapse; margin: 0.5em 0; width: 100%; font-size: 0.88em; }
.md-body :deep(th), .md-body :deep(td) {
  border: 1px solid #e5e7eb; padding: 5px 10px; text-align: left; word-break: break-all;
}
.md-body :deep(th) { background: #f9fafb; color: #1f2d3d; font-weight: 600; white-space: nowrap; }
.md-body :deep(tr:nth-child(even) td) { background: #fcfcfd; }
.md-body :deep(code) { background: #f3f4f6; color: #d0611c; padding: 1px 5px; border-radius: 4px; font-size: 0.86em; }
.md-body :deep(pre) { background: #1f2d3d; padding: 12px 14px; border-radius: 8px; overflow-x: auto; margin: 0.5em 0; }
.md-body :deep(pre code) { background: transparent; color: #e8ecf1; padding: 0; }
.md-body :deep(blockquote) { border-left: 3px solid var(--color-primary); padding-left: 0.8em; color: #6b7280; margin: 0.4em 0; }
.md-body :deep(a) { color: var(--color-primary); text-decoration: underline; }
</style>