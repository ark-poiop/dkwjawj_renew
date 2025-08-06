#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 Open API 클라이언트
실시간 시장 데이터 수집 및 정제
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KISAPIClient:
    """한국투자증권 Open API 클라이언트"""
    
    def __init__(self):
        # 환경변수에서 API 키 로드
        self.app_key = os.getenv('KIS_APP_KEY')
        self.app_secret = os.getenv('KIS_APP_SECRET')
        self.account_no = os.getenv('KIS_ACCOUNT_NO')
        
        # API 엔드포인트
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.auth_url = f"{self.base_url}/oauth2/tokenP"
        self.data_url = f"{self.base_url}/uapi/domestic-stock/v1/quotations"
        self.overseas_url = f"{self.base_url}/uapi/overseas-price/v1/quotations"
        
        # 인증 토큰
        self.access_token = None
        self.token_expires = None
        
        # API 호출 제한 관리
        self.last_call_time = 0
        self.call_interval = 0.1  # 100ms 간격
        
        if not all([self.app_key, self.app_secret, self.account_no]):
            logger.warning("KIS API 키가 설정되지 않았습니다. 샘플 데이터를 사용합니다.")
    
    def _rate_limit(self):
        """API 호출 제한 준수"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        if time_since_last_call < self.call_interval:
            time.sleep(self.call_interval - time_since_last_call)
        self.last_call_time = time.time()
    
    def _get_access_token(self) -> str:
        """액세스 토큰 발급"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        if not self.app_key or not self.app_secret:
            logger.warning("API 키가 없어 토큰 발급을 건너뜁니다.")
            return None
        
        try:
            headers = {
                "content-type": "application/json"
            }
            body = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            response = requests.post(self.auth_url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 86400)  # 24시간
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("액세스 토큰 발급 완료")
            return self.access_token
            
        except Exception as e:
            logger.error(f"토큰 발급 실패: {e}")
            return None
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """API 요청 실행"""
        self._rate_limit()
        
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self._get_access_token()}" if self._get_access_token() else "",
            "appkey": self.app_key or "",
            "appsecret": self.app_secret or "",
            "tr_id": "FHKST01010100"  # 기본 TR ID
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API 요청 실패: {e}")
            return None
    
    def get_domestic_index(self, index_code: str = "0001") -> Optional[Dict]:
        """국내 지수 조회 (코스피: 0001, 코스닥: 1001)"""
        if not self._get_access_token():
            return self._get_sample_domestic_index(index_code)
        
        url = f"{self.data_url}/inquire-price"
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": index_code
        }
        
        result = self._make_request(url, params)
        if result and result.get('rt_cd') == '0':
            return result.get('output', {})
        return None
    
    def get_overseas_index(self, index_code: str = "SPX") -> Optional[Dict]:
        """해외 지수 조회 (S&P500: SPX, NASDAQ: IXIC, DOW: DJI)"""
        if not self._get_access_token():
            return self._get_sample_overseas_index(index_code)
        
        url = f"{self.overseas_url}/price"
        params = {
            "AUTH": "",
            "EXCD": "NAS",  # NASDAQ
            "SYMB": index_code
        }
        
        result = self._make_request(url, params)
        if result and result.get('rt_cd') == '0':
            return result.get('output', {})
        return None
    
    def get_stock_price(self, stock_code: str) -> Optional[Dict]:
        """개별 종목 가격 조회"""
        if not self._get_access_token():
            return self._get_sample_stock_price(stock_code)
        
        url = f"{self.data_url}/inquire-price"
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        result = self._make_request(url, params)
        if result and result.get('rt_cd') == '0':
            return result.get('output', {})
        return None
    
    def get_market_data(self) -> Dict[str, Any]:
        """전체 시장 데이터 수집"""
        logger.info("시장 데이터 수집 시작")
        
        market_data = {
            "indices": {},
            "changes": {},
            "sectors": {},
            "stocks": {},
            "issues": [],
            "events": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 국내 지수
        kospi_data = self.get_domestic_index("0001")  # 코스피
        kosdaq_data = self.get_domestic_index("1001")  # 코스닥
        
        if kospi_data:
            market_data["indices"]["KOSPI"] = float(kospi_data.get('stck_prpr', 0))
            market_data["changes"]["KOSPI"] = float(kospi_data.get('prdy_vrss', 0))
        
        if kosdaq_data:
            market_data["indices"]["KOSDAQ"] = float(kosdaq_data.get('stck_prpr', 0))
            market_data["changes"]["KOSDAQ"] = float(kosdaq_data.get('prdy_vrss', 0))
        
        # 해외 지수
        sp500_data = self.get_overseas_index("SPX")  # S&P500
        nasdaq_data = self.get_overseas_index("IXIC")  # NASDAQ
        dow_data = self.get_overseas_index("DJI")  # DOW
        
        if sp500_data:
            market_data["indices"]["S&P500"] = float(sp500_data.get('last', 0))
            market_data["changes"]["S&P500"] = float(sp500_data.get('diff', 0))
        
        if nasdaq_data:
            market_data["indices"]["NASDAQ"] = float(nasdaq_data.get('last', 0))
            market_data["changes"]["NASDAQ"] = float(nasdaq_data.get('diff', 0))
        
        if dow_data:
            market_data["indices"]["DOW"] = float(dow_data.get('last', 0))
            market_data["changes"]["DOW"] = float(dow_data.get('diff', 0))
        
        # 주요 종목
        major_stocks = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035420": "NAVER",
            "051910": "LG화학",
            "006400": "삼성SDI"
        }
        
        for code, name in major_stocks.items():
            stock_data = self.get_stock_price(code)
            if stock_data:
                price = float(stock_data.get('stck_prpr', 0))
                change = float(stock_data.get('prdy_vrss', 0))
                if price > 0:
                    market_data["stocks"][name] = change
        
        # 섹터별 성과 (샘플 데이터)
        market_data["sectors"] = {
            "반도체": 2.1,
            "AI": 1.8,
            "바이오": -0.5,
            "금융": 0.3,
            "자동차": 1.2
        }
        
        # 주요 이슈 (샘플)
        market_data["issues"] = [
            "FOMC 결과 발표",
            "반도체 수급 개선",
            "AI 투자 확대",
            "글로벌 경기 우려"
        ]
        
        # 예정 이벤트 (샘플)
        market_data["events"] = [
            "주요 기업 실적 발표",
            "한국은행 금리 결정",
            "경제지표 발표"
        ]
        
        logger.info("시장 데이터 수집 완료")
        return market_data
    
    def _get_sample_domestic_index(self, index_code: str) -> Dict:
        """샘플 국내 지수 데이터"""
        sample_data = {
            "0001": {  # 코스피
                "stck_prpr": "2500.12",
                "prdy_vrss": "12.45",
                "prdy_ctrt": "0.50"
            },
            "1001": {  # 코스닥
                "stck_prpr": "800.45",
                "prdy_vrss": "9.67",
                "prdy_ctrt": "1.22"
            }
        }
        return sample_data.get(index_code, {})
    
    def _get_sample_overseas_index(self, index_code: str) -> Dict:
        """샘플 해외 지수 데이터"""
        sample_data = {
            "SPX": {  # S&P500
                "last": "5500.12",
                "diff": "43.67",
                "diff_rt": "0.80"
            },
            "IXIC": {  # NASDAQ
                "last": "17900.45",
                "diff": "195.23",
                "diff_rt": "1.10"
            },
            "DJI": {  # DOW
                "last": "38500.0",
                "diff": "115.50",
                "diff_rt": "0.30"
            }
        }
        return sample_data.get(index_code, {})
    
    def _get_sample_stock_price(self, stock_code: str) -> Dict:
        """샘플 종목 가격 데이터"""
        sample_data = {
            "005930": {  # 삼성전자
                "stck_prpr": "75000",
                "prdy_vrss": "1125",
                "prdy_ctrt": "1.52"
            },
            "000660": {  # SK하이닉스
                "stck_prpr": "125000",
                "prdy_vrss": "3875",
                "diff_rt": "3.20"
            }
        }
        return sample_data.get(stock_code, {})


def main():
    """테스트 실행"""
    client = KISAPIClient()
    market_data = client.get_market_data()
    
    print("=== 수집된 시장 데이터 ===")
    print(json.dumps(market_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 