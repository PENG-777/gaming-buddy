<template>
  <tr class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
    <td class="px-3 py-3" :style="{ paddingLeft: (depth * 24 + 12) + 'px' }">
      <div class="flex items-center gap-1.5">
        <span v-if="row.children && row.children.length > 0" @click="expanded = !expanded" class="cursor-pointer w-4 h-4 flex items-center justify-center">
          <svg class="w-3 h-3 text-gray-400 transition-transform duration-200" :class="{ 'rotate-90': expanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </span>
        <span v-else class="w-4 h-4"></span>
        {{ row.menuName }}
      </div>
    </td>
    <td class="px-3 py-3 text-center">
      <svg-icon v-if="row.icon" :icon-class="row.icon" class="w-4 h-4 inline"/>
    </td>
    <td class="px-3 py-3 text-center">{{ row.menuSort }}</td>
    <td class="px-3 py-3 text-center text-gray-500 text-xs">{{ row.component }}</td>
    <td class="px-3 py-3 text-center">
      <button @click="$emit('update', row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">修改</button>
      <button @click="$emit('delete', row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
    </td>
  </tr>
  <template v-if="row.children && expanded">
    <MenuTreeRow v-for="child in row.children" :key="child.menuId" :row="child" :depth="depth + 1" @update="$emit('update', $event)" @delete="$emit('delete', $event)"/>
  </template>
</template>

<script setup>
import {ref} from 'vue'
import SvgIcon from "@/components/SvgIcon/index.vue";

defineProps({
  row: { type: Object, required: true },
  depth: { type: Number, default: 0 }
})

defineEmits(['update', 'delete'])

const expanded = ref(true)
</script>
