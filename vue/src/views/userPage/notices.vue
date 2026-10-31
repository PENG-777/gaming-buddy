<template>
  <div class="max-w-[900px] mx-auto px-4 py-6">
    <!-- 顶部 banner -->
    <div class="bg-warm-primary rounded-2xl p-6 text-white flex items-center gap-5 relative overflow-hidden">
      <span class="u-icon w-32 h-32 text-white/10 absolute -right-4 -top-4" v-html="ICONS.bell"></span>
      <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center flex-shrink-0">
        <span class="u-icon w-6 h-6" v-html="ICONS.bell"></span>
      </div>
      <div class="flex-1 min-w-0">
        <h1 class="text-lg font-extrabold">平台公告</h1>
        <p class="mt-1 text-sm opacity-80">平台动态、活动与服务保障更新, 第一时间在这里发布</p>
      </div>
      <span class="text-xs opacity-80 flex-shrink-0">共 {{ notices.length }} 条</span>
    </div>

    <!-- 公告列表(手风琴单开) -->
    <div class="mt-4 bg-white border border-warm-border rounded-2xl p-5">
      <EmptyState v-if="!loading && notices.length === 0" icon="bell" text="暂无公告" />
      <div v-else class="divide-y divide-warm-border">
        <div v-for="n in notices" :key="n.noticeId">
          <button
            class="w-full flex items-center gap-3 py-4 text-left"
            @click="toggle(n.noticeId)"
          >
            <span
              class="px-2 py-0.5 rounded-lg text-xs font-bold flex-shrink-0"
              :style="tagStyle(n.noticeType)"
            >{{ n.noticeType }}</span>
            <span class="flex-1 min-w-0 text-sm font-semibold text-warm-text truncate">{{ n.title }}</span>
            <span class="hidden sm:flex items-center gap-1 text-xs text-warm-sub flex-shrink-0">
              <span class="u-icon w-3.5 h-3.5" v-html="ICONS.clock"></span>{{ fmtDate(n.createTime) }}
            </span>
            <span
              class="u-icon w-4 h-4 text-warm-sub transition-transform duration-200 flex-shrink-0"
              :class="{ 'rotate-180': opened === n.noticeId }"
              v-html="ICONS.arrowDown"
            ></span>
          </button>
          <Transition name="notice">
            <div v-show="opened === n.noticeId" class="pb-4 pr-2 sm:pr-6">
              <p class="text-sm leading-6 text-warm-sub bg-warm-page rounded-xl px-4 py-3">{{ n.content }}</p>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { selectPublishedNoticeList } from '@/api/biz/notice'
import { ICONS } from './icons'
import EmptyState from './components/EmptyState.vue'

/* 公告来自后端(仅已发布, 按发布时间倒序) */
const notices = ref([])
const loading = ref(false)
onMounted(() => {
  loading.value = true
  selectPublishedNoticeList().then(res => { notices.value = res.data || [] })
    .finally(() => { loading.value = false })
})

/* 发布时间仅展示日期(yyyy-MM-dd) */
const fmtDate = (t) => (t || '').slice(0, 10)

/* 手风琴(单开模式) */
const opened = ref(null)
const toggle = (id) => { opened.value = opened.value === id ? null : id }

/* 类型标签配色(与首页快捷入口色系一致) */
const TYPE_COLORS = {
  保障: { bg: '#e4f4f2', fg: '#26a69a' },
  活动: { bg: '#fff3e8', fg: '#f07c2a' },
  上新: { bg: '#fdf3e3', fg: '#e6b422' },
  安全: { bg: '#fdeeee', fg: '#e8746b' },
}
const tagStyle = (type) => {
  const c = TYPE_COLORS[type] || { bg: '#f3f4f6', fg: '#909399' }
  return { backgroundColor: c.bg, color: c.fg }
}
</script>

<style scoped>
/* 公告展开动画(同帮助中心 FAQ) */
.notice-enter-active,
.notice-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.notice-enter-from,
.notice-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>