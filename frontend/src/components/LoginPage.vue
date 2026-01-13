<template>
  <div class="page">
    <div class="section_1">
      <div class="group_1 flex-row">
        <!-- 装饰图片1 - 左下角 -->
        <img
          class="image_1"
          src="/images/decoration1.png"
          alt="Decoration 1"
        />
        <!-- 装饰图片2 - 左侧中间 -->
        <img
          class="image_2"
          src="/images/decoration3.png"
          alt="Decoration 3"
        />
        <!-- 登录卡片 -->
        <div class="group_2 flex-col">
          <span class="text_1">登录 Login</span>
          <div class="form-item">
            <label class="text_2">用户名 username</label>
            <input v-model="username" type="text" class="form-input" />
            <div class="form-line"></div>
          </div>
          <div class="form-item">
            <label class="text_3">密码 password</label>
            <input v-model="password" type="password" class="form-input" />
            <div class="form-line"></div>
          </div>
          <div class="text-wrapper_1 flex-col" @click="handleLogin">
            <span class="text_5">登 录</span>
          </div>
          <div class="text-wrapper_2 flex-row justify-between">
            <span class="text_6">没有账号？</span>
            <span class="text_7" @click="$emit('switch-to-register')">注册一个</span>
          </div>
        </div>
        <!-- 装饰图片3 - 右侧中间 -->
        <img
          class="image_3"
          src="/images/decoration4.png"
          alt="Decoration 4"
        />
        <!-- 装饰图片4 - 右下角 -->
        <img
          class="image_4"
          src="/images/decoration5.png"
          alt="Decoration 5"
        />
      </div>
      <!-- 装饰图片5 - 右上角 -->
      <div class="image-wrapper_1 flex-row">
        <img
          class="image_5"
          src="/images/decoration2.png"
          alt="Decoration 2"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref('')
const password = ref('')

function handleLogin() {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }
  // 登录逻辑
  console.log('登录:', username.value, password.value)
  emit('close')
}

const emit = defineEmits(['close', 'switch-to-register'])
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
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 背景区域 */
.section_1 {
  height: 1562px;
  background: url(/images/background.png) 100% no-repeat;
  background-size: 100% 100%;
  margin-left: -47px;
  width: 2778px;
  position: relative;
  max-width: 100vw;
  max-height: 100vh;
}

/* 主要内容组 */
.group_1 {
  width: 2489px;
  height: 1219px;
  margin: 181px 0 0 47px;
  position: relative;
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
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
}

/* 登录卡片 */
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
  width: 293px;
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

/* 表单标签 */
.text_2 {
  width: 240px;
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
  width: 203px;
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

/* 输入框 */
.form-input {
  width: 558px;
  border: none;
  outline: none;
  background: transparent;
  color: rgba(0, 0, 0, 1);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', sans-serif;
  margin: 0 0 0 120px;
  padding: 0;
}

.form-line {
  position: absolute;
  bottom: 0;
  left: 120px;
  width: 558px;
  height: 1px;
  background: rgba(0, 0, 0, 1);
}

/* 登录按钮 */
.text-wrapper_1 {
  background-image: linear-gradient(
    163deg,
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
  width: 89px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(15, 20, 25, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
}

/* 注册链接 */
.text-wrapper_2 {
  width: 288px;
  height: 52px;
  margin: 81px 0 181px 113px;
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
  width: 128px;
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

/* 装饰图片3 - 右侧中间 */
.image_3 {
  width: 450.5px;
  height: 362.49px;
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
.image-wrapper_1 {
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
  box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.25);
}

/* 响应式调整 */
@media (max-width: 2560px) {
  .page {
    transform: scale(calc(100vw / 2560));
    transform-origin: top left;
  }
  
  .section_1 {
    transform: scale(1);
  }
}

@media (max-width: 1920px) {
  .page {
    transform: scale(calc(100vw / 2560));
  }
}

@media (max-width: 1440px) {
  .page {
    transform: scale(calc(100vw / 2560));
  }
  
  .group_2 {
    padding: 0 20px;
  }
  
  .text_1 {
    font-size: 48px;
    margin-left: 20px;
  }
  
  .text_2,
  .text_3,
  .form-input {
    font-size: 24px;
  }
  
  .form-input,
  .form-line {
    width: calc(100% - 240px);
    max-width: 480px;
  }
  
  .text-wrapper_1 {
    width: 100%;
    max-width: 480px;
    margin-left: 20px;
  }
}

@media (max-width: 768px) {
  .page {
    transform: scale(1);
  }
  
  .section_1 {
    width: 100vw;
    margin-left: 0;
    background-size: cover;
  }
  
  .group_1 {
    width: 100%;
    margin: 50px 0 0 0;
    flex-wrap: wrap;
  }
  
  .group_2 {
    width: 90vw;
    max-width: 500px;
    margin: 0 auto;
    height: auto;
    min-height: 600px;
  }
  
  .image_1,
  .image_2,
  .image_3,
  .image_4,
  .image-wrapper_1 {
    display: none;
  }
  
  .text_1 {
    font-size: 36px;
    margin: 60px auto 0;
    text-align: center;
  }
  
  .text_2,
  .text_3 {
    margin-left: 20px;
  }
  
  .form-input,
  .form-line {
    margin-left: 20px;
    width: calc(100% - 40px);
  }
  
  .text-wrapper_1 {
    margin-left: 20px;
    width: calc(100% - 40px);
  }
  
  .text-wrapper_2 {
    margin-left: 20px;
  }
}
</style>
