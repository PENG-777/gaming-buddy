<template>
  <!-- 区块标题头: 图标 + 标题 + 副标题 + 右侧更多链接 -->
  <div class="flex items-end justify-between">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-warm-bg flex items-center justify-center">
        <span class="u-icon w-4.5 h-4.5 text-warm-primary" v-html="iconOf(icon)"></span>
      </div>
      <div>
        <h2 class="text-lg font-extrabold text-warm-text leading-6">{{ title }}</h2>
        <p v-if="sub" class="text-xs text-warm-sub mt-0.5">{{ sub }}</p>
      </div>
    </div>
    <router-link
      v-if="moreText"
      :to="moreTo"
      class="flex items-center gap-1 text-xs font-semibold text-warm-sub hover:text-warm-primary transition-colors"
    >
      {{ moreText }}
      <span class="u-icon w-3 h-3" v-html="ICONS.arrowRight"></span>
    </router-link>
  </div>
</template>

<script setup>
import { ICONS, iconOf } from '../icons'

defineProps({
  icon: { type: String, default: 'star' },
  title: { type: String, required: true },
  sub: { type: String, default: '' },
  moreText: { type: String, default: '' },
  moreTo: { type: String, default: '' },
})
</script>