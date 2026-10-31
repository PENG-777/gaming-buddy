import {defineStore} from "pinia";
import {getRouters} from "@/api/system/menu.js";
import { constantRouters } from '@/router/index.js'
import Layout from '@/views/layout/index.vue'
import ParentView from '@/views/layout/components/ParentView.vue'

//使用vite的自动导入功能: 一次性导入views目录下的所有.vue的文件
const modules = import.meta.glob('./../../views/**/*.vue')

//预构建 "视图路径 -> 加载器" 映射表(如 'system/user/index' -> 加载函数), 避免每次查找都重复拆路径
const viewModules = {}
for (const path in modules) {
  //完整路径: ./../../views/system/user/index.vue -> 相对路径: system/user/index
  viewModules[path.split('views/')[1].split('.vue')[0]] = modules[path]
}

const useRouteStore = defineStore(
    'permission', //这里全局必须唯一
    {
      state: () => ({
        sidebarRouters: [], //存储侧边栏菜单路由 (固定路由 + 用户专属路由, 用于显示菜单)
      }),
      actions: {
        //核心方法: 生成用户的专属路由
        generateRoutes() {
          return new Promise((resolve, reject) => {
            //调用API从后端获取路由数据(失败时 reject, 避免守卫一直等待导致页面卡死)
            getRouters().then(res => {
              //转换数据格式: 把后端的数据变成前端路由能用的格式
              const sidebarRoutes = convertToRoutes(res.data);

              //侧边栏显示: 固定路由 + 用户路由
              this.sidebarRouters = constantRouters.concat(sidebarRoutes)

              //告诉调用者: 我处理完了, 这是处理好的路由数据
              resolve(sidebarRoutes);
            }).catch(err => reject(err))
          })
        }
      }
    }
)

/**
 * 核心数据转换: 把后端的数据变成前端路由能用的格式
 * 后端给的格式可能是这样的:
 * [
 *   {
 *     "name": "System",
 *     "path": "/system/xxx",
 *     "component": "Layout",
 *     "children": [...]
 *   }
 * ]
 *
 * 前端需要的格式是这样的:
 * [
 *   {
 *     "name": "System",
 *     "path": "/system/xxx",
 *     "component": Layout组件对象,
 *     "children": [...]
 *   }
 * ]
 *
 * @param routes 后端返回的路由数组数据
 */
const convertToRoutes = (routes) => {
  //对每个路由进行处理
  return routes.map(route => {
    //1. 把字符串转换成真正的组件
    if (route.component){
      if (route.component === 'Layout') {
        //如果是Layout, 就用导入的主布局组件
        route.component = Layout
      } else if (route.component === 'ParentView') {
        //空壳父级视图: 只承载子路由的透传容器
        route.component = ParentView
      } else {
        //如果是页面组件, 就动态加载
        //比如把'system/user/index'变成对应的vue组件
        route.component = loadView(route.component)
      }
    }

    //2.递归处理子路由
    if (route.children && route.children.length ) {
      //继续处理子路由
      route.children = convertToRoutes(route.children)
    } else {
      //如果没有子路由, 就删除children属性
      delete route.children
    }

    return route
  })
}

//动态加载视图组件
const loadView = (view) => {
  //从预构建的映射表中查找(找不到时兜底到 404 页, 避免白屏)
  return viewModules[view] || (() => import('@/views/404.vue'))
}

//导出这个store, 其他地方可以导入使用了
export default useRouteStore
