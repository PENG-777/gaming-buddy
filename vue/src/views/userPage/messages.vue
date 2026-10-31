<template>
  <div class="max-w-[1100px] mx-auto px-4 py-6">
    <div class="bg-white border border-warm-border rounded-2xl overflow-hidden grid grid-cols-1 md:grid-cols-[300px_1fr]" style="height: calc(100vh - 140px); min-height: 520px">
      <!-- ==================== 左侧会话列表 ==================== -->
      <div class="flex flex-col border-r border-warm-border min-w-0">
        <!-- Tab -->
        <div class="flex border-b border-warm-border flex-shrink-0">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="flex-1 relative py-3.5 text-sm font-bold transition-colors"
            :class="tab === t.key ? 'text-warm-primary' : 'text-warm-sub hover:text-warm-text'"
            @click="tab = t.key"
          >
            {{ t.label }}
            <span v-if="t.badge" class="absolute top-2.5 right-4 min-w-[16px] h-4 px-1 rounded-full bg-warm-danger text-white text-[10px] font-bold flex items-center justify-center">{{ t.badge > 99 ? '99+' : t.badge }}</span>
            <span class="absolute left-1/4 right-1/4 bottom-0 h-0.5 rounded-full transition-opacity" :class="tab === t.key ? 'bg-warm-primary opacity-100' : 'opacity-0'"></span>
          </button>
        </div>

        <!-- 搜索 -->
        <div class="p-3 flex-shrink-0">
          <div class="flex items-center gap-2 bg-warm-page rounded-lg px-3 h-9">
            <span class="u-icon w-4 h-4 text-warm-sub" v-html="ICONS.search"></span>
            <input v-model="convSearch" placeholder="搜索会话" class="flex-1 bg-transparent outline-none text-xs text-warm-text placeholder:text-warm-sub" />
          </div>
        </div>

        <!-- 会话列表 -->
        <div class="flex-1 overflow-y-auto">
          <div
            v-for="c in filteredConvs"
            :key="c.id"
            class="flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors"
            :class="activeConvId === c.id ? 'bg-warm-bg' : 'hover:bg-warm-page'"
            @click="openConv(c.id)"
          >
            <div class="relative flex-shrink-0">
              <template v-if="c.type === 'service'">
                <div class="w-11 h-11 rounded-full bg-warm-primary flex items-center justify-center">
                  <span class="u-icon w-5 h-5 text-white" v-html="ICONS.customer"></span>
                </div>
              </template>
              <BaseAvatar v-else :name="convName(c)" :image="convAvatar(c)" :size="44" />
              <span v-if="c.unread" class="absolute -right-1 -top-1 min-w-[18px] h-[18px] px-1 rounded-full bg-warm-danger text-white text-[10px] font-bold flex items-center justify-center ring-2 ring-white">{{ c.unread > 99 ? '99+' : c.unread }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <p class="text-sm font-bold text-warm-text truncate">{{ convName(c) }}</p>
                <span class="text-[11px] text-warm-sub flex-shrink-0">{{ c.lastTime?.slice(11, 16) || '' }}</span>
              </div>
              <p class="text-xs text-warm-sub truncate mt-0.5">{{ lastMsg(c) }}</p>
            </div>
          </div>
          <p v-if="!filteredConvs.length" class="py-10 text-center text-xs text-warm-sub">没有找到相关会话</p>
        </div>
      </div>

      <!-- ==================== 右侧聊天区 ==================== -->
      <div class="flex flex-col min-w-0">
        <template v-if="activeConvId && activeConv">
          <!-- 对方信息头 -->
          <div class="flex items-center gap-3 px-5 py-3 border-b border-warm-border flex-shrink-0">
            <BaseAvatar v-if="activeConv.type === 'companion'" :name="convName(activeConv)" :image="convAvatar(activeConv)" :size="38" />
            <div v-else class="w-[38px] h-[38px] rounded-full bg-warm-primary flex items-center justify-center">
              <span class="u-icon w-4.5 h-4.5 text-white" v-html="ICONS.customer"></span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-warm-text">
                {{ convName(activeConv) }}
                <span v-if="activeConv.type === 'companion'" class="ml-1 text-xs font-medium text-warm-sub">在线</span>
                <span v-else class="ml-1.5 inline-flex items-center gap-1 text-xs font-medium" :class="bizStore.serviceOnline ? 'text-emerald-500' : 'text-warm-sub'">
                  <span class="w-1.5 h-1.5 rounded-full" :class="bizStore.serviceOnline ? 'bg-emerald-500' : 'bg-warm-sub'"></span>{{ bizStore.serviceOnline ? '在线' : '重连中' }}
                </span>
              </p>
              <p v-if="activeConv.type === 'companion' && companionById(activeConv.companionId)" class="text-xs text-warm-sub mt-0.5 truncate">
                {{ gameByKey(companionById(activeConv.companionId)?.mainGame)?.name }} · ¥{{ companionById(activeConv.companionId)?.price }}/小时
              </p>
            </div>
            <button
              v-if="activeConv.type === 'companion'"
              class="text-xs font-semibold px-3.5 py-1.5 rounded-lg bg-warm-bg text-warm-primary hover:bg-[#ffe9d6] transition-colors"
              @click="router.push(`/user/companion/${activeConv.companionId}`)"
            >去预约</button>
          </div>

          <!-- 消息流 -->
          <div ref="msgBoxRef" class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            <div v-for="m in activeConv.messages" :key="m.id" class="flex" :class="m.from === 'me' ? 'justify-end' : 'justify-start'">
              <div v-if="m.from !== 'me'" class="mr-2.5 flex-shrink-0 mt-0.5">
                <BaseAvatar v-if="activeConv.type === 'companion'" :name="convName(activeConv)" :image="convAvatar(activeConv)" :size="32" />
                <div v-else class="w-8 h-8 rounded-full bg-warm-primary flex items-center justify-center">
                  <span class="u-icon w-4 h-4 text-white" v-html="ICONS.customer"></span>
                </div>
              </div>
              <div
                class="max-w-[65%] px-4 py-2.5 text-sm leading-6"
                :class="m.from === 'me'
                  ? 'bg-warm-primary text-white rounded-2xl rounded-tr-md'
                  : 'bg-warm-page text-warm-text rounded-2xl rounded-tl-md'"
              >
                {{ m.content }}
                <p class="text-[10px] mt-1 text-right opacity-60">{{ m.time }}</p>
              </div>
            </div>
          </div>

          <!-- 输入区 -->
          <div class="border-t border-warm-border p-4 flex-shrink-0">
            <div class="flex items-end gap-3">
              <textarea
                v-model="input"
                rows="2"
                :disabled="activeConv.type === 'service' && !bizStore.serviceOnline"
                :placeholder="activeConv.type === 'service' && !bizStore.serviceOnline ? '客服连接中, 请稍候...' : '输入消息, Enter 发送, Shift+Enter 换行'"
                class="flex-1 rounded-xl border border-warm-border px-4 py-2.5 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors resize-none disabled:bg-warm-page disabled:cursor-not-allowed"
                @keydown.enter.exact.prevent="send()"
              ></textarea>
              <button
                :disabled="activeConv.type === 'service' && !bizStore.serviceOnline"
                class="px-5 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.97] transition-all flex items-center gap-1.5 flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
                @click="send()"
              >
                <span class="u-icon w-4 h-4" v-html="ICONS.send"></span>发送
              </button>
            </div>
          </div>
        </template>

        <!-- 未选择会话 -->
        <div v-else class="flex-1 flex flex-col items-center justify-center text-warm-sub">
          <div class="w-16 h-16 rounded-2xl bg-warm-bg flex items-center justify-center mb-4">
            <span class="u-icon w-8 h-8 text-warm-accent" v-html="ICONS.chat"></span>
          </div>
          <p class="text-sm">选择一个会话开始聊天</p>
          <p class="text-xs mt-1.5">与陪玩师确认档期, 沟通更高效</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from '@/utils/toast.js'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS } from './icons'
import useBizStore from '@/stores/modules/bizStore.js'
import BaseAvatar from './components/BaseAvatar.vue'

const route = useRoute()
const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()

/* 聊天对象信息来自后端(loadAll 幂等) */
onMounted(() => companionStore.loadAll())
const companionById = (id) => companionStore.companionById(id)
const gameByKey = (id) => companionStore.gameById(id)
/* 会话对方名称: 客服固定文案; 私聊优先后端会话行携带的昵称(陪玩师改名也最新), 兜底陪玩师资料 */
const convName = (c) => c.type === 'service' ? '官方客服' : (c.companionName || companionById(c.companionId)?.name || '陪玩师')
/* 会话对方真实头像: 优先后端会话行携带, 兜底陪玩师资料, 均无回退首字头像 */
const convAvatar = (c) => c.companionAvatar || companionById(c.companionId)?.avatar || ''

const tab = ref('chat') // chat 私聊 / service 官方客服
const convSearch = ref('')
const input = ref('')
const msgBoxRef = ref(null)
const activeConvId = ref('')

const tabs = computed(() => [
  { key: 'chat', label: '私聊', badge: chatUnread.value },
  { key: 'service', label: '官方客服', badge: serviceUnread.value },
])

const chatUnread = computed(() => bizStore.conversations.filter(c => c.type === 'companion').reduce((s, c) => s + (c.unread || 0), 0))
const serviceUnread = computed(() => bizStore.conversations.filter(c => c.type === 'service').reduce((s, c) => s + (c.unread || 0), 0))

/* 会话列表(按 Tab + 搜索过滤) */
const filteredConvs = computed(() => {
  let list = bizStore.sortedConversations
  if (tab.value === 'chat') list = list.filter(c => c.type === 'companion')
  if (tab.value === 'service') list = list.filter(c => c.type === 'service')
  const kw = convSearch.value.trim()
  if (kw) {
    list = list.filter(c => {
      const name = convName(c)
      return name.includes(kw) || (c.messages.at(-1)?.content || '').includes(kw)
    })
  }
  return list
})

const activeConv = computed(() => bizStore.conversations.find(c => c.id === activeConvId.value))

const lastMsg = (c) => {
  const m = c.messages.at(-1)
  if (m) return (m.from === 'me' ? '我: ' : '') + m.content
  return c.lastMessage || ''  // 私聊列表行不带消息, 预览用后端快照
}

/* 打开会话: 标记已读 + 同步到 store(实时推送未读判断用); 私聊首次打开拉取历史 */
const openConv = (id) => {
  activeConvId.value = id
  bizStore.activeConvId = id
  bizStore.markConvRead(id)
  const conv = bizStore.conversations.find(c => c.id === id)
  if (conv && conv.type === 'companion' && !conv.messages.length) {
    bizStore.ensureConversation(conv.companionId)  // 拉取全部历史(幂等, 顺带清未读)
  }
}

/* 发送消息(客服/私聊均走 WS, 连接未就绪时提示) */
const send = (preset) => {
  const content = (preset || input.value).trim()
  if (!content || !activeConvId.value) return
  if (!bizStore.sendMsg(activeConvId.value, content)) {
    ElMessage.warning('消息通道连接中, 请稍候再试')
    return
  }
  if (!preset) input.value = ''
}

/* 消息变化滚动到底部 */
watch(() => activeConv.value?.messages.length, () => {
  nextTick(() => {
    if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight
  })
})
watch(activeConvId, () => {
  nextTick(() => {
    if (msgBoxRef.value) msgBoxRef.value.scrollTop = msgBoxRef.value.scrollHeight
  })
})

/* 从 query.conv 直达指定会话 */
onMounted(() => {
  const q = route.query.conv
  if (!q) return
  if (q === 'service') {
    // 直达客服会话: 先拉最新再打开(REST 可能尚未返回, 客服会话不在本地缓存)
    bizStore.loadServiceConv().finally(() => { openConv('service'); tab.value = 'service' })
  } else if (q.startsWith('c_')) {
    // 直达私聊会话: 后端 get_or_create + 历史 + 清未读后打开
    const companionId = Number(q.slice(2))
    if (companionId) {
      tab.value = 'chat'
      bizStore.ensureConversation(companionId).then(conv => { if (conv) openConv(conv.id) })
    }
  }
})

/* 离开页面清除"正在会话"标志 */
onUnmounted(() => { bizStore.activeConvId = '' })
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { scrollbar-width: none; }
</style>