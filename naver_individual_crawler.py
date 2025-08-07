#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 증권 개별 지수 크롤러
각 지수별 개별 페이지에서 실시간 데이터 수집
"""

import requests
import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import re
import time
import random

logger = logging.getLogger(__name__)

class NaverIndividualCrawler:
    """네이버 증권 개별 지수 크롤러"""
    
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
        
        # 개별 지수 URL 매핑
        self.index_urls = {
            'S&P500': 'https://finance.naver.com/world/sise.naver?symbol=SPI@SPX',
            'NASDAQ': 'https://finance.naver.com/world/sise.naver?symbol=NAS@IXIC',
            'DOW': 'https://finance.naver.com/world/sise.naver?symbol=DJI@DJI'
        }
    
    def get_overseas_market_data(self) -> Dict[str, Any]:
        """
        해외 시장 데이터 수집
        
        Returns:
            Dict[str, Any]: 해외 시장 데이터
        """
        try:
            logger.info("네이버 증권 개별 페이지에서 데이터 수집 시작")
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "naver_individual"
            }
            
            # 각 지수별 개별 페이지에서 데이터 수집
            for index_name, url in self.index_urls.items():
                try:
                    data = self._get_index_data(url, index_name)
                    if data:
                        market_data["indices"][index_name] = data["price"]
                        market_data["changes"][index_name] = data["change"]
                        logger.info(f"{index_name}: {data['price']:,.2f} ({data['change']:+.2f})")
                    
                    # 요청 간 딜레이
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"{index_name} 데이터 수집 실패: {e}")
                    continue
            
            success_count = len(market_data["indices"])
            logger.info(f"해외 시장 데이터 수집 완료: {success_count}개 지수")
            
            return market_data
            
        except Exception as e:
            logger.error(f"해외 시장 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "naver_individual_error"}
    
    def _get_index_data(self, url: str, index_name: str) -> Optional[Dict[str, float]]:
        """
        개별 지수 페이지에서 데이터 수집
        
        Args:
            url: 지수 페이지 URL
            index_name: 지수 이름
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 인코딩 설정
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 현재가 추출
            price = self._extract_price(soup)
            if price is None:
                logger.warning(f"{index_name}: 가격을 찾을 수 없음")
                return None
            
            # 변동폭 추출
            change = self._extract_change(soup)
            
            # 가격 범위 검증
            if not self._is_valid_price(price, index_name):
                logger.warning(f"{index_name}: 가격이 비정상적입니다 - {price}")
                return None
            
            return {
                "price": price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"{index_name} 데이터 수집 중 오류: {e}")
            return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """현재가 추출"""
        try:
            # 여러 방법으로 가격 추출 시도
            price_selectors = [
                'span.price',
                'strong.price',
                'span.current_price',
                'div.price_area strong',
                'td.price',
                'span#current_price'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip().replace(',', '')
                    price = self._parse_number(price_text)
                    if price:
                        return price
            
            # 텍스트에서 패턴 매칭
            page_text = soup.get_text()
            price_patterns = [
                r'현재가[^\d]*([\d,]+\.?\d*)',
                r'종가[^\d]*([\d,]+\.?\d*)',
                r'가격[^\d]*([\d,]+\.?\d*)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    price_text = match.group(1).replace(',', '')
                    price = self._parse_number(price_text)
                    if price:
                        return price
            
            return None
            
        except Exception as e:
            logger.error(f"가격 추출 중 오류: {e}")
            return None
    
    def _extract_change(self, soup: BeautifulSoup) -> float:
        """변동폭 추출"""
        try:
            # 여러 방법으로 변동폭 추출 시도
            change_selectors = [
                'span.change',
                'em.change',
                'span.diff',
                'td.change',
                'span#change'
            ]
            
            for selector in change_selectors:
                change_element = soup.select_one(selector)
                if change_element:
                    change_text = change_element.get_text().strip()
                    change = self._parse_number(change_text)
                    if change is not None:
                        return change
            
            # 텍스트에서 패턴 매칭
            page_text = soup.get_text()
            change_patterns = [
                r'변동[^\d]*([+-]?[\d,]+\.?\d*)',
                r'등락[^\d]*([+-]?[\d,]+\.?\d*)',
                r'([+-]?\d+\.?\d*)\s*[%]'
            ]
            
            for pattern in change_patterns:
                match = re.search(pattern, page_text)
                if match:
                    change_text = match.group(1).replace(',', '')
                    change = self._parse_number(change_text)
                    if change is not None:
                        return change
            
            return 0.0
            
        except Exception as e:
            logger.error(f"변동폭 추출 중 오류: {e}")
            return 0.0
    
    def _parse_number(self, text: str) -> Optional[float]:
        """텍스트에서 숫자 추출"""
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
    
    def _is_valid_price(self, price: float, index_name: str) -> bool:
        """가격 유효성 검사"""
        if index_name == 'S&P500':
            return 1000 <= price <= 10000  # S&P500 일반적인 범위
        elif index_name == 'NASDAQ':
            return 5000 <= price <= 30000  # NASDAQ 일반적인 범위
        elif index_name == 'DOW':
            return 10000 <= price <= 50000  # DOW 일반적인 범위
        return True

def test_naver_individual_crawler():
    """네이버 개별 지수 크롤러 테스트"""
    crawler = NaverIndividualCrawler()
    
    print("=== 네이버 증권 개별 지수 테스트 ===")
    data = crawler.get_overseas_market_data()
    
    print(f"수집된 데이터: {data}")
    
    if data.get("indices"):
        print("\n=== 수집 결과 ===")
        for index, price in data["indices"].items():
            change = data.get("changes", {}).get(index, 0)
            print(f"{index}: {price:,.2f} ({change:+.2f})")
    else:
        print("데이터 수집 실패")

if __name__ == "__main__":
    test_naver_individual_crawler()
