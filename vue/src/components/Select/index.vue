<template>
  <div class="relative" ref="selectRef">
    <div @click="open = !open" class="rounded-lg border border-gray-300 text-sm flex items-center justify-between cursor-pointer bg-white hover:border-gray-400 transition-colors" :class="[dense ? 'h-8 px-2 rounded' : 'h-9 px-3', { 'border-red-400': error }]">
      <span :class="selectedLabel != null ? 'text-gray-700' : 'text-gray-400'">{{ selectedLabel != null ? selectedLabel + suffix : placeholder }}</span>
      <svg class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': open }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
    </div>
    <div v-if="open" class="absolute top-full left-0 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-[200px] overflow-y-auto py-1">
      <div v-for="opt in options" :key="opt[valueKey]" @click="select(opt)" class="px-3 py-1.5 text-sm hover:bg-gray-50 cursor-pointer" :class="opt[valueKey] === modelValue ? 'text-[var(--color-primary)] bg-[var(--color-primary-bg)]' : 'text-gray-700'">
        {{ opt[labelKey] }}{{ suffix }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onBeforeUnmount, ref, computed} from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: null },
  options: { type: Array, required: true },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'value' },
  placeholder: { type: String, default: '请选择' },
  suffix: { type: String, default: '' },
  dense: { type: Boolean, default: false },
  error: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const selectRef = ref(null)

const selectedLabel = computed(() => {
  const hit = props.options.find(o => o[props.valueKey] === props.modelValue)
  return hit ? hit[props.labelKey] : null
})

const select = (opt) => {
  emit('update:modelValue', opt[props.valueKey])
  open.value = false
}

const onClickOutside = (e) => {
  if (selectRef.value && !selectRef.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>
