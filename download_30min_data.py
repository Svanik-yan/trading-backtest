import requests
import json
import os

def download_30min_data():
    # API configuration
    API_TOKEN = "750ad66d1a5440e5884dcfb6379ab147"
    STOCK_CODE = "300377"
    
    # Construct the API URL
    url = f"https://tsanghi.com/api/fin/stock/XSHE/30min/realtime?token={API_TOKEN}&ticker={STOCK_CODE}"
    
    try:
        # Send request
        response = requests.get(url)
        
        if response.status_code == 200:
            # Get the JSON data
            data = response.json()
            
            # Save to file
            output_file = f'{STOCK_CODE}_30m.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully downloaded 30-minute data for {STOCK_CODE}")
            return True
        else:
            print(f"Failed to download data: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading data: {str(e)}")
        return False

if __name__ == "__main__":
    download_30min_data() 