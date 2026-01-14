<template>
  <DatabaseView @switch-to-scene="$emit('switch-to-scene')" />
</template>

<script setup>
import DatabaseView from '@/components/DatabaseView.vue'

defineEmits(['switch-to-scene'])
</script>
