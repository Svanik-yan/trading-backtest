import pandas as pd
import numpy as np
from pathlib import Path
import tushare as ts
from datetime import datetime, timedelta
import streamlit as st
import time

class DataLoader:
    def __init__(self, data_dir="public/daily_stock_data"):
        """初始化数据加载器"""
        self.data_dir = Path(data_dir)
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_stock_list(self):
        """加载股票列表"""
        try:
            # 从本地文件加载
            stock_list_path = Path("stock_list.txt")
            if stock_list_path.exists():
                df = pd.read_csv(stock_list_path)
                if not df.empty:
                    return df
            
            # 如果本地文件不存在或为空，返回示例数据
            return pd.DataFrame({
                'ts_code': ['000001.SZ', '600000.SH'],
                'symbol': ['000001', '600000'],
                'name': ['平安银行', '浦发银行'],
                'list_date': ['1991-04-03', '1999-11-10']
            })
        except Exception as e:
            st.error(f"加载股票列表失败: {str(e)}")
            # 返回示例数据
            return pd.DataFrame({
                'ts_code': ['000001.SZ', '600000.SH'],
                'symbol': ['000001', '600000'],
                'name': ['平安银行', '浦发银行'],
                'list_date': ['1991-04-03', '1999-11-10']
            })
            
    def load_daily_data(self, stock_code):
        """加载单个股票的日线数据"""
        try:
            file_path = self.data_dir / f"{stock_code}.txt"
            
            # 从本地文件加载
            if file_path.exists():
                df = pd.read_csv(file_path)
                if not df.empty:
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df = df.sort_values('trade_date')
                    return df
            
            # 如果本地文件不存在或为空，返回示例数据
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
                df = pd.read_csv(file_path)
                if not df.empty:
                    latest_data = df.iloc[-1]
                    return pd.DataFrame([{
                        'code': stock_code,
                        'name': '本地数据',
                        'price': latest_data['close'],
                        'open': latest_data['open'],
                        'high': latest_data['high'],
                        'low': latest_data['low'],
                        'volume': latest_data['vol'],
                        'amount': latest_data['amount'],
                        'time': latest_data['trade_date']
                    }])
            return self._generate_sample_quote(stock_code)
        except:
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
        return pd.DataFrame(data)
        
    def _generate_sample_quote(self, stock_code):
        """生成示例实时行情"""
        price = 100 * (1 + np.random.normal(0, 0.02))
        return pd.DataFrame([{
            'code': stock_code,
            'name': '示例股票',
            'price': f"{price:.2f}",
            'bid': f"{price * 0.99:.2f}",
            'ask': f"{price * 1.01:.2f}",
            'volume': f"{np.random.randint(1000000, 10000000)}",
            'amount': f"{np.random.randint(10000000, 100000000)}",
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