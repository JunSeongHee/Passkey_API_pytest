import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def delete_client_basic_auth_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    method: str = "DELETE",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',

        }

    response = requests.request(method, url, headers=headers)
    return response.status_code, response.text

def delete_client_basic_auth_no_clientid_api(
    base_url: str,
    admin_encoded_credentials,
    method: str = "DELETE"
):
    url = f"{base_url}/admin/v1/clients/"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
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

        # clientId 필수
        assert "clientId" in data and data["clientId"], "data에 clientId 없음 또는 빈 값"
        assert data["clientId"] == self.rpId, "clientId 값 불일치"

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

class Test_delete_client_basic_auth:
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

    rp_scope = jsonUtil.readJson('client', 'rp_scope')
    no_exist_client = jsonUtil.readJson('client', 'no_exist_client')

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

    def test_delete_client_basic_auth_001(self):
        self.logger.info("#001 등록된 Client 삭제 요청")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, scopes=self.rp_scope)

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId
        )

        response_assertion(self, response_code, response_text)

    def test_delete_client_basic_auth_002(self):
        self.logger.info("#002 clientid 미기입 시 404 에러 반환 확인")
        response_code, response_text = delete_client_basic_auth_no_clientid_api(
            self.bUrl, self.admin_encoded_credentials
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_client_basic_auth_003(self):
        self.logger.info("#003 존재하지 않는 clientId - 404 에러 반환 확인")
        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_client
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_client_basic_auth_004(self):
        self.logger.info("#004 clientId - "" 전송(404 에러)")
        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl, self.admin_encoded_credentials, client_id=""
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_client_basic_auth_005(self):
        self.logger.info("#005 clientId - " " 공백 전송(400 에러)")
        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl, self.admin_encoded_credentials, client_id=" "
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")

            assert False

    def test_delete_client_basic_auth_006(self):
        self.logger.info("#006 POST 요청")

        response_code, response_text = delete_client_basic_auth_api(
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

    def test_delete_client_basic_auth_007(self):
        self.logger.info("#007 PUT 요청")

        response_code, response_text = delete_client_basic_auth_api(
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

    def test_delete_client_basic_auth_008(self):
        self.logger.info("#008 PATCH 요청")

        response_code, response_text = delete_client_basic_auth_api(
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

    def test_delete_client_basic_auth_009(self):
        self.logger.info("#009 OPTIONS 요청")

        response_code, response_text = delete_client_basic_auth_api(
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

    def test_create_rpid_info_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, clientid=self.rpId, name=self.name, scopes=self.rp_scope)

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"
        self.logger.info(f"scope update - {update_result}")

        get_re_credentials(self)
        # self.clientid = jsonUtil.readJson('client', 'clientId')
        # self.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        # self.logger.info(f"self.clientid {self.clientid}, self.clientsecret - {self.clientsecret}")

        # re_credentials = f"{self.clientid}:{self.clientsecret}"
        # self.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 응답 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_create_rpid_info_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"
        self.logger.info(f"scope update - {update_result}")

        get_re_credentials(self)

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 응답 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_create_rpid_info_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"
        self.logger.info(f"scope update - {update_result}")

        get_re_credentials(self)

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 #401 응답 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_create_rpid_info_013(self):
        self.logger.info("#013 Client 권한 : 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"
        self.logger.info(f"scope update - {update_result}")

        get_re_credentials(self)

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId
        )
        check_response_code = 403 # 401 응답 옮

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_create_rpid_info_014(self):
        self.logger.info("#014 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = delete_client_basic_auth_api(
            self.bUrl,
            self.client_encoded_credentials,
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

    def test_create_rpid_info_015(self):
        self.logger.info("#015 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = delete_client_basic_auth_api(
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