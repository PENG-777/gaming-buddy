<template>
  <div class="flex items-center justify-end gap-3 py-6 px-4">
    <!-- 总数 -->
    <span class="text-sm text-gray-500">共 {{ total }} 条</span>

    <!-- 每页条数 -->
    <Select v-model="localPageSize" @update:model-value="handleSizeChange" :options="sizeOptions" suffix="条/页" dense/>

    <!-- 页码按钮 -->
    <div class="flex items-center gap-0.5">
      <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)" class="w-8 h-8 flex items-center justify-center rounded text-sm transition-colors" :class="currentPage <= 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
      </button>

      <template v-for="p in pageList" :key="p">
        <span v-if="p === '...'" class="w-8 h-8 flex items-center justify-center text-sm text-gray-400">...</span>
        <button v-else @click="goPage(p)" class="w-8 h-8 flex items-center justify-center rounded text-sm transition-colors" :class="p === currentPage ? 'bg-[var(--color-primary)] text-white font-medium' : 'text-gray-600 hover:bg-gray-100'">{{ p }}</button>
      </template>

      <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)" class="w-8 h-8 flex items-center justify-center rounded text-sm transition-colors" :class="currentPage >= totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>

    <!-- 跳转 -->
    <div class="flex items-center gap-1 text-sm text-gray-500">
      <span>前往</span>
      <input v-model="jumpPage" @keyup.enter="doJump" class="w-10 h-8 text-center rounded border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)]" type="number" :min="1" :max="totalPages"/>
      <span>页</span>
    </div>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'

const currentPage = defineModel('page', {default: 1})
const pageSize = defineModel('limit', {default: 10})

const props = defineProps({
  total: {type: Number, required: true},
  pageSizes: {type: Array, default: () => [10, 20, 30, 50]},
})

const emit = defineEmits(['pagination'])

const localPageSize = ref(pageSize.value)
const jumpPage = ref('')

const sizeOptions = computed(() => props.pageSizes.map(s => ({ label: s, value: s })))

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / pageSize.value)))

const pageList = computed(() => {
  const pages = []
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('...')
    for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
    if (cur < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const goPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  emit('pagination', {page: p, limit: pageSize.value})
}

const doJump = () => {
  const p = parseInt(jumpPage.value)
  if (p && p >= 1 && p <= totalPages.value) goPage(p)
  jumpPage.value = ''
}

const handleSizeChange = () => {
  pageSize.value = localPageSize.value
  if (currentPage.value * pageSize.value > props.total) currentPage.value = 1
  emit('pagination', {page: currentPage.value, limit: pageSize.value})
}
</script>
