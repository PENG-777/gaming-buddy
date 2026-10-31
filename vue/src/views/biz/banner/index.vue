<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">轮播标题</label>
        <input v-model="query.title" placeholder="请输入轮播标题" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[52px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option :value="0">启用</option>
          <option :value="1">停用</option>
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
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">轮播图片</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">标题</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">副标题</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">标签</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">按钮文字</th>
            <th class="w-[150px] px-3 py-3 text-center font-medium text-gray-600">跳转地址</th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">排序</th>
            <th class="w-[80px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">创建时间</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in bannerList" :key="row.bannerId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.bannerId) }">
            <td class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.bannerId)" @change="toggleRow(row.bannerId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center">
              <image-preview v-if="row.image" :src="row.image" :width="96" :height="54"/>
              <div v-else class="w-24 h-[54px] rounded-lg border border-dashed border-gray-300 text-gray-400 text-xs flex items-center justify-center mx-auto">{{ row.bgColor || '无图片' }}</div>
            </td>
            <td class="px-3 py-3 text-center font-medium">{{ row.title }}</td>
            <td class="px-3 py-3 text-center text-gray-500 max-w-[220px] truncate" :title="row.subtitle">{{ row.subtitle || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <span v-if="row.tag" class="inline-block px-2 py-0.5 rounded text-xs bg-[var(--color-primary-bg)] text-[var(--color-primary)]">{{ row.tag }}</span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.linkText || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-500 max-w-[150px] truncate" :title="row.linkUrl">{{ row.linkUrl || '-' }}</td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.bannerSort }}</td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.status === 0 ? 'text-green-600' : 'text-gray-400'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === 0 ? 'bg-green-500' : 'bg-gray-300'"></span>{{ row.status === 0 ? '启用' : '停用' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleUpdate(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">修改</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="bannerList.length === 0"><td colspan="12" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 对话框 -->
    <Modal :title="title" v-model="open" width="560px">
      <form @submit.prevent="submitForm" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>标题</label>
          <div class="flex-1">
            <input v-model="form.title" placeholder="请输入轮播标题" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">副标题</label>
          <div class="flex-1">
            <input v-model="form.subtitle" placeholder="请输入副标题" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">标签</label>
          <div class="flex-1">
            <input v-model="form.tag" placeholder="请输入标签角标文字, 如: 限时活动" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">轮播图片</label>
          <div class="flex-1">
            <ImageUpload v-model="form.image" :limit="1"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">按钮文字</label>
          <div class="flex-1">
            <input v-model="form.linkText" placeholder="请输入按钮文字, 如: 去领券" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">跳转地址</label>
          <div class="flex-1">
            <input v-model="form.linkUrl" placeholder="请输入站内路由, 如: /user/coupons" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">回退背景色</label>
          <div class="flex-1 flex items-center gap-2">
            <input v-model="form.bgColor" placeholder="图片缺失时的背景色, 如: #fff3e8" class="flex-1 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            <span class="w-9 h-9 rounded-lg border border-gray-300 flex-shrink-0" :style="{ backgroundColor: isColor(form.bgColor) ? form.bgColor : '#ffffff' }"></span>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">回退前景色</label>
          <div class="flex-1 flex items-center gap-2">
            <input v-model="form.fgColor" placeholder="标签/按钮文字颜色, 如: #f07c2a" class="flex-1 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            <span class="w-9 h-9 rounded-lg border border-gray-300 flex-shrink-0" :style="{ backgroundColor: isColor(form.fgColor) ? form.fgColor : '#ffffff' }"></span>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">排序</label>
          <div class="flex-1">
            <input v-model="form.bannerSort" type="number" placeholder="请输入排序(数字越小越靠前)" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">状态</label>
          <div class="flex-1 flex items-center gap-4 pt-1.5">
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="0" v-model="form.status" class="accent-[var(--color-primary)]"/>启用
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input type="radio" :value="1" v-model="form.status" class="accent-[var(--color-primary)]"/>停用
            </label>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitForm" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">保存</button>
        <button @click="open = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {deleteBannerByBannerIds, insertBanner, selectBannerByBannerId, selectBannerList, updateBanner} from "@/api/biz/banner.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";

const title = ref('')
const open = ref(false)

const form = reactive({ bannerId: null, title: '', subtitle: '', tag: '', image: '', bgColor: '', fgColor: '', linkText: '', linkUrl: '', status: 0, bannerSort: 0 })

/** 色值格式校验: 空串或 #RGB/#RRGGBB 为合法 */
const isColor = (v) => !v || /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(v)

const handleInsert = () => {
  Object.assign(form, { bannerId: null, title: '', subtitle: '', tag: '', image: '', bgColor: '', fgColor: '', linkText: '', linkUrl: '', status: 0, bannerSort: 0 })
  open.value = true
  title.value = '新增轮播图'
}

const handleUpdate = (row) => {
  const bannerId = row ? row.bannerId : ids.value[0]
  if (!bannerId) return
  selectBannerByBannerId(bannerId).then(res => {
    Object.assign(form, { bannerId: null, title: '', subtitle: '', tag: '', image: '', bgColor: '', fgColor: '', linkText: '', linkUrl: '', status: 0, bannerSort: 0 }, res.data)
    open.value = true
    title.value = '修改轮播图'
  })
}

const handleDelete = (row) => {
  const bannerIds = row ? [row.bannerId] : ids.value
  if (!bannerIds || bannerIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的轮播图?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteBannerByBannerIds(bannerIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const submitForm = () => {
  if (!form.title || !form.title.trim()) {
    ElMessage.warning('请输入轮播标题')
    return
  }
  if (!isColor(form.bgColor)) {
    ElMessage.warning('回退背景色格式不正确, 应如 #fff3e8')
    return
  }
  if (!isColor(form.fgColor)) {
    ElMessage.warning('回退前景色格式不正确, 应如 #f07c2a')
    return
  }
  if (form.bannerSort !== '' && form.bannerSort !== null && !/^\d+$/.test(String(form.bannerSort))) {
    ElMessage.warning('排序必须为非负整数')
    return
  }
  const data = { ...form, title: form.title.trim(), bannerSort: form.bannerSort === '' ? 0 : Number(form.bannerSort) }
  if (data.bannerId != null) {
    updateBanner(data).then(() => {
      ElMessage.success('修改成功')
      open.value = false; getList()
    })
  } else {
    insertBanner(data).then(() => {
      ElMessage.success('新增成功')
      open.value = false; getList()
    })
  }
}

const query = ref({ pageNum: 1, pageSize: 10, title: '', status: null })
const bannerList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const single = computed(() => ids.value.length !== 1)
const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => bannerList.value.length > 0 && selectedIds.size === bannerList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) bannerList.value.forEach(r => selectedIds.delete(r.bannerId))
  else bannerList.value.forEach(r => selectedIds.add(r.bannerId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.title = ''; query.value.status = null; handleQuery() }

const getList = () => {
  loading.value = true
  selectBannerList(query.value).then(res => {
    bannerList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => getList())
</script>