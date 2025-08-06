#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 Open API 인증 모듈
공식 GitHub kis_auth.py 기반
"""

import os
import yaml
import json
import time
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 설정 파일 경로
config_root = os.path.join(os.path.expanduser("~"), "KIS", "config")

class KISAuth:
    """한국투자증권 API 인증 클래스"""
    
    def __init__(self):
        self.config = self._load_config()
        self.access_token = None
        self.token_expires = None
        self.trenv = {}
        
    def _load_config(self):
        """설정 파일 로드"""
        try:
            # 현재 디렉토리의 kis_devlp.yaml 파일 로드
            config_path = "kis_devlp.yaml"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("kis_devlp.yaml 파일이 없습니다. 환경변수를 사용합니다.")
                return self._load_from_env()
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return self._load_from_env()
    
    def _load_from_env(self):
        """환경변수에서 설정 로드"""
        return {
            'my_app': os.getenv('KIS_APP_KEY', ''),
            'my_sec': os.getenv('KIS_APP_SECRET', ''),
            'paper_app': os.getenv('KIS_PAPER_APP_KEY', ''),
            'paper_sec': os.getenv('KIS_PAPER_APP_SECRET', ''),
            'my_htsid': os.getenv('KIS_HTS_ID', ''),
            'my_acct_stock': os.getenv('KIS_ACCOUNT_STOCK', ''),
            'my_prod': os.getenv('KIS_ACCOUNT_PROD', '01')
        }
    
    def auth(self, svr="vps", product="01"):
        """
        API 인증 및 토큰 발급
        
        Args:
            svr: 서버 환경 ("vps": 모의투자, "prod": 실전투자)
            product: 계좌 종류 ("01": 종합계좌)
        """
        try:
            # 서버 환경에 따른 설정
            if svr == "vps":
                app_key = self.config.get('paper_app', '')
                app_secret = self.config.get('paper_sec', '')
                base_url = "https://openapivts.koreainvestment.com:29443"
            else:  # prod
                app_key = self.config.get('my_app', '')
                app_secret = self.config.get('my_sec', '')
                base_url = "https://openapi.koreainvestment.com:9443"
            
            if not app_key or not app_secret:
                logger.error("앱키 또는 앱시크릿이 설정되지 않았습니다.")
                return False
            
            # 토큰 발급 요청
            auth_url = f"{base_url}/oauth2/tokenP"
            headers = {
                "content-type": "application/json"
            }
            body = {
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret
            }
            
            logger.info(f"토큰 발급 시도 - 서버: {svr}")
            response = requests.post(auth_url, headers=headers, data=json.dumps(body))
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                expires_in = data.get('expires_in', 86400)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
                # 거래 환경 설정
                self.trenv = {
                    'svr': svr,
                    'product': product,
                    'base_url': base_url,
                    'app_key': app_key,
                    'app_secret': app_secret,
                    'access_token': self.access_token
                }
                
                logger.info("토큰 발급 성공")
                return True
            else:
                logger.error(f"토큰 발급 실패 - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"인증 실패: {e}")
            return False
    
    def getTREnv(self):
        """거래 환경 정보 반환"""
        return self.trenv
    
    def get_access_token(self):
        """액세스 토큰 반환"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        return None

# 전역 인스턴스
kis_auth = KISAuth()

def auth(svr="vps", product="01"):
    """인증 함수 (공식 API와 호환)"""
    return kis_auth.auth(svr, product)

def getTREnv():
    """거래 환경 정보 반환 함수 (공식 API와 호환)"""
    return kis_auth.getTREnv() 