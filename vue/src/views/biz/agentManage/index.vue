<template>
  <div class="app-container">
    <!-- 页头: 标题 + 统计 -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-4 flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-6">
      <div class="flex items-center gap-3.5 flex-1 min-w-0">
        <div class="w-12 h-12 rounded-xl bg-[#fff3e8] flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-[#f07c2a]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/><line x1="12" y1="8" x2="12" y2="5"/><circle cx="12" cy="3.5" r="1.2"/></svg>
        </div>
        <div class="min-w-0">
          <h1 class="text-lg font-bold text-gray-800 leading-tight">Agent 编排管理</h1>
          <p class="text-[13px] text-gray-400 mt-1">多 Agent 协作团队 · 提示词 / 采样温度 / 启停热更新, 修改后下一次对话即时生效</p>
        </div>
      </div>
      <div class="flex items-center divide-x divide-gray-100 border-t lg:border-t-0 pt-4 lg:pt-0 flex-shrink-0">
        <div class="px-6 first:pl-0">
          <div class="text-[22px] font-bold text-gray-800 leading-none">{{ loading ? '–' : configs.length }}</div>
          <div class="text-xs text-gray-400 mt-1.5">Agent 总数</div>
        </div>
        <div class="px-6">
          <div class="text-[22px] font-bold leading-none" style="color: var(--color-primary)">{{ loading ? '–' : enabledCount }}</div>
          <div class="text-xs text-gray-400 mt-1.5">启用中</div>
        </div>
        <div class="px-6">
          <div class="text-[22px] font-bold text-gray-800 leading-none">{{ loading ? '–' : fmtNum(totalCalls) }}</div>
          <div class="text-xs text-gray-400 mt-1.5">近 30 天调用</div>
        </div>
      </div>
    </div>

    <!-- 加载骨架 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-[1600px]">
      <div v-for="i in 4" :key="i" class="bg-white border border-gray-200 rounded-xl p-4 animate-pulse">
        <div class="flex items-start gap-3">
          <div class="w-11 h-11 rounded-xl bg-gray-100 flex-shrink-0"></div>
          <div class="flex-1 space-y-2 py-1">
            <div class="h-4 bg-gray-100 rounded w-1/2"></div>
            <div class="h-3 bg-gray-100 rounded w-1/3"></div>
          </div>
        </div>
        <div class="mt-4 space-y-2"><div class="h-3 bg-gray-100 rounded"></div><div class="h-3 bg-gray-100 rounded w-4/5"></div></div>
        <div class="mt-4 h-8 bg-gray-100 rounded-lg"></div>
        <div class="mt-4 pt-3 border-t border-gray-100 flex justify-between"><div class="h-5 bg-gray-100 rounded w-32"></div><div class="h-5 bg-gray-100 rounded w-16"></div></div>
      </div>
    </div>

    <!-- 主体: 左侧按场景分组卡片 + 右侧排行/说明 -->
    <div v-else class="grid grid-cols-1 xl:grid-cols-3 gap-4 items-start">
      <div class="xl:col-span-2 space-y-7 min-w-0">
        <section v-for="g in sceneGroups" :key="g.key">
          <!-- 分组标题 -->
          <div class="flex items-center gap-2.5 mb-3.5">
            <span class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: g.bg, color: g.color }">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="g.icon"></svg>
            </span>
            <div class="flex items-baseline gap-2 min-w-0 flex-1">
              <h2 class="text-[15px] font-bold text-gray-800 flex-shrink-0">{{ g.label }}</h2>
              <span class="text-xs text-gray-400 truncate">{{ g.agents.length }} 个 Agent · {{ g.desc }}</span>
            </div>
          </div>
          <!-- Agent 卡片 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <article v-for="(row, i) in g.agents" :key="row.agentId"
                     class="agent-card group bg-white border border-gray-200 rounded-xl p-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                     :class="row.enabled === 1 ? 'opacity-75' : ''"
                     :style="{ animationDelay: `${i * 45}ms` }">
              <!-- 头部: 图标 + 身份 + 开关 -->
              <div class="flex items-start gap-3">
                <div class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" :class="row.enabled === 1 ? 'grayscale' : ''"
                     :style="{ background: iconStyle(row.agentKey).bg, color: iconStyle(row.agentKey).color }">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS[iconOf(row.agentKey)]"></svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-1.5 flex-wrap">
                    <h3 class="text-[15px] font-bold text-gray-800 leading-tight">{{ row.agentName }}</h3>
                    <span v-if="isSupervisor(row)" class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#1f2d3d] text-white flex-shrink-0">主管</span>
                    <span v-if="row.enabled === 1" class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-400 border border-gray-200 flex-shrink-0">已停用</span>
                  </div>
                  <p class="text-xs text-gray-400 font-mono mt-1 truncate">{{ row.agentKey }}</p>
                </div>
                <button @click="toggleEnabled(row)" role="switch" :aria-checked="row.enabled === 0" title="启用 / 停用"
                        class="relative inline-flex h-[22px] w-[40px] items-center rounded-full transition-colors flex-shrink-0"
                        :style="{ background: row.enabled === 0 ? 'var(--color-primary)' : '#d1d5db' }">
                  <span class="inline-block w-[18px] h-[18px] rounded-full bg-white shadow transition-transform"
                        :style="{ transform: row.enabled === 0 ? 'translateX(20px)' : 'translateX(2px)' }"></span>
                </button>
              </div>

              <!-- 职责描述 -->
              <p class="mt-3 text-[13px] text-gray-500 leading-relaxed line-clamp-2" :title="row.description">{{ row.description || '暂无职责描述' }}</p>

              <!-- 工具清单 -->
              <div v-if="toolList(row.tools).length" class="mt-3 bg-gray-50 border border-gray-100 rounded-lg px-2.5 py-2">
                <div class="flex flex-wrap items-center gap-1">
                  <span class="text-[10px] text-gray-400 mr-0.5 flex-shrink-0 select-none">工具</span>
                  <code v-for="t in visibleTools(row)" :key="t"
                        class="px-1.5 py-0.5 rounded bg-white border border-gray-200 text-[10.5px] text-gray-600 font-mono">{{ t }}</code>
                  <button v-if="hiddenToolCount(row)" @click="toggleTools(row.agentId)"
                          class="px-1.5 py-0.5 rounded text-[10.5px] font-medium transition-colors"
                          :class="isExpanded(row.agentId) ? 'text-gray-500 bg-gray-200/70 hover:bg-gray-200' : 'text-[var(--color-primary)] bg-[var(--color-primary-bg)] hover:bg-[#ffe9d6]'">
                    {{ isExpanded(row.agentId) ? '收起' : `+${hiddenToolCount(row)}` }}
                  </button>
                </div>
              </div>
              <div v-else class="mt-3 bg-gray-50 border border-gray-100 rounded-lg px-2.5 py-2 text-[10.5px] text-gray-400 flex items-center gap-1.5">
                <svg class="w-3 h-3 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v4"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                纯调度角色 · 不直接调用工具
              </div>

              <!-- 底部: 参数徽章 + 编辑 -->
              <div class="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between gap-2">
                <div class="flex items-center gap-1.5 text-[11px] text-gray-500 min-w-0 flex-wrap">
                  <span class="inline-flex items-center gap-1 bg-gray-50 border border-gray-100 rounded-md px-1.5 py-0.5" title="采样温度">
                    <svg class="w-3 h-3 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>
                    {{ Number(row.temperature).toFixed(2) }}
                  </span>
                  <span class="inline-flex items-center gap-1 bg-gray-50 border border-gray-100 rounded-md px-1.5 py-0.5" title="近 30 天调用次数">
                    <svg class="w-3 h-3 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    {{ fmtNum(row.callCount) }} 次
                  </span>
                  <span class="text-gray-400 hidden sm:inline" :title="row.updateTime">· {{ shortTime(row.updateTime) }}</span>
                </div>
                <button @click="handleUpdate(row)" aria-label="编辑 Agent 配置"
                        class="inline-flex items-center gap-1 text-[13px] font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] transition-colors flex-shrink-0">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
                  编辑配置
                </button>
              </div>
            </article>
          </div>
        </section>

        <!-- 空态 -->
        <div v-if="configs.length === 0" class="bg-white border border-gray-200 rounded-xl py-16 flex flex-col items-center gap-3">
          <svg class="w-10 h-10 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/><line x1="12" y1="8" x2="12" y2="5"/><circle cx="12" cy="3.5" r="1.2"/></svg>
          <p class="text-sm text-gray-400">暂无 Agent 配置</p>
        </div>
      </div>

      <!-- 右侧: 调用排行 + 编排说明(sticky) -->
      <aside class="space-y-4 xl:sticky xl:top-5">
        <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-4">
          <div class="flex items-center gap-2 mb-1">
            <span class="w-1 h-4 rounded-full bg-[var(--color-primary)]"></span>
            <h3 class="text-sm font-bold text-gray-700">近 30 天调用排行</h3>
          </div>
          <p class="text-xs text-gray-400 mb-2 pl-3">按各 Agent 应答消息数统计</p>
          <div class="relative w-full" :style="{ height: chartHeight }">
            <div ref="chartRef" class="absolute inset-0"></div>
            <div v-if="!loading && !chartRows.length" class="absolute inset-0 bg-white flex flex-col items-center justify-center gap-2">
              <svg class="w-8 h-8 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
              <span class="text-xs text-gray-400">暂无调用数据</span>
            </div>
          </div>
        </div>

        <div class="bg-[#fff8f1] border border-[#f7c59f]/70 rounded-xl p-4">
          <div class="flex items-center gap-1.5 mb-3">
            <svg class="w-4 h-4 text-[#f07c2a]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.4 1 2.3h6c0-.9.4-1.8 1-2.3A7 7 0 0 0 12 2z"/></svg>
            <h3 class="text-[13px] font-bold text-[#d96a1f]">编排机制</h3>
          </div>
          <ul class="space-y-2.5 text-xs text-gray-600 leading-relaxed">
            <li class="flex gap-2"><span class="w-1 h-1 rounded-full bg-[#f07c2a] mt-1.5 flex-shrink-0"></span>主管 Agent 理解用户意图后, 分派给最合适的专职 Agent 并整合最终答复</li>
            <li class="flex gap-2"><span class="w-1 h-1 rounded-full bg-[#f07c2a] mt-1.5 flex-shrink-0"></span>停用某个专职 Agent 后, 相关请求由主管兜底接管</li>
            <li class="flex gap-2"><span class="w-1 h-1 rounded-full bg-[#f07c2a] mt-1.5 flex-shrink-0"></span>提示词 / 温度 / 描述修改无需重启服务, 下一次对话即时生效</li>
          </ul>
        </div>
      </aside>
    </div>

    <!-- 编辑对话框 -->
    <Modal :title="title" v-model="open" width="720px">
      <form @submit.prevent="submitForm" class="space-y-5">
        <!-- Agent 身份头 -->
        <div class="flex items-center gap-3 p-3.5 bg-gray-50 border border-gray-100 rounded-xl">
          <div class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
               :style="{ background: iconStyle(form.agentKey || '').bg, color: iconStyle(form.agentKey || '').color }">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS[iconOf(form.agentKey || '')]"></svg>
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-sm font-bold text-gray-800">{{ form.agentName }}</span>
              <span v-if="isSupervisor(form)" class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#1f2d3d] text-white">主管</span>
              <span class="px-2 py-0.5 rounded-md text-[11px] font-bold"
                    :class="form.scene === 'user' ? 'text-[#26a69a] bg-[#e4f4f2]' : 'text-[#f07c2a] bg-[#fff3e8]'">{{ form.scene === 'user' ? '用户端' : '经营分析' }}</span>
            </div>
            <p class="text-xs text-gray-400 font-mono mt-1 truncate">{{ form.agentKey }}</p>
          </div>
          <div class="ml-auto text-right flex-shrink-0">
            <p class="text-[11px] text-gray-400">近 30 天调用</p>
            <p class="text-base font-bold text-gray-700 mt-0.5">{{ fmtNum(form.callCount) }}</p>
          </div>
        </div>

        <!-- 职责描述 -->
        <div>
          <label class="block text-[13px] font-medium text-gray-600 mb-1.5">职责描述</label>
          <textarea v-model="form.description" rows="2" maxlength="500" placeholder="职责描述(管理页展示)"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none transition-colors"></textarea>
        </div>

        <!-- 系统提示词 -->
        <div>
          <label class="flex items-center justify-between mb-1.5">
            <span class="text-[13px] font-medium text-gray-600"><span class="text-red-500 mr-0.5">*</span>系统提示词</span>
            <span class="text-[11px] text-gray-400 font-mono">{{ (form.prompt || '').length }} 字</span>
          </label>
          <textarea v-model="form.prompt" rows="10" placeholder="系统提示词(Agent 人设与职责指令, 保存后下次对话生效)"
                    class="w-full px-3 py-2.5 rounded-lg border border-gray-300 text-[13px] text-gray-700 outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-y font-mono leading-relaxed transition-colors"></textarea>
          <p class="mt-1.5 text-xs text-gray-400 flex items-center gap-1">
            <svg class="w-3 h-3 text-[#f07c2a] flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            提示词即 Agent 的人设与行为指令, 由主管按 agent_key 引用; 保存后无需重启, 下一次对话即生效
          </p>
        </div>

        <!-- 采样温度 -->
        <div>
          <label class="flex items-center justify-between mb-2">
            <span class="text-[13px] font-medium text-gray-600">采样温度</span>
            <span class="px-2 py-0.5 rounded-md text-xs font-bold font-mono text-[var(--color-primary)] bg-[var(--color-primary-bg)]">{{ Number(form.temperature || 0).toFixed(1) }}</span>
          </label>
          <input v-model.number="form.temperature" type="range" min="0" max="1" step="0.1" class="temp-slider flex-1 w-full" />
          <div class="flex justify-between text-[11px] text-gray-400 mt-1.5">
            <span>0 严谨确定</span>
            <span>1 发散创造</span>
          </div>
        </div>

        <!-- 操作 -->
        <div class="flex justify-end gap-2 pt-1">
          <button type="button" @click="open = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
          <button type="submit" :disabled="saving || !form.prompt"
                  class="h-9 px-5 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-1.5"
                  :class="saving || !form.prompt ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
            <svg v-if="saving" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from '@/utils/toast.js'
import { listAgentConfigs, updateAgentConfig } from '@/api/agent/agent.js'

// ==================== 图标与配色(agentKey -> 图标/语义色, 暖橙主题无紫无渐变) ====================

const ICONS = {
  crown: '<path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.52l4.276 3.664a1 1 0 0 0 1.516-.294z"/><path d="M5 21h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
  bag: '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  chart: '<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>',
  db: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14a8 3 0 0 0 16 0V5"/><path d="M4 12a8 3 0 0 0 16 0"/>',
  bot: '<rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/><line x1="12" y1="8" x2="12" y2="5"/><circle cx="12" cy="3.5" r="1.2"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  trend: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
}

// 主管橙实底白字突出, 专职 Agent 各配语义浅底色(与管理端首页指标卡同源)
const ICON_STYLES = {
  crown: { bg: '#f07c2a', color: '#ffffff' },
  search: { bg: '#e4f4f2', color: '#26a69a' },
  bag: { bg: '#fdf6e3', color: '#d97706' },
  help: { bg: '#fdf0ef', color: '#e8746b' },
  chart: { bg: '#f3f9ec', color: '#7cae4f' },
  db: { bg: '#eef2f6', color: '#64748b' },
  bot: { bg: '#fff3e8', color: '#f07c2a' },
}

const iconOf = (key) => {
  if (!key) return 'bot'
  if (key.startsWith('supervisor')) return 'crown'
  if (key.includes('recommendation')) return 'search'
  if (key.includes('order')) return 'bag'
  if (key.includes('faq')) return 'help'
  if (key.includes('metrics')) return 'chart'
  if (key.includes('sql')) return 'db'
  return 'bot'
}
const iconStyle = (key) => ICON_STYLES[iconOf(key)]
const isSupervisor = (row) => (row?.agentKey || '').startsWith('supervisor')

// ==================== 状态 ====================

const loading = ref(true)      // 列表加载中
const saving = ref(false)      // 表单保存中
const configs = ref([])        // Agent 配置列表
const open = ref(false)        // 编辑框开关
const title = ref('')          // 编辑框标题
const form = ref({})           // 编辑表单
const chartRef = ref(null)     // 调用排行图容器
const expandedKeys = ref([])   // 工具清单展开的 agentId 列表
let chart = null               // ECharts 实例

// ==================== 计算属性 ====================

// 启用数 / 近 30 天总调用
const enabledCount = computed(() => configs.value.filter((r) => r.enabled === 0).length)
const totalCalls = computed(() => configs.value.reduce((s, r) => s + (r.callCount || 0), 0))

// 按场景分组(用户端团队 / 经营分析团队)
const sceneGroups = computed(() => ([
  { key: 'user', label: '用户端助手团队', desc: '面向 C 端用户 · 咨询问答 / 陪玩推荐 / 订单资产查询', icon: ICONS.users, bg: '#e4f4f2', color: '#26a69a', agents: configs.value.filter((r) => r.scene === 'user') },
  { key: 'analyst', label: '经营分析团队', desc: '面向管理员 · 看板指标查询 / NL2SQL 自由分析', icon: ICONS.trend, bg: '#fff3e8', color: '#f07c2a', agents: configs.value.filter((r) => r.scene === 'analyst') },
].filter((g) => g.agents.length)))

// 调用排行数据(升序, 图表自下而上渲染)与容器高度
const chartRows = computed(() => configs.value.filter((r) => (r.callCount || 0) > 0).sort((a, b) => a.callCount - b.callCount))
const chartHeight = computed(() => `${Math.max(180, chartRows.value.length * 34 + 16)}px`)

// ==================== 工具方法 ====================

const fmtNum = (n) => (n || 0).toLocaleString()
const shortTime = (dt) => (dt || '').slice(5, 16) || '-'

// 工具清单字符串转数组(只读展示)
const toolList = (tools) => (tools || '').split(',').filter(Boolean)
const isExpanded = (agentId) => expandedKeys.value.includes(agentId)
const visibleTools = (row) => (isExpanded(row.agentId) ? toolList(row.tools) : toolList(row.tools).slice(0, 3))
const hiddenToolCount = (row) => Math.max(0, toolList(row.tools).length - 3)
const toggleTools = (agentId) => {
  expandedKeys.value = isExpanded(agentId) ? expandedKeys.value.filter((id) => id !== agentId) : [...expandedKeys.value, agentId]
}

onMounted(() => {
  getList()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  if (chart) chart.dispose()
})

// 加载列表 + 渲染调用排行图
const getList = () => {
  loading.value = true
  listAgentConfigs().then((res) => {
    configs.value = res.data || []
    loading.value = false // 先关骨架屏: chartRef 在 v-else 内, 须与 configs 同轮 flush 挂载, 否则 renderChart 时容器不存在
    renderChart()
  }).finally(() => {
    loading.value = false // 失败兜底(成功路径重复赋同值不触发更新)
  })
}

// 调用排行横向柱状图(纯色暖橙, 容器高度随条数变化故每次重建实例)
const renderChart = () => {
  nextTick(() => {
    if (!chartRef.value) return
    if (chart) chart.dispose()
    chart = echarts.init(chartRef.value)
    const rows = chartRows.value
    chart.setOption({
      grid: { left: 8, right: 40, top: 6, bottom: 6, containLabel: true },
      xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f3f4f6' } }, axisLabel: { color: '#9ca3af', fontSize: 10 } },
      yAxis: { type: 'category', data: rows.map((r) => r.agentName), axisLabel: { color: '#6b7280', fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, textStyle: { fontSize: 12 } },
      series: [{
        type: 'bar', barWidth: 12, data: rows.map((r) => r.callCount),
        itemStyle: { color: '#f07c2a', borderRadius: [0, 6, 6, 0] },
        label: { show: true, position: 'right', color: '#6b7280', fontSize: 11 },
      }],
    })
  })
}

const resizeChart = () => { if (chart) chart.resize() }

// 启停切换(停用需确认)
const toggleEnabled = (row) => {
  if (row.enabled === 0) {
    ElMessageBox.confirm(`停用后「${row.agentName}」不再参与对话路由, 相关请求由主管兜底。确定停用吗？`, '停用确认', {
      confirmButtonText: '停用', cancelButtonText: '取消', type: 'warning',
    }).then(() => doToggle(row)).catch(() => {})
  } else {
    doToggle(row)
  }
}

const doToggle = (row) => {
  const enabled = row.enabled === 0 ? 1 : 0
  updateAgentConfig(row.agentId, { enabled }).then(() => {
    row.enabled = enabled
    ElMessage.success(enabled === 0 ? '已启用' : '已停用')
  })
}

// 打开编辑框
const handleUpdate = (row) => {
  form.value = { ...row }
  title.value = `编辑 Agent - ${row.agentName}`
  open.value = true
}

// 保存编辑(描述/提示词/温度)
const submitForm = () => {
  if (!form.value.prompt || !form.value.prompt.trim()) {
    ElMessage.error('系统提示词不能为空')
    return
  }
  saving.value = true
  updateAgentConfig(form.value.agentId, {
    description: form.value.description,
    prompt: form.value.prompt,
    temperature: form.value.temperature,
  }).then(() => {
    ElMessage.success('保存成功, 下次对话生效')
    open.value = false
    getList()
  }).finally(() => {
    saving.value = false
  })
}
</script>

<style scoped>
/* Agent 卡片入场(逐卡错峰上浮) */
.agent-card {
  animation: card-in 0.35s ease-out backwards;
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 温度滑块(纯色 track + 橙描边圆钮, 无渐变) */
.temp-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 999px;
  background: #f3f4f6;
  outline: none;
}
.temp-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid var(--color-primary);
  box-shadow: 0 1px 4px rgba(31, 45, 61, 0.15);
  cursor: pointer;
  transition: transform 0.15s ease-out;
}
.temp-slider::-webkit-slider-thumb:hover {
  transform: scale(1.12);
}
.temp-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid var(--color-primary);
  box-shadow: 0 1px 4px rgba(31, 45, 61, 0.15);
  cursor: pointer;
  transition: transform 0.15s ease-out;
}
.temp-slider::-moz-range-thumb:hover {
  transform: scale(1.12);
}
</style>