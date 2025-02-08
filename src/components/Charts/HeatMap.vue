<template>
  <div class="heat-map">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from '@vue/runtime-core'
import { Chart, registerables } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

Chart.register(...registerables)

interface HeatMapData {
  x: number
  y: number
  value: number
  label?: string
}

const props = defineProps<{
  data: HeatMapData[]
  options?: ChartOptions
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

// 转换数据为散点图格式
const transformData = (data: HeatMapData[]) => {
  return {
    datasets: [{
      label: '参数敏感度',
      data: data.map(d => ({
        x: d.x,
        y: d.y,
        r: Math.abs(d.value) * 10,
        value: d.value,
        label: d.label
      })),
      backgroundColor: (context: any) => {
        const value = context.raw?.value ?? 0
        const alpha = Math.min(Math.abs(value) / 100, 1)
        return value > 0 
          ? `rgba(75, 192, 192, ${alpha})`
          : `rgba(255, 99, 132, ${alpha})`
      }
    }]
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chart = new Chart(chartRef.value, {
    type: 'scatter',
    data: transformData(props.data),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          title: {
            display: true,
            text: '参数值'
          }
        },
        y: {
          type: 'linear',
          title: {
            display: true,
            text: '参数名称'
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const point = context.raw
              const label = point.label ? `${point.label}: ` : ''
              return `${label}敏感度: ${point.value.toFixed(2)}%`
            }
          }
        },
        ...props.options?.plugins
      }
    }
  })
}

// 更新图表数据
const updateChart = () => {
  if (!chart) return
  chart.data = transformData(props.data)
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
    ...chart.options,
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
.heat-map {
  width: 100%;
  height: 100%;
}
</style> 