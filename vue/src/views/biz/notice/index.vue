<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">公告标题</label>
        <input v-model="query.title" placeholder="请输入公告标题" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">类型</label>
        <select v-model="query.noticeType" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option v-for="t in NOTICE_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option :value="0">发布</option>
          <option :value="1">撤下</option>
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
      <button @click="handleInsert" class="h-9 px-4 rounded-lg text-sm font-medium text-[var(--color-primary)] border border-[var(--color-primary)] bg-white hover:bg-[var(--color-primary-bg)] transition-colors flex items-center gap-1">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>新增
      </button>
      <button :disabled="single" @click="handleUpdate()" class="h-9 px-4 rounded-lg text-sm font-medium transition-colors flex items-center gap-1" :class="single ? 'text-gray-400 border border-gray-200 bg-gray-50 cursor-not-allowed' : 'text-green-600 border border-green-500 bg-white hover:bg-green-50'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>修改
      </button>
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
            <th class="px-3 py-3 text-center font-medium text-gray-600">公告标题</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">类型</th>
            <th class="w-[80px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">发布时间</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">内容摘要</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in noticeList" :key="row.noticeId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.noticeId) }">
            <td class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.noticeId)" @change="toggleRow(row.noticeId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center font-medium max-w-[260px]">
              <button class="block mx-auto max-w-full truncate hover:text-[var(--color-primary)] transition-colors" :title="row.title" @click="handleDetail(row)">{{ row.title }}</button>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="tagStyle(row.noticeType)">{{ row.noticeType }}</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.status === 0 ? 'text-green-600' : 'text-gray-400'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === 0 ? 'bg-green-500' : 'bg-gray-300'"></span>{{ row.status === 0 ? '发布' : '撤下' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500 max-w-[240px] truncate" :title="row.content">{{ row.content || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleUpdate(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">修改</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="noticeList.length === 0"><td colspan="8" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 对话框 -->
    <Modal :title="title" v-model="open" width="560px">
      <form @submit.prevent="submitForm" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>公告标题</label>
          <div class="flex-1">
            <input v-model="form.title" placeholder="请输入公告标题(100 字以内)" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>公告类型</label>
          <div class="flex-1">
            <select v-model="form.noticeType" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white">
              <option v-for="t in NOTICE_TYPES" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>公告正文</label>
          <div class="flex-1">
            <textarea v-model="form.content" rows="5" placeholder="请输入公告正文(1000 字以内)" class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">状态</label>
          <div class="flex-1 flex items-center gap-4 pt-1.5">
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="0" v-model="form.status" class="accent-[var(--color-primary)]"/>发布
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="1" v-model="form.status" class="accent-[var(--color-primary)]"/>撤下
            </label>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitForm" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">保存</button>
        <button @click="open = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>
    <!-- 详情对话框 -->
    <Modal title="公告详情" v-model="detailOpen" width="640px">
      <div v-if="detail">
        <div class="flex items-center gap-3">
          <span class="inline-block px-2 py-0.5 rounded-lg text-xs font-bold" :style="tagStyle(detail.noticeType)">{{ detail.noticeType }}</span>
          <span class="inline-flex items-center gap-1.5 text-sm" :class="detail.status === 0 ? 'text-green-600' : 'text-gray-400'">
            <span class="w-1.5 h-1.5 rounded-full" :class="detail.status === 0 ? 'bg-green-500' : 'bg-gray-300'"></span>{{ detail.status === 0 ? '发布' : '撤下' }}
          </span>
          <span class="ml-auto flex items-center gap-1 text-xs text-gray-400">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>{{ detail.createTime || '-' }}
          </span>
        </div>
        <h3 class="mt-3 text-base font-bold text-gray-800 break-all">{{ detail.title }}</h3>
        <div class="mt-3 pt-3 border-t border-gray-100 max-h-[320px] overflow-y-auto">
          <p class="text-sm leading-7 text-gray-600 whitespace-pre-wrap break-all">{{ detail.content }}</p>
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
import {deleteNoticeByNoticeIds, insertNotice, selectNoticeByNoticeId, selectNoticeList, updateNotice} from "@/api/biz/notice.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";

/* 公告类型(与后端白名单/用户端标签一致) */
const NOTICE_TYPES = ['保障', '活动', '上新', '安全']

/* 类型标签配色(与用户端公告页语义色一致) */
const TYPE_COLORS = {
  保障: { bg: '#e4f4f2', fg: '#26a69a' },
  活动: { bg: '#fff3e8', fg: '#f07c2a' },
  上新: { bg: '#fdf3e3', fg: '#e6b422' },
  安全: { bg: '#fdeeee', fg: '#e8746b' },
}
const tagStyle = (type) => {
  const c = TYPE_COLORS[type] || { bg: '#f3f4f6', fg: '#909399' }
  return { backgroundColor: c.bg, color: c.fg }
}

const title = ref('')
const open = ref(false)

/* 详情对话框(列表行已含全部字段, 直接展示无需再查) */
const detailOpen = ref(false)
const detail = ref(null)
const handleDetail = (row) => {
  detail.value = row
  detailOpen.value = true
}

const form = reactive({ noticeId: null, title: '', noticeType: '活动', content: '', status: 0 })

const handleInsert = () => {
  Object.assign(form, { noticeId: null, title: '', noticeType: '活动', content: '', status: 0 })
  open.value = true
  title.value = '新增公告'
}

const handleUpdate = (row) => {
  const noticeId = row ? row.noticeId : ids.value[0]
  if (!noticeId) return
  selectNoticeByNoticeId(noticeId).then(res => {
    Object.assign(form, { noticeId: null, title: '', noticeType: '活动', content: '', status: 0 }, res.data)
    open.value = true
    title.value = '修改公告'
  })
}

const handleDelete = (row) => {
  const noticeIds = row ? [row.noticeId] : ids.value
  if (!noticeIds || noticeIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的公告?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteNoticeByNoticeIds(noticeIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const submitForm = () => {
  if (!form.title || !form.title.trim()) {
    ElMessage.warning('请输入公告标题')
    return
  }
  if (form.title.trim().length > 100) {
    ElMessage.warning('公告标题不能超过 100 字')
    return
  }
  if (!NOTICE_TYPES.includes(form.noticeType)) {
    ElMessage.warning('请选择公告类型')
    return
  }
  if (!form.content || !form.content.trim()) {
    ElMessage.warning('请输入公告正文')
    return
  }
  if (form.content.trim().length > 1000) {
    ElMessage.warning('公告正文不能超过 1000 字')
    return
  }
  const data = { ...form, title: form.title.trim(), content: form.content.trim() }
  if (data.noticeId != null) {
    updateNotice(data).then(() => {
      ElMessage.success('修改成功')
      open.value = false; getList()
    })
  } else {
    insertNotice(data).then(() => {
      ElMessage.success('新增成功')
      open.value = false; getList()
    })
  }
}

const query = ref({ pageNum: 1, pageSize: 10, title: '', noticeType: null, status: null })
const noticeList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const single = computed(() => ids.value.length !== 1)
const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => noticeList.value.length > 0 && selectedIds.size === noticeList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) noticeList.value.forEach(r => selectedIds.delete(r.noticeId))
  else noticeList.value.forEach(r => selectedIds.add(r.noticeId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.title = ''; query.value.noticeType = null; query.value.status = null; handleQuery() }

const getList = () => {
  loading.value = true
  selectNoticeList(query.value).then(res => {
    noticeList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>