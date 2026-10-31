<template>
  <div class="min-h-screen flex flex-col bg-warm-page">
    <!-- 头部导航栏 — 毛玻璃 + 暖橙纯色主题(无渐变) -->
    <header class="sticky top-0 z-[1000]">
      <div class="flex items-center h-[64px] bg-white/85 backdrop-blur-xl border-b border-warm-border shadow-[0_1px_2px_rgba(31,45,61,0.04)]">
        <div class="max-w-[1200px] w-full mx-auto px-4 flex items-center h-full">
          <!-- 左侧 Logo -->
          <div class="flex items-center flex-shrink-0 pr-8">
            <div class="w-9 h-9 rounded-xl bg-warm-primary flex items-center justify-center shadow-[0_4px_10px_rgba(240,124,42,0.35)]">
              <span class="u-icon w-5 h-5 text-white" v-html="ICONS.gamepad"></span>
            </div>
            <span @click="router.push('/user/home')" class="ml-3 text-lg font-extrabold cursor-pointer text-warm-primary tracking-tight select-none">一起开黑吧</span>
          </div>

          <!-- 中间导航 -->
          <nav class="flex-1 flex items-center h-full gap-1 overflow-x-auto no-scrollbar">
            <router-link
              v-for="nav in navs"
              :key="nav.to"
              :to="nav.to"
              class="nav-link relative h-full flex items-center gap-1.5 px-4 text-sm font-semibold transition-colors duration-200 whitespace-nowrap"
              :class="isActive(nav) ? 'text-warm-primary' : 'text-warm-sub hover:text-warm-text'"
            >
              <span v-if="nav.badge" class="absolute left-[calc(100%-2px)] top-3 min-w-[16px] h-4 px-1 rounded-full bg-warm-danger text-white text-[10px] font-bold flex items-center justify-center">{{ nav.badge > 99 ? '99+' : nav.badge }}</span>
              {{ nav.label }}
            </router-link>
          </nav>

          <!-- 右侧用户区域 -->
          <div class="flex items-center flex-shrink-0 pl-4">
            <!-- 未登录 -->
            <div v-if="!userStore.name" class="flex items-center gap-3">
              <button
                @click="router.push('/login')"
                class="px-5 py-2 text-sm font-semibold text-warm-primary border border-warm-primary rounded-xl hover:bg-warm-bg active:scale-[0.97] transition-all"
              >登录</button>
              <button
                @click="router.push('/register')"
                class="px-5 py-2 text-sm font-semibold text-white rounded-xl bg-warm-primary hover:bg-warm-deep active:scale-[0.97] transition-all"
              >注册</button>
            </div>

            <!-- 已登录 -->
            <div v-else class="flex items-center">
              <div class="relative" ref="dropdownRef">
                <div
                  @click="dropdownOpen = !dropdownOpen"
                  class="flex items-center gap-2 py-1.5 px-2 rounded-xl cursor-pointer hover:bg-warm-bg transition-colors"
                >
                  <img :src="userStore.avatar" alt="" class="w-9 h-9 rounded-full object-cover ring-2 ring-warm-bg ring-offset-1">
                  <span class="text-sm font-semibold text-warm-text">{{ displayName }}</span>
                  <span
                    class="u-icon w-3.5 h-3.5 text-warm-sub transition-transform duration-200"
                    :class="{ 'rotate-180': dropdownOpen }"
                    v-html="ICONS.arrowDown"
                  ></span>
                </div>

                <Transition name="dropdown-fade">
                  <div
                    v-if="dropdownOpen"
                    class="absolute right-0 top-full mt-2 w-44 bg-white rounded-xl shadow-[0_8px_24px_rgba(31,45,61,0.12)] border border-warm-border py-1.5 z-50 overflow-hidden"
                  >
                    <button v-for="item in menuItems" :key="item.to" class="menu-item" @click="goMenu(item)">
                      <span class="u-icon w-4 h-4" v-html="iconOf(item.icon)"></span>
                      <span class="flex-1 text-left">{{ item.label }}</span>
                      <span v-if="item.badge" class="min-w-[16px] h-4 px-1 rounded-full bg-warm-danger text-white text-[10px] font-bold flex items-center justify-center">{{ item.badge > 99 ? '99+' : item.badge }}</span>
                    </button>
                    <div class="my-1.5 border-t border-warm-border"></div>
                    <button class="menu-item text-warm-danger" @click="logout">
                      <span class="u-icon w-4 h-4" v-html="iconOf('logout')"></span>
                      <span class="flex-1 text-left">退出登录</span>
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- 底部 Footer -->
    <footer class="mt-10 border-t border-warm-border bg-white">
      <div class="max-w-[1200px] mx-auto px-4 py-10">
        <div class="flex flex-col md:flex-row md:items-start gap-8 justify-between">
          <div class="max-w-xs">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-warm-primary flex items-center justify-center">
                <span class="u-icon w-4 h-4 text-white" v-html="ICONS.gamepad"></span>
              </div>
              <span class="text-base font-extrabold text-warm-primary">一起开黑吧</span>
            </div>
            <p class="mt-3 text-xs leading-6 text-warm-sub">专业的游戏陪玩预约平台, 平台担保交易, 服务不满意可退款。找陪玩, 就来一起开黑吧。</p>
          </div>
          <div class="flex gap-16">
            <div>
              <p class="text-sm font-bold text-warm-text mb-3">快捷导航</p>
              <div class="flex flex-col gap-2">
                <router-link to="/user/companions" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">找陪玩</router-link>
                <router-link to="/user/games" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">游戏专区</router-link>
              </div>
            </div>
            <div>
              <p class="text-sm font-bold text-warm-text mb-3">服务中心</p>
              <div class="flex flex-col gap-2">
                <router-link to="/user/help" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">帮助中心</router-link>
                <router-link to="/user/messages" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">在线客服</router-link>
                <router-link to="/user/coupons" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">领券中心</router-link>
              </div>
            </div>
          </div>
        </div>
        <p class="mt-8 pt-6 border-t border-warm-border text-center text-xs text-warm-sub">Copyright 2026 一起开黑吧 · 本站为演示项目, 所有陪玩师信息均为虚构演示数据</p>
      </div>
    </footer>

    <!-- 悬浮 AI 小助手(多 Agent 对话) -->
    <AiAssistant />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from '@/utils/toast.js'
import useUserStore from '@/stores/modules/userStore.js'
import useBizStore from '@/stores/modules/bizStore.js'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS, iconOf } from './icons'
import AiAssistant from './components/AiAssistant.vue'

const userStore = useUserStore()
const bizStore = useBizStore()
const companionStore = useCompanionStore()
const route = useRoute()
const router = useRouter()
const dropdownOpen = ref(false)
const dropdownRef = ref(null)

// 预取游戏/服务/陪玩师后端数据 + 我的优惠券(余额/订单/会话等由 bizStore.load 拉取)
onMounted(() => {
  bizStore.load()
  companionStore.loadAll()
  bizStore.loadCoupons()  // 优惠券(侧栏角标/下单选券共用)
  document.addEventListener('click', (e) => {
    if (dropdownRef.value && !dropdownRef.value.contains(e.target)) dropdownOpen.value = false
  })
})

// 用户端展示昵称: 即登录用户名(个人资料已落库 user 表)
const displayName = computed(() => userStore.name)

const navs = computed(() => [
  { to: '/user/home', label: '首页', exact: true },
  { to: '/user/companions', label: '找陪玩', prefix: '/user/companion' },
  { to: '/user/games', label: '游戏专区' },
  { to: '/user/messages', label: '消息', badge: bizStore.unreadTotal },
  { to: '/user/help', label: '帮助中心' },
])

const isActive = (nav) => {
  if (nav.exact) return route.path === nav.to
  if (nav.prefix) return route.path === nav.to || route.path.startsWith(nav.prefix)
  return route.path === nav.to || route.path.startsWith(nav.to + '/')
}

const menuItems = computed(() => [
  { to: '/user/profile', label: '个人中心', icon: 'user' },
  { to: '/user/orders', label: '我的订单', icon: 'order', badge: bizStore.orderCounters.ongoing },
  { to: '/user/wallet', label: '我的钱包', icon: 'wallet' },
  { to: '/user/coupons', label: '优惠券', icon: 'coupon', badge: bizStore.usableCoupons.length },
  { to: '/user/follows', label: '我的关注', icon: 'users' },
])

const goMenu = (item) => {
  dropdownOpen.value = false
  router.push(item.to)
}

const logout = () => {
  dropdownOpen.value = false
  ElMessageBox.confirm('确定注销并退出系统吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      userStore.logOut().then(() => {
        location.href = '/login'
      })
    })
    .catch(() => {})
}
</script>

<style scoped>
/* 导航链接下划线动效(纯色, 无渐变) */
.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2.5px;
  background: #f07c2a;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(-50%);
  border-radius: 2px;
}
.nav-link:hover::after { width: 65%; }
.nav-link.router-link-active::after { width: 80%; }

/* 下拉菜单项 */
.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 16px;
  font-size: 13px;
  color: #5c6670;
  transition: all 0.15s;
}
.menu-item:hover {
  background: #fff3e8;
  color: #f07c2a;
}

/* 下拉菜单动画 */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 导航横向滚动时隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { scrollbar-width: none; }
</style>