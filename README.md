# 자동 시장 브리핑 시스템

한국투자증권 Open API를 활용한 실시간 시장 데이터 수집 및 Threads 자동 게시 시스템입니다.

## 🎯 주요 기능

- **실시간 데이터 수집**: 한국투자증권 Open API로 국내외 시장 데이터 자동 수집
- **시간대별 자동화**: 5개 시간대(07:00, 08:00, 12:00, 15:40, 19:00)에 맞는 브리핑 자동 생성
- **Threads 자동 게시**: 생성된 브리핑을 Threads에 자동 포스팅
- **GitHub Actions 스케줄링**: 평일 자동 실행 및 모니터링

## 📅 시간대별 브리핑 유형

| 시간대 | 브리핑 유형 | 주요 내용 |
|--------|-------------|-----------|
| **07:00** | 미국 마켓 마감 브리핑 | 🌅 S&P500, 나스닥, 다우 지수 + 주요 종목 |
| **08:00** | 한국시장 프리뷰 | 🌞 전일 미국장 영향 + 오늘 전망 |
| **12:00** | 한국시장 중간 브리핑 | ☀️ 오전장 결과 + 오후장 관전포인트 |
| **15:40** | 한국시장 마감 브리핑 | 🌆 마감 지수 + 내일장 전망 |
| **19:00** | 미국 마켓 프리뷰 | 🌙 선물 지수 + 오늘밤 체크포인트 |

## 🚀 설치 및 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd dkwjawj_renew
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

#### 로컬 개발용 (.env 파일)
```bash
# 한국투자증권 Open API
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCOUNT_NO=your_account_number

# Threads API (향후 공개 시)
THREADS_API_KEY=your_threads_api_key
THREADS_ACCESS_TOKEN=your_threads_access_token
THREADS_USER_ID=your_threads_user_id

# 알림 서비스 (선택사항)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

#### GitHub Secrets (자동화용)
GitHub 저장소 Settings → Secrets and variables → Actions에서 다음 키들을 등록:

| Secret Name | 설명 |
|-------------|------|
| `KIS_APP_KEY` | 한국투자증권 Open API 앱 키 |
| `KIS_APP_SECRET` | 한국투자증권 Open API 앱 시크릿 |
| `KIS_ACCOUNT_NO` | 한국투자증권 계좌번호 |
| `THREADS_API_KEY` | Threads API 키 |
| `THREADS_ACCESS_TOKEN` | Threads 액세스 토큰 |
| `THREADS_USER_ID` | Threads 사용자 ID |
| `SLACK_WEBHOOK_URL` | Slack 웹훅 URL (알림용) |

## 🛠️ 사용법

### 1. 로컬 실행

#### 단일 시간대 브리핑
```bash
# 07:00 브리핑 실행
python auto_briefing_system.py --time 07:00

# 결과 저장
python auto_briefing_system.py --time 08:00 --save
```

#### 모든 시간대 브리핑
```bash
python auto_briefing_system.py --time all --save
```

#### 시스템 상태 확인
```bash
python auto_briefing_system.py --status
```

### 2. 개별 모듈 테스트

#### API 클라이언트 테스트
```bash
python kis_api_client.py
```

#### 브리핑 생성기 테스트
```bash
python market_briefing_generator.py
```

#### Threads 게시 테스트
```bash
python threads_api_client.py
```

### 3. GitHub Actions 자동화

#### 자동 스케줄링
- 평일 07:00, 08:00, 12:00, 15:40, 19:00 자동 실행
- GitHub Actions에서 설정된 스케줄에 따라 자동 브리핑 생성 및 게시

#### 수동 실행
GitHub 저장소 Actions 탭에서 "Market Briefing Automation" 워크플로우를 선택하고 수동 실행 가능

## 📊 데이터 수집 항목

### 국내 시장
- **지수**: 코스피, 코스닥
- **주요 종목**: 삼성전자, SK하이닉스, NAVER, LG화학, 삼성SDI
- **섹터**: 반도체, AI, 바이오, 금융, 자동차

### 해외 시장
- **지수**: S&P500, NASDAQ, DOW
- **주요 종목**: 테슬라, 엔비디아, 애플, 마이크로소프트
- **글로벌 이슈**: FOMC, 실적발표, 경제지표

## 📝 출력 예시

### 07:00 미국 마켓 마감 브리핑
```
🌅 미국 증시 마감 요약
• S&P500 5,500.12pt (+0.8%)
• 나스닥 17,900.45pt (+1.1%)
• 다우 38,500pt (+0.3%)
• 테슬라 +4.2%
• 엔비디아 +3.0%
• 애플 +1.8%

💡 오늘의 관전포인트
- FOMC 결과 발표 후 변동성 확대
- 반도체, AI 섹터 랠리 지속
- 주요 기업 실적 발표 대기

#미국증시 #S&P500 #나스닥 #글로벌마켓
```

### 08:00 한국시장 프리뷰
```
🌞 오늘의 한국시장 전망
• 전일 코스피 2,500.12pt (+0.5%)
• 전일 코스닥 800.45pt (+1.2%)
• 미국장 영향: S&P500 +0.8%
• 주요 이슈: 반도체 수급 개선

📋 개장 전 체크리스트
- 글로벌 증시 동향 체크
- 주요 경제지표 발표 일정
- 섹터별 투자 포인트

#한국증시 #코스피 #코스닥 #오늘의시장
```

## 📁 프로젝트 구조

```
dkwjawj_renew/
├── .github/
│   └── workflows/
│       └── market_briefing.yml      # GitHub Actions 워크플로우
├── kis_api_client.py               # 한국투자증권 API 클라이언트
├── market_briefing_generator.py    # 브리핑 생성기
├── threads_api_client.py           # Threads API 클라이언트
├── auto_briefing_system.py         # 메인 자동화 시스템
├── requirements.txt                # 의존성 목록
├── README.md                       # 프로젝트 문서
└── .env                           # 환경변수 (로컬용)
```

## 🔧 설정 가이드

### 한국투자증권 Open API 설정
1. [한국투자증권 Open API](https://securities.koreainvestment.com/main/index.jsp) 접속
2. 개발자센터에서 앱 등록
3. API 키 및 시크릿 발급
4. 계좌번호 확인

### Threads API 설정 (향후)
- Threads API가 공개되면 해당 문서 참조
- 현재는 시뮬레이션 모드로 동작

## 📈 모니터링 및 로그

### 로그 파일
- `briefing_system.log`: 시스템 실행 로그
- `briefing_*.json`: 생성된 브리핑 데이터

### GitHub Actions 아티팩트
- 실행 결과 및 로그 파일 자동 저장
- 7일간 보관

### 알림 설정
- Slack 웹훅을 통한 실패 알림
- 매일 오전 6시 시스템 상태 점검

## 🚨 문제 해결

### API 키 오류
```bash
# 환경변수 확인
python auto_briefing_system.py --status
```

### 네트워크 오류
- 한국투자증권 API 서버 상태 확인
- 방화벽 설정 확인

### Threads 게시 실패
- API 키 및 토큰 유효성 확인
- 계정 권한 확인

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## ⚠️ 주의사항

- 한국투자증권 API 호출 제한을 준수하세요
- 실제 거래에 사용하지 마세요 (정보 제공 목적)
- API 키는 절대 공개하지 마세요

## 📞 문의

프로젝트에 대한 문의사항이나 개선 제안이 있으시면 이슈를 생성해 주세요. 