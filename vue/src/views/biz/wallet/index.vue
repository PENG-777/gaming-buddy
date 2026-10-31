<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex gap-2">
        <button @click="handleQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-1" :class="loading ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
          <svg v-if="!loading" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <svg v-else class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>
          {{ loading ? '查询中...' : '搜索' }}
        </button>
        <button @click="resetQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors flex items-center gap-1" :class="{ 'opacity-50 cursor-not-allowed': loading }">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>重置
        </button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg relative">
      <div v-if="loading" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center rounded-lg">
        <div class="flex flex-col items-center gap-2">
          <svg class="w-8 h-8 animate-spin text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>
          <span class="text-sm text-gray-500">加载中...</span>
        </div>
      </div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">用户</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">当前余额</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">累计充值</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">累计支出</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">最近变动时间</th>
            <th class="w-[140px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in walletList" :key="row.userId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center font-bold text-red-500">¥{{ row.balance }}</td>
            <td class="px-3 py-3 text-center text-green-600">¥{{ row.totalRecharge ?? 0 }}</td>
            <td class="px-3 py-3 text-center text-gray-600">¥{{ row.totalExpense ?? 0 }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.lastTime || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleAdjust(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">调整余额</button>
              <button @click="handleShowTx(row)" class="text-green-600 hover:text-green-700 text-sm font-medium">流水</button>
            </td>
          </tr>
          <tr v-if="walletList.length === 0"><td colspan="7" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 调整余额对话框 -->
    <Modal :title="`调整余额 - ${adjustRow?.userName || ''}`" v-model="adjustOpen" width="480px">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <label class="w-20 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>调整方式</label>
          <div class="flex-1 flex items-center gap-4">
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="1" v-model="adjustForm.direction" class="accent-[var(--color-primary)]"/>增加
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="-1" v-model="adjustForm.direction" class="accent-[var(--color-primary)]"/>扣减
            </label>
            <span class="text-xs text-gray-400">当前余额 ¥{{ adjustRow?.balance ?? 0 }}</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <label class="w-20 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>金额(元)</label>
          <input v-model="adjustForm.amount" type="number" placeholder="请输入正整数金额" class="flex-1 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>调整原因</label>
          <textarea v-model="adjustForm.note" rows="3" placeholder="请输入调整原因(如 客服补偿/活动赠送/异常冲正), 将记入流水留痕" class="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
        </div>
      </div>
      <template #footer>
        <button @click="submitAdjust" :disabled="adjustLoading" class="h-9 px-5 rounded-lg text-sm font-medium text-white transition-colors" :class="adjustLoading ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">{{ adjustLoading ? '提交中...' : '确认调整' }}</button>
        <button @click="adjustOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>

    <!-- 用户流水对话框 -->
    <Modal :title="`钱包流水 - ${txRow?.userName || ''}`" v-model="txOpen" width="720px">
      <div class="overflow-x-auto border border-gray-200 rounded-lg">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="w-[90px] px-3 py-2.5 text-center font-medium text-gray-600">类型</th>
              <th class="w-[100px] px-3 py-2.5 text-center font-medium text-gray-600">变动金额</th>
              <th class="w-[100px] px-3 py-2.5 text-center font-medium text-gray-600">变动后余额</th>
              <th class="px-3 py-2.5 text-center font-medium text-gray-600">备注</th>
              <th class="w-[150px] px-3 py-2.5 text-center font-medium text-gray-600">时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in txList" :key="t.txId" class="border-t border-gray-100">
              <td class="px-3 py-2.5 text-center"><span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="typeMetaOf(t.type).cls">{{ typeMetaOf(t.type).label }}</span></td>
              <td class="px-3 py-2.5 text-center font-bold" :class="t.amount >= 0 ? 'text-green-600' : 'text-red-500'">{{ t.amount >= 0 ? '+' : '' }}{{ t.amount }}</td>
              <td class="px-3 py-2.5 text-center text-gray-600">¥{{ t.balanceAfter }}</td>
              <td class="px-3 py-2.5 text-center text-gray-500 max-w-[220px] truncate" :title="t.note">{{ t.note || '-' }}</td>
              <td class="px-3 py-2.5 text-center text-gray-500">{{ t.createTime }}</td>
            </tr>
            <tr v-if="txList.length === 0"><td colspan="5" class="px-3 py-10 text-center text-gray-400">暂无流水</td></tr>
          </tbody>
        </table>
      </div>
      <pagination :total="txTotal" v-model:page="txQuery.pageNum" v-model:limit="txQuery.pageSize" :page-sizes="[10]" @pagination="getTxList"/>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive} from "vue";
import {adjustWallet, selectWalletList, selectWalletTransactionList} from "@/api/biz/wallet.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage} from "@/utils/toast.js";

/* 流水类型元数据(标签样式) */
const TYPE_META = {
  recharge: {label: '充值', cls: 'bg-green-50 text-green-600'},
  consume: {label: '消费', cls: 'bg-blue-50 text-blue-600'},
  refund: {label: '退款', cls: 'bg-teal-50 text-teal-600'},
  reward: {label: '打赏', cls: 'bg-orange-50 text-orange-600'},
  adjust: {label: '人工调整', cls: 'bg-purple-50 text-purple-600'},
}
const typeMetaOf = (type) => TYPE_META[type] || {label: type, cls: 'bg-gray-50 text-gray-500'}

/* 余额列表 */
const query = ref({ pageNum: 1, pageSize: 10, userName: '' })
const walletList = ref([])
const total = ref(0)
const loading = ref(false)

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; handleQuery() }

const getList = () => {
  loading.value = true
  selectWalletList(query.value).then(res => {
    walletList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

/* 调整余额 */
const adjustOpen = ref(false)
const adjustLoading = ref(false)
const adjustRow = ref(null)
const adjustForm = reactive({ direction: 1, amount: '', note: '' })

const handleAdjust = (row) => {
  adjustRow.value = row
  Object.assign(adjustForm, { direction: 1, amount: '', note: '' })
  adjustOpen.value = true
}

const submitAdjust = () => {
  const amount = Number(adjustForm.amount)
  if (!/^\d+$/.test(String(adjustForm.amount)) || amount < 1) {
    ElMessage.warning('金额必须为正整数')
    return
  }
  if (!adjustForm.note || !adjustForm.note.trim()) {
    ElMessage.warning('请输入调整原因')
    return
  }
  adjustLoading.value = true
  adjustWallet({
    userId: adjustRow.value.userId,
    amount: adjustForm.direction * amount,
    note: adjustForm.note.trim()
  }).then(() => {
    ElMessage.success('调整成功')
    adjustOpen.value = false
    getList()
  }).finally(() => { adjustLoading.value = false })
}

/* 查看用户流水 */
const txOpen = ref(false)
const txRow = ref(null)
const txList = ref([])
const txTotal = ref(0)
const txQuery = reactive({ pageNum: 1, pageSize: 10 })

const handleShowTx = (row) => {
  txRow.value = row
  txQuery.pageNum = 1
  txOpen.value = true
  getTxList()
}

const getTxList = () => {
  selectWalletTransactionList({ ...txQuery, userId: txRow.value.userId }).then(res => {
    txList.value = res.rows
    txTotal.value = res.total
  })
}

onMounted(() => getList())
</script>