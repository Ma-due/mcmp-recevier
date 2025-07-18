from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.organizations_api import OrganizationsApi
import json

def get_organization_info(api_key_auth, app_key_auth, account_id):
    """
    Datadog API를 사용하여 조직 정보를 가져오는 함수
    
    Args:
        api_key_auth (str): Datadog API 키
        app_key_auth (str): Datadog Application 키
        account_id (str): 조직의 public_id
    
    Returns:
        dict: 조직 정보 또는 None (오류 발생시)
    """
    # 설정
    configuration = Configuration()
    configuration.api_key['apiKeyAuth'] = api_key_auth
    configuration.api_key['appKeyAuth'] = app_key_auth
    
    # OrganizationsApi.get_org() 호출 (public_id 전달)
    with ApiClient(configuration) as api_client:
        api_instance = OrganizationsApi(api_client)
        try:
            response = api_instance.get_org(public_id=account_id)
            return response
        except Exception as e:
            print(f"조직 정보 조회 오류 ({account_id}): {e}")
            return None