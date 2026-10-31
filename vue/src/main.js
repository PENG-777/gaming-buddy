import { createApp, defineAsyncComponent } from 'vue'
import { createPinia } from 'pinia'

import '@/assets/styles/tailwind.css'

import App from './App.vue'
import router from './router'
//引入路由守卫
import './permission'

import SvgIcon from '@/components/SvgIcon'
import 'virtual:svg-icons-register'

//分页组件
import Pagination from '@/components/Pagination'

//自定义 Modal 组件
import Modal from '@/components/Modal'

//自定义 Select 下拉组件
import Select from '@/components/Select'

//图标选择组件(异步加载, 减小首屏主包体积)
const IconSelect = defineAsyncComponent(() => import('@/components/IconSelect'))

// 图片预览组件(异步加载, 减小首屏主包体积)
const ImagePreview = defineAsyncComponent(() => import('@/components/ImagePreview'))

// 图片上传组件(异步加载, 减小首屏主包体积)
const ImageUpload = defineAsyncComponent(() => import('@/components/ImageUpload'))

// 文件上传组件(异步加载, 减小首屏主包体积)
const FileUpload = defineAsyncComponent(() => import('@/components/FileUpload'))

// 富文本编辑器组件(体积大, 异步加载)
const Editor = defineAsyncComponent(() => import('@/components/Editor'))

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.component('Pagination', Pagination)

app.component('svg-icon', SvgIcon)

app.component('IconSelect', IconSelect)

app.component('ImagePreview', ImagePreview)

app.component('ImageUpload', ImageUpload)

app.component('FileUpload', FileUpload)

app.component('Editor', Editor)

app.component('Modal', Modal)

app.component('Select', Select)

app.mount('#app')
