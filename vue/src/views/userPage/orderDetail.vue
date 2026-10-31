<template>
  <div v-if="order" class="max-w-[860px] mx-auto px-4 py-6">
    <!-- 返回 -->
    <div class="flex items-center gap-2 text-xs text-warm-sub mb-4">
      <button class="flex items-center gap-1 hover:text-warm-primary transition-colors" @click="router.back()">
        <span class="u-icon w-3.5 h-3.5" v-html="ICONS.arrowLeft"></span>返回
      </button>
      <span>/</span>
      <router-link to="/user/orders" class="hover:text-warm-primary transition-colors">我的订单</router-link>
      <span>/</span>
      <span class="text-warm-text">订单详情</span>
    </div>

    <!-- 状态卡 -->
    <div class="bg-white border border-warm-border rounded-2xl p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="flex items-center gap-2 text-xl font-extrabold" :class="ORDER_STATUS[order.status].cls">
            <span class="w-2 h-2 rounded-full" :class="ORDER_STATUS[order.status].dot"></span>
            {{ ORDER_STATUS[order.status].label }}
          </p>
          <p class="mt-1.5 text-xs text-warm-sub">{{ statusHint }}</p>
        </div>
        <div class="text-right">
          <p class="text-xs text-warm-sub">实付金额</p>
          <p class="text-2xl font-extrabold" :class="order.status === 'cancelled' ? 'text-warm-sub' : 'text-warm-primary'">¥{{ order.amount }}</p>
        </div>
      </div>

      <!-- 状态时间线 -->
      <div class="mt-6 flex items-center">
        <template v-for="(n, i) in timeline" :key="n.label">
          <div class="flex flex-col items-center gap-1.5 flex-shrink-0">
            <span
              class="w-8 h-8 rounded-full flex items-center justify-center"
              :class="n.done ? 'bg-warm-primary text-white' : 'bg-warm-page text-warm-sub'"
            >
              <span class="u-icon w-4 h-4" v-html="ICONS[n.icon]"></span>
            </span>
            <span class="text-xs font-semibold" :class="n.done ? 'text-warm-text' : 'text-warm-sub'">{{ n.label }}</span>
          </div>
          <div v-if="i < timeline.length - 1" class="flex-1 h-0.5 mx-2 mb-6" :class="timeline[i + 1].done ? 'bg-warm-primary' : 'bg-warm-border'"></div>
        </template>
      </div>
    </div>

    <div class="mt-4 grid grid-cols-1 md:grid-cols-[1fr_280px] gap-4 items-start">
      <div class="space-y-4">
        <!-- 陪玩师卡 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5 flex items-center gap-4">
          <BaseAvatar :name="order.companionName" :image="order.avatar" :size="52" />
          <div class="flex-1 min-w-0">
            <p class="font-bold text-warm-text">{{ order.companionName }}</p>
            <p class="text-xs text-warm-sub mt-0.5">{{ order.serviceName }} · {{ order.hours }} 小时</p>
          </div>
          <button class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-warm-border text-warm-sub hover:text-warm-primary hover:border-warm-primary transition-all" @click="goChat">聊一聊</button>
          <button class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-warm-border text-warm-sub hover:text-warm-primary hover:border-warm-primary transition-all" @click="router.push(`/user/companion/${order.companionId}`)">主页</button>
        </div>

        <!-- 服务信息 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">服务信息</h3>
          <div class="mt-3 space-y-2.5 text-sm">
            <div class="flex justify-between"><span class="text-warm-sub">服务项目</span><span class="text-warm-text font-semibold">{{ order.serviceName }}</span></div>
            <div class="flex justify-between"><span class="text-warm-sub">服务时间</span><span class="text-warm-text">{{ orderTimeText(order) }}</span></div>
            <div class="flex justify-between"><span class="text-warm-sub">服务时长</span><span class="text-warm-text">{{ order.hours }} 小时</span></div>
            <div v-if="order.note" class="flex justify-between"><span class="text-warm-sub flex-shrink-0 mr-6">备注</span><span class="text-warm-text text-right">{{ order.note }}</span></div>
          </div>
        </div>

        <!-- 我的评价 -->
        <div v-if="order.review" class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">我的评价</h3>
          <div class="mt-3 flex items-center gap-2">
            <RatingStars :model-value="order.review.rating" :size="16" />
            <span class="text-xs text-warm-sub">{{ order.review.time }}</span>
          </div>
          <p class="mt-2.5 text-sm leading-6 text-warm-text">{{ order.review.content }}</p>
          <div v-if="order.review.tags?.length" class="mt-2 flex flex-wrap gap-1.5">
            <TagBadge v-for="t in order.review.tags" :key="t" :text="t" type="warning" />
          </div>
          <div v-if="order.review.reply" class="mt-2.5 bg-warm-page rounded-xl px-4 py-2.5 text-xs leading-5 text-warm-sub">
            <b class="text-warm-primary">平台回复:</b> {{ order.review.reply }}
          </div>
        </div>

        <!-- 投诉记录(已投诉时展示处理进度/结果, 与发起投诉按钮互斥) -->
        <div v-if="order.complaint" class="bg-white border border-warm-border rounded-2xl p-5">
          <div class="flex items-center justify-between">
            <h3 class="section-title">投诉记录</h3>
            <span class="inline-flex items-center gap-1.5 text-xs font-semibold" :class="order.complaint.status === 0 ? 'text-warm-warning' : 'text-warm-success'">
              <span class="w-1.5 h-1.5 rounded-full" :class="order.complaint.status === 0 ? 'bg-warm-warning' : 'bg-warm-success'"></span>
              {{ order.complaint.status === 0 ? '处理中' : '已处理' }}
            </span>
          </div>
          <div class="mt-3 flex items-center gap-2">
            <TagBadge :text="order.complaint.type" type="danger" />
            <span class="text-xs text-warm-sub">提交于 {{ order.complaint.time }}</span>
          </div>
          <div v-if="order.complaint.status === 1" class="mt-3 rounded-xl bg-warm-page px-4 py-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-warm-sub">平台处理</span>
              <span class="text-xs text-warm-sub">{{ order.complaint.handleTime }}</span>
            </div>
            <p class="mt-1.5 text-sm font-bold" :class="order.complaint.result === '驳回投诉' ? 'text-warm-sub' : 'text-warm-primary'">{{ order.complaint.result }}</p>
            <p v-if="order.complaint.reply" class="mt-1.5 text-sm leading-6 text-warm-text whitespace-pre-wrap break-all">{{ order.complaint.reply }}</p>
          </div>
          <p v-else class="mt-2.5 text-xs text-warm-sub">平台将在 24 小时内处理, 请留意消息通知</p>
        </div>

        <!-- 订单信息 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">订单信息</h3>
          <div class="mt-3 space-y-2.5 text-sm">
            <div class="flex justify-between"><span class="text-warm-sub">订单编号</span><span class="text-warm-text">{{ order.id }}</span></div>
            <div class="flex justify-between"><span class="text-warm-sub">下单时间</span><span class="text-warm-text">{{ order.createdAt }}</span></div>
            <div v-if="order.payAt" class="flex justify-between"><span class="text-warm-sub">支付时间</span><span class="text-warm-text">{{ order.payAt }}</span></div>
            <div v-if="order.payAt" class="flex justify-between">
              <span class="text-warm-sub">支付方式</span>
              <span class="text-warm-text">{{ { balance: '余额支付', wechat: '微信支付', alipay: '支付宝' }[order.payMethod] || '-' }}</span>
            </div>
            <div v-if="order.startAt" class="flex justify-between"><span class="text-warm-sub">开始时间</span><span class="text-warm-text">{{ order.startAt }}</span></div>
            <div v-if="order.endAt" class="flex justify-between"><span class="text-warm-sub">完成时间</span><span class="text-warm-text">{{ order.endAt }}</span></div>
            <div v-if="order.cancelReason" class="flex justify-between"><span class="text-warm-sub">取消原因</span><span class="text-warm-danger">{{ order.cancelReason }}</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧价格明细 + 操作 -->
      <div class="md:sticky md:top-20 space-y-4">
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">价格明细</h3>
          <div class="mt-3 space-y-2.5 text-sm">
            <div class="flex justify-between"><span class="text-warm-sub">服务单价</span><span class="text-warm-text">¥{{ order.price }}/小时</span></div>
            <div class="flex justify-between"><span class="text-warm-sub">服务小计</span><span class="text-warm-text">¥{{ order.gross }}</span></div>
            <div v-if="order.couponAmount" class="flex justify-between"><span class="text-warm-sub">{{ order.couponName }}</span><span class="text-warm-danger">-¥{{ order.couponAmount }}</span></div>
            <div class="flex justify-between items-baseline pt-2.5 border-t border-warm-border">
              <span class="text-warm-sub">实付款</span>
              <span class="text-xl font-extrabold" :class="order.status === 'cancelled' ? 'text-warm-sub' : 'text-warm-primary'">¥{{ order.amount }}</span>
            </div>
          </div>
        </div>

        <!-- 操作 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5 space-y-2">
          <button v-if="order.status === 'pending'" class="w-full h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all" @click="opsRef.open('pay', order)">立即支付</button>
          <button v-if="order.status === 'pending'" class="w-full h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-danger hover:border-warm-danger transition-all" @click="opsRef.open('cancel', order)">取消订单</button>

          <button v-if="order.status === 'booked'" class="w-full h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-all" @click="opsRef.open('cancel', order)">取消退款</button>

          <button v-if="order.status === 'ongoing'" class="w-full h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all" @click="finishService">确认完成</button>

          <button v-if="order.status === 'completed' && !order.review" class="w-full h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all" @click="opsRef.open('review', order)">评价本次服务</button>

          <button v-if="['booked', 'ongoing', 'completed'].includes(order.status) && !order.complaint" class="w-full h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-danger hover:border-warm-danger transition-all" @click="opsRef.open('complain', order)">发起投诉</button>

          <button v-if="canReorder" class="w-full h-10 text-sm font-semibold rounded-xl border border-warm-primary text-warm-primary hover:bg-warm-bg transition-all" @click="reorder">再次预约</button>
        </div>
      </div>
    </div>

    <OrderOps ref="opsRef" @done="reload"/>
  </div>

  <div v-else class="max-w-[860px] mx-auto px-4 py-6">
    <EmptyState icon="order" text="订单不存在或已被删除" action-text="去看订单列表" class="bg-white border border-warm-border rounded-2xl" @action="router.push('/user/orders')" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS } from './icons'
import { ORDER_STATUS, orderTimeText } from './utils'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'
import BaseAvatar from './components/BaseAvatar.vue'
import RatingStars from './components/RatingStars.vue'
import TagBadge from './components/TagBadge.vue'
import EmptyState from './components/EmptyState.vue'
import OrderOps from './OrderOps.vue'

const route = useRoute()
const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()
const opsRef = ref(null)

/* 陪玩师信息来自后端(loadAll 幂等); 订单详情来自后端(按订单号拉取) */
onMounted(() => { companionStore.loadAll(); reload() })

const order = ref(null)
const reload = () => bizStore.fetchOrder(route.params.id).then(o => { order.value = o })

/* 状态时间线(评价为可选末步, 已评价才点亮) */
const flowDone = { pending: 1, booked: 2, ongoing: 3, completed: 4 }
const stepIndex = computed(() => flowDone[order.value?.status] ?? 0)

const timeline = computed(() => {
  if (['cancelled', 'refunding'].includes(order.value?.status)) {
    return [
      { label: '提交订单', icon: 'order', done: true },
      { label: order.value.status === 'refunding' ? '退款中' : '已取消', icon: order.value.status === 'refunding' ? 'refund' : 'close', done: true },
    ]
  }
  return [
    { label: '提交订单', icon: 'order', done: true },
    { label: '支付订单', icon: 'wallet', done: stepIndex.value >= 2 },
    { label: '开始服务', icon: 'play', done: stepIndex.value >= 3 },
    { label: '服务完成', icon: 'check', done: stepIndex.value >= 4 },
    { label: '评价', icon: 'star', done: !!order.value.review },
  ]
})

const statusHint = computed(() => {
  if (order.value?.status === 'completed') {
    return order.value.review ? '订单已完成, 感谢使用平台服务' : '服务已完成, 别忘了给陪玩师一个评价'
  }
  return {
    pending: '订单尚未支付, 15 分钟内未支付将自动取消',
    booked: '预约成功, 服务将在约定时间开始, 请留意消息通知',
    ongoing: '服务进行中, 尽情享受游戏时光',
    refunding: '退款处理中, 到账后将通过消息通知你',
    cancelled: '订单已取消',
  }[order.value?.status] || ''
})

/* ---- 操作 ---- */
const finishService = () => {
  ElMessageBox.confirm('确认本次服务已完成?', '提示', { type: 'info' })
    .then(async () => {
      const res = await bizStore.finishOrder(order.value.id)
      if (!res.ok) return
      ElMessage.success('服务完成, 记得评价哦')
      reload()
    })
    .catch(() => {})
}
const goChat = () => {
  // 跳转消息页直达私聊会话(页面内由 ensureConversation 后端 get_or_create + 拉历史)
  router.push({ path: '/user/messages', query: { conv: `c_${order.value.companionId}` } })
}
const canReorder = computed(() => ['completed', 'cancelled'].includes(order.value?.status))

const reorder = () => {
  const c = companionStore.companionById(order.value.companionId)
  if (!c) return ElMessage.error('该陪玩师已下架')
  router.push(`/user/booking/${c.id}`)
}
</script>

<style scoped>
.section-title {
  font-size: 15px;
  font-weight: 800;
  color: #1f2d3d;
}
</style>