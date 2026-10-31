<template>
  <div class="max-w-[900px] mx-auto px-4 py-6">
    <!-- 余额卡 -->
    <div class="bg-warm-primary rounded-2xl p-7 text-white relative overflow-hidden">
      <!-- 装饰图标(纯色, 无渐变) -->
      <span class="u-icon w-40 h-40 text-white/10 absolute -right-6 -top-6" v-html="ICONS.wallet"></span>
      <p class="text-sm opacity-80">当前余额 (元)</p>
      <p class="mt-1 text-4xl font-extrabold tracking-tight">{{ bizStore.balance.toFixed(2) }}</p>
      <div class="mt-5 flex items-center gap-3">
        <button
            class="px-6 h-10 text-sm font-bold bg-white text-warm-primary rounded-xl hover:bg-warm-bg active:scale-[0.97] transition-all"
            @click="openRecharge">立即充值
        </button>
        <router-link to="/user/orders"
                     class="px-5 h-10 flex items-center text-sm font-semibold border border-white/60 rounded-xl hover:bg-white/10 transition-colors">
          消费记录
        </router-link>
      </div>
    </div>

    <!-- 收支明细(后端 wallet_transaction 分页) -->
    <div class="mt-4 bg-white border border-warm-border rounded-2xl p-5">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-extrabold text-warm-text">收支明细</h2>
        <p class="text-xs text-warm-sub">共 {{ txTotal }} 条记录</p>
      </div>

      <div v-if="txList.length" class="mt-3 divide-y divide-warm-border">
        <div v-for="t in txList" :key="t.txId" class="flex items-center gap-3 py-3.5">
          <div class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
               :class="TYPE_META[t.type]?.bg">
            <span class="u-icon w-4 h-4" :class="TYPE_META[t.type]?.cls"
                  v-html="iconOf(TYPE_META[t.type]?.icon)"></span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-warm-text truncate">{{ t.note }}</p>
            <p class="text-xs text-warm-sub mt-0.5">{{ t.createTime }}</p>
          </div>
          <p class="text-sm font-extrabold flex-shrink-0"
             :class="t.amount >= 0 ? 'text-warm-success' : 'text-warm-text'">
            {{ t.amount >= 0 ? '+' : '' }}¥{{ Math.abs(t.amount) }}
          </p>
        </div>
      </div>
      <EmptyState v-else-if="!txLoading" icon="wallet" text="暂无收支记录"/>

      <div v-if="txTotal > pageSize" style="--color-primary: #f07c2a">
        <Pagination v-model:page="page" v-model:limit="pageSize" :total="txTotal" :page-sizes="[8, 15, 30]"
                    @pagination="loadTxList"/>
      </div>
    </div>

    <!-- 充值弹窗 -->
    <div v-if="rechargeOpen" class="fixed inset-0 z-[2000] bg-black/40 flex items-center justify-center p-4"
         @click.self="rechargeOpen = false">
      <div class="w-[440px] max-w-full bg-white rounded-2xl p-6 modal-pop">
        <h3 class="text-base font-extrabold text-warm-text">余额充值</h3>
        <p class="mt-1 text-xs text-warm-sub">当前余额 ¥{{ bizStore.balance.toFixed(2) }}</p>

        <!-- 档位 -->
        <div class="mt-4 grid grid-cols-3 gap-2.5">
          <button
              v-for="op in RECHARGE_OPTIONS"
              :key="op"
              class="rounded-xl border py-3 text-center transition-all"
              :class="amount === op ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
              @click="amount = op; customAmount = ''"
          >
            <span class="text-lg font-extrabold" :class="amount === op ? 'text-warm-primary' : 'text-warm-text'">¥{{
                op
              }}</span>
          </button>
        </div>
        <!-- 自定义 -->
        <div class="mt-3 flex items-center rounded-xl border px-3.5 h-10 transition-colors"
             :class="customFocus ? 'border-warm-primary' : 'border-warm-border'">
          <span class="text-sm text-warm-sub mr-1">自定义</span>
          <input
              v-model="customAmount"
              type="number"
              min="1"
              placeholder="请输入金额"
              class="flex-1 outline-none text-sm text-warm-text placeholder:text-warm-sub bg-transparent"
              @focus="customFocus = true; amount = 0"
              @blur="customFocus = false"
          />
          <span class="text-sm text-warm-sub">元</span>
        </div>

        <!-- 支付方式 -->
        <p class="mt-4 text-xs font-bold text-warm-sub">支付方式</p>
        <div class="mt-2 grid grid-cols-2 gap-2.5">
          <button
              v-for="m in payMethods"
              :key="m.key"
              class="flex items-center gap-2.5 rounded-xl border px-3.5 py-2.5 transition-all"
              :class="payMethod === m.key ? 'border-warm-primary bg-warm-bg' : 'border-warm-border hover:border-warm-accent'"
              @click="payMethod = m.key"
          >
            <span class="u-icon w-4.5 h-4.5" :style="{ color: m.ink }" v-html="iconOf(m.icon)"></span>
            <span class="text-sm font-semibold text-warm-text">{{ m.label }}</span>
          </button>
        </div>

        <div class="mt-5 flex gap-3">
          <button
              class="flex-1 h-10 text-sm font-semibold rounded-xl border border-warm-border text-warm-sub hover:text-warm-text transition-colors"
              @click="rechargeOpen = false">取消
          </button>
          <button
              class="flex-1 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep transition-all disabled:opacity-50"
              :disabled="!finalAmount || rechargeLoading"
              @click="confirmRecharge"
          >{{ rechargeLoading ? '充值中...' : `充值 ¥${finalAmount || 0}` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import {RECHARGE_OPTIONS} from '@/mock'
import {ICONS, iconOf} from './icons'
import useBizStore from '@/stores/modules/bizStore.js'
import {listMyTransactions} from '@/api/biz/wallet.js'
import {ElMessage} from '@/utils/toast.js'
import EmptyState from './components/EmptyState.vue'

const bizStore = useBizStore()

/* 明细类型元数据(adjust 为管理端人工调整) */
const TYPE_META = {
  recharge: {icon: 'wallet', bg: 'bg-warm-bg', cls: 'text-warm-primary'},
  consume: {icon: 'order', bg: 'bg-[#eef3f8]', cls: 'text-[#5b7a99]'},
  refund: {icon: 'refund', bg: 'bg-[#e4f4f2]', cls: 'text-warm-success'},
  reward: {icon: 'gift', bg: 'bg-[#fdeeee]', cls: 'text-warm-danger'},
  adjust: {icon: 'setting', bg: 'bg-warm-bg', cls: 'text-warm-accent'},
}

/* 收支明细(后端分页) */
const page = ref(1)
const pageSize = ref(8)
const txList = ref([])
const txTotal = ref(0)
const txLoading = ref(false)

const loadTxList = () => {
  txLoading.value = true
  listMyTransactions({pageNum: page.value, pageSize: pageSize.value}).then(res => {
    txList.value = res.rows
    txTotal.value = res.total
  }).finally(() => {
    txLoading.value = false
  })
}

onMounted(() => {
  bizStore.loadWallet()
  loadTxList()
})

/* 充值(后端入账) */
const rechargeOpen = ref(false)
const rechargeLoading = ref(false)
const amount = ref(50)
const customAmount = ref('')
const customFocus = ref(false)
const payMethod = ref('alipay')
const payMethods = [
  {key: 'alipay', label: '支付宝', icon: 'check', ink: '#5b7a99'},
  {key: 'wechat', label: '微信支付', icon: 'chat', ink: '#3eb575'},
]

const finalAmount = computed(() => {
  if (customAmount.value) return Math.max(1, Math.floor(Number(customAmount.value) || 0))
  return amount.value
})

const openRecharge = () => {
  amount.value = 50
  customAmount.value = ''
  rechargeOpen.value = true
}

const confirmRecharge = async () => {
  if (!finalAmount.value) return
  rechargeLoading.value = true
  const ok = await bizStore.recharge(finalAmount.value, payMethod.value)
  rechargeLoading.value = false
  if (!ok) return  // 失败原因已由拦截器提示
  ElMessage.success(`充值成功, ¥${finalAmount.value} 已到账`)
  rechargeOpen.value = false
  page.value = 1
  loadTxList()
}
</script>

<style scoped>
.modal-pop {
  animation: modal-pop 0.22s cubic-bezier(0.34, 1.4, 0.64, 1);
}

@keyframes modal-pop {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>