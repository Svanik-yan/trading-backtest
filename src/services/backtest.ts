import type { DailyData, TechIndicator } from '@/stores/market'

export interface Position {
  ts_code: string
  quantity: number
  cost: number
  value: number
  profit: number
}

export interface Trade {
  ts_code: string
  trade_date: string
  type: 'buy' | 'sell'
  price: number
  quantity: number
  amount: number
}

export interface DailyReturn {
  date: string
  value: number
}

export interface BacktestResult {
  trades: Trade[]
  positions: Position[]
  totalValue: number
  totalProfit: number
  maxDrawdown: number
  winRate: number
  profitRatio: number
  annualReturn: number
  sharpeRatio: number
  maxConsecutiveLosses: number
  avgWinAmount: number
  avgLossAmount: number
  maxSingleWin: number
  maxSingleLoss: number
  dailyReturns: DailyReturn[]
}

export interface BacktestConfig {
  initialCapital: number
  startDate: string
  endDate: string
  commissionRate: number
  slippageRate: number
}

export class BacktestEngine {
  private stockData: DailyData[]
  private techData: TechIndicator[]
  private config: BacktestConfig
  private capital: number
  private positions: Map<string, Position>
  private trades: Trade[]
  private dailyReturns: { date: string; value: number }[]

  constructor(
    stockData: DailyData[],
    techData: TechIndicator[],
    config: BacktestConfig
  ) {
    this.stockData = stockData.sort((a, b) => 
      a.trade_date.localeCompare(b.trade_date)
    )
    this.techData = techData.sort((a, b) => 
      a.trade_date.localeCompare(b.trade_date)
    )
    this.config = config
    this.capital = config.initialCapital
    this.positions = new Map()
    this.trades = []
    this.dailyReturns = []
  }

  // 计算交易成本
  private calculateCost(price: number, quantity: number): number {
    const amount = price * quantity
    const commission = amount * this.config.commissionRate
    const slippage = amount * this.config.slippageRate
    return commission + slippage
  }

  // 执行买入操作
  protected buy(date: string, price: number, quantity: number): void {
    const cost = this.calculateCost(price, quantity)
    const totalCost = price * quantity + cost

    if (totalCost > this.capital) {
      quantity = Math.floor((this.capital - cost) / price)
      if (quantity <= 0) return
    }

    const trade: Trade = {
      ts_code: this.stockData[0].ts_code,
      trade_date: date,
      type: 'buy',
      price,
      quantity,
      amount: price * quantity
    }

    const position = this.positions.get(trade.ts_code) || {
      ts_code: trade.ts_code,
      quantity: 0,
      cost: 0,
      value: 0,
      profit: 0
    }

    position.quantity += quantity
    position.cost += totalCost
    position.value = position.quantity * price
    position.profit = position.value - position.cost

    this.positions.set(trade.ts_code, position)
    this.capital -= totalCost
    this.trades.push(trade)
  }

  // 执行卖出操作
  protected sell(date: string, price: number, quantity: number): void {
    const position = this.positions.get(this.stockData[0].ts_code)
    if (!position || position.quantity < quantity) return

    const cost = this.calculateCost(price, quantity)
    const trade: Trade = {
      ts_code: this.stockData[0].ts_code,
      trade_date: date,
      type: 'sell',
      price,
      quantity,
      amount: price * quantity
    }

    position.quantity -= quantity
    const sellValue = price * quantity - cost
    this.capital += sellValue

    if (position.quantity === 0) {
      this.positions.delete(trade.ts_code)
    } else {
      position.value = position.quantity * price
      position.profit = position.value - position.cost
      this.positions.set(trade.ts_code, position)
    }

    this.trades.push(trade)
  }

  // 更新每日收益
  private updateDailyReturn(date: string): void {
    let totalValue = this.capital
    for (const position of this.positions.values()) {
      totalValue += position.value
    }

    const dailyReturn = {
      date,
      value: totalValue
    }
    this.dailyReturns.push(dailyReturn)
  }

  // 计算夏普比率
  private calculateSharpeRatio(returns: number[]): number {
    const riskFreeRate = 0.03 // 假设无风险利率为3%
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
    const excessReturns = returns.map(r => r - riskFreeRate / 252) // 转换为日化无风险利率
    const stdDev = Math.sqrt(
      excessReturns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / (returns.length - 1)
    )
    return stdDev === 0 ? 0 : (avgReturn - riskFreeRate / 252) / stdDev * Math.sqrt(252) // 年化夏普比率
  }

  // 计算最大连续亏损次数
  private calculateMaxConsecutiveLosses(returns: number[]): number {
    let maxConsecutive = 0
    let current = 0
    
    for (const ret of returns) {
      if (ret < 0) {
        current++
        maxConsecutive = Math.max(maxConsecutive, current)
      } else {
        current = 0
      }
    }
    
    return maxConsecutive
  }

  // 计算日收益率序列
  private calculateDailyReturns(): number[] {
    const returns: number[] = []
    for (let i = 1; i < this.dailyReturns.length; i++) {
      const todayValue = this.dailyReturns[i].value
      const yesterdayValue = this.dailyReturns[i - 1].value
      returns.push((todayValue - yesterdayValue) / yesterdayValue)
    }
    return returns
  }

  // 计算回测结果
  private calculateResults(): BacktestResult {
    const initialValue = this.config.initialCapital
    let totalValue = this.capital
    let maxDrawdown = 0
    let peakValue = initialValue
    let totalWinCount = 0
    let totalTradeCount = 0

    // 计算总价值和最大回撤
    for (const position of this.positions.values()) {
      totalValue += position.value
    }

    this.dailyReturns.forEach(daily => {
      if (daily.value > peakValue) {
        peakValue = daily.value
      }
      const drawdown = (peakValue - daily.value) / peakValue
      maxDrawdown = Math.max(maxDrawdown, drawdown)
    })

    // 计算胜率
    this.trades.forEach(trade => {
      if (trade.type === 'sell') {
        totalTradeCount++
        const buyTrade = this.trades.find(t => 
          t.type === 'buy' && 
          t.ts_code === trade.ts_code && 
          t.trade_date < trade.trade_date
        )
        if (buyTrade && trade.price > buyTrade.price) {
          totalWinCount++
        }
      }
    })

    const totalProfit = totalValue - initialValue
    const winRate = totalTradeCount > 0 ? totalWinCount / totalTradeCount : 0
    const profitRatio = initialValue > 0 ? totalProfit / initialValue : 0

    // 计算年化收益率
    const startDate = new Date(this.config.startDate)
    const endDate = new Date(this.config.endDate)
    const years = (endDate.getTime() - startDate.getTime()) / (365 * 24 * 60 * 60 * 1000)
    const annualReturn = years > 0 ? Math.pow(1 + profitRatio, 1 / years) - 1 : 0

    // 计算日收益率序列
    const dailyReturns = this.calculateDailyReturns()
    
    // 计算夏普比率
    const sharpeRatio = this.calculateSharpeRatio(dailyReturns)
    
    // 计算最大连续亏损次数
    const maxConsecutiveLosses = this.calculateMaxConsecutiveLosses(dailyReturns)

    // 计算交易统计
    let totalWinAmount = 0
    let totalLossAmount = 0
    let profitTradeCount = 0
    let lossTradeCount = 0
    let maxSingleWin = 0
    let maxSingleLoss = 0

    // 遍历所有卖出交易
    for (let i = 0; i < this.trades.length; i++) {
      const trade = this.trades[i]
      if (trade.type === 'sell') {
        const buyTrade = this.trades.find(t => 
          t.type === 'buy' && 
          t.ts_code === trade.ts_code && 
          t.trade_date < trade.trade_date
        )
        
        if (buyTrade) {
          const profit = (trade.price - buyTrade.price) * trade.quantity
          if (profit > 0) {
            totalWinAmount += profit
            profitTradeCount++
            maxSingleWin = Math.max(maxSingleWin, profit)
          } else {
            totalLossAmount += Math.abs(profit)
            lossTradeCount++
            maxSingleLoss = Math.min(maxSingleLoss, profit)
          }
        }
      }
    }

    const avgWinAmount = profitTradeCount > 0 ? totalWinAmount / profitTradeCount : 0
    const avgLossAmount = lossTradeCount > 0 ? -totalLossAmount / lossTradeCount : 0

    return {
      trades: this.trades,
      positions: Array.from(this.positions.values()),
      totalValue,
      totalProfit,
      maxDrawdown,
      winRate,
      profitRatio,
      annualReturn,
      sharpeRatio,
      maxConsecutiveLosses,
      avgWinAmount,
      avgLossAmount,
      maxSingleWin,
      maxSingleLoss,
      dailyReturns: this.dailyReturns
    }
  }

  // 运行回测
  public run(strategy: (data: DailyData, tech: TechIndicator) => { action: 'buy' | 'sell' | 'hold', quantity?: number }): BacktestResult {
    for (let i = 0; i < this.stockData.length; i++) {
      const data = this.stockData[i]
      const tech = this.techData.find(t => t.trade_date === data.trade_date)
      
      if (!tech) continue

      const signal = strategy(data, tech)
      const price = data.close

      if (signal.action === 'buy') {
        const quantity = signal.quantity || Math.floor(this.capital / (price * (1 + this.config.commissionRate)))
        this.buy(data.trade_date, price, quantity)
      } else if (signal.action === 'sell') {
        const position = this.positions.get(data.ts_code)
        const quantity = signal.quantity || (position?.quantity || 0)
        this.sell(data.trade_date, price, quantity)
      }

      this.updateDailyReturn(data.trade_date)
    }

    return this.calculateResults()
  }
} 