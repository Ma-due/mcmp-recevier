import requests
import os
from dotenv import load_dotenv


def get_azure_info(username, password):

    url = "https://bizapi.cloudz.co.kr/account/csp/getAllAccountInfoList?cloudSupplyCode=07"

    response = requests.get(url, auth=(username, password))
    data = response.json()

    csp_account_list = data.get('cspAccountInfoList', [])

    for csp_account in csp_account_list:
        master_check = False
        customer_info = csp_account.get('customerInfo', {})
        customer_id = customer_info.get('customerId', '')
        customer_name = customer_info.get('customerName', '')
        user_info_list = csp_account.get('userInfoList', [])

        for user_info in user_info_list:
            if user_info.get('userType', '') == 'master':
                master_check = True
                break
            
        if not master_check:
            print(f"Customer ID: {customer_id}, Customer Name: {customer_name}, ### not in master ### userLen : {len(user_info_list)}")
            
            
        

if __name__ == "__main__":
    load_dotenv()
    
    username = os.getenv("MCMP_USERNAME")
    password = os.getenv("MCMP_PASSWORD")
    get_azure_info(username, password)