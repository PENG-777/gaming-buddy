<template>
  <div>
    <!-- 缩略图 -->
    <img
      v-if="realSrc"
      :src="realSrc"
      :style="`width:${realWidth};height:${realHeight};`"
      class="object-cover rounded cursor-pointer hover:opacity-90 transition-opacity"
      @click="previewOpen = true"
      alt=""
    />

    <!-- 预览弹窗 -->
    <Teleport to="body">
      <Transition name="preview-fade">
        <div v-if="previewOpen" class="fixed inset-0 z-[9999] bg-black/80 flex items-center justify-center" @click="previewOpen = false">
          <img :src="previewSrc" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl" @click.stop alt="Preview"/>
          <!-- 关闭按钮 -->
          <button class="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/30 transition-colors" @click="previewOpen = false">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>

          <!-- 图片列表切换 -->
          <div v-if="srcList.length > 1" class="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
            <button v-for="(s, i) in srcList" :key="i" @click.stop="currentIdx = i" class="w-2 h-2 rounded-full transition-all" :class="i === currentIdx ? 'bg-white w-6' : 'bg-white/40 hover:bg-white/60'"/>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import {computed, ref} from "vue";

const props = defineProps({
  src: { type: String, default: "" },
  width: { type: [Number, String], default: "" },
  height: { type: [Number, String], default: "" }
})

const previewOpen = ref(false)
const currentIdx = ref(0)

const realSrc = computed(() => {
  if (!props.src) return ''
  let real_src = props.src.split(",")[0]
  if (/^(https?:)/.test(real_src)) return real_src
  if (real_src.startsWith('/src')) return real_src
  return import.meta.env.VITE_APP_BASE_API + real_src
})

const srcList = computed(() => {
  if (!props.src) return []
  return props.src.split(",").map(item => {
    if (item.startsWith('http') || item.startsWith('/src')) return item
    return import.meta.env.VITE_APP_BASE_API + item
  })
})

const previewSrc = computed(() => srcList.value[currentIdx.value] || realSrc.value)

const realWidth = computed(() =>
  typeof props.width == "string" ? props.width : `${props.width}px`
)
const realHeight = computed(() =>
  typeof props.height == "string" ? props.height : `${props.height}px`
)
</script>

<style scoped>
.preview-fade-enter-active, .preview-fade-leave-active {
  transition: opacity 0.25s ease;
}
.preview-fade-enter-from, .preview-fade-leave-to {
  opacity: 0;
}
</style>
