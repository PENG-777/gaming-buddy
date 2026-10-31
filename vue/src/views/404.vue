<template>
<div class="min-h-screen flex items-center justify-center bg-[var(--color-bg-page)]">
  <div class="text-center">
    <h1 class="text-7xl font-bold text-[var(--color-text-light)] mb-2">404</h1>
    <p class="text-base text-[var(--color-text-medium)] mb-8">该网页不存在</p>
    <button @click="router.go(-1)"
      class="inline-flex items-center justify-center h-10 px-6 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors cursor-pointer">
      返回
    </button>
  </div>
</div>
</template>

<script setup>
import {useRouter} from "vue-router";

// 路由实例
const router = useRouter()
</script>
