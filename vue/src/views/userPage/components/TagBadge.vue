<template>
  <!-- 统一标签徽章: type 控制配色(纯色浅底, 无渐变) -->
  <span
    class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium leading-5 whitespace-nowrap"
    :class="TYPE_CLS[type] || TYPE_CLS.warm"
  >{{ text }}</span>
</template>

<script setup>
defineProps({
  text: { type: String, required: true },
  type: { type: String, default: 'warm' }, // warm/success/warning/danger/info/plain
})

const TYPE_CLS = {
  warm: 'bg-warm-bg text-warm-primary',
  success: 'bg-[#e4f4f2] text-warm-success',
  warning: 'bg-[#fdf6e3] text-[#c79500]',
  danger: 'bg-[#fdeeee] text-warm-danger',
  info: 'bg-[#eef3f8] text-[#5b7a99]',
  plain: 'bg-[#f5f5f4] text-warm-sub',
}
</script>