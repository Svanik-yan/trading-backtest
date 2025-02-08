<template>
  <div class="line-chart">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from '@vue/runtime-core'
import { Chart, registerables } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  data: ChartData
  options?: ChartOptions
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chart = new Chart(chartRef.value, {
    type: 'line',
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options
    }
  })
}

// 更新图表数据
const updateChart = () => {
  if (!chart) return
  chart.data = props.data
  chart.update()
}

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 监听配置变化
watch(() => props.options, () => {
  if (!chart) return
  chart.options = {
    responsive: true,
    maintainAspectRatio: false,
    ...props.options
  }
  chart.update()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
    chart = null
  }
})
</script>

<style scoped>
.line-chart {
  width: 100%;
  height: 100%;
}
</style> 