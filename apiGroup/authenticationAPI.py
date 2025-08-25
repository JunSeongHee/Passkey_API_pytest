import json, requests, base64


class useCredential:

    ############### Authentication API (Use Credential)- 인증 옵션 요청
    def authentication_api(baseUrl, userId, token, client_id):
        url = f"{baseUrl}/v1/authentication/request"
        payload = ("{\n"
                   f"    \"userId\": \"{userId}\",\n"
                   "    \"timeout\": 200000,\n"
                   "    \"userVerification\": \"required\"\n"
                   "}")
        headers = {
            'Authorization': f'{token}',
            'X-WebAuthentication-RpId': f'{client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code, response.text

    ############### Authentication API (Use Credential)- 인증 결과 전송
    def authentication_api_response(baseUrl, transactionId, authenticatorData, clientDataJson, signature, userHandle, credentialId, token, client_id):
        url = f"{baseUrl}/v1/authentication/response"
        payload = ("{\n"
                   f"    \"transactionId\": \"{transactionId}\",\n"
                   "    \"publicKeyCredential\": {\n"
                   "        \"response\": {\n"
                   f"            \"clientDataJSON\": \"{clientDataJson}\",\n"
                   f"            \"authenticatorData\": \"{authenticatorData}\",\n"
                   f"            \"signature\": \"{signature}\",\n"
                   f"            \"userHandle\": \"{userHandle}\"\n"
                   "        },\n"
                   f"        \"rawId\": \"{credentialId}\",\n"
                   f"        \"id\": \"{credentialId}\",\n"
                   "        \"type\": \"public-key\"\n"
                   "    }\n"
                   "}")
        headers = {
            'Authorization': f'{token}',
            'X-WebAuthentication-RpId': f'{client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code, response.text