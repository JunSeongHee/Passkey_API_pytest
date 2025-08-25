import json, requests, base64
from util.customLogger import LogGen
from util import jsonUtil

class controlClient:
    logger = LogGen.loggen()

    def get_clientid_api(baseUrl, client_auth, clientid):
        url = f"{baseUrl}/admin/v1/clients/{clientid}"
        headers = {
            'Authorization': f'Basic {client_auth}',
        }

        response = requests.request("GET", url, headers=headers)
        return response.status_code

    def create_client_api(baseUrl, client_auth, clientid, name, scopes: list, client_secret_expires_in_seconds = None, content_type: str = 'application/json;charset=UTF-8'):
        url = f"{baseUrl}/admin/v1/clients"
        payload = {
            "clientId": clientid,
            "scopes": scopes
        }
        headers = {
            'Authorization': f'Basic {client_auth}',
            'Content-Type': content_type
        }
        if client_secret_expires_in_seconds is not None:
            payload["clientSecretExpiresInSeconds"] = client_secret_expires_in_seconds

        response = requests.request("POST", url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                body = response.json()

                # clientId와 clientSecret 추출 및 저장
                clientId = body["data"]["client"]["clientId"]
                clientSecret = body["data"]["client"]["clientSecret"]

                re_credentials = f"{clientId}:{clientSecret}"
                client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
                jsonUtil.writeJson('client', 'clientId', clientId)
                jsonUtil.writeJson('client', 'clientSecret', clientSecret)
                jsonUtil.writeJson('client', 'client_encoded_credentials', client_encoded_credentials)
                
                print(f"[DEBUG] clientId 저장됨: {clientId}")
                print(f"[DEBUG] clientSecret 저장됨: {clientSecret}")
                print(f"[DEBUG] encoded_credentials 저장됨: {client_encoded_credentials}")
                '''
                scope_set = set(scopes)

                if scope_set == {"passkey:rp"}:
                    jsonUtil.writeJson('client', 'rp_clientId', clientId)
                    jsonUtil.writeJson('client', 'rp_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'rp_client_encoded_credentials', client_encoded_credentials)

                elif scope_set == {"passkey:rp:migration"}:
                    jsonUtil.writeJson('client', 'migration_clientId', clientId)
                    jsonUtil.writeJson('client', 'migration_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'migration_client_encoded_credentials', client_encoded_credentials)

                elif scope_set == {"passkey:rp", "passkey:rp:migration"}:
                    jsonUtil.writeJson('client', 'rp_migration_clientId', clientId)
                    jsonUtil.writeJson('client', 'rp_migration_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'rp_migration_client_encoded_credentials', client_encoded_credentials)
                '''
            except Exception as e:
                print(f"[❌] 응답 파싱 오류: {e}")
                return 500, f"Response parsing failed: {e}"

        return response.status_code, response.text

    def create_naver_client_api(baseUrl, client_auth, clientid, name, scopes: list, client_secret_expires_in_seconds = None, content_type: str = 'application/json;charset=UTF-8'):
        url = f"{baseUrl}/admin/v1/clients"
        payload = {
            "clientId": clientid,
            "scopes": scopes
        }
        headers = {
            'Authorization': f'Basic {client_auth}',
            'Content-Type': content_type
        }
        if client_secret_expires_in_seconds is not None:
            payload["clientSecretExpiresInSeconds"] = client_secret_expires_in_seconds

        response = requests.request("POST", url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                body = response.json()

                # clientId와 clientSecret 추출 및 저장
                clientId = body["data"]["client"]["clientId"]
                clientSecret = body["data"]["client"]["clientSecret"]

                re_credentials = f"{clientId}:{clientSecret}"
                client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
                jsonUtil.writeJson('naver', 'clientId', clientId)
                jsonUtil.writeJson('naver', 'clientSecret', clientSecret)
                jsonUtil.writeJson('naver', 'client_encoded_credentials', client_encoded_credentials)
                print(f"[DEBUG] clientId 저장됨: {clientId}")
                print(f"[DEBUG] clientSecret 저장됨: {clientSecret}")
                print(f"[DEBUG] encoded_credentials 저장됨: {client_encoded_credentials}")
                '''
                scope_set = set(scopes)

                if scope_set == {"passkey:rp"}:
                    jsonUtil.writeJson('client', 'rp_clientId', clientId)
                    jsonUtil.writeJson('client', 'rp_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'rp_client_encoded_credentials', client_encoded_credentials)

                elif scope_set == {"passkey:rp:migration"}:
                    jsonUtil.writeJson('client', 'migration_clientId', clientId)
                    jsonUtil.writeJson('client', 'migration_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'migration_client_encoded_credentials', client_encoded_credentials)

                elif scope_set == {"passkey:rp", "passkey:rp:migration"}:
                    jsonUtil.writeJson('client', 'rp_migration_clientId', clientId)
                    jsonUtil.writeJson('client', 'rp_migration_clientSecret', clientSecret)
                    jsonUtil.writeJson('client', 'rp_migration_client_encoded_credentials', client_encoded_credentials)
                '''
            except Exception as e:
                print(f"[❌] 응답 파싱 오류: {e}")
                return 500, f"Response parsing failed: {e}"

        return response.status_code, response.text

    def delete_client_api(baseUrl, client_auth, clientid):
        url = f"{baseUrl}/admin/v1/clients/{clientid}"
        headers = {
            'Authorization': f'Basic {client_auth}'
        }
        response = requests.request("DELETE", url, headers=headers)
        return response.status_code, response.text


    def update_client_admin_scopes_api(base_url, client_auth: str, clientid: str):
        scopes = ["passkey:admin"]
        url = f"{base_url}/admin/v1/clients/{clientid}/scopes"

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": "application/json;charset=UTF-8"
        }
        body = {
            "scopes": scopes
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(body)
        )
        return response.status_code

    def update_client_re_scopes_api(base_url, client_auth: str, clientid: str):
        scopes = ["passkey:rp"]
        url = f"{base_url}/admin/v1/clients/{clientid}/scopes"

        # base64 인코딩

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": "application/json;charset=UTF-8"
        }
        body = {
            "scopes": scopes
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(body)
        )
        return response.status_code


    def update_client_migration_scopes_api(base_url, client_auth: str, clientid: str):
        scopes = ["passkey:rp:migration"]
        url = f"{base_url}/admin/v1/clients/{clientid}/scopes"

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": "application/json;charset=UTF-8"
        }
        body = {
            "scopes": scopes
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(body)
        )
        return response.status_code

    def update_client_rp_migration_scopes_api(base_url, client_auth: str, clientid: str):
        scopes = ["passkey:rp:migration", "passkey:rp"]
        url = f"{base_url}/admin/v1/clients/{clientid}/scopes"

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": "application/json;charset=UTF-8"
        }
        body = {
            "scopes": scopes
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(body)
        )
        return response.status_code

    def update_client_no_scopes_api(base_url, client_auth: str, clientid: str):
        scopes = None
        url = f"{base_url}/admin/v1/clients/{clientid}/scopes"

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": "application/json;charset=UTF-8"
        }
        body = {
            "scopes": scopes
        }
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(body)
        )

        return response.status_code






