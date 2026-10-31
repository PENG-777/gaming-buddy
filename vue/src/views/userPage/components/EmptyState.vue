<template>
  <!-- 空状态: SVG 图标 + 文案 + 可选操作按钮 -->
  <div class="flex flex-col items-center justify-center py-16 px-4">
    <div class="w-16 h-16 rounded-2xl bg-warm-bg flex items-center justify-center mb-4">
      <span class="u-icon w-8 h-8 text-warm-accent" v-html="iconOf(icon)"></span>
    </div>
    <p class="text-sm text-warm-sub">{{ text }}</p>
    <button
      v-if="actionText"
      class="mt-5 px-6 py-2 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.97] transition-all"
      @click="$emit('action')"
    >{{ actionText }}</button>
  </div>
</template>

<script setup>
import { iconOf } from '../icons'

defineProps({
  icon: { type: String, default: 'box' },
  text: { type: String, default: '暂无数据' },
  actionText: { type: String, default: '' },
})
defineEmits(['action'])
</script>