<template>
  <!-- 订单操作弹窗组: 支付 / 取消 / 投诉 / 评价 (orders 与 orderDetail 共用) -->
  <div v-if="visible" class="fixed inset-0 z-[2000] bg-black/40 flex items-center justify-center p-4" @click.self="close">
    <div class="w-[440px] max-w-full bg-white rounded-2xl p-6 modal-pop max-h-[90vh] overflow-y-auto">

      <!-- ======== 支付 ======== -->
      <template v-if="type === 'pay'">
        <h3 class="text-base font-extrabold text-warm-text">订单支付</h3>
        <div class="mt-4 bg-warm-page rounded-xl p-4 text-sm">
          <div class="flex justify-between text-warm-sub">
            <span>{{ order?.companionName }} · {{ order?.serviceName }}</span>
            <span class="text-warm-text">{{ order?.date }} {{ p(order?.startHour) }}:00</span>
          </div>
          <div class="flex justify-between items-baseline mt-2">
            <span class="text-warm-sub">应付金额</span>
            <span class="text-2xl font-extrabold text-warm-primary">¥{{ order?.amount }}</span>
          </div>
        </div>
        <div class="mt-4 space-y-2">
          <button
            v-for="m in payMethods"
            :key="m.key"
            class="w-full flex items-center gap-3 rounded-xl border px-3.5 py-2.5 transition-all"
            :class="payMethod === m.key ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
            @click="payMethod = m.key"
          >
            <span class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ backgroundColor: m.color }">
              <span class="u-icon w-4 h-4" :style="{ color: m.ink }" v-html="iconOf(m.icon)"></span>
            </span>
            <span class="flex-1 text-left text-sm font-semibold text-warm-text">{{ m.label }}</span>
            <span v-if="m.key === 'balance'" class="text-xs" :class="bizStore.balance < order?.amount ? 'text-warm-danger' : 'text-warm-sub'">¥{{ bizStore.balance }}</span>
            <span class="w-4 h-4 rounded-full border-2 flex-shrink-0" :class="payMethod === m.key ? 'border-warm-primary bg-warm-primary' : 'border-warm-border'"></span>
          </button>
        </div>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="close">取消</button>
          <button class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all" @click="confirmPay">确认支付</button>
        </div>
      </template>

      <!-- ======== 取消订单 ======== -->
      <template v-if="type === 'cancel'">
        <h3 class="text-base font-extrabold text-warm-text">取消订单</h3>
        <p class="mt-1.5 text-xs text-warm-sub">
          <template v-if="order?.status === 'booked'">已支付订单取消后将进入退款流程, 余额支付即时到账</template>
          <template v-else>待支付订单取消后无法恢复</template>
        </p>
        <p class="mt-4 text-xs font-bold text-warm-sub">请选择取消原因:</p>
        <div class="mt-2 space-y-2">
          <button
            v-for="r in CANCEL_REASONS"
            :key="r"
            class="w-full text-left rounded-xl border px-4 py-2.5 text-sm transition-all"
            :class="cancelReason === r ? 'border-warm-primary bg-warm-bg text-warm-primary font-semibold' : 'border-warm-border text-warm-text hover:border-warm-accent'"
            @click="cancelReason = r"
          >{{ r }}</button>
        </div>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="close">再想想</button>
          <button class="flex-1 h-10 text-sm font-semibold text-white bg-warm-danger rounded-xl hover:brightness-95 transition-all" @click="confirmCancel">确认取消</button>
        </div>
      </template>

      <!-- ======== 投诉 ======== -->
      <template v-if="type === 'complain'">
        <h3 class="text-base font-extrabold text-warm-text">发起投诉</h3>
        <p class="mt-1.5 text-xs text-warm-sub">平台将在 24 小时内处理, 情节属实全额退款</p>
        <p class="mt-4 text-xs font-bold text-warm-sub">投诉类型:</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="t in COMPLAINT_TYPES"
            :key="t"
            class="px-3 py-1.5 rounded-lg border text-xs font-medium transition-all"
            :class="complainType === t ? 'border-warm-primary bg-warm-bg text-warm-primary' : 'border-warm-border text-warm-sub hover:border-warm-accent'"
            @click="complainType = t"
          >{{ t }}</button>
        </div>
        <textarea
          v-model="complainContent"
          rows="3"
          maxlength="200"
          placeholder="请描述具体问题(可附聊天记录/截图说明)"
          class="mt-3 w-full rounded-xl border border-warm-border px-4 py-3 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors resize-none"
        ></textarea>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="close">取消</button>
          <button class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all disabled:opacity-50" :disabled="!complainType || !complainContent.trim()" @click="confirmComplain">提交投诉</button>
        </div>
      </template>

      <!-- ======== 评价 ======== -->
      <template v-if="type === 'review'">
        <h3 class="text-base font-extrabold text-warm-text">服务评价</h3>
        <div class="mt-4 flex items-center gap-3 bg-warm-page rounded-xl p-3.5">
          <BaseAvatar :name="order?.companionName || ''" :size="40" />
          <div>
            <p class="text-sm font-bold text-warm-text">{{ order?.companionName }}</p>
            <p class="text-xs text-warm-sub mt-0.5">{{ order?.serviceName }} · {{ order?.hours }}小时</p>
          </div>
        </div>
        <!-- 星级 -->
        <div class="mt-4 flex flex-col items-center py-2">
          <RatingStars v-model="reviewForm.rating" :size="30" interactive />
          <p class="mt-1.5 text-xs font-semibold" :class="ratingText.cls">{{ ratingText.text }}</p>
        </div>
        <!-- 标签 -->
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="t in REVIEW_TAGS"
            :key="t"
            class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
            :class="reviewForm.tags.includes(t) ? 'bg-warm-primary text-white' : 'bg-warm-page text-warm-sub hover:text-warm-primary'"
            @click="toggleTag(t)"
          >{{ t }}</button>
        </div>
        <textarea
          v-model="reviewForm.content"
          rows="3"
          maxlength="100"
          placeholder="说说这次服务的体验吧~"
          class="mt-3 w-full rounded-xl border border-warm-border px-4 py-3 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors resize-none"
        ></textarea>
        <div class="mt-5 flex gap-3">
          <button class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors" @click="close">取消</button>
          <button class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all disabled:opacity-50" :disabled="!reviewForm.rating" @click="confirmReview">提交评价</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { CANCEL_REASONS, COMPLAINT_TYPES, REVIEW_TAGS } from '@/mock'
import { iconOf } from './icons'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage } from '@/utils/toast.js'
import BaseAvatar from './components/BaseAvatar.vue'
import RatingStars from './components/RatingStars.vue'

const bizStore = useBizStore()
const emit = defineEmits(['done'])

/* 弹窗状态 */
const visible = ref(false)
const type = ref('') // pay/cancel/complain/review
const order = ref(null)

const p = (n) => String(n ?? 0).padStart(2, '0')

/* ---- 支付 ---- */
const payMethod = ref('balance')
const payMethods = [
  { key: 'balance', label: '余额支付', icon: 'wallet', color: '#fff3e8', ink: '#f07c2a' },
  { key: 'wechat', label: '微信支付', icon: 'chat', color: '#e8f6ee', ink: '#3eb575' },
  { key: 'alipay', label: '支付宝', icon: 'check', color: '#eef3f8', ink: '#5b7a99' },
]

/* ---- 取消 ---- */
const cancelReason = ref('')

/* ---- 投诉 ---- */
const complainType = ref('')
const complainContent = ref('')

/* ---- 评价 ---- */
const reviewForm = ref({ rating: 0, tags: [], content: '' })
const RATING_TEXTS = {
  1: { text: '非常差, 强烈不满', cls: 'text-warm-danger' },
  2: { text: '不满意, 体验较差', cls: 'text-warm-danger' },
  3: { text: '一般, 中规中矩', cls: 'text-warm-warning' },
  4: { text: '满意, 体验不错', cls: 'text-warm-primary' },
  5: { text: '超赞, 强烈推荐!', cls: 'text-warm-primary' },
}
const ratingText = computed(() => RATING_TEXTS[reviewForm.value.rating] || { text: '点击星星打分', cls: 'text-warm-sub' })

const toggleTag = (t) => {
  const i = reviewForm.value.tags.indexOf(t)
  if (i >= 0) reviewForm.value.tags.splice(i, 1)
  else if (reviewForm.value.tags.length < 5) reviewForm.value.tags.push(t)
}

/* ---- 打开/关闭 ---- */
const open = (t, o) => {
  type.value = t
  order.value = o
  payMethod.value = 'balance'
  cancelReason.value = CANCEL_REASONS[0]
  complainType.value = ''
  complainContent.value = ''
  reviewForm.value = { rating: 0, tags: [], content: '' }
  visible.value = true
}
const close = () => { visible.value = false }

defineExpose({ open })

/* ---- 确认动作 ---- */
const confirmPay = async () => {
  const res = await bizStore.payOrder(order.value, payMethod.value)
  if (!res.ok) {
    if (res.msg) ElMessage.error(res.msg)  // 空 msg 表示失败原因已由拦截器提示
    return
  }
  emit('done')
  ElMessage.success('支付成功, 陪玩师已接单')
  close()
}

const confirmCancel = async () => {
  const wasPending = order.value.status === 'pending'
  const res = await bizStore.cancelOrder(order.value.orderNo || order.value.id, cancelReason.value)
  if (!res.ok) return
  emit('done')
  ElMessage.success(wasPending ? '订单已取消' : '订单已取消, 退款将由平台审核后原路退回')
  close()
}

const confirmComplain = async () => {
  const res = await bizStore.complain(order.value.orderNo || order.value.id, complainType.value, complainContent.value.trim())
  if (!res.ok) return
  emit('done')
  ElMessage.success('投诉已提交, 客服将尽快联系您')
  close()
}

const confirmReview = async () => {
  const res = await bizStore.reviewOrder(order.value.orderNo || order.value.id, {
    rating: reviewForm.value.rating,
    tags: [...reviewForm.value.tags],
    content: reviewForm.value.content || '服务不错, 下次还来~',
  })
  if (!res.ok) return
  emit('done')
  ElMessage.success('评价成功, 感谢您的反馈')
  close()
}
</script>

<style scoped>
.modal-pop { animation: modal-pop 0.22s cubic-bezier(0.34, 1.4, 0.64, 1); }
@keyframes modal-pop {
  from { opacity: 0; transform: scale(0.92) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>