import {createRouter, createWebHistory} from 'vue-router'
//导入布局组件
import Layout from '@/views/layout'

//路由配置
export const constantRouters = [
  {
    path: '/login',
    component: () => import('@/views/login'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register'),
    hidden: true
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    // 管理端个人中心(挂在 Layout 下, 用 /profile 独立路径避免与下方 /user/profile 用户端个人中心重复)
    path: '/profile',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/system/user/profile'),
        meta: {title: '个人中心'}
      },
    ]
  },
  {
    path: '/user',
    component: () => import('@/views/userPage/index'),
    redirect: '/user/home',
    hidden: true,
    children: [
      {
        path: 'home',
        component: () => import('@/views/userPage/home'),
        hidden: true,
      },
      {
        path: 'games',
        component: () => import('@/views/userPage/games'),
        hidden: true,
      },
      {
        path: 'profile',
        component: () => import('@/views/userPage/profile'),
        hidden: true,
      },
      {
        path: 'companions',
        component: () => import('@/views/userPage/companions'),
        hidden: true,
      },
      {
        path: 'companion/:id',
        component: () => import('@/views/userPage/companionDetail'),
        hidden: true,
      },
      {
        path: 'booking/:companionId',
        component: () => import('@/views/userPage/booking'),
        hidden: true,
      },
      {
        path: 'help',
        component: () => import('@/views/userPage/help'),
        hidden: true,
      },
      {
        path: 'notices',
        component: () => import('@/views/userPage/notices'),
        hidden: true,
      },
      {
        path: 'orders',
        component: () => import('@/views/userPage/orders'),
        hidden: true,
      },
      {
        path: 'order/:id',
        component: () => import('@/views/userPage/orderDetail'),
        hidden: true,
      },
      {
        path: 'messages',
        component: () => import('@/views/userPage/messages'),
        hidden: true,
      },
      {
        path: 'follows',
        component: () => import('@/views/userPage/follows'),
        hidden: true,
      },
      {
        path: 'reviews',
        component: () => import('@/views/userPage/reviews'),
        hidden: true,
      },
      {
        path: 'wallet',
        component: () => import('@/views/userPage/wallet'),
        hidden: true,
      },
      {
        path: 'coupons',
        component: () => import('@/views/userPage/coupons'),
        hidden: true,
      },
      {
        path: 'self',
        component: () => import('@/views/system/user/profile'),
        hidden: true,
      },
    ]
  }
]

//创建路由器实例
const router = createRouter({
  history: createWebHistory(),
  routes: constantRouters,
  scrollBehavior(to, from, savedPosition) {
    //滚动行为配置: 控台路由切换时的页面滚动位置
    if (savedPosition) {
      //如果有保存的位置, 恢复到之前的位置
      return savedPosition
    }
    //否则滚动到顶部
    return {top: 0}
  }
})

export default router