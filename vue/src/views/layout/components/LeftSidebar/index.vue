<template>
  <aside v-if="leftMenuItems.length > 0" class="fixed top-16 left-0 w-[220px] h-[calc(100vh-64px)] overflow-y-auto bg-white/95 backdrop-blur-sm border-r border-gray-200/70 z-[1000]">
    <nav class="py-3">
      <LeftSidebarItem v-for="(item, index) in leftMenuItems"
                       :key="item.path + index"
                       :item="item"
                       :base-path="activeTopMenu.path + '/' + item.path"
      />
    </nav>
  </aside>
</template>

<script setup>
import {computed} from "vue";
import {useRoute} from "vue-router";
import LeftSidebarItem from "./Item.vue";
import useRouteStore from "@/stores/modules/routeStore.js";

const route = useRoute()
const routeStore = useRouteStore()

const topMenuItems = computed(() => routeStore.sidebarRouters.filter(r => !r.hidden))

const activeTopMenu = computed(() => {
  const path = route.path
  let best = null
  let bestLen = 0
  for (const item of topMenuItems.value) {
    const itemPath = item.path
    if (path === itemPath || path.startsWith(itemPath + '/')) {
      if (itemPath.length > bestLen) { best = item; bestLen = itemPath.length }
    }
  }
  return best
})

const leftMenuItems = computed(() => {
  const top = activeTopMenu.value
  if (!top?.children) return []
  const visible = top.children.filter(c => !c.hidden)
  if (visible.length <= 1 && !top.alwaysShow) return []
  return visible
})
</script>
