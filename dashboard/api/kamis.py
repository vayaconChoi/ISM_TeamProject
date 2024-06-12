import requests
import os
from datetime import datetime, timedelta
from re import sub

from dotenv import load_dotenv

def data_for_graph():
    today = datetime.today()
    ten_day_ago = today - timedelta(10)
    today = today.strftime('%Y-%m-%d')
    ten_day_ago = ten_day_ago.strftime('%Y-%m-%d')




    # API KEY 불러오기
    key = os.getenv('KAMIS_KEY')
    print(key)
    id = "4465"
    product = {
        "사과상품":['400', '411',"04"],
        "사과중품":['400', '411',"05"],
        "배상품":['400', '412',"04"],
        "배중품":['400', '412',"05"]
    }
    url = f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_startday={ten_day_ago}&p_endday={today}&p_itemcategorycode={product['사과상품'][0]}&p_itemcode={product['사과상품'][1]}&p_productrankcode={product['사과상품'][2]}&p_cert_key={key}&p_cert_id={id}&p_returntype=json"

    response = requests.get(url)
    data = response.json()["data"]["item"][0:10]

    date = []
    price = []
    for i in data:
        if i['countyname'] == "평균":
            date.append(i['regday'])
            price.append(sub(r'[^\d.]','', i['price']))

    return date, price


