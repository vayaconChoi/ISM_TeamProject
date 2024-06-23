import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import json

def get_naver_api():
    today = datetime.today() - timedelta(days=1)
    date_90_days_earlier = today - timedelta(days=90-1)
    today = today.strftime('%Y-%m-%d')
    date_90_days_earlier = date_90_days_earlier.strftime('%Y-%m-%d')

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    url = "https://openapi.naver.com/v1/datalab/shopping/categories"
    body = f"{{\"startDate\":\"{date_90_days_earlier}\",\"endDate\":\"{today}\",\"timeUnit\":\"date\",\"category\":[{{\"name\":\"사과 검색량\",\"param\":[\"50002160\"]}},{{\"name\":\"배 검색량\",\"param\":[\"50002161\"]}}]}}"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    response_body = response.read()
    # print(response_body.decode('utf-8'))

    response_body = json.loads(response_body)

    df_list = []
    for item in response_body["results"]:
        title = item["title"]
        for data_point in item["data"]:
            data_point["title"] = title
            df_list.append(data_point)

    df = pd.DataFrame(df_list)

    # 날짜를 datetime 형식으로 변환
    df["period"] = pd.to_datetime(df["period"])

    # 5일 이동 평균 계산
    df["moving_average"] = df.groupby("title")["ratio"].rolling(window=5, min_periods=1).mean().reset_index(level=0, drop=True)

    df_pivot = df.pivot(index='period', columns='title', values='moving_average')

    # 날짜를 index로 설정
    df_pivot.index = pd.to_datetime(df_pivot.index)

    # 인덱스를 열로 변환하고 다시 날짜로 설정
    df_final = df_pivot.reset_index().rename(columns={'period': '날짜'})
    df_final.drop('날짜', axis=1, inplace=True)

    return df_final
# print(get_naver_api())