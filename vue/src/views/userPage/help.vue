<template>
  <div class="max-w-[900px] mx-auto px-4 py-6">
    <!-- 顶部: 客服入口 -->
    <div class="bg-warm-primary rounded-2xl p-6 text-white flex items-center gap-5 relative overflow-hidden">
      <span class="u-icon w-32 h-32 text-white/10 absolute -right-4 -top-4 pointer-events-none" v-html="ICONS.headset"></span>
      <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center flex-shrink-0">
        <span class="u-icon w-6 h-6" v-html="ICONS.customer"></span>
      </div>
      <div class="flex-1 min-w-0">
        <h1 class="text-lg font-extrabold">帮助中心</h1>
        <p class="mt-1 text-sm opacity-80">常见问题自助排查, 或联系在线客服 7x24 小时为您服务</p>
      </div>
      <button
        class="px-5 h-10 text-sm font-bold bg-white text-warm-primary rounded-xl hover:bg-warm-bg active:scale-[0.97] transition-all flex-shrink-0"
        @click="goService"
      >在线客服</button>
    </div>

    <div class="mt-4 grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-4 items-start">
      <!-- FAQ 手风琴 -->
      <div class="space-y-4">
        <div v-for="g in faqGroups" :key="g.group" class="bg-white border border-warm-border rounded-2xl p-5">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-warm-bg flex items-center justify-center">
              <span class="u-icon w-4 h-4 text-warm-primary" v-html="iconOf(g.icon)"></span>
            </div>
            <h2 class="text-base font-extrabold text-warm-text">{{ g.group }}</h2>
            <span class="text-xs text-warm-sub">{{ g.items.length }} 个问题</span>
          </div>
          <div class="mt-3 divide-y divide-warm-border">
            <div v-for="(item, i) in g.items" :key="i">
              <button
                class="w-full flex items-center justify-between gap-3 py-3.5 text-left"
                @click="toggle(`${g.group}-${i}`)"
              >
                <span class="text-sm font-semibold text-warm-text">{{ item.q }}</span>
                <span
                  class="u-icon w-4 h-4 text-warm-sub transition-transform duration-200 flex-shrink-0"
                  :class="{ 'rotate-180': opened === `${g.group}-${i}` }"
                  v-html="ICONS.arrowDown"
                ></span>
              </button>
              <Transition name="faq">
                <div v-show="opened === `${g.group}-${i}`" class="pb-4 pr-6">
                  <p class="text-sm leading-6 text-warm-sub bg-warm-page rounded-xl px-4 py-3">{{ item.a }}</p>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧: 反馈 + 联系 -->
      <div class="space-y-4 lg:sticky lg:top-20">
        <!-- 意见反馈 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5">
          <h2 class="text-base font-extrabold text-warm-text">意见反馈</h2>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="t in FEEDBACK_TYPES"
              :key="t"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              :class="fbType === t ? 'bg-warm-primary text-white' : 'bg-warm-page text-warm-sub hover:text-warm-primary'"
              @click="fbType = t"
            >{{ t }}</button>
          </div>
          <textarea
            v-model="fbContent"
            rows="4"
            maxlength="200"
            placeholder="告诉我们你的建议或遇到的问题, 我们会认真对待每一条反馈"
            class="mt-3 w-full rounded-xl border border-warm-border px-4 py-3 text-sm text-warm-text placeholder:text-warm-sub outline-none focus:border-warm-primary transition-colors resize-none"
          ></textarea>
          <p class="mt-1 text-right text-xs text-warm-sub">{{ fbContent.length }}/200</p>
          <button
            class="w-full mt-2 h-10 text-sm font-semibold text-white bg-warm-primary rounded-xl hover:bg-warm-deep active:scale-[0.98] transition-all disabled:opacity-50"
            :disabled="!fbType || !fbContent.trim()"
            @click="submitFeedback"
          >提交反馈</button>
        </div>

        <!-- 其他渠道 -->
        <div class="bg-white border border-warm-border rounded-2xl p-5 space-y-3.5">
          <h2 class="text-base font-extrabold text-warm-text">其他渠道</h2>
          <p class="flex items-center gap-2.5 text-xs text-warm-sub">
            <span class="u-icon w-4 h-4 text-warm-primary" v-html="ICONS.chat"></span>
            官方交流群: 8264 陪玩爱好者基地
          </p>
          <p class="flex items-center gap-2.5 text-xs text-warm-sub">
            <span class="u-icon w-4 h-4 text-warm-primary" v-html="ICONS.phone"></span>
            客服热线: 400-826-4000 (9:00-23:00)
          </p>
          <p class="flex items-center gap-2.5 text-xs text-warm-sub">
            <span class="u-icon w-4 h-4 text-warm-primary" v-html="ICONS.bell"></span>
            举报邮箱: report@yiqikaihei.demo
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ICONS, iconOf } from './icons'
import { insertFeedback } from '@/api/biz/feedback.js'
import { selectPublishedFaqList } from '@/api/biz/faq.js'
import { ElMessage } from '@/utils/toast.js'

const router = useRouter()

/* FAQ 手风琴(单开模式), 数据来自帮助中心接口 */
const opened = ref('')
const toggle = (key) => { opened.value = opened.value === key ? '' : key }

/* FAQ 分组展示顺序与图标(与后台帮助中心管理分组一致) */
const FAQ_CATEGORY_ORDER = ['新手指南', '下单支付', '服务保障']
const FAQ_CATEGORY_ICONS = { 新手指南: 'book', 下单支付: 'wallet', 服务保障: 'shield' }
const faqGroups = ref([])

const loadFaqs = () => {
  selectPublishedFaqList().then(res => {
    const list = res.data || []  // 接口已按分组+组内排序返回
    faqGroups.value = FAQ_CATEGORY_ORDER
      .map(group => ({
        group,
        icon: FAQ_CATEGORY_ICONS[group],
        items: list.filter(f => f.category === group).map(f => ({ q: f.question, a: f.answer })),
      }))
      .filter(g => g.items.length > 0)  // 空分组不展示
  })
}

onMounted(loadFaqs)

/* 意见反馈 */
const FEEDBACK_TYPES = ['功能建议', '体验问题', '内容举报', '其他']
const fbType = ref('')
const fbContent = ref('')

const submitFeedback = () => {
  insertFeedback({ feedbackType: fbType.value, content: fbContent.value }).then(() => {
    ElMessage.success('反馈提交成功, 感谢您的支持')
    fbType.value = ''
    fbContent.value = ''
  })
}

const goService = () => router.push({ path: '/user/messages', query: { conv: 'service' } })
</script>

<style scoped>
/* FAQ 展开动画 */
.faq-enter-active,
.faq-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.faq-enter-from,
.faq-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>