import json, requests, base64


class createCredential:

    ############### Registration API (create Credential) - 등록 옵션 요청
    def registration_api(baseUrl, displayName, name, encoded_id, token, client_id):
        url = f"{baseUrl}/v1/registration/request"
        payload = ("{\n"
                   "    \"authenticatorSelection\": {\n"
                   "        \"authenticatorAttachment\": \"cross-platform\",\n"
                   "        \"residentKey\": \"required\",\n"
                   "        \"userVerification\": \"required\"\n"
                   "    },\n"
                   "    \"attestation\": \"direct\",\n"
                   "    \"user\": {\n"
                   f"        \"displayName\": \"{displayName}\",\n"
                   f"        \"name\": \"{name}\",\n"
                   f"        \"id\": \"{encoded_id}\"\n"
                   "    },\n"
                   "    \"timeout\": 200000,\n"
                   "    \"excludeCredentials\": true\n"
                   "}")
        headers = {
            'Authorization': f'{token}',
            'X-WebAuthentication-RpId': f'{client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code, response.text

    ############### Registration API (create Credential) - 등록 결과 전송
    def registration_api_response(baseUrl, transactionId, clientDataJson, attestationObject, userId, token, client_id):
        url = f"{baseUrl}/v1/registration/response"
        payload = ("{\n"
                   f"    \"transactionId\": \"{transactionId}\",\n"
                   "    \"publicKeyCredential\": {\n"
                   "        \"response\": {\n"
                   f"            \"clientDataJSON\": \"{clientDataJson}\",\n"
                   f"            \"attestationObject\": \"{attestationObject}\"\n"
                   "        },\n"
                   f"        \"rawId\": \"{userId}\",\n"
                   f"        \"id\": \"{userId}\",\n"
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
