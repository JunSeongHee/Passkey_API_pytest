import base64, json, pytest, requests, math

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_auth_client_secret_lifetime_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    clientSecretExpiresInSeconds: int = None,
    method: str = "PATCH",
    content_type = "application/json;charset=UTF-8",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}/secret-lifetime"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": content_type
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": content_type
        }

    body = {
        "clientSecretExpiresInSeconds": clientSecretExpiresInSeconds
    }
    response = requests.request(
        method, url, headers=headers, data=json.dumps(body)
    )
    return response.status_code, response.text

def update_auth_client_secret_lifetime_custom_payload_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    payload,
    method: str = "PATCH",
    content_type = "application/json;charset=UTF-8",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}/secret-lifetime"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": content_type
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": content_type
        }

    response = requests.request(
        method, url, headers=headers, data=json.dumps(payload)
    )
    return response.status_code, response.text

def update_auth_client_secret_lifetime_no_clientid_api(
    base_url: str,
    admin_encoded_credentials,
    clientSecretExpiresInSeconds: int = None,
    method: str = "PATCH",
    content_type = "application/json;charset=UTF-8",
):
    url = f"{base_url}/admin/v1/clients//secret-lifetime"
    headers = {
        'Authorization': f'Basic{admin_encoded_credentials}',
        "Content-Type": content_type
    }

    body = {
        "clientSecretExpiresInSeconds": clientSecretExpiresInSeconds
    }
    response = requests.request(
        method, url, headers=headers, data=json.dumps(body)
    )
    return response.status_code, response.text

def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"
        body = json.loads(response_text)

        # id 필수
        assert "id" in body and body["id"], "응답에 id 없음 또는 빈 값"

        # data 객체 필수
        assert "data" in body and isinstance(body["data"], dict), "응답에 data 없음 또는 객체 아님"
        data = body["data"]

        # client 객체 필수
        assert "client" in data and isinstance(data["client"], dict), "data에 client 없음 또는 객체 아님"
        client = data["client"]

        # 필수 필드 체크
        assert client["clientId"] == self.rpId, "clientId 값 불일치"
        assert isinstance(client["scopes"], list), "scopes 리스트여야 함"
        assert isinstance(client["clientSecretCreatedAt"], str), "clientSecretCreatedAt은 RFC3339 문자열"
        if "clientSecretExpiresInSeconds" in client:
            if client["clientSecretExpiresInSeconds"] is not None:
                assert client["clientSecretExpiresInSeconds"] == self.clientSecretExpiresInSeconds, "만료기간 값 불일치"
        else:
            self.logger.info("ℹ️ clientSecretExpiresInSeconds 키가 존재하지 않음 (null 처리된 상태로 간주)")

        #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_update_auth_client_secret_lifetime:
    logger = LogGen.loggen()

    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id')
    client_secret = readConfig.getValue('basic Info', 'client_secret')
    client_url = readConfig.getValue('basic Info', 'client_url')
    client_name = readConfig.getValue('Admin Info', 'client_name') # naver_rp_test_inc_mig
    no_exist_clientId = readConfig.getValue('Admin Info', 'no_exist_clientId')
    # admin 권한 base64 인코딩
    admin_credentials = f"{admin_client_id}:{admin_client_secret}"
    admin_encoded_credentials = base64.b64encode(admin_credentials.encode("utf-8")).decode("utf-8")

    clientSecretExpiresInSeconds = 2592000  # 30일 ,604800 - 7일

    rp_scope = jsonUtil.readJson('client', 'rp_scope')
    rpId = jsonUtil.readJson("create_rpid", "id")
    name = jsonUtil.readJson("create_rpid", "name")
    registrationEnabled = jsonUtil.readJson("create_rpid", "registrationEnabled")
    authenticationEnabled = jsonUtil.readJson("create_rpid", "authenticationEnabled")
    origins = jsonUtil.readJson("create_rpid", "origins")
    policy = jsonUtil.readJson("create_rpid", "policy")

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_update_auth_client_secret_lifetime_001(self):
        self.logger.info("#001 Client Secret 만료 기간 업데이트")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )

        response_assertion(self, response_code, response_text)

    def test_update_auth_client_secret_lifetime_002(self):
        self.logger.info("#002 clientSecretExpiresInSeconds 없이 전송")

        payload = {}

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_auth_client_secret_lifetime_003(self):
        self.logger.info("#003 clientSecretExpiresInSeconds Null 전송")

        payload = { "clientSecretExpiresInSeconds" : None }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        self.logger.info(f"response_code - {response_code}, response_text - {response_text}")
        response_assertion(self, response_code, response_text)

    def test_update_auth_client_secret_lifetime_004(self):
        self.logger.info("#004 client id 누락(400 에러)")

        response_code, response_text = update_auth_client_secret_lifetime_no_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_005(self):
        self.logger.info("#005 미존재하는 client id 전송(400 에러)")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.no_exist_clientId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_006(self):
        self.logger.info("#006 clientId : " " 공백 전송(400 에러)")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            client_id=" ",
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_007(self):
        self.logger.info("#007 GET 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="GET"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_008(self):
        self.logger.info("#008 POST 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_009(self):
        self.logger.info("#009 PUT 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_010(self):
        self.logger.info("#010 DELETE 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_011(self):
        self.logger.info("#011 HEAD 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="HEAD"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_012(self):
        self.logger.info("#012 OPTIONS 요청")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_013(self):
        self.logger.info("#013 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            content_type="application/gzip"
        )
        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_014(self):
        self.logger.info("#014 admin 아닌 권한 - passkey:rp")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.rp_scope)

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 403 # 401 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_update_auth_client_secret_lifetime_015(self):
        self.logger.info("#015 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 403 # 401 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_016(self):
        self.logger.info("#016 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 403 # 401 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_017(self):
        self.logger.info("#017 Client 권한 : 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 403 # 401 오고 있음

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_018(self):
        self.logger.info("#018 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds,
            space_yes=True
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_019(self):
        self.logger.info("#019 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_auth_client_secret_lifetime_api(
            self.bUrl,
            self.wrong_client_encoded_credentials,
            self.rpId,
            clientSecretExpiresInSeconds=self.clientSecretExpiresInSeconds
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_020(self):
        self.logger.info("#020 clientSecretExpiresInSeconds - 잘못된 타입(문자열) 전송")

        payload = { "clientSecretExpiresInSeconds" : "1000000" }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_021(self):
        self.logger.info("#021 clientSecretExpiresInSeconds - 잘못된 타입(배열) 전송")

        payload = { "clientSecretExpiresInSeconds" : [] }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_022(self):
        self.logger.info("#022 clientSecretExpiresInSeconds - 0 유효하지 않은 값 전송")

        payload = { "clientSecretExpiresInSeconds" : 0 }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_023(self):
        self.logger.info("#023 clientSecretExpiresInSeconds - 0 유효하지 않은 값 전송")

        payload = { "clientSecretExpiresInSeconds" : -10000 }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_secret_lifetime_024(self):
        self.logger.info("#024 clientSecretExpiresInSeconds NaN 유효하지 않은 값 전송")

        payload = { "clientSecretExpiresInSeconds" : math.nan }

        response_code, response_text = update_auth_client_secret_lifetime_custom_payload_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            payload=payload
        )
        check_response_code = 400 # 200 전송 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False




