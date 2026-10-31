//导入路由实例
import router from './router'
import {getToken} from "@/utils/auth.js";
import useUserStore from "@/stores/modules/userStore.js";
import {isReLogin} from "@/utils/request.js";
import {ElMessage} from "@/utils/toast.js";
import useRouteStore from "@/stores/modules/routeStore.js";

//白名单 定义不需要登录就可以访问的路由路径
const whiteList = ['/login', '/register']

//判断路径是否在白名单中
const isWhiteList = (path) => {
    return whiteList.includes(path)
}

//加载失败统一处理: 提示原因 -> 退出登录 -> 跳回登录页
const failHandler = (err, next) => {
    isReLogin.show = false  //复位弹窗标志, 避免后续 401 弹窗被抑制
    const msg = typeof err === 'string' ? err : (err?.msg || err?.message || '获取用户信息失败')
    ElMessage.error(msg)
    useUserStore().logOut().then(() => {
        next({path: '/login'})
    })
}

//全局路由守卫 每次路由跳转前都会执行这个函数
router.beforeEach((to, from, next) => {
    //先检查用户是否有token (相当于检查有没有会员卡)
    if (getToken()) {
        //情况1: 用户有token(已登录)

        //情况1.1 用户已经登录, 但是要去登录页/注册页
        if (to.path === '/login' || to.path === '/register') {
            //已经登录了还要去登录页? 直接跳转到首页
            next({path: '/'})
            return
        }

        //情况1.2 用户已登录 访问其他页面
        //检查store中是否已加载过用户信息(用独立标志判断, 空用户名也不会误判)
        if (!useUserStore().loaded) {
            //用户信息未加载, 需要先获取用户信息

            //设置"正在重新登录"的标志
            isReLogin.show = true

            //调用获取用户信息的方法
            useUserStore().getInfo().then(res => {
                //清除标志
                isReLogin.show = false

                //调用路由状态工具方法
                useRouteStore().generateRoutes().then(accessRoutes => {
                    //根据角色权限生成可访问的路由表
                    accessRoutes.forEach(route => {
                        router.addRoute(route) //动态添加可访问的路由表
                    })

                    //根据角色名称确定跳转路径
                    const userRoleName = res.data.roleName
                    //如果是跟路径, 则根据角色名称跳转页面(未知角色兜底进用户前台)
                    let redirectPath = to.path
                    if (to.path === '/' || to.path === '/index' || to.path === '/user') {
                        if (userRoleName === 'admin') {
                            redirectPath = '/index'
                        } else if (userRoleName === 'user') {
                            redirectPath = '/user/home'
                        } else if (userRoleName === 'companion') {
                            redirectPath = '/privateChat'
                        } else if (userRoleName === 'service') {
                            redirectPath = '/chat'
                        }
                    }
                    //如果需要跳转到特定页面
                    if (redirectPath !== to.path) {
                        next({path: redirectPath, replace: true})
                    } else {
                        next({...to, replace: true})
                    }
                }).catch(err => {
                    //动态路由获取失败, 与用户信息失败走相同的降级
                    failHandler(err, next)
                })
            }).catch(err => {
                //获取用户信息失败(token可能过期了)
                failHandler(err, next)
            })
        } else {
            //用户信息已存在, 直接放行
            next()
        }
    } else {
        //没有token
        if (isWhiteList(to.path)) {
            //在免登录白名单, 直接进入
            next()
        } else {
            //否则全部重定向到登录页
            next({path: '/login'})
        }
    }
})
