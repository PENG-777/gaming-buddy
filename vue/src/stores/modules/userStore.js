import {defineStore} from "pinia";
import {getToken, removeToken, setToken} from "@/utils/auth.js";
import {disconnectChatWs} from "@/utils/chat-ws.js";
import {getInfo, login, logout} from "@/api/login.js";
import defaultAvatar from '@/assets/images/profile.jpg'

const useUserStore = defineStore(
    'user', //这里全局必须唯一
    {
      //第一部分: 状态定义(存储的数据)
      state: () => ({
        token: getToken(), //用户登录后的token
        id: '', //用户ID
        name: '', //用户名
        avatar: '', //用户头像地址
        sex: null, //性别(0男 1女, 空为保密; 用户端个人资料展示用)
        createTime: '', //注册时间('yyyy-MM-dd HH:mm:ss', 计算"加入平台X天")
        roleName: '', //角色名称(admin/companion/user, 页面按角色区分视角)
        loaded: false //是否已加载过用户信息(路由守卫据此判断, 避免用空用户名误判)
      }),

      //第二部分: 操作方法(处理数据的函数)
      actions: {
        /**
         * 登录方法
         * 作用: 发送登录请求, 保存登录凭证
         */
        login(userInfo) {
          //返回一个Promise (表示一个异步操作)
          return new Promise((resolve, reject) => {
            //调用登录接口
            login(userInfo).then(res => {
              //登录成功
              //1.保存token到本地存储(这样刷新页面也不会丢失)
              setToken(res.token)

              //2.更新Store中的token
              this.token = res.token

              //3.告诉调用者:成功了!
              resolve()

            }).catch(error => {
              //登录失败
              reject(error)
            })
          })
        },

        /**
         * 获取用户详细信息
         * 作用: 获取用户的ID 姓名 头像等信息
         */
        getInfo() {
          return new Promise((resolve, reject) => {
            //调用获取用户信息的接口
            getInfo().then(res => {
              //从响应数据中获取用户数据
              const user = res.data

              //处理头像地址
              let avatar = user.avatar || ""

              //判断头像地址是否完整(是否包含 http:// 或者 https://)
              if (avatar.indexOf('http://') === -1 && avatar.indexOf('https://') === -1) {
                //如果头像地址不完整(是相对路径)
                if (avatar) {
                  avatar = import.meta.env.VITE_APP_BASE_API + avatar
                } else {
                  //如果没有头像. 使用默认头像
                  avatar = defaultAvatar
                }
              }

              //更新用户信息
              this.id = user.userId
              this.name = user.userName
              this.avatar = avatar
              this.sex = user.sex ?? null
              this.createTime = user.createTime || ''
              this.roleName = user.roleName || ''
              this.loaded = true //标记用户信息已加载

              //3.告诉调用者:成功了!
              resolve(res) //同时返回完整响应
            }).catch(error => {
              //获取失败
              reject(error)
            })
          })
        },

        /**
         * 用户退出登录
         * 后端接口失败也不阻塞本地清理, 保证一定能退出
         */
        logOut() {
          return new Promise(resolve => {
            //调用退出登录接口(告诉服务器我要退出, 失败不影响本地清理)
            logout().catch(() => {}).finally(() => {
              //0.断开官方客服 WS 连接(停止心跳与重连)
              disconnectChatWs()

              //1.清空store中的token与用户信息
              this.token = ''
              this.loaded = false
              this.roleName = ''
              this.sex = null
              this.createTime = ''

              //2.删除本地存储的token
              removeToken()

              //3.告诉调用者: 本地已清理完毕
              resolve()
            })
          })
        }
      }
    }
)

//导出这个store, 其他地方可以导入使用了
export default useUserStore