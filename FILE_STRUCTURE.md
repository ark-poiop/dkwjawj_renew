# 📁 프로젝트 파일 구조

## 🗂 전체 구조
```
dkwjawj_renew/
├── 📄 README.md                    # 프로젝트 개요
├── 📄 SYSTEM_OVERVIEW.md           # 시스템 전체 개요
├── 📄 FILE_STRUCTURE.md            # 이 파일 (파일 구조)
├── 📄 requirements.txt             # Python 의존성
│
├── 🔧 핵심 시스템
│   ├── 📄 auto_briefing_system.py      # 메인 시스템 (브리핑 생성 + 포스팅)
│   ├── 📄 market_briefing_generator.py # 브리핑 템플릿 및 생성
│   └── 📄 market_data_strategy.py      # 데이터 수집 전략 관리
│
├── 📊 데이터 수집
│   ├── 📄 market_crawler_strategy.py   # 통합 데이터 수집 전략
│   ├── 📄 real_time_market_data.py     # 실시간 데이터 수집기
│   ├── 📄 yfinance_client.py           # Yahoo Finance API 클라이언트
│   ├── 📄 kis_api_client.py            # 한국투자증권 API 클라이언트
│   ├── 📄 kis_auth.py                  # KIS API 인증 관리
│   └── 📄 domestic_stock_functions.py  # 국내 주식 함수들
│
├── 💾 데이터 저장
│   └── 📄 market_data_storage.py       # 시장 데이터 저장/로드
│
├── 📱 소셜 미디어
│   └── 📄 threads_api_client.py        # Threads API 클라이언트
│
├── 🧪 테스트 파일들
│   ├── 📄 test_market_hours.py         # 시장 시간 테스트
│   ├── 📄 test_briefing_types.py       # 브리핑 타입 테스트
│   ├── 📄 test_deployment.py           # 배포 테스트
│   └── 📄 test_threads_api.py          # Threads API 테스트
│
├── 🔄 크롤링 (백업용)
│   ├── 📄 naver_finance_crawler.py     # 네이버 증권 크롤러 (국내)
│   ├── 📄 naver_world_crawler.py       # 네이버 해외 크롤러
│   ├── 📄 naver_individual_crawler.py  # 네이버 개별 지수 크롤러
│   └── 📄 yahoo_finance_crawler.py     # Yahoo Finance 크롤러 (백업 데이터)
│
├── ⚙️ 설정 및 유틸리티
│   ├── 📄 api_req.py                   # API 요청 테스트
│   ├── 📄 local_test.py                # 로컬 테스트
│   └── 📄 kis_devlp.yaml.backup        # KIS API 설정 백업
│
└── 🚀 GitHub Actions
    └── 📁 .github/workflows/
        ├── 📄 market_briefing.yml          # 메인 브리핑 스케줄링
        ├── 📄 market_data_collection.yml  # 데이터 수집 스케줄링
        └── 📄 threads_api_test.yml        # Threads API 테스트
```

---

## 📋 파일별 상세 설명

### 🔧 **핵심 시스템**

#### `auto_briefing_system.py`
- **역할**: 전체 시스템의 메인 진입점
- **주요 기능**:
  - 동적 브리핑 타입 선택 (`get_current_briefing_type()`)
  - 시장 데이터 수집 및 브리핑 생성
  - Threads 포스팅 실행
- **사용법**: `python auto_briefing_system.py --time_slot now`

#### `market_briefing_generator.py`
- **역할**: 브리핑 콘텐츠 생성
- **주요 기능**:
  - 시간대별 브리핑 템플릿
  - 시장 데이터 기반 콘텐츠 생성
  - 한국어 자연어 생성

#### `market_data_strategy.py`
- **역할**: 데이터 수집 전략 관리
- **주요 기능**:
  - 실시간 데이터 우선 수집
  - 백업 데이터 폴백
  - 데이터 유효성 검증

### 📊 **데이터 수집**

#### `market_crawler_strategy.py`
- **역할**: 통합 데이터 수집 전략
- **주요 기능**:
  - 실시간 데이터 우선 수집
  - 국내/해외 데이터 통합
  - 백업 데이터 생성

#### `real_time_market_data.py`
- **역할**: 실시간 데이터 수집기
- **주요 기능**:
  - yfinance를 통한 해외 데이터
  - KIS API를 통한 국내 데이터
  - 실시간 데이터 검증

#### `yfinance_client.py` ⭐ **NEW**
- **역할**: Yahoo Finance API 클라이언트
- **주요 기능**:
  - S&P500, NASDAQ, DOW 실시간 데이터
  - 가격 범위 검증
  - 과거 데이터 수집

#### `kis_api_client.py`
- **역할**: 한국투자증권 API 클라이언트
- **주요 기능**:
  - KOSPI, KOSDAQ 실시간 데이터
  - API 인증 관리
  - 에러 처리

#### `kis_auth.py`
- **역할**: KIS API 인증 관리
- **주요 기능**:
  - 토큰 발급 및 갱신
  - 환경변수 관리
  - 인증 상태 확인

### 💾 **데이터 저장**

#### `market_data_storage.py`
- **역할**: 시장 데이터 저장/로드
- **주요 기능**:
  - JSON 파일 기반 저장
  - 날짜별 데이터 관리
  - 오래된 데이터 정리

### 📱 **소셜 미디어**

#### `threads_api_client.py`
- **역할**: Threads API 클라이언트
- **주요 기능**:
  - 브리핑 포스팅
  - 미디어 컨테이너 생성
  - 응답 검증

### 🧪 **테스트 파일들**

#### `test_*.py` 파일들
- **역할**: 각 컴포넌트별 테스트
- **주요 기능**:
  - 시장 시간 로직 테스트
  - 브리핑 타입 선택 테스트
  - API 연결 테스트

### 🔄 **크롤링 (백업용)**

#### `naver_*.py` 파일들
- **역할**: 네이버 증권 크롤링 (백업용)
- **상태**: 현재는 백업 데이터로 대체됨

#### `yahoo_finance_crawler.py`
- **역할**: Yahoo Finance 크롤링 (백업용)
- **상태**: 현실적인 백업 데이터 생성으로 변경됨

### ⚙️ **설정 및 유틸리티**

#### `api_req.py`
- **역할**: API 요청 테스트
- **사용법**: 개별 API 테스트용

#### `local_test.py`
- **역할**: 로컬 테스트
- **사용법**: 로컬 환경에서 전체 시스템 테스트

### 🚀 **GitHub Actions**

#### `.github/workflows/market_briefing.yml`
- **역할**: 메인 브리핑 스케줄링
- **스케줄**: 09:00, 12:00, 15:30, 21:00 KST
- **수동 실행**: `now` 옵션 지원

#### `.github/workflows/market_data_collection.yml`
- **역할**: 데이터 수집 스케줄링
- **스케줄**: 15:25 KST (한국장), 04:55 KST (미국장)
- **수동 실행**: `data_type` 옵션 지원

---

## 🔄 데이터 흐름

```
1. 스케줄링 (GitHub Actions)
   ↓
2. 데이터 수집 (market_crawler_strategy.py)
   ├── 실시간 데이터 (real_time_market_data.py)
   │   ├── 해외: yfinance_client.py
   │   └── 국내: kis_api_client.py
   └── 백업 데이터 (현실적 시뮬레이션)
   ↓
3. 브리핑 생성 (market_briefing_generator.py)
   ↓
4. Threads 포스팅 (threads_api_client.py)
   ↓
5. 결과 로깅 및 저장
```

---

## 🎯 주요 업데이트 히스토리

### **2025년 8월 - 실시간 데이터 확보** ⭐
- ✅ `yfinance_client.py` 추가
- ✅ `real_time_market_data.py` 업데이트
- ✅ 실시간 해외 데이터 수집 구현
- ✅ 백업 데이터 전략 개선

### **이전 업데이트들**
- ✅ GitHub Actions 스케줄링 수정 (UTC → KST)
- ✅ 동적 브리핑 타입 선택 구현
- ✅ Threads API 연동 완료
- ✅ KIS API 인증 강화

---

## 🛠 개발 가이드

### **새로운 데이터 소스 추가**
1. `real_time_market_data.py`에 새로운 메서드 추가
2. `market_crawler_strategy.py`에서 호출
3. 테스트 파일 생성 및 검증

### **브리핑 템플릿 수정**
1. `market_briefing_generator.py` 수정
2. 시간대별 템플릿 업데이트
3. 로컬 테스트 실행

### **스케줄링 변경**
1. `.github/workflows/` 파일 수정
2. cron 표현식 업데이트
3. GitHub Actions에서 테스트

---

*마지막 업데이트: 2025년 8월*
