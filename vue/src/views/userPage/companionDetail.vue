<template>
  <div v-if="companion" class="max-w-[1200px] mx-auto px-4 py-6">
    <!-- 面包屑式返回 -->
    <div class="flex items-center gap-2 text-xs text-warm-sub mb-4">
      <button class="flex items-center gap-1 hover:text-warm-primary transition-colors" @click="router.back()">
        <span class="u-icon w-3.5 h-3.5" v-html="ICONS.arrowLeft"></span>返回
      </button>
      <span>/</span>
      <router-link to="/user/companions" class="hover:text-warm-primary transition-colors">找陪玩</router-link>
      <span>/</span>
      <span class="text-warm-text">{{ companion.name }}</span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-5 items-start">
      <!-- ==================== 左侧主内容 ==================== -->
      <div class="space-y-5 min-w-0">
        <!-- 头部信息卡 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <div class="flex items-start gap-5">
            <div class="relative flex-shrink-0">
              <BaseAvatar :name="companion.name" :image="companion.avatar" :size="88" />
              <span class="absolute -right-1 -bottom-1 w-6 h-6 rounded-full flex items-center justify-center ring-2 ring-white"
                :style="{ backgroundColor: companion.gender === 'female' ? '#e8746b' : '#5b7a99' }">
                <span class="u-icon w-3.5 h-3.5 text-white" v-html="companion.gender === 'female' ? ICONS.genderFemale : ICONS.genderMale"></span>
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h1 class="text-2xl font-extrabold text-warm-text">{{ companion.name }}</h1>
                <span v-if="companion.certified" class="flex items-center gap-1 px-2 py-0.5 rounded-md bg-warm-bg text-warm-primary text-xs font-bold">
                  <span class="u-icon w-3.5 h-3.5" v-html="ICONS.verified"></span>平台认证
                </span>
              </div>
              <p class="mt-1.5 text-sm text-warm-sub flex items-center gap-1">
                <span class="u-icon w-3.5 h-3.5" v-html="ICONS.location"></span>{{ companion.city }}
                <span class="mx-1">·</span>{{ companion.age }}岁
                <span class="mx-1">·</span>声线: {{ companion.voice }}
                <span class="mx-1">·</span>入驻于 {{ companion.joinedAt }}
              </p>
              <div class="mt-3 flex flex-wrap gap-1.5">
                <TagBadge :text="companion.rank" type="warning" />
                <TagBadge v-for="t in companion.tags" :key="t" :text="t" />
              </div>
            </div>
          </div>

          <!-- 数据统计 -->
          <div class="mt-5 pt-4 border-t border-warm-border grid grid-cols-4 gap-2 text-center">
            <div>
              <p class="flex items-center justify-center gap-1 text-lg font-extrabold text-warm-warning">
                <span class="u-icon w-4 h-4" v-html="ICONS.star"></span>{{ companion.rating }}
              </p>
              <p class="text-xs text-warm-sub mt-0.5">综合评分</p>
            </div>
            <div class="border-l border-warm-border">
              <p class="text-lg font-extrabold text-warm-text">{{ companion.orders }}</p>
              <p class="text-xs text-warm-sub mt-0.5">累计接单</p>
            </div>
            <div class="border-l border-warm-border">
              <p class="text-lg font-extrabold text-warm-text">{{ formatFans }}</p>
              <p class="text-xs text-warm-sub mt-0.5">粉丝关注</p>
            </div>
            <div class="border-l border-warm-border">
              <p class="text-lg font-extrabold text-warm-primary">¥{{ companion.price }}<span class="text-xs font-semibold text-warm-sub">起/时</span></p>
              <p class="text-xs text-warm-sub mt-0.5">服务价格</p>
            </div>
          </div>
        </div>

        <!-- 擅长游戏 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <h2 class="section-title">擅长游戏</h2>
          <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div v-for="g in companion.games" :key="g.key" class="flex items-center gap-3 bg-warm-page border border-warm-border rounded-xl px-4 py-3">
              <GameImage :game="companionStore.gameById(g.key)" size="sm"/>
              <div class="min-w-0">
                <p class="text-sm font-bold text-warm-text">{{ g.name || '综合' }}</p>
                <p class="text-xs text-warm-sub mt-0.5 truncate">{{ g.rank }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 服务包 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <h2 class="section-title">服务项目</h2>
          <div class="mt-4 space-y-3">
            <div
              v-for="s in companion.services"
              :key="s.id"
              class="service-item"
              :class="{ selected: selectedService?.id === s.id }"
              @click="selectedService = s"
            >
              <div class="w-10 h-10 rounded-lg bg-warm-bg flex items-center justify-center flex-shrink-0">
                <span class="u-icon w-5 h-5 text-warm-primary" v-html="iconOf(s.icon)"></span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-warm-text">{{ s.name }}</p>
                <p class="text-xs text-warm-sub mt-0.5">{{ s.desc }}</p>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-lg font-extrabold text-warm-primary">¥{{ s.price }}<span class="text-xs font-medium text-warm-sub">/小时</span></p>
                <button
                  class="mt-1 px-4 py-1 text-xs font-semibold text-white bg-warm-primary rounded-lg hover:bg-warm-deep active:scale-95 transition-all"
                  @click.stop="bookService(s)"
                >立即预约</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 可约时间 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <h2 class="section-title">可约时间<span class="ml-2 text-xs font-normal text-warm-sub">点击选择时段, 橙色为可预约</span></h2>
          <div class="mt-4 overflow-x-auto no-scrollbar">
            <table class="slot-table">
              <thead>
                <tr>
                  <th class="time-col">时段</th>
                  <th v-for="d in days" :key="d.dateStr" class="text-center">
                    <p class="font-bold text-warm-text">{{ d.label }}</p>
                    <p class="text-xs text-warm-sub font-normal mt-0.5">{{ d.monthDay }}</p>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in SLOT_HOURS" :key="h">
                  <td class="time-col font-semibold text-warm-sub">{{ String(h).padStart(2, '0') }}:00</td>
                  <td v-for="d in days" :key="d.dateStr" class="text-center">
                    <button
                      v-if="isSlotAvailable(d.dateStr, h)"
                      class="slot-btn"
                      :class="{ active: pickedDate === d.dateStr && pickedHour === h }"
                      @click="pickSlot(d.dateStr, h)"
                    >可约</button>
                    <span v-else class="slot-btn disabled">满</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 用户评价 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <h2 class="section-title">用户评价 ({{ allReviews.length }})</h2>
          <!-- 评分分布 + 高频标签 -->
          <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-5">
            <div class="space-y-1.5">
              <div v-for="(p, i) in ratingDist" :key="i" class="flex items-center gap-2 text-xs">
                <span class="w-8 text-warm-sub flex-shrink-0">{{ 5 - i }}星</span>
                <div class="flex-1 h-2 rounded-full bg-warm-page overflow-hidden">
                  <div class="h-full rounded-full bg-warm-primary" :style="{ width: p + '%' }"></div>
                </div>
                <span class="w-9 text-right text-warm-sub">{{ p }}%</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 content-start">
              <TagBadge v-for="t in hotTags" :key="t.name" :text="`${t.name} ${t.count}`" type="warning" />
            </div>
          </div>

          <!-- 评价列表 -->
          <div class="mt-6 divide-y divide-warm-border">
            <div v-for="r in pagedReviews" :key="r.id" class="py-4 first:pt-0">
              <div class="flex items-center gap-3">
                <BaseAvatar :name="r.user" :image="r.avatar" :size="36" />
                <div class="flex-1">
                  <p class="text-sm font-bold text-warm-text">{{ r.user }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <RatingStars :model-value="r.rating" :size="13" />
                    <span class="text-xs text-warm-sub">{{ r.time.slice(0, 10) }} · {{ r.game }}</span>
                  </div>
                </div>
              </div>
              <p class="mt-2.5 text-sm leading-6 text-warm-text">{{ r.content }}</p>
              <div v-if="r.tags?.length" class="mt-2 flex flex-wrap gap-1.5">
                <TagBadge v-for="t in r.tags" :key="t" :text="t" type="plain" />
              </div>
              <div v-if="r.reply" class="mt-2.5 bg-warm-page rounded-xl px-4 py-2.5 text-xs leading-5 text-warm-sub">
                <b class="text-warm-primary">平台回复:</b> {{ r.reply }}
              </div>
            </div>
          </div>

          <!-- 评价分页 -->
          <div v-if="allReviews.length > reviewPageSize" class="flex items-center justify-center gap-2 mt-4">
            <button
              v-for="p in reviewPageCount" :key="p"
              class="w-8 h-8 rounded-lg text-sm font-semibold transition-all"
              :class="reviewPage === p ? 'bg-warm-primary text-white' : 'bg-warm-page text-warm-sub hover:text-warm-primary'"
              @click="reviewPage = p"
            >{{ p }}</button>
          </div>
        </div>

        <!-- 相似推荐 -->
        <div class="bg-white border border-warm-border rounded-2xl p-6">
          <h2 class="section-title">相似推荐</h2>
          <div class="mt-4 flex gap-3 overflow-x-auto pb-2 no-scrollbar">
            <div
              v-for="s in similar"
              :key="s.id"
              class="flex items-center gap-3 bg-warm-page border border-warm-border rounded-xl p-3 pr-5 cursor-pointer hover:border-warm-accent transition-all flex-shrink-0"
              @click="goOther(s.id)"
            >
              <BaseAvatar :name="s.name" :image="s.avatar" :size="44" />
              <div>
                <p class="text-sm font-bold text-warm-text">{{ s.name }}</p>
                <p class="text-xs text-warm-sub mt-0.5">
                  <span class="text-warm-warning">{{ s.rating }}分</span> · ¥{{ s.price }}/小时
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== 右侧粘性操作栏 ==================== -->
      <div class="lg:sticky lg:top-20 space-y-4">
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <!-- 已选服务摘要 -->
          <div v-if="selectedService" class="flex items-center justify-between bg-warm-bg rounded-xl px-4 py-3">
            <div>
              <p class="text-sm font-bold text-warm-text">{{ selectedService.name }}</p>
              <p class="text-xs text-warm-sub mt-0.5" v-if="pickedDate">
                {{ pickedDate }} {{ String(pickedHour).padStart(2, '0') }}:00 起
              </p>
              <p class="text-xs text-warm-sub mt-0.5" v-else>请在下方时间表选择时段</p>
            </div>
            <p class="text-xl font-extrabold text-warm-primary">¥{{ selectedService.price }}</p>
          </div>

          <button
            class="w-full mt-4 h-12 text-sm font-bold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.98] transition-all flex items-center justify-center gap-2"
            @click="doBooking"
          >
            <span class="u-icon w-4 h-4" v-html="ICONS.calendar"></span>
            立即预约
          </button>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <button
              class="h-10 text-sm font-semibold rounded-xl border transition-all active:scale-95 flex items-center justify-center gap-1.5"
              :class="isFollowed ? 'border-warm-primary text-warm-primary bg-warm-bg' : 'border-warm-border text-warm-sub hover:text-warm-primary hover:border-warm-primary'"
              @click="toggleFollow"
            >
              <span class="u-icon w-4 h-4" v-html="isFollowed ? ICONS.check : ICONS.plus"></span>
              {{ isFollowed ? '已关注' : '关注' }}
            </button>
            <button
              class="h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-primary hover:border-warm-primary transition-all active:scale-95 flex items-center justify-center gap-1.5"
              @click="goChat"
            >
              <span class="u-icon w-4 h-4" v-html="ICONS.chat"></span>聊一聊
            </button>
          </div>
          <button
            class="w-full mt-3 h-10 text-sm font-semibold text-warm-primary bg-warm-bg rounded-xl hover:bg-[#ffe9d6] transition-all active:scale-[0.98] flex items-center justify-center gap-2"
            @click="giftOpen = true"
          >
            <span class="u-icon w-4 h-4" v-html="ICONS.gift"></span>送礼物打赏
          </button>

          <!-- 服务保障 -->
          <div class="mt-5 pt-4 border-t border-warm-border space-y-2.5">
            <p class="flex items-center gap-2 text-xs text-warm-sub">
              <span class="u-icon w-4 h-4 text-warm-success" v-html="ICONS.shield"></span>平台担保交易, 服务不满意可退款
            </p>
            <p class="flex items-center gap-2 text-xs text-warm-sub">
              <span class="u-icon w-4 h-4 text-warm-success" v-html="ICONS.clock"></span>迟到 10 分钟无理由全额退款
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 送礼物弹窗 -->
    <div v-if="giftOpen" class="fixed inset-0 z-[2000] bg-black/40 flex items-center justify-center p-4" @click.self="giftOpen = false">
      <div class="w-[420px] max-w-full bg-white rounded-2xl p-6 modal-pop">
        <h3 class="text-base font-extrabold text-warm-text">送礼物给 {{ companion.name }}</h3>
        <p class="mt-1 text-xs text-warm-sub">当前余额 ¥{{ bizStore.balance }}, 打赏直接扣除余额</p>
        <div class="mt-4 grid grid-cols-4 gap-3">
          <button
            v-for="g in bizStore.gifts"
            :key="g.id"
            class="flex flex-col items-center gap-2 rounded-xl border py-4 transition-all"
            :class="pickedGift?.id === g.id ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
            @click="pickedGift = g"
          >
            <img v-if="g.image" :src="giftImg(g.image)" :alt="g.name" class="w-10 h-10 object-contain rounded-lg"/>
            <span v-else class="u-icon w-7 h-7 text-warm-accent" v-html="ICONS.gift"></span>
            <span class="text-xs font-bold text-warm-text">{{ g.name }}</span>
            <span class="text-xs font-bold text-warm-primary">¥{{ g.price }}</span>
          </button>
        </div>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="giftOpen = false">取消</button>
          <button
            class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!pickedGift"
            @click="confirmGift"
          >确认打赏</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 加载中 -->
  <div v-else-if="!companionStore.loaded" class="max-w-[1200px] mx-auto px-4 py-6">
    <EmptyState icon="clock" text="正在加载陪玩师信息..." class="bg-white border border-warm-border rounded-2xl" />
  </div>

  <!-- 不存在兜底 -->
  <div v-else class="max-w-[1200px] mx-auto px-4 py-6">
    <EmptyState icon="user" text="未找到该陪玩师, 可能已下架" action-text="去找陪玩" @action="router.push('/user/companions')" class="bg-white border border-warm-border rounded-2xl" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS, iconOf } from './icons'
import { SLOT_HOURS, nextDays, fmtDate } from './utils'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage } from '@/utils/toast.js'
import { selectCompanionReviews } from '@/api/biz/review.js'
import { selectOccupiedSlotsBatch } from '@/api/biz/order.js'
import BaseAvatar from './components/BaseAvatar.vue'
import GameImage from './components/GameImage.vue'
import TagBadge from './components/TagBadge.vue'
import RatingStars from './components/RatingStars.vue'
import EmptyState from './components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()

/* 陪玩师详情来自后端(loadAll 幂等, 数据到位后 computed 自动刷新); 礼物/评价/时段同步拉取 */
onMounted(() => { companionStore.loadAll(); bizStore.loadGifts(); loadReviews(); loadOccupied() })

/* ---- 真实评价(后端 companion_order 评价, 含我发出的; 新评价在前) ---- */
const reviews = ref([])
const loadReviews = () => {
  const id = Number(route.params.id)
  if (!id) return
  selectCompanionReviews(id).then(res => { reviews.value = res.data || [] }).catch(() => { /* 拦截器已提示 */ })
}

/* ---- 可约时间表(后端订单占用为准) ---- */
const occupiedMap = ref({})  // { 'yyyy-MM-dd': [已占用小时, ...] }
const loadOccupied = () => {
  const id = Number(route.params.id)
  if (!id) return
  selectOccupiedSlotsBatch(id, 7).then(res => { occupiedMap.value = res.data || {} }).catch(() => { /* 拦截器已提示 */ })
}

const companion = computed(() => companionStore.companionById(route.params.id))
const similar = computed(() => (companion.value ? companionStore.similarCompanions(companion.value) : []))
const formatFans = computed(() => {
  const n = companion.value?.fans || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : String(n)
})

/* ---- 服务选择 / 时段选择 ---- */
const selectedService = ref(null)
const days = nextDays(7)
const pickedDate = ref('')
const pickedHour = ref(0)

// 默认选中第一个服务包
watch(companion, (c) => { if (c && !selectedService.value) selectedService.value = c.services[0] }, { immediate: true })

const pickSlot = (dateStr, h) => {
  pickedDate.value = dateStr
  pickedHour.value = h
}

/** 时段是否可约: 已过时段不可约 + 该陪玩师当天已被占用时段不可约(后端订单为准) */
const isSlotAvailable = (dateStr, hour) => {
  const now = new Date()
  if (dateStr === fmtDate(now) && hour <= now.getHours()) return false
  return !(occupiedMap.value[dateStr] || []).includes(hour)
}

const bookService = (s) => {
  selectedService.value = s
  doBooking()
}

const doBooking = () => {
  if (!selectedService.value) return ElMessage.warning('请先选择服务项目')
  router.push({
    path: `/user/booking/${companion.value.id}`,
    query: {
      service: selectedService.value.id,
      date: pickedDate.value || undefined,
      hour: pickedDate.value ? pickedHour.value : undefined,
    },
  })
}

/* ---- 关注 / 聊天 ---- */
const isFollowed = computed(() => companion.value && bizStore.isFollow(companion.value.id))
const toggleFollow = async () => {
  const on = await bizStore.toggleFollow(companion.value.id)
  if (on === null) return  // 失败原因已由拦截器提示
  ElMessage.success(on ? '关注成功, 动态将第一时间通知你' : '已取消关注')
}
const goChat = () => {
  // 跳转消息页直达私聊会话(页面内由 ensureConversation 后端 get_or_create + 拉历史)
  router.push({ path: '/user/messages', query: { conv: `c_${companion.value.id}` } })
}

/* ---- 评价(后端真实数据直连, 无需前端合并) ---- */
const allReviews = computed(() => reviews.value)

/* 评分分布(按真实评价星级统计, 5星 -> 1星百分比) */
const ratingDist = computed(() => {
  const total = allReviews.value.length
  if (!total) return [0, 0, 0, 0, 0]
  const counts = [0, 0, 0, 0, 0]
  for (const r of allReviews.value) counts[5 - (r.rating || 5)] += 1
  return counts.map(c => Math.round((c / total) * 100))
})

/* 高频标签统计 */
const hotTags = computed(() => {
  const counter = {}
  for (const r of allReviews.value) r.tags?.forEach(t => { counter[t] = (counter[t] || 0) + 1 })
  return Object.entries(counter).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 6)
})

/* 评价分页 */
const reviewPage = ref(1)
const reviewPageSize = 4
const reviewPageCount = computed(() => Math.max(1, Math.ceil(allReviews.value.length / reviewPageSize)))
const pagedReviews = computed(() => allReviews.value.slice((reviewPage.value - 1) * reviewPageSize, reviewPage.value * reviewPageSize))
watch(allReviews, () => { reviewPage.value = 1 })

/* 相似推荐跳转(同一路由复用组件): 陪玩师ID变化时清空选择并重拉评价/时段 */
watch(() => route.params.id, () => {
  selectedService.value = null
  pickedDate.value = ''
  pickedHour.value = 0
  reviews.value = []
  occupiedMap.value = {}
  loadReviews()
  loadOccupied()
})

/* ---- 礼物 ---- */
const giftOpen = ref(false)
const pickedGift = ref(null)
/** 礼物图片地址: 相对路径(/profile/..)拼代理前缀, 完整 URL 原样使用 */
const giftImg = (image) => /^https?:/.test(image) ? image : import.meta.env.VITE_APP_BASE_API + image
const confirmGift = async () => {
  if (!pickedGift.value) return
  const sent = await bizStore.sendGift(companion.value.id, pickedGift.value)
  if (sent) {
    ElMessage.success(`已送出${pickedGift.value.name}, ${companion.value.name} 收到啦`)
    giftOpen.value = false
    pickedGift.value = null
  } else if (bizStore.balance < pickedGift.value.price) {
    ElMessage.error('余额不足, 请先前往钱包充值')
  }  // 其余失败原因已由拦截器提示
}

/* 跳转其他陪玩师 */
const goOther = (id) => router.push(`/user/companion/${id}`)
</script>

<style scoped>
.section-title {
  font-size: 16px;
  font-weight: 800;
  color: #1f2d3d;
}

/* 服务包条目 */
.service-item {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid #f0e4d8;
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.service-item:hover { border-color: #ff9a4d; }
.service-item.selected {
  border-color: #f07c2a;
  background: #fff3e8;
  box-shadow: 0 0 0 1px #f07c2a inset;
}

/* 时段表 */
.slot-table { border-collapse: separate; border-spacing: 0 4px; min-width: 640px; }
.slot-table th { font-size: 13px; padding: 6px 8px; }
.slot-table .time-col { text-align: left; font-size: 12px; width: 64px; padding-right: 8px; }
.slot-btn {
  width: 44px;
  height: 26px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s;
}
.slot-btn:not(.disabled) {
  background: #fff3e8;
  color: #f07c2a;
  cursor: pointer;
}
.slot-btn:not(.disabled):hover { background: #ffe9d6; }
.slot-btn.active { background: #f07c2a; color: #ffffff; }
.slot-btn.disabled {
  background: #f5f5f4;
  color: #c8c9c7;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: not-allowed;
}

/* 弹窗入场 */
.modal-pop { animation: modal-pop 0.22s cubic-bezier(0.34, 1.4, 0.64, 1); }
@keyframes modal-pop {
  from { opacity: 0; transform: scale(0.92) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { scrollbar-width: none; }
</style>