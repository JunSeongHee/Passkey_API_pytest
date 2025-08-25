import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def check_rpid_add_possibility_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        method: str = 'GET',
        space_yes: bool = False
):
    params = { 'rpId': rpId }
    base_url = f"{base_url}/admin/v1/rps/check-availability"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}'

        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }
    response = requests.request(method, base_url, headers=headers, params=params)
    return response.status_code, response.text

def check_rpid_add_possibility_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        method: str = 'GET'
):
    params = {}
    base_url = f"{base_url}/admin/v1/rps/check-availability"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}'
    }
    response = requests.request(method, base_url, headers=headers, params=params)
    return response.status_code, response.text

class Test_check_rpid_add_possibility:
    logger = LogGen.loggen()

    ############### base URL
    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id')
    client_secret = readConfig.getValue('basic Info', 'client_secret')
    client_url = readConfig.getValue('basic Info', 'client_url')
    client_name = readConfig.getValue('Admin Info', 'client_name')
    no_exist_clientId = readConfig.getValue('Admin Info', 'no_exist_clientId')
    new_rpId = readConfig.getValue('Admin Info', 'new_rpId') # nhis.or.kr
    # admin 권한 base64 인코딩
    admin_credentials = f"{admin_client_id}:{admin_client_secret}"
    admin_encoded_credentials = base64.b64encode(admin_credentials.encode("utf-8")).decode("utf-8")

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

    def test_check_rpid_add_possibility_001(self):
        self.logger.info("#001 요청한 RP ID가 사용 (또는 등록) 가능한 RP ID 임을 확인")

        response_code, response_text = check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.new_rpId)
        check_response_code = 200

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data, data.id 필드가 있는지 확인
            assert "id" in body
            assert "data" in body

            data = body["data"]

            # id, data, data.rpId 필드가 있는지 확인
            assert "id" in body
            assert "data" in body
            assert "rpId" in body["data"]
            assert "available" in body["data"]

            assert body["data"]["rpId"] == self.new_rpId
            assert isinstance(body["data"]["available"], bool), "available은 bool 타입이어야 함"
            assert body["data"]["available"] is True, "등록 가능한 RP ID여야 하므로 available 값은 True여야 함"


            #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info(f"🟢 {self.new_rpId} 는 등록이 가능합니다.")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

    def test_check_rpid_add_possibility_002(self):
        self.logger.info("#002 요청한 RP ID가 사용 (또는 등록) 불가능한 RP ID 임을 확인")

        response_code, response_text = check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        check_response_code = 200

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data, data.id 필드가 있는지 확인
            assert "id" in body
            assert "data" in body

            data = body["data"]

            # id, data, data.rpId 필드가 있는지 확인
            assert "id" in body
            assert "data" in body
            assert "rpId" in body["data"]
            assert "available" in body["data"]

            assert body["data"]["rpId"] == self.client_id

            assert isinstance(body["data"]["available"], bool), "available은 bool 타입이어야 함"
            assert body["data"]["available"] is False, "등록 불가능한 RP ID여야 하므로 available 값은 False여야 함"

            #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info(f"🔴 {self.rpId} 는 이미 존재하거나 등록이 불가능합니다.")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

    def test_check_rpid_add_possibility_003(self):
        self.logger.info("#003 rpId 누락 - 400 에러 반환 확인")
        response_code, response_text = check_rpid_add_possibility_no_rpid_api(self.bUrl, self.admin_encoded_credentials)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_004(self):
        self.logger.info("#004 rpId "" 전송 - 400 에러 반환 확인")
        response_code, response_text = check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, "")

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_005(self):
        self.logger.info("#005 rpId " " 공백 전송 - 400 에러 반환 확인")
        response_code, response_text = check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, " ")

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_006(self):
        self.logger.info("#006 POST 요청")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_007(self):
        self.logger.info("#007 PUT 요청")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_008(self):
        self.logger.info("#008 HEAD 요청")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_009(self):
        self.logger.info("#009 OPTIONS 요청")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_013(self):
        self.logger.info("#013 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_014(self):
        self.logger.info("#014 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, space_yes=True
        )

        check_response_code = 401 # 403 아닐까?

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_rpid_add_possibility_015(self):
        self.logger.info("#015 헤더에 [(client id:client secret) 인코딩 값] 오입력")
        response_code, response_text = check_rpid_add_possibility_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

