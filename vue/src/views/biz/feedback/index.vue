<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名</label>
        <input v-model="query.userName" placeholder="请输入用户名" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">类型</label>
        <select v-model="query.feedbackType" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option v-for="t in FEEDBACK_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option :value="0">待处理</option>
          <option :value="1">已处理</option>
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

    <!-- 操作按钮 -->
    <div class="flex gap-2 mb-2">
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
            <th class="w-[55px] px-3 py-3 text-center"><input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="w-4 h-4 rounded"/></th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[140px] px-3 py-3 text-center font-medium text-gray-600">用户</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">类型</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">反馈内容</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">提交时间</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">回复摘要</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in feedbackList" :key="row.feedbackId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.feedbackId) }">
            <td class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.feedbackId)" @change="toggleRow(row.feedbackId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <image-preview v-if="row.avatar" :src="row.avatar" :width="32" :height="32"/>
                <div v-else class="w-8 h-8 rounded-full bg-[var(--color-primary-bg)] text-[var(--color-primary)] text-xs font-bold flex items-center justify-center flex-shrink-0">{{ (row.userName || '用')[0] }}</div>
                <span class="font-medium">{{ row.userName }}</span>
              </div>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="tagStyle(row.feedbackType)">{{ row.feedbackType }}</span>
            </td>
            <td class="px-3 py-3 text-center max-w-[240px] truncate" :title="row.content">
              <button class="max-w-full truncate hover:text-[var(--color-primary)] transition-colors" @click="handleDetail(row)">{{ row.content }}</button>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.status === 0 ? 'text-amber-600' : 'text-green-600'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === 0 ? 'bg-amber-500' : 'bg-green-500'"></span>{{ row.status === 0 ? '待处理' : '已处理' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500 max-w-[200px] truncate" :title="row.reply">{{ row.reply || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleReply(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">回复</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="feedbackList.length === 0"><td colspan="9" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 详情对话框(列表行已含全部字段, 直接展示无需再查) -->
    <Modal title="反馈详情" v-model="detailOpen" width="640px">
      <div v-if="detail">
        <div class="flex items-center gap-3">
          <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="tagStyle(detail.feedbackType)">{{ detail.feedbackType }}</span>
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
        <div class="mt-3 pt-3 border-t border-gray-100 max-h-[180px] overflow-y-auto">
          <p class="text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.content }}</p>
        </div>
        <div v-if="detail.reply" class="mt-3 rounded-lg bg-gray-50 border border-gray-100 px-4 py-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-gray-500">处理回复</span>
            <span class="text-xs text-gray-400">{{ detail.replyTime || '-' }}</span>
          </div>
          <p class="mt-1.5 text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.reply }}</p>
        </div>
      </div>
      <template #footer>
        <button v-if="detail && detail.status === 0" @click="detailToReply" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">回复</button>
        <button @click="detailOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">关闭</button>
      </template>
    </Modal>

    <!-- 回复对话框 -->
    <Modal title="回复反馈" v-model="replyOpen" width="560px">
      <form @submit.prevent="submitReply" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">反馈内容</label>
          <div class="flex-1 rounded-lg bg-gray-50 border border-gray-100 px-3 py-2 max-h-[120px] overflow-y-auto">
            <p class="text-sm leading-6 text-gray-600 whitespace-pre-wrap break-all">{{ replyRow ? replyRow.content : '' }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">回复内容</label>
          <div class="flex-1">
            <textarea v-model="replyForm.reply" rows="5" placeholder="请输入回复内容(500 字以内, 选填), 保存后该反馈将标记为已处理" class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
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
import {deleteFeedbackByFeedbackIds, selectFeedbackList, updateFeedback} from "@/api/biz/feedback.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";

/* 反馈类型(与后端白名单/用户端帮助中心一致) */
const FEEDBACK_TYPES = ['功能建议', '体验问题', '内容举报', '其他']

/* 类型标签配色(与公告管理语义色风格一致) */
const TYPE_COLORS = {
  功能建议: { bg: '#fff3e8', fg: '#f07c2a' },
  体验问题: { bg: '#e4f4f2', fg: '#26a69a' },
  内容举报: { bg: '#fdeeee', fg: '#e8746b' },
  其他: { bg: '#f3f4f6', fg: '#909399' },
}
const tagStyle = (type) => {
  const c = TYPE_COLORS[type] || { bg: '#f3f4f6', fg: '#909399' }
  return { backgroundColor: c.bg, color: c.fg }
}

/* 详情对话框(列表行已含全部字段, 直接展示无需再查) */
const detailOpen = ref(false)
const detail = ref(null)
const handleDetail = (row) => {
  detail.value = row
  detailOpen.value = true
}

/* 回复对话框 */
const replyOpen = ref(false)
const replyRow = ref(null)
const replyForm = reactive({ reply: '' })
const handleReply = (row) => {
  replyRow.value = row
  replyForm.reply = row.reply || ''
  replyOpen.value = true
}
/* 详情弹窗内待处理项跳转回复 */
const detailToReply = () => {
  handleReply(detail.value)
  detailOpen.value = false
}

const submitReply = () => {
  if (replyForm.reply.trim().length > 500) {
    ElMessage.warning('回复内容不能超过 500 字')
    return
  }
  updateFeedback({ feedbackId: replyRow.value.feedbackId, reply: replyForm.reply.trim() }).then(() => {
    ElMessage.success('处理成功')
    replyOpen.value = false
    getList()
  })
}

const handleDelete = (row) => {
  const feedbackIds = row ? [row.feedbackId] : ids.value
  if (!feedbackIds || feedbackIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的反馈?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteFeedbackByFeedbackIds(feedbackIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const query = ref({ pageNum: 1, pageSize: 10, userName: '', feedbackType: null, status: null })
const feedbackList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => feedbackList.value.length > 0 && selectedIds.size === feedbackList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) feedbackList.value.forEach(r => selectedIds.delete(r.feedbackId))
  else feedbackList.value.forEach(r => selectedIds.add(r.feedbackId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; query.value.feedbackType = null; query.value.status = null; handleQuery() }

const getList = () => {
  loading.value = true
  selectFeedbackList(query.value).then(res => {
    feedbackList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>