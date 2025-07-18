import requests
import os
from dotenv import load_dotenv

def get_datadog_key(username, password):
    """
    CloudZ API를 사용하여 Datadog 계정 정보를 가져오는 함수
    
    Args:
        username (str): Basic Auth 사용자명
        password (str): Basic Auth 비밀번호
    
    Returns:
        list: Datadog 계정 정보 리스트 또는 None (오류 발생시)
              각 항목은 accountId, apiKey, accessKey, customerId 포함
    """
    try:
        # API 요청
        url = f"https://bizapi.cloudz.co.kr/account/csp/getAllDatadogAccountInfoList"
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # HTTP 오류 체크
        
        # JSON 응답 파싱
        data = response.json()
        
        # API 응답 코드 확인
        result_code = data.get('result', {}).get('code')
        if result_code == '0000':
            datadog_api_list = data.get('datadogApiInfoList', [])
            
            # 필요한 필드만 추출
            filtered_accounts = []
            for account in datadog_api_list:
                filtered_account = {
                    'accountId': account.get('accountId', ''),
                    'apiKey': account.get('apiKey', ''),
                    'accessKey': account.get('accessKey', ''),
                    'customerId': account.get('customerId', '')
                }
                filtered_accounts.append(filtered_account)
            
            print(f"Datadog 계정 {len(filtered_accounts)}개 조회 성공")
            return filtered_accounts
            
        else:
            print(f"API 오류 ({result_code}) - {data.get('result', {}).get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return None

# 이전 함수명과의 호환성을 위한 alias
def get_csp_accounts(username, password, cloud_supply_codes):
    """
    기존 호환성을 위한 함수 - customer_relationship 모듈의 build_customer_relationships 호출
    """
    from customer_relationship import build_customer_relationships
    return build_customer_relationships(username, password, cloud_supply_codes)

if __name__ == "__main__":
    load_dotenv()

    username = os.getenv("MCMP_USERNAME")
    password = os.getenv("MCMP_PASSWORD")

    if not username or not password:
        print("오류: MCMP_USERNAME과 MCMP_PASSWORD 환경 변수를 설정해주세요.")
        exit(1)

    # Datadog 계정 정보 조회
    accounts = get_datadog_key(username, password)
    
    if accounts:
        print(f"\n=== 조회된 Datadog 계정 정보 ===")
        for i, account in enumerate(accounts, 1):
            print(f"{i}. Customer ID: {account['customerId']}")
            print(f"   Account ID: {account['accountId']}")
            print(f"   API Key: {account['apiKey']}")
            print(f"   Access Key: {account['accessKey']}")
            print()
    else:
        print("Datadog 계정 정보를 가져올 수 없습니다.")
    


    