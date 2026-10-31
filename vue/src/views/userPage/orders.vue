<template>
  <div class="max-w-[1000px] mx-auto px-4 py-6">
    <h1 class="text-xl font-extrabold text-warm-text">我的订单</h1>

    <!-- 状态 Tab -->
    <div class="mt-4 flex gap-1 bg-white border border-warm-border rounded-xl p-1 overflow-x-auto no-scrollbar">
      <button
        v-for="t in ORDER_TABS"
        :key="t.key"
        class="relative px-4 py-2 rounded-lg text-sm font-semibold whitespace-nowrap transition-all"
        :class="activeTab === t.key ? 'bg-warm-bg text-warm-primary' : 'text-warm-sub hover:text-warm-primary'"
        @click="activeTab = t.key"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- 订单列表 -->
    <div v-if="orders.length" class="mt-4 space-y-4">
      <div v-for="o in orders" :key="o.id" class="bg-white border border-warm-border rounded-2xl p-5 hover:border-warm-accent transition-colors">
        <!-- 头: 订单号 + 状态 -->
        <div class="flex items-center justify-between">
          <span class="text-xs text-warm-sub">订单号 {{ o.id }}</span>
          <span class="flex items-center gap-1.5 text-sm font-bold" :class="ORDER_STATUS[o.status].cls">
            <span class="w-1.5 h-1.5 rounded-full" :class="ORDER_STATUS[o.status].dot"></span>
            {{ ORDER_STATUS[o.status].label }}
          </span>
        </div>

        <!-- 主体: 陪玩师 + 服务信息 -->
        <div class="mt-3 flex items-center gap-3 cursor-pointer" @click="router.push(`/user/order/${o.id}`)">
          <BaseAvatar :name="o.companionName" :image="o.avatar" :size="48" />
          <div class="flex-1 min-w-0">
            <p class="font-bold text-warm-text truncate">{{ o.companionName }}</p>
            <p class="text-xs text-warm-sub mt-0.5">
              <span class="inline-flex items-center gap-1">
                <span class="u-icon w-3 h-3" v-html="iconOf(o.serviceIcon)"></span>{{ o.serviceName }} · {{ o.hours }}小时
              </span>
            </p>
          </div>
          <div class="text-right flex-shrink-0">
            <p class="text-lg font-extrabold" :class="o.status === 'cancelled' ? 'text-warm-sub' : 'text-warm-primary'">¥{{ o.amount }}</p>
            <p v-if="o.couponAmount" class="text-[11px] text-warm-sub">已优惠 ¥{{ o.couponAmount }}</p>
          </div>
        </div>

        <!-- 时间 -->
        <div class="mt-2.5 flex items-center gap-1.5 text-xs text-warm-sub">
          <span class="u-icon w-3.5 h-3.5" v-html="ICONS.clock"></span>
          {{ orderTimeText(o) }}
        </div>

        <!-- 退款中提示 -->
        <div v-if="o.status === 'refunding'" class="mt-2.5 bg-[#fdeeee] rounded-xl px-4 py-2 text-xs text-warm-danger">
          退款处理中, 退款将原路退回({{ o.payMethod === 'balance' ? '余额即时到账' : '1-3 个工作日' }})
        </div>
        <!-- 取消原因 -->
        <div v-if="o.status === 'cancelled' && o.cancelReason" class="mt-2.5 bg-warm-page rounded-xl px-4 py-2 text-xs text-warm-sub">
          取消原因: {{ o.cancelReason }}
        </div>

        <!-- 操作按钮区 -->
        <div class="mt-4 pt-3 border-t border-warm-border flex items-center justify-between flex-wrap gap-2">
          <span class="text-[11px] text-warm-sub">下单于 {{ o.createdAt }}</span>
          <div class="flex items-center gap-2 flex-wrap">
            <button v-if="o.status === 'pending'" class="btn-outline" @click="opsRef.open('cancel', o)">取消订单</button>
            <button v-if="o.status === 'pending'" class="btn-solid" @click="opsRef.open('pay', o)">立即支付</button>

            <button v-if="o.status === 'booked'" class="btn-outline" @click="opsRef.open('cancel', o)">取消退款</button>
            <button v-if="o.status === 'booked'" class="btn-outline" @click="complain(o)">投诉</button>

            <button v-if="o.status === 'ongoing'" class="btn-outline" @click="complain(o)">投诉</button>
            <button v-if="o.status === 'ongoing'" class="btn-solid" @click="finishService(o)">确认完成</button>

            <button v-if="o.status === 'completed' && !o.review" class="btn-outline" @click="complain(o)">投诉</button>
            <button v-if="o.status === 'completed' && !o.review" class="btn-solid" @click="opsRef.open('review', o)">去评价</button>

            <button v-if="canReorder(o)" class="btn-outline" @click="reorder(o)">再次预约</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <EmptyState
      v-else
      icon="order"
      text="还没有相关订单, 去挑选一位合心意的陪玩师吧"
      action-text="去找陪玩"
      class="bg-white border border-warm-border rounded-2xl mt-4"
      @action="router.push('/user/companions')"
    />

    <!-- 操作弹窗组 -->
    <OrderOps ref="opsRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS, iconOf } from './icons'
import { ORDER_STATUS, ORDER_TABS, orderTimeText } from './utils'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'
import BaseAvatar from './components/BaseAvatar.vue'
import EmptyState from './components/EmptyState.vue'
import OrderOps from './OrderOps.vue'

const route = useRoute()
const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()
const opsRef = ref(null)

/* 陪玩师信息来自后端(loadAll 幂等) */
onMounted(() => companionStore.loadAll())

/* 路由 query 支持 ?status=pending 直达 */
const activeTab = ref(route.query.status || 'all')

/* 订单来自后端(loadOrders 按 Tab 状态拉取) */
const orders = computed(() => bizStore.orders)
const reload = () => bizStore.loadOrders(activeTab.value === 'all' ? null : activeTab.value)
onMounted(reload)
watch(activeTab, reload)

/* ---- 操作 ---- */
const finishService = (o) => {
  ElMessageBox.confirm('确认本次服务已完成?', '提示', { type: 'info' })
    .then(async () => {
      const res = await bizStore.finishOrder(o.id)
      if (!res.ok) return
      ElMessage.success('服务完成, 记得评价哦')
    })
    .catch(() => {})
}

const complain = (o) => opsRef.value.open('complain', o)

const canReorder = (o) => ['completed', 'cancelled'].includes(o.status)

const reorder = (o) => {
  const c = companionStore.companionById(o.companionId)
  if (!c) return ElMessage.error('该陪玩师已下架')
  router.push({ path: `/user/booking/${c.id}`, query: o.serviceId ? { service: o.serviceId } : {} })
}
</script>

<style scoped>
.btn-outline {
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  border: 1px solid #e5e0da;
  border-radius: 10px;
  transition: all 0.15s;
}
.btn-outline:hover { color: #f07c2a; border-color: #f07c2a; }
.btn-solid {
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  background: #f07c2a;
  border-radius: 10px;
  transition: all 0.15s;
}
.btn-solid:hover { background: #d96a1f; }
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { scrollbar-width: none; }
</style>