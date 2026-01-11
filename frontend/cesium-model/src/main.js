import { createApp } from 'vue'
import App from './App.vue'

// 设置 Cesium 访问令牌
if (window.Cesium) {
  window.Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYWE1OWUxNy1mMWZiLTQzYjYtYTQ0OS1kMWFjYmFkN2Y0YzciLCJpZCI6MjAzOTIsInNjb3BlcyI6WyJhc3IiLCJnYyJdLCJpYXQiOjE1NzE4NTI0ODJ9.t-p1cTU0TLmtdKXQ-4WEsG2qWlP6CbMkQCFaBqOjZ-w';
}

createApp(App).mount('#app')