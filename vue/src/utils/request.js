import axios from "axios";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import {getToken} from '@/utils/auth'
import useUserStore from "@/stores/modules/userStore.js";

/* 第一部分: 全局设置 */

//是否正在显示重新登录的弹窗(防止重复弹出多个)
//想象成是一个正在处理登录过期的标志牌
export let isReLogin = { show: false }

//告诉axios我们的默认请求格式是JSON
axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8'

//创建一个定制版的axios实例 (就像邮局给你分配了一个专属的快递员)
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API, //服务器地址(从配置文件中读取)
  timeout: 20000, //20秒之内没有收到回复就认为请求失败了
})

/* 第二部分: 处理重新登录的函数 */
const handleReLogin = () => {
  //如果已经显示登录弹窗, 就别再弹一个了(避免重复弹窗)
  if (isReLogin.show) return

  //打开弹窗
  isReLogin.show = true

  //弹出确认框问用户怎么办
  ElMessageBox.confirm(
      '登录状态已过期,您可以继续留在当前页面,或者重新登录',
      '系统提示',
      {
        confirmButtonText: '重新登录',
        cancelButtonText: '取消',
        type: 'warning',
      }
  )
      .then(() => {
        //用户点击了重新登录
        isReLogin.show = false
        //调用退出登录的方法(清空用户信息)
        useUserStore().logOut().then(() => {
          //退出后跳转到登录页面(重新登录)
          location.href = '/login' //相当于在浏览器地址栏输入这个地址
        })
      })
      .catch(() => {
        //用户点击了取消
        isReLogin.show = false
      })
}

/* 第三部分: 请求拦截器(发送请求前要干的事情) */

service.interceptors.request.use(
    config => {
      //1.检查是否需要添加token (有些请求不需要身份认证)
      const isToken = config.headers?.isToken !== false
      const isRepeatSubmit = config.headers?.repeatSubmit !== false

      //如果有token并且这个请求需要token
      if (getToken() && isToken) {
        //在请求头里面加上token
        config.headers['Authorization'] = 'Bearer ' + getToken()
      }

      //2.防止重复提交
      if (!isRepeatSubmit && ['post', 'put'].includes(config.method)) {
        //FormData(文件上传)不参与防重检测
        if (!(config.data instanceof FormData)) {
          //同一请求(url+参数)单独记一条时间戳, 不同请求互不覆盖
          const repeatKey = 'repeat:' + config.url + ':' + JSON.stringify(config.data)
          const now = new Date().getTime()

          //从浏览器临时存储中取出上一次的请求时间
          const lastTime = sessionStorage.getItem(repeatKey)

          //检查是否重复提交(同一条请求 1 秒内重复提交则拦截)
          if (lastTime && now - Number(lastTime) < 1000) {
            //如果是重复提交, 就拒绝这次请求
            const message = '请勿重复点击'
            ElMessage.error(message)
            return Promise.reject(new Error(message))
          }

          //不是重复提交, 就保存这次请求时间(用于下次比较)
          sessionStorage.setItem(repeatKey, String(now))
        }
      }
      //处理完所有请求, 放行请求
      return config;
    },
    error => {
      ElMessage.error(error)
    }
)

/* 第四部分: 响应拦截器(收到响应后要干的事情) */
service.interceptors.response.use(
    res => {
      if (['blob'].includes(res.request.responseType)) {
        //直接返回原始数据(不需要进行下面的业务逻辑处理)
        return res.data
      }

      //从响应数据中取出业务状态码和提示消息
      const code = res.data.code || 200
      const msg = res.data.msg || '操作失败'

      //根据不同的状态码进行不同的处理
      if (code === 401) {
        handleReLogin()
        return Promise.reject('登录已过期, 请重新登录')
      }

      //如果不是200
      if (code !== 200) {
        ElMessage.error(msg)
        return Promise.reject(new Error(msg))
      }
      //一切正常, 返回数据部分
      return res.data
    },
    error => {
      //这里处理网络HTTP错误(比如500,404等等)
      let { message, response } = error

      //1.如果是401错误
      if (response?.status === 401) {
        handleReLogin()
        return Promise.reject('登录已过期, 请重新登录')
      }

      //2.错误信息翻译(优先展示后端返回的具体文案, 便于定位问题)
      if (response) {
        //有响应: 后端统一返回 {code, msg}, 有具体文案优先展示(如 参数错误: pageSize 应为整数)
        message = (response.data && typeof response.data.msg === 'string' && response.data.msg)
            || '系统接口' + response.status + '异常'
      } else if (message.includes('Network Error')) {
        //网络断了
        message = '后端接口连接异常'
      } else if (message.includes('timeout')) {
        //请求超时
        message = '系统接口请求超时'
      }

      //3.显示错误提示
      ElMessage.error(message)

      //4.把错误传递下去
      return Promise.reject(error)
    }
)

//导出这个定制版的axios实例
export default service
