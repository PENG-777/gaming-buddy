<template>
  <div class="app-container">
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden grid grid-cols-1 lg:grid-cols-[340px_1fr]" style="height: calc(100vh - 130px); min-height: 520px">
      <!-- ==================== 左侧: 会话列表 ==================== -->
      <div class="flex flex-col border-r border-gray-200 min-w-0">
        <!-- 搜索 -->
        <div class="p-3 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 h-9">
            <svg class="w-4 h-4 text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="query.kw" placeholder="搜索用户名, 回车查询" class="flex-1 bg-transparent outline-none text-sm text-gray-800 placeholder:text-gray-400" @keyup.enter="handleQuery"/>
          </div>
        </div>

        <!-- 会话卡片(不展示未读角标, 仅按最近活跃排序) -->
        <div class="flex-1 overflow-y-auto">
          <div
            v-for="c in conversations"
            :key="c.conversationId"
            class="flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors border-l-2"
            :class="activeId === c.conversationId
              ? 'bg-[var(--color-primary-bg)]/40 border-l-[var(--color-primary)]'
              : 'border-l-transparent hover:bg-gray-50'"
            @click="openConv(c)"
          >
            <image-preview v-if="c.avatar" :src="c.avatar" :width="40" :height="40" class="rounded-full flex-shrink-0"/>
            <div v-else class="w-10 h-10 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-sm font-bold flex items-center justify-center flex-shrink-0">{{ (c.userName || '用')[0] }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <p class="text-sm font-bold text-gray-800 truncate">{{ c.userName }}</p>
                <span class="text-[11px] text-gray-400 flex-shrink-0">{{ shortTime(c.lastTime) }}</span>
              </div>
              <p class="text-xs text-gray-500 truncate mt-0.5">{{ c.lastMessage || '暂无消息' }}</p>
            </div>
          </div>
          <p v-if="!conversations.length && !loading" class="py-10 text-center text-sm text-gray-400">暂无会话</p>
        </div>

        <!-- 分页(窄栏精简: 仅上一页/页码/下一页) -->
        <div class="border-t border-gray-100 h-11 px-3 flex items-center justify-between flex-shrink-0">
          <span class="text-xs text-gray-400">共 {{ total }} 条</span>
          <div class="flex items-center gap-0.5">
            <button :disabled="query.pageNum <= 1" aria-label="上一页" @click="goPage(query.pageNum - 1)" class="w-7 h-7 flex items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 active:scale-90 transition-all disabled:opacity-30 disabled:pointer-events-none">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="text-xs text-gray-500 px-1.5 tabular-nums"><span class="font-semibold text-[var(--color-primary)]">{{ query.pageNum }}</span> / {{ totalPages }}</span>
            <button :disabled="query.pageNum >= totalPages" aria-label="下一页" @click="goPage(query.pageNum + 1)" class="w-7 h-7 flex items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 active:scale-90 transition-all disabled:opacity-30 disabled:pointer-events-none">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- ==================== 右侧: 聊天窗口 ==================== -->
      <div class="flex flex-col min-w-0">
        <template v-if="active">
          <!-- 会话头部 -->
          <div class="flex items-center gap-3 px-5 py-3 border-b border-gray-100 flex-shrink-0">
            <image-preview v-if="active.avatar" :src="active.avatar" :width="38" :height="38" class="rounded-full"/>
            <div v-else class="w-[38px] h-[38px] rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-sm font-bold flex items-center justify-center">{{ (active.userName || '用')[0] }}</div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-gray-800">{{ active.userName }}</p>
              <p class="text-xs text-gray-400 mt-0.5">最近消息: {{ active.lastTime || '-' }}</p>
            </div>
            <span class="inline-flex items-center gap-1.5 text-xs font-medium" :class="wsOpen ? 'text-green-600' : 'text-amber-500'">
              <span class="w-1.5 h-1.5 rounded-full" :class="wsOpen ? 'bg-green-500' : 'bg-amber-400'"></span>{{ wsOpen ? '实时通道在线' : '重连中...' }}
            </span>
          </div>

          <!-- 消息流(用户靠左白底, 客服靠右主题色) -->
          <div ref="msgBoxRef" class="flex-1 overflow-y-auto px-5 py-4 space-y-4 bg-gray-50/60">
            <div v-for="m in messages" :key="m.messageId" class="flex" :class="m.senderType === 1 ? 'justify-end' : 'justify-start'">
              <image-preview v-if="m.senderType === 0 && active.avatar" :src="active.avatar" :width="30" :height="30" class="rounded-full flex-shrink-0 mt-1"/>
              <div v-else-if="m.senderType === 0" class="w-[30px] h-[30px] rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0 mt-1">{{ (active.userName || '用')[0] }}</div>
              <div
                class="max-w-[65%] px-4 py-2.5 text-sm leading-6 whitespace-pre-wrap break-all shadow-sm"
                :class="m.senderType === 1
                  ? 'bg-[var(--color-primary)] text-white rounded-2xl rounded-tr-md'
                  : 'bg-white border border-gray-100 text-gray-800 rounded-2xl rounded-tl-md'"
              >
                {{ m.content }}
                <p class="text-[10px] mt-1 text-right opacity-60">{{ m.createTime || '' }}</p>
              </div>
              <div v-if="m.senderType === 1" class="w-[30px] h-[30px] rounded-full bg-gray-700 text-white flex-shrink-0 mt-1 flex items-center justify-center">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              </div>
            </div>
          </div>

          <!-- 输入区 -->
          <div class="border-t border-gray-200 p-4 flex-shrink-0 bg-white">
            <div class="flex items-end gap-3">
              <textarea
                v-model="input"
                rows="2"
                :disabled="!wsOpen"
                :placeholder="wsOpen ? '输入回复内容, Enter 发送, Shift+Enter 换行' : '实时通道重连中, 暂不能回复...'"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 transition-colors resize-none disabled:bg-gray-50 disabled:cursor-not-allowed"
                @keydown.enter.exact.prevent="send"
              ></textarea>
              <button
                :disabled="!wsOpen"
                class="h-10 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors flex items-center gap-1.5 flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="send"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>发送
              </button>
            </div>
          </div>
        </template>

        <!-- 未选择会话 -->
        <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 bg-gray-50/60">
          <div class="w-16 h-16 rounded-2xl bg-[var(--color-primary-bg)] flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          </div>
          <p class="text-sm font-medium">选择左侧会话开始回复</p>
          <p class="text-xs mt-1.5">用户咨询实时推送, 离线消息自动保留</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref, computed, watch, nextTick} from "vue";
import {listChatMessages, pageChatConversations} from "@/api/biz/chat.js";
import {connectChatWs, disconnectChatWs, sendChatWs} from "@/utils/chat-ws.js";
import {ElMessage} from "@/utils/toast.js";

/* 查询与列表状态 */
const query = ref({pageNum: 1, pageSize: 20, kw: ''})
const conversations = ref([])
const total = ref(0)
const loading = ref(false)

/* 当前会话与消息 */
const activeId = ref(null)
const messages = ref([])
const input = ref('')
const msgBoxRef = ref(null)
const wsOpen = ref(false)   // 管理端 WS 连接状态(断线禁用输入)
const active = computed(() => conversations.value.find(c => c.conversationId === activeId.value) || null)

/* 'yyyy-MM-dd HH:mm:ss' -> 'HH:mm'(会话列表用短时间) */
const shortTime = (t) => (t || '').slice(11, 16)

/* 分页查询会话列表 */
const getList = () => {
  loading.value = true
  pageChatConversations(query.value).then(res => {
    conversations.value = res.rows
    total.value = res.total
    // 列表刷新后当前选中会话可能不在本页, 保持 activeId 不变(右侧仍可回复)
  }).finally(() => { loading.value = false })
}
const handleQuery = () => { query.value.pageNum = 1; getList() }

/* 精简分页(窄栏): 仅上一页/下一页 */
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / query.value.pageSize)))
const goPage = (p) => { if (p >= 1 && p <= totalPages.value) { query.value.pageNum = p; getList() } }

/* 打开会话: 拉取历史消息 */
const openConv = (c) => {
  activeId.value = c.conversationId
  listChatMessages(c.conversationId).then(res => { messages.value = res.data || [] })
}

/* 发送回复: 走 WS, 消息由服务端广播回来统一入列(多工作台一致, 不本地先插) */
const send = () => {
  const content = input.value.trim()
  if (!content || !activeId.value) return
  if (!sendChatWs({type: 'reply', conversationId: activeId.value, content})) {
    ElMessage.warning('实时通道未连接, 请稍候再试')
    return
  }
  input.value = ''
}

/* WS 推送处理: 更新会话摘要并置顶; 新消息在当前会话时入列(广播含客服自己的回复) */
const onPush = (data) => {
  if (data.type !== 'message' || !data.conversation) return
  const conv = data.conversation
  const list = conversations.value.filter(c => c.conversationId !== conv.conversationId)
  if (list.length === conversations.value.length) total.value += 1  // 原列表无此会话 -> 新会话, 总数+1
  list.unshift(conv)  // 更新后的会话置顶
  conversations.value = list
  if (conv.conversationId === activeId.value) {
    messages.value.push(data.message)
  }
}

/* 消息变化/切换会话滚动到底部 */
watch(() => messages.value.length, () => nextTick(() => { if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight }))
watch(activeId, () => nextTick(() => { if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight }))

onMounted(() => {
  getList()  // 初始会话列表
  connectChatWs('/ws/adminChat', {
    onOpen: () => {
      const first = !wsOpen.value
      wsOpen.value = true
      getList()                                   // 首连/重连均刷新列表(补偿离线期间的新会话)
      if (!first && activeId.value) openConv({conversationId: activeId.value})  // 重连: 当前会话消息重拉补偿
    },
    onClose: () => { wsOpen.value = false },
    onMessage: onPush,
  })
})

onUnmounted(() => disconnectChatWs())  // 离开页面断开实时通道
</script>