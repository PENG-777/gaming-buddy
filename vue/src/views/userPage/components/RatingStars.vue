<template>
  <!-- 星级: 默认纯展示, interactive 开启打分交互 -->
  <div class="flex items-center gap-0.5" @mouseleave="hoverIndex = 0">
    <span
      v-for="i in 5"
      :key="i"
      class="u-icon transition-transform duration-100"
      :class="interactive ? 'cursor-pointer hover:scale-110' : 'pointer-events-none'"
      :style="{ width: size + 'px', height: size + 'px', color: i <= activeValue ? '#e6b422' : '#e5e2dd' }"
      @mouseenter="interactive && (hoverIndex = i)"
      @click="interactive && select(i)"
      v-html="ICONS.star"
    ></span>
    <span v-if="showValue" class="ml-1 text-sm font-semibold" :class="modelValue >= 4.5 ? 'text-warm-warning' : 'text-warm-sub'">
      {{ Number(modelValue || 0).toFixed(1) }}
    </span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ICONS } from '../icons'

const props = defineProps({
  modelValue: { type: Number, default: 0 },     // 星级 1-5
  size: { type: Number, default: 16 },          // 星星像素尺寸
  interactive: { type: Boolean, default: false },
  showValue: { type: Boolean, default: false }, // 星级后显示数值
})
const emit = defineEmits(['update:modelValue'])

const hoverIndex = ref(0)
const activeValue = computed(() => (props.interactive ? hoverIndex.value || props.modelValue : props.modelValue))

const select = (i) => emit('update:modelValue', i)
</script>