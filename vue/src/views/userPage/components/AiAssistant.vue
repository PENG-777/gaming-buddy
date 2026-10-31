<template>
  <!-- 悬浮球(暖橙纯色, 无渐变) -->
  <div v-if="!open" @click="toggleOpen"
       class="fixed right-6 bottom-6 z-[1200] w-14 h-14 rounded-full bg-warm-primary shadow-[0_6px_20px_rgba(240,124,42,0.45)] flex items-center justify-center cursor-pointer hover:scale-105 active:scale-95 transition-transform"
       title="AI 小助手">
    <svg class="w-7 h-7 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1.2" fill="currentColor"/>
      <circle cx="15" cy="14" r="1.2" fill="currentColor"/><path d="M12 8V5"/><circle cx="12" cy="4" r="1.4"/>
      <path d="M8 4.5 6 6M16 4.5 18 6"/>
    </svg>
  </div>

  <!-- 对话面板 -->
  <Transition name="panel-pop">
    <div v-if="open" class="fixed right-6 bottom-6 z-[1200] w-[400px] h-[600px] max-h-[calc(100vh-48px)]
                bg-white/95 backdrop-blur-xl rounded-2xl border border-warm-border shadow-[0_16px_48px_rgba(31,45,61,0.18)]
                flex flex-col overflow-hidden">
      <!-- 头部 -->
      <div class="flex items-center gap-2 px-4 h-[56px] border-b border-warm-border bg-white/80 flex-shrink-0">
        <div class="w-8 h-8 rounded-xl bg-warm-primary flex items-center justify-center">
          <svg class="w-4.5 h-4.5 w-[18px] h-[18px] text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1.2" fill="currentColor"/>
            <circle cx="15" cy="14" r="1.2" fill="currentColor"/><path d="M12 8V5"/><circle cx="12" cy="4" r="1.4"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-warm-text leading-tight">AI 小助手</p>
          <p class="text-[11px] text-warm-sub leading-tight">多 Agent 智能问答 · 秒级响应</p>
        </div>
        <!-- 会话切换下拉 -->
        <div class="relative" ref="convDropRef">
          <button @click="convDropOpen = !convDropOpen" class="w-8 h-8 rounded-lg hover:bg-warm-bg flex items-center justify-center text-warm-sub transition-colors" title="历史会话">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </button>
          <div v-if="convDropOpen" class="absolute right-0 top-full mt-1 w-56 max-h-64 overflow-y-auto bg-white rounded-xl border border-warm-border shadow-lg py-1 z-10">
            <div v-if="conversations.length === 0" class="px-3 py-2 text-xs text-warm-sub">暂无历史会话</div>
            <button v-for="c in conversations" :key="c.conversationId" @click="switchConversation(c)"
                    class="w-full flex items-center gap-2 px-3 py-2 hover:bg-warm-bg transition-colors text-left">
              <span class="flex-1 truncate text-xs" :class="c.conversationId === conversationId ? 'text-warm-primary font-bold' : 'text-warm-text'">{{ c.title }}</span>
              <span @click.stop="removeConversation(c)" class="text-warm-sub hover:text-warm-danger flex-shrink-0" title="删除">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
              </span>
            </button>
          </div>
        </div>
        <button @click="newConversation" class="w-8 h-8 rounded-lg hover:bg-warm-bg flex items-center justify-center text-warm-sub transition-colors" title="新对话">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
        <button @click="open = false" class="w-8 h-8 rounded-lg hover:bg-warm-bg flex items-center justify-center text-warm-sub transition-colors" title="收起">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </button>
      </div>

      <!-- 消息区 -->
      <div ref="msgBoxRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <!-- 欢迎卡片 + 建议问题 -->
        <div v-if="messages.length === 0" class="pt-6">
          <div class="w-12 h-12 mx-auto rounded-2xl bg-warm-bg flex items-center justify-center">
            <svg class="w-6 h-6 text-warm-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1.2" fill="currentColor"/>
              <circle cx="15" cy="14" r="1.2" fill="currentColor"/><path d="M12 8V5"/><circle cx="12" cy="4" r="1.4"/>
            </svg>
          </div>
          <p class="text-center text-sm font-bold text-warm-text mt-3">你好, 我是 AI 小助手</p>
          <p class="text-center text-xs text-warm-sub mt-1">推荐陪玩 · 查订单券包 · 平台规则问答</p>
          <div class="grid grid-cols-1 gap-2 mt-4">
            <button v-for="q in SUGGESTIONS" :key="q" @click="sendMessage(q)"
                    class="px-3 py-2.5 rounded-xl border border-warm-border bg-white text-left text-xs text-warm-text hover:border-warm-primary hover:text-warm-primary hover:bg-warm-bg transition-colors">
              {{ q }}
            </button>
          </div>
        </div>

        <template v-for="(m, i) in messages" :key="i">
          <!-- 用户气泡 -->
          <div v-if="m.role === 'user'" class="flex justify-end">
            <div class="max-w-[80%] px-3.5 py-2.5 rounded-2xl rounded-tr-md bg-warm-primary text-white text-sm leading-relaxed whitespace-pre-wrap break-words">{{ m.content }}</div>
          </div>
          <!-- 助手气泡(含工具调用链) -->
          <div v-else class="flex justify-start">
            <div class="max-w-[86%]">
              <!-- Agent 工具调用链(移交/工具调用逐步追加, 正文输出后自动折叠) -->
              <div v-if="m.steps && m.steps.length" class="mb-1.5 bg-warm-bg border border-warm-border rounded-lg overflow-hidden">
                <button @click="m.showSteps = !m.showSteps"
                        class="w-full flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-warm-sub hover:text-warm-text transition-colors">
                  <svg class="w-3 h-3 flex-shrink-0 transition-transform" :class="m.showSteps ? 'rotate-90' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                  <span class="truncate">执行过程 · {{ m.steps.length }} 步</span>
                </button>
                <div v-show="m.showSteps" class="px-2.5 pb-2 pt-1.5 space-y-1 border-t border-warm-border/60">
                  <div v-for="(s, si) in m.steps" :key="si" class="flex items-start gap-1.5 text-[11px] leading-5">
                    <svg v-if="si === m.steps.length - 1 && !m.content" class="w-3 h-3 mt-1 animate-spin flex-shrink-0 text-warm-sub" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-40"/>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                    </svg>
                    <span v-else class="w-3.5 h-3.5 mt-[3px] flex-shrink-0 rounded-full bg-warm-primary/15 text-warm-primary flex items-center justify-center text-[9px] font-bold leading-none">{{ si + 1 }}</span>
                    <span class="text-warm-sub break-all">{{ s.msg }}</span>
                  </div>
                </div>
              </div>
              <div v-if="m.content" class="px-3.5 py-2.5 rounded-2xl rounded-tl-md bg-warm-bg border border-warm-border text-warm-text text-sm leading-relaxed md-body" v-html="m.html"></div>
              <div v-else-if="!(m.steps && m.steps.length)" class="px-3.5 py-2.5 rounded-2xl rounded-tl-md bg-warm-bg border border-warm-border flex items-center gap-1.5">
                <span class="dot-flashing"></span><span class="dot-flashing" style="animation-delay:0.15s"></span><span class="dot-flashing" style="animation-delay:0.3s"></span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 输入区 -->
      <div class="px-4 pt-3 pb-4 border-t border-warm-border bg-white/80 flex-shrink-0">
        <div class="flex items-end gap-2">
          <textarea v-model="input" rows="1" ref="inputRef" @keydown.enter.exact.prevent="sendMessage()"
                    placeholder="问我任何问题, 例如: 帮我推荐便宜的 LOL 陪玩"
                    class="flex-1 max-h-24 px-3 py-2.5 rounded-xl border border-warm-border bg-white text-sm text-warm-text
                           placeholder:text-warm-sub/70 outline-none focus:border-warm-primary focus:ring-2 focus:ring-warm-primary/20 resize-none"></textarea>
          <button @click="sendMessage()" :disabled="sending || !input.trim()"
                  class="w-10 h-10 rounded-xl flex items-center justify-center transition-all flex-shrink-0"
                  :class="sending || !input.trim() ? 'bg-warm-bg text-warm-sub/50 cursor-not-allowed' : 'bg-warm-primary text-white hover:bg-warm-deep active:scale-95'">
            <svg v-if="!sending" class="w-4.5 h-4.5 w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          </button>
        </div>
        <p class="mt-2 text-[10px] text-warm-sub/80 text-center">内容由 AI 生成, 请以平台页面实际数据为准</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'
import useUserStore from '@/stores/modules/userStore.js'
import { chatStream, listConversations, listMessages, deleteConversation } from '@/api/agent/agent.js'
import { renderMarkdown } from '@/utils/markdown.js'

const userStore = useUserStore()
const router = useRouter()

const open = ref(false)                 // 面板开关
const convDropOpen = ref(false)         // 会话下拉开关
const convDropRef = ref(null)           // 下拉根元素(点击外部收起)
const conversations = ref([])           // 历史会话列表
const conversationId = ref(null)        // 当前会话ID
const messages = ref([])                // 消息列表 [{role, content, html, steps, showSteps}]
const input = ref('')                   // 输入框
const sending = ref(false)              // 发送中
const msgBoxRef = ref(null)             // 消息滚动容器
let abortFn = null                      // 当前流的中断函数

// 建议问题(空会话引导)
const SUGGESTIONS = [
  '帮我推荐评分高的英雄联盟陪玩师',
  '查一下我最近的订单',
  '我还有哪些优惠券可以用？',
  '下单后陪玩师迟到怎么办？',
]

// 打开/收起面板(未登录跳登录页)
const toggleOpen = () => {
  if (!userStore.name) {
    ElMessage.warning('请先登录后使用 AI 小助手')
    router.push('/login')
    return
  }
  open.value = !open.value
  if (open.value && conversations.value.length === 0) loadConversations()
}

// 加载历史会话列表
const loadConversations = () => {
  listConversations('user').then((res) => {
    conversations.value = res.data || []
  })
}

// 切换会话(拉取历史消息)
const switchConversation = (c) => {
  if (sending.value) return
  convDropOpen.value = false
  conversationId.value = c.conversationId
  listMessages(c.conversationId).then((res) => {
    messages.value = (res.data || []).map((m) => ({
      role: m.role, content: m.content,
      html: m.role === 'assistant' ? renderMarkdown(m.content) : '',
    }))
    scrollToBottom()
  })
}

// 删除会话(删除的是当前会话则同时清空消息区)
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

// 新对话(不预创建, 发送时由后端创建)
const newConversation = () => {
  if (sending.value) return
  convDropOpen.value = false
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
  if (!userStore.name) {
    ElMessage.warning('请先登录后使用 AI 小助手')
    router.push('/login')
    return
  }
  input.value = ''
  messages.value.push({ role: 'user', content })
  // reply 需为 reactive: SSE 回调/打字机闭包直接修改其字段, 普通对象会绕过
  // Proxy 的 set 拦截导致视图不更新(流式输出与进度全部失活)
  const reply = reactive({ role: 'assistant', content: '', html: '', buffer: '', steps: [], showSteps: true })
  messages.value.push(reply)
  sending.value = true
  scrollToBottom()

  abortFn = chatStream('user', { conversationId: conversationId.value, content }, (event, data) => {
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
      conversationId.value = data.conversationId // 新会话记住 ID + 更新标题
      const conv = conversations.value.find((c) => c.conversationId === data.conversationId)
      if (conv) conv.title = data.title
      else { conversations.value.unshift({ conversationId: data.conversationId, title: data.title }) }
      loadConversations()
    } else if (event === 'error') {
      if (!reply.content) { // 无内容则展示错误气泡
        reply.content = data.msg || 'AI 服务异常, 请稍后重试'
        reply.html = `<p class="text-warm-danger">${reply.content}</p>`
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

// 消息变化自动滚到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight
  })
}

// 点击面板外部收起会话下拉
const onDocClick = (e) => {
  if (convDropRef.value && !convDropRef.value.contains(e.target)) convDropOpen.value = false
}

onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => {
  document.removeEventListener('click', onDocClick)
  stopTyper() // 清理打字机定时器
  if (abortFn) abortFn() // 离开页面中断未完成的流
})
</script>

<style scoped>
/* 面板弹出动画 */
.panel-pop-enter-active, .panel-pop-leave-active {
  transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.34, 1.4, 0.64, 1);
}
.panel-pop-enter-from, .panel-pop-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}

/* 思考中三点闪烁 */
.dot-flashing {
  position: relative;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f07c2a;
  animation: dot-flash 1s infinite ease-in-out;
}
@keyframes dot-flash {
  0%, 60%, 100% { transform: scale(1); opacity: 0.5; }
  30% { transform: scale(1.35); opacity: 1; }
}

/* AI 回复 markdown 样式(气泡内) */
.md-body :deep(p) { margin: 0.35em 0; }
.md-body :deep(p:first-child) { margin-top: 0; }
.md-body :deep(p:last-child) { margin-bottom: 0; }
.md-body :deep(ul), .md-body :deep(ol) { padding-left: 1.2em; margin: 0.35em 0; }
.md-body :deep(li) { margin: 0.2em 0; }
.md-body :deep(strong) { color: #f07c2a; }
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3), .md-body :deep(h4) {
  font-size: 0.95em; font-weight: 700; color: #1f2d3d; margin: 0.6em 0 0.3em;
}
.md-body :deep(table) { border-collapse: collapse; margin: 0.5em 0; width: 100%; font-size: 0.86em; }
.md-body :deep(th), .md-body :deep(td) {
  border: 1px solid #f0d9c4; padding: 4px 8px; text-align: left; white-space: normal; word-break: break-all;
}
.md-body :deep(th) { background: #fff3e8; color: #1f2d3d; font-weight: 600; }
.md-body :deep(code) {
  background: #fff3e8; color: #d0611c; padding: 1px 5px; border-radius: 4px; font-size: 0.86em;
}
.md-body :deep(pre) { background: #1f2d3d; padding: 10px 12px; border-radius: 8px; overflow-x: auto; margin: 0.5em 0; }
.md-body :deep(pre code) { background: transparent; color: #e8ecf1; padding: 0; }
.md-body :deep(blockquote) { border-left: 3px solid #f07c2a; padding-left: 0.8em; color: #909399; margin: 0.4em 0; }
.md-body :deep(a) { color: #f07c2a; text-decoration: underline; }
</style>