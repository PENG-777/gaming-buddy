<template>
  <div class="px-4 pb-4 pt-5">
    <router-view v-slot="{ Component, route }">
      <div :key="route.path" class="min-h-[calc(100vh-100px)] bg-white rounded-xl border-0 shadow-[0_2px_12px_rgba(0,23,45,0.06),0_1px_2px_rgba(0,23,45,0.04)]">
        <component v-if="!route.meta.link" :is="Component"/>
      </div>
    </router-view>
  </div>
</template>

<script setup>
</script>
