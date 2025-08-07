#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 증권 크롤러
국내 시장 데이터 수집 (KOSPI, KOSDAQ)
"""

import requests
import time
import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re
import random

logger = logging.getLogger(__name__)

class NaverFinanceCrawler:
    """네이버 증권 국내 시장 크롤러"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 네이버 증권 URL
        self.base_url = 'https://finance.naver.com'
        self.urls = {
            'main': 'https://finance.naver.com/',
            'kospi': 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI',
            'kosdaq': 'https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ'
        }
    
    def get_domestic_market_data(self) -> Dict[str, Any]:
        """
        국내 시장 데이터 수집 (KOSPI, KOSDAQ)
        
        Returns:
            Dict[str, Any]: 국내 시장 데이터
        """
        try:
            logger.info("네이버 증권에서 국내 시장 데이터 수집 시작")
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "naver_finance"
            }
            
            # 메인 페이지에서 모든 데이터 수집
            response = self.session.get(self.urls['main'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # KOSPI, KOSDAQ 데이터 추출
            kospi_data = self._extract_index_from_main(soup, 'KOSPI')
            if kospi_data:
                market_data["indices"]["KOSPI"] = kospi_data["price"]
                market_data["changes"]["KOSPI"] = kospi_data["change"]
                logger.info(f"KOSPI: {kospi_data['price']:,.2f} ({kospi_data['change']:+.2f})")
            
            kosdaq_data = self._extract_index_from_main(soup, 'KOSDAQ')
            if kosdaq_data:
                market_data["indices"]["KOSDAQ"] = kosdaq_data["price"]
                market_data["changes"]["KOSDAQ"] = kosdaq_data["change"]
                logger.info(f"KOSDAQ: {kosdaq_data['price']:,.2f} ({kosdaq_data['change']:+.2f})")
            
            success_count = len(market_data["indices"])
            logger.info(f"국내 시장 데이터 수집 완료: {success_count}/2개 성공")
            
            return market_data
            
        except Exception as e:
            logger.error(f"국내 시장 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "naver_finance_error"}
    
    def _extract_index_from_main(self, soup: BeautifulSoup, index_name: str) -> Optional[Dict[str, float]]:
        """
        메인 페이지에서 지수 데이터 추출
        
        Args:
            soup: BeautifulSoup 객체
            index_name: 지수 이름 (KOSPI, KOSDAQ)
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            # 페이지 전체 텍스트에서 패턴 찾기
            page_text = soup.get_text()
            
            # KOSPI 패턴
            if index_name == 'KOSPI':
                # 여러 패턴 시도
                patterns = [
                    r'KOSPI[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                    r'코스피[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                    r'코스피지수[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                ]
            else:  # KOSDAQ
                patterns = [
                    r'KOSDAQ[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                    r'코스닥[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                    r'코스닥지수[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                ]
            
            price = None
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    price_text = match.group(1)
                    price = self._parse_number(price_text)
                    if price and self._is_valid_price(price, index_name):
                        break
            
            if price is None:
                logger.warning(f"{index_name} 가격을 찾을 수 없음")
                return None
            
            # 변동폭 추출 (가격 근처에서 찾기)
            change = 0.0
            change_patterns = [
                r'[+-]?\d+\.?\d*',
                r'[+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?'
            ]
            
            # 가격 주변 텍스트에서 변동폭 찾기
            price_index = page_text.find(str(int(price)))
            if price_index != -1:
                # 가격 주변 100자 내에서 변동폭 찾기
                start = max(0, price_index - 50)
                end = min(len(page_text), price_index + 150)
                nearby_text = page_text[start:end]
                
                for pattern in change_patterns:
                    matches = re.findall(pattern, nearby_text)
                    for match in matches:
                        change_val = self._parse_number(match)
                        if change_val and change_val != price and abs(change_val) < price * 0.1:  # 변동폭은 가격의 10% 이내
                            change = change_val
                            break
                    if change != 0.0:
                        break
            
            return {
                "price": price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"{index_name} 데이터 추출 중 오류: {e}")
            return None
    
    def _is_valid_price(self, price: float, index_name: str) -> bool:
        """
        가격 유효성 검사
        
        Args:
            price: 가격
            index_name: 지수 이름
            
        Returns:
            bool: 유효성 여부
        """
        if index_name == 'KOSPI':
            return 1000 <= price <= 5000  # KOSPI 일반적인 범위
        elif index_name == 'KOSDAQ':
            return 500 <= price <= 1200   # KOSDAQ 일반적인 범위
        return True
    
    def _get_kospi_data(self) -> Optional[Dict[str, float]]:
        """KOSPI 데이터 수집"""
        try:
            response = self.session.get(self.urls['kospi'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # KOSPI 현재가 추출 - 여러 방법 시도
            price = None
            change = 0.0
            
            # 방법 1: 메인 지수 정보에서 추출
            main_info = soup.find('div', {'class': 'main_info'})
            if main_info:
                price_element = main_info.find('span', {'id': 'now_value'})
                if price_element:
                    price_text = price_element.get_text().strip()
                    price = self._parse_number(price_text)
                
                change_element = main_info.find('span', {'id': 'change_value'})
                if change_element:
                    change_text = change_element.get_text().strip()
                    change = self._parse_number(change_text) or 0.0
            
            # 방법 2: 테이블에서 추출
            if price is None:
                table = soup.find('table', {'class': 'type_1'})
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            first_cell = cells[0].get_text().strip()
                            if '현재가' in first_cell or '종가' in first_cell:
                                price_text = cells[1].get_text().strip()
                                price = self._parse_number(price_text)
                                if len(cells) >= 3:
                                    change_text = cells[2].get_text().strip()
                                    change = self._parse_number(change_text) or 0.0
                                break
            
            # 방법 3: 전체 텍스트에서 패턴 매칭
            if price is None:
                page_text = soup.get_text()
                # KOSPI 패턴 찾기
                kospi_pattern = r'KOSPI[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                match = re.search(kospi_pattern, page_text)
                if match:
                    price_text = match.group(1)
                    price = self._parse_number(price_text)
            
            if price is None:
                logger.warning("KOSPI 가격을 찾을 수 없음")
                return None
            
            # 가격 범위 검증 (KOSPI는 보통 2000-4000 범위)
            if price < 1000 or price > 5000:
                logger.warning(f"KOSPI 가격이 비정상적입니다: {price}")
                return None
            
            return {
                "price": price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"KOSPI 데이터 수집 중 오류: {e}")
            return None
    
    def _get_kosdaq_data(self) -> Optional[Dict[str, float]]:
        """KOSDAQ 데이터 수집"""
        try:
            response = self.session.get(self.urls['kosdaq'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # KOSDAQ 현재가 추출 - 여러 방법 시도
            price = None
            change = 0.0
            
            # 방법 1: 메인 지수 정보에서 추출
            main_info = soup.find('div', {'class': 'main_info'})
            if main_info:
                price_element = main_info.find('span', {'id': 'now_value'})
                if price_element:
                    price_text = price_element.get_text().strip()
                    price = self._parse_number(price_text)
                
                change_element = main_info.find('span', {'id': 'change_value'})
                if change_element:
                    change_text = change_element.get_text().strip()
                    change = self._parse_number(change_text) or 0.0
            
            # 방법 2: 테이블에서 추출
            if price is None:
                table = soup.find('table', {'class': 'type_1'})
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            first_cell = cells[0].get_text().strip()
                            if '현재가' in first_cell or '종가' in first_cell:
                                price_text = cells[1].get_text().strip()
                                price = self._parse_number(price_text)
                                if len(cells) >= 3:
                                    change_text = cells[2].get_text().strip()
                                    change = self._parse_number(change_text) or 0.0
                                break
            
            # 방법 3: 전체 텍스트에서 패턴 매칭
            if price is None:
                page_text = soup.get_text()
                # KOSDAQ 패턴 찾기
                kosdaq_pattern = r'KOSDAQ[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                match = re.search(kosdaq_pattern, page_text)
                if match:
                    price_text = match.group(1)
                    price = self._parse_number(price_text)
            
            if price is None:
                logger.warning("KOSDAQ 가격을 찾을 수 없음")
                return None
            
            # 가격 범위 검증 (KOSDAQ은 보통 700-900 범위)
            if price < 500 or price > 1200:
                logger.warning(f"KOSDAQ 가격이 비정상적입니다: {price}")
                return None
            
            return {
                "price": price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"KOSDAQ 데이터 수집 중 오류: {e}")
            return None
    
    def _parse_number(self, text: str) -> Optional[float]:
        """
        텍스트에서 숫자 추출
        
        Args:
            text: 숫자가 포함된 텍스트
            
        Returns:
            Optional[float]: 추출된 숫자
        """
        try:
            if not text:
                return None
            
            # 쉼표와 공백 제거
            cleaned = re.sub(r'[,\s]', '', text)
            
            # 부호 처리
            if '+' in cleaned:
                cleaned = cleaned.replace('+', '')
            elif '-' in cleaned:
                # 음수는 그대로 유지
                pass
            
            # 숫자만 추출
            number_match = re.search(r'[\d.-]+', cleaned)
            if number_match:
                return float(number_match.group())
            
            return None
        except (ValueError, TypeError):
            return None

def test_naver_finance_crawler():
    """네이버 증권 크롤러 테스트"""
    crawler = NaverFinanceCrawler()
    
    print("=== 네이버 증권 국내 시장 데이터 테스트 ===")
    data = crawler.get_domestic_market_data()
    
    print(f"수집된 데이터: {data}")
    
    if data.get("indices"):
        print("\n=== 수집 결과 ===")
        for index, price in data["indices"].items():
            change = data.get("changes", {}).get(index, 0)
            print(f"{index}: {price:,.2f} ({change:+.2f})")
    else:
        print("데이터 수집 실패")

if __name__ == "__main__":
    test_naver_finance_crawler()
