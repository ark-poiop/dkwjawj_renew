#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬 테스트 스크립트
.env 파일을 사용한 로컬 환경 테스트
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_env_variables():
    """환경변수 테스트"""
    print("=== 환경변수 테스트 ===")
    
    # 한국투자증권 API
    kis_app_key = os.getenv('KIS_APP_KEY')
    kis_app_secret = os.getenv('KIS_APP_SECRET')
    
    print(f"KIS_APP_KEY: {'설정됨' if kis_app_key and kis_app_key != 'your_kis_app_key_here' else '설정되지 않음'}")
    print(f"KIS_APP_SECRET: {'설정됨' if kis_app_secret and kis_app_secret != 'your_kis_app_secret_here' else '설정되지 않음'}")
    
    # Threads API
    threads_api_key = os.getenv('THREADS_API_KEY')
    threads_access_token = os.getenv('THREADS_ACCESS_TOKEN')
    threads_user_id = os.getenv('THREADS_USER_ID')
    
    print(f"THREADS_API_KEY: {'설정됨' if threads_api_key and threads_api_key != 'your_threads_api_key_here' else '설정되지 않음'}")
    print(f"THREADS_ACCESS_TOKEN: {'설정됨' if threads_access_token and threads_access_token != 'your_threads_access_token_here' else '설정되지 않음'}")
    print(f"THREADS_USER_ID: {'설정됨' if threads_user_id and threads_user_id != 'your_threads_user_id_here' else '설정되지 않음'}")
    
    # Slack
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    print(f"SLACK_WEBHOOK_URL: {'설정됨' if slack_webhook and slack_webhook != 'your_slack_webhook_url_here' else '설정되지 않음'}")
    
    print()

def test_system():
    """시스템 테스트"""
    print("=== 시스템 테스트 ===")
    
    try:
        from auto_briefing_system import AutoBriefingSystem
        
        system = AutoBriefingSystem()
        
        # 시스템 상태 확인
        status = system.get_system_status()
        print("시스템 상태:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print()
        
        # 07:00 브리핑 테스트
        print("07:00 브리핑 테스트 실행...")
        result = system.run_briefing("07:00")
        
        if result['success']:
            print("✅ 브리핑 생성 성공!")
            print(f"주제: {result['topic']}")
            print(f"게시 결과: {result['publish_result'].get('success', False)}")
            
            # 브리핑 내용 미리보기
            content = result['briefing_content']
            print("\n=== 생성된 브리핑 ===")
            print(content[:200] + "..." if len(content) > 200 else content)
            
        else:
            print("❌ 브리핑 생성 실패!")
            print(f"에러: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 시스템 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

def main():
    """메인 함수"""
    print("🚀 자동 시장 브리핑 시스템 - 로컬 테스트")
    print("=" * 50)
    
    # 환경변수 테스트
    test_env_variables()
    
    # 시스템 테스트
    test_system()
    
    print("=" * 50)
    print("테스트 완료!")

if __name__ == "__main__":
    main() 