<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">类型</label>
        <select v-model="query.txType" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option value="">全部</option>
          <option value="recharge">充值</option>
          <option value="consume">消费</option>
          <option value="refund">退款</option>
          <option value="reward">打赏</option>
          <option value="adjust">人工调整</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">变动时间</label>
        <input v-model="query.beginTime" type="date" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-40"/>
        <span class="text-gray-400">至</span>
        <input v-model="query.endTime" type="date" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-40"/>
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

    <!-- 数据表格(只读审计, 流水不可编辑/删除) -->
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
            <th class="w-[140px] px-3 py-3 text-center font-medium text-gray-600">用户</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">类型</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">变动金额</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">变动后余额</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">备注</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">操作人</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in txList" :key="row.txId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center"><span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="typeMetaOf(row.type).cls">{{ typeMetaOf(row.type).label }}</span></td>
            <td class="px-3 py-3 text-center font-bold" :class="row.amount >= 0 ? 'text-green-600' : 'text-red-500'">{{ row.amount >= 0 ? '+' : '' }}{{ row.amount }}</td>
            <td class="px-3 py-3 text-center text-gray-600">¥{{ row.balanceAfter }}</td>
            <td class="px-3 py-3 text-center text-gray-500 max-w-[220px] truncate" :title="row.note">{{ row.note || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.operator || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime }}</td>
          </tr>
          <tr v-if="txList.length === 0"><td colspan="8" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>
  </div>
</template>

<script setup>
import {onMounted, ref} from "vue";
import {selectWalletTransactionList} from "@/api/biz/wallet.js";
import Pagination from "@/components/Pagination/index.vue";

/* 流水类型元数据(标签样式) */
const TYPE_META = {
  recharge: {label: '充值', cls: 'bg-green-50 text-green-600'},
  consume: {label: '消费', cls: 'bg-blue-50 text-blue-600'},
  refund: {label: '退款', cls: 'bg-teal-50 text-teal-600'},
  reward: {label: '打赏', cls: 'bg-orange-50 text-orange-600'},
  adjust: {label: '人工调整', cls: 'bg-purple-50 text-purple-600'},
}
const typeMetaOf = (type) => TYPE_META[type] || {label: type, cls: 'bg-gray-50 text-gray-500'}

const query = ref({ pageNum: 1, pageSize: 10, userName: '', txType: '', beginTime: '', endTime: '' })
const txList = ref([])
const total = ref(0)
const loading = ref(false)

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; query.value.txType = ''; query.value.beginTime = ''; query.value.endTime = ''; handleQuery() }

const getList = () => {
  loading.value = true
  /* 结束日期补 23:59:59, 保证含当天全部流水 */
  const params = { ...query.value }
  if (params.endTime) params.endTime = `${params.endTime} 23:59:59`
  selectWalletTransactionList(params).then(res => {
    txList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>