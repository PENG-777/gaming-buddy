<template>
  <!-- 陪玩师卡片: 列表/首页/关注页复用 -->
  <div
    class="group flex flex-col h-full bg-white border border-warm-border rounded-2xl overflow-hidden cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_8px_24px_rgba(240,124,42,0.12)]"
    @click="goDetail"
  >
    <!-- 封面: 游戏图片封面, 无图时浅橙底 + 图标装饰兜底 -->
    <div class="relative h-[84px]">
      <img v-if="gameSrc" :src="gameSrc" :alt="game.name" class="absolute inset-0 w-full h-full object-cover"/>
      <div v-else class="absolute inset-0 bg-[#fff3e8] flex items-center">
        <span
          class="u-icon w-14 h-14 ml-5 opacity-40 text-[#f07c2a] transition-transform duration-300 group-hover:scale-110"
          v-html="iconOf('gamepad')"
        ></span>
      </div>
      <!-- 关注 -->
      <button
        class="absolute right-3 top-3 h-8 px-2.5 rounded-full flex items-center justify-center gap-1 transition-all active:scale-95"
        :class="followed
          ? 'bg-warm-primary text-white'
          : 'bg-white/90 backdrop-blur text-warm-sub hover:text-warm-primary'"
        :title="followed ? '取消关注' : '关注'"
        @click.stop="toggleFollow"
      >
        <span class="u-icon w-3.5 h-3.5" v-html="followed ? ICONS.check : ICONS.plus"></span>
        <span class="text-xs font-bold">{{ followed ? '已关注' : '关注' }}</span>
      </button>
    </div>

    <!-- 头像与基本信息(flex-col + 垫片: 评分价格区跨卡片贴底对齐, 保证等高) -->
    <div class="px-4 pb-4 flex-1 flex flex-col">
      <div class="flex items-end gap-2.5 -mt-8">
        <div class="relative">
          <div class="rounded-full ring-3 ring-white">
            <BaseAvatar :name="companion.name" :image="companion.avatar" :size="56" />
          </div>
          <!-- 性别角标 -->
          <span
            class="absolute -right-1 -bottom-1 w-5 h-5 rounded-full flex items-center justify-center ring-2 ring-white"
            :style="{ backgroundColor: companion.gender === 'female' ? '#e8746b' : '#5b7a99' }"
          >
            <span class="u-icon w-3 h-3 text-white" v-html="companion.gender === 'female' ? ICONS.genderFemale : ICONS.genderMale"></span>
          </span>
        </div>
        <div class="flex-1 min-w-0 pt-9">
          <div class="flex items-center gap-1">
            <span class="font-bold text-warm-text truncate">{{ companion.name }}</span>
            <span v-if="companion.certified" class="u-icon w-3.5 h-3.5 text-warm-primary" v-html="ICONS.verified" title="平台认证"></span>
          </div>
          <div class="text-xs text-warm-sub mt-0.5">{{ companion.age }}岁 · {{ companion.city }} · {{ companion.voice }}</div>
        </div>
      </div>

      <!-- 段位 + 主游戏 -->
      <div class="flex items-center gap-2 mt-3">
        <TagBadge :text="companion.rank" type="warning" />
        <TagBadge :text="game.name" type="info" />
      </div>

      <!-- 标签 -->
      <div class="flex flex-wrap gap-1.5 mt-2">
        <TagBadge v-for="tag in companion.tags.slice(0, 3)" :key="tag" :text="tag" type="plain" />
      </div>

      <!-- 弹性垫片: 吸收标签行数差异带来的高度差 -->
      <div class="flex-1"></div>

      <!-- 评分与价格 -->
      <div class="flex items-center justify-between mt-3.5 pt-3 border-t border-warm-border">
        <div class="flex items-center gap-3 text-xs text-warm-sub">
          <span class="flex items-center gap-1">
            <span class="u-icon w-3.5 h-3.5 text-warm-warning" v-html="ICONS.star"></span>
            <b class="text-warm-text">{{ companion.rating }}</b>
          </span>
          <span class="flex items-center gap-1">
            <span class="u-icon w-3.5 h-3.5" v-html="ICONS.order"></span>
            {{ companion.orders }}单
          </span>
        </div>
        <div class="text-right">
          <span class="text-xl font-extrabold text-warm-primary">¥{{ companion.price }}</span>
          <span class="text-xs text-warm-sub">/小时</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS, iconOf } from '../icons'
import useBizStore from '@/stores/modules/bizStore.js'
import { ElMessage } from '@/utils/toast.js'
import BaseAvatar from './BaseAvatar.vue'
import TagBadge from './TagBadge.vue'

const props = defineProps({
  companion: { type: Object, required: true },
})

const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()

/* 主游戏(mainGame 为后端 gameId, 经 store 查游戏信息取封面) */
const game = computed(() => companionStore.gameById(props.companion.mainGame) || { name: props.companion.mainGameName || '综合', image: '' })

/** 封面游戏图片地址(相对路径拼代理前缀) */
const gameSrc = computed(() => {
  const image = game.value?.image
  if (!image) return ''
  return /^https?:/.test(image) ? image : import.meta.env.VITE_APP_BASE_API + image
})
const followed = computed(() => bizStore.isFollow(props.companion.id))

const goDetail = () => router.push(`/user/companion/${props.companion.id}`)

const toggleFollow = async () => {
  const on = await bizStore.toggleFollow(props.companion.id)
  if (on === null) return  // 失败原因已由拦截器提示
  ElMessage.success(on ? '关注成功, 动态将第一时间通知你' : '已取消关注')
}
</script>