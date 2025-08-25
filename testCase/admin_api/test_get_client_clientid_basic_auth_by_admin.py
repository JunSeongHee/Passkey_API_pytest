import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_auth_client_clientid_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    method: str = "GET",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }

    response = requests.request(method, url, headers=headers)
    return response.status_code, response.text

def get_auth_client_clientid_no_clientid_api(
    base_url: str,
    admin_encoded_credentials,
    method: str = "GET",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }

    response = requests.request(method, url, headers=headers)
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

        # 필수 필드
        for field in ["clientId", "scopes", "clientSecretCreatedAt"]:
            assert field in client, f"client에 {field} 없음"
        assert isinstance(client["clientId"], str) and client["clientId"].strip(), "clientId는 빈 문자열/공백 불가"
        assert isinstance(client["scopes"], list), "scopes는 리스트여야 함"
        assert isinstance(client["clientSecretCreatedAt"], str), "clientSecretCreatedAt은 문자열(RFC3339)이어야 함"

        # clientSecretExpiresInSeconds (옵셔널, 있으면 검증)
        if "clientSecretExpiresInSeconds" in client:
            assert isinstance(client["clientSecretExpiresInSeconds"], int) and client["clientSecretExpiresInSeconds"] > 0, "clientSecretExpiresInSeconds는 양수 int"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_get_auth_client_clientid:
    logger = LogGen.loggen()

    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id') # naver.com
    client_name = readConfig.getValue('Admin Info', 'client_name') # naver_rp_test_inc_mig
    client_secret = readConfig.getValue('Admin Info', 'client_secret')
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

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_get_auth_client_clientid_001(self):
        self.logger.info("#001 Client Id 로 등록된 Client 조회")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId
        )

        response_assertion(self, response_code, response_text)

    def test_get_auth_client_clientid_002(self):
        self.logger.info("#002 Client Id - 필수 파라미터 값 누락")

        response_code, response_text = get_auth_client_clientid_no_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_003(self):
        self.logger.info("#003 미존재하는 client id 전송(400 에러)")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            "testtest123.com"
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_004(self):
        self.logger.info("#004 client id " " 공백 전송(400 에러)")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            " "
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_005(self):
        self.logger.info("#005 POST 요청")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_006(self):
        self.logger.info("#006 PUT 요청")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_007(self):
        self.logger.info("#007 PATCH 요청")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_get_auth_client_clientid_008(self):
        self.logger.info("#008 HEAD 요청")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_009(self):
        self.logger.info("#009 OPTIONS 요청")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_get_auth_client_clientid_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_013(self):
        self.logger.info("#013 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        self.logger.info(f"self.client_encoded_credentials = {self.client_encoded_credentials}")
        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_get_auth_client_clientid_014(self):
        self.logger.info("#014 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            space_yes=True
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_auth_client_clientid_015(self):
        self.logger.info("#015 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = get_auth_client_clientid_api(
            self.bUrl,
            self.wrong_client_encoded_credentials,
            self.rpId
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False