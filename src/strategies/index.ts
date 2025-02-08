import type { DailyData, TechIndicator } from '@/stores/market'

// 计算移动平均线
function calculateMA(prices: number[], period: number): number[] {
  const ma: number[] = []
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      ma.push(NaN)
      continue
    }
    const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
    ma.push(sum / period)
  }
  return ma
}

// 计算MACD
function calculateMACD(prices: number[], fastPeriod = 12, slowPeriod = 26, signalPeriod = 9): {
  DIF: number[]
  DEA: number[]
  MACD: number[]
} {
  // 计算EMA
  const calculateEMA = (data: number[], period: number): number[] => {
    const k = 2 / (period + 1)
    const ema: number[] = []
    let prevEMA = data[0]

    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        ema.push(data[0])
      } else {
        prevEMA = (data[i] - prevEMA) * k + prevEMA
        ema.push(prevEMA)
      }
    }
    return ema
  }

  const fastEMA = calculateEMA(prices, fastPeriod)
  const slowEMA = calculateEMA(prices, slowPeriod)
  
  // 计算DIF
  const DIF = fastEMA.map((fast, i) => fast - slowEMA[i])
  
  // 计算DEA
  const DEA = calculateEMA(DIF, signalPeriod)
  
  // 计算MACD
  const MACD = DIF.map((dif, i) => (dif - DEA[i]) * 2)

  return { DIF, DEA, MACD }
}

// 计算RSI
function calculateRSI(prices: number[], period = 14): number[] {
  const rsi: number[] = []
  let gains: number[] = []
  let losses: number[] = []

  // 计算价格变化
  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1]
    gains.push(change > 0 ? change : 0)
    losses.push(change < 0 ? -change : 0)
  }

  // 计算RSI
  for (let i = 0; i < prices.length; i++) {
    if (i < period) {
      rsi.push(NaN)
      continue
    }

    const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b) / period
    const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b) / period

    if (avgLoss === 0) {
      rsi.push(100)
    } else {
      const RS = avgGain / avgLoss
      rsi.push(100 - (100 / (1 + RS)))
    }
  }

  return rsi
}

// 均线交叉策略
export function maStrategy(data: DailyData, tech: TechIndicator, shortPeriod = 5, longPeriod = 20) {
  const prices = data.close
  const shortMA = calculateMA([prices], shortPeriod)[0]
  const longMA = calculateMA([prices], longPeriod)[0]
  const prevShortMA = calculateMA([data.close], shortPeriod)[0]
  const prevLongMA = calculateMA([data.close], longPeriod)[0]

  // 金叉：短期均线上穿长期均线
  if (prevShortMA <= prevLongMA && shortMA > longMA) {
    return { action: 'buy' as const }
  }
  // 死叉：短期均线下穿长期均线
  else if (prevShortMA >= prevLongMA && shortMA < longMA) {
    return { action: 'sell' as const }
  }

  return { action: 'hold' as const }
}

// MACD策略
export function macdStrategy(data: DailyData, tech: TechIndicator) {
  const prices = [data.close]
  const { MACD, DIF, DEA } = calculateMACD(prices)
  const currentMACD = MACD[MACD.length - 1]
  const prevMACD = MACD[MACD.length - 2]

  // MACD由负转正，买入信号
  if (prevMACD < 0 && currentMACD > 0) {
    return { action: 'buy' as const }
  }
  // MACD由正转负，卖出信号
  else if (prevMACD > 0 && currentMACD < 0) {
    return { action: 'sell' as const }
  }

  return { action: 'hold' as const }
}

// RSI策略
export function rsiStrategy(data: DailyData, tech: TechIndicator, oversold = 30, overbought = 70) {
  const prices = [data.close]
  const rsi = calculateRSI(prices)[prices.length - 1]

  // RSI低于超卖线，买入信号
  if (rsi < oversold) {
    return { action: 'buy' as const }
  }
  // RSI高于超买线，卖出信号
  else if (rsi > overbought) {
    return { action: 'sell' as const }
  }

  return { action: 'hold' as const }
}

// 策略映射表
export const strategies = {
  ma: {
    name: '均线策略',
    description: '基于移动平均线的交叉策略',
    execute: maStrategy
  },
  macd: {
    name: 'MACD策略',
    description: '基于MACD指标的趋势跟踪策略',
    execute: macdStrategy
  },
  rsi: {
    name: 'RSI策略',
    description: '基于RSI超买超卖的反转策略',
    execute: rsiStrategy
  }
} 