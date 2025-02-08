import tushare as ts
import pandas as pd
import os
from datetime import datetime
import time
import requests
import json

# 设置token
ts.set_token('7a704330a5be992e1a89736e558f1fe72b5329f3696824e994037be0')
pro = ts.pro_api()

# API配置
API_TOKEN = "750ad66d1a5440e5884dcfb6379ab147"
BASE_URL = "https://tsanghi.com/api/fin/stock"

def download_exchange_list():
    """下载交易所股票清单"""
    try:
        # 确保目录存在
        os.makedirs('public', exist_ok=True)
        
        # 构建API URL
        url = f"{BASE_URL}/list?token={API_TOKEN}"
        
        # 发送请求
        response = requests.get(url)
        
        if response.status_code == 200:
            # 保存数据
            file_path = 'public/exchange_list.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            print("Successfully downloaded exchange list")
            return True
        else:
            print(f"Failed to download exchange list: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading exchange list: {str(e)}")
        return False

def download_stock_basic(retries=3, delay=5):
    """下载股票基础信息"""
    file_path = 'public/metadata/stock_basic.csv'
    
    for attempt in range(retries):
        try:
            # 使用stock_company接口，这个接口通常限制较少
            df = pro.stock_company(exchange='SZSE', fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope')
            
            # 获取上交所数据
            df2 = pro.stock_company(exchange='SSE', fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope')
            
            # 合并数据
            df = pd.concat([df, df2], ignore_index=True)
            
            if df is not None and not df.empty:
                # 确保目录存在
                os.makedirs('public/metadata', exist_ok=True)
                
                # 添加symbol列
                df['symbol'] = df['ts_code'].apply(lambda x: x.split('.')[0])
                
                # 保存数据
                df.to_csv(file_path, index=False)
                print(f"Successfully downloaded stock company info, total {len(df)} stocks")
                return True
            else:
                print("No data received from API")
                
            if attempt < retries - 1:  # 如果不是最后一次尝试
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
                
        except Exception as e:
            print(f"Error downloading stock company info (attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:  # 如果不是最后一次尝试
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
            if os.path.exists(file_path):
                print("Using existing stock company info file")
                return True
    return False

def main():
    print("Starting to download metadata...")
    
    # 下载交易所清单
    download_exchange_list()
    
    # 下载股票基础信息
    download_stock_basic()
    
    print("Metadata download completed")

if __name__ == "__main__":
    main() 