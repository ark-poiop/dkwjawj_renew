#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 증권 크롤러
국내외 시장 데이터 수집
"""

import requests
import time
import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class NaverFinanceCrawler:
    """네이버 증권 크롤러"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 네이버 증권 URL
        self.urls = {
            'domestic': 'https://finance.naver.com/sise/',
            'overseas': 'https://finance.naver.com/world/'
        }
    
    def get_domestic_index(self) -> Optional[Dict]:
        """
        국내 지수 데이터 수집 (코스피, 코스닥)
        
        Returns:
            Dict: 국내 지수 데이터
        """
        try:
            logger.info("국내 지수 크롤링 시작")
            response = self.session.get(self.urls['domestic'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 지수 정보 추출
            index_data = {}
            
            # 코스피, 코스닥 정보 찾기
            # 페이지에서 "코스피", "코스닥" 텍스트가 포함된 부분 찾기
            kospi_text = soup.find(text=re.compile(r'코스피.*\d+\.\d+.*\d+\.\d+.*[+-]\d+\.\d+%'))
            kosdaq_text = soup.find(text=re.compile(r'코스닥.*\d+\.\d+.*\d+\.\d+.*[+-]\d+\.\d+%'))
            
            if kospi_text:
                # 코스피 데이터 파싱
                kospi_match = re.search(r'코스피\s+(\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%', kospi_text)
                if kospi_match:
                    index_data['KOSPI'] = {
                        'current_price': float(kospi_match.group(1)),
                        'change': float(kospi_match.group(2)),
                        'change_rate': float(kospi_match.group(3))
                    }
            
            if kosdaq_text:
                # 코스닥 데이터 파싱
                kosdaq_match = re.search(r'코스닥\s+(\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%', kosdaq_text)
                if kosdaq_match:
                    index_data['KOSDAQ'] = {
                        'current_price': float(kosdaq_match.group(1)),
                        'change': float(kosdaq_match.group(2)),
                        'change_rate': float(kosdaq_match.group(3))
                    }
            
            logger.info(f"국내 지수 크롤링 완료: {index_data}")
            return index_data
            
        except Exception as e:
            logger.error(f"국내 지수 크롤링 실패: {e}")
            return None
    
    def get_overseas_index(self) -> Optional[Dict]:
        """
        해외 지수 데이터 수집 (S&P500, NASDAQ, DOW)
        
        Returns:
            Dict: 해외 지수 데이터
        """
        try:
            logger.info("해외 지수 크롤링 시작")
            response = self.session.get(self.urls['overseas'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 지수 정보 추출
            index_data = {}
            
            # S&P500, NASDAQ, DOW 정보 찾기
            # 페이지에서 해외 지수 정보가 포함된 부분 찾기
            sp500_text = soup.find(text=re.compile(r'S&P500.*\d+\.\d+.*[+-]\d+\.\d+'))
            nasdaq_text = soup.find(text=re.compile(r'NASDAQ.*\d+\.\d+.*[+-]\d+\.\d+'))
            dow_text = soup.find(text=re.compile(r'다우.*\d+\.\d+.*[+-]\d+\.\d+'))
            
            if sp500_text:
                # S&P500 데이터 파싱
                sp500_match = re.search(r'S&P500\s+(\d+\.\d+)\s+([+-]?\d+\.\d+)', sp500_text)
                if sp500_match:
                    index_data['S&P500'] = {
                        'current_price': float(sp500_match.group(1)),
                        'change': float(sp500_match.group(2))
                    }
            
            if nasdaq_text:
                # NASDAQ 데이터 파싱
                nasdaq_match = re.search(r'NASDAQ\s+(\d+\.\d+)\s+([+-]?\d+\.\d+)', nasdaq_text)
                if nasdaq_match:
                    index_data['NASDAQ'] = {
                        'current_price': float(nasdaq_match.group(1)),
                        'change': float(nasdaq_match.group(2))
                    }
            
            if dow_text:
                # DOW 데이터 파싱
                dow_match = re.search(r'다우\s+(\d+\.\d+)\s+([+-]?\d+\.\d+)', dow_text)
                if dow_match:
                    index_data['DOW'] = {
                        'current_price': float(dow_match.group(1)),
                        'change': float(dow_match.group(2))
                    }
            
            logger.info(f"해외 지수 크롤링 완료: {index_data}")
            return index_data
            
        except Exception as e:
            logger.error(f"해외 지수 크롤링 실패: {e}")
            return None
    
    def get_market_data(self) -> Dict[str, Any]:
        """
        전체 시장 데이터 수집
        
        Returns:
            Dict: 전체 시장 데이터
        """
        logger.info("네이버 증권 시장 데이터 수집 시작")
        
        market_data = {
            "indices": {},
            "changes": {},
            "sectors": {},
            "stocks": {},
            "issues": [],
            "events": [],
            "timestamp": datetime.now().isoformat(),
            "source": "naver_finance"
        }
        
        # 국내 지수
        domestic_data = self.get_domestic_index()
        if domestic_data:
            for index_name, data in domestic_data.items():
                market_data["indices"][index_name] = data['current_price']
                market_data["changes"][index_name] = data['change']
        
        # 해외 지수
        overseas_data = self.get_overseas_index()
        if overseas_data:
            for index_name, data in overseas_data.items():
                market_data["indices"][index_name] = data['current_price']
                market_data["changes"][index_name] = data['change']
        
        # API 호출 제한을 위한 대기
        time.sleep(1)
        
        logger.info(f"네이버 증권 시장 데이터 수집 완료: {len(market_data.get('indices', {}))}개 지수")
        return market_data


def main():
    """테스트 실행"""
    crawler = NaverFinanceCrawler()
    
    # 국내 지수 테스트
    print("=== 국내 지수 테스트 ===")
    domestic = crawler.get_domestic_index()
    print(f"국내 지수: {domestic}")
    
    # 해외 지수 테스트
    print("\n=== 해외 지수 테스트 ===")
    overseas = crawler.get_overseas_index()
    print(f"해외 지수: {overseas}")
    
    # 전체 데이터 테스트
    print("\n=== 전체 시장 데이터 테스트 ===")
    market_data = crawler.get_market_data()
    print(f"시장 데이터: {market_data}")


if __name__ == "__main__":
    main()
