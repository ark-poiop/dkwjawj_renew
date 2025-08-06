#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시장 브리핑 생성기
시간대별 프롬프트 분기 및 Threads 포맷팅
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BriefingContent:
    """브리핑 콘텐츠 구조체"""
    main_content: str      # 본문
    comments: List[str]    # 댓글 리스트
    hashtags: List[str]    # 해시태그


class MarketBriefingGenerator:
    """시장 브리핑 생성기"""
    
    def __init__(self):
        self.time_slots = {
            "07:00": "미국 마켓 마감 브리핑",
            "08:00": "오늘의 한국시장 프리뷰", 
            "12:00": "한국시장 시황 중간 브리핑",
            "15:40": "한국시장 마감 브리핑",
            "19:00": "미국 마켓 프리뷰"
        }
        
    def generate_briefing(self, time_slot: str, topic: str, market_data: Dict[str, Any]) -> BriefingContent:
        """
        브리핑 생성 메인 함수
        
        Args:
            time_slot: 시간대 (07:00, 08:00, 12:00, 15:40, 19:00)
            topic: 주제
            market_data: 시장 데이터 딕셔너리
            
        Returns:
            BriefingContent: 생성된 브리핑 콘텐츠
        """
        # 시간대별 프롬프트 분기
        if time_slot == "07:00":
            return self._generate_us_market_close_briefing(topic, market_data)
        elif time_slot == "08:00":
            return self._generate_kr_market_preview_briefing(topic, market_data)
        elif time_slot == "12:00":
            return self._generate_kr_market_midday_briefing(topic, market_data)
        elif time_slot == "15:40":
            return self._generate_kr_market_close_briefing(topic, market_data)
        elif time_slot == "19:00":
            return self._generate_us_market_preview_briefing(topic, market_data)
        else:
            raise ValueError(f"지원하지 않는 시간대: {time_slot}")
    
    def _generate_us_market_close_briefing(self, topic: str, data: Dict[str, Any]) -> BriefingContent:
        """07:00 - 미국 마켓 마감 브리핑"""
        # 본문 생성
        main_content = f"🌅 {topic}\n"
        
        # 주요 지수
        indices = data.get('indices', {})
        changes = data.get('changes', {})
        
        if 'S&P500' in indices:
            change_pct = (changes.get('S&P500', 0) / indices['S&P500'] * 100) if indices['S&P500'] > 0 else 0
            main_content += f"• S&P500 {indices['S&P500']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'NASDAQ' in indices:
            change_pct = (changes.get('NASDAQ', 0) / indices['NASDAQ'] * 100) if indices['NASDAQ'] > 0 else 0
            main_content += f"• 나스닥 {indices['NASDAQ']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'DOW' in indices:
            change_pct = (changes.get('DOW', 0) / indices['DOW'] * 100) if indices['DOW'] > 0 else 0
            main_content += f"• 다우 {indices['DOW']:,.0f}pt ({change_pct:+.1f}%)\n"
        
        # 주요 종목 (변동률 상위 3개)
        stocks = data.get('stocks', {})
        top_stocks = sorted(stocks.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        for stock, change in top_stocks:
            main_content += f"• {stock} {change:+.1f}%\n"
        
        # 댓글 생성
        issues = data.get('issues', [])
        comments = [
            "💡 오늘의 관전포인트",
            f"- {issues[0] if issues else 'FOMC 결과 발표'} 후 변동성 확대",
            "- 반도체, AI 섹터 랠리 지속" if any(sector in ['반도체', 'AI'] for sector in data.get('sectors', {})) else "- 주요 섹터 성과 분화",
            "- 주요 기업 실적 발표 대기"
        ]
        
        return BriefingContent(
            main_content=main_content.strip(),
            comments=comments,
            hashtags=['#미국증시', '#S&P500', '#나스닥', '#글로벌마켓']
        )
    
    def _generate_kr_market_preview_briefing(self, topic: str, data: Dict[str, Any]) -> BriefingContent:
        """08:00 - 오늘의 한국시장 프리뷰"""
        main_content = f"🌞 {topic}\n"
        
        # 전일 마감 지수
        indices = data.get('indices', {})
        changes = data.get('changes', {})
        
        if 'KOSPI' in indices:
            change_pct = (changes.get('KOSPI', 0) / indices['KOSPI'] * 100) if indices['KOSPI'] > 0 else 0
            main_content += f"• 전일 코스피 {indices['KOSPI']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'KOSDAQ' in indices:
            change_pct = (changes.get('KOSDAQ', 0) / indices['KOSDAQ'] * 100) if indices['KOSDAQ'] > 0 else 0
            main_content += f"• 전일 코스닥 {indices['KOSDAQ']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        # 글로벌 영향
        if 'S&P500' in changes:
            change_pct = (changes['S&P500'] / indices.get('S&P500', 1) * 100) if indices.get('S&P500', 0) > 0 else 0
            main_content += f"• 미국장 영향: S&P500 {change_pct:+.1f}%\n"
        
        # 주요 이슈
        issues = data.get('issues', [])
        if issues:
            main_content += f"• 주요 이슈: {issues[0]}\n"
        
        comments = [
            "📋 개장 전 체크리스트",
            "- 글로벌 증시 동향 체크",
            "- 주요 경제지표 발표 일정",
            "- 섹터별 투자 포인트"
        ]
        
        return BriefingContent(
            main_content=main_content.strip(),
            comments=comments,
            hashtags=['#한국증시', '#코스피', '#코스닥', '#오늘의시장']
        )
    
    def _generate_kr_market_midday_briefing(self, topic: str, data: Dict[str, Any]) -> BriefingContent:
        """12:00 - 한국시장 시황 중간 브리핑"""
        main_content = f"☀️ {topic}\n"
        
        # 오전장 지수
        indices = data.get('indices', {})
        changes = data.get('changes', {})
        
        if 'KOSPI' in indices:
            change_pct = (changes.get('KOSPI', 0) / indices['KOSPI'] * 100) if indices['KOSPI'] > 0 else 0
            main_content += f"• 코스피 {indices['KOSPI']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'KOSDAQ' in indices:
            change_pct = (changes.get('KOSDAQ', 0) / indices['KOSDAQ'] * 100) if indices['KOSDAQ'] > 0 else 0
            main_content += f"• 코스닥 {indices['KOSDAQ']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        # 주요 섹터 (변동률 상위 2개)
        sectors = data.get('sectors', {})
        top_sectors = sorted(sectors.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
        for sector, change in top_sectors:
            main_content += f"• {sector} {change:+.1f}%\n"
        
        # 투자자 동향
        main_content += "• 외국인/기관 수급 관심\n"
        
        comments = [
            "🔍 오후장 관전포인트",
            "- 변동성 확대 원인 분석",
            "- 외국인/기관 수급 동향",
            "- 섹터별 성과 전망"
        ]
        
        return BriefingContent(
            main_content=main_content.strip(),
            comments=comments,
            hashtags=['#한국증시', '#오전장', '#시황', '#투자자동향']
        )
    
    def _generate_kr_market_close_briefing(self, topic: str, data: Dict[str, Any]) -> BriefingContent:
        """15:40 - 한국시장 마감 브리핑"""
        main_content = f"🌆 {topic}\n"
        
        # 마감 지수
        indices = data.get('indices', {})
        changes = data.get('changes', {})
        
        if 'KOSPI' in indices:
            change_pct = (changes.get('KOSPI', 0) / indices['KOSPI'] * 100) if indices['KOSPI'] > 0 else 0
            main_content += f"• 코스피 {indices['KOSPI']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'KOSDAQ' in indices:
            change_pct = (changes.get('KOSDAQ', 0) / indices['KOSDAQ'] * 100) if indices['KOSDAQ'] > 0 else 0
            main_content += f"• 코스닥 {indices['KOSDAQ']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        # 주도 업종 (변동률 상위 2개)
        sectors = data.get('sectors', {})
        top_sectors = sorted(sectors.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
        for sector, change in top_sectors:
            main_content += f"• {sector} {change:+.1f}%\n"
        
        # 주요 종목 (변동률 상위 2개)
        stocks = data.get('stocks', {})
        top_stocks = sorted(stocks.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
        for stock, change in top_stocks:
            main_content += f"• {stock} {change:+.1f}%\n"
        
        comments = [
            "📈 내일장 관전포인트",
            "- 실적발표 예정 기업 체크",
            "- 정책/이벤트 영향 분석",
            "- 투자 전략 점검"
        ]
        
        return BriefingContent(
            main_content=main_content.strip(),
            comments=comments,
            hashtags=['#한국증시', '#마감', '#일일시황', '#투자전략']
        )
    
    def _generate_us_market_preview_briefing(self, topic: str, data: Dict[str, Any]) -> BriefingContent:
        """19:00 - 미국 마켓 프리뷰"""
        main_content = f"🌙 {topic}\n"
        
        # 선물 지수
        indices = data.get('indices', {})
        changes = data.get('changes', {})
        
        if 'S&P500' in indices:
            change_pct = (changes.get('S&P500', 0) / indices['S&P500'] * 100) if indices['S&P500'] > 0 else 0
            main_content += f"• S&P500 선물 {indices['S&P500']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        if 'NASDAQ' in indices:
            change_pct = (changes.get('NASDAQ', 0) / indices['NASDAQ'] * 100) if indices['NASDAQ'] > 0 else 0
            main_content += f"• 나스닥 선물 {indices['NASDAQ']:,.2f}pt ({change_pct:+.1f}%)\n"
        
        # 글로벌 뉴스
        issues = data.get('issues', [])
        if issues:
            main_content += f"• 글로벌 이슈: {issues[0]}\n"
        
        # 발표 예정
        events = data.get('events', [])
        if events:
            main_content += f"• 발표 예정: {events[0]}\n"
        
        comments = [
            "🌃 오늘밤 주목 포인트",
            "- 주요 경제지표 발표",
            "- 기업 실적 발표 일정",
            "- 글로벌 이벤트 영향"
        ]
        
        return BriefingContent(
            main_content=main_content.strip(),
            comments=comments,
            hashtags=['#미국증시', '#프리마켓', '#글로벌이슈', '#실적발표']
        )
    
    def format_for_threads(self, briefing: BriefingContent) -> str:
        """Threads용 포맷으로 변환"""
        result = briefing.main_content + "\n\n"
        
        for comment in briefing.comments:
            result += comment + "\n"
        
        if briefing.hashtags:
            result += "\n" + " ".join(briefing.hashtags)
        
        return result


def main():
    """테스트 실행"""
    from kis_api_client import KISAPIClient
    
    # API 클라이언트로 데이터 수집
    client = KISAPIClient()
    market_data = client.get_market_data()
    
    # 브리핑 생성기
    generator = MarketBriefingGenerator()
    
    # 각 시간대별 브리핑 생성 테스트
    time_slots = ["07:00", "08:00", "12:00", "15:40", "19:00"]
    topics = [
        "미국 증시 마감 요약",
        "오늘의 한국시장 전망",
        "오전장 시황 요약",
        "한국시장 마감 요약",
        "미국장 개장 전 체크"
    ]
    
    for time_slot, topic in zip(time_slots, topics):
        print(f"\n=== {time_slot} - {topic} ===")
        briefing = generator.generate_briefing(time_slot, topic, market_data)
        print(generator.format_for_threads(briefing))
        print("=" * 60)


if __name__ == "__main__":
    main() 