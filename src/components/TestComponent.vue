<template>
  <div class="test">
    <h2>测试组件</h2>
    <van-button type="primary" @click="count++">点击次数: {{ count }}</van-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<style scoped>
.test {
  padding: 20px;
  text-align: center;
}
</style> 