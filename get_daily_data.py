import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保数据保存目录存在
DATA_DIR = 'public/daily_stock_data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_daily_data(ts_code):
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
    return response.json()

def save_stock_data(ts_code):
    result = get_daily_data(ts_code)
    filename = os.path.join(DATA_DIR, f"{ts_code.split('.')[0]}.txt")
    
    # 保存为制表符分隔的格式
    with open(filename, 'w', encoding='utf-8') as f:
        # 写入表头
        if result['code'] == 0 and result['data']['items']:
            fields = result['data']['fields']
            f.write('\t'.join(fields) + '\n')
            
            # 写入数据
            for item in result['data']['items']:
                f.write('\t'.join(str(x) for x in item) + '\n')
                
    print(f'数据已保存到 {filename}')

if __name__ == '__main__':
    # 需要下载的股票列表
    stock_list = ['000421.SZ', '601727.SH', '300563.SZ']
    
    for stock_code in stock_list:
        save_stock_data(stock_code)
        print(f'{stock_code} 数据下载完成') 