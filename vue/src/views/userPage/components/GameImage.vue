<template>
  <!-- 游戏图片: 有图显示图片(object-cover), 无图浅橙底 + 游戏名首字兜底(纯色, 无渐变) -->
  <div
    class="flex items-center justify-center font-bold select-none flex-shrink-0 overflow-hidden transition-transform duration-300 group-hover:scale-110"
    :class="SIZES[size]"
    :style="src ? {} : { backgroundColor: '#fff3e8', color: '#f07c2a' }"
  >
    <img v-if="src" :src="src" class="w-full h-full object-cover" :alt="game?.name || ''"/>
    <span v-else>{{ initial }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  game: { type: Object, default: null },  // 游戏对象 { name, image }
  size: { type: String, default: 'md' },  // 尺寸档位: sm 40 / md 48 / lg 56
})

/** 尺寸档位 -> 圆角方块样式 */
const SIZES = {
  sm: 'w-10 h-10 rounded-lg text-base',
  md: 'w-12 h-12 rounded-xl text-lg',
  lg: 'w-14 h-14 rounded-2xl text-xl',
}

const initial = computed(() => (props.game?.name || '游').trim().charAt(0))

/** 图片地址: 相对路径(/profile/..)拼代理前缀, 完整 URL 原样使用 */
const src = computed(() => {
  const image = props.game?.image
  if (!image) return ''
  return /^https?:/.test(image) ? image : import.meta.env.VITE_APP_BASE_API + image
})
</script>