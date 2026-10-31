<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">订单号</label>
        <input v-model="query.orderNo" placeholder="请输入订单号" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">用户名</label>
        <input v-model="query.userName" placeholder="评价用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-36" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">陪玩师</label>
        <input v-model="query.nickName" placeholder="被评价陪玩师昵称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-40" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">星级</label>
        <select v-model="query.rating" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-32">
          <option :value="null">全部</option>
          <option v-for="n in 5" :key="n" :value="n">{{ n }} 星</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">评价时间</label>
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
            <th v-if="!isCompanion" class="w-[55px] px-3 py-3 text-center"><input type="checkbox" :checked="isAllSelected" :disabled="reviewList.length === 0" @change="toggleSelectAll" class="w-4 h-4 rounded"/></th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[190px] px-3 py-3 text-center font-medium text-gray-600">订单信息</th>
            <th class="w-[120px] px-3 py-3 text-center font-medium text-gray-600">评价用户</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">陪玩师</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">星级</th>
            <th class="w-[150px] px-3 py-3 text-center font-medium text-gray-600">评价标签</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">评价内容</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">回复状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">评价时间</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in reviewList" :key="row.orderId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.orderId) }">
            <td v-if="!isCompanion" class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.orderId)" @change="toggleRow(row.orderId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center">
              <p class="font-mono text-xs text-gray-700">{{ row.orderNo }}</p>
              <p class="mt-1 flex items-center justify-center gap-1.5 text-xs text-gray-500">
                <span>{{ row.serviceName }}</span>
                <span class="text-[var(--color-primary)] font-semibold">¥{{ row.amount }}</span>
                <span class="inline-flex px-1.5 py-0.5 rounded-full text-[11px] font-medium" :class="ORDER_STATUS[row.status]?.cls">{{ ORDER_STATUS[row.status]?.label || row.status }}</span>
              </p>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <image-preview v-if="row.avatar" :src="row.avatar" :width="32" :height="32"/>
                <div v-else class="w-8 h-8 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (row.userName || '用')[0] }}</div>
                <span class="font-medium">{{ row.userName }}</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center font-medium text-gray-700">{{ row.nickName }}</td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-0.5">
                <svg v-for="i in 5" :key="i" class="w-3.5 h-3.5" viewBox="0 0 24 24" :fill="i <= row.reviewRating ? '#f59e0b' : '#e5e7eb'"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                <span class="ml-1 text-xs text-gray-500">{{ row.reviewRating }}.0</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="flex flex-wrap gap-1 justify-center">
                <span v-for="t in tagsOf(row)" :key="t" class="inline-block px-1.5 py-0.5 rounded-full text-[11px] font-medium bg-[var(--color-primary-bg)] text-[var(--color-primary)]">{{ t }}</span>
              </div>
              <span v-if="!tagsOf(row).length" class="text-gray-400">-</span>
            </td>
            <td class="px-3 py-3 text-center max-w-[220px] truncate" :title="row.reviewContent || ''">
              <button class="max-w-full truncate hover:text-[var(--color-primary)] transition-colors" @click="handleDetail(row)">{{ row.reviewContent || '未填写文字评价' }}</button>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.reviewReply ? 'text-green-600' : 'text-gray-400'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.reviewReply ? 'bg-green-500' : 'bg-gray-300'"></span>{{ row.reviewReply ? '已回复' : '未回复' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.reviewTime || '-' }}</td>
            <td class="px-3 py-3 text-center whitespace-nowrap">
              <button @click="handleDetail(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-2 font-medium">详情</button>
              <button v-if="!isCompanion" @click="handleReply(row)" class="text-green-600 hover:text-green-700 text-sm mr-2 font-medium">回复</button>
              <button v-if="!isCompanion" @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="reviewList.length === 0"><td :colspan="tableColspan" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 详情对话框(列表行已含全部字段, 直接展示无需再查) -->
    <Modal title="评价详情" v-model="detailOpen" width="680px">
      <div v-if="detail">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-0.5">
            <svg v-for="i in 5" :key="i" class="w-4 h-4" viewBox="0 0 24 24" :fill="i <= detail.reviewRating ? '#f59e0b' : '#e5e7eb'"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          </div>
          <span class="text-xs text-gray-400">{{ detail.reviewTime || '-' }}</span>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <image-preview v-if="detail.avatar" :src="detail.avatar" :width="28" :height="28"/>
          <div v-else class="w-7 h-7 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (detail.userName || '用')[0] }}</div>
          <span class="text-sm font-bold text-gray-800">{{ detail.userName }}</span>
        </div>
        <!-- 被评价订单摘要 -->
        <div class="mt-3 rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div class="flex justify-between"><span class="text-gray-500">订单号</span><span class="font-mono text-xs">{{ detail.orderNo }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">陪玩师</span><span class="font-medium">{{ detail.nickName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">服务项目</span><span class="font-medium">{{ detail.serviceName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">实付金额</span><span class="font-semibold text-[var(--color-primary)]">¥{{ detail.amount }}</span></div>
          <div class="flex justify-between col-span-2"><span class="text-gray-500">订单状态</span><span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="ORDER_STATUS[detail.status]?.cls">{{ ORDER_STATUS[detail.status]?.label || detail.status }}</span></div>
        </div>
        <div class="mt-3 pt-3 border-t border-gray-100 max-h-[160px] overflow-y-auto">
          <p class="text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.reviewContent || '未填写文字评价' }}</p>
          <div v-if="tagsOf(detail).length" class="mt-2 flex flex-wrap gap-1.5">
            <span v-for="t in tagsOf(detail)" :key="t" class="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--color-primary-bg)] text-[var(--color-primary)]">{{ t }}</span>
          </div>
        </div>
        <div v-if="detail.reviewReply" class="mt-3 rounded-lg bg-gray-50 border border-gray-100 px-4 py-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-gray-500">平台回复</span>
            <span class="text-xs text-gray-400">{{ detail.reviewReplyTime || '-' }}</span>
          </div>
          <p class="mt-1.5 text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.reviewReply }}</p>
        </div>
      </div>
      <template #footer>
        <button v-if="!isCompanion" @click="detailToReply" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">{{ detail?.reviewReply ? '修改回复' : '回复' }}</button>
        <button @click="detailOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">关闭</button>
      </template>
    </Modal>

    <!-- 回复对话框 -->
    <Modal title="回复评价" v-model="replyOpen" width="560px">
      <form @submit.prevent="submitReply" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">评价内容</label>
          <div class="flex-1 rounded-lg bg-gray-50 border border-gray-100 px-3 py-2 max-h-[120px] overflow-y-auto">
            <div class="flex items-center gap-0.5">
              <svg v-for="i in 5" :key="i" class="w-3.5 h-3.5" viewBox="0 0 24 24" :fill="i <= (replyRow?.reviewRating || 0) ? '#f59e0b' : '#e5e7eb'"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            </div>
            <p class="mt-1 text-sm leading-6 text-gray-600 whitespace-pre-wrap break-all">{{ replyRow ? (replyRow.reviewContent || '未填写文字评价') : '' }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>回复内容</label>
          <div class="flex-1">
            <textarea v-model="replyForm.reply" rows="5" placeholder="请输入回复内容(255 字以内), 保存后用户可在订单详情与我的评价中查看" class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitReply" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">保存</button>
        <button @click="replyOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {deleteReviewByOrderIds, selectReviewList, updateReviewReply} from "@/api/biz/review.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import useUserStore from "@/stores/modules/userStore.js";

/* 陪玩师视角: 只读查看自己的评价 */
const isCompanion = computed(() => useUserStore().roleName === 'companion')
/* 空数据行跨列数(陪玩师隐藏勾选列) */
const tableColspan = computed(() => isCompanion.value ? 10 : 11)

/* 订单状态元数据(与订单管理一致, 6 态) */
const ORDER_STATUS = {
  pending: {label: '待支付', cls: 'bg-yellow-50 text-yellow-600'},
  booked: {label: '待开始', cls: 'bg-orange-50 text-orange-600'},
  ongoing: {label: '进行中', cls: 'bg-green-50 text-green-600'},
  completed: {label: '已完成', cls: 'bg-gray-100 text-gray-500'},
  refunding: {label: '退款中', cls: 'bg-red-50 text-red-500'},
  cancelled: {label: '已取消', cls: 'bg-gray-100 text-gray-400'},
}

/* 评价标签(逗号分隔字符串 -> 数组) */
const tagsOf = (row) => row.reviewTags ? row.reviewTags.split(',').filter(Boolean) : []

/* 详情对话框(列表行已含全部字段, 直接展示无需再查) */
const detailOpen = ref(false)
const detail = ref(null)
const handleDetail = (row) => {
  detail.value = row
  detailOpen.value = true
}

/* 回复对话框(已回复项打开时预填, 保存覆盖旧回复) */
const replyOpen = ref(false)
const replyRow = ref(null)
const replyForm = reactive({ reply: '' })
const handleReply = (row) => {
  replyRow.value = row
  replyForm.reply = row.reviewReply || ''
  replyOpen.value = true
}
/* 详情弹窗内跳转回复 */
const detailToReply = () => {
  handleReply(detail.value)
  detailOpen.value = false
}

const submitReply = () => {
  if (!replyForm.reply.trim()) {
    ElMessage.warning('回复内容不能为空')
    return
  }
  if (replyForm.reply.trim().length > 255) {
    ElMessage.warning('回复内容不能超过 255 字')
    return
  }
  updateReviewReply({
    orderId: replyRow.value.orderId,
    reply: replyForm.reply.trim(),
  }).then(() => {
    ElMessage.success(replyRow.value.reviewReply ? '回复已更新' : '回复成功')
    replyOpen.value = false
    getList()
  })
}

/* 删除评价(行删除/勾选批量删除; 清空评价字段, 订单保留) */
const handleDelete = (row) => {
  const orderIds = row ? [row.orderId] : ids.value
  if (!orderIds || orderIds.length === 0) return
  ElMessageBox.confirm('删除将清空该订单的评价及回复, 订单记录保留, 用户可重新评价。是否确认删除?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteReviewByOrderIds(orderIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const query = ref({ pageNum: 1, pageSize: 10, orderNo: '', userName: '', nickName: '', rating: null, beginTime: '', endTime: '' })
const reviewList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => reviewList.value.length > 0 && selectedIds.size === reviewList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) reviewList.value.forEach(r => selectedIds.delete(r.orderId))
  else reviewList.value.forEach(r => selectedIds.add(r.orderId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => {
  query.value.orderNo = ''; query.value.userName = ''; query.value.nickName = ''
  query.value.rating = null; query.value.beginTime = ''; query.value.endTime = ''
  handleQuery()
}

const getList = () => {
  loading.value = true
  /* 结束日期补 23:59:59, 保证含当天全部评价 */
  const params = { ...query.value }
  if (params.endTime) params.endTime = `${params.endTime} 23:59:59`
  selectReviewList(params).then(res => {
    reviewList.value = res.rows
    total.value = res.total
    selectedIds.clear(); syncSelected()
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>