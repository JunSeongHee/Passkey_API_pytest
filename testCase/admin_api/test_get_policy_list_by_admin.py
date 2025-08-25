import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_policy_list_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        method: str = 'GET',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/policy"
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

def get_policy_list_no_rpid_api(
        base_url: str,
        admin_token,
        method: str = 'GET'
):
    base_url = f"{base_url}/admin/v1/rps//policy"
    headers = {
        'Authorization': f'{admin_token}'
    }
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text


class Test_get_policy_list:
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

    no_exist_rpid = readConfig.getValue('Admin Info', 'no_exist_clientId')

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

    def test_get_policy_list_001(self):
        self.logger.info("#001 RP와 관련된 Policy를 조회")

        res = controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if not res == 200:
        #not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, scopes=self.rp_scope)

        res1 = controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        if not res1 == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
                self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy)

        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId
        )
        check_response_code = 200

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data 필드가 있는지 확인
            assert "id" in body, "응답에 id 없음"
            assert "data" in body, "응답에 data 없음"

            policy = body["data"]

            if "acceptableAuthenticators" in policy:
                assert isinstance(policy["acceptableAuthenticators"], list)
                assert len(policy["acceptableAuthenticators"]) > 0

            if "disallowedAuthenticators" in policy:
                assert isinstance(policy["disallowedAuthenticators"], list)
                assert len(policy["disallowedAuthenticators"]) > 0

            if "allowCertifiedAuthenticatorsOnly" in policy:
                assert isinstance(policy["allowCertifiedAuthenticatorsOnly"], bool)

            if "enforceAttestation" in policy:
                assert isinstance(policy["enforceAttestation"], bool)

            if "acceptableAttestationTypes" in policy:
                assert isinstance(policy["acceptableAttestationTypes"], list)
                assert len(policy["acceptableAttestationTypes"]) > 0
                # 값 체크 (명세에 있는 값만)
                allowed_types = {"basic", "self", "attestationCA", "anonymizationCA", "none"}
                for att_type in policy["acceptableAttestationTypes"]:
                    assert att_type in allowed_types, f"허용되지 않은 Attestation Type: {att_type}"

            #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

    def test_get_policy_list_002(self):
        self.logger.info("#002 rpId 미기입 - 404 에러 반환 확인")
        response_code, response_text = get_policy_list_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_003(self):
        self.logger.info("#003 미존재 rpId 전송 - 404 에러 반환 확인")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_rpid
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_004(self):
        self.logger.info("#004 rpId 공백 기입 - 404 에러 반환 확인")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, " "
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_005(self):
        self.logger.info("#005 POST 요청")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_006(self):
        self.logger.info("#006 DELETE 요청")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_007(self):
        self.logger.info("#007 PATCH 요청")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_008(self):
        self.logger.info("#008 HEAD 요청")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_009(self):
        self.logger.info("#009 OPTIONS 요청")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_012(self):
        self.logger.info("#012 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_013(self):
        self.logger.info("#013 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_policy_list_api(
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

    def test_get_policy_list_014(self):
        self.logger.info("#014 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = get_policy_list_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, space_yes=True
        )

        check_response_code = 401 # 403이 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_policy_list_015(self):
        self.logger.info("#015 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = get_policy_list_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False