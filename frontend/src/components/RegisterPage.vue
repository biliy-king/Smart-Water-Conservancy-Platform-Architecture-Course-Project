<template>
  <div class="register-page">
    <div class="register-background"></div>
    <div class="register-card">
      <div class="register-header">
        <h2 class="register-title">注册 Setup</h2>
      </div>
      <div class="register-form">
        <div class="form-item">
          <label class="form-label">设置用户名</label>
          <input v-model="username" type="text" class="form-input" placeholder="请输入用户名" />
          <div class="form-line"></div>
        </div>
        <div class="form-item">
          <label class="form-label">设置密码</label>
          <input v-model="password" type="password" class="form-input" placeholder="请输入密码" />
          <div class="form-line"></div>
        </div>
        <div class="form-item">
          <label class="form-label">再次输入密码</label>
          <input v-model="confirmPassword" type="password" class="form-input" placeholder="请再次输入密码" />
          <div class="form-line"></div>
        </div>
        <button class="register-button" @click="handleRegister">
          <span class="button-text">注册</span>
        </button>
        <div class="login-link">
          <span class="link-text">已有账号？</span>
          <span class="link-action" @click="$emit('switch-to-login')">去登录</span>
        </div>
      </div>
      <div class="register-decorations">
        <div class="decoration decoration-1"></div>
        <div class="decoration decoration-2"></div>
        <div class="decoration decoration-3"></div>
        <div class="decoration decoration-4"></div>
        <div class="decoration decoration-5"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')

function handleRegister() {
  if (!username.value || !password.value || !confirmPassword.value) {
    alert('请填写所有字段')
    return
  }
  if (password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }
  // 注册逻辑
  console.log('注册:', username.value, password.value)
  emit('close')
}

const emit = defineEmits(['close', 'switch-to-login'])
</script>

<style scoped>
.register-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.register-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: cover;
  z-index: 0;
}

.register-card {
  position: relative;
  width: 771px;
  height: 1039px;
  background: #FFFFFF;
  border-radius: 50px;
  box-shadow: 4px 4px 4px 4px rgba(0, 0, 0, 0.25);
  padding: 181px 100px;
  box-sizing: border-box;
  z-index: 1;
}

.register-header {
  margin-bottom: 60px;
}

.register-title {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 64px;
  color: #000000;
  text-align: center;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.form-item {
  position: relative;
}

.form-label {
  display: block;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #797979;
  margin-bottom: 12px;
}

.form-input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 32px;
  padding: 8px 0;
  background: transparent;
  color: #000000;
}

.form-line {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 558px;
  height: 1px;
  background: #000000;
}

.register-button {
  width: 538px;
  height: 81px;
  background: linear-gradient(163deg, rgba(253, 240, 184, 1) 0%, rgba(209, 240, 254, 1) 100%);
  border: none;
  border-radius: 15px;
  cursor: pointer;
  margin-top: 40px;
  transition: transform 0.2s;
}

.register-button:hover {
  transform: scale(1.02);
}

.register-button:active {
  transform: scale(0.98);
}

.button-text {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 40px;
  color: #0F1419;
}

.login-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
}

.link-text {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #6D6C6C;
}

.link-action {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #6DC2FF;
  cursor: pointer;
  text-decoration: underline;
}

.link-action:hover {
  color: #4AA3E8;
}

.register-decorations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration {
  position: absolute;
  background-size: cover;
  background-position: center;
  opacity: 0.6;
}

.decoration-1 {
  width: 367px;
  height: 377px;
  bottom: 0;
  left: 0;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzY3IiBoZWlnaHQ9IjM3NyIgdmlld0JveD0iMCAwIDM2NyAzNzciIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzNjciIGhlaWdodD0iMzc3IiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPg==') no-repeat;
}

.decoration-2 {
  width: 208px;
  height: 186px;
  top: 18px;
  right: 1398px;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjA4IiBoZWlnaHQ9IjE4NiIgdmlld0JveD0iMCAwIDIwOCAxODYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDgiIGhlaWdodD0iMTg2IiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPg==') no-repeat;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
}

.decoration-3 {
  width: 213px;
  height: 334px;
  top: 273px;
  left: 388px;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEzIiBoZWlnaHQ9IjMzNCIgdmlld0JveD0iMCAwIDIxMyAzMzQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMTMiIGhlaWdodD0iMzM0IiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPg==') no-repeat;
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
}

.decoration-4 {
  width: 450.5px;
  height: 362.49px;
  top: 508px;
  right: 1804px;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDUwLjUiIGhlaWdodD0iMzYyLjQ5IiB2aWV3Qm94PSIwIDAgNDUwLjUgMzYyLjQ5IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0iNDUwLjUiIGhlaWdodD0iMzYyLjQ5IiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPg==') no-repeat;
}

.decoration-5 {
  width: 234px;
  height: 325px;
  bottom: 1075px;
  right: 2255px;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjM0IiBoZWlnaHQ9IjMyNSIgdmlld0JveD0iMCAwIDIzNCAzMjUiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMzQiIGhlaWdodD0iMzI1IiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPg==') no-repeat;
}
</style>
