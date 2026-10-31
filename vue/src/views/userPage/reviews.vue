<template>
  <div class="max-w-[900px] mx-auto px-4 py-6">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-extrabold text-warm-text">我的评价</h1>
      <p class="text-xs text-warm-sub">累计评价 {{ bizStore.reviews.length }} 条</p>
    </div>

    <div v-if="list.length" class="mt-4 space-y-4">
      <div v-for="r in pagedList" :key="r.id" class="bg-white border border-warm-border rounded-2xl p-5">
        <!-- 评价对象 -->
        <div class="flex items-center gap-3 cursor-pointer" @click="router.push(`/user/companion/${r.companionId}`)">
          <BaseAvatar :name="companionById(r.companionId)?.name || '陪玩师'" :size="42" />
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-warm-text">{{ companionById(r.companionId)?.name || '已下架陪玩师' }}</p>
            <p class="text-xs text-warm-sub mt-0.5">订单号 {{ r.orderId }}</p>
          </div>
          <div class="flex flex-col items-end gap-1 flex-shrink-0">
            <RatingStars :model-value="r.rating" :size="14" />
            <span class="text-[11px] text-warm-sub">{{ r.time }}</span>
          </div>
        </div>
        <!-- 评价内容 -->
        <p class="mt-3 text-sm leading-6 text-warm-text">{{ r.content }}</p>
        <div v-if="r.tags?.length" class="mt-2.5 flex flex-wrap gap-1.5">
          <TagBadge v-for="t in r.tags" :key="t" :text="t" type="warning" />
        </div>
        <!-- 平台回复(管理端评价管理回复, 可空) -->
        <div v-if="r.reply" class="mt-2.5 bg-warm-page rounded-xl px-4 py-2.5 text-xs leading-5 text-warm-sub">
          <b class="text-warm-primary">平台回复:</b> {{ r.reply }}
        </div>
      </div>

      <!-- 分页(局部覆盖主题色为用户端暖橙) -->
      <div v-if="list.length > pageSize" class="bg-white border border-warm-border rounded-2xl overflow-hidden" style="--color-primary: #f07c2a">
        <Pagination v-model:page="page" v-model:limit="pageSize" :total="list.length" :page-sizes="[5, 10, 20]" />
      </div>
    </div>

    <EmptyState
      v-else
      icon="star"
      text="暂无评价, 完成服务后别忘了分享你的体验"
      action-text="去看看订单"
      class="bg-white border border-warm-border rounded-2xl mt-4"
      @action="router.push('/user/orders')"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useCompanionStore from '@/stores/modules/companionStore.js'
import useBizStore from '@/stores/modules/bizStore.js'
import BaseAvatar from './components/BaseAvatar.vue'
import RatingStars from './components/RatingStars.vue'
import TagBadge from './components/TagBadge.vue'
import EmptyState from './components/EmptyState.vue'

const router = useRouter()
const bizStore = useBizStore()
const companionStore = useCompanionStore()

/* 评价对象信息来自后端(loadAll 幂等) */
onMounted(() => companionStore.loadAll())
const companionById = (id) => companionStore.companionById(id)

const list = computed(() => bizStore.reviews)

const page = ref(1)
const pageSize = ref(5)
const pagedList = computed(() => list.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value))
</script>