<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">订单号</label>
        <input v-model="query.orderNo" placeholder="请输入订单号" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-48" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">用户名</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-36" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">陪玩师</label>
        <input v-model="query.nickName" placeholder="请输入陪玩师昵称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-36" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-32">
          <option value="">全部</option>
          <option v-for="(m, k) in STATUS_META" :key="k" :value="k">{{ m.label }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">下单时间</label>
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

    <!-- 操作按钮(陪玩师只读自己的订单, 不展示删除) -->
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
            <th v-if="!isCompanion" class="w-[55px] px-3 py-3 text-center"><input type="checkbox" :checked="isAllSelected" :disabled="orderList.length === 0" @change="toggleSelectAll" class="w-4 h-4 rounded"/></th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[180px] px-3 py-3 text-center font-medium text-gray-600">订单号</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">用户</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">陪玩师</th>
            <th class="w-[150px] px-3 py-3 text-center font-medium text-gray-600">服务</th>
            <th class="w-[170px] px-3 py-3 text-center font-medium text-gray-600">服务时间</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">金额</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">支付方式</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">下单时间</th>
            <th class="w-[170px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in orderList" :key="row.orderId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.orderId) }">
            <td v-if="!isCompanion" class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.orderId)" @change="toggleRow(row.orderId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-mono text-xs text-gray-700">{{ row.orderNo }}</td>
            <td class="px-3 py-3 text-center font-medium">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <image-preview v-if="row.avatar" :src="row.avatar" :width="32" :height="32"/>
                <div v-else class="w-8 h-8 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (row.nickName || '陪')[0] }}</div>
                <span class="font-medium">{{ row.nickName }}</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center">
              <p class="font-medium">{{ row.serviceName }}</p>
              <p class="text-xs text-gray-400">¥{{ row.price }} × {{ row.hours }}小时</p>
            </td>
            <td class="px-3 py-3 text-center text-gray-600 text-xs">{{ serviceTimeText(row) }}</td>
            <td class="px-3 py-3 text-center">
              <p class="font-bold" :class="row.status === 'cancelled' ? 'text-gray-400' : 'text-[var(--color-primary)]'">¥{{ row.amount }}</p>
              <p v-if="row.couponAmount" class="text-xs text-red-400">优惠 ¥{{ row.couponAmount }}</p>
            </td>
            <td class="px-3 py-3 text-center text-gray-600">{{ payMethodText(row.payMethod) }}</td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="STATUS_META[row.status]?.cls">{{ STATUS_META[row.status]?.label || row.status }}</span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center whitespace-nowrap">
              <button @click="handleDetail(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-2 font-medium">详情</button>
              <button v-if="row.status === 'booked'" @click="handleStart(row)" class="text-green-600 hover:text-green-700 text-sm mr-2 font-medium">开始服务</button>
              <button v-if="!isCompanion && ['pending', 'booked'].includes(row.status)" @click="handleCancel(row)" class="text-orange-500 hover:text-orange-600 text-sm mr-2 font-medium">取消</button>
              <button v-if="!isCompanion && row.status === 'refunding'" @click="handleRefund(row)" class="text-red-500 hover:text-red-600 text-sm mr-2 font-medium">确认退款</button>
              <button v-if="!isCompanion && deletable(row)" @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="orderList.length === 0"><td :colspan="tableColspan" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 订单详情对话框 -->
    <Modal :title="'订单详情'" v-model="detailOpen" width="640px">
      <div v-if="detail" class="space-y-4">
        <!-- 状态 + 金额头 -->
        <div class="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
          <span class="inline-flex px-2.5 py-1 rounded-full text-xs font-medium" :class="STATUS_META[detail.status]?.cls">{{ STATUS_META[detail.status]?.label }}</span>
          <span class="text-lg font-extrabold" :class="detail.status === 'cancelled' ? 'text-gray-400' : 'text-[var(--color-primary)]'">¥{{ detail.amount }}</span>
        </div>
        <!-- 基本信息 -->
        <div class="grid grid-cols-2 gap-x-6 gap-y-2.5 text-sm">
          <div class="flex justify-between"><span class="text-gray-500">订单号</span><span class="font-mono text-xs">{{ detail.orderNo }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">下单用户</span><span class="font-medium">{{ detail.userName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">陪玩师</span><span class="font-medium">{{ detail.nickName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">服务项目</span><span class="font-medium">{{ detail.serviceName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">单价/时长</span><span>¥{{ detail.price }}/时 × {{ detail.hours }}小时</span></div>
          <div class="flex justify-between"><span class="text-gray-500">服务时间</span><span>{{ serviceTimeText(detail) }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">订单原价</span><span>¥{{ detail.grossAmount }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">优惠券</span><span class="text-red-500">{{ detail.couponName ? `${detail.couponName} -¥${detail.couponAmount}` : '未使用' }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">实付金额</span><span class="font-bold">¥{{ detail.amount }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">支付方式</span><span>{{ payMethodText(detail.payMethod) }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">下单时间</span><span>{{ detail.createTime || '-' }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">支付时间</span><span>{{ detail.payTime || '-' }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">开始时间</span><span>{{ detail.startTime || '-' }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">完成时间</span><span>{{ detail.endTime || '-' }}</span></div>
        </div>
        <!-- 备注 / 取消原因 -->
        <div v-if="detail.note" class="text-sm">
          <p class="text-gray-500 mb-1">需求备注</p>
          <p class="bg-gray-50 rounded-lg px-4 py-2.5 text-gray-700 leading-6">{{ detail.note }}</p>
        </div>
        <div v-if="detail.cancelReason" class="text-sm">
          <p class="text-gray-500 mb-1">取消原因</p>
          <p class="bg-red-50 rounded-lg px-4 py-2.5 text-red-500 leading-6">{{ detail.cancelReason }}</p>
        </div>
        <!-- 评价 -->
        <div v-if="detail.reviewRating" class="text-sm">
          <p class="text-gray-500 mb-1">用户评价 <span class="text-amber-500 font-bold">{{ '★'.repeat(detail.reviewRating) }}</span> <span class="text-gray-400 text-xs ml-1">{{ detail.reviewTime }}</span></p>
          <div v-if="reviewTags(detail)" class="flex flex-wrap gap-1.5 mb-1.5">
            <span v-for="t in reviewTags(detail)" :key="t" class="px-2 py-0.5 rounded text-xs bg-[var(--color-primary-bg)] text-[var(--color-primary)]">{{ t }}</span>
          </div>
          <p class="bg-gray-50 rounded-lg px-4 py-2.5 text-gray-700 leading-6">{{ detail.reviewContent || '-' }}</p>
        </div>
      </div>
      <template #footer>
        <button @click="detailOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">关闭</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {cancelOrder, confirmRefund, deleteOrderByOrderIds, selectOrderList, startOrder} from "@/api/biz/order.js";
import Pagination from "@/components/Pagination/index.vue";
import Modal from "@/components/Modal/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import useUserStore from "@/stores/modules/userStore.js";

/* 陪玩师视角: 只读自己的订单(可"开始服务"自己的订单) */
const isCompanion = computed(() => useUserStore().roleName === 'companion')
/* 空数据行跨列数(陪玩师隐藏勾选列) */
const tableColspan = computed(() => isCompanion.value ? 11 : 12)

/* 订单状态元数据(标签样式, 6 态) */
const STATUS_META = {
  pending: {label: '待支付', cls: 'bg-yellow-50 text-yellow-600'},
  booked: {label: '待开始', cls: 'bg-orange-50 text-orange-600'},
  ongoing: {label: '进行中', cls: 'bg-green-50 text-green-600'},
  completed: {label: '已完成', cls: 'bg-gray-100 text-gray-500'},
  refunding: {label: '退款中', cls: 'bg-red-50 text-red-500'},
  cancelled: {label: '已取消', cls: 'bg-gray-100 text-gray-400'},
}
/* 支付方式文案 */
const payMethodText = (m) => ({balance: '余额支付', wechat: '微信支付', alipay: '支付宝'}[m] || '未支付')
/* 服务时间描述: '2026-10-18 20:00 ~ 22:00' */
const serviceTimeText = (row) => {
  const p = (n) => String(n ?? 0).padStart(2, '0')
  return `${row.serviceDate} ${p(row.startHour)}:00 ~ ${p(row.startHour + row.hours)}:00`
}
/* 评价标签拆分 */
const reviewTags = (row) => row.reviewTags ? row.reviewTags.split(',').filter(Boolean) : []
/* 仅已取消/已完成订单可删除(可勾选) */
const deletable = (row) => ['cancelled', 'completed'].includes(row.status)

const detailOpen = ref(false)
const detail = ref(null)

const handleDetail = (row) => {
  detail.value = row
  detailOpen.value = true
}

/* 开始服务(booked -> ongoing) */
const handleStart = (row) => {
  ElMessageBox.confirm(`确认开始订单 ${row.orderNo} 的服务? 开始后订单进入进行中状态`, '开始服务', {
    confirmButtonText: '确认开始', cancelButtonText: '取消', type: 'info',
  }).then(() => {
    startOrder(row.orderId).then(() => {
      ElMessage.success('服务已开始')
      getList()
    })
  }).catch(() => {})
}

/* 取消订单(pending 直接取消, booked 取消并退款, prompt 输入原因) */
const handleCancel = (row) => {
  const paid = row.status === 'booked'
  ElMessageBox.prompt(paid ? '已支付订单取消后将原路退款(余额即时到账), 请输入取消原因' : '请输入取消原因', '取消订单', {
    confirmButtonText: '确认取消', cancelButtonText: '再想想', type: 'warning',
    inputPlaceholder: '取消原因(留空默认为 管理员取消)',
  }).then(({value}) => {
    cancelOrder({orderId: row.orderId, cancelReason: value || ''}).then(() => {
      ElMessage.success('订单已取消')
      getList()
    })
  }).catch(() => {})
}

/* 确认退款(refunding -> cancelled, 余额退回+券返还) */
const handleRefund = (row) => {
  ElMessageBox.confirm(`确认退款 ¥${row.amount}? 余额支付订单将原路退回用户钱包`, '确认退款', {
    confirmButtonText: '确认退款', cancelButtonText: '取消', type: 'warning',
  }).then(() => {
    confirmRefund(row.orderId).then(() => {
      ElMessage.success('退款已完成')
      getList()
    })
  }).catch(() => {})
}

/* 删除订单(行删除/勾选批量删除, 仅已取消/已完成) */
const handleDelete = (row) => {
  const orderIds = row ? [row.orderId] : ids.value
  if (!orderIds || orderIds.length === 0) return
  ElMessageBox.confirm('删除后订单记录将不可恢复, 是否确认删除?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteOrderByOrderIds(orderIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const query = ref({ pageNum: 1, pageSize: 10, orderNo: '', userName: '', nickName: '', status: '', beginTime: '', endTime: '' })
const orderList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => orderList.value.length > 0 && selectedIds.size === orderList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) orderList.value.forEach(r => selectedIds.delete(r.orderId))
  else orderList.value.forEach(r => selectedIds.add(r.orderId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => {
  query.value.orderNo = ''; query.value.userName = ''; query.value.nickName = ''
  query.value.status = ''; query.value.beginTime = ''; query.value.endTime = ''
  handleQuery()
}

const getList = () => {
  loading.value = true
  /* 结束日期补 23:59:59, 保证含当天全部订单 */
  const params = { ...query.value }
  if (params.endTime) params.endTime = `${params.endTime} 23:59:59`
  selectOrderList(params).then(res => {
    orderList.value = res.rows
    total.value = res.total
    selectedIds.clear(); syncSelected()
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>