import pandas as pd
import numpy as np
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta
import streamlit as st
import time
import os

class DataLoader:
    def __init__(self, data_dir="public/daily_stock_data"):
        """初始化数据加载器"""
        self.data_dir = Path(data_dir)
        self.base_dir = self.data_dir.parent  # public目录
        self.api_token = '750ad66d1a5440e5884dcfb6379ab147'
        self.base_url = 'https://tsanghi.com/api/fin/stock'
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_stock_list(self):
        """从API获取股票列表"""
        try:
            # 获取上海和深圳的股票列表
            sh_stocks = self._get_exchange_stocks('XSHG')  # 上海证券交易所
            sz_stocks = self._get_exchange_stocks('XSHE')  # 深圳证券交易所
            
            # 合并股票列表
            all_stocks = sh_stocks + sz_stocks
            
            # 保存到文件
            stock_list_path = Path("stock_list.txt")
            with open(stock_list_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'msg': '操作成功',
                    'code': 200,
                    'data': all_stocks
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            st.error(f"获取股票列表失败: {str(e)}")
            return False
            
    def _get_exchange_stocks(self, exchange):
        """获取指定交易所的股票列表"""
        url = f"{self.base_url}/{exchange}/list?token={self.api_token}"
        response = requests.get(url)
        return response.json()['data'] if response.json()['code'] == 200 else []
        
    def load_stock_list(self):
        """加载股票列表"""
        try:
            # 从根目录下的stock_list.txt加载
            stock_list_path = Path("stock_list.txt")
            
            # 如果文件不存在或为空，尝试重新获取
            if not stock_list_path.exists() or stock_list_path.stat().st_size == 0:
                if not self.fetch_stock_list():
                    return self._get_default_stock_list()
            
            # 读取JSON格式的文件
            with open(stock_list_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data['code'] == 200 and data['data']:
                    stock_list = pd.DataFrame(data['data'])
                    # 转换列名以匹配所需格式
                    stock_list['ts_code'] = stock_list.apply(
                        lambda x: f"{x['ticker']}.{x['exchange_code'][-2:]}", axis=1
                    )
                    stock_list['symbol'] = stock_list['ticker']
                    
                    # 只保留活跃的股票
                    stock_list = stock_list[stock_list['is_active'] == 1]
                    
                    # 选择所需的列
                    return stock_list[['ts_code', 'symbol', 'name']]
            
            return self._get_default_stock_list()
        except Exception as e:
            st.error(f"加载股票列表失败: {str(e)}")
            return self._get_default_stock_list()
            
    def _get_default_stock_list(self):
        """返回默认的股票列表"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH'],
            'symbol': ['000001', '600000'],
            'name': ['平安银行', '浦发银行']
        })
            
    def fetch_daily_data(self, ts_code):
        """从API获取股票日线数据"""
        try:
            token = os.getenv('VITE_TUSHARE_TOKEN')
            url = 'http://api.tushare.pro'
            params = {
                'api_name': 'daily',
                'token': token,
                'params': {
                    'ts_code': ts_code,
                    'freq': 'D',
                    'asset': 'E'
                }
            }
            response = requests.post(url, json=params)
            result = response.json()
            
            if result['code'] == 0 and result['data']['items']:
                # 保存数据
                filename = self.data_dir / f"{ts_code.split('.')[0]}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    # 写入表头
                    fields = result['data']['fields']
                    f.write('\t'.join(fields) + '\n')
                    
                    # 写入数据
                    for item in result['data']['items']:
                        f.write('\t'.join(str(x) for x in item) + '\n')
                
                return True
            return False
        except Exception as e:
            st.error(f"获取股票日线数据失败: {str(e)}")
            return False
            
    def load_daily_data(self, stock_code):
        """加载单个股票的日线数据"""
        try:
            file_path = self.data_dir / f"{stock_code}.txt"
            
            # 如果文件不存在，尝试获取数据
            if not file_path.exists():
                ts_code = f"{stock_code}.SH" if stock_code.startswith('6') else f"{stock_code}.SZ"
                if not self.fetch_daily_data(ts_code):
                    return self._generate_sample_data(stock_code)
            
            # 从本地文件加载
            df = pd.read_csv(file_path, sep='\t')
            if not df.empty:
                # 确保所需的列都存在
                required_columns = ['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
                if not all(col in df.columns for col in required_columns):
                    return self._generate_sample_data(stock_code)
                
                # 重命名 volume 列
                if 'volume' in df.columns:
                    df = df.rename(columns={'volume': 'vol'})
                
                # 转换日期格式
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                
                # 确保数值列为浮点数
                numeric_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 按日期排序
                df = df.sort_values('trade_date')
                
                return df
            
            return self._generate_sample_data(stock_code)
                
        except Exception as e:
            st.error(f"加载股票数据失败: {str(e)}")
            return self._generate_sample_data(stock_code)
            
    def get_realtime_quote(self, stock_code):
        """获取最新行情数据"""
        try:
            # 从本地文件获取最新数据
            file_path = self.data_dir / f"{stock_code}.txt"
            if file_path.exists():
                df = pd.read_csv(file_path, sep='\t')
                if not df.empty:
                    latest_data = df.iloc[-1]
                    return pd.DataFrame([{
                        'code': stock_code,
                        'name': '本地数据',
                        'price': latest_data['close'],
                        'open': latest_data['open'],
                        'high': latest_data['high'],
                        'low': latest_data['low'],
                        'vol': latest_data['vol'],
                        'amount': latest_data['amount'],
                        'time': latest_data['trade_date']
                    }])
            return self._generate_sample_quote(stock_code)
        except Exception as e:
            st.error(f"获取实时行情失败: {str(e)}")
            return self._generate_sample_quote(stock_code)
            
    def _generate_sample_data(self, stock_code):
        """生成示例数据"""
        dates = pd.date_range(end=datetime.now(), periods=250, freq='B')
        price = 100
        data = []
        for date in dates:
            price = price * (1 + np.random.normal(0, 0.02))
            data.append({
                'trade_date': date,
                'open': price * (1 + np.random.normal(0, 0.005)),
                'high': price * (1 + np.random.normal(0, 0.01)),
                'low': price * (1 + np.random.normal(0, 0.01)),
                'close': price,
                'vol': np.random.randint(1000000, 10000000),
                'amount': np.random.randint(10000000, 100000000)
            })
        df = pd.DataFrame(data)
        # 确保日期格式正确
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df
        
    def _generate_sample_quote(self, stock_code):
        """生成示例实时行情"""
        price = 100 * (1 + np.random.normal(0, 0.02))
        return pd.DataFrame([{
            'code': stock_code,
            'name': '示例股票',
            'price': f"{price:.2f}",
            'open': f"{price * 0.98:.2f}",
            'high': f"{price * 1.02:.2f}",
            'low': f"{price * 0.97:.2f}",
            'vol': np.random.randint(1000000, 10000000),
            'amount': np.random.randint(10000000, 100000000),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        try:
            # 计算MA
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            
            # 计算MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['Histogram'] = df['MACD'] - df['Signal']
            
            # 计算RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            return df
        except Exception as e:
            st.error(f"计算技术指标失败: {str(e)}")
            return df 