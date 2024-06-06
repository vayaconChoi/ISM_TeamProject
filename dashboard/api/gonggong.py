import requests
import os
from datetime import datetime

from re import sub


from dotenv import load_dotenv
from pathlib import Path

def get_live_auction():
    today = datetime.today()
    today = today.strftime('%Y%m%d')

    # API KEY 불러오기
    env_path = Path('.', '.env')
    load_dotenv(dotenv_path=env_path)
    key = os.getenv('LIVE_AUCTION')

    apple_url = f"https://at.agromarket.kr/openApi/price/real.do?serviceKey={key}&apiType=json&pageNo=1&whsalCd=110001&largeCd=06&midCd=01"
    response = requests.get(apple_url)
    data = response.json()['data']

    pear_url = f"https://at.agromarket.kr/openApi/price/real.do?serviceKey={key}&apiType=json&pageNo=1&whsalCd=110001&largeCd=06&midCd=02"
    response = requests.get(pear_url)
    for i in response.json()['data']:
        data.append(i)

    return data