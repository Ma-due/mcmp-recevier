from dotenv import load_dotenv
import os
from csp import get_csp_accounts
from org import get_organization_info
import json

# 환경변수 로드 (한 번만)
load_dotenv()

# Cloud Supply Codes 설정 (필요에 따라 수정)
CLOUD_SUPPLY_CODES = {
    "DATADOG": ["11"],
    "AWS": ["04"],
    "AZURE": ["05", "07"],
}

def get_auth_credentials():
    """
    환경변수에서 인증 정보를 가져오는 함수
    
    Returns:
        tuple: (username, password) 또는 (None, None) if 실패
    """
    username = os.getenv("MCMP_USERNAME")
    password = os.getenv("MCMP_PASSWORD")
    
    if not username or not password:
        print("인증 정보가 없습니다.")
        exit(0)
        return None, None
    
    return username, password

