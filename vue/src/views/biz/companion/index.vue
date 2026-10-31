<template>
  <div class="app-container">
    <!-- 顶部查询 -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">陪玩师昵称</label>
        <input v-model="query.nickName" placeholder="请输入陪玩师昵称" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-44" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[34px]">性别</label>
        <select v-model="query.gender" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-28">
          <option :value="null">全部</option>
          <option :value="0">男</option>
          <option :value="1">女</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">主游戏</label>
        <select v-model="query.mainGameId" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-36">
          <option :value="null">全部</option>
          <option v-for="g in gameList" :key="g.gameId" :value="g.gameId">{{ g.gameName }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[58px]">认证状态</label>
        <select v-model="query.certified" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-28">
          <option :value="null">全部</option>
          <option :value="1">已认证</option>
          <option :value="0">未认证</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[34px]">状态</label>
        <select v-model="query.status" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white w-28">
          <option :value="null">全部</option>
          <option :value="0">启用</option>
          <option :value="1">停用</option>
        </select>
      </div>
      <div class="flex gap-2">
        <button @click="handleQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-1" :class="loading ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
          <svg v-if="!loading" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <svg v-else class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          {{ loading ? '查询中...' : '搜索' }}
        </button>
        <button @click="resetQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors flex items-center gap-1" :class="{ 'opacity-50 cursor-not-allowed': loading }">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>重置
        </button>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-2 mb-2">
      <button @click="handleInsert" class="h-9 px-4 rounded-lg text-sm font-medium text-[var(--color-primary)] border border-[var(--color-primary)] bg-white hover:bg-[var(--color-primary-bg)] transition-colors flex items-center gap-1">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>新增
      </button>
      <button :disabled="single" @click="handleUpdate()" class="h-9 px-4 rounded-lg text-sm font-medium transition-colors flex items-center gap-1" :class="single ? 'text-gray-400 border border-gray-200 bg-gray-50 cursor-not-allowed' : 'text-green-600 border border-green-500 bg-white hover:bg-green-50'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>修改
      </button>
      <button :disabled="multiple" @click="handleDelete()" class="h-9 px-4 rounded-lg text-sm font-medium transition-colors flex items-center gap-1" :class="multiple ? 'text-gray-400 border border-gray-200 bg-gray-50 cursor-not-allowed' : 'text-red-500 border border-red-400 bg-white hover:bg-red-50'">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>删除
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg relative">
      <div v-if="loading" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center rounded-lg">
        <div class="flex flex-col items-center gap-2">
          <svg class="w-8 h-8 animate-spin text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          <span class="text-sm text-gray-500">加载中...</span>
        </div>
      </div>
      <table class="w-full text-sm min-w-[1280px]">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-[55px] px-3 py-3 text-center"><input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="w-4 h-4 rounded"/></th>
            <th class="w-[60px] px-3 py-3 text-center font-medium text-gray-600">序号</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">头像</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">昵称</th>
            <th class="w-[70px] px-3 py-3 text-center font-medium text-gray-600">城市</th>
            <th class="w-[130px] px-3 py-3 text-center font-medium text-gray-600">主游戏</th>
            <th class="w-[90px] px-3 py-3 text-center font-medium text-gray-600">声线</th>
            <th class="w-[80px] px-3 py-3 text-center font-medium text-gray-600">起步价</th>
            <th class="w-[80px] px-3 py-3 text-center font-medium text-gray-600">认证</th>
            <th class="w-[72px] px-3 py-3 text-center font-medium text-gray-600">状态</th>
            <th class="w-[160px] px-3 py-3 text-center font-medium text-gray-600">创建时间</th>
            <th class="w-[110px] px-3 py-3 text-center font-medium text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in companionList" :key="row.companionId" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors" :class="{ 'bg-[var(--color-primary-bg)]/30': selectedIds.has(row.companionId) }">
            <td class="px-3 py-3 text-center"><input type="checkbox" :checked="selectedIds.has(row.companionId)" @change="toggleRow(row.companionId)" class="w-4 h-4 rounded"/></td>
            <td class="px-3 py-3 text-center text-gray-600">{{ (query.pageNum - 1) * query.pageSize + index + 1 }}</td>
            <td class="px-3 py-3 text-center">
              <image-preview v-if="row.avatar" :src="row.avatar" :width="40" :height="40"/>
              <div v-else class="w-10 h-10 rounded-lg bg-[var(--color-primary-bg)] text-[var(--color-primary)] font-bold flex items-center justify-center mx-auto">{{ (row.nickName || '陪')[0] }}</div>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="font-medium">{{ row.nickName }}</div>
              <div class="text-xs text-gray-400 mt-0.5">{{ row.gender === 1 ? '女' : '男' }}<span v-if="row.age"> · {{ row.age }}岁</span></div>
            </td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.city || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <div class="text-gray-700">{{ row.mainGameName || '-' }}</div>
              <div class="text-xs text-gray-400 mt-0.5 truncate" :title="row.mainRank">{{ row.mainRank || '' }}</div>
            </td>
            <td class="px-3 py-3 text-center text-gray-600">{{ row.voice || '-' }}</td>
            <td class="px-3 py-3 text-center text-orange-500 font-medium">¥{{ row.price ?? '-' }}</td>
            <td class="px-3 py-3 text-center">
              <span v-if="row.certified === 1" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-600 border border-green-200">已认证</span>
              <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-400 border border-gray-200">未认证</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span class="inline-flex items-center gap-1.5 text-sm" :class="row.status === 0 ? 'text-green-600' : 'text-gray-400'">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === 0 ? 'bg-green-500' : 'bg-gray-300'"></span>{{ row.status === 0 ? '启用' : '停用' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center text-gray-500">{{ row.createTime || '-' }}</td>
            <td class="px-3 py-3 text-center">
              <button @click="handleUpdate(row)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] text-sm mr-3 font-medium">修改</button>
              <button @click="handleDelete(row)" class="text-red-500 hover:text-red-600 text-sm font-medium">删除</button>
            </td>
          </tr>
          <tr v-if="companionList.length === 0"><td colspan="12" class="px-3 py-12 text-center text-gray-400">暂无数据</td></tr>
        </tbody>
      </table>
    </div>

    <pagination :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList"/>

    <!-- 对话框 -->
    <Modal :title="title" v-model="open" width="720px">
      <form @submit.prevent="submitForm" class="space-y-4">
        <div class="grid grid-cols-2 gap-x-6 gap-y-4">
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>昵称</label>
            <div class="flex-1">
              <input v-model="form.nickName" placeholder="请输入陪玩师昵称" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">性别</label>
            <div class="flex-1 flex items-center gap-4 pt-1.5">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="0" v-model="form.gender" class="accent-[var(--color-primary)]"/>男
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="1" v-model="form.gender" class="accent-[var(--color-primary)]"/>女
              </label>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">年龄</label>
            <div class="flex-1">
              <input v-model="form.age" type="number" placeholder="请输入年龄" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">城市</label>
            <div class="flex-1">
              <input v-model="form.city" placeholder="请输入城市" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">声线</label>
            <div class="flex-1">
              <input v-model="form.voice" placeholder="如: 温软甜音 / 低音炮" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">起步价</label>
            <div class="flex-1 relative">
              <input v-model="form.price" type="number" placeholder="元/小时" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
              <span class="absolute right-3 top-2 text-xs text-gray-400">元/时</span>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">认证状态</label>
            <div class="flex-1 flex items-center gap-4 pt-1.5">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="1" v-model="form.certified" class="accent-[var(--color-primary)]"/>已认证
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="0" v-model="form.certified" class="accent-[var(--color-primary)]"/>未认证
              </label>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">状态</label>
            <div class="flex-1 flex items-center gap-4 pt-1.5">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="0" v-model="form.status" class="accent-[var(--color-primary)]"/>启用
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" :value="1" v-model="form.status" class="accent-[var(--color-primary)]"/>停用
              </label>
            </div>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">标签</label>
          <div class="flex-1">
            <input v-model="form.tags" placeholder="多个标签用英文逗号分隔" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">个人简介</label>
          <div class="flex-1">
            <textarea v-model="form.intro" rows="2" placeholder="请输入个人简介" class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none"></textarea>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">头像</label>
          <div class="flex-1">
            <ImageUpload v-model="form.avatar" :limit="1"/>
          </div>
        </div>

        <!-- 擅长游戏(动态行, 第一行为主游戏) -->
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0"><span class="text-red-500 mr-0.5">*</span>擅长游戏</label>
          <div class="flex-1 space-y-2">
            <div v-for="(g, i) in games" :key="i" class="flex items-center gap-2">
              <span v-if="i === 0" class="px-1.5 py-0.5 rounded text-xs font-medium text-[var(--color-primary)] border border-[var(--color-primary)] flex-shrink-0">主游戏</span>
              <span v-else class="px-1.5 py-0.5 rounded text-xs text-gray-400 border border-gray-200 flex-shrink-0 w-[52px] text-center">游戏{{ i + 1 }}</span>
              <select v-model="g.gameId" class="flex-1 h-9 px-2.5 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white min-w-0">
                <option :value="null" disabled>请选择游戏</option>
                <option v-for="opt in gameList" :key="opt.gameId" :value="opt.gameId">{{ opt.gameName }}</option>
              </select>
              <input v-model="g.gameRank" placeholder="段位(如: 最强王者)" class="w-44 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] flex-shrink-0"/>
              <button type="button" @click="removeGame(i)" :disabled="games.length === 1" class="w-9 h-9 rounded-lg border border-red-300 text-red-500 hover:bg-red-50 transition-colors flex items-center justify-center flex-shrink-0" :class="{ 'opacity-40 cursor-not-allowed hover:bg-white': games.length === 1 }">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <button type="button" @click="addGame" :disabled="games.length >= gameList.length" class="h-8 px-3 rounded-lg text-sm font-medium text-[var(--color-primary)] border border-dashed border-[var(--color-primary)] bg-white hover:bg-[var(--color-primary-bg)] transition-colors flex items-center gap-1" :class="{ 'opacity-40 cursor-not-allowed': games.length >= gameList.length }">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>添加游戏
            </button>
          </div>
        </div>

        <!-- 服务项目(动态行) -->
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">服务项目</label>
          <div class="flex-1 space-y-2">
            <div v-for="(s, i) in services" :key="i" class="flex items-center gap-2">
              <select v-model="s.serviceId" class="w-36 h-9 px-2.5 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] bg-white flex-shrink-0">
                <option :value="null" disabled>请选择服务</option>
                <option v-for="opt in serviceList" :key="opt.serviceId" :value="opt.serviceId">{{ opt.serviceName }}</option>
              </select>
              <div class="relative w-28 flex-shrink-0">
                <input v-model="s.price" type="number" min="0" placeholder="价格" class="w-full h-9 pl-3 pr-8 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)]"/>
                <span class="absolute right-2.5 top-2 text-xs text-gray-400">元/时</span>
              </div>
              <input v-model="s.description" placeholder="服务说明(可选)" class="flex-1 h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] min-w-0"/>
              <button type="button" @click="removeService(i)" :disabled="services.length === 1" class="w-9 h-9 rounded-lg border border-red-300 text-red-500 hover:bg-red-50 transition-colors flex items-center justify-center flex-shrink-0" :class="{ 'opacity-40 cursor-not-allowed hover:bg-white': services.length === 1 }">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <button type="button" @click="addService" :disabled="services.length >= serviceList.length" class="h-8 px-3 rounded-lg text-sm font-medium text-[var(--color-primary)] border border-dashed border-[var(--color-primary)] bg-white hover:bg-[var(--color-primary-bg)] transition-colors flex items-center gap-1" :class="{ 'opacity-40 cursor-not-allowed': services.length >= serviceList.length }">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>添加服务
            </button>
            <div v-if="services.length === 0" class="text-xs text-gray-400">未添加服务项目(可留空)</div>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitForm" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">保存</button>
        <button @click="open = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">取消</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed} from "vue";
import {deleteCompanionByCompanionIds, insertCompanion, selectCompanionByCompanionId, selectCompanionList, updateCompanion} from "@/api/biz/companion.js";
import {selectAllGame} from "@/api/biz/game.js";
import {selectAllServiceItem} from "@/api/biz/serviceItem.js";
import Pagination from "@/components/Pagination/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";

const title = ref('')
const open = ref(false)

/* 表单默认值(新增/回显前重置用; 评分/接单量/粉丝数均为动态聚合数据, 不在表单维护) */
const DEFAULT_FORM = {
  companionId: null, nickName: '', gender: 0, age: null, city: '', avatar: '', voice: '',
  price: null, intro: '', tags: '',
  certified: 1, status: 0
}
const form = reactive({...DEFAULT_FORM})
const games = ref([{gameId: null, gameRank: ''}])  // 擅长游戏动态行(第一行为主游戏)
const services = ref([{serviceId: null, price: '', description: ''}])  // 服务项目动态行

/* 游戏分类/服务项目下拉选项 */
const gameList = ref([])
const serviceList = ref([])

const addGame = () => games.value.push({gameId: null, gameRank: ''})
const removeGame = (i) => games.value.splice(i, 1)
const addService = () => services.value.push({serviceId: null, price: '', description: ''})
const removeService = (i) => services.value.splice(i, 1)

const handleInsert = () => {
  Object.assign(form, DEFAULT_FORM)
  games.value = [{gameId: null, gameRank: ''}]
  services.value = [{serviceId: null, price: '', description: ''}]
  open.value = true
  title.value = '新增陪玩师'
}

const handleUpdate = (row) => {
  const companionId = row ? row.companionId : ids.value[0]
  if (!companionId) return
  selectCompanionByCompanionId(companionId).then(res => {
    Object.assign(form, DEFAULT_FORM, res.data)
    // 回显关联数据: 后端返回 [{gameId, gameName, gameRank}] / [{serviceId, serviceName, price, description}]
    games.value = (res.data.games && res.data.games.length)
      ? res.data.games.map(g => ({gameId: g.gameId, gameRank: g.gameRank || ''}))
      : [{gameId: null, gameRank: ''}]
    services.value = (res.data.services && res.data.services.length)
      ? res.data.services.map(s => ({serviceId: s.serviceId, price: s.price ?? '', description: s.description || ''}))
      : []
    open.value = true
    title.value = '修改陪玩师'
  })
}

const handleDelete = (row) => {
  const companionIds = row ? [row.companionId] : ids.value
  if (!companionIds || companionIds.length === 0) return
  ElMessageBox.confirm('是否确认删除选中的陪玩师?', '系统提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    deleteCompanionByCompanionIds(companionIds.join(',')).then(() => {
      ElMessage.success('删除成功')
      getList()
    })
  }).catch(() => {})
}

const submitForm = () => {
  if (!form.nickName || !form.nickName.trim()) {
    ElMessage.warning('请输入陪玩师昵称')
    return
  }
  const validGames = games.value.filter(g => g.gameId != null)
  if (validGames.length === 0) {
    ElMessage.warning('请至少添加一个擅长游戏')
    return
  }
  const gameIds = validGames.map(g => Number(g.gameId))
  if (new Set(gameIds).size !== gameIds.length) {
    ElMessage.warning('擅长游戏存在重复, 请调整')
    return
  }
  const validServices = services.value.filter(s => s.serviceId != null)
  const serviceIds = validServices.map(s => Number(s.serviceId))
  if (new Set(serviceIds).size !== serviceIds.length) {
    ElMessage.warning('服务项目存在重复, 请调整')
    return
  }
  const toNum = (v) => (v === '' || v === null || v === undefined) ? null : Number(v)
  const data = {
    companionId: form.companionId,
    nickName: form.nickName.trim(),
    gender: Number(form.gender), age: toNum(form.age), city: form.city || null,
    avatar: form.avatar || null, voice: form.voice || null, price: toNum(form.price),
    intro: form.intro || null, tags: form.tags || null,
    certified: Number(form.certified), status: Number(form.status),
    // 关联数据: 主游戏冗余字段由后端按 games[0] 自动同步
    games: validGames.map(g => ({gameId: Number(g.gameId), gameRank: g.gameRank || null})),
    services: validServices.map(s => ({
      serviceId: Number(s.serviceId),
      price: toNum(s.price) ?? 0,
      description: s.description || null
    }))
  }
  if (data.companionId != null) {
    updateCompanion(data).then(() => {
      ElMessage.success('修改成功')
      open.value = false; getList()
    })
  } else {
    insertCompanion(data).then(() => {
      ElMessage.success('新增成功, 已同步创建登录账号(用户名同昵称, 初始密码 123456)')
      open.value = false; getList()
    })
  }
}

const query = ref({ pageNum: 1, pageSize: 10, nickName: '', gender: null, mainGameId: null, certified: null, status: null })
const companionList = ref([])
const total = ref(0)
const ids = ref([])
const selectedIds = reactive(new Set())
const loading = ref(false)

const single = computed(() => ids.value.length !== 1)
const multiple = computed(() => ids.value.length === 0)
const isAllSelected = computed(() => companionList.value.length > 0 && selectedIds.size === companionList.value.length)

const syncSelected = () => { ids.value = [...selectedIds] }
const toggleRow = (id) => {
  if (selectedIds.has(id)) selectedIds.delete(id)
  else selectedIds.add(id)
  syncSelected()
}
const toggleSelectAll = () => {
  if (isAllSelected.value) companionList.value.forEach(r => selectedIds.delete(r.companionId))
  else companionList.value.forEach(r => selectedIds.add(r.companionId))
  syncSelected()
}

const handleQuery = () => { query.value.pageNum = 1; getList() }
const resetQuery = () => {
  query.value.nickName = ''; query.value.gender = null
  query.value.mainGameId = null; query.value.certified = null; query.value.status = null
  handleQuery()
}

const getList = () => {
  loading.value = true
  selectCompanionList(query.value).then(res => {
    companionList.value = res.rows
    total.value = res.total
  }).finally(() => { loading.value = false })
}

onMounted(() => {
  getList()
  selectAllGame().then(res => { gameList.value = res.data || [] })
  selectAllServiceItem().then(res => { serviceList.value = res.data || [] })
})
</script>