<template>
  <div class="app-container">
    <!-- 指标卡 -->
    <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-4">
      <!-- 总营收 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#fff3e8] text-[#f07c2a]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">总营收(元)</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtMoney(stats?.totalRevenue) }}</div>
        </div>
      </div>
      <!-- 订单总数 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#e4f4f2] text-[#26a69a]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">订单总数</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtCount(stats?.orderCount) }}</div>
        </div>
      </div>
      <!-- 今日订单 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#fdf6e3] text-[#faad14]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="12" y1="14" x2="12" y2="18"/><line x1="10" y1="16" x2="14" y2="16"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">今日订单</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtCount(stats?.todayOrderCount) }}</div>
        </div>
      </div>
      <!-- 注册用户 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#f3f9ec] text-[#9ccc65]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">注册用户</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtCount(stats?.userCount) }}</div>
        </div>
      </div>
      <!-- 陪玩师数 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#fdf0ef] text-[#e8746b]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">陪玩师数</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtCount(stats?.companionCount) }}</div>
        </div>
      </div>
      <!-- 好评率 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex items-center gap-3">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#fff3e8] text-[#d96a1f]">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-0.5">好评率</div>
          <div class="text-lg font-bold text-gray-800 truncate">{{ loading ? '...' : fmtRate(stats?.praiseRate) }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- 订单状态分布 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-1 h-4 rounded-full bg-[var(--color-primary)]"></span>
          <h3 class="text-sm font-bold text-gray-700">订单状态分布</h3>
        </div>
        <div class="relative h-[300px]">
          <div v-show="hasData('statusDist')" ref="statusChartRef" class="h-full"></div>
          <div v-if="!loading && !hasData('statusDist')" class="absolute inset-0 flex items-center justify-center text-sm text-gray-400">暂无数据</div>
        </div>
      </div>

      <!-- 游戏订单分布 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-1 h-4 rounded-full bg-[var(--color-primary)]"></span>
          <h3 class="text-sm font-bold text-gray-700">游戏订单分布</h3>
        </div>
        <div class="relative h-[300px]">
          <div v-show="hasData('gameDist')" ref="gameChartRef" class="h-full"></div>
          <div v-if="!loading && !hasData('gameDist')" class="absolute inset-0 flex items-center justify-center text-sm text-gray-400">暂无数据</div>
        </div>
      </div>

      <!-- 热门服务 TOP5 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-1 h-4 rounded-full bg-[var(--color-primary)]"></span>
          <h3 class="text-sm font-bold text-gray-700">热门服务 TOP5</h3>
        </div>
        <div class="relative h-[300px]">
          <div v-show="hasData('serviceTop')" ref="serviceChartRef" class="h-full"></div>
          <div v-if="!loading && !hasData('serviceTop')" class="absolute inset-0 flex items-center justify-center text-sm text-gray-400">暂无数据</div>
        </div>
      </div>

      <!-- 评价星级分布 -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-1 h-4 rounded-full bg-[var(--color-primary)]"></span>
          <h3 class="text-sm font-bold text-gray-700">评价星级分布</h3>
        </div>
        <div class="relative h-[300px]">
          <div v-show="hasData('ratingDist')" ref="ratingChartRef" class="h-full"></div>
          <div v-if="!loading && !hasData('ratingDist')" class="absolute inset-0 flex items-center justify-center text-sm text-gray-400">暂无数据</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue'
import {getAdminStats} from '@/api/index'

const loading = ref(true)  // 看板数据加载中
const stats = ref(null)  // 后端聚合的看板数据

/* 图表容器 */
const statusChartRef = ref(null)
const gameChartRef = ref(null)
const serviceChartRef = ref(null)
const ratingChartRef = ref(null)

let chartInstances = []  // 已创建的 echarts 实例(统一 resize/dispose)

/* 看板配色(暖橙主题 + 辅助纯色, 无紫无渐变) */
const CHART_COLORS = ['#f07c2a', '#26a69a', '#faad14', '#e8746b', '#9ccc65', '#909399', '#8d6e63']
/* 星级柱状配色(1星 -> 5星, 低星警示色/高星主色) */
const RATING_COLORS = ['#e8746b', '#faad14', '#f5c842', '#ff9a4d', '#f07c2a']

/* 某一图表维度是否有数据 */
const hasData = key => (stats.value?.[key] || []).length > 0

/* 指标卡格式化(未加载/无数据展示 --) */
const fmtMoney = v => (v == null ? '--' : `¥${v}`)
const fmtCount = v => (v == null ? '--' : v)
const fmtRate = v => (v == null ? '--' : `${v}%`)

/* 初始化单个图表并登记实例 */
function renderChart(el, option) {
  const chart = echarts.init(el)
  chart.setOption(option)
  chartInstances.push(chart)
}

/* 环形饼图通用 option(状态分布/游戏分布共用) */
function pieOption(data) {
  return {
    color: CHART_COLORS,
    tooltip: {trigger: 'item', formatter: '{b}: {c}单 ({d}%)'},
    legend: {bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, itemGap: 16, textStyle: {color: '#606266', fontSize: 12}},
    series: [
      {
        type: 'pie',
        radius: ['42%', '68%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: {borderColor: '#fff', borderWidth: 2, borderRadius: 4},
        label: {show: false},
        data,
      },
    ],
  }
}

/* 渲染全部图表(空数据维度跳过, 由模板展示暂无数据) */
function renderCharts() {
  const s = stats.value || {}

  // 订单状态分布 / 游戏订单分布(环形饼图)
  if (hasData('statusDist')) renderChart(statusChartRef.value, pieOption(s.statusDist))
  if (hasData('gameDist')) renderChart(gameChartRef.value, pieOption(s.gameDist))

  // 热门服务 TOP5(横向柱状, inverse 让第一名在顶部)
  if (hasData('serviceTop')) {
    renderChart(serviceChartRef.value, {
      tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
      grid: {left: 8, right: 36, top: 10, bottom: 10, containLabel: true},
      xAxis: {type: 'value', minInterval: 1, splitLine: {lineStyle: {color: '#f0f0f0'}}, axisLabel: {color: '#909399'}},
      yAxis: {
        type: 'category',
        inverse: true,
        data: s.serviceTop.map(item => item.name),
        axisLine: {show: false},
        axisTick: {show: false},
        axisLabel: {color: '#606266', fontSize: 12},
      },
      series: [
        {
          type: 'bar',
          barWidth: 16,
          itemStyle: {color: CHART_COLORS[0], borderRadius: [0, 8, 8, 0]},
          label: {show: true, position: 'right', color: '#606266', fontSize: 12},
          data: s.serviceTop.map(item => item.value),
        },
      ],
    })
  }

  // 评价星级分布(柱状, 1-5星按星级递进配色)
  if (hasData('ratingDist')) {
    renderChart(ratingChartRef.value, {
      tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
      grid: {left: 8, right: 16, top: 24, bottom: 10, containLabel: true},
      xAxis: {
        type: 'category',
        data: s.ratingDist.map(item => item.name),
        axisLine: {lineStyle: {color: '#e5e7eb'}},
        axisTick: {show: false},
        axisLabel: {color: '#606266', fontSize: 12},
      },
      yAxis: {type: 'value', minInterval: 1, splitLine: {lineStyle: {color: '#f0f0f0'}}, axisLabel: {color: '#909399'}},
      series: [
        {
          type: 'bar',
          barWidth: 30,
          itemStyle: {borderRadius: [6, 6, 0, 0], color: params => RATING_COLORS[params.dataIndex]},
          label: {show: true, position: 'top', color: '#606266', fontSize: 12},
          data: s.ratingDist.map(item => item.value),
        },
      ],
    })
  }
}

/* 加载看板数据并渲染图表(失败提示由 request 拦截器统一弹出) */
async function loadStats() {
  loading.value = true
  try {
    const res = await getAdminStats()
    stats.value = res.data
    await nextTick()  // 等 v-show 容器显隐更新后再初始化, 保证尺寸就绪
    renderCharts()
  } catch (e) {
    // 忽略: 拦截器已提示, 页面保持空态
  } finally {
    loading.value = false
  }
}

/* 窗口缩放时统一自适应 */
const handleResize = () => chartInstances.forEach(chart => chart.resize())

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach(chart => chart.dispose())
  chartInstances = []
})
</script>

<style scoped>

</style>