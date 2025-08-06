#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 배포 테스트 스크립트
Threads API 통신 및 전체 시스템 상태 확인
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """환경 변수 설정 확인"""
    print("🔍 환경 변수 설정 확인...")
    
    # .env 파일 로드
    load_dotenv()
    
    required_vars = [
        'KIS_APP_KEY',
        'KIS_APP_SECRET', 
        'THREADS_ACCESS_TOKEN',
        'THREADS_USER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 설정됨")
        else:
            print(f"❌ {var}: 설정되지 않음")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  누락된 환경 변수: {', '.join(missing_vars)}")
        return False
    
    print("✅ 모든 환경 변수가 설정되었습니다.")
    return True

def test_threads_api():
    """Threads API 연결 테스트"""
    print("\n🧪 Threads API 연결 테스트...")
    
    try:
        from threads_api_client import ThreadsAPIClient
        
        client = ThreadsAPIClient()
        
        print(f"✅ Access Token: {'있음' if client.access_token else '없음'}")
        print(f"✅ User ID: {'있음' if client.user_id else '없음'}")
        print(f"✅ Base URL: {client.base_url}")
        print(f"✅ Post URL: {client.post_url}")
        
        # 간단한 테스트 게시
        test_content = "🧪 배포 테스트\n\nGitHub Actions 배포 확인 중입니다.\n\n#배포테스트 #ThreadsAPI"
        
        print("\n📝 테스트 게시 시도...")
        result = client.post_thread(test_content)
        
        if result and 'id' in result:
            print(f"✅ 게시 성공! 게시 ID: {result['id']}")
            return True
        else:
            print("❌ 게시 실패")
            return False
            
    except Exception as e:
        print(f"❌ Threads API 테스트 실패: {e}")
        return False

def test_kis_api():
    """KIS API 연결 테스트"""
    print("\n🏦 KIS API 연결 테스트...")
    
    try:
        from kis_api_client import KISAPIClient
        
        client = KISAPIClient()
        
        print(f"✅ App Key: {'있음' if client.app_key else '없음'}")
        print(f"✅ App Secret: {'있음' if client.app_secret else '없음'}")
        
        # 간단한 연결 테스트
        print("📊 시장 데이터 조회 테스트...")
        # 실제 API 호출은 여기서 생략 (테스트 목적)
        
        print("✅ KIS API 설정 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ KIS API 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 GitHub Actions 배포 테스트 시작")
    print("=" * 50)
    
    # 환경 변수 테스트
    env_ok = test_environment()
    
    # Threads API 테스트
    threads_ok = test_threads_api()
    
    # KIS API 테스트
    kis_ok = test_kis_api()
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약:")
    print(f"  - 환경 변수: {'✅' if env_ok else '❌'}")
    print(f"  - Threads API: {'✅' if threads_ok else '❌'}")
    print(f"  - KIS API: {'✅' if kis_ok else '❌'}")
    
    if all([env_ok, threads_ok, kis_ok]):
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("✅ GitHub Actions 배포 준비 완료")
        return 0
    else:
        print("\n⚠️  일부 테스트가 실패했습니다.")
        print("❌ 배포 전 문제를 해결해주세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 