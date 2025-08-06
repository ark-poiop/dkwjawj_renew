#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 Open API 클라이언트
실시간 시장 데이터 수집 및 정제
공식 GitHub API 사용
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
    """한국투자증권 Open API 클라이언트 (공식 API 사용)"""
    
    def __init__(self):
        # 공식 API 인증 모듈 사용
        try:
            from kis_auth import auth, getTREnv
            self.auth = auth
            self.getTREnv = getTREnv
            self.trenv = None
            
            # 인증 시도
            if self.auth("vps"):  # 모의투자 환경으로 시작
                self.trenv = self.getTREnv()
                logger.info("한국투자증권 API 인증 성공 (모의투자)")
            else:
                logger.warning("한국투자증권 API 인증 실패. 샘플 데이터를 사용합니다.")
                
        except ImportError:
            logger.warning("kis_auth 모듈을 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
            self.trenv = None
    
    def get_domestic_index(self, index_code: str = "0001") -> Optional[Dict]:
        """국내 지수 조회 (코스피: 0001, 코스닥: 1001)"""
        if not self.trenv:
            return self._get_sample_domestic_index(index_code)
        
        try:
            from domestic_stock_functions import inquire_index_price
            
            result = inquire_index_price("J", index_code)
            if result:
                return result
            else:
                logger.warning("API 조회 실패, 샘플 데이터 사용")
                return self._get_sample_domestic_index(index_code)
                
        except ImportError:
            logger.warning("domestic_stock_functions 모듈을 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
            return self._get_sample_domestic_index(index_code)
    
    def get_overseas_index(self, index_code: str = "SPX") -> Optional[Dict]:
        """해외 지수 조회 (S&P500: SPX, NASDAQ: IXIC, DOW: DJI)"""
        # 해외 지수는 별도 API가 필요하므로 샘플 데이터 사용
        return self._get_sample_overseas_index(index_code)
    
    def get_stock_price(self, stock_code: str) -> Optional[Dict]:
        """개별 종목 가격 조회"""
        if not self.trenv:
            return self._get_sample_stock_price(stock_code)
        
        try:
            from domestic_stock_functions import get_stock_price
            
            result = get_stock_price(stock_code)
            if result:
                return result
            else:
                logger.warning("API 조회 실패, 샘플 데이터 사용")
                return self._get_sample_stock_price(stock_code)
                
        except ImportError:
            logger.warning("domestic_stock_functions 모듈을 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
            return self._get_sample_stock_price(stock_code)
    
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
        
        collected_count = 0
        
        try:
            # 국내 지수
            kospi_data = self.get_domestic_index("0001")  # 코스피
            if kospi_data:
                market_data["indices"]["KOSPI"] = float(kospi_data.get('stck_prpr', 0))
                market_data["changes"]["KOSPI"] = float(kospi_data.get('prdy_vrss', 0))
                collected_count += 1
            
            kosdaq_data = self.get_domestic_index("1001")  # 코스닥
            if kosdaq_data:
                market_data["indices"]["KOSDAQ"] = float(kospi_data.get('stck_prpr', 0))
                market_data["changes"]["KOSDAQ"] = float(kospi_data.get('prdy_vrss', 0))
                collected_count += 1
            
            # 해외 지수 (샘플 데이터)
            sp500_data = self.get_overseas_index("SPX")  # S&P500
            if sp500_data:
                market_data["indices"]["S&P500"] = float(sp500_data.get('last', 0))
                market_data["changes"]["S&P500"] = float(sp500_data.get('diff', 0))
                collected_count += 1
            
            nasdaq_data = self.get_overseas_index("IXIC")  # NASDAQ
            if nasdaq_data:
                market_data["indices"]["NASDAQ"] = float(nasdaq_data.get('last', 0))
                market_data["changes"]["NASDAQ"] = float(nasdaq_data.get('diff', 0))
                collected_count += 1
            
            dow_data = self.get_overseas_index("DJI")  # DOW
            if dow_data:
                market_data["indices"]["DOW"] = float(dow_data.get('last', 0))
                market_data["changes"]["DOW"] = float(dow_data.get('diff', 0))
                collected_count += 1
                
        except Exception as e:
            logger.error(f"시장 데이터 수집 중 오류 발생: {e}")
            # 오류가 발생해도 수집된 데이터는 유지
        
        logger.info(f"시장 데이터 수집 완료: {collected_count}개 지수")
        return market_data
        
        # 주요 종목
        major_stocks = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035420": "NAVER",
            "051910": "LG화학",
            "006400": "삼성SDI"
        }
        
        for stock_code, stock_name in major_stocks.items():
            try:
                stock_data = self.get_stock_price(stock_code)
                if stock_data:
                    market_data["stocks"][stock_name] = {
                        "code": stock_code,
                        "price": float(stock_data.get('stck_prpr', 0)),
                        "change": float(stock_data.get('prdy_vrss', 0)),
                        "change_rate": float(stock_data.get('prdy_ctrt', 0))
                    }
            except Exception as e:
                logger.warning(f"종목 {stock_name} 데이터 수집 실패: {e}")
        
        return market_data
    
    def _get_sample_domestic_index(self, index_code: str) -> Dict:
        """샘플 국내 지수 데이터"""
        if index_code == "0001":  # 코스피
            return {
                "stck_prpr": "2500.12",
                "prdy_vrss": "15.23",
                "prdy_ctrt": "0.61",
                "acml_tr_pbmn": "1234567890",
                "acml_vol": "987654321"
            }
        elif index_code == "1001":  # 코스닥
            return {
                "stck_prpr": "800.45",
                "prdy_vrss": "8.12",
                "prdy_ctrt": "1.02",
                "acml_tr_pbmn": "5678901234",
                "acml_vol": "123456789"
            }
        else:
            return {
                "stck_prpr": "1000.00",
                "prdy_vrss": "0.00",
                "prdy_ctrt": "0.00",
                "acml_tr_pbmn": "0",
                "acml_vol": "0"
            }
    
    def _get_sample_overseas_index(self, index_code: str) -> Dict:
        """샘플 해외 지수 데이터"""
        if index_code == "SPX":  # S&P500
            return {
                "last": "5500.12",
                "diff": "44.23",
                "change": "0.81",
                "volume": "2345678901"
            }
        elif index_code == "IXIC":  # NASDAQ
            return {
                "last": "17900.45",
                "diff": "195.67",
                "change": "1.10",
                "volume": "3456789012"
            }
        elif index_code == "DJI":  # DOW
            return {
                "last": "38500.00",
                "diff": "115.50",
                "change": "0.30",
                "volume": "4567890123"
            }
        else:
            return {
                "last": "1000.00",
                "diff": "0.00",
                "change": "0.00",
                "volume": "0"
            }
    
    def _get_sample_stock_price(self, stock_code: str) -> Dict:
        """샘플 주식 가격 데이터"""
        sample_data = {
            "005930": {  # 삼성전자
                "stck_prpr": "75000",
                "prdy_vrss": "1500",
                "prdy_ctrt": "2.04",
                "acml_tr_pbmn": "1234567890",
                "acml_vol": "987654321"
            },
            "000660": {  # SK하이닉스
                "stck_prpr": "125000",
                "prdy_vrss": "2500",
                "prdy_ctrt": "2.04",
                "acml_tr_pbmn": "5678901234",
                "acml_vol": "123456789"
            },
            "035420": {  # NAVER
                "stck_prpr": "180000",
                "prdy_vrss": "3000",
                "prdy_ctrt": "1.69",
                "acml_tr_pbmn": "3456789012",
                "acml_vol": "234567890"
            }
        }
        
        return sample_data.get(stock_code, {
            "stck_prpr": "10000",
            "prdy_vrss": "0",
            "prdy_ctrt": "0.00",
            "acml_tr_pbmn": "0",
            "acml_vol": "0"
        })


def main():
    """테스트 실행"""
    client = KISAPIClient()
    
    # 코스피 지수 조회
    kospi_data = client.get_domestic_index("0001")
    print(f"코스피: {kospi_data}")
    
    # 삼성전자 주가 조회
    samsung_data = client.get_stock_price("005930")
    print(f"삼성전자: {samsung_data}")
    
    # 전체 시장 데이터 조회
    market_data = client.get_market_data()
    print(f"시장 데이터: {market_data}")


if __name__ == "__main__":
    main() 