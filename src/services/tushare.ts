import axios from 'axios'

export interface TushareResponse {
  code: number
  msg: string
  data: {
    fields: string[]
    items: any[][]
  }
}

class TushareService {
  private token: string
  private baseURL = 'http://api.tushare.pro'

  constructor(token: string) {
    this.token = token
  }

  private async request(api_name: string, params: any = {}): Promise<TushareResponse> {
    try {
      const response = await axios.post(this.baseURL, {
        api_name,
        token: this.token,
        params,
        fields: api_name === 'stock_basic' ? [
          'ts_code',
          'symbol',
          'name',
          'area',
          'industry',
          'list_date',
          'market',
          'exchange',
          'curr_type',
          'list_status',
          'delist_date',
          'is_hs'
        ] : undefined
      })
      return response.data
    } catch (error) {
      console.error('Tushare API Error:', error)
      throw error
    }
  }

  // 格式化股票代码
  private formatStockCode(code: string): string {
    // 移除所有空格
    code = code.replace(/\s/g, '')
    
    // 如果已经包含后缀，直接返回
    if (code.includes('.')) {
      return code.toUpperCase()
    }

    // 根据股票代码规则添加后缀
    if (code.startsWith('6')) {
      return `${code}.SH`
    } else if (code.startsWith('0') || code.startsWith('3')) {
      return `${code}.SZ`
    } else if (code.startsWith('8') || code.startsWith('4')) {
      return `${code}.BJ`
    }
    
    return code
  }

  // 获取股票基础信息
  async getStockBasic(params: { 
    ts_code?: string
    list_status?: string 
  } = {}) {
    const apiParams: any = {
      exchange: '',
      list_status: params.list_status || 'L'
    }
    
    if (params.ts_code) {
      apiParams.ts_code = this.formatStockCode(params.ts_code)
    }

    return this.request('stock_basic', apiParams)
  }

  // 获取日线行情
  async getDailyData(params: {
    ts_code: string
    trade_date?: string
    start_date?: string
    end_date?: string
  }) {
    const apiParams = {
      ts_code: this.formatStockCode(params.ts_code),
      start_date: params.start_date,
      end_date: params.end_date,
      freq: 'D',
      asset: 'E'
    }
    return this.request('daily', apiParams)
  }

  // 获取财务指标数据
  async getFinanceIndicator(params: {
    ts_code: string
    period?: string
    start_date?: string
    end_date?: string
  }) {
    const apiParams = {
      ts_code: this.formatStockCode(params.ts_code),
      period: params.period,
      start_date: params.start_date,
      end_date: params.end_date
    }
    return this.request('fina_indicator', apiParams)
  }

  // 获取技术指标数据
  async getTechIndicator(params: {
    ts_code: string
    start_date?: string
    end_date?: string
  }) {
    const apiParams = {
      ts_code: this.formatStockCode(params.ts_code),
      start_date: params.start_date,
      end_date: params.end_date
    }
    return this.request('daily_basic', apiParams)
  }

  // 搜索股票
  async searchStock(keyword: string) {
    try {
      const formattedCode = this.formatStockCode(keyword)
      
      // 构建搜索参数
      const searchParams: any = {
        list_status: 'L'
      }

      // 如果是股票代码格式，使用精确搜索
      if (/^\d{6}$/.test(keyword) || /^\d{6}\.(SH|SZ|BJ)$/i.test(keyword)) {
        searchParams.ts_code = formattedCode
      } else {
        // 如果是股票名称，使用模糊搜索
        searchParams.name = keyword
      }

      const response = await this.getStockBasic(searchParams)
      
      // 如果没有找到结果，尝试获取所有股票列表
      if (response.code === 0 && response.data.items.length === 0) {
        return this.getStockBasic({ list_status: 'L' })
      }

      return response
    } catch (error) {
      console.error('Stock search error:', error)
      throw error
    }
  }

  // 获取实时行情
  async getRealTimeQuote(params: {
    ts_code?: string
    trade_date?: string
  }) {
    const apiParams: any = {}
    
    if (params.ts_code) {
      apiParams.ts_code = this.formatStockCode(params.ts_code)
    }
    
    if (params.trade_date) {
      apiParams.trade_date = params.trade_date
    }

    return this.request('quotes', apiParams)
  }
}

export const tushareService = new TushareService(import.meta.env.VITE_TUSHARE_TOKEN) 