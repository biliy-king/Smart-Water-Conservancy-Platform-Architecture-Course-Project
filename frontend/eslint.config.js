import js from '@eslint/js'
import globals from 'globals'
import vue from 'eslint-plugin-vue'

export default [
  {
    files: ['**/*.{js,vue}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        Cesium: 'readonly',  // 允许 Cesium 全局变量
        CESIUM_BASE_URL: 'readonly'
      }
    },
    rules: {
      ...js.configs.recommended.rules,
      ...vue.configs['vue3-recommended'].rules
    }
  }
]