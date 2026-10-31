<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">
    <!-- ============ Hero: 标题 + 搜索 + Banner 轮播 ============ -->
    <section class="grid grid-cols-1 lg:grid-cols-[1fr_480px] gap-5">
      <!-- 左: 搜索区 -->
      <div class="bg-warm-bg rounded-2xl border border-warm-border p-8 flex flex-col justify-center min-h-[260px]">
        <h1 class="text-3xl font-extrabold text-warm-text leading-snug">
          找到你的<span class="text-warm-primary">专属陪玩搭子</span>
        </h1>
        <p class="mt-2 text-sm text-warm-sub">{{ heroCompanionText }} · 平台担保交易 · 不满意可退款</p>
        <!-- 搜索框 -->
        <div class="mt-6 flex">
          <div class="flex-1 flex items-center gap-2 bg-white rounded-xl border border-warm-border px-4 h-12 focus-within:border-warm-primary transition-colors">
            <span class="u-icon w-5 h-5 text-warm-sub" v-html="ICONS.search"></span>
            <input
              v-model="keyword"
              placeholder="搜索昵称 / 游戏 / 标签, 例如: 王者荣耀"
              class="flex-1 outline-none text-sm text-warm-text placeholder:text-warm-sub bg-transparent"
              @keyup.enter="doSearch"
            />
          </div>
          <button
            class="ml-3 px-7 h-12 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.97] transition-all"
            @click="doSearch"
          >搜 索</button>
        </div>
        <!-- 热门搜索 -->
        <div class="mt-4 flex items-center flex-wrap gap-2">
          <span class="text-xs text-warm-sub flex items-center gap-1">
            <span class="u-icon w-3.5 h-3.5 text-warm-accent" v-html="ICONS.fire"></span>热门:
          </span>
          <button
            v-for="w in hotWords"
            :key="w"
            class="px-2.5 py-1 text-xs bg-white border border-warm-border rounded-lg text-warm-sub hover:text-warm-primary hover:border-warm-primary transition-colors"
            @click="searchWord(w)"
          >{{ w }}</button>
        </div>
      </div>

      <!-- 右: Banner 轮播(数据来自后端, 插图优先, 图片缺失时回退纯色卡片) -->
      <div v-if="banners.length" class="relative rounded-2xl overflow-hidden border border-warm-border h-[260px] group">
        <Transition name="banner-fade" mode="out-in">
          <div
            :key="curBanner.bannerId"
            class="absolute inset-0 p-8 flex flex-col justify-center"
            :class="curBanner.linkUrl ? 'cursor-pointer' : ''"
            :style="bannerImgOk[curBanner.bannerId] === false || !bannerImg ? { backgroundColor: bannerBg } : {}"
            @click="goBanner"
          >
            <!-- 插图层(主体靠右, 左侧留白供文字叠加) -->
            <img
              v-if="bannerImg && bannerImgOk[curBanner.bannerId] !== false"
              :src="bannerImg"
              alt=""
              class="absolute inset-0 w-full h-full object-cover"
              @error="bannerImgOk[curBanner.bannerId] = false"
            />
            <!-- 文字层 -->
            <div class="relative z-10 max-w-[55%] flex flex-col items-start">
              <span v-if="curBanner.tag" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-white" :style="{ color: bannerFg }">{{ curBanner.tag }}</span>
              <h3 class="mt-4 text-2xl font-extrabold text-warm-text">{{ curBanner.title }}</h3>
              <p class="mt-2 text-sm" :style="{ color: bannerFg }">{{ curBanner.subtitle }}</p>
              <span
                class="mt-5 flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-semibold text-white transition-transform group-hover:translate-x-1"
                :style="{ backgroundColor: bannerFg }"
              >{{ curBanner.linkText || '去看看' }}<span class="u-icon w-3.5 h-3.5" v-html="ICONS.arrowRight"></span></span>
            </div>
          </div>
        </Transition>
        <!-- 指示器 -->
        <div class="absolute bottom-4 right-6 flex gap-2 z-10">
          <button
            v-for="(b, i) in banners"
            :key="b.bannerId"
            class="h-2 rounded-full transition-all duration-300"
            :class="i === bannerIndex ? 'w-6 bg-warm-primary' : 'w-2 bg-white/80'"
            @click="bannerIndex = i"
          ></button>
        </div>
      </div>
    </section>

    <!-- ============ 公告条 ============ -->
    <section class="mt-4 flex items-center gap-3 bg-white border border-warm-border rounded-2xl px-5 h-11 overflow-hidden">
      <span class="flex items-center gap-1.5 text-xs font-bold text-warm-primary flex-shrink-0">
        <span class="u-icon w-4 h-4" v-html="ICONS.bell"></span>平台公告
      </span>
      <div class="flex-1 relative h-full overflow-hidden">
        <Transition name="notice-slide">
          <div :key="noticeIndex" class="absolute inset-0 flex items-center">
            <router-link to="/user/notices" class="text-xs text-warm-sub hover:text-warm-primary transition-colors truncate">
              {{ notices[noticeIndex]?.title || '暂无公告' }}
            </router-link>
          </div>
        </Transition>
      </div>
      <router-link to="/user/notices" class="text-xs text-warm-sub hover:text-warm-primary flex-shrink-0 transition-colors">更多 &gt;</router-link>
    </section>

    <!-- ============ 快捷入口 ============ -->
    <section class="mt-5 grid grid-cols-3 md:grid-cols-5 gap-3">
      <div
        v-for="e in entries"
        :key="e.label"
        class="flex flex-col items-center gap-2.5 bg-white border border-warm-border rounded-2xl py-5 cursor-pointer hover:-translate-y-0.5 hover:border-warm-accent hover:shadow-[0_6px_16px_rgba(240,124,42,0.1)] transition-all"
        @click="router.push(e.to)"
      >
        <img :src="e.img" :alt="e.label" class="w-11 h-11 object-contain" draggable="false" />
        <span class="text-xs font-semibold text-warm-text">{{ e.label }}</span>
      </div>
    </section>

    <!-- ============ 热门游戏 ============ -->
    <section class="mt-8">
      <SectionHeader icon="fire" title="热门游戏" sub="按游戏找陪玩, 快速匹配同区大神" more-text="全部游戏" more-to="/user/games" />
      <div class="mt-4 flex gap-3 overflow-x-auto pb-2 no-scrollbar">
        <div
          v-for="g in companionStore.hotGames"
          :key="g.id"
          class="flex items-center gap-3 bg-white border border-warm-border rounded-2xl pl-3 pr-5 py-3 cursor-pointer flex-shrink-0 hover:-translate-y-0.5 hover:border-warm-accent transition-all"
          @click="router.push(`/user/companions?game=${g.id}`)"
        >
          <GameImage :game="g" size="md"/>
          <div>
            <p class="text-sm font-bold text-warm-text">{{ g.name }}</p>
            <p class="text-xs text-warm-sub mt-0.5">{{ g.count }} 位陪玩师 · ¥{{ g.minPrice }}起</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 精选陪玩 ============ -->
    <section class="mt-8">
      <SectionHeader icon="star" title="精选陪玩" sub="高分好评陪玩师, 平台精选" more-text="找陪玩" more-to="/user/companions" />
      <div class="mt-4 flex gap-4 overflow-x-auto pb-2 no-scrollbar">
        <div v-for="c in companionStore.featuredCompanions" :key="c.id" class="w-[240px] flex-shrink-0">
          <CompanionCard :companion="c" />
        </div>
      </div>
    </section>

    <!-- ============ 服务玩法 ============ -->
    <section class="mt-8">
      <SectionHeader icon="sparkle" title="服务玩法" sub="多种服务类型, 总有一款适合你" />
      <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- 左图右文: 服务图片来自后端(/profile/upload/..), 无图或加载失败回退图标 -->
        <div
          v-for="s in companionStore.serviceTypes"
          :key="s.id"
          class="bg-white border border-warm-border rounded-2xl p-4 cursor-pointer hover:-translate-y-0.5 hover:border-warm-accent transition-all group flex items-center gap-3"
          @click="router.push(`/user/companions?service=${s.id}`)"
        >
          <div v-if="hasServiceImg(s)" class="w-10 h-10 rounded-lg bg-warm-bg overflow-hidden flex-shrink-0 transition-transform duration-300 group-hover:scale-105">
            <img :src="s.img" :alt="s.name" class="w-full h-full object-cover" @error="serviceImgOk[s.id] = false"/>
          </div>
          <div v-else class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ backgroundColor: s.color }">
            <span class="u-icon w-5 h-5" :style="{ color: s.ink }" v-html="iconOf(s.icon)"></span>
          </div>
          <div class="min-w-0">
            <p class="font-bold text-warm-text">{{ s.name }}</p>
            <p class="mt-1 text-xs leading-5 text-warm-sub">{{ s.desc }}</p>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { selectPublishedNoticeList } from '@/api/biz/notice'
import { selectPublishedBannerList } from '@/api/biz/banner'
import { ICONS, iconOf } from './icons'
import GameImage from './components/GameImage.vue'
import CompanionCard from './components/CompanionCard.vue'
import SectionHeader from './components/SectionHeader.vue'
import entryFindImg from '@/assets/images/entry-find.png'
import entryGamesImg from '@/assets/images/entry-games.png'
import entryCouponImg from '@/assets/images/entry-coupon.png'
import entryOrdersImg from '@/assets/images/entry-orders.png'
import entryHelpImg from '@/assets/images/entry-help.png'

const router = useRouter()
const companionStore = useCompanionStore()

/* 游戏分类/服务玩法/榜单数据来自后端(loadAll 幂等) */
onMounted(() => companionStore.loadAll())

/* ---- 搜索 ---- */
const keyword = ref('')
const hotWords = ['王者荣耀', '英雄联盟', '哄睡', '永劫无间', '上分', '原神']
const doSearch = () => router.push({ path: '/user/companions', query: { keyword: keyword.value || undefined } })
const searchWord = (w) => router.push({ path: '/user/companions', query: { keyword: w } })

/* ---- Banner 轮播(数据来自后端, 仅启用中) ---- */
const banners = ref([])
const bannerIndex = ref(0)
/* 各张插图加载状态: bannerId -> true 可用 / false 失败回退纯色 */
const bannerImgOk = ref({})
let bannerTimer = null

/* ---- 公告轮播(公告来自后端, 仅已发布) ---- */
const notices = ref([])
const noticeIndex = ref(0)
let noticeTimer = null
/* 当前轮播项及缺省回退(色值未配置时用主题色) */
const curBanner = computed(() => banners.value[bannerIndex.value])
const bannerBg = computed(() => curBanner.value?.bgColor || '#fff3e8')
const bannerFg = computed(() => curBanner.value?.fgColor || '#f07c2a')
/* 图片地址: 相对路径(/profile/..)拼代理前缀, 完整 URL 原样使用 */
const bannerImg = computed(() => {
  const img = curBanner.value?.image
  if (!img) return ''
  return /^https?:/.test(img) ? img : import.meta.env.VITE_APP_BASE_API + img
})
const goBanner = () => {
  if (curBanner.value?.linkUrl) router.push(curBanner.value.linkUrl)
}

/* Hero 文案: 平台统计接口接入前使用固定文案 */
const heroCompanionText = '认证陪玩师在线接单'

onMounted(() => {
  selectPublishedBannerList().then(res => {  // 轮播图来自后端, 刷新后索引归零防越界
    banners.value = res.data || []
    bannerIndex.value = 0
  })
  bannerTimer = setInterval(() => {  // 无数据时不切换
    if (banners.value.length) bannerIndex.value = (bannerIndex.value + 1) % banners.value.length
  }, 4000)
  selectPublishedNoticeList().then(res => {  // 加载成功且有两条以上才启动轮播
    notices.value = res.data || []
    if (notices.value.length > 1) {
      noticeTimer = setInterval(() => { noticeIndex.value = (noticeIndex.value + 1) % notices.value.length }, 3200)
    }
  })
})
onUnmounted(() => {
  clearInterval(bannerTimer)
  clearInterval(noticeTimer)
})

/* ---- 快捷入口(3D 立体图标图片, 白底与白卡片融合) ---- */
const entries = [
  { label: '找陪玩', img: entryFindImg, to: '/user/companions' },
  { label: '游戏专区', img: entryGamesImg, to: '/user/games' },
  { label: '领券中心', img: entryCouponImg, to: '/user/coupons' },
  { label: '我的订单', img: entryOrdersImg, to: '/user/orders' },
  { label: '帮助中心', img: entryHelpImg, to: '/user/help' },
]

/* ---- 服务玩法封面图(后端 image, 加载失败回退图标) ---- */
const serviceImgOk = ref({})
const hasServiceImg = (s) => !!s.img && serviceImgOk.value[s.id] !== false
</script>

<style scoped>
/* banner 切换动画 */
.banner-fade-enter-active,
.banner-fade-leave-active {
  transition: opacity 0.5s ease;
}
.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
}

/* 公告垂直滚动 */
.notice-slide-enter-active,
.notice-slide-leave-active {
  transition: all 0.4s ease;
}
.notice-slide-enter-from {
  transform: translateY(100%);
  opacity: 0;
}
.notice-slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* 隐藏横向滚动条 */
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { scrollbar-width: none; }
</style>