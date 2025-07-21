import requests
import os
from dotenv import load_dotenv
import pandas as pd
import json

class Customer:
    def __init__(self, customer_id, customer_name, parent_customer_id, parent_customer_name):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.parent_customer_id = parent_customer_id
        self.parent_customer_name = parent_customer_name
        self.children = []
        self.depth = 0

        

def get_all_customers(username, password, cloud_supply_codes):
    """
    여러 클라우드 서비스 코드에서 모든 고객 정보 수집
    
    Args:
        cloud_supply_codes: 클라우드 서비스 코드 리스트 (예: ["04", "05", "07", "11"])
    """
    all_customers = {}
    
    for code in cloud_supply_codes:
        print(f"CloudSupplyCode {code} 처리 중...")
        
        url = f"https://bizapi.cloudz.co.kr/account/csp/getAllAccountInfoList?cloudSupplyCode={code}"
        
        try:
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()
            data = response.json()

            if data.get('result', {}).get('code') == '0000':
                csp_account_list = []
                csp_account_list = data.get('cspAccountInfoList', [])
                print(f"  - {len(csp_account_list)}개 계정 발견")
                
                for csp_account in csp_account_list:
                    # customerInfo는 중첩 객체 안에 있음
                    customer_info = csp_account.get('customerInfo', {})
                    customer = Customer(
                        customer_info.get('customerId', ''), 
                        customer_info.get('customerName', ''), 
                        customer_info.get('parentCustomerId', ''),
                        customer_info.get('parentCustomerName', '')
                    )
                    all_customers[customer.customer_id] = customer
            else:
                print(f"  - API 오류: {data.get('result', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  - 요청 오류: {e}")

    return all_customers if all_customers else None

def get_all_customers_datadog(username, password, cloud_supply_codes):
    url = f"https://bizapi.cloudz.co.kr/account/csp/getAllDatadogAccountInfoList"
    
    response = requests.get(url, auth=(username, password))
    data = response.json()

    if data.get('result').get('code') == '0000':
        return data.get('cspAccountInfoList', [])
    else:
        print(data.get('result').get('message'))
        return None

    return data

def get_customer_info(username, password, customer_id):
    url = f"https://bizapi.cloudz.co.kr/account/getCustomerInfo?customerId={customer_id}"
    
    response = requests.get(url, auth=(username, password))
    data = response.json()

    if data.get('result').get('code') == '0000':
        return data.get('customerInfo', [])
    else:
        return None

    
    return data

def customer_chain(all_customers, username, password):
    check_list = set()  # 전체에서 공유할 check_list
    
    
    for customer in list(all_customers.values()):  # ✅ 리스트로 복사해서 순회
        recursive_customer_info(all_customers, customer, username, password, check_list)
    
    print(f"=== 처리 완료 ===")
    print(f"처리된 고객 목록: {len(all_customers)}")
    return all_customers

def recursive_customer_info(all_customers, customer, username, password, check_list):
    # 이미 처리된 고객이면 건너뛰기
    if customer.customer_id in check_list:
        return
    
    # 고객 정보 조회
    customer_data = get_customer_info(username, password, customer.customer_id)
    
    # API 호출 실패하거나 result가 0000이 아니면 루트 부모로 판단   
    if not customer_data:
        check_list.add(customer.customer_id)
        customer.depth = 1
        return
    
    if not customer.parent_customer_id or customer.parent_customer_id.strip() == '':
        customer.parent_customer_id = customer_data.get('parentCustomerId', '')
        customer.parent_customer_name = customer_data.get('parentCustomerName', '')
        
    parent_customer = all_customers.get(customer.parent_customer_id)
    if not parent_customer:
        parent_customer = Customer(customer.parent_customer_id, customer.parent_customer_name, '', '')
        all_customers[customer.parent_customer_id] = parent_customer
    
    # 부모를 먼저 재귀 처리
    recursive_customer_info(all_customers, parent_customer, username, password, check_list)
    
    # 부모의 자식 목록에 현재 고객 추가
    if customer.customer_id not in parent_customer.children:
        parent_customer.children.append(customer.customer_id)
        customer.depth = parent_customer.depth + 1
        check_list.add(customer.customer_id)


def chain_to_json(all_customers):
    """
    고객 계층 구조를 customerId를 키로 하는 JSON으로 변환
    depth 1 (최상위 부모)를 건너뛰고 depth 2부터 시작
    { "customerId": {"name": "고객명", "children": [...]} }
    """
    def build_children_array(customer_id):
        """재귀적으로 자식들의 배열을 구성"""
        customer = all_customers.get(customer_id)
        if not customer or not customer.children:
            return []
        
        children_array = []
        for child_id in customer.children:
            child = all_customers.get(child_id)
            if child:
                child_obj = {
                    "customer_id": child.customer_id,
                    "name": child.customer_name,
                    "children": build_children_array(child_id)
                }
                children_array.append(child_obj)
        
        return children_array
    
    # depth 2 고객들을 최상위로 설정 (depth 1은 건너뛰기)
    depth_2_customers = [customer for customer in all_customers.values() if customer.depth == 2]
    
    result = {}
    for customer in depth_2_customers:
        result[customer.customer_id] = {
            "name": customer.customer_name,
            "children": build_children_array(customer.customer_id)
        }
    
    return result

if __name__ == "__main__":
    # 환경 변수 로드
    load_dotenv()
    
    username = os.getenv("MCMP_USERNAME")
    password = os.getenv("MCMP_PASSWORD")
    
    if not username or not password:
        print("오류: MCMP_USERNAME과 MCMP_PASSWORD 환경 변수를 설정해주세요.")
        exit(1)

    # 모든 클라우드 서비스의 고객 관계 구성
    cloud_supply_codes = ["04", "05", "07", "11"]  # AWS, Azure, Azure, Datadog
    all_customers = get_all_customers(username, password, cloud_supply_codes)

    if all_customers:
        # 계층 구조 구축
        chain_result = customer_chain(all_customers, username, password)
        
        # JSON 변환
        json_result = chain_to_json(chain_result)
        
        # JSON 파일로 저장
        with open("customer_hierarchy.json", "w", encoding="utf-8") as f:
            json.dump(json_result, f, ensure_ascii=False, indent=2)
                
        print(f"\nJSON 파일 저장: customer_hierarchy.json")
    else:
        print("고객 데이터를 가져올 수 없습니다.")
    