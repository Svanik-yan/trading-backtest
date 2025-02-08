import tushare as ts
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import random

# 设置token
ts.set_token('7a704330a5be992e1a89736e558f1fe72b5329f3696824e994037be0')
pro = ts.pro_api()

# 获取已下载的股票列表
def get_downloaded_stocks():
    downloaded = set()
    data_dir = 'public/daily_stock_data'
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.txt'):
                stock_code = file.split('.')[0]
                downloaded.add(stock_code)
    return downloaded

# 获取所有股票列表
def get_all_stocks():
    try:
        # 从API获取最新股票列表
        stocks = pro.stock_basic(exchange='', list_status='L')
        if not stocks.empty:
            # 保存到本地文件
            stocks.to_csv('stock_list.txt', index=False)
            print("Successfully downloaded stock list from API")
        else:
            print("Failed to get stock list from API")
            # 如果API获取失败，尝试从本地文件读取
            if os.path.exists('stock_list.txt'):
                stocks = pd.read_csv('stock_list.txt')
                print("Using cached stock list from local file")
        
        return stocks[['ts_code', 'symbol', 'name', 'list_date']]
    except Exception as e:
        print(f"Error getting stock list: {str(e)}")
        return pd.DataFrame()

# 下载单个股票的数据
def download_stock_data(ts_code, start_date, end_date, retry_count=3):
    for attempt in range(retry_count):
        try:
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if not df.empty:
                # 确保目录存在
                os.makedirs('public/daily_stock_data', exist_ok=True)
                # 保存数据
                file_path = f'public/daily_stock_data/{ts_code.split(".")[0]}.txt'
                df.to_csv(file_path, index=False)
                print(f"Successfully downloaded {ts_code}")
                return True
            return False
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {ts_code}: {str(e)}")
            if "每天最多访问该接口" in str(e):
                print("API daily limit reached. Waiting for reset...")
                time.sleep(60)  # 等待1分钟后重试
            else:
                time.sleep(random.uniform(1, 3))  # 随机等待1-3秒
    return False

def main():
    # 设置日期范围 - 使用2023年的数据
    end_date = datetime(2023, 12, 31)
    start_date = datetime(2023, 1, 1)
    
    # 格式化日期
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    
    # 获取已下载的股票
    downloaded_stocks = get_downloaded_stocks()
    print(f"Already downloaded {len(downloaded_stocks)} stocks")
    
    # 获取所有股票
    all_stocks = get_all_stocks()
    if all_stocks.empty:
        print("Failed to get stock list")
        return
    
    # 过滤掉已下载的股票
    stocks_to_download = all_stocks[~all_stocks['ts_code'].str.split('.').str[0].isin(downloaded_stocks)]
    print(f"Found {len(stocks_to_download)} stocks to download")
    
    # 随机选择1000个股票
    stocks_to_download = stocks_to_download.sample(n=min(1000, len(stocks_to_download)))
    
    # 下载数据
    success_count = 0
    for _, stock in stocks_to_download.iterrows():
        if download_stock_data(stock['ts_code'], start_date, end_date):
            success_count += 1
        time.sleep(random.uniform(0.5, 1.5))  # 随机等待0.5-1.5秒
        
        # 每下载50个股票打印一次进度
        if success_count % 50 == 0:
            print(f"Progress: {success_count}/{len(stocks_to_download)} stocks downloaded")
    
    print(f"Successfully downloaded {success_count} new stocks")

if __name__ == "__main__":
    main() 