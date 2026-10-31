<template>
  <div>
    <TreeNode v-for="node in data" :key="node[nodeKey]" :node="node" :node-key="nodeKey" :label-key="labelKey" :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)"/>
  </div>
</template>

<script setup>
import TreeNode from './TreeNode.vue'

defineProps({
  data: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  nodeKey: { type: String, default: 'id' },
  labelKey: { type: String, default: 'label' }
})

defineEmits(['update:modelValue'])
</script>
