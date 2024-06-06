# TEAM Fresh Fossil
## ISM_TEAMPROJECT

---
* 최범근
* 박기윤
* 박진우

---
# 2024-06-06 Update
##### 기윤
* 대쉬보드 - 소매 시세 가격 표시 그래프 구현 (KAMIS API 연동)
* Django Auth - 로그인 로그아웃 구현

### API KEY 관리방법 (GITHUB 통한 유출 예방)

1. 아래 방법으로 dotenv 다운
```python
$ pip install python-dotenv
```

2. .env 추가
    - 가장 상단 폴더에 추가 (manage.py 있는 폴더)

3. 키 이름 : "키" 형식으로 입력 후 저장
```.env
    KAMIS_KEY : "어쩌고 저쩌고"
```

+ .gitignore에 .env 추가되어 있는지 확인

### API KEY 사용하는 법
1. API 키 사용하고 싶은 파이썬 파일에 아래와 같이 작성
```python
from dotenv import load_dotenv

# 키 불러올 함수, 클래스 내에 아래와 같이 작성
load_dotenv()
key = os.getenv('KAMIS_KEY')
```
