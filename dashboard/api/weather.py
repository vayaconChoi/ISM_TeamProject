# import requests
# import pandas as pd
# from datetime import datetime, timedelta
#
#
# def weather_for_ML(day_before=90):
#     merged = pd.DataFrame()
#     # API 엔드포인트 URL
#     url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php"
#     end_date = datetime.today().date() - timedelta(days=1)
#     start_date = end_date - timedelta(days=day_before - 1)
#     # start_b = start_date
#
#     while end_date >= start_date:
#         start_dt = start_date.strftime('%Y%m%d')
#         end_dt = end_date.strftime('%Y%m%d')
#         # 요청 파라미터
#         params = {
#             "tm": start_dt,
#             "stn": "108",
#             "help": "0",
#             "authKey": "E-5_A1LwTlGufwNS8J5R3w"
#         }
#
#         # API 요청 보내기
#         response = requests.get(url, params=params)
#
#         # 응답 데이터를 Pandas DataFrame으로 변환
#         if response.status_code == 200:
#             lines = response.text.split('\n')
#
#             # Extract and process header line
#             header_line = lines[1].strip('#').strip()
#             headers = [header.strip() for header in header_line.split()]
#
#             # Extract data lines
#             data_lines = lines[2:-1]  # Exclude the last empty line
#             data = [line.split(',') for line in data_lines]
#             data = data[3:]
#             data = pd.DataFrame(data)
#             merged = pd.concat([merged, data], axis=0)
#         start_date += timedelta(days=1)
#     merged = merged.dropna()
#     merged = merged.iloc[:, [10, 2]]
#     merged.columns = ['평균기온', '평균풍속']
#     merged.reset_index(drop=True, inplace=True)
#     return merged
# # print(weather_for_ML(3))
import pandas as pd
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_weather_data(start_date, end_date, url, params):
    # 요청 파라미터 수정
    params["tm"] = start_date.strftime('%Y%m%d')
    response = requests.get(url, params=params)

    if response.status_code == 200:
        lines = response.text.split('\n')
        header_line = lines[1].strip('#').strip()
        headers = [header.strip() for header in header_line.split()]
        data_lines = lines[2:-1]  # Exclude the last empty line
        data = [line.split(',') for line in data_lines]
        data = data[3:]  # Skip headers
        data_df = pd.DataFrame(data)
        return data_df
    return pd.DataFrame()

def weather_for_ML(day_before=90):
    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php"
    end_date = datetime.today().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=day_before - 1)

    params = {
        "stn": "108",
        "help": "0",
        "authKey": "E-5_A1LwTlGufwNS8J5R3w"
    }

    date_range = pd.date_range(start_date, end_date)
    merged = pd.DataFrame()

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_date = {executor.submit(fetch_weather_data, date, end_date, url, params): date for date in date_range}
        for future in as_completed(future_to_date):
            date = future_to_date[future]
            try:
                data_df = future.result()
                if not data_df.empty:
                    merged = pd.concat([merged, data_df], axis=0)
            except Exception as e:
                print(f"Error fetching data for {date}: {e}")

    merged = merged.dropna()
    merged = merged.iloc[:, [10, 2]]
    merged.columns = ['평균기온', '평균풍속']
    merged.reset_index(drop=True, inplace=True)
    return merged
