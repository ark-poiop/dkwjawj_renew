#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threads API 통신 테스트 스크립트
.env 파일의 API 키로 Threads API 연결 상태만 확인
"""

import os
import requests
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_threads_api_connection():
    """Threads API 연결 테스트"""
    print("=== Threads API 연결 테스트 ===")
    
    # 환경변수 확인
    api_key = os.getenv('THREADS_API_KEY')
    access_token = os.getenv('THREADS_ACCESS_TOKEN')
    user_id = os.getenv('THREADS_USER_ID')
    
    print(f"API Key: {'✅ 설정됨' if api_key and api_key != 'your_threads_api_key_here' else '❌ 설정되지 않음'}")
    print(f"Access Token: {'✅ 설정됨' if access_token and access_token != 'your_threads_access_token_here' else '❌ 설정되지 않음'}")
    print(f"User ID: {'✅ 설정됨' if user_id and user_id != 'your_threads_user_id_here' else '❌ 설정되지 않음'}")
    
    # Access Token만 있어도 테스트 가능
    if not access_token or access_token == 'your_threads_access_token_here':
        print("\n❌ Access Token이 설정되지 않았습니다.")
        print("   .env 파일에서 실제 Access Token을 입력해주세요.")
        return False
    
    print("\n🔍 API 연결 테스트 중...")
    
    # Threads API 엔드포인트 (실제 API가 공개되면 업데이트 필요)
    base_url = "https://www.threads.net/api/v1"
    
    # 테스트할 엔드포인트들
    test_endpoints = [
        {
            "name": "사용자 정보 조회",
            "url": f"{base_url}/users/self/",
            "method": "GET"
        },
        {
            "name": "게시물 목록 조회",
            "url": f"{base_url}/media/configure/",
            "method": "GET"
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    success_count = 0
    
    for endpoint in test_endpoints:
        try:
            print(f"\n📡 {endpoint['name']} 테스트...")
            print(f"   URL: {endpoint['url']}")
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers, timeout=10)
            else:
                response = requests.post(endpoint['url'], headers=headers, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ 연결 성공!")
                success_count += 1
                
                # 응답 내용 일부 출력
                try:
                    data = response.json()
                    print(f"   응답: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   응답: {response.text[:200]}...")
                    
            elif response.status_code == 401:
                print("   ❌ 인증 실패 (Access Token 오류)")
            elif response.status_code == 403:
                print("   ❌ 권한 없음 (API 권한 부족)")
            elif response.status_code == 404:
                print("   ❌ 엔드포인트 없음 (API 경로 오류)")
            else:
                print(f"   ⚠️ 예상치 못한 응답: {response.status_code}")
                print(f"   응답: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("   ❌ 타임아웃 (서버 응답 없음)")
        except requests.exceptions.ConnectionError:
            print("   ❌ 연결 오류 (네트워크 또는 서버 문제)")
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
    
    print(f"\n📊 테스트 결과: {success_count}/{len(test_endpoints)} 성공")
    
    if success_count > 0:
        print("✅ Threads API 연결이 정상적으로 작동합니다!")
        return True
    else:
        print("❌ Threads API 연결에 실패했습니다.")
        return False

def test_simple_post():
    """간단한 게시 테스트"""
    print("\n=== 간단한 게시 테스트 ===")
    
    access_token = os.getenv('THREADS_ACCESS_TOKEN')
    user_id = os.getenv('THREADS_USER_ID')
    
    if not access_token or access_token == 'your_threads_access_token_here':
        print("❌ Access Token이 설정되지 않았습니다.")
        return False
    
    # 테스트 게시 내용
    test_content = "🧪 Threads API 연결 테스트\n\n이것은 테스트 게시물입니다.\n\n#테스트 #API #Threads"
    
    print(f"게시 내용:\n{test_content}")
    print("\n📡 게시 시도 중...")
    
    try:
        # Threads API 게시 엔드포인트 (실제 API가 공개되면 업데이트 필요)
        url = "https://www.threads.net/api/v1/media/configure/"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        payload = {
            "text": test_content,
            "user_id": user_id
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 게시 성공!")
            try:
                data = response.json()
                print(f"응답: {json.dumps(data, indent=2)}")
            except:
                print(f"응답: {response.text}")
            return True
        else:
            print(f"❌ 게시 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 게시 테스트 오류: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🧪 Threads API 통신 테스트")
    print("=" * 50)
    
    # 연결 테스트
    connection_ok = test_threads_api_connection()
    
    if connection_ok:
        # 게시 테스트
        test_simple_post()
    
    print("\n" + "=" * 50)
    print("테스트 완료!")

if __name__ == "__main__":
    main() 