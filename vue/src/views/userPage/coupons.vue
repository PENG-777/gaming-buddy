<template>
  <div class="max-w-[900px] mx-auto px-4 py-6">
    <!-- 我的优惠券 -->
    <div class="bg-white border border-warm-border rounded-2xl p-5">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-extrabold text-warm-text">我的优惠券</h1>
        <p class="text-xs text-warm-sub">可用 {{ bizStore.usableCoupons.length }} 张</p>
      </div>

      <!-- 状态 Tab -->
      <div class="mt-4 flex gap-1 bg-warm-page rounded-xl p-1 self-start">
        <button
          v-for="t in tabs"
          :key="t.key"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
          :class="tab === t.key ? 'bg-white text-warm-primary shadow-sm' : 'text-warm-sub hover:text-warm-primary'"
          @click="tab = t.key"
        >{{ t.label }} ({{ countOf(t.key) }})</button>
      </div>

      <!-- 券列表 -->
      <div v-if="list.length" class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="c in list"
          :key="c.id"
          class="flex items-stretch rounded-2xl border overflow-hidden transition-all"
          :class="c.status === 'usable' ? 'border-warm-border bg-white' : 'border-warm-border bg-warm-page opacity-70'"
        >
          <!-- 金额区 -->
          <div class="w-[96px] flex flex-col items-center justify-center py-4 flex-shrink-0" :class="c.status === 'usable' ? 'bg-warm-bg' : 'bg-[#f5f5f4]'">
            <p class="text-2xl font-extrabold" :class="c.status === 'usable' ? 'text-warm-danger' : 'text-warm-sub'">
              <span class="text-sm align-top">¥</span>{{ c.amount }}
            </p>
            <p class="text-[10px] mt-0.5" :class="c.status === 'usable' ? 'text-warm-primary' : 'text-warm-sub'">
              {{ c.kind === 'free' ? '无门槛' : `满${c.threshold}可用` }}
            </p>
          </div>
          <!-- 信息区 -->
          <div class="flex-1 min-w-0 px-4 py-3.5 flex flex-col">
            <p class="text-sm font-bold truncate" :class="c.status === 'usable' ? 'text-warm-text' : 'text-warm-sub'">{{ c.name }}</p>
            <p class="mt-1 text-xs text-warm-sub">{{ c.expireAt }} 前有效</p>
            <p class="mt-auto pt-2 text-[11px] text-warm-sub">
              <template v-if="c.status === 'used'">已于 {{ c.usedAt }} 使用</template>
              <template v-else-if="c.status === 'expired'">已过期</template>
              <template v-else>下单时可选择抵扣</template>
            </p>
          </div>
          <!-- 状态角标 -->
          <div v-if="c.status !== 'usable'" class="self-stretch flex items-center pr-4">
            <span class="px-2 py-1 rounded-lg text-[11px] font-bold bg-warm-page text-warm-sub">{{ c.status === 'used' ? '已使用' : '已过期' }}</span>
          </div>
        </div>
      </div>
      <EmptyState v-else icon="coupon" text="该状态下暂无优惠券" action-text="去领券" @action="scrollToCenter" class="!py-10" />
    </div>

    <!-- 领券中心 -->
    <div ref="centerRef" class="mt-4 bg-white border border-warm-border rounded-2xl p-5">
      <h2 class="text-base font-extrabold text-warm-text">领券中心</h2>
      <p class="mt-1 text-xs text-warm-sub">领取后自动放入我的优惠券, 达到限领次数或抢完即止</p>
      <div v-if="availableList.length" class="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="t in availableList"
          :key="t.couponId"
          class="rounded-2xl border border-warm-border p-4 flex flex-col transition-all"
          :class="canClaim(t) ? 'hover:border-warm-accent' : 'opacity-70'"
        >
          <div class="flex items-baseline justify-between">
            <p class="text-xl font-extrabold text-warm-danger">
              <span class="text-xs align-top">¥</span>{{ t.amount }}
            </p>
            <span class="text-[11px] text-warm-sub">{{ t.threshold > 0 ? `满${t.threshold}可用` : '无门槛' }}</span>
          </div>
          <p class="mt-1.5 text-sm font-bold text-warm-text">{{ t.couponName }}</p>
          <p class="mt-0.5 text-xs text-warm-sub">{{ t.description || '下单可抵扣' }} · 领取后{{ t.validDays }}天有效</p>
          <button
            class="mt-3 h-8 text-xs font-bold rounded-lg transition-all active:scale-95"
            :class="canClaim(t)
              ? 'bg-warm-primary text-white hover:bg-warm-deep'
              : 'bg-warm-page text-warm-sub cursor-default'"
            :disabled="!canClaim(t)"
            @click="claim(t)"
          >{{ soldOut(t) ? '已抢完' : claimed(t) ? '已领取' : '立即领取' }}</button>
        </div>
      </div>
      <EmptyState v-else icon="coupon" text="暂无可领取的优惠券" class="!py-10" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { selectAvailableCouponList } from '@/api/biz/coupon.js'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage } from '@/utils/toast.js'
import EmptyState from './components/EmptyState.vue'

const bizStore = useBizStore()

const tabs = [
  { key: 'usable', label: '可使用' },
  { key: 'used', label: '已使用' },
  { key: 'expired', label: '已过期' },
]
const tab = ref('usable')

const list = computed(() => bizStore.coupons.filter(c => c.status === tab.value))
const countOf = (key) => bizStore.coupons.filter(c => c.status === key).length

/* 领券中心(后端启用券, 附本人已领次数与全站已领数量) */
const availableList = ref([])
const claimed = (t) => (t.claimedCount ?? 0) >= (t.perLimit ?? 1)   // 已达限领次数
const soldOut = (t) => t.totalCount > 0 && (t.receivedCount ?? 0) >= t.totalCount  // 限量已领完
const canClaim = (t) => !claimed(t) && !soldOut(t)

const loadAvailable = () => {
  selectAvailableCouponList().then(res => { availableList.value = res.data || [] })
}

/* 领取: 后端校验限领/限量, 失败提示由响应拦截器统一弹出 */
const claim = async (t) => {
  const res = await bizStore.claimCoupon(t.couponId)
  if (res.ok) {
    ElMessage.success(`「${t.couponName}」领取成功`)
    tab.value = 'usable'
    loadAvailable()  // 刷新领券中心按钮状态
  }
}

const centerRef = ref(null)
const scrollToCenter = () => centerRef.value?.scrollIntoView({ behavior: 'smooth' })

onMounted(() => {
  bizStore.loadCoupons()  // 我的优惠券(后端)
  loadAvailable()         // 领券中心
})
</script>