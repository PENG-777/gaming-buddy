<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">用户名称</label>
        <input v-model="query.userName" placeholder="请输入用户名称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
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
      <button :disabled="multple" @click="handleDelete()" class="h-9 px-4 rounded-lg text-sm font-medium transition-colors flex items-center gap-1" :class="multple ? 'text-gray-400 border border-gray-200 bg-gray-50 cursor-not-allowed' : 'text-red-500 border border-red-400 bg-white hover:bg-red-50'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>删除
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg relative">
      <!-- Loading 遮罩 -->
      <div v-if="loading" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center rounded-lg">
        <div class="flex flex-col items-center gap-2">
          <svg class="w-8 h-8 animate-spin text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          <span class="text-sm text-gray-500">加载中...</span>
        </div>
      </div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-[55px] px-3 py-3 text-center">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="w-4 h-4 rounded"/>
            </th>
            <th class="w-[180px] px-3 py-3 text-center font-medium text-gray-600">用户编号</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">用户名</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">性别</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">用户头像</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">对应角色</th>
            <th class="w-[200px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in userList" :key="row.userId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.userId) }">
            <td class="px-3 py-3 text-center">
              <input type="checkbox" :checked="selectedIds.has(row.userId)" @change="toggleRow(row.userId)" class="w-4 h-4 rounded"/>
            </td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.userId }}</td>
            <td class="px-3 py-3 text-center">{{ row.userName }}</td>
            <td class="px-3 py-3 text-center">
              <span v-if="row.sex === 0">男</span>
              <span v-else-if="row.sex === 1">女</span>
              <span v-else class="text-gray-400">未设置</span>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="flex justify-center">
                <image-preview :src="row.avatar ? row.avatar : defaultAvatar" alt="" :width="50" :height="50"/>
              </div>
            </td>
            <td class="px-3 py-3 text-center">{{ row.roleName }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleUpdate(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">修改</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="userList.length === 0">
            <td colspan="7" class="px-3 py-12 text-center text-gray-400">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 添加/修改对话框 -->
    <Modal :title="title" v-model="open" width="500px">
      <form @submit.prevent="submitForm" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">用户名</label>
          <div class="flex-1">
            <input v-model="form.userName" placeholder="请输入用户名" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20" :class="{ '!border-red-400': errors.userName }"/>
            <p v-if="errors.userName" class="text-red-500 text-xs mt-1">{{ errors.userName }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">性别</label>
          <div class="flex gap-6 pt-2">
            <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.sex" :value="0"/>男</label>
            <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.sex" :value="1"/>女</label>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">密码</label>
          <div class="flex-1">
            <input v-model="form.password" placeholder="请输入密码" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20" :class="{ '!border-red-400': errors.password }"/>
            <p v-if="errors.password" class="text-red-500 text-xs mt-1">{{ errors.password }}</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">对应角色</label>
          <div class="flex-1">
            <Select v-model="form.roleId" :options="roleList" label-key="roleName" value-key="roleId" placeholder="请选择角色" class="w-full" :error="!!errors.roleId"/>
            <p v-if="errors.roleId" class="text-red-500 text-xs mt-1">{{ errors.roleId }}</p>
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
import {deleteUserByUserIds, insertUser, selectUserByUserId, selectUserList, updateUser} from "@/api/system/user.js";
import defaultAvatar from '@/assets/images/profile.jpg'
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import {selectAllRole} from "@/api/system/role.js";

const title = ref('')
const open = ref(false)

const form = reactive({
  userId: null, userName: '', sex: null, password: '', roleId: null
})

const errors = reactive({ userName: '', password: '', roleId: '' })

const validateForm = () => {
  let valid = true
  errors.userName = ''; errors.password = ''; errors.roleId = ''
  if (!form.userName) { errors.userName = '请输入用户名'; valid = false }
  if (!form.password) { errors.password = '请输入密码'; valid = false }
  if (!form.roleId) { errors.roleId = '请选择角色'; valid = false }
  return valid
}

const handleInsert = () => {
  Object.assign(form, { userId: null, userName: '', sex: null, password: '', roleId: null })
  Object.assign(errors, { userName: '', password: '', roleId: '' })
  open.value = true
  title.value = '新增用户'
}

const handleUpdate = (row) => {
  Object.assign(errors, { userName: '', password: '', roleId: '' })
  const userId = row ? row.userId : ids.value[0]
  if (!userId) return
  selectUserByUserId(userId).then(res => {
    Object.assign(form, res.data)
    open.value = true
    title.value = '修改用户'
  })
}

const handleDelete = (row) => {
  const userIds = row ? [row.userId] : ids.value
  if (!userIds || userIds.length === 0) return
  ElMessageBox.confirm('是否确认删除用户?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteUserByUserIds(userIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const submitForm = () => {
  if (!validateForm()) return
  if (form.userId != null) {
    updateUser({...form}).then(() => {
      ElMessage.success('修改成功')
      open.value = false
      getList()
    })
  } else {
    insertUser({...form}).then(() => {
      ElMessage.success('新增成功')
      open.value = false
      getList()
    })
  }
}

const query = ref({ pageNum: 1, pageSize: 10, userName: '' })
const userList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const single = computed(() => ids.value.length !== 1)
const multple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => userList.value.length > 0 && selectedIds.size === userList.value.length)

const syncSelected = () => {
  ids.value = [...selectedIds]
}
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    userList.value.forEach(r => selectedIds.delete(r.userId))
  } else {
    userList.value.forEach(r => selectedIds.add(r.userId))
  }
  syncSelected()
}

const getList = () => {
  loading.value = true
  selectUserList(query.value).then(res => {
    userList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => { query.value.userName = ''; handleQuery() }

const roleList = ref([])

onMounted(() => {
  getList()
  selectAllRole().then(res => { roleList.value = res.data })
})
</script>
