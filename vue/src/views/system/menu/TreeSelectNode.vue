<template>
  <div>
    <div @click.stop="$emit('select', node)" class="px-3 py-1.5 text-sm hover:bg-gray-50 cursor-pointer flex items-center gap-1.5" :class="{ 'text-[var(--color-primary)] bg-[var(--color-primary-bg)]': node.menuId === selectedId }" :style="{ paddingLeft: (depth * 16 + 12) + 'px' }">
      <span v-if="node.children && node.children.length > 0" @click.stop="expanded = !expanded" class="w-4 flex-shrink-0">
        <svg class="w-3 h-3 text-gray-400 transition-transform duration-200" :class="{ 'rotate-90': expanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      </span>
      <span v-else class="w-4 flex-shrink-0"></span>
      {{ node.menuName }}
    </div>
    <template v-if="node.children && expanded">
      <TreeSelectNode v-for="child in node.children" :key="child.menuId" :node="child" :depth="depth + 1" :selected-id="selectedId" @select="$emit('select', $event)"/>
    </template>
  </div>
</template>

<script setup>
import {ref} from 'vue'

defineProps({
  node: { type: Object, required: true },
  depth: { type: Number, default: 0 },
  selectedId: { type: Number, default: null }
})

defineEmits(['select'])

const expanded = ref(false)
</script>
