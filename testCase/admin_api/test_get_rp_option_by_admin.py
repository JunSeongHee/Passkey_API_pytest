import base64, json, pytest, requests, os

from apiGroup.controlclientAPI import controlClient
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_rp_option_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        method: str = 'GET',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/defaultOptions"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}'
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }

    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text

def get_rp_option_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        method: str = 'GET',
):
    base_url = f"{base_url}/admin/v1/rps//defaultOptions"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text


class Test_get_rp_option:
    logger = LogGen.loggen()

    ############### base URL
    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id')
    client_secret = readConfig.getValue('Admin Info', 'client_secret')
    client_name = readConfig.getValue('Admin Info', 'client_name')

    no_exist_clientId = readConfig.getValue('Admin Info', 'no_exist_clientId')
    no_exist_rpid = readConfig.getValue('Admin Info', 'no_exist_clientId')
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

    def test_get_rp_option_001(self):
        self.logger.info("#001 RP의 사전에 설정된 Default Option을 조회")
        response_code, response_text = get_rp_option_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        check_response_code = 200

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data, data.id 필드가 있는지 확인
            assert "id" in body, "응답에 data 없음"

            assert "data" in body, "응답에 data 없음"

            data = body["data"]
            # creationAuthenticatorAttachment 옵션?
            if "creationAuthenticatorAttachment" in data:
                assert data["creationAuthenticatorAttachment"] in ["platform", "cross-platform"], \
                    f"creationAuthenticatorAttachment 값 오류: {data['creationAuthenticatorAttachment']}"
            else:
                self.logger.warning("creationAuthenticatorAttachment 필드가 응답에 없음(옵셔널)")

            # creationResidentKey
            if "creationResidentKey" in data:
                assert data["creationResidentKey"] in ["required", "preferred", "discouraged"], \
                    f"creationResidentKey 값 오류: {data.get('creationResidentKey')}"
            else:
                self.logger.warning("creationResidentKey 필드가 없음")

            # creationUserVerification
            if "creationUserVerification" in data:
                cuv = data["creationUserVerification"]
                assert cuv in ["required", "preferred", "discouraged"], \
                    f"creationUserVerification 값 오류: {cuv}"

                # creationTimeoutInMs, creationTimeoutForUvDiscouragedInMs
                if cuv in ["required", "preferred"]:
                    assert "creationTimeoutInMs" in data, "creationTimeoutInMs 없음"
                    assert isinstance(data["creationTimeoutInMs"], (int, float)), "creationTimeoutInMs는 숫자여야 함"
                else:
                    assert "creationTimeoutForUvDiscouragedInMs" in data, "creationTimeoutForUvDiscouragedInMs 없음"
                    assert isinstance(data["creationTimeoutForUvDiscouragedInMs"], (int, float)), "creationTimeoutForUvDiscouragedInMs는 숫자여야 함"
            else:
                self.logger.warning("creationUserVerification 필드가 없음")

            # requestUserVerification
            if "requestUserVerification" in data:
                ruv = data["requestUserVerification"]
                assert ruv in ["required", "preferred", "discouraged"], \
                    f"requestUserVerification 값 오류: {ruv}"

                # requestTimeoutInMs, requestTimeoutForUvDiscouragedInMs
                if ruv in ["required", "preferred"]:
                    assert "requestTimeoutInMs" in data, "requestTimeoutInMs 없음"
                    assert isinstance(data["requestTimeoutInMs"], (int, float)), "requestTimeoutInMs는 숫자여야 함"
                else:
                    if "requestTimeoutForUvDiscouragedInMs" in data:
                        assert isinstance(data["requestTimeoutForUvDiscouragedInMs"],
                                          (int, float)), "requestTimeoutForUvDiscouragedInMs는 숫자여야 함"
                    elif "requestTimeoutInMs" in data:
                        self.logger.warning("requestTimeoutInMs 필드가 'discouraged' 상태에서도 존재함 (스펙과 다를 수 있음)")
                    else:
                        assert False, "requestTimeout 관련 필드 없음"
            else:
                self.logger.warning("requestUserVerification 필드가 없음")

            self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info("🟢 TEST PASS")

            # ==== 응답 필드 write to testData/options_list.json ====
            jsonUtil.writeJsonBulk('options_list', body)

            self.logger.info(f"testData/options_list.json 파일에 응답 데이터 저장 완료")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

    def test_get_rp_option_002(self):
        self.logger.info("#002 rpId 미기입 시 404 에러 반환 확인")
        response_code, response_text = get_rp_option_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_003(self):
        self.logger.info("#003 미존재 rpId 전송 - 404 에러 반환 확인")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_rpid
        )


        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_004(self):
        self.logger.info("#004 rpId 공백 기입 - 404 에러 반환 확인")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, " "
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_005(self):
        self.logger.info("#005 POST 요청")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_006(self):
        self.logger.info("#006 DELETE 요청")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_007(self):
        self.logger.info("#007 PATCH 요청")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_008(self):
        self.logger.info("#008 HEAD 요청")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_009(self):
        self.logger.info("#009 OPTIONS 요청")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_option_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_013(self):
        self.logger.info("#013 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_option_api(
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

    def test_get_rp_option_014(self):
        self.logger.info("#014 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = get_rp_option_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, space_yes=True
        )

        check_response_code = 401 # 403이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_option_015(self):
        self.logger.info("#015 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = get_rp_option_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False