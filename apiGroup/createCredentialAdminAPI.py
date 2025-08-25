import json, requests, base64
import time, random

from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util.readProperties import readConfig
from util.get_publicKeyCredential import publickeyCredential
from util.customLogger import LogGen
from util import jsonUtil

class user_server_api:
    logger = LogGen.loggen()

    bUrl = readConfig.getValue('Admin Info', 'bUrl')

    # RP 이름과 비밀번호, RP URL
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')
    # admin 권한 base64 인코딩
    admin_credentials = f"{admin_client_id}:{admin_client_secret}"
    admin_encoded_credentials = base64.b64encode(admin_credentials.encode("utf-8")).decode("utf-8")

    client_id = readConfig.getValue('Admin Info', 'client_id') # naver.com
    client_name = readConfig.getValue('Admin Info', 'client_name') # naver

    registrationEnabled = jsonUtil.readJson('naver', 'registrationEnabled')
    authenticationEnabled = jsonUtil.readJson('naver', 'authenticationEnabled')
    origins = jsonUtil.readJson('naver', 'origins')
    policy = jsonUtil.readJson('naver', 'policy')

    res1=controlRPID.get_specific_rpid_info_api(bUrl, admin_encoded_credentials, client_id)
    logger.info(f"res1 {res1}")
    #rp 부터 먼저 생성해야 함
    if not res1 == 200:#not controlRPID.get_specific_rpid_info_api(bUrl, admin_encoded_credentials, client_id) == 200:
        controlRPID.create_rpId_api(bUrl, admin_encoded_credentials, client_id, client_name, registrationEnabled=True, authenticationEnabled=True, origins=origins, policy=policy)

    res = controlClient.get_clientid_api(bUrl, admin_encoded_credentials, client_id)

    #rp 생성 후, client 생성
    if not res==200:#not controlClient.get_clientid_api(bUrl, admin_encoded_credentials, client_id) == 200:
        logger.info(f"clientid get 200 아니므로 client 생성 - {res}")
        controlClient.create_naver_client_api(bUrl, admin_encoded_credentials, client_id, client_name, [ "passkey:rp" ])
    else:
        logger.info(f"clientid get 200 이므로 client 삭제 후 다시 생성 - {res}")
        controlClient.delete_client_api(bUrl, admin_encoded_credentials, client_id)
        time.sleep(2)
        controlClient.create_naver_client_api(bUrl, admin_encoded_credentials, client_id, client_name, [ "passkey:rp" ])

    #client_secret = readConfig.getValue('Admin Info', 'client_secret') # naver.com 의 secret
    #res1 = controlClient.update_client_re_scopes_api(bUrl, admin_encoded_credentials, client_id)
    #logger.info(f"client scope passkey:rp, udpate - {res1}")
    client_secret = jsonUtil.readJson('naver', 'clientSecret')
    #client_secret = readConfig.getValue('Admin Info', 'client_secret')
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    logger.info(f"client_id - {client_id}, secret - {client_secret}, encoded_credentials - {encoded_credentials}")

    # 사용자 이름
    displayName = readConfig.getValue('Admin Info', 'displayName') + str(random.randrange(100, 1000))
    name = readConfig.getValue('Admin Info', 'name')
    id = f"{displayName}:{name}"
    encoded_id = base64.b64encode(id.encode("utf-8")).decode("utf-8").rstrip("=")

    ############### Registration API (create Credential) - 등록 옵션 요청
    @classmethod
    def registration_api(cls):
        cls.logger.info(f"registration_api Start - user id(displayName) : {cls.displayName}, user name : {cls.name}")
        url = f"{cls.bUrl}/v1/registration/request"
        payload = ("{\n"
                   "    \"authenticatorSelection\": {\n"
                   "        \"authenticatorAttachment\": \"platform\",\n"
                   "        \"residentKey\": \"required\",\n"
                   "        \"userVerification\": \"required\"\n"
                   "    },\n"
                   "    \"attestation\": \"none\",\n"
                   "    \"user\": {\n"
                   f"        \"displayName\": \"{cls.displayName}\",\n"
                   f"        \"name\": \"{cls.name}\",\n"
                   f"        \"id\": \"{cls.encoded_id}\"\n"
                   "    },\n"
                   "    \"timeout\": 200000,\n"
                   "    \"excludeCredentials\": true\n"
                   "}")

        headers = {
            'Authorization': f'Basic {cls.encoded_credentials}',
            'X-WebAuthentication-RpId': f'{cls.client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        cls.logger.info("\n [등록 옵션 요청 Response]")
        cls.logger.info(f"[✅] response status code: {response.status_code}")
        cls.logger.info(f"response: {response.text}")
        response_json = json.loads(response.text)
        jsonUtil.writeJson("data", "transactionId", response_json["data"]["transactionId"])
        global options
        options = response_json["data"]["options"]

        cls.logger.info(f"options: {options}")
        json_paylaod = json.dumps(payload)
        cls.logger.info(f"request body - {json_paylaod}")

    ############### JAR API SERVER로 options를 보내서 publickKey Credential을 생성함
    @classmethod
    def create_publickeyCredential(cls):
        cls.logger.info("create_publickeyCredential Start")
        result = publickeyCredential.credentialCreate(options)
        cls.logger.info(f"create_publickeyCredential reuslt : {result}")
        jsonUtil.writeJson("data", "userId", result["id"])
        jsonUtil.writeJson("data", "clientDataJSON", result["response"]["clientDataJSON"])
        jsonUtil.writeJson("data","attestationObject", result["response"]["attestationObject"])
        time.sleep(1)

    ############### Registration API (create Credential) - 등록 결과 전송
    @classmethod
    def registration_api_response(cls):
        cls.logger.info("registration_api_response Start")
        transactionId = jsonUtil.readJson("data", "transactionId")
        clientDataJSON = jsonUtil.readJson("data", "clientDataJSON")
        attestationObject = jsonUtil.readJson("data", "attestationObject")
        userId = jsonUtil.readJson("data", "userId")

        url = f"{cls.bUrl}/v1/registration/response"
        payload = ("{\n"
                   f"    \"transactionId\": \"{transactionId}\",\n"
                   "    \"publicKeyCredential\": {\n"
                   "        \"response\": {\n"
                   f"            \"clientDataJSON\": \"{clientDataJSON}\",\n"
                   f"            \"attestationObject\": \"{attestationObject}\"\n"
                   "        },\n"
                   f"        \"rawId\": \"{userId}\",\n"
                   f"        \"id\": \"{userId}\",\n"
                   "        \"type\": \"public-key\"\n"
                   "    }\n"
                   "}")
        headers = {
            'Authorization': f'Basic {cls.encoded_credentials}',
            'X-WebAuthentication-RpId': f'{cls.client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        cls.logger.info("\n [등록 결과 전송 Response]")
        cls.logger.info(f"[✅] response status code: {response.status_code}")
        cls.logger.info(f"response: {response.text}")
        jsonUtil.writeJson("data", "credentialId", json.loads(response.text)["data"]["authenticator"]["credentialId"])
        jsonUtil.writeJson("data", "userId", json.loads(response.text)["data"]["userId"])

    ############### Authentication API (Use Credential)- 인증 옵션 요청
    @classmethod
    def authentication_api(cls):
        cls.logger.info("authentication_api Start")
        url = f"{cls.bUrl}/v1/authentication/request"
        userId = jsonUtil.readJson('data', 'userId')
        payload = ("{\n"
                   f"    \"userId\": \"{userId}\",\n"
                   "    \"timeout\": 200000,\n"
                   "    \"userVerification\": \"required\"\n"
                   "}")
        headers = {
            'Authorization': f'Basic {cls.encoded_credentials}',
            'X-WebAuthentication-RpId': f'{cls.client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        cls.logger.info("\n [인증 옵션 요청 Response]")
        cls.logger.info(f"[✅] response status code: {response.status_code}")
        cls.logger.info(f"response: {response.text}")
        response_json = json.loads(response.text)
        jsonUtil.writeJson('data', "auth_transactionId", response_json["data"]["transactionId"])
        jsonUtil.writeJson('data', "assertionOptions", response_json["data"]["options"])

    @classmethod
    def get_publickeyCredential(cls):
        cls.logger.info("get_publickeyCredential Start")
        assertionOptions = jsonUtil.readJson("data", "assertionOptions")
        cls.logger.info(f"assetionOptions: {assertionOptions}")
        auth_result = publickeyCredential.credentialGet(assertionOptions)
        cls.logger.info(f"assetionOptions auth_result : {auth_result}")
        jsonUtil.writeJson("data", "clientDataJson_auth", auth_result["response"]["clientDataJSON"])
        jsonUtil.writeJson("data", "authenticatorData", auth_result["response"]["authenticatorData"])
        jsonUtil.writeJson("data", "signature", auth_result["response"]["signature"])
        jsonUtil.writeJson("data", "userHandle", auth_result["response"]["userHandle"])
        jsonUtil.writeJson("data", "credentialId", auth_result["id"])
        time.sleep(1)

    @classmethod
    ############### Authentication API (Use Credential)- 인증 결과 전송
    def authentication_api_response(cls):
        cls.logger.info("authentication_api_response Start")
        transactionId = jsonUtil.readJson("data", "auth_transactionId")
        clientDataJson = jsonUtil.readJson("data", "clientDataJson_auth")
        authenticatorData  =jsonUtil.readJson("data", "authenticatorData")
        signature = jsonUtil.readJson("data", "signature")
        userHandle = jsonUtil.readJson("data", "userHandle")
        credentialId = jsonUtil.readJson("data", "credentialId")

        url = f"{cls.bUrl}/v1/authentication/response"
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
            'Authorization': f'Basic {cls.encoded_credentials}',
            'X-WebAuthentication-RpId': f'{cls.client_id}',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        cls.logger.info("\n [인증 결과 요청 Response]")
        cls.logger.info(f"[✅] response status code: {response.status_code}")
        cls.logger.info(f"response: {response.text}")

    @classmethod
    def b64url_decode(cls, data):
        cls.logger.info("b64url_decode Start")
        rem = len(data) % 4
        if rem > 0:
            data += '=' * (4 - rem)
        return base64.urlsafe_b64decode(data.encode('utf-8'))

# server_api.registration_api()
# server_api.create_publickeyCredential()
# server_api.registration_api_response()
# time.sleep(3)
# server_api.authentication_api()
# server_api.get_publickeyCredential()
# server_api.authentication_api_response()
