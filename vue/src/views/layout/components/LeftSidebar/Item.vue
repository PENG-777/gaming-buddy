<template>
  <div v-if="!item.hidden">
    <!-- 单个菜单项（不含子菜单） -->
    <template v-if="shouldShowSingleItem">
      <app-link :to="singleItemPath">
        <div
          class="mx-3 my-[3px] h-10 flex items-center px-3 rounded-[10px] text-[15px] cursor-pointer transition-colors duration-200"
          :class="route.path === singleItemPath
            ? 'text-[var(--color-primary)] bg-[var(--color-primary-bg)] font-semibold'
            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'"
        >
          <svg-icon :icon-class="onlyOneChild.meta?.icon || (item.meta && item.meta.icon)" class="w-4 h-4 mr-2.5 flex-shrink-0"/>
          <span class="truncate">{{ onlyOneChild.meta?.title }}</span>
        </div>
      </app-link>
    </template>

    <!-- 含子菜单（可展开折叠） -->
    <div v-else>
      <div
        class="mx-3 my-[3px] h-10 flex items-center justify-between pl-3 pr-3.5 rounded-[10px] text-[15px] cursor-pointer transition-colors duration-200"
        :class="isSubMenuActive
          ? 'text-[var(--color-primary)] bg-[var(--color-primary-bg)] font-semibold'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'"
        @click="subOpen = !subOpen"
      >
        <div class="flex items-center min-w-0">
          <svg-icon v-if="item.meta" :icon-class="item.meta.icon" class="w-4 h-4 mr-2.5 flex-shrink-0"/>
          <span class="truncate">{{ item.meta?.title }}</span>
        </div>
        <svg class="w-3 h-3 flex-shrink-0 ml-2 text-gray-400 transition-transform duration-300 ease-out" :class="{ 'rotate-90': subOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      </div>

      <!-- 子菜单（高度过渡展开 + 层级引导线） -->
      <div class="grid transition-[grid-template-rows,opacity] duration-300 ease-out" :class="subOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'">
        <div class="overflow-hidden">
          <div class="ml-[27px] border-l border-gray-200/80 my-1">
            <LeftSidebarItem v-for="child in item.children"
                             :key="child.path"
                             :item="child"
                             :base-path="resolvePath(child.path)"
                             is-next
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, ref} from "vue";
import {useRoute} from "vue-router";
import AppLink from "@/views/layout/components/Sidebar/AppLink.vue";
import SvgIcon from "@/components/SvgIcon/index.vue";

const props = defineProps({
  item: { type: Object, required: true },
  isNext: { type: Boolean, default: false },
  basePath: { type: String, default: '' }
})

const route = useRoute()
const subOpen = ref(false)

const onlyOneChild = computed(() => {
  const children = props.item.children || []
  const showingChildren = children.filter(item => !item.hidden)
  if (showingChildren.length === 1) return showingChildren[0]
  if (showingChildren.length === 0) return { ...props.item, path: '', noShowingChildren: true }
  return null
})

const shouldShowSingleItem = computed(() => {
  return onlyOneChild.value && (!onlyOneChild.value.children || onlyOneChild.value.noShowingChildren)
      && !props.item.alwaysShow
})

const singleItemPath = computed(() => resolvePath(onlyOneChild.value.path))

const isSubMenuActive = computed(() => {
  const children = props.item.children || []
  return children.some(c => {
    const resolved = resolvePath(c.path)
    return route.path === resolved || route.path.startsWith(resolved + '/')
  })
})

// Auto-open if current route is in this submenu
if (isSubMenuActive.value) {
  subOpen.value = true
}

const resolvePath = (routePath, base) => {
  const basePath = base !== undefined ? base : props.basePath
  const fullPath = basePath + '/' + routePath
  if (!fullPath) return fullPath
  return fullPath.replace('//', '/').replace(/\/$/, '')
}
</script>
