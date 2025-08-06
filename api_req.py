import requests
import json

# 실전 환경용 설정
APP_KEY = "PSVZnVe8e49FcFvlG8AcDdGeVpFDZ2jrqlcT".strip()
APP_SECRET = "QMx20CB3ibv6Cp+v6AtXJICu3ZWOCGztQ/uo4sLxAFTsew/R+0+pMX6lloSa0QYo7TFvBX/u6O2fMkvgi2KFqjsFXosJqbNQ8zjlMDruG3mSpoQpellZGmIgFIy1aV9+NmAG4S+e7V5R+x2Wls3eG3xHjzs41mHSyqJx8l5aU+s1sj2ThWE=".strip()

# 이전에 성공한 토큰 사용
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjYwNzJlODM5LWNiNDUtNDgyYS04ODJiLTk3NTg4MDQzM2M2MyIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc1NDU3NjcwMSwiaWF0IjoxNzU0NDkwMzAxLCJqdGkiOiJQU1ZablZlOGU0OUZjRnZsRzhBY0RkR2VWcEZEWjJqcnFsY1QifQ.FSOkn-r375D6PQj0BLN4030k9TIvuhpxBcWlDDAVrTxJP6t_l6ymNCnCl6MaqAgq7mRAVhSrkahO4MxubW_NQA"

print("=== 한국투자증권 API 실제 호출 테스트 ===")
print(f"APP_KEY: {APP_KEY}")
print(f"ACCESS_TOKEN: {ACCESS_TOKEN[:50]}...")

# 실제 API 호출 테스트
print("\n=== 코스피 지수 조회 테스트 ===")

# 코스피 지수 조회
kospi_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
kospi_headers = {
    "Content-Type": "application/json",
    "authorization": f"Bearer {ACCESS_TOKEN}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST01010100"  # 주식 현재가 시세
}

kospi_params = {
    "FID_COND_MRKT_DIV_CODE": "J",  # 코스피
    "FID_INPUT_ISCD": "0001"  # 코스피 지수
}

print(f"코스피 조회 URL: {kospi_url}")
print(f"요청 헤더: {kospi_headers}")
print(f"요청 파라미터: {kospi_params}")

kospi_response = requests.get(kospi_url, headers=kospi_headers, params=kospi_params)

print(f"\n코스피 조회 Status Code: {kospi_response.status_code}")

if kospi_response.status_code == 200:
    kospi_result = kospi_response.json()
    print("✅ 코스피 지수 조회 성공!")
    print(f"응답 내용: {json.dumps(kospi_result, indent=2, ensure_ascii=False)}")
    
    if 'output' in kospi_result:
        output = kospi_result['output']
        print(f"\n📊 코스피 지수 정보:")
        print(f"현재가: {output.get('stck_prpr', 'N/A')}")
        print(f"전일대비: {output.get('prdy_vrss', 'N/A')}")
        print(f"등락률: {output.get('prdy_ctrt', 'N/A')}%")
else:
    print(f"❌ 코스피 지수 조회 실패: {kospi_response.text}")

print("\n=== 코스닥 지수 조회 테스트 ===")

# 코스닥 지수 조회
kosdaq_params = {
    "FID_COND_MRKT_DIV_CODE": "J",  # 코스닥
    "FID_INPUT_ISCD": "1001"  # 코스닥 지수
}

kosdaq_response = requests.get(kospi_url, headers=kospi_headers, params=kosdaq_params)

print(f"코스닥 조회 Status Code: {kosdaq_response.status_code}")

if kosdaq_response.status_code == 200:
    kosdaq_result = kosdaq_response.json()
    print("✅ 코스닥 지수 조회 성공!")
    
    if 'output' in kosdaq_result:
        output = kosdaq_result['output']
        print(f"\n📊 코스닥 지수 정보:")
        print(f"현재가: {output.get('stck_prpr', 'N/A')}")
        print(f"전일대비: {output.get('prdy_vrss', 'N/A')}")
        print(f"등락률: {output.get('prdy_ctrt', 'N/A')}%")
else:
    print(f"❌ 코스닥 지수 조회 실패: {kosdaq_response.text}")
