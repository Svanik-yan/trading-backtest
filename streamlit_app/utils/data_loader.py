import pandas as pd
import numpy as np
from pathlib import Path
import tushare as ts
from datetime import datetime, timedelta
import streamlit as st

class DataLoader:
    def __init__(self, data_dir="public/daily_stock_data"):
        self.data_dir = Path(data_dir)
        self.ts_token = st.secrets["tushare"]["token"]
        ts.set_token(self.ts_token)
        self.pro = ts.pro_api()
        
    def load_stock_list(self):
        """加载股票列表"""
        try:
            df = pd.read_csv('stock_list.txt')
            return df
        except:
            # 如果本地文件不存在，从API获取
            df = self.pro.stock_basic(exchange='', list_status='L')
            df.to_csv('stock_list.txt', index=False)
            return df
            
    def load_daily_data(self, stock_code):
        """加载单个股票的日线数据"""
        file_path = self.data_dir / f"{stock_code}.txt"
        if file_path.exists():
            df = pd.read_csv(file_path)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        return None
        
    def get_realtime_quote(self, stock_code):
        """获取实时行情数据"""
        try:
            df = ts.get_realtime_quotes(stock_code)
            return df
        except:
            return None
            
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
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