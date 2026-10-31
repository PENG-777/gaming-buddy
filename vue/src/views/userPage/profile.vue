<template>
  <div class="max-w-[1000px] mx-auto px-4 py-6">
    <!-- 用户资料卡 -->
    <div class="bg-white border border-warm-border rounded-2xl p-6">
      <div class="flex items-center gap-5">
        <div class="relative flex-shrink-0">
          <img :src="userStore.avatar" alt="" class="w-[76px] h-[76px] rounded-full object-cover ring-4 ring-warm-bg">
          <span class="absolute -right-0.5 -bottom-0.5 w-6 h-6 rounded-full bg-warm-primary flex items-center justify-center ring-2 ring-white cursor-pointer hover:bg-warm-deep transition-colors" @click="editOpen = true">
            <span class="u-icon w-3 h-3 text-white" v-html="ICONS.edit"></span>
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2.5 flex-wrap">
            <h1 class="text-xl font-extrabold text-warm-text">{{ displayName }}</h1>
            <span class="px-2 py-0.5 rounded-md bg-warm-bg text-warm-primary text-xs font-bold">普通用户</span>
          </div>
          <p class="mt-1 text-xs text-warm-sub">
            <span v-if="userStore.sex === 0 || userStore.sex === 1">{{ userStore.sex === 1 ? '女' : '男' }} · </span>
            加入平台 {{ joinedDays }} 天
          </p>
        </div>
        <button
          class="flex-shrink-0 px-4 py-2 text-xs font-semibold text-warm-primary border border-warm-primary rounded-xl hover:bg-warm-bg active:scale-95 transition-all"
          @click="editOpen = true"
        >编辑资料</button>
      </div>

      <!-- 数据概览 -->
      <div class="mt-5 pt-4 border-t border-warm-border grid grid-cols-4 gap-2 text-center">
        <router-link to="/user/wallet" class="group py-1">
          <p class="text-lg font-extrabold text-warm-text group-hover:text-warm-primary transition-colors">¥{{ bizStore.balance }}</p>
          <p class="text-xs text-warm-sub mt-0.5">余额</p>
        </router-link>
        <router-link to="/user/coupons" class="group py-1">
          <p class="text-lg font-extrabold text-warm-text group-hover:text-warm-primary transition-colors">{{ bizStore.usableCoupons.length }}</p>
          <p class="text-xs text-warm-sub mt-0.5">优惠券</p>
        </router-link>
        <router-link to="/user/follows" class="group py-1">
          <p class="text-lg font-extrabold text-warm-text group-hover:text-warm-primary transition-colors">{{ bizStore.follows.length }}</p>
          <p class="text-xs text-warm-sub mt-0.5">关注</p>
        </router-link>
        <router-link to="/user/reviews" class="group py-1">
          <p class="text-lg font-extrabold text-warm-text group-hover:text-warm-primary transition-colors">{{ bizStore.reviews.length }}</p>
          <p class="text-xs text-warm-sub mt-0.5">评价</p>
        </router-link>
      </div>
    </div>

    <!-- 我的订单 -->
    <div class="mt-4 bg-white border border-warm-border rounded-2xl p-5">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-extrabold text-warm-text">我的订单</h2>
        <router-link to="/user/orders" class="flex items-center gap-1 text-xs font-semibold text-warm-sub hover:text-warm-primary transition-colors">
          全部订单<span class="u-icon w-3 h-3" v-html="ICONS.arrowRight"></span>
        </router-link>
      </div>
      <div class="mt-4 grid grid-cols-4 gap-2">
        <router-link
          v-for="s in orderShortcuts"
          :key="s.key"
          :to="`/user/orders?status=${s.key}`"
          class="flex flex-col items-center gap-2 py-2 rounded-xl hover:bg-warm-bg transition-colors"
        >
          <span class="relative">
            <span class="u-icon w-6 h-6 text-warm-text" v-html="iconOf(s.icon)"></span>
            <span v-if="s.count" class="absolute -right-2 -top-1.5 min-w-[16px] h-4 px-1 rounded-full bg-warm-danger text-white text-[10px] font-bold flex items-center justify-center">{{ s.count > 99 ? '99+' : s.count }}</span>
          </span>
          <span class="text-xs text-warm-sub">{{ s.label }}</span>
        </router-link>
      </div>
    </div>

    <!-- 功能宫格 -->
    <div class="mt-4 bg-white border border-warm-border rounded-2xl p-5">
      <h2 class="text-base font-extrabold text-warm-text">更多功能</h2>
      <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <router-link
          v-for="f in features"
          :key="f.label"
          :to="f.to"
          class="flex items-center gap-3 rounded-xl border border-warm-border px-4 py-3.5 hover:border-warm-accent hover:bg-warm-bg/50 transition-all"
        >
          <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ backgroundColor: f.color }">
            <span class="u-icon w-4.5 h-4.5" :style="{ color: f.ink }" v-html="iconOf(f.icon)"></span>
          </div>
          <span class="text-sm font-semibold text-warm-text">{{ f.label }}</span>
        </router-link>
        <button
          class="flex items-center gap-3 rounded-xl border border-warm-border px-4 py-3.5 hover:border-warm-accent hover:bg-warm-bg/50 transition-all text-left"
          @click="goService"
        >
          <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #eef3f8">
            <span class="u-icon w-4.5 h-4.5" style="color: #5b7a99" v-html="iconOf('customer')"></span>
          </div>
          <span class="text-sm font-semibold text-warm-text">在线客服</span>
        </button>
      </div>
    </div>

    <!-- 其他操作 -->
    <div class="mt-4 bg-white border border-warm-border rounded-2xl divide-y divide-warm-border overflow-hidden">
      <div class="flex items-center justify-between px-5 py-4">
        <div class="flex items-center gap-2.5">
          <span class="u-icon w-4 h-4 text-warm-sub" v-html="ICONS.lock"></span>
          <span class="text-sm text-warm-text">账号安全</span>
        </div>
        <router-link to="/user/self" class="text-xs text-warm-sub hover:text-warm-primary transition-colors">修改密码 / 资料 &gt;</router-link>
      </div>
      <div class="flex items-center justify-between px-5 py-4">
        <div class="flex items-center gap-2.5">
          <span class="u-icon w-4 h-4 text-warm-sub" v-html="ICONS.logout"></span>
          <span class="text-sm text-warm-text">退出登录</span>
        </div>
        <button class="text-xs text-warm-sub hover:text-warm-danger transition-colors" @click="logout">注销并退出 &gt;</button>
      </div>
    </div>

    <!-- 编辑资料弹窗 -->
    <div v-if="editOpen" class="fixed inset-0 z-[2000] bg-black/40 flex items-center justify-center p-4" @click.self="editOpen = false">
      <div class="w-[420px] max-w-full bg-white rounded-2xl p-6 modal-pop">
        <h3 class="text-base font-extrabold text-warm-text">编辑资料</h3>
        <div class="mt-5 space-y-4">
          <div>
            <p class="text-xs font-bold text-warm-sub mb-2">昵称</p>
            <input v-model="editForm.nickname" maxlength="12" placeholder="请输入昵称(即登录用户名)"
              class="w-full h-10 rounded-xl border border-warm-border px-3.5 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors" />
          </div>
          <div>
            <p class="text-xs font-bold text-warm-sub mb-2">性别</p>
            <div class="flex gap-2">
              <button
                v-for="g in [{ k: 'male', t: '男' }, { k: 'female', t: '女' }, { k: 'secret', t: '保密' }]"
                :key="g.k"
                class="flex-1 h-10 rounded-xl border text-sm font-semibold transition-all"
                :class="editForm.gender === g.k ? 'border-warm-primary bg-warm-bg text-warm-primary' : 'border-warm-border text-warm-sub hover:border-warm-accent'"
                @click="editForm.gender = g.k"
              >{{ g.t }}</button>
            </div>
          </div>
        </div>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="editOpen = false">取消</button>
          <button class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all disabled:opacity-50 disabled:cursor-not-allowed" :disabled="!editForm.nickname.trim()" @click="saveProfile">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, watch, onMounted} from 'vue'
import { useRouter } from 'vue-router'
import useUserStore from '@/stores/modules/userStore.js'
import useBizStore from '@/stores/modules/bizStore.js'
import { ICONS, iconOf } from './icons'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'

const router = useRouter()
const userStore = useUserStore()
const bizStore = useBizStore()

onMounted(() => {
  bizStore.loadWallet()
  bizStore.loadCoupons()
  bizStore.loadFollows()
  bizStore.loadReviews()
})

const displayName = computed(() => userStore.name)

/* 加入平台天数(后端注册时间计算, 不足 1 天按 1 天; 横杠日期转斜杠避免 Safari 解析失败) */
const joinedDays = computed(() => {
  const t = userStore.createTime ? new Date(userStore.createTime.replace(/-/g, '/')).getTime() : 0
  return t ? Math.max(1, Math.ceil((Date.now() - t) / 86400000)) : 1
})

/* 订单快捷入口 */
const orderShortcuts = computed(() => {
  const c = bizStore.orderCounters
  return [
    { key: 'pending', label: '待支付', icon: 'wallet', count: c.pending || 0 },
    { key: 'booked', label: '待开始', icon: 'calendar', count: c.booked || 0 },
    { key: 'ongoing', label: '进行中', icon: 'play', count: c.ongoing || 0 },
    { key: 'completed', label: '已完成', icon: 'check', count: c.completed || 0 },
  ]
})

/* 功能宫格 */
const features = [
  { label: '我的钱包', icon: 'wallet', color: '#fff3e8', ink: '#f07c2a', to: '/user/wallet' },
  { label: '优惠券', icon: 'coupon', color: '#fdeeee', ink: '#e8746b', to: '/user/coupons' },
  { label: '我的关注', icon: 'users', color: '#fdf3e3', ink: '#e6b422', to: '/user/follows' },
  { label: '我的评价', icon: 'chat', color: '#e4f4f2', ink: '#26a69a', to: '/user/reviews' },
]

/* 编辑资料(昵称/性别落库 user 表) */
const editOpen = ref(false)
const editForm = ref({ nickname: '', gender: 'secret' })

// 弹窗打开时同步最新资料到表单(昵称/性别来自后端 user 表)
watch(editOpen, (v) => {
  if (v) editForm.value = { nickname: userStore.name, gender: userStore.sex === 0 ? 'male' : userStore.sex === 1 ? 'female' : 'secret' }
})

const saveProfile = async () => {
  const ok = await bizStore.updateProfile({
    userName: editForm.value.nickname,
    sex: editForm.value.gender === 'male' ? 0 : editForm.value.gender === 'female' ? 1 : 2,  // 保密(2)不下发, 库中保留原值
  })
  if (!ok) return  // 失败原因(如"用户名已存在")已由拦截器提示
  ElMessage.success('资料已保存')
  editOpen.value = false
}

/* 客服 */
const goService = () => router.push({ path: '/user/messages', query: { conv: 'service' } })

/* 退出登录 */
const logout = () => {
  ElMessageBox.confirm('确定注销并退出系统吗？', '提示', { type: 'warning' })
    .then(() => {
      userStore.logOut().then(() => { location.href = '/login' })
    })
    .catch(() => {})
}
</script>

<style scoped>
.modal-pop { animation: modal-pop 0.22s cubic-bezier(0.34, 1.4, 0.64, 1); }
@keyframes modal-pop {
  from { opacity: 0; transform: scale(0.92) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>