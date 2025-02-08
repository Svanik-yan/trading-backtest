import { defineStore } from 'pinia'
import { ref } from '@vue/runtime-core'
import { tushareService } from '@/services/tushare'

export interface StockBasic {
  ts_code: string
  symbol: string
  name: string
  area: string
  industry: string
  list_date: string
}

export interface DailyData {
  ts_code: string
  trade_date: string
  open: number
  high: number
  low: number
  close: number
  vol: number
  amount: number
}

export interface TechIndicator {
  ts_code: string
  trade_date: string
  turnover_rate: number
  volume_ratio: number
  pe: number
  pb: number
}

export const useMarketStore = defineStore('market', () => {
  const stockList = ref<StockBasic[]>([])
  const currentStockData = ref<DailyData[]>([])
  const currentTechData = ref<TechIndicator[]>([])
  const loading = ref(false)
  const error = ref('')

  // 获取股票列表
  async function fetchStockList() {
    try {
      loading.value = true
      error.value = ''
      const response = await tushareService.getStockBasic({ list_status: 'L' })
      if (response.code === 0) {
        const fields = response.data.fields
        stockList.value = response.data.items.map(item => {
          const stock: any = {}
          fields.forEach((field, index) => {
            stock[field] = item[index]
          })
          return stock as StockBasic
        })
      } else {
        error.value = response.msg
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取股票列表失败'
    } finally {
      loading.value = false
    }
  }

  // 获取股票历史数据
  async function fetchStockData(params: {
    ts_code: string
    start_date?: string
    end_date?: string
  }) {
    try {
      loading.value = true
      error.value = ''
      const [dailyResponse, techResponse] = await Promise.all([
        tushareService.getDailyData(params),
        tushareService.getTechIndicator(params)
      ])

      if (dailyResponse.code === 0) {
        const fields = dailyResponse.data.fields
        currentStockData.value = dailyResponse.data.items.map(item => {
          const daily: any = {}
          fields.forEach((field, index) => {
            daily[field] = item[index]
          })
          return daily as DailyData
        })
      }

      if (techResponse.code === 0) {
        const fields = techResponse.data.fields
        currentTechData.value = techResponse.data.items.map(item => {
          const tech: any = {}
          fields.forEach((field, index) => {
            tech[field] = item[index]
          })
          return tech as TechIndicator
        })
      }

      if (dailyResponse.code !== 0 || techResponse.code !== 0) {
        error.value = dailyResponse.msg || techResponse.msg
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取股票数据失败'
    } finally {
      loading.value = false
    }
  }

  return {
    stockList,
    currentStockData,
    currentTechData,
    loading,
    error,
    fetchStockList,
    fetchStockData
  }
}) 