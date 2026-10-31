<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="fixed inset-0 z-[9998] flex items-center justify-center" @click.self="handleOverlayClick">
        <!-- 遮罩 -->
        <div class="absolute inset-0 bg-black/40"></div>

        <!-- 弹窗主体 -->
        <div
          class="relative bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden max-h-[calc(100vh-4rem)]"
          :style="modalStyle"
        >
          <!-- 标题栏 -->
          <div v-if="title" class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h3 class="text-base font-semibold text-gray-800">{{ title }}</h3>
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              @click="close"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- 内容区 -->
          <div class="flex-1 overflow-auto p-6">
            <slot />
          </div>

          <!-- 底部按钮区 -->
          <div v-if="$slots.footer" class="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: [String, Number], default: '520px' },
  closeOnOverlay: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const modalStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width
}))

const close = () => {
  emit('update:modelValue', false)
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close()
  }
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-active > :nth-child(2),
.modal-fade-leave-active > :nth-child(2) {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from > :nth-child(2) {
  transform: scale(0.92) translateY(10px);
  opacity: 0;
}
.modal-fade-leave-to > :nth-child(2) {
  transform: scale(0.95);
  opacity: 0;
}
</style>