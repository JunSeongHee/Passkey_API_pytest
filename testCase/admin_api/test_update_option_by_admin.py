import base64, json, pytest, requests, os

from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_rp_option_api(
    base_url: str,
    admin_encoded_credentials,
    rpId: str,
    creationAuthenticatorAttachment=None,
    creationResidentKey=None,
    creationUserVerification=None,
    creationTimeoutInMs=None,
    creationTimeoutForUvDiscouragedInMs=None,
    requestUserVerification=None,
    requestTimeoutInMs=None,
    requestTimeoutForUvDiscouragedInMs=None,
    method: str = 'PUT',
    content_type: str = 'application/json;charset=UTF-8',
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/rps/{rpId}/defaultOptions"
    # 값이 있는 필드만 payload에 포함
    payload = {}
    if creationAuthenticatorAttachment is not None:
        payload["creationAuthenticatorAttachment"] = creationAuthenticatorAttachment
    if creationResidentKey is not None:
        payload["creationResidentKey"] = creationResidentKey
    if creationUserVerification is not None:
        payload["creationUserVerification"] = creationUserVerification
    if creationTimeoutInMs is not None:
        payload["creationTimeoutInMs"] = creationTimeoutInMs
    if creationTimeoutForUvDiscouragedInMs is not None:
        payload["creationTimeoutForUvDiscouragedInMs"] = creationTimeoutForUvDiscouragedInMs
    if requestUserVerification is not None:
        payload["requestUserVerification"] = requestUserVerification
    if requestTimeoutInMs is not None:
        payload["requestTimeoutInMs"] = requestTimeoutInMs
    if requestTimeoutForUvDiscouragedInMs is not None:
        payload["requestTimeoutForUvDiscouragedInMs"] = requestTimeoutForUvDiscouragedInMs

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
    response = requests.request(method, url, headers=headers, json=payload)
    return response.status_code, response.text

def update_rp_option_custom_payload_api(
    base_url: str,
    admin_encoded_credentials,
    rpId: str,
    payload,
    method: str = 'PUT',
    content_type: str = 'application/json;charset=UTF-8'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/defaultOptions"
    # 값이 있는 필드만 payload에 포함

    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, url, headers=headers, json=payload)
    return response.status_code, response.text

def update_rp_option_no_rpid_api(
    base_url: str,
    admin_encoded_credentials,
    creationAuthenticatorAttachment=None,
    creationResidentKey=None,
    creationUserVerification=None,
    creationTimeoutInMs=None,
    creationTimeoutForUvDiscouragedInMs=None,
    requestUserVerification=None,
    requestTimeoutInMs=None,
    requestTimeoutForUvDiscouragedInMs=None,
    method: str = 'PUT',
    content_type: str = 'application/json;charset=UTF-8'
):
    url = f"{base_url}/admin/v1/rps//defaultOptions"
    # 값이 있는 필드만 payload에 포함
    payload = {}
    if creationAuthenticatorAttachment is not None:
        payload["creationAuthenticatorAttachment"] = creationAuthenticatorAttachment
    if creationResidentKey is not None:
        payload["creationResidentKey"] = creationResidentKey
    if creationUserVerification is not None:
        payload["creationUserVerification"] = creationUserVerification
    if creationTimeoutInMs is not None:
        payload["creationTimeoutInMs"] = creationTimeoutInMs
    if creationTimeoutForUvDiscouragedInMs is not None:
        payload["creationTimeoutForUvDiscouragedInMs"] = creationTimeoutForUvDiscouragedInMs
    if requestUserVerification is not None:
        payload["requestUserVerification"] = requestUserVerification
    if requestTimeoutInMs is not None:
        payload["requestTimeoutInMs"] = requestTimeoutInMs
    if requestTimeoutForUvDiscouragedInMs is not None:
        payload["requestTimeoutForUvDiscouragedInMs"] = requestTimeoutForUvDiscouragedInMs

    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, url, headers=headers, json=payload)
    return response.status_code, response.text

def load_options_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} 파일이 존재하지 않습니다.")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 파일 구조가 {"id": "...", "data": {...}} 라면 body["data"]만 추출
    return data.get("data", data)  # 혹시 data만 필요하다면

def response_assertion(self, response_code:str, response_text:str):
    try:
        assert response_code == 200, f"❌ Status code is {response_code} not 200"
        body = json.loads(response_text)
        assert "id" in body and body["id"], "응답에 id 없음"
        assert "data" in body, "응답에 data 없음"
        assert "rpId" in body["data"] and body["data"]["rpId"] == self.rpId, "rpId 불일치 또는 없음"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")

    except FileNotFoundError as e:
        self.logger.error(f"❌ 옵션 파일 없음: {e}, response_text = {response_text}")
        print(f"❌ 옵션 파일 없음: {e}")
        assert False, str(e)

    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e}, response_text = {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)

    except Exception as e:
        self.logger.error(f"❌ 예외 발생: {e}, response_text = {response_text}")
        assert False, f"예외 발생: {e}"


class Test_update_rp_option:
    logger = LogGen.loggen()
    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id')
    client_secret = readConfig.getValue('Admin Info', 'client_secret')
    client_url = readConfig.getValue('basic Info', 'client_url')
    client_name = readConfig.getValue('Admin Info', 'client_name') # naver_rp_test_inc_mig
    no_exist_clientId = readConfig.getValue('Admin Info', 'no_exist_clientId')
    # admin 권한 base64 인코딩
    admin_credentials = f"{admin_client_id}:{admin_client_secret}"
    admin_encoded_credentials = base64.b64encode(admin_credentials.encode("utf-8")).decode("utf-8")

    no_exist_rpId = readConfig.getValue('Admin Info', 'no_exist_clientId')

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

    def test_update_rp_option_001(self):
        self.logger.info("#001 RP Default Option 갱신 - 모두 파라미터 갱신(200 전송)")

        res = controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if not res == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, scopes=self.rp_scope)

        res1 = controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        if not res1 == 200:
            controlRPID.create_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy)


        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment="platform",
            creationResidentKey="required",
            creationUserVerification="required",
            creationTimeoutInMs=1200000,
            creationTimeoutForUvDiscouragedInMs=800000,
            requestUserVerification="required",
            requestTimeoutInMs=1300000,
            requestTimeoutForUvDiscouragedInMs=900000
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_002(self):
        self.logger.info("#002 RP Default Option 갱신 - 모든 옵션 파라미터 누락 시 200 전송")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_003(self):
        self.logger.info("#003 RP Default Option 갱신 - 다양한 옵션 전송1(200 전송)")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment="cross-platform",
            creationResidentKey="preferred",
            creationUserVerification="required",
            creationTimeoutInMs=600000,
            requestUserVerification="required",
            requestTimeoutInMs=500000
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_004(self):
        self.logger.info("#004 RP Default Option 갱신 - 다양한 옵션 전송2")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationResidentKey="discouraged",
            creationUserVerification="preferred",
            creationTimeoutInMs=400000,
            requestUserVerification="preferred",
            requestTimeoutInMs=300000
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_005(self):
        self.logger.info("#005 RP Default Option 갱신 - 다양한 옵션 전송3")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification="discouraged",
            creationTimeoutForUvDiscouragedInMs=200000,
            requestUserVerification="discouraged",
            requestTimeoutForUvDiscouragedInMs=100000
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_006(self):
        self.logger.info("#006 RP Default Option 갱신 - creationUserVerification 값이 required 일 때 creationTimeoutForUvDiscouragedInMs 전송(200 전송)")

        payload = {
            "creationUserVerification": "required",
            "creationTimeoutForUvDiscouragedInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_007(self):
        self.logger.info("#007 RP Default Option 갱신 - creationUserVerification 값이 preferred 일 때 creationTimeoutForUvDiscouragedInMs 전송(200 전송)")

        payload = {
            "creationUserVerification": "preferred",
            "creationTimeoutForUvDiscouragedInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_008(self):
        self.logger.info("#008 RP Default Option 갱신 - creationUserVerification 값이 discouraged 일 때 creationTimeoutInMs 전송(200 전송)")

        payload = {
            "creationUserVerification": "discouraged",
            "creationTimeoutInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_009(self):
        self.logger.info("#009 RP Default Option 갱신 - requestUserVerification 값이 required 일 때 requestTimeoutForUvDiscouragedInMs 전송(200 전송)")

        payload = {
            "requestUserVerification": "required",
            "requestTimeoutForUvDiscouragedInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_010(self):
        self.logger.info("#010 RP Default Option 갱신 - requestUserVerification 값이 preferred 일 때 requestTimeoutForUvDiscouragedInMs 전송(200 전송)")

        payload = {
            "requestUserVerification": "preferred",
            "requestTimeoutForUvDiscouragedInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_011(self):
        self.logger.info("#011 RP Default Option 갱신 - requestUserVerification 값이 discouraged 일 때 requestTimeoutInMs 전송(200 전송)")

        payload = {
            "requestUserVerification": "discouraged",
            "requestTimeoutInMs" : 800000,
        }
        response_code, response_text = update_rp_option_custom_payload_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, payload=payload
        )

        response_assertion(self, response_code, response_text)

    def test_update_rp_option_012(self):
        self.logger.info("#012 rpId 미기입 - 404 에러 반환 확인")
        response_code, response_text = update_rp_option_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials,
            creationUserVerification="required",
            creationTimeoutInMs=1200000,
            requestUserVerification="required",
            requestTimeoutInMs=1300000,
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_013(self):
        self.logger.info("#013 미존재 rpId 전송 - 400 에러 반환 확인")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_rpId,
            creationUserVerification="required",
            creationTimeoutInMs=1200000,
            requestUserVerification="required",
            requestTimeoutInMs=1300000,
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_014(self):
        self.logger.info("#014 rpId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, " "
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_015(self):
        self.logger.info("#015 POST 요청")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_016(self):
        self.logger.info("#016 PATCH 요청")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_017(self):
        self.logger.info("#017 HEAD 요청")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_018(self):
        self.logger.info("#018 OPTIONS 요청")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_019(self):
        self.logger.info("#019 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            content_type="application/gzip"
        )

        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_020(self):
        self.logger.info("#020 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_021(self):
        self.logger.info("#021 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_022(self):
        self.logger.info("#022 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_023(self):
        self.logger.info("#023 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rp_option_api(
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

    def test_update_rp_option_024(self):
        self.logger.info("#024 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, space_yes=True
        )

        check_response_code = 401 # 403이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_025(self):
        self.logger.info("#025 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_rp_option_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_026(self):
        self.logger.info("#026 creationAuthenticatorAttachment - enum 에 없는 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment="device"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_027(self):
        self.logger.info("#027 creationAuthenticatorAttachment - 대소문자 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment="Platform"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rp_option_028(self):
        self.logger.info("#028 creationAuthenticatorAttachment - 잘못된 타입(int) 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment= 10
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_029(self):
        self.logger.info("#029 creationAuthenticatorAttachment - " " 공백 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationAuthenticatorAttachment= " "
        )

        check_response_code = 400 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_030(self):
        self.logger.info("#030 creationResidentKey - enum 에 없는 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationResidentKey="device"
        )

        check_response_code = 400 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_031(self):
        self.logger.info("#031 creationResidentKey - 대소문자 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationResidentKey="Discouraged"
        )

        check_response_code = 400 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_032(self):
        self.logger.info("#032 creationResidentKey - 잘못된 타입(int) 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationResidentKey= 10
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_033(self):
        self.logger.info("#033 creationResidentKey - " " 공백 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationResidentKey= " "
        )

        check_response_code = 400 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_034(self):
        self.logger.info("#034 creationUserVerification - enum 에 없는 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification="device",
            creationTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_035(self):
        self.logger.info("#035 creationUserVerification - 대소문자 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification="Preferred",
            creationTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_036(self):
        self.logger.info("#036 creationUserVerification - 잘못된 타입(int) 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= 10,
            creationTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_037(self):
        self.logger.info("#037 creationUserVerification - " " 공백 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= " ",
            creationTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_038(self):
        self.logger.info("#038 creationTimeoutInMs - 음수 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "required",
            creationTimeoutInMs= -1000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_039(self):
        self.logger.info("#039 creationTimeoutInMs - 잘못된 타입(str) 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "preferred",
            creationTimeoutInMs= "300000"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_040(self):
        self.logger.info("#040 creationTimeoutForUvDiscouragedInMs - 음수 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "discouraged",
            creationTimeoutForUvDiscouragedInMs= -1000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_041(self):
        self.logger.info("#041 creationTimeoutForUvDiscouragedInMs - 잘못된 타입(str) 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "discouraged",
            creationTimeoutForUvDiscouragedInMs= "300000"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_042(self):
        self.logger.info("#042 requestUserVerification - enum 에 없는 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            requestUserVerification="device",
            requestTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_043(self):
        self.logger.info("#043 requestUserVerification - 대소문자 값 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            requestUserVerification="Preferred",
            requestTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_044(self):
        self.logger.info("#044 requestUserVerification - 잘못된 타입(int) 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            requestUserVerification= 10,
            requestTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_045(self):
        self.logger.info("#045 requestUserVerification - " " 공백 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= " ",
            requestTimeoutInMs=300000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_046(self):
        self.logger.info("#046 requestTimeoutInMs - 음수 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "required",
            requestTimeoutInMs= -1000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_047(self):
        self.logger.info("#047 requestTimeoutInMs - 잘못된 타입(str) 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "preferred",
            requestTimeoutInMs= "300000"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_048(self):
        self.logger.info("#048 requestTimeoutForUvDiscouragedInMs - 음수 전송 ")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "discouraged",
            requestTimeoutForUvDiscouragedInMs= -1000
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False

    def test_update_rp_option_049(self):
        self.logger.info("#049 requestTimeoutForUvDiscouragedInMs - 잘못된 타입(str) 전송")
        response_code, response_text = update_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            creationUserVerification= "discouraged",
            requestTimeoutForUvDiscouragedInMs= "300000"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text = {response_text}")
            assert False