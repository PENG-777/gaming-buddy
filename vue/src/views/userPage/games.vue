<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">
    <SectionHeader icon="gamepad" title="游戏专区" sub="覆盖主流手游 / 端游 / 主机与语音娱乐, 点击进入对应游戏陪玩列表" />

    <div v-if="companionStore.games.length" class="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="g in companionStore.games"
        :key="g.id"
        class="group bg-white border border-warm-border rounded-2xl p-5 cursor-pointer hover:-translate-y-1 hover:border-warm-accent hover:shadow-[0_8px_24px_rgba(240,124,42,0.12)] transition-all"
        @click="router.push(`/user/companions?game=${g.id}`)"
      >
        <div class="flex items-start justify-between">
          <GameImage :game="g" size="lg"/>
          <div class="flex flex-col items-end gap-1.5">
            <span class="flex items-center gap-1 text-xs font-bold text-warm-danger">
              <span class="u-icon w-3.5 h-3.5" v-html="ICONS.fire"></span>热度 {{ g.hot }}
            </span>
            <span class="text-xs text-warm-sub">{{ g.count }} 位陪玩师</span>
          </div>
        </div>

        <div class="mt-4 flex items-center justify-between">
          <h3 class="font-extrabold text-warm-text">{{ g.name }}</h3>
          <div class="flex gap-1.5">
            <TagBadge v-for="t in g.tags" :key="t" :text="t" type="plain" />
          </div>
        </div>
        <p class="mt-1.5 text-xs leading-5 text-warm-sub">{{ g.desc }}</p>

        <div class="mt-4 pt-3 border-t border-warm-border flex items-center justify-between">
          <span class="text-xs text-warm-sub">
            低至 <b class="text-lg font-extrabold text-warm-primary">¥{{ g.minPrice }}</b>/小时
          </span>
          <span class="flex items-center gap-1 text-xs font-semibold text-warm-primary opacity-0 group-hover:opacity-100 transition-opacity">
            去找陪玩<span class="u-icon w-3 h-3" v-html="ICONS.arrowRight"></span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import { ICONS } from './icons'
import GameImage from './components/GameImage.vue'
import SectionHeader from './components/SectionHeader.vue'
import TagBadge from './components/TagBadge.vue'

const router = useRouter()
const companionStore = useCompanionStore()

/* 游戏分类来自后端(loadAll 幂等, 热度/陪玩师数/最低价为真实陪玩师数据聚合) */
onMounted(() => companionStore.loadAll())
</script>