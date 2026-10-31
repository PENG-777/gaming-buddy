<template>
  <!-- 头像: 后端图片优先(相对路径拼代理前缀), 无图回退首字纯色头像(色板按昵称哈希轮转, 无渐变) -->
  <img
    v-if="imgSrc"
    :src="imgSrc"
    :alt="name"
    class="rounded-full object-cover select-none flex-shrink-0 ring-1 ring-black/5"
    :style="{ width: size + 'px', height: size + 'px' }"
    @error="imgFailed = true"
  />
  <div
    v-else
    class="flex items-center justify-center rounded-full font-bold text-white select-none flex-shrink-0"
    :style="{ width: size + 'px', height: size + 'px', backgroundColor: color, fontSize: Math.max(12, size * 0.42) + 'px' }"
  >{{ initial }}</div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 40 },
  image: { type: String, default: '' },  // 后端头像 URL(/profile/.. 相对路径)
})

/* 图片加载失败后永久回退首字头像 */
const imgFailed = ref(false)

/** 暖系 8 色纯色色板 */
const PALETTE = ['#f07c2a', '#26a69a', '#e8746b', '#e6b422', '#5b7a99', '#3eb575', '#c08a5a', '#6b7a9e']

const initial = computed(() => (props.name || '友').trim().charAt(0))

const color = computed(() => {
  let hash = 0
  for (const ch of props.name || '') hash = (hash * 31 + ch.charCodeAt(0)) % 997
  return PALETTE[hash % PALETTE.length]
})

/** 图片地址: 相对路径(/profile/..)拼代理前缀, 完整 URL 原样使用 */
const imgSrc = computed(() => {
  if (imgFailed.value || !props.image) return ''
  return /^https?:/.test(props.image) ? props.image : import.meta.env.VITE_APP_BASE_API + props.image
})
</script>