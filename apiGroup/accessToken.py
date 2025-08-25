import requests


class AccessToken:

    ############## access token 발급 받기
    def issue_admin_access_token(encoded_credentials: str):
        url = "https://idp.stg-passkey.com/oauth2/token"

        payload = 'grant_type=client_credentials&scope=passkey%3Aadmin passkey%3Arp'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': f'Basic {encoded_credentials}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_code = response.status_code
        access_token = response.json().get("access_token")
        token_type = response.json().get("token_type")

        token = f'{token_type} {access_token}'
        return response_code, token
    
    def issue_access_token(encoded_credentials: str):
        url = "https://idp.stg-passkey.com/oauth2/token"

        payload = 'grant_type=client_credentials&scope=passkey%3Arp'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': f'Basic {encoded_credentials}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_code = response.status_code
        access_token = response.json().get("access_token")
        token_type = response.json().get("token_type")

        token = f'{token_type} {access_token}'
        return response_code, token

    # scope = migration
    def issue_migration_access_token(encoded_credentials: str):
        url = "https://idp.stg-passkey.com/oauth2/token"

        payload = 'grant_type=client_credentials&scope=passkey%3Arp%3Amigration'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': f'Basic {encoded_credentials}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_code = response.status_code
        access_token = response.json().get("access_token")
        token_type = response.json().get("token_type")

        token = f'{token_type} {access_token}'
        return response_code, token

    # scope = rp + migration
    def issue_rp_and_migration_access_token(encoded_credentials: str):
        url = "https://idp.stg-passkey.com/oauth2/token"

        payload = 'grant_type=client_credentials&scope=passkey%3Arp passkey%3Arp%3Amigration'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': f'Basic {encoded_credentials}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_code = response.status_code
        access_token = response.json().get("access_token")
        token_type = response.json().get("token_type")

        token = f'{token_type} {access_token}'
        return response_code, token

    # scope = 공백
    def issue_blank_space_scope_access_token(encoded_credentials: str):
        url = "https://idp.stg-passkey.com/oauth2/token"

        payload = 'grant_type=client_credentials&scope= '
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': f'Basic {encoded_credentials}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_code = response.status_code
        access_token = response.json().get("access_token")
        token_type = response.json().get("token_type")

        token = f'{token_type} {access_token}'
        return response_code, token
