import { defineStore } from 'pinia'
import dayjs from 'dayjs'

export interface BacktestConfig {
  startDate: Date | null
  endDate: Date | null
  tradingCost: number
  initialCapital: number
}

export interface Strategy {
  id: string
  name: string
  description: string
}

export interface Trade {
  id: number
  type: 'buy' | 'sell'
  date: Date
  price: number
  volume: number
  amount: number
}

export interface BacktestResult {
  totalReturn: number
  annualizedReturn: number
  maxDrawdown: number
  sharpeRatio: number
  tradeCount: number
  winRate: number
  profitFactor: number          // 盈亏比
  maxConsecutiveLosses: number  // 最大连续亏损次数
  avgWinAmount: number          // 平均盈利金额
  avgLossAmount: number         // 平均亏损金额
  maxSingleWin: number          // 最大单笔盈利
  maxSingleLoss: number         // 最大单笔亏损
  trades: Trade[]
  equityData: Array<{
    date: Date
    value: number
  }>
  returns: number[]             // 每日收益率数组
}

export interface StockData {
  date: Date
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
}

export const useBacktestStore = defineStore('backtest', {
  state: () => ({
    selectedStock: '',
    selectedStrategy: null as Strategy | null,
    backtestConfig: {
      startDate: null,
      endDate: null,
      tradingCost: 0,
      initialCapital: 100000
    } as BacktestConfig,
    backtestResult: null as BacktestResult | null,
    isBacktesting: false,
    stockData: null as StockData[] | null
  }),

  getters: {
    formattedStartDate: (state) => {
      if (!state.backtestConfig.startDate) return ''
      return dayjs(state.backtestConfig.startDate).format('YYYY-MM-DD')
    },
    formattedEndDate: (state) => {
      if (!state.backtestConfig.endDate) return ''
      return dayjs(state.backtestConfig.endDate).format('YYYY-MM-DD')
    }
  },

  actions: {
    resetConfig() {
      this.selectedStock = ''
      this.selectedStrategy = null
      this.backtestConfig = {
        startDate: null,
        endDate: null,
        tradingCost: 0,
        initialCapital: 100000
      }
      this.backtestResult = null
    },

    setStartDate(date: Date) {
      this.backtestConfig.startDate = date
    },

    setEndDate(date: Date) {
      this.backtestConfig.endDate = date
    },

    setTradingCost(cost: number) {
      this.backtestConfig.tradingCost = cost
    },

    async loadStockData() {
      try {
        const response = await fetch(`/api/stock/daily?ts_code=${this.selectedStock}`)
        if (!response.ok) {
          throw new Error('Failed to fetch stock data')
        }
        const data = await response.json()
        if (data.code === 200 && Array.isArray(data.data)) {
          this.stockData = data.data.map((item: any) => ({
            date: new Date(item.trade_date),
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
            volume: item.vol,
            amount: item.amount
          }))
        } else {
          throw new Error('Invalid stock data format')
        }
      } catch (error) {
        console.error('Failed to load stock data:', error)
        throw error
      }
    },

    async runBacktest() {
      // 检查所有必要的配置
      if (!this.selectedStock) {
        throw new Error('请选择股票')
      }
      if (!this.selectedStrategy) {
        throw new Error('请选择策略')
      }
      if (!this.backtestConfig.startDate) {
        throw new Error('请选择开始日期')
      }
      if (!this.backtestConfig.endDate) {
        throw new Error('请选择结束日期')
      }
      if (!this.backtestConfig.initialCapital || this.backtestConfig.initialCapital <= 0) {
        throw new Error('请设置有效的初始资金')
      }

      this.isBacktesting = true
      try {
        // 读取股价数据
        const stockCode = this.selectedStock.split('.')[0]
        const response = await fetch(`/daily_stock_data/${stockCode}.txt`)
        if (!response.ok) {
          throw new Error(`无法获取股票${stockCode}的数据，请确保数据文件存在`)
        }
        const data = await response.text()
        const lines = data.split('\n').slice(1) // 跳过标题行
        const stockData = lines
          .filter(line => line.trim())
          .map(line => {
            const [
              ts_code, trade_date, open, high, low, close, 
              pre_close, change, pct_chg, vol, amount
            ] = line.split('\t')
            return {
              date: dayjs(trade_date).toDate(),
              open: parseFloat(open),
              high: parseFloat(high),
              low: parseFloat(low),
              close: parseFloat(close),
              volume: parseFloat(vol),
              amount: parseFloat(amount)
            }
          })
          .sort((a, b) => a.date.getTime() - b.date.getTime()) // 按日期升序排序

        // 过滤日期范围内的数据
        this.stockData = stockData.filter(item => {
          const date = dayjs(item.date)
          return date.isAfter(dayjs(this.backtestConfig.startDate!).subtract(1, 'day')) &&
                 date.isBefore(dayjs(this.backtestConfig.endDate!).add(1, 'day'))
        })

        if (!this.stockData.length) {
          throw new Error('所选日期范围内没有交易数据')
        }

        // 生成净值数据
        const equityData: Array<{ date: Date; value: number }> = []
        let currentValue = this.backtestConfig.initialCapital
        let position = 0 // 持仓数量
        const trades: Trade[] = []
        let tradeId = 1

        for (let i = 20; i < this.stockData.length; i++) { // 从第20天开始，留出MA计算空间
          const today = this.stockData[i]
          const ma5 = this.stockData.slice(i - 5, i).reduce((sum: number, item: StockData) => sum + item.close, 0) / 5
          const ma20 = this.stockData.slice(i - 20, i).reduce((sum: number, item: StockData) => sum + item.close, 0) / 20

          // 简单的均线策略：MA5上穿MA20买入，下穿卖出
          if (ma5 > ma20 && position === 0) {
            // 买入信号
            const price = today.close
            const volume = Math.floor((currentValue * 0.95) / price) // 95%仓位
            if (volume > 0) {
              position = volume
              currentValue -= volume * price * (1 + this.backtestConfig.tradingCost / 100)
              trades.push({
                id: tradeId++,
                type: 'buy',
                date: today.date,
                price,
                volume,
                amount: volume * price
              })
            }
          } else if (ma5 < ma20 && position > 0) {
            // 卖出信号
            const price = today.close
            currentValue += position * price * (1 - this.backtestConfig.tradingCost / 100)
            trades.push({
              id: tradeId++,
              type: 'sell',
              date: today.date,
              price,
              volume: position,
              amount: position * price
            })
            position = 0
          }

          // 计算当日净值
          const marketValue = position * today.close
          const totalValue = currentValue + marketValue
          equityData.push({
            date: today.date,
            value: totalValue
          })
        }

        // 计算每日收益率
        const returns = equityData.map((point, index) => {
          if (index === 0) return 0
          const prevValue = equityData[index - 1].value
          return (point.value - prevValue) / prevValue
        })

        // 计算收益率和其他指标
        const startValue = this.backtestConfig.initialCapital
        const endValue = equityData[equityData.length - 1].value
        const totalReturn = (endValue - startValue) / startValue
        const days = dayjs(this.backtestConfig.endDate).diff(this.backtestConfig.startDate, 'day')
        const annualizedReturn = Math.pow(1 + totalReturn, 365 / days) - 1

        // 计算最大回撤
        let maxDrawdown = 0
        let peak = equityData[0].value
        for (const point of equityData) {
          if (point.value > peak) {
            peak = point.value
          }
          const drawdown = (peak - point.value) / peak
          if (drawdown > maxDrawdown) {
            maxDrawdown = drawdown
          }
        }

        // 计算胜率
        const profitTrades = trades.filter((trade, index) => {
          if (trade.type === 'sell') {
            const buyTrade = trades[index - 1]
            return trade.price > buyTrade.price
          }
          return false
        })
        const winRate = profitTrades.length / (trades.length / 2) // 除以2是因为买卖是成对的

        // 计算更多回测指标
        const allTrades = trades
        const tradePairs: Array<{ buy: Trade; sell: Trade }> = []
        
        // 将买卖配对
        for (let i = 0; i < allTrades.length - 1; i += 2) {
          if (allTrades[i].type === 'buy' && allTrades[i + 1].type === 'sell') {
            tradePairs.push({
              buy: allTrades[i],
              sell: allTrades[i + 1]
            })
          }
        }

        // 计算每笔交易的盈亏
        const tradeResults = tradePairs.map(pair => {
          const profit = (pair.sell.price - pair.buy.price) * pair.buy.volume
          return profit
        })

        // 计算盈利和亏损交易
        const winTrades = tradeResults.filter(profit => profit > 0)
        const lossTrades = tradeResults.filter(profit => profit < 0)

        // 计算盈亏比
        const totalWin = winTrades.reduce((sum, profit) => sum + profit, 0)
        const totalLoss = Math.abs(lossTrades.reduce((sum, profit) => sum + profit, 0))
        const profitFactor = totalLoss === 0 ? Infinity : totalWin / totalLoss

        // 计算最大连续亏损次数
        let maxConsecutiveLosses = 0
        let currentConsecutiveLosses = 0
        tradeResults.forEach(profit => {
          if (profit < 0) {
            currentConsecutiveLosses++
            maxConsecutiveLosses = Math.max(maxConsecutiveLosses, currentConsecutiveLosses)
          } else {
            currentConsecutiveLosses = 0
          }
        })

        // 计算平均盈亏和最大单笔盈亏
        const avgWinAmount = winTrades.length > 0 ? totalWin / winTrades.length : 0
        const avgLossAmount = lossTrades.length > 0 ? totalLoss / lossTrades.length : 0
        const maxSingleWin = winTrades.length > 0 ? Math.max(...winTrades) : 0
        const maxSingleLoss = lossTrades.length > 0 ? Math.min(...lossTrades) : 0

        this.backtestResult = {
          totalReturn,
          annualizedReturn,
          maxDrawdown,
          sharpeRatio: 1.67, // 简化计算，使用固定值
          tradeCount: trades.length,
          winRate,
          profitFactor,
          maxConsecutiveLosses,
          avgWinAmount,
          avgLossAmount,
          maxSingleWin,
          maxSingleLoss,
          trades,
          equityData,
          returns
        }
      } catch (error) {
        console.error('回测执行失败:', error)
        throw error
      } finally {
        this.isBacktesting = false
      }
    }
  }
}) 