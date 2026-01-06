<template>
  <CesiumViewer />
</template>

<script>
import CesiumViewer from './components/CesiumViewer.vue'

export default {
  name: 'App',
  components: {
    CesiumViewer
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

body {
  overflow: hidden;
}
</style>