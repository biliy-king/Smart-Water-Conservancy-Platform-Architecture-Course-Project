<template>
  <div class="page">
    <div class="section_1">
      <div class="box_1 flex-row">
        <!-- 装饰图片1 - 左下角 -->
        <img
          class="image_1"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG7c8238176f094a3f68b0358b561c52f6.png"
          alt="Decoration 1"
        />
        <!-- 装饰图片2 - 左侧中间 -->
        <img
          class="image_2"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNGe2995af67c8dc1cdaaad4b07b1f09a97.png"
          alt="Decoration 2"
        />
        <!-- 注册卡片 -->
        <div class="group_2 flex-col">
          <span class="text_1">注册&nbsp;Setup</span>
          <div class="form-item">
            <span class="text_2">设置用户名</span>
            <input v-model="username" type="text" class="form-input" />
            <div class="form-line"></div>
          </div>
          <div class="form-item">
            <span class="text_3">设置密码</span>
            <input v-model="password" type="password" class="form-input" />
            <div class="form-line"></div>
          </div>
          <div class="form-item">
            <span class="text_4">再次输入密码</span>
            <input v-model="confirmPassword" type="password" class="form-input" />
            <div class="form-line"></div>
          </div>
          <div class="text-wrapper_1 flex-col" @click="handleRegister" :class="{ disabled: loading }">
            <span class="text_5">{{ loading ? '注册中...' : '注册' }}</span>
          </div>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <div class="text-wrapper_3 flex-row justify-between">
            <span class="text_6">已有账号？</span>
            <span class="text_7" @click="$emit('switch-to-login')">去登录</span>
          </div>
        </div>
        <!-- 装饰图片3 - 右侧中间 -->
        <img
          class="image_3"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNGf8871e5d7d5c13b58215073c91ae75e2.png"
          alt="Decoration 3"
        />
        <!-- 装饰图片4 - 右下角 -->
        <img
          class="image_4"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG6f9d4f80b5079d47ed499decb938bc02.png"
          alt="Decoration 4"
        />
      </div>
      <!-- 装饰图片5 - 右上角 -->
      <div class="image-wrapper_2 flex-row">
        <img
          class="image_5"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNGaa72bdee37d82e2868ecf7b3d9cc6b4e.png"
          alt="Decoration 5"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { register } from '@/api/auth'
import { setLoggedIn } from '@/store/auth'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')

const emit = defineEmits(['close', 'switch-to-login'])

async function handleRegister() {
  // 验证输入
  if (!username.value || !password.value || !confirmPassword.value) {
    errorMessage.value = '请填写所有字段'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少6位'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    // 调用注册接口
    const response = await register(username.value, password.value)
    
    if (response.data.success) {
      // 保存token和用户信息
      localStorage.setItem('access_token', response.data.tokens.access)
      localStorage.setItem('refresh_token', response.data.tokens.refresh)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      // 更新认证状态
      setLoggedIn()
      
      
      // 关闭注册页面
      emit('close')
    } else {
      errorMessage.value = response.data.message || '注册失败'
    }
  } catch (error) {
    // 处理错误
    console.error('注册错误:', error)
    
    if (error.response?.data?.message) {
      errorMessage.value = error.response.data.message
    } else if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = '注册失败，请检查网络连接或联系管理员'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Flexbox 工具类 */
.flex-row {
  display: flex;
  flex-direction: row;
}

.flex-col {
  display: flex;
  flex-direction: column;
}

.justify-between {
  justify-content: space-between;
}

/* 主容器 */
.page {
  background-color: rgba(255, 255, 255, 1);
  position: relative;
  width: 2560px;
  height: 1400px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 背景区域 */
.section_1 {
  height: 1400px;
  background: url(https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG1128297724d259c8891a24e415425f3c.png) 100% no-repeat;
  background-size: 100% 100%;
  margin-left: -47px;
  width: 2607px;
  position: relative;
}

/* 主要内容组 */
.box_1 {
  width: 2489px;
  height: 1219px;
  margin: 181px 0 0 47px;
  position: relative;
}

/* 所有装饰图片通用样式 - 无边框 */
.section_1 img {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  -moz-box-shadow: none !important;
}

/* 装饰图片1 - 左下角 */
.image_1 {
  width: 367px;
  height: 377px;
  margin-top: 842px;
  object-fit: cover;
}

/* 装饰图片2 - 左侧中间 */
.image_2 {
  width: 213px;
  height: 334px;
  margin: 92px 0 0 21px;
  object-fit: cover;
}

/* 注册卡片 */
.group_2 {
  box-shadow: 4px 4px 4px 4px rgba(0, 0, 0, 0.25);
  background-color: rgba(255, 255, 255, 1);
  border-radius: 50px;
  width: 771px;
  height: 1039px;
  margin-left: 294px;
  position: relative;
}

/* 标题 */
.text_1 {
  width: 302px;
  height: 104px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 64px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 64px;
  margin: 122px 0 0 239px;
}

/* 表单项 */
.form-item {
  position: relative;
  width: 100%;
  margin-top: 101px;
}

.form-item:first-of-type {
  margin-top: 101px;
}

.form-item:nth-of-type(2) {
  margin-top: 47px;
}

.form-item:nth-of-type(3) {
  margin-top: 47px;
}

/* 表单标签 */
.text_2 {
  width: 160px;
  height: 52px;
  overflow-wrap: break-word;
  color: rgba(121, 121, 121, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 32px;
  margin: 0 0 0 120px;
  display: block;
}

.text_3 {
  width: 128px;
  height: 52px;
  overflow-wrap: break-word;
  color: rgba(121, 121, 121, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 32px;
  margin: 0 0 0 120px;
  display: block;
}

.text_4 {
  width: 192px;
  height: 52px;
  overflow-wrap: break-word;
  color: rgba(121, 121, 121, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 32px;
  margin: 0 0 0 119px;
  display: block;
}

/* 输入框 */
.form-input {
  width: 558px;
  border: none;
  outline: none;
  background: transparent;
  color: rgba(0, 0, 0, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  margin: 8px 0 0 120px;
  padding: 0;
}

.form-item:nth-of-type(3) .form-input {
  margin-left: 119px;
}

.form-line {
  position: absolute;
  bottom: 0;
  left: 120px;
  width: 558px;
  height: 1px;
  background: rgba(0, 0, 0, 1);
}

.form-item:nth-of-type(3) .form-line {
  left: 119px;
}

/* 注册按钮 */
.text-wrapper_1 {
  background-image: linear-gradient(
    86deg,
    rgba(253, 240, 184, 1) 0,
    rgba(209, 240, 254, 1) 100%
  );
  border-radius: 15px;
  height: 81px;
  width: 538px;
  margin: 101px 0 0 116px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.text-wrapper_1:hover {
  transform: scale(1.02);
}

.text-wrapper_1:active {
  transform: scale(0.98);
}

.text_5 {
  width: 80px;
  overflow-wrap: break-word;
  color: rgba(15, 20, 25, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: center;
  white-space: nowrap;
  line-height: 1;
}

/* 登录链接 */
.text-wrapper_3 {
  width: 256px;
  height: 52px;
  margin: 47px 0 181px 257px;
}

.text_6 {
  width: 160px;
  height: 52px;
  overflow-wrap: break-word;
  color: rgba(109, 108, 108, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 32px;
}

.text_7 {
  width: 96px;
  height: 52px;
  overflow-wrap: break-word;
  color: rgba(109, 194, 255, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 32px;
  cursor: pointer;
}

.text_7:hover {
  text-decoration: underline;
}

/* 错误消息 */
.error-message {
  color: #f56c6c;
  font-size: 24px;
  margin: 20px 0 0 120px;
  text-align: left;
  min-height: 30px;
}

/* 禁用状态 */
.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 装饰图片3 - 右侧中间 */
.image_3 {
  width: 395px;
  height: 270px;
  margin: 430px 0 0 138px;
  object-fit: cover;
}

/* 装饰图片4 - 右下角 */
.image_4 {
  width: 234px;
  height: 325px;
  margin: 894px 0 0 56px;
  object-fit: cover;
}

/* 装饰图片5 - 右上角 */
.image-wrapper_2 {
  position: absolute;
  left: 1445px;
  top: 18px;
  width: 208px;
  height: 186px;
}

.image_5 {
  width: 208px;
  height: 186px;
  object-fit: cover;
}

</style>
