<template>
  <div class="max-w-[1000px] mx-auto px-4 py-6">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-extrabold text-warm-text">我的关注</h1>
      <p class="text-xs text-warm-sub">共关注 {{ followList.length }} 位陪玩师</p>
    </div>

    <div v-if="followList.length" class="mt-4 bg-white border border-warm-border rounded-2xl divide-y divide-warm-border overflow-hidden">
      <div v-for="c in followList" :key="c.companionId" class="flex items-center gap-4 px-5 py-4 hover:bg-warm-bg/50 transition-colors">
        <div class="cursor-pointer" @click="router.push(`/user/companion/${c.companionId}`)">
          <BaseAvatar :name="c.nickName" :image="c.avatar" :size="48" />
        </div>
        <div class="flex-1 min-w-0 cursor-pointer" @click="router.push(`/user/companion/${c.companionId}`)">
          <div class="flex items-center gap-2">
            <p class="font-bold text-warm-text truncate">{{ c.nickName }}</p>
            <span v-if="c.certified" class="u-icon w-3.5 h-3.5 text-warm-primary" v-html="ICONS.verified"></span>
            <span class="text-xs text-warm-sub">{{ c.gender === 1 ? '女' : '男' }}{{ c.city ? ` · ${c.city}` : '' }}</span>
          </div>
          <p class="text-xs text-warm-sub mt-0.5 truncate">{{ c.mainGameName || '暂无主游戏' }}<template v-if="c.mainRank"> · {{ c.mainRank }}</template> · ¥{{ c.price ?? '-' }}/时</p>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            class="px-3.5 py-1.5 text-xs font-semibold rounded-lg border border-warm-border text-warm-sub transition-all active:scale-95 hover:text-warm-danger hover:border-warm-danger"
            @click="unfollow(c)"
          >取消关注</button>
          <button
            class="px-3.5 py-1.5 text-xs font-semibold text-white bg-warm-primary rounded-lg hover:bg-warm-deep transition-all active:scale-95"
            @click="router.push(`/user/booking/${c.companionId}`)"
          >立即预约</button>
        </div>
      </div>
    </div>

    <EmptyState
      v-else-if="!loading"
      icon="users"
      text="还没有关注的陪玩师, 关注后可收到TA的动态通知"
      action-text="去找陪玩"
      class="bg-white border border-warm-border rounded-2xl mt-4"
      @action="router.push('/user/companions')"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import useBizStore from '@/stores/modules/bizStore.js'
import { selectMyFollowList } from '@/api/biz/follow.js'
import { ICONS } from './icons'
import { ElMessage } from '@/utils/toast.js'
import BaseAvatar from './components/BaseAvatar.vue'
import EmptyState from './components/EmptyState.vue'

const router = useRouter()
const bizStore = useBizStore()

/* 关注列表来自后端(follow join companion, 含陪玩师详情与主游戏名) */
const followList = ref([])
const loading = ref(true)

onMounted(() => {
  selectMyFollowList().then(res => {
    followList.value = res.data || []
  }).finally(() => { loading.value = false })
})

const unfollow = async (c) => {
  const on = await bizStore.toggleFollow(c.companionId)  // 后端取关并同步本地 id 列表
  if (on === null) return  // 失败原因已由拦截器提示
  followList.value = followList.value.filter(x => x.companionId !== c.companionId)
  ElMessage.success('已取消关注')
}
</script>