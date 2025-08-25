import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def check_origin_add_possibility_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        origin: str,
        method: str = 'GET',
        space_yes: bool = False
):
    params = { 'origin': origin }
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins/check-acceptability"
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

def check_origin_add_possibility_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        origin: str,
        method: str = 'GET'
):
    params = { 'origin': origin }
    base_url = f"{base_url}/admin/v1/rps//origins/check-acceptability"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}'
    }
    response = requests.request(method, base_url, headers=headers, params=params)
    return response.status_code, response.text

def check_origin_add_possibility_custom_params_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        params,
        method: str = 'GET',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins/check-acceptability"

    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, params=params)
    return response.status_code, response.text


def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

        body = json.loads(response_text)

        # id, data, data.rpId 필드가 있는지 확인
        assert "id" in body
        assert "data" in body
        assert "rpId" in body["data"]
        assert "origin" in body["data"]
        assert "acceptable" in body["data"]

        assert body["data"]["rpId"] == self.rpId

        assert isinstance(body["data"]["acceptable"], bool), "acceptable은 bool 타입이어야 함"

        assert body["data"]["acceptable"] is True, "추가하는 Origin의 acceptable 값은 True여야 함"

        #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info(f"🟢 해당 origin 은 추가가 가능합니다.")
        self.logger.info("🟢 TEST PASS")

    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        # 에러 메시지를 그대로 출력
        print(f"❌ AssertionError: {e}")
        assert False, str(e)

    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_check_origin_add_possibility:
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

    no_exist_origin = "https://playwright.dev/java/"
    exist_origin = "https://playwright.dev/"
    wrong_origin = "https://abcabcabcd.or.kr"

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

    def test_check_origin_add_possibility_001(self):
        self.logger.info("#001 존재하는 RP ID에 대해 Origin의 추가 가능 - True 확인(200 전송)")

        response_code, response_text = check_origin_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin)

        response_assertion(self, response_code, response_text)

    def test_check_origin_add_possibility_002(self):
        self.logger.info("#002 존재하는 RP ID에 대해 Origin의 추가 불가능 - False 확인(200 전송)")

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials,
            self.client_id, self.exist_origin # "https://playwright.dev/"
        )
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
            assert "acceptable" in body["data"]

            assert body["data"]["rpId"] == self.client_id

            assert isinstance(body["data"]["acceptable"], bool), "acceptable bool 타입이어야 함"
            assert body["data"]["acceptable"] is False, "추가 불가능한 Origin이어야 하므로 acceptable 값은 False여야 함"
            #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info(f"🔴 {self.exist_origin} 는 이미 존재하거나 추가가 불가능합니다.")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

    def test_check_origin_add_possibility_003(self):
        self.logger.info("#003 rpId 누락 - 400 에러 반환 확인")
        response_code, response_text = check_origin_add_possibility_no_rpid_api(self.bUrl, self.admin_encoded_credentials, self.no_exist_origin)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_004(self):
        self.logger.info("#004 미존재 rpId  - 400 에러 반환 확인")
        response_code, response_text = check_origin_add_possibility_no_rpid_api(self.bUrl, self.admin_encoded_credentials, self.no_exist_origin)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_005(self):
        self.logger.info("#005 rpId "" 전송 - 400 에러 반환 확인")
        response_code, response_text = check_origin_add_possibility_api(self.bUrl, self.admin_encoded_credentials, "", self.no_exist_origin)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_006(self):
        self.logger.info("#006 rpId " " 공백 전송 - 400 에러 반환 확인")
        response_code, response_text = check_origin_add_possibility_api(self.bUrl, self.admin_encoded_credentials, " ", self.no_exist_origin)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_007(self):
        self.logger.info("#007 필수 body 미기입")

        params = json.dumps({})

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_check_origin_add_possibility_008(self):
        self.logger.info("#008 필수 body - origins 미기입")

        params = json.dumps({
            "origin": []
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_009(self):
        self.logger.info("#009 필수 body - origins "" 적용")

        params = json.dumps({
            "origins": [ "" ]
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_010(self):
        self.logger.info("#010 필수 body - origins " " 공백 적용")

        params = json.dumps({
            "origins": [ " " ]
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_011(self):
        self.logger.info("#011 필수 body - origins 잘못된 형식 적용")

        params = json.dumps({
            "origins": [ "not-a-url" ]
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_012(self):
        self.logger.info("#012 필수 body - origins 잘못된 타입 str 적용")

        params = json.dumps({
            "origins": "https://naver.com/blog/"
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_013(self):
        self.logger.info("#013 필수 body - origins 잘못된 타입 dict 적용")

        params = json.dumps({
            "origins": { "https://naver.com/blog/" : "https://shopping.naver.com/" }
        })

        response_code, response_text = check_origin_add_possibility_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_014(self):
        self.logger.info("#014 POST 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_015(self):
        self.logger.info("#015 PUT 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_016(self):
        self.logger.info("#016 PATCH 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.no_exist_origin, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_017(self):
        self.logger.info("#017 DELETE 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_018(self):
        self.logger.info("#018 HEAD 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_019(self):
        self.logger.info("#019 OPTIONS 요청")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.no_exist_origin, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_020(self):
        self.logger.info("#020 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.no_exist_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_021(self):
        self.logger.info("#021 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.no_exist_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_022(self):
        self.logger.info("#022 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.no_exist_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_023(self):
        self.logger.info("#023 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.no_exist_origin
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_024(self):
        self.logger.info("#024 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.admin_encoded_credentials,
            self.client_id, self.no_exist_origin, space_yes=True
        )

        check_response_code = 401 # 403 아닐까?

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_check_origin_add_possibility_025(self):
        self.logger.info("#025 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = check_origin_add_possibility_api(
            self.bUrl, self.wrong_client_encoded_credentials,
            self.client_id, self.no_exist_origin
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False