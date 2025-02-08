import requests
import json

# API配置
API_TOKEN = '750ad66d1a5440e5884dcfb6379ab147'
BASE_URL = 'https://tsanghi.com/api/fin/stock'

def get_stock_list(exchange):
    url = f"{BASE_URL}/{exchange}/list?token={API_TOKEN}"
    response = requests.get(url)
    return response.json()['data'] if response.json()['code'] == 200 else []

try:
    # 获取上海和深圳的股票列表
    sh_stocks = get_stock_list('XSHG')  # 上海证券交易所
    sz_stocks = get_stock_list('XSHE')  # 深圳证券交易所
    
    # 合并股票列表
    all_stocks = sh_stocks + sz_stocks
    
    # 保存到文件
    with open('stock_list.txt', 'w', encoding='utf-8') as f:
        json.dump({
            'msg': '操作成功',
            'code': 200,
            'data': all_stocks
        }, f, ensure_ascii=False, indent=2)
    
    print('股票清单已成功保存到 stock_list.txt')
    print(f'共获取到 {len(all_stocks)} 只股票信息')
    print(f'其中上海证券交易所: {len(sh_stocks)} 只')
    print(f'深圳证券交易所: {len(sz_stocks)} 只')

except requests.exceptions.RequestException as e:
    print(f'请求失败: {e}')
except json.JSONDecodeError as e:
    print(f'JSON解析失败: {e}')
except Exception as e:
    print(f'发生错误: {e}') 