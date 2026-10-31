<template>
  <!-- 第一步: 检查这个菜单项是都应该显示 -->
  <div v-if="!item.hidden">
    <!-- 情况1: 当这个菜单项只需要显示为一个简单的菜单项(没有子菜单) -->
    <template v-if="shouldShowSingleItem">
      <app-link :to="singleItemPath">
        <el-menu-item :index="singleItemPath">
          <svg-icon :icon-class="onlyOneChild.meta.icon || (item.meta && item.meta.icon)"
                    style="margin-right: 6px"/>
          <template #title>
            <span style="margin-left: 2px">
              {{ onlyOneChild.meta.title }}
            </span>
          </template>
        </el-menu-item>
      </app-link>
    </template>

    <!-- 情况2: 当这个菜单项需要显示为有子菜单的折叠菜单 -->
    <el-sub-menu v-else :index="resolvePath(item.path)" teleported>
      <template v-if="item.meta" #title>
        <span @click.stop="goFirstChild" style="display: flex;align-items: center">
          <svg-icon :icon-class="item.meta.icon" style="margin-right: 6px"/>
          <span style="margin-left: 2px">
                {{ item.meta.title }}
          </span>
        </span>
      </template>

      <!-- 递归渲染子菜单项 -->
      <sidebar-item v-for="child in item.children"
                    :key="child.path"
                    :item="child"
                    :base-path="resolvePath(child.path)"
                    is-next
      />
    </el-sub-menu>
  </div>
</template>

<script setup>
import {computed} from "vue";
import {useRouter} from "vue-router";
import AppLink from "@/views/layout/components/Sidebar/AppLink.vue";
import SvgIcon from "@/components/SvgIcon/index.vue";

const router = useRouter()

const props = defineProps({
  //菜单项的数据对象, 必须传入
  item: {
    type: Object,
    required: true
  },
  //标记是否是嵌套调用
  isNext: {
    type: Boolean,
    default: false
  },
  //基础路径, 用于拼接完整的路由路径
  basePath: {
    type: String,
    default: ''
  }
})

//递归查找第一个非隐藏、无子菜单的叶子节点路径
const findFirstLeaf = (node, base) => {
  //当前节点完整路径
  const fullPath = resolvePath(node.path, base)

  //获取非隐藏的子项
  const children = (node.children || []).filter(c => !c.hidden)

  //没有子菜单, 当前就是叶子节点
  if (children.length === 0) {
    return fullPath
  }

  //有子菜单, 递归查找第一个子项的叶子节点
  return findFirstLeaf(children[0], fullPath)
}

//点击父级菜单时, 跳转到第一个子菜单
const goFirstChild = () => {
  //获取非隐藏的子项
  const visibleChildren = (props.item.children || []).filter(c => !c.hidden)
  if (visibleChildren.length === 0) return

  //从第一个子项开始递归查找叶子节点, base 使用当前组件的 basePath
  const targetPath = findFirstLeaf(visibleChildren[0], props.basePath)
  if (targetPath) {
    router.push(targetPath)
  }
}

//计算当前菜单项的唯一显示子项
const onlyOneChild = computed(() => {
  //获取当前菜单项的子项数组, 如果没有子项就使用空数组
  const children = props.item.children || []

  //过滤出所有不需要隐藏的子项
  const showingChildren = children.filter(item => !item.hidden)

  //情况1: 如果只有一个需要显示的子项
  if (showingChildren.length === 1) {
    //返回这个唯一的子项
    return showingChildren[0]
  }

  //情况2: 如果没有需要显示的子项
  if (showingChildren.length === 0) {
    return {
      ...props.item, //复制父项的所有属性
      path: '', //路径设置为空
      noShowingChildren: true //标记没有显示的子项
    }
  }

  //情况3: 如果有多个需要显示的子项
  return null
})

//判断是否应该将当前菜单项显示为单个菜单项
const shouldShowSingleItem = computed(() => {
  //条件1: 存在onlyOneChild (有唯一的子项或者没有子项)
  //条件2: 这个唯一的子项没有子带单, 或者标记了noShowingChildren
  //条件3: 父向没有设置显示为折叠菜单
  return onlyOneChild.value && (!onlyOneChild.value.children || onlyOneChild.value.noShowingChildren)
      && !props.item.alwaysShow
})

//计算单个菜单项点击后应该跳转的完整路径
const singleItemPath = computed(() => {
  return resolvePath(onlyOneChild.value.path)
})

//解析并拼接路由路径, 处理特殊情况
const resolvePath = (routePath, base) => {
  //拼接基础路径和相对路径, base 未传则使用 props.basePath
  const basePath = base !== undefined ? base : props.basePath
  const fullPath = basePath + '/' + routePath

  //如果路径为空, 直接返回
  if (!fullPath) return fullPath

  //处理特殊情况
  return fullPath.replace('//', '/')
      .replace(/\/$/, '')
}

</script>

<style scoped>

</style>
