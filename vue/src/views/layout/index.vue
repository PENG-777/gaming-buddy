<template>
  <div>
    <!-- 顶部导航栏 -->
    <header class="fixed top-0 left-0 right-0 h-16 z-[1001] flex items-center px-6 bg-white/80 backdrop-blur-xl border-b border-gray-200/70 shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
      <!-- Logo -->
      <div class="flex items-center gap-3 flex-shrink-0 min-w-[200px]">
        <img :src="logo" alt="" class="w-10 h-10 rounded-xl object-contain p-1 bg-white border border-gray-200/80 shadow-[0_2px_6px_rgba(0,0,0,0.06)]">
        <span class="text-[20px] font-bold tracking-wide whitespace-nowrap text-[var(--color-primary)]">后台管理端</span>
      </div>

      <!-- 水平菜单 -->
      <div class="flex-1 min-w-0 h-full flex items-center px-5">
        <SideBar/>
      </div>

      <!-- 用户区域 -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <!-- 头像下拉 -->
        <div class="relative" ref="dropdownRef">
          <button
            class="flex items-center gap-1.5 py-1 pl-1 pr-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
            @click="dropdownOpen = !dropdownOpen"
          >
            <img :src="userStore.avatar" alt="" class="w-[34px] h-[34px] rounded-full object-cover border-2 border-white shadow-[0_0_0_1.5px_var(--color-primary-border)]">
            <span class="text-[15px] text-gray-700 max-w-[120px] truncate hidden md:inline">{{ userStore.name }}</span>
            <svg class="w-3 h-3 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': dropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>

          <!-- 下拉菜单 -->
          <Transition name="dropdown-fade">
            <div v-if="dropdownOpen" class="absolute right-0 top-full mt-2 w-52 bg-white rounded-xl border border-gray-200/70 shadow-[0_12px_32px_-8px_rgba(0,0,0,0.12),0_2px_8px_rgba(0,0,0,0.04)] py-1.5 z-50">
              <!-- 用户信息头 -->
              <div class="flex items-center gap-2.5 px-3.5 pb-2.5 mb-1 border-b border-gray-100">
                <img :src="userStore.avatar" alt="" class="w-9 h-9 rounded-full object-cover">
                <div class="min-w-0">
                  <p class="text-[15px] font-semibold text-gray-800 truncate leading-tight">{{ userStore.name }}</p>
                  <p class="text-[13px] text-gray-400 leading-tight mt-0.5">已登录</p>
                </div>
              </div>
              <router-link
                to="/profile"
                class="block mx-1.5 px-2.5 py-2 rounded-lg text-[15px] text-gray-700 hover:bg-gray-50 transition-colors duration-150"
                @click="dropdownOpen = false"
              >
                个人中心
              </router-link>
              <button
                class="block mx-1.5 w-[calc(100%-12px)] px-2.5 py-2 rounded-lg text-[15px] text-left text-gray-700 hover:bg-red-50 hover:text-red-500 transition-colors duration-150"
                @click="logout"
              >
                退出登录
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </header>

    <!-- 主体区域 -->
    <div class="flex relative top-16 min-h-[calc(100vh-64px)]">
      <LeftSidebar/>

      <!-- 主内容 -->
      <main class="flex-1 min-h-[calc(100vh-64px)] bg-[var(--color-bg-page)] transition-[margin] duration-300 ease-out" :class="{ 'ml-[220px]': hasSidebar }">
        <AppMain/>
      </main>
    </div>
  </div>
</template>

<script setup>
import logo from '@/assets/logo/logo.png'
import {computed, onMounted, onUnmounted, ref} from "vue";
import {useRoute} from "vue-router";
import useUserStore from "@/stores/modules/userStore.js";
import useRouteStore from "@/stores/modules/routeStore.js";
import {ElMessageBox} from "@/utils/toast.js";
import AppMain from "@/views/layout/components/AppMain.vue";
import SideBar from './components/Sidebar'
import LeftSidebar from './components/LeftSidebar/index.vue'

const userStore = useUserStore()
const route = useRoute()
const routeStore = useRouteStore()
const dropdownOpen = ref(false)

// 点击外部关闭下拉
const dropdownRef = ref(null)
const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const hasSidebar = computed(() => {
  const path = route.path
  const topItems = routeStore.sidebarRouters.filter(r => !r.hidden)
  let best = null
  let bestLen = 0
  for (const item of topItems) {
    const itemPath = item.path
    if (path === itemPath || path.startsWith(itemPath + '/')) {
      if (itemPath.length > bestLen) { best = item; bestLen = itemPath.length }
    }
  }
  if (!best?.children) return false
  const visible = best.children.filter(c => !c.hidden)
  return !(visible.length <= 1 && !best.alwaysShow)
})

const logout = () => {
  dropdownOpen.value = false
  ElMessageBox.confirm('确定退出系统吗?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    userStore.logOut().then(() => { location.href = '/login' })
  }).catch(() => {})
}
</script>

<style scoped>
.kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 5px;
  border: 1px solid #e5e7eb;
  background: #fff;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
  font-size: 12px;
  line-height: 1;
  color: #9ca3af;
  font-family: inherit;
}

.dropdown-fade-enter-active, .dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>