<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">券名称</label>
        <input v-model="query.couponName" placeholder="请输入券名称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option :value="0">未使用</option>
          <option :value="1">已使用</option>
          <option :value="2">已过期</option>
        </select>
      </div>
      <div class="flex gap-2">
        <button @click="handleQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-1" :class="loading ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
          <svg v-if="!loading" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <svg v-else class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
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
          <svg class="w-8 h-8 animate-spin text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          <span class="text-sm text-gray-500">加载中...</span>
        </div>
      </div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[140px] px-3 py-3 text-center font-medium text-gray-600">用户</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">券名称</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">面额</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">使用门槛</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">领取时间</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">过期时间</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">使用时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in userCouponList" :key="row.id" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'opacity-70': statusOf(row).key !== 'usable' }">
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.couponName }}</td>
            <td class="px-3 py-3 text-center font-bold text-red-500">¥{{ row.amount }}</td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.threshold > 0 ? `满${row.threshold}元` : '无门槛' }}</td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="statusOf(row).text">
                <span class="w-1.5 h-1.5 rounded-full" :class="statusOf(row).dot"></span>{{ statusOf(row).label }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.receiveTime || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.expireTime || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.useTime || '-' }}</td>
          </tr>
          <tr v-if="userCouponList.length === 0"><td colspan="9" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>
  </div>
</template>

<script setup>
import {onMounted, ref} from "vue";
import {selectUserCouponList} from "@/api/biz/coupon.js";
import Pagination from "@/components/Pagination/index.vue";

const query = ref({ pageNum: 1, pageSize: 10, userName: '', couponName: '', status: null })
const userCouponList = ref([])
const total = ref(0)
const loading = ref(false)

/* 行状态三态渲染: 库内 status=1 已使用; status=0 且 expireTime 已过为已过期; 其余未使用 */
const statusOf = (row) => {
  if (row.status === 1) return { key: 'used', label: '已使用', text: 'text-gray-400', dot: 'bg-gray-300' }
  if (row.expireTime && new Date(row.expireTime.replace(/-/g, '/')).getTime() < Date.now())
    return { key: 'expired', label: '已过期', text: 'text-gray-400', dot: 'bg-gray-300' }
  return { key: 'usable', label: '未使用', text: 'text-green-600', dot: 'bg-green-500' }
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; query.value.couponName = ''; query.value.status = null; handleQuery() }

const getList = () => {
  loading.value = true
  selectUserCouponList(query.value).then(res => {
    userCouponList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>