<template>
  <div class="auth-page">

    <!-- 左侧品牌区 -->
    <aside class="auth-brand">
      <div class="brand-overlay"></div>

      <!-- 浮动装饰形状 -->
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>

      <div class="brand-content">
        <!-- 品牌行 -->
        <div class="brand-row">
          <img :src="logo" alt="后台管理端" class="brand-logo">
          <span class="brand-name">后台管理端</span>
        </div>

        <!-- 品牌标语 -->
        <div class="brand-slogan">
          <span class="slogan-quote">"</span>
          <h1 class="slogan-title">高效运营，<br>从这里轻松开始</h1>
          <p class="slogan-sub">简洁易用的后台管理平台，让每一次操作都得心应手</p>
        </div>

      </div>
    </aside>

    <!-- 右侧表单区 -->
    <main class="auth-form">
      <div class="form-box">
        <div class="form-header">
          <h2 class="form-title">欢迎回来</h2>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- 用户名 -->
          <div class="field">
            <label class="field-label">用户名</label>
            <div class="field-wrap" :class="{ 'field-error': errors.userName }">
              <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input
                v-model="loginForm.userName"
                type="text"
                placeholder="请输入用户名"
                class="field-input"
              />
            </div>
            <p v-if="errors.userName" class="field-msg">{{ errors.userName }}</p>
          </div>

          <!-- 密码 -->
          <div class="field">
            <label class="field-label">密码</label>
            <div class="field-wrap" :class="{ 'field-error': errors.password }">
              <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input
                v-model="loginForm.password"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请输入密码"
                class="field-input"
              />
              <button type="button" class="field-toggle" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
            <p v-if="errors.password" class="field-msg">{{ errors.password }}</p>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="submit-btn"
            :class="{ 'submit-loading': loading }"
          >
            <svg v-if="loading" class="spinner" viewBox="0 0 24 24" fill="none">
              <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="spinner-head" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? '登录中...' : '登 录' }}
          </button>

          <div class="login-footer">
            还没有账户？
            <router-link to="/register" class="login-link">立即注册 →</router-link>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import useUserStore from "@/stores/modules/userStore.js";
import { useRouter } from "vue-router";
import logo from "@/assets/logo/logo.png";

const loading = ref(false)
const showPwd = ref(false)

const loginForm = reactive({
  userName: '',
  password: ''
})

const errors = reactive({
  userName: '',
  password: ''
})

const validateForm = () => {
  let valid = true
  errors.userName = ''
  errors.password = ''

  if (!loginForm.userName) {
    errors.userName = '请输入用户名'
    valid = false
  }
  if (!loginForm.password) {
    errors.password = '请输入密码'
    valid = false
  }
  return valid
}

const userStore = useUserStore()
const router = useRouter()

const handleLogin = () => {
  if (!validateForm()) return

  loading.value = true
  userStore.login({ ...loginForm }).then(() => {
    const redirectPath = '/'
    router.push(redirectPath)
  }).catch(() => {
    loading.value = false
  })
}
</script>

<style scoped>
/* ========== 页面骨架 ========== */
.auth-page { display: flex; min-height: 100vh; }

/* ========== 左侧品牌区 ========== */
.auth-brand {
  position: relative; flex: 1.15; overflow: hidden;
  display: flex; flex-direction: column;
  padding: 44px 52px 32px;
  color: #fff;
  background: url('../assets/images/background.jpg') center center / cover no-repeat;
  animation: fadeSlideLeft 0.5s ease-out both;
}
.brand-overlay {
  position: absolute; inset: 0; z-index: 1;
  background: rgba(217, 106, 31, 0.88);
}
.brand-content {
  position: relative; z-index: 2; flex: 1;
  display: flex; flex-direction: column; justify-content: center; gap: 40px;
}

/* 品牌行 */
.brand-row { display: flex; align-items: center; gap: 12px; }
.brand-logo {
  width: 44px; height: 44px; border-radius: 12px;
  background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.18);
}
.brand-name { font-size: 17px; font-weight: 700; letter-spacing: 0.02em; }

/* 品牌标语 */
.brand-slogan { display: flex; flex-direction: column; gap: 14px; }
.slogan-quote {
  font-family: Georgia, "Noto Serif SC", "Songti SC", serif;
  font-size: 60px; line-height: 0.6; height: 30px;
  color: rgba(255,255,255,0.4);
}
.slogan-title {
  margin: 0;
  font-family: Georgia, "Noto Serif SC", "Songti SC", serif;
  font-size: 34px; font-weight: 700; line-height: 1.45; letter-spacing: 0.02em;
  text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.slogan-sub { margin: 0; font-size: 14px; line-height: 1.7; color: rgba(255,255,255,0.82); }

/* 浮动装饰形状 */
.blob {
  position: absolute; z-index: 1;
  border-radius: 44% 56% 62% 38% / 52% 44% 56% 48%;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  animation: float 8s ease-in-out infinite alternate;
  pointer-events: none;
}
.blob-1 { width: 220px; height: 220px; top: -60px; right: -50px; }
.blob-2 { width: 150px; height: 150px; bottom: 130px; right: 56px; animation-delay: -3s; }
.blob-3 { width: 90px; height: 90px; top: 38%; left: -30px; animation-delay: -5s; }

/* ========== 右侧表单区 ========== */
.auth-form {
  position: relative; flex: 1; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  padding: 48px 40px;
  background: var(--color-bg-page, #F0F2F5);
}
.auth-form::before {
  content: ''; position: absolute; top: -90px; right: -90px;
  width: 320px; height: 320px; border-radius: 50%;
  background: rgba(240, 124, 42, 0.07);
  pointer-events: none;
}
.auth-form::after {
  content: ''; position: absolute; bottom: -110px; left: -70px;
  width: 300px; height: 300px; border-radius: 50%;
  background: rgba(255, 154, 77, 0.09);
  pointer-events: none;
}
.form-box { position: relative; z-index: 1; width: 100%; max-width: 400px; }

.form-header { margin-bottom: 32px; animation: fadeUp 0.4s ease-out 0.05s both; }
.form-title { font-size: 28px; font-weight: 800; letter-spacing: -0.02em; color: var(--color-text-dark, #2D3748); margin: 0 0 8px; }
.form-subtitle { font-size: 14px; color: var(--color-text-light, #A0AEC0); margin: 0; }

.login-form { display: flex; flex-direction: column; gap: 20px; }
.login-form > * { animation: fadeUp 0.4s ease-out both; }
.login-form > *:nth-child(1) { animation-delay: 0.13s; }
.login-form > *:nth-child(2) { animation-delay: 0.21s; }
.login-form > *:nth-child(3) { animation-delay: 0.29s; }
.login-form > *:nth-child(4) { animation-delay: 0.37s; }

/* ========== 字段 ========== */
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; font-weight: 600; color: var(--color-text-medium, #718096); }
.field-wrap {
  display: flex; align-items: center; gap: 10px; padding: 0 14px;
  height: 48px; background: #fff; border-radius: 12px;
  border: 1.5px solid var(--color-border, #E5E7EB); transition: all 0.2s ease;
}
.field-wrap:focus-within {
  border-color: var(--color-primary, #f07c2a);
  box-shadow: 0 0 0 3px rgba(240,124,42,0.12);
}
.field-error {
  border-color: #FCA5A5 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,0.08) !important;
}
.field-icon { width: 18px; height: 18px; color: #94A3B8; flex-shrink: 0; transition: color 0.2s; }
.field-wrap:focus-within .field-icon { color: var(--color-primary, #f07c2a); }
.field-error .field-icon { color: #FCA5A5; }
.field-input {
  flex: 1; border: none; background: transparent; outline: none;
  font-size: 14px; color: #0F172A; min-width: 0;
}
.field-input::placeholder { color: #94A3B8; }
.field-toggle {
  background: none; border: none; cursor: pointer; padding: 4px;
  color: #94A3B8; transition: color 0.2s; display: flex;
}
.field-toggle:hover { color: var(--color-text-medium, #718096); }
.field-toggle svg { width: 17px; height: 17px; }
.field-msg { font-size: 12px; color: #EF4444; padding-left: 4px; margin: 0; }

/* ========== 提交按钮 ========== */
.submit-btn {
  margin-top: 4px; height: 48px; border: none; border-radius: 12px;
  font-size: 15px; font-weight: 700; color: #fff; cursor: pointer;
  background: var(--color-primary, #f07c2a);
  box-shadow: 0 4px 20px rgba(240,124,42,0.3);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.2s ease;
}
.submit-btn:hover { background: var(--color-primary-dark, #d96a1f); transform: translateY(-1px); box-shadow: 0 6px 28px rgba(240,124,42,0.4); }
.submit-btn:active { transform: scale(0.97); }
.submit-loading { opacity: 0.65; cursor: not-allowed; pointer-events: none; }

/* Spinner */
.spinner { width: 18px; height: 18px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-track { opacity: 0.2; }
.spinner-head { opacity: 0.8; }

/* ========== 底部链接 ========== */
.login-footer { text-align: center; font-size: 14px; color: var(--color-text-light, #A0AEC0); }
.login-link {
  font-weight: 600; color: var(--color-primary, #f07c2a); text-decoration: none;
  transition: color 0.2s; margin-left: 4px;
}
.login-link:hover { color: var(--color-primary-dark, #d96a1f); }

/* ========== 动画 ========== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideLeft {
  from { opacity: 0; transform: translateX(-28px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes float {
  from { transform: translate(0, 0) rotate(0deg); }
  to { transform: translate(14px, -18px) rotate(8deg); }
}

/* ========== 响应式 ========== */
@media (max-width: 992px) {
  .auth-page { flex-direction: column; }

  /* 品牌区压缩为顶部横幅 */
  .auth-brand { flex: none; padding: 18px 24px; }
  .brand-content { justify-content: center; gap: 10px; }
  .brand-row { gap: 10px; }
  .brand-logo { width: 36px; height: 36px; border-radius: 10px; }
  .brand-name { font-size: 15px; }
  .brand-slogan { padding: 0; gap: 0; }
  .slogan-quote, .slogan-sub, .blob { display: none; }
  .slogan-title { font-size: 16px; line-height: 1.4; font-weight: 600; opacity: 0.92; }
  .slogan-title br { display: none; }

  .auth-form { padding: 36px 24px; }
}
@media (max-width: 480px) {
  .auth-form { padding: 28px 18px; }
  .form-header { margin-bottom: 26px; }
  .form-title { font-size: 24px; }
}
</style>