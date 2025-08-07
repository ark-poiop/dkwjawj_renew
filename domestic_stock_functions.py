#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 Open API 국내주식 함수들
공식 GitHub domestic_stock_functions.py 기반
"""

import requests
import json
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

def _ensure_auth():
    """인증 상태 확인 및 필요시 재인증"""
    try:
        from kis_auth import getTREnv, auth
        
        trenv = getTREnv()
        if not trenv or not trenv.get('access_token'):
            logger.info("인증이 필요합니다. 재인증을 시도합니다.")
            if auth('prod'):
                trenv = getTREnv()
                return trenv
            else:
                logger.error("인증 실패")
                return None
        return trenv
    except Exception as e:
        logger.error(f"인증 확인 중 오류: {e}")
        return None

def inquire_price(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930"):
    """
    주식현재가 시세 조회
    
    Args:
        env_dv: 환경 구분 ("real": 실전, "vps": 모의)
        fid_cond_mrkt_div_code: 시장 구분 ("J": 주식)
        fid_input_iscd: 종목 코드 (예: "005930" - 삼성전자)
    
    Returns:
        Dict: 조회 결과
    """
    try:
        # 인증 상태 확인
        trenv = _ensure_auth()
        if not trenv:
            logger.error("거래 환경이 설정되지 않았습니다.")
            return None
        
        # API 엔드포인트
        url = f"{trenv['base_url']}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        # 헤더 설정
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {trenv['access_token']}",
            "appkey": trenv['app_key'],
            "appsecret": trenv['app_secret'],
            "tr_id": "FHKST01010100"
        }
        
        # 파라미터 설정
        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd
        }
        
        logger.info(f"현재가 조회 - 종목: {fid_input_iscd}")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('rt_cd') == '0':
                result = data.get('output', {})
                logger.info(f"현재가 조회 성공 - 종목: {fid_input_iscd}")
                return result
            else:
                logger.error(f"현재가 조회 실패 - {data.get('msg1', '알 수 없는 오류')}")
                return None
        else:
            logger.error(f"현재가 조회 실패 - Status: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"현재가 조회 중 오류: {e}")
        return None

def inquire_index_price(fid_cond_mrkt_div_code="J", fid_input_iscd="0001"):
    """
    지수 현재가 조회
    
    Args:
        fid_cond_mrkt_div_code: 시장 구분 ("J": 주식)
        fid_input_iscd: 지수 코드 ("0001": 코스피, "1001": 코스닥)
    
    Returns:
        Dict: 조회 결과
    """
    return inquire_price(
        env_dv="real",
        fid_cond_mrkt_div_code=fid_cond_mrkt_div_code,
        fid_input_iscd=fid_input_iscd
    )

def get_kospi_price():
    """코스피 지수 조회"""
    return inquire_index_price("J", "0001")

def get_kosdaq_price():
    """코스닥 지수 조회"""
    return inquire_index_price("J", "1001")

def get_stock_price(stock_code):
    """
    개별 주식 현재가 조회
    
    Args:
        stock_code: 종목 코드 (예: "005930" - 삼성전자)
    
    Returns:
        Dict: 조회 결과
    """
    return inquire_price("real", "J", stock_code) 