<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">打赏用户</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">陪玩昵称</label>
        <input v-model="query.nickName" placeholder="请输入陪玩昵称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">礼物名称</label>
        <input v-model="query.giftName" placeholder="请输入礼物名称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">打赏时间</label>
        <input v-model="query.beginTime" type="date" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-40"/>
        <span class="text-gray-400">至</span>
        <input v-model="query.endTime" type="date" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-40"/>
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

    <!-- 操作按钮(陪玩师只读, 不展示删除) -->
    <div v-if="!isCompanion" class="flex gap-2 mb-2">
      <button :disabled="multiple" @click="handleDelete()" class="h-9 px-4 rounded-lg text-sm font-medium transition-colors flex items-center gap-1" :class="multiple ? 'text-gray-400 border border-gray-200 bg-gray-50 cursor-not-allowed' : 'text-red-500 border border-red-400 bg-white hover:bg-red-50'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>删除
      </button>
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
            <th v-if="!isCompanion" class="w-[55px] px-3 py-3 text-center"><input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="w-4 h-4 rounded"/></th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[150px] px-3 py-3 text-center font-medium text-gray-600">打赏用户</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">陪玩师</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">礼物</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">金额</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">打赏时间</th>
            <th v-if="!isCompanion" class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in rewardList" :key="row.rewardId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.rewardId) }">
            <td v-if="!isCompanion" class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.rewardId)" @change="toggleRow(row.rewardId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <image-preview v-if="row.avatar" :src="row.avatar" :width="32" :height="32"/>
                <div v-else class="w-8 h-8 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (row.nickName || '陪')[0] }}</div>
                <span class="font-medium">{{ row.nickName }}</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <image-preview v-if="row.giftImage" :src="row.giftImage" :width="32" :height="32"/>
                <div v-else class="w-8 h-8 rounded-lg bg-orange-50 text-orange-500 text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (row.giftName || '礼')[0] }}</div>
                <span class="font-medium">{{ row.giftName }}</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center font-bold text-red-500">¥{{ row.amount }}</td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td v-if="!isCompanion" class="px-3 py-3 text-center">
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="rewardList.length === 0"><td :colspan="tableColspan" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {deleteRewardByIds, selectRewardList} from "@/api/biz/reward.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import useUserStore from "@/stores/modules/userStore.js";

/* 陪玩师视角: 只读查看打赏给自己的记录 */
const isCompanion = computed(() => useUserStore().roleName === 'companion')
/* 空数据行跨列数(陪玩师隐藏勾选/操作两列) */
const tableColspan = computed(() => isCompanion.value ? 6 : 8)

const query = ref({ pageNum: 1, pageSize: 10, userName: '', nickName: '', giftName: '', beginTime: '', endTime: '' })
const rewardList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => rewardList.value.length > 0 && selectedIds.size === rewardList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) rewardList.value.forEach(r => selectedIds.delete(r.rewardId))
  else rewardList.value.forEach(r => selectedIds.add(r.rewardId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; query.value.nickName = ''; query.value.giftName = ''; query.value.beginTime = ''; query.value.endTime = ''; handleQuery() }

const handleDelete = (row) => {
  const rewardIds = row ? [row.rewardId] : ids.value
  if (!rewardIds || rewardIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的打赏记录?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteRewardByIds(rewardIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const getList = () => {
  loading.value = true
  /* 结束日期补 23:59:59, 保证含当天全部打赏 */
  const params = { ...query.value }
  if (params.endTime) params.endTime = `${params.endTime} 23:59:59`
  selectRewardList(params).then(res => {
    rewardList.value = res.rows
    total.value = res.total
    selectedIds.clear()
    syncSelected()
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>