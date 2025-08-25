import base64, json, pytest, requests, math


from apiGroup.controlclientAPI import controlClient

from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def register_basic_auth_client_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    scopes: list = None,
    client_secret_expires_in_seconds: int = None,
    method: str = "POST",
    content_type: str = "application/json;charset=UTF-8",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": content_type,
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": content_type,
        }
    data = {
        "clientId": client_id,
        "scopes": scopes
    }
    if client_secret_expires_in_seconds is not None:
        data["clientSecretExpiresInSeconds"] = client_secret_expires_in_seconds

    response = requests.request(method, url, headers=headers, data=json.dumps(data))
    return response.status_code, response.text

def register_basic_auth_client_custom_payload_api(
    base_url: str,
    admin_encoded_credentials,
    payload,
    method: str = "POST",
    content_type: str = "application/json;charset=UTF-8",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": content_type,
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": content_type,
        }

    response = requests.request(method, url, headers=headers, data=json.dumps(payload))
    return response.status_code, response.text

def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"
        body = json.loads(response_text)

        assert "id" in body and isinstance(body["id"], str) and body["id"].strip(), "응답에 'id' 없음 또는 빈 문자열"

        # data 필수
        assert "data" in body and isinstance(body["data"], dict), "'data' 필드 없음 또는 객체 아님"
        data = body["data"]

        # client 객체 필수
        assert "client" in data and isinstance(data["client"], dict), "'client' 필드 없음 또는 객체 아님"
        client = data["client"]

        # clientId 검증
        assert "clientId" in client and isinstance(client["clientId"], str) and client["clientId"].strip(), "clientId 없음 또는 빈 문자열"
        assert client["clientId"] == self.rpId, f"clientId 불일치: {client['clientId']} != {self.rpId}"
        clientId = client["clientId"]
        jsonUtil.writeJson('client', 'clientId', clientId)
        # clientSecret 검증
        assert "clientSecret" in client and isinstance(client["clientSecret"], str) and client["clientSecret"].strip(), "clientSecret 없음 또는 빈 문자열"
        clientSecret = client["clientSecret"]
        jsonUtil.writeJson('client', 'clientSecret', clientSecret)

        if "scopes" in client:
            assert "scopes" in client and isinstance(client["scopes"], list), "scopes 필드 없음 또는 리스트 아님"
            assert all(isinstance(scope, str) for scope in client["scopes"]), "scopes 항목은 문자열이어야 함"

        # clientSecretCreatedAt 검증 (RFC 3339 형식)
        assert "clientSecretCreatedAt" in client and isinstance(client["clientSecretCreatedAt"], str), "clientSecretCreatedAt 없음 또는 문자열 아님"

        # clientSecretExpiresInSeconds (선택적 필드)
        if "clientSecretExpiresInSeconds" in client:
            expires = client["clientSecretExpiresInSeconds"]
            assert isinstance(expires, (int, float)) and expires > 0, "clientSecretExpiresInSeconds는 양수여야 함"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

def get_re_credentials(self):
    self.clientid = jsonUtil.readJson('client', 'clientId')
    self.clientsecret = jsonUtil.readJson('client', 'clientSecret')

    self.logger.info(f"self.clientid {self.clientid}, cls.clientsecret - {self.clientsecret}")

    re_credentials = f"{self.clientid}:{self.clientsecret}"
    self.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")

class Test_register_basic_auth_client:
    logger = LogGen.loggen()

    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id') # naver.com
    client_name = readConfig.getValue('Admin Info', 'client_name') # naver_rp_test_inc_mig
    # admin 권한 base64 인코딩
    admin_credentials = f"{admin_client_id}:{admin_client_secret}"
    admin_encoded_credentials = base64.b64encode(admin_credentials.encode("utf-8")).decode("utf-8")

    rp_scope = jsonUtil.readJson('client', 'rp_scope')
    rpId = jsonUtil.readJson("create_rpid", "id")
    name = jsonUtil.readJson("create_rpid", "name")
    registrationEnabled = jsonUtil.readJson("create_rpid", "registrationEnabled")
    authenticationEnabled = jsonUtil.readJson("create_rpid", "authenticationEnabled")
    origins = jsonUtil.readJson("create_rpid", "origins")
    policy = jsonUtil.readJson("create_rpid", "policy")
    client_secret_expires_in_seconds = 2592000  # 30일 ,604800 - 7일

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_register_basic_auth_client_001(self):
        self.logger.info("#001 신규 Client 정보 등록 (Basic Authentication)")

        if controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.delete_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            self.client_secret_expires_in_seconds
        )

        response_assertion(self, response_code, response_text)

    def test_register_basic_auth_client_002(self):
        self.logger.info("#002 신규 Client 정보 등록 (Basic Authentication) - clientSecretExpiresInSeconds 누락(200 전송)")

        if controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.delete_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope
        )

        response_assertion(self, response_code, response_text)

    def test_register_basic_auth_client_003(self):
        self.logger.info("#003 신규 Client 정보 등록 (Basic Authentication) - scopes 누락(200 전송)")

        if controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.delete_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=self.client_secret_expires_in_seconds
        )

        response_assertion(self, response_code, response_text)

    def test_register_basic_auth_client_004(self):
        self.logger.info("#004 PUT 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_register_basic_auth_client_005(self):
        self.logger.info("#005 PATCH 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_register_basic_auth_client_006(self):
        self.logger.info("#006 DELETE 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_register_basic_auth_client_007(self):
        self.logger.info("#007 DELETE 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_register_basic_auth_client_008(self):
        self.logger.info("#008 HEAD 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_register_basic_auth_client_009(self):
        self.logger.info("#009 OPTIONS 요청")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_010(self):
        self.logger.info("#010 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
            content_type="application/gzip"
        )
        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.rp_scope)

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"
        self.logger.info(f"update_result - {update_result}, self.client_encoded_credentials - {self.client_encoded_credentials}")

        get_re_credentials(self)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_scope
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답이 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_create_rpid_info_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        get_re_credentials(self)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_scope
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답이 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_013(self):
        self.logger.info("#013 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        get_re_credentials(self)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답이 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_014(self):
        self.logger.info("#014 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        get_re_credentials(self)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_scope
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답이 옮

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_015(self):
        self.logger.info("#015 Basic + [(client id:client secret) 인코딩 값] 사이 공백")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope,
            space_yes=True
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_016(self):
        self.logger.info("#016 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.wrong_client_encoded_credentials,
            self.rpId,
            self.rp_scope,
            #self.client_secret_expires_in_second
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_017(self):
        self.logger.info("#017 존재하는 client id 전송(400 에러)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, scopes=self.rp_scope)

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_018(self):
        self.logger.info("#018 client id 누락(400 에러)")

        payload = {}

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_019(self):
        self.logger.info("#019 client id Null 전송(400 에러)")

        payload = {
            "clientId" : None
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_create_rpid_info_020(self):
        self.logger.info("#020 clientId : "" 전송(400 에러)")

        payload = {
            "clientId" : ""
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_021(self):
        self.logger.info("#021 clientId : " " 공백 전송(400 에러)")

        payload = {
            "clientId" : " "
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_022(self):
        self.logger.info("#022 clientId : 도메인 포맷이 아닌 값으로 전송, not a domain(400 에러)")

        payload = {
            "clientId" : "not a domain"
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_023(self):
        self.logger.info("#023 clientId : 도메인 포맷이 아닌 값으로 전송, not a domain(400 에러)")

        payload = {
            "clientId" : "https://playwright"
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400 # http나 https 같은 protocol 정보 없어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_024(self):
        self.logger.info("#024 clientId : 123 잘못된 타입으로 전송(400 에러)")

        payload = {
            "clientId" : 123
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_025(self):
        self.logger.info("#025 clientId :  잘못된 타입으로 전송- 배열(400 에러)")

        payload = {
            "clientId" : ["test.com"]
        }

        response_code, response_text = register_basic_auth_client_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_026(self):
        self.logger.info("#026 clientSecretExpiresInSeconds : 0, 유효하지 않은 값(400 에러)")

        client_secret_expires_in_seconds = 0
        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=client_secret_expires_in_seconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_027(self):
        self.logger.info("#027 clientSecretExpiresInSeconds : -1000, 유효하지 않은 값(400 에러)")

        client_secret_expires_in_seconds = -1000
        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=client_secret_expires_in_seconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_028(self):
        self.logger.info("#028 clientSecretExpiresInSeconds : NaN, 유효하지 않은 값(400 에러)")

        client_secret_expires_in_seconds =  math.nan
        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=client_secret_expires_in_seconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_029(self):
        self.logger.info("#029 clientSecretExpiresInSeconds : 문자열 잘못된 타입(400 에러)")

        client_secret_expires_in_seconds =  "2592000"
        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=client_secret_expires_in_seconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_030(self):
        self.logger.info("#030 clientSecretExpiresInSeconds : 문자열 잘못된 타입(400 에러)")

        client_secret_expires_in_seconds =  math.nan

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            client_secret_expires_in_seconds=client_secret_expires_in_seconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_031(self):
        self.logger.info("#031 scopes : 빈 배열(400 에러)")

        scope = []

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_032(self):
        self.logger.info("#032 scopes : [" "] 공백 입력(400 에러)")

        scope = [ " " ]

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_033(self):
        self.logger.info("#033 scopes : 타입 오류(400 에러)")

        scope = "passkey:admin"

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_034(self):
        self.logger.info("#034 scopes : [invalid:scope] 미존재하는 권한 전송(400 에러)")

        scope =  ["invalid:scope"]

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_create_rpid_info_035(self):
        self.logger.info("#035 scopes : 중복 권한 전송(400 에러)")

        scope =  ["passkey:rp", "passkey:rp"]

        response_code, response_text = register_basic_auth_client_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False





