<template>
  <div class="max-w-[1000px] mx-auto px-4 py-6">
    <!-- 步骤指示 -->
    <div class="flex items-center justify-center gap-0 mb-6 select-none">
      <div v-for="(s, i) in steps" :key="s.label" class="flex items-center" :class="{ 'opacity-100': true }">
        <div class="flex items-center gap-2">
          <span class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
                :class="step >= i + 1 ? 'bg-warm-primary text-white' : 'bg-warm-page text-warm-sub'">{{ i + 1 }}</span>
          <span class="text-sm font-semibold" :class="step >= i + 1 ? 'text-warm-text' : 'text-warm-sub'">{{
              s.label
            }}</span>
        </div>
        <div v-if="i < steps.length - 1" class="w-16 h-0.5 mx-3"
             :class="step >= i + 2 ? 'bg-warm-primary' : 'bg-warm-border'"></div>
      </div>
    </div>

    <!-- ========== 下单视图(陪玩师数据到位后渲染) ========== -->
    <div v-if="companion && !successOrder" class="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-5 items-start">
      <div class="space-y-5 min-w-0">
        <!-- 陪玩师摘要 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5 flex items-center gap-4">
          <BaseAvatar :name="companion.name" :image="companion.avatar" :size="56"/>
          <div class="flex-1 min-w-0">
            <p class="font-extrabold text-warm-text">{{ companion.name }}</p>
            <p class="text-xs text-warm-sub mt-0.5">{{ companionStore.gameById(companion.mainGame)?.name }} ·
              {{ companion.rank }} · 评分 {{ companion.rating }}</p>
          </div>
          <button class="text-xs text-warm-sub hover:text-warm-primary transition-colors flex items-center gap-1"
                  @click="router.push(`/user/companion/${companion.id}`)">
            主页<span class="u-icon w-3 h-3" v-html="ICONS.arrowRight"></span>
          </button>
        </div>

        <!-- 1. 选服务 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">选择服务</h3>
          <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
                v-for="s in companion.services"
                :key="s.id"
                class="text-left rounded-xl border p-4 transition-all"
                :class="form.serviceId === s.id ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
                @click="form.serviceId = s.id"
            >
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-2 font-bold text-sm text-warm-text">
                  <span class="u-icon w-4 h-4 text-warm-primary" v-html="iconOf(s.icon)"></span>{{ s.name }}
                </span>
                <span class="font-extrabold text-warm-primary">¥{{ s.price }}<span
                    class="text-xs font-medium text-warm-sub">/时</span></span>
              </div>
              <p class="mt-1.5 text-xs text-warm-sub">{{ s.desc }}</p>
            </button>
          </div>
        </div>

        <!-- 2. 选日期时段 + 时长 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">选择时间</h3>
          <!-- 日期 -->
          <p class="mt-3 text-xs font-bold text-warm-sub">服务日期</p>
          <div class="mt-2 grid grid-cols-4 sm:grid-cols-7 gap-2">
            <button
                v-for="d in days"
                :key="d.dateStr"
                class="rounded-xl border py-2.5 text-center transition-all"
                :class="form.date === d.dateStr ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
                @click="form.date = d.dateStr; form.hour = 0"
            >
              <p class="text-xs font-bold" :class="form.date === d.dateStr ? 'text-warm-primary' : 'text-warm-text'">
                {{ d.label }}</p>
              <p class="text-[11px] text-warm-sub mt-0.5">{{ d.monthDay }}</p>
            </button>
          </div>
          <!-- 时段 -->
          <p class="mt-4 text-xs font-bold text-warm-sub">开始时段</p>
          <div class="mt-2 grid grid-cols-5 sm:grid-cols-9 gap-2">
            <template v-if="form.date">
              <button
                  v-for="h in SLOT_HOURS"
                  :key="h"
                  :disabled="!isSlotAvailable(form.date, h)"
                  class="rounded-lg border py-2 text-xs font-semibold transition-all"
                  :class="[
                  form.hour === h ? 'border-warm-primary bg-warm-primary text-white'
                    : isSlotAvailable(form.date, h) ? 'border-warm-border text-warm-text hover:border-warm-accent'
                    : 'border-warm-border bg-warm-page text-warm-sub/50 cursor-not-allowed'
                ]"
                  @click="form.hour = h"
              >{{ String(h).padStart(2, '0') }}:00
              </button>
            </template>
            <p v-else class="col-span-full text-xs text-warm-sub py-2">请先选择服务日期</p>
          </div>
          <!-- 时长 -->
          <p class="mt-4 text-xs font-bold text-warm-sub">服务时长</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <button
                v-for="n in 5"
                :key="n"
                :disabled="form.hour > 0 && form.hour + n > 24"
                class="px-4 py-2 rounded-lg border text-xs font-semibold transition-all"
                :class="[
                form.hours === n ? 'border-warm-primary bg-warm-primary text-white'
                  : form.hour > 0 && form.hour + n > 24 ? 'border-warm-border bg-warm-page text-warm-sub/50 cursor-not-allowed'
                  : 'border-warm-border text-warm-text hover:border-warm-accent'
              ]"
                @click="form.hours = n"
            >{{ n }} 小时
            </button>
          </div>
        </div>

        <!-- 3. 备注 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">需求备注 <span class="text-xs font-normal text-warm-sub">(选填)</span></h3>
          <textarea
              v-model="form.note"
              rows="3"
              maxlength="100"
              placeholder="例如: 我黄金段位主玩射手, 想冲铂金, 麻烦带飞~"
              class="mt-3 w-full rounded-xl border border-warm-border px-4 py-3 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors resize-none"
          ></textarea>
          <p class="mt-1 text-right text-xs text-warm-sub">{{ form.note.length }}/100</p>
        </div>

        <!-- 4. 优惠券 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h3 class="section-title">优惠券</h3>
          <div v-if="usableCoupons.length" class="mt-3 space-y-2">
            <button
                v-for="c in usableCoupons"
                :key="c.id"
                class="w-full flex items-center gap-3 rounded-xl border px-4 py-3 transition-all"
                :class="form.couponId === c.id ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
                @click="form.couponId = form.couponId === c.id ? null : c.id"
            >
              <div class="w-14 text-center border-r border-dashed border-warm-border pr-3">
                <p class="text-lg font-extrabold text-warm-danger">¥{{ c.amount }}</p>
                <p class="text-[10px] text-warm-sub">{{ c.kind === 'free' ? '无门槛' : `满${c.threshold}可用` }}</p>
              </div>
              <div class="flex-1 text-left min-w-0">
                <p class="text-sm font-bold text-warm-text">{{ c.name }}</p>
                <p class="text-xs text-warm-sub mt-0.5">{{ c.expireAt }} 前有效</p>
              </div>
              <span
                  class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors"
                  :class="form.couponId === c.id ? 'border-warm-primary bg-warm-primary' : 'border-warm-border'"
              >
                <span v-if="form.couponId === c.id" class="u-icon w-3 h-3 text-white" v-html="ICONS.check"></span>
              </span>
            </button>
          </div>
          <p v-else class="mt-3 text-xs text-warm-sub">暂无可用优惠券, 去
            <router-link to="/user/coupons" class="text-warm-primary font-semibold">领券中心</router-link>
            看看
          </p>
        </div>
      </div>

      <!-- 右侧订单摘要(粘性) -->
      <div class="lg:sticky lg:top-20 bg-white border border-warm-border rounded-2xl p-5">
        <h3 class="section-title">订单明细</h3>
        <div class="mt-4 space-y-2.5 text-sm">
          <div class="flex justify-between text-warm-sub"><span>服务</span><span
              class="text-warm-text">{{ service?.name || '未选择' }}</span></div>
          <div class="flex justify-between text-warm-sub"><span>单价</span><span
              class="text-warm-text">¥{{ service?.price ?? '-' }}/小时</span></div>
          <div class="flex justify-between text-warm-sub"><span>时间</span><span class="text-warm-text">{{
              timeText
            }}</span></div>
          <div class="flex justify-between text-warm-sub"><span>时长</span><span class="text-warm-text">{{ form.hours }} 小时</span>
          </div>
          <div class="flex justify-between text-warm-sub"><span>小计</span><span class="text-warm-text">¥{{
              gross
            }}</span></div>
          <div v-if="couponAmount" class="flex justify-between text-warm-sub"><span>优惠券</span><span
              class="text-warm-danger">-¥{{ couponAmount }}</span></div>
        </div>
        <div class="mt-4 pt-3 border-t border-warm-border flex items-center justify-between">
          <span class="text-sm text-warm-sub">应付</span>
          <span class="text-2xl font-extrabold text-warm-primary">¥{{ amount }}</span>
        </div>

        <!-- 支付方式 -->
        <p class="mt-4 text-xs font-bold text-warm-sub">支付方式</p>
        <div class="mt-2 space-y-2">
          <button
              v-for="m in payMethods"
              :key="m.key"
              class="w-full flex items-center gap-3 rounded-xl border px-3.5 py-2.5 transition-all"
              :class="payMethod === m.key ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
              @click="payMethod = m.key"
          >
            <span class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  :style="{ backgroundColor: m.color }">
              <span class="u-icon w-4 h-4" :style="{ color: m.ink }" v-html="iconOf(m.icon)"></span>
            </span>
            <span class="flex-1 text-left text-sm font-semibold text-warm-text">{{ m.label }}</span>
            <span v-if="m.key === 'balance'" class="text-xs text-warm-sub">¥{{ bizStore.balance }}</span>
            <span
                class="w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                :class="payMethod === m.key ? 'border-warm-primary' : 'border-warm-border'"
                :style="payMethod === m.key ? 'backgroundColor: #f07c2a' : ''"
            >
              <span v-if="payMethod === m.key" class="w-1.5 h-1.5 rounded-full bg-white"></span>
            </span>
          </button>
        </div>

        <button
            class="w-full mt-5 h-12 text-sm font-bold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!canSubmit"
            @click="submit"
        >{{ payMethod === 'balance' ? `余额支付 ¥${amount}` : `提交订单 ¥${amount}` }}
        </button>
        <p class="mt-2.5 text-center text-[11px] text-warm-sub">支付即表示同意平台服务协议, 平台担保交易</p>
      </div>
    </div>

    <!-- ========== 成功视图 ========== -->
    <div v-else-if="successOrder"
         class="bg-white border border-warm-border rounded-2xl py-16 px-4 flex flex-col items-center">
      <div class="w-16 h-16 rounded-full bg-[#e4f4f2] flex items-center justify-center">
        <span class="u-icon w-8 h-8 text-warm-success" v-html="ICONS.check"></span>
      </div>
      <h2 class="mt-4 text-xl font-extrabold text-warm-text">预约成功</h2>
      <p class="mt-2 text-sm text-warm-sub">订单已支付, 陪玩师会在服务开始前与你确认细节</p>
      <div class="mt-5 bg-warm-page rounded-xl px-6 py-3 text-sm">
        订单号: <b class="text-warm-text">{{ successOrder.id }}</b>
      </div>
      <div class="mt-6 flex gap-3">
        <button
            class="px-6 h-11 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors"
            @click="router.push('/user/companions')">继续逛逛
        </button>
        <button
            class="px-6 h-11 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all"
            @click="router.push(`/user/order/${successOrder.id}`)">查看订单
        </button>
      </div>
    </div>

    <!-- ========== 加载中兜底(陪玩师数据未到位) ========== -->
    <div v-else class="bg-white border border-warm-border rounded-2xl py-16 px-4 text-center text-sm text-warm-sub">
      正在加载陪玩师信息...
    </div>
  </div>
</template>

<script setup>
import {ref, computed, watch, onMounted} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import {ICONS, iconOf} from './icons'
import {SLOT_HOURS, nextDays, fmtDate} from './utils'
import {selectOccupiedSlots} from '@/api/biz/order.js'
import useBizStore from '@/stores/modules/bizStore.js'
import {ElMessage} from '@/utils/toast.js'
import BaseAvatar from './components/BaseAvatar.vue'

const route = useRoute()
const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()

/* 陪玩师及服务包来自后端(loadAll 幂等) */
onMounted(() => {
  bizStore.loadWallet()
  bizStore.loadCoupons()
  companionStore.loadAll()
})

const companion = computed(() => companionStore.companionById(route.params.companionId))

/* 数据到位后仍查不到才提示并跳转(避免加载中误判) */
watch(() => companionStore.loaded, (loaded) => {
  if (loaded && !companion.value) {
    ElMessage.error('陪玩师不存在')
    router.replace('/user/companions')
  }
})

const days = nextDays(7)
const steps = [{label: '选择服务'}, {label: '确认时间'}, {label: '支付下单'}]

/* 表单(query 预填: 从详情页带参进入) */
const form = ref({
  serviceId: Number(route.query.service) || companion.value?.services[0]?.id || null,
  date: route.query.date || '',
  hour: Number(route.query.hour) || 0,
  hours: 2,
  note: '',
  couponId: null,
})
const payMethod = ref('balance')
const successOrder = ref(null)

/* 数据到位后若未选服务则默认选第一个服务包(异步加载兜底) */
watch(companion, (c) => {
  if (c && !form.value.serviceId && c.services.length) {
    form.value.serviceId = c.services[0].id
  }
})

/* 已占用时段(后端订单为准): 陪玩师/日期变化时重新拉取 */
const occupiedHours = ref([])
watch([() => companion.value?.id, () => form.value.date], ([cid, date]) => {
  occupiedHours.value = []
  if (!cid || !date) return
  selectOccupiedSlots(cid, date).then(res => {
    occupiedHours.value = res.data || []
  }).catch(() => {
  })
})

/** 时段是否可约: 已过时段不可约 + 该陪玩师当天已被占用时段不可约(后端订单为准) */
const isSlotAvailable = (dateStr, hour) => {
  const now = new Date()
  if (dateStr === fmtDate(now) && hour <= now.getHours()) return false
  return !occupiedHours.value.includes(hour)
}

const payMethods = [
  {key: 'balance', label: '余额支付', icon: 'wallet', color: '#fff3e8', ink: '#f07c2a'},
  {key: 'wechat', label: '微信支付', icon: 'chat', color: '#e8f6ee', ink: '#3eb575'},
  {key: 'alipay', label: '支付宝', icon: 'check', color: '#eef3f8', ink: '#5b7a99'},
]

const service = computed(() => companion.value?.services.find(s => s.id === form.value.serviceId))
const gross = computed(() => (service.value ? service.value.price * form.value.hours : 0))

/* 可用券(满足门槛) */
const usableCoupons = computed(() => bizStore.usableCoupons.filter(c => gross.value >= c.threshold))
const couponAmount = computed(() => {
  const c = usableCoupons.value.find(x => x.id === form.value.couponId)
  return c ? Math.min(c.amount, gross.value) : 0
})
const amount = computed(() => Math.max(0, gross.value - couponAmount.value))

const timeText = computed(() => {
  if (!form.value.date || !form.value.hour) return '未选择'
  const p = (n) => String(n).padStart(2, '0')
  return `${form.value.date.slice(5)} ${p(form.value.hour)}:00-${p(form.value.hour + form.value.hours)}:00`
})

/* 步骤高亮进度 */
const step = computed(() => {
  let s = 1
  if (form.value.serviceId) s = 2
  if (form.value.date && form.value.hour) s = 3
  return s
})

const canSubmit = computed(() => service.value && form.value.date && form.value.hour && form.value.hours > 0)

const submit = async () => {
  if (!canSubmit.value) return
  if (form.value.hour + form.value.hours > 24) return ElMessage.warning('服务结束时间超出当天, 请减少时长')
  /* 余额支付预校验: 余额不足直接拦截, 不发起下单(避免残留待支付订单) */
  if (payMethod.value === 'balance' && bizStore.balance < amount.value) {
    return ElMessage.error('余额不足, 请先前往钱包充值或更换支付方式')
  }
  /* 创建订单(后端事务校验/定价) -> 支付(余额/微信/支付宝) */
  const created = await bizStore.createOrder({
    companionId: companion.value.id,
    serviceId: form.value.serviceId,
    date: form.value.date,
    startHour: form.value.hour,
    hours: form.value.hours,
    note: form.value.note,
    userCouponId: form.value.couponId,
  })
  if (!created.ok) {
    if (created.msg) ElMessage.error(created.msg)  // 空 msg 表示失败原因已由拦截器提示
    return
  }
  const res = await bizStore.payOrder({
    orderNo: created.orderNo,
    companionId: companion.value.id,
    couponId: form.value.couponId,
    date: form.value.date,
    startHour: form.value.hour,
  }, payMethod.value)
  if (!res.ok) {
    /* 支付失败(如并发下余额变动): 自动取消刚创建的待支付订单, 避免残留占用时段(失败原因已由拦截器提示) */
    if (created.orderNo) await bizStore.cancelOrder(created.orderNo, '支付未完成, 自动取消')
    return
  }
  successOrder.value = {id: created.orderNo}
  ElMessage.success('支付成功')
}
</script>

<style scoped>
.section-title {
  font-size: 15px;
  font-weight: 800;
  color: #1f2d3d;
}
</style>