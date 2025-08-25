import json, requests, base64, time
from util.customLogger import LogGen
from util import jsonUtil

class controlRPID:

    def check_rpid_add_possibility_api(baseUrl, client_auth, rpId) -> bool:
        url = f"{baseUrl}/admin/v1/rps/check-availability"
        params = { 'rpId': rpId }
        headers = {
            'Authorization': f'Basic {client_auth}'
        }

        response = requests.request("GET", url, headers=headers, params=params)
        if response.status_code == 200:
            body = json.loads(response.text)
            return body["data"].get("available", False)
        return False

    def get_specific_rpid_info_api(baseUrl, client_auth, rpid):
        url = f"{baseUrl}/admin/v1/rps/{rpid}"

        headers = {
            'Authorization': f'Basic {client_auth}'
        }

        response = requests.request('GET', url, headers=headers)
        return response.status_code

    def create_rpId_api(baseUrl, client_auth, rpid, name, registrationEnabled, authenticationEnabled, origins, policy, content_type: str = 'application/json;charset=UTF-8'):
        url = f"{baseUrl}/admin/v1/rps"
        payload = {
            "id": rpid,
            "name": name,
            "registrationEnabled": registrationEnabled,
            "authenticationEnabled": authenticationEnabled,
            "origins": origins,
            "policy": policy
        }
        headers = {
            'Authorization': f'Basic {client_auth}',
            'Content-Type': content_type
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        return response.status_code, response.text

    def delete_rpId_api(baseUrl, client_auth, rpId):
        url = f"{baseUrl}/admin/v1/rps/{rpId}"
        headers = {
            'Authorization': f'Basic {client_auth}'
        }
        response = requests.request("DELETE", url, headers=headers)
        return response.status_code, response.text

    def get_rp_origins_list_api(baseUrl, client_auth, rpId):
        url = f"{baseUrl}/admin/v1/rps/{rpId}/origins"

        headers = {
            'Authorization': f'Basic {client_auth}'
        }
        response = requests.request("GET", url, headers=headers)
        return response.text

    def delete_origin_api(baseUrl, client_auth, rpId, origin):
        url = f"{baseUrl}/admin/v1/rps/{rpId}/origins"
        params = {
            "origin": origin
        }

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": 'application/json;charset=UTF-8',
        }
        response = requests.request("DELETE", url, headers=headers, params=params)
        return response.status_code, response.text

    def check_origin_add_possibility_api(baseUrl, client_auth, rpId, origin):
        params = { 'origin': origin }
        url = f"{baseUrl}/admin/v1/rps/{rpId}/origins/check-acceptability"
        headers = {
            'Authorization': f'Basic {client_auth}'
        }
        response = requests.request('GET', url, headers=headers, params=params)
        if response.status_code == 200:
            body = json.loads(response.text)
            return body["data"].get("acceptable", False)
        return False

    def get_rp_credentials_api(baseUrl, client_auth, rpId):
        logger = LogGen.loggen()

        url = f"{baseUrl}/admin/v1/rps/{rpId}/credentials"
        headers = {
            'Authorization': f'Basic {client_auth}'
        }
        params = {}
        response = requests.request("GET", url, headers=headers, params=params)

        if response.status_code == 200:
            try:
                body = response.json()

                assert "id" in body, "응답에 id 없음"
                assert "data" in body, "응답에 data 없음"
                data = body["data"]

                # content 리스트 검증 (존재할 경우)
                assert "content" in data, "data에 content 없음"
                content = data["content"]
                assert isinstance(content, list), "content는 리스트여야 함"
                # 조회된 credential이 있다면 몇가지 필드 예시 검증 (없어도 에러 아님)
                if content:
                    rpids = [cred["rpId"] for cred in content if "rpId" in cred]
                    rpid_count = len(rpids)
                    logger.info(f"credential 갯수 : {rpid_count}")
                    jsonUtil.writeJson('credential_user', 'userId', content[0]["userId"])
                    jsonUtil.writeJson('credential_user', 'credentialId', content[0]["credentialId"])
                    jsonUtil.writeJson('credential_user', 'aaguid', content[0]["aaguid"])
            except Exception as e:
                assert False, "응답 구조가 올바르지 않음"

        return response.status_code

    def add_origin_api(baseUrl, client_auth, rpId, origin):
        url = f"{baseUrl}/admin/v1/rps/{rpId}/origins"
        payload = {
            "origin": origin
        }

        headers = {
            'Authorization': f'Basic {client_auth}',
            "Content-Type": 'application/json;charset=UTF-8',
        }
        response = requests.request("POST", url, headers=headers, json=payload)
        return response.status_code, response.text