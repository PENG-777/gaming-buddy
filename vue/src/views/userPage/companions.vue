<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">
    <!-- 搜索栏 -->
    <div class="bg-white border border-warm-border rounded-2xl p-4">
      <div class="flex">
        <div class="flex-1 flex items-center gap-2 bg-warm-page rounded-xl border border-warm-border px-4 h-11 focus-within:border-warm-primary transition-colors">
          <span class="u-icon w-5 h-5 text-warm-sub" v-html="ICONS.search"></span>
          <input
            v-model="filters.keyword"
            placeholder="搜索陪玩师昵称 / 段位 / 标签"
            class="flex-1 outline-none text-sm text-warm-text placeholder:text-warm-sub bg-transparent"
            @keyup.enter="resetPage"
          />
        </div>
        <button
          class="ml-3 px-6 h-11 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.97] transition-all"
          @click="resetPage"
        >搜索</button>
      </div>

      <!-- 筛选组 -->
      <div class="mt-4 space-y-2.5">
        <div v-for="group in filterGroups" :key="group.label" class="flex items-start gap-3">
          <span class="w-16 pt-1.5 text-xs font-bold text-warm-sub flex-shrink-0">{{ group.label }}</span>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="opt in group.options"
              :key="opt.value"
              class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all"
              :class="group.value === opt.value
                ? 'bg-warm-primary text-white'
                : 'bg-warm-page text-warm-sub hover:text-warm-primary'"
              @click="setFilter(group.key, opt.value)"
            >{{ opt.label }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果条: 数量 + 排序 -->
    <div class="mt-4 flex items-center justify-between">
      <p class="text-sm text-warm-sub">共找到 <b class="text-warm-primary">{{ filtered.length }}</b> 位陪玩师</p>
      <div class="flex items-center gap-1 bg-white border border-warm-border rounded-xl p-1">
        <button
          v-for="s in sortOptions"
          :key="s.value"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
          :class="sort === s.value ? 'bg-warm-bg text-warm-primary' : 'text-warm-sub hover:text-warm-primary'"
          @click="sort = s.value; resetPage()"
        >{{ s.label }}</button>
      </div>
    </div>

    <!-- 卡片网格 -->
    <div v-if="pagedList.length" class="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <CompanionCard v-for="c in pagedList" :key="c.id" :companion="c" />
    </div>
    <EmptyState
      v-else
      icon="search"
      text="没有找到符合条件的陪玩师, 换个筛选条件试试吧"
      action-text="清空筛选"
      class="bg-white border border-warm-border rounded-2xl mt-4"
      @action="clearFilters"
    />

    <!-- 分页(局部覆盖主题色为用户端暖橙) -->
    <div v-if="filtered.length" class="bg-white border border-warm-border rounded-2xl mt-4 overflow-hidden" style="--color-primary: #f07c2a">
      <Pagination v-model:page="page" v-model:limit="limit" :total="filtered.length" :page-sizes="[12, 20, 40]" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { RANK_TIERS, tierIndexOf } from './utils'
import { ICONS } from './icons'
import CompanionCard from './components/CompanionCard.vue'
import EmptyState from './components/EmptyState.vue'

const route = useRoute()
const companionStore = useCompanionStore()

/* 陪玩师/游戏/服务项目来自后端(loadAll 幂等) */
onMounted(() => companionStore.loadAll())

/* ---- 筛选状态(从 query 初始化; game/service 为后端 ID) ---- */
const filters = ref({
  keyword: route.query.keyword || '',
  game: route.query.game || '',
  gender: '',
  service: route.query.service || '',
  tier: '',
  price: '',
})

const filterGroups = computed(() => [
  {
    label: '游戏',
    key: 'game',
    value: filters.value.game,
    options: [{ label: '全部', value: '' }, ...companionStore.games.map(g => ({ label: g.name, value: String(g.id) }))],
  },
  {
    label: '性别',
    key: 'gender',
    value: filters.value.gender,
    options: [
      { label: '全部', value: '' },
      { label: '女神', value: 'female' },
      { label: '男神', value: 'male' },
    ],
  },
  {
    label: '服务',
    key: 'service',
    value: filters.value.service,
    options: [{ label: '全部', value: '' }, ...companionStore.serviceItems.map(s => ({ label: s.name, value: String(s.id) }))],
  },
  {
    label: '段位',
    key: 'tier',
    value: filters.value.tier,
    options: [{ label: '全部', value: '' }, ...RANK_TIERS.map((t, i) => ({ label: t, value: String(i) }))],
  },
  {
    label: '价格',
    key: 'price',
    value: filters.value.price,
    options: [
      { label: '全部', value: '' },
      { label: '¥20以下', value: '0-20' },
      { label: '¥20-40', value: '20-40' },
      { label: '¥40-60', value: '40-60' },
      { label: '¥60以上', value: '60-999' },
    ],
  },
])

const setFilter = (key, value) => {
  filters.value[key] = value
  resetPage()
}

/* ---- 排序 ---- */
const sort = ref('default')
const sortOptions = [
  { label: '综合排序', value: 'default' },
  { label: '价格最低', value: 'priceAsc' },
  { label: '价格最高', value: 'priceDesc' },
  { label: '评分最高', value: 'rating' },
  { label: '接单最多', value: 'orders' },
]

/* ---- 过滤(游戏/服务按后端 ID 精确匹配) ---- */
const filtered = computed(() => {
  const f = filters.value
  const kw = f.keyword.trim().toLowerCase()
  let list = companionStore.companions.filter(c => {
    if (f.game && String(c.mainGame) !== f.game && !c.games.some(g => String(g.key) === f.game)) return false
    if (f.gender && c.gender !== f.gender) return false
    if (f.service && !c.services.some(s => String(s.id) === f.service)) return false
    if (f.tier !== '' && String(tierIndexOf(c.rank)) !== f.tier) return false
    if (f.price) {
      const [min, max] = f.price.split('-').map(Number)
      if (c.price < min || c.price > max) return false
    }
    if (kw) {
      const hay = `${c.name}${c.rank}${c.mainGameName}${c.tags.join('')}${c.voice}`.toLowerCase()
      if (!hay.includes(kw)) return false
    }
    return true
  })
  switch (sort.value) {
    case 'priceAsc': list = [...list].sort((a, b) => a.price - b.price); break
    case 'priceDesc': list = [...list].sort((a, b) => b.price - a.price); break
    case 'rating': list = [...list].sort((a, b) => b.rating - a.rating); break
    case 'orders': list = [...list].sort((a, b) => b.orders - a.orders); break
    default: list = [...list].sort((a, b) => (b.rating * Math.log(b.orders + 2)) - (a.rating * Math.log(a.orders + 2)))
  }
  return list
})

/* ---- 分页 ---- */
const page = ref(1)
const limit = ref(12)
const pagedList = computed(() => filtered.value.slice((page.value - 1) * limit.value, page.value * limit.value))

const resetPage = () => { page.value = 1 }

const clearFilters = () => {
  filters.value = { keyword: '', game: '', gender: '', service: '', tier: '', price: '' }
  resetPage()
}

/* 路由 query 变化时同步筛选(如从游戏专区跳入) */
watch(() => route.query, (q) => {
  filters.value.keyword = q.keyword || ''
  filters.value.game = q.game || ''
  filters.value.service = q.service || ''
  resetPage()
})
</script>