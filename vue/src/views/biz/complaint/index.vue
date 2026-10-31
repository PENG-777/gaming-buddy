<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">订单号</label>
        <input v-model="query.orderNo" placeholder="请输入订单号" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名</label>
        <input v-model="query.userName" placeholder="投诉用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-36" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">陪玩师</label>
        <input v-model="query.nickName" placeholder="被投诉陪玩师昵称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-40" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">类型</label>
        <select v-model="query.complaintType" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-40">
          <option :value="null">全部</option>
          <option v-for="t in COMPLAINT_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-32">
          <option :value="null">全部</option>
          <option value="0">待处理</option>
          <option value="1">已处理</option>
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
            <th class="w-[200px] px-3 py-3 text-center font-medium text-gray-600">订单信息</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">投诉用户</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">被投诉陪玩师</th>
            <th class="w-[140px] px-3 py-3 text-center font-medium text-gray-600">投诉类型</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">投诉内容</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">提交时间</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">处理结果</th>
            <th v-if="!isCompanion" class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in complaintList" :key="row.complaintId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.complaintId) }">
            <td v-if="!isCompanion" class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.complaintId)" @change="toggleRow(row.complaintId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center">
              <p class="font-mono text-xs text-gray-700">{{ row.orderNo }}</p>
              <p class="mt-1 flex items-center justify-center gap-1.5 text-xs text-gray-500">
                <span>{{ row.serviceName }}</span>
                <span class="text-[var(--color-primary)] font-semibold">¥{{ row.amount }}</span>
                <span class="inline-flex px-1.5 py-0.5 rounded-full text-[11px] font-medium" :class="ORDER_STATUS[row.orderStatus]?.cls">{{ ORDER_STATUS[row.orderStatus]?.label || row.orderStatus }}</span>
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
              <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="typeStyle(row.complaintType)">{{ row.complaintType }}</span>
            </td>
            <td class="px-3 py-3 text-center max-w-[220px] truncate" :title="row.content">
              <button class="max-w-full truncate hover:text-[var(--color-primary)] transition-colors" @click="handleDetail(row)">{{ row.content }}</button>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.status === 0 ? 'text-amber-600' : 'text-green-600'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === 0 ? 'bg-amber-500' : 'bg-green-500'"></span>{{ row.status === 0 ? '待处理' : '已处理' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <span v-if="row.handleResult" class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="resultStyle(row.handleResult)">{{ row.handleResult }}</span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td v-if="!isCompanion" class="px-3 py-3 text-center">
              <button v-if="row.status === 0" @click="handleHandle(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">处理</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium" :class="{ 'ml-3': row.status !== 0 }">删除</button>
            </td>
          </tr>
          <tr v-if="complaintList.length === 0"><td :colspan="tableColspan" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 详情对话框(列表行已含全部字段, 直接展示无需再查) -->
    <Modal title="投诉详情" v-model="detailOpen" width="680px">
      <div v-if="detail">
        <div class="flex items-center gap-3">
          <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="typeStyle(detail.complaintType)">{{ detail.complaintType }}</span>
          <span class="inline-flex items-center gap-1.5 text-sm" :class="detail.status === 0 ? 'text-amber-600' : 'text-green-600'">
            <span class="w-1.5 h-1.5 rounded-full" :class="detail.status === 0 ? 'bg-amber-500' : 'bg-green-500'"></span>{{ detail.status === 0 ? '待处理' : '已处理' }}
          </span>
          <span class="ml-auto flex items-center gap-1 text-xs text-gray-400">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>{{ detail.createTime || '-' }}
          </span>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <image-preview v-if="detail.avatar" :src="detail.avatar" :width="28" :height="28"/>
          <div v-else class="w-7 h-7 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (detail.userName || '用')[0] }}</div>
          <span class="text-sm font-bold text-gray-800">{{ detail.userName }}</span>
        </div>
        <!-- 被投诉订单摘要 -->
        <div class="mt-3 rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div class="flex justify-between"><span class="text-gray-500">订单号</span><span class="font-mono text-xs">{{ detail.orderNo }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">陪玩师</span><span class="font-medium">{{ detail.nickName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">服务项目</span><span class="font-medium">{{ detail.serviceName }}</span></div>
          <div class="flex justify-between"><span class="text-gray-500">实付金额</span><span class="font-semibold text-[var(--color-primary)]">¥{{ detail.amount }}</span></div>
          <div class="flex justify-between col-span-2"><span class="text-gray-500">订单状态</span><span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="ORDER_STATUS[detail.orderStatus]?.cls">{{ ORDER_STATUS[detail.orderStatus]?.label || detail.orderStatus }}</span></div>
        </div>
        <div class="mt-3 pt-3 border-t border-gray-100 max-h-[160px] overflow-y-auto">
          <p class="text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.content }}</p>
        </div>
        <div v-if="detail.status === 1" class="mt-3 rounded-lg bg-gray-50 border border-gray-100 px-4 py-3">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-2">
              <span class="text-xs font-bold text-gray-500">处理结果</span>
              <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="resultStyle(detail.handleResult)">{{ detail.handleResult }}</span>
            </span>
            <span class="text-xs text-gray-400">{{ detail.handleTime || '-' }}</span>
          </div>
          <p v-if="detail.reply" class="mt-1.5 text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.reply }}</p>
        </div>
      </div>
      <template #footer>
        <button v-if="!isCompanion && detail && detail.status === 0" @click="detailToHandle" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">处理</button>
        <button @click="detailOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">关闭</button>
      </template>
    </Modal>

    <!-- 处理对话框 -->
    <Modal title="处理投诉" v-model="handleOpen" width="560px">
      <form @submit.prevent="submitHandle" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">投诉内容</label>
          <div class="flex-1 rounded-lg bg-gray-50 border border-gray-100 px-3 py-2 max-h-[120px] overflow-y-auto">
            <p class="text-sm leading-6 text-gray-600 whitespace-pre-wrap break-all">{{ handleRow ? handleRow.content : '' }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <label class="w-20 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>处理结果</label>
          <select v-model="handleForm.handleResult" class="flex-1 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white">
            <option v-for="r in HANDLE_RESULTS" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">处理说明</label>
          <div class="flex-1">
            <textarea v-model="handleForm.reply" rows="5" placeholder="请输入处理说明(500 字以内, 选填), 保存后该投诉将标记为已处理" class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
          </div>
        </div>
        <div v-if="handleForm.handleResult === '全额退款'" class="flex items-start gap-2 rounded-lg bg-red-50 border border-red-100 px-3 py-2.5 text-xs leading-5 text-red-500">
          <svg class="w-4 h-4 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>保存后关联订单将被取消, 实付金额原路退回(余额支付退回钱包并记录退款流水, 已用优惠券自动返还), 该投诉不可再次处理。</span>
        </div>
      </form>
      <template #footer>
        <button @click="submitHandle" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">保存</button>
        <button @click="handleOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {deleteComplaintByComplaintIds, selectComplaintList, updateComplaint} from "@/api/biz/complaint.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import useUserStore from "@/stores/modules/userStore.js";

/* 陪玩师视角: 只读查看针对自己的投诉 */
const isCompanion = computed(() => useUserStore().roleName === 'companion')
/* 空数据行跨列数(陪玩师隐藏勾选/操作两列) */
const tableColspan = computed(() => isCompanion.value ? 9 : 11)

/* 投诉类型(与后端白名单/用户端一致); 处理结果(管理端处理弹窗下拉) */
const COMPLAINT_TYPES = ['服务态度差', '迟到未提供服务', '技术水平与描述不符', '诱导私下交易', '言语不当', '其他问题']
const HANDLE_RESULTS = ['警告陪玩师', '全额退款', '驳回投诉', '其他']

/* 订单状态元数据(与订单管理一致, 6 态) */
const ORDER_STATUS = {
  pending: {label: '待支付', cls: 'bg-yellow-50 text-yellow-600'},
  booked: {label: '待开始', cls: 'bg-orange-50 text-orange-600'},
  ongoing: {label: '进行中', cls: 'bg-green-50 text-green-600'},
  completed: {label: '已完成', cls: 'bg-gray-100 text-gray-500'},
  refunding: {label: '退款中', cls: 'bg-red-50 text-red-500'},
  cancelled: {label: '已取消', cls: 'bg-gray-100 text-gray-400'},
}

/* 投诉类型标签配色(与反馈管理语义色风格一致) */
const TYPE_COLORS = {
  服务态度差: { bg: '#fdeeee', fg: '#e8746b' },
  迟到未提供服务: { bg: '#fff3e8', fg: '#f07c2a' },
  技术水平与描述不符: { bg: '#e4f4f2', fg: '#26a69a' },
  诱导私下交易: { bg: '#fdf6e3', fg: '#d48806' },
  言语不当: { bg: '#f7e8e8', fg: '#b45c5c' },
  其他问题: { bg: '#f3f4f6', fg: '#909399' },
}
const typeStyle = (type) => {
  const c = TYPE_COLORS[type] || { bg: '#f3f4f6', fg: '#909399' }
  return { backgroundColor: c.bg, color: c.fg }
}

/* 处理结果标签配色 */
const RESULT_COLORS = {
  警告陪玩师: { bg: '#fff3e8', fg: '#f07c2a' },
  全额退款: { bg: '#fdeeee', fg: '#e8746b' },
  驳回投诉: { bg: '#f3f4f6', fg: '#909399' },
  其他: { bg: '#e4f4f2', fg: '#26a69a' },
}
const resultStyle = (result) => {
  const c = RESULT_COLORS[result] || { bg: '#f3f4f6', fg: '#909399' }
  return { backgroundColor: c.bg, color: c.fg }
}

/* 详情对话框(列表行已含全部字段, 直接展示无需再查) */
const detailOpen = ref(false)
const detail = ref(null)
const handleDetail = (row) => {
  detail.value = row
  detailOpen.value = true
}

/* 处理对话框 */
const handleOpen = ref(false)
const handleRow = ref(null)
const handleForm = reactive({ handleResult: HANDLE_RESULTS[0], reply: '' })
const handleHandle = (row) => {
  handleRow.value = row
  handleForm.handleResult = HANDLE_RESULTS[0]
  handleForm.reply = ''
  handleOpen.value = true
}
/* 详情弹窗内待处理项跳转处理 */
const detailToHandle = () => {
  handleHandle(detail.value)
  detailOpen.value = false
}

const submitHandle = () => {
  if (!handleForm.handleResult) {
    ElMessage.warning('请选择处理结果')
    return
  }
  if (handleForm.reply.trim().length > 500) {
    ElMessage.warning('处理说明不能超过 500 字')
    return
  }
  updateComplaint({
    complaintId: handleRow.value.complaintId,
    handleResult: handleForm.handleResult,
    reply: handleForm.reply.trim(),
  }).then(() => {
    ElMessage.success('处理成功')
    handleOpen.value = false
    getList()
  })
}

const handleDelete = (row) => {
  const complaintIds = row ? [row.complaintId] : ids.value
  if (!complaintIds || complaintIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的投诉?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteComplaintByComplaintIds(complaintIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const query = ref({ pageNum: 1, pageSize: 10, orderNo: '', userName: '', nickName: '', complaintType: null, status: null })
const complaintList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => complaintList.value.length > 0 && selectedIds.size === complaintList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) complaintList.value.forEach(r => selectedIds.delete(r.complaintId))
  else complaintList.value.forEach(r => selectedIds.add(r.complaintId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.orderNo = ''; query.value.userName = ''; query.value.nickName = ''; query.value.complaintType = null; query.value.status = null; handleQuery() }

const getList = () => {
  loading.value = true
  selectComplaintList(query.value).then(res => {
    complaintList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>