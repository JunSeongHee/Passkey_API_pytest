import base64, json, pytest, requests

from apiGroup.authenticationAPI import useCredential
from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from apiGroup.registrationAPI import createCredential
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_all_rpid_info_api(
    base_url: str,
    admin_encoded_credentials,
    method: str = 'GET',
    space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps"
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

def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

        body = json.loads(response_text)

        #id, data, data.id 필드가 있는지 확인
        assert "id" in body
        assert "data" in body
        assert "rps" in body["data"]
        rps = body["data"]["rps"]
        assert isinstance(rps, list)

        for rp in rps:
            # 1. 필수 필드 및 타입
            assert "id" in rp and isinstance(rp["id"], str) and rp["id"].strip() != ""
            assert "name" in rp and isinstance(rp["name"], str) and 0 < len(rp["name"].strip()) <= 250
            assert "registrationEnabled" in rp and isinstance(rp["registrationEnabled"], bool)
            assert "authenticationEnabled" in rp and isinstance(rp["authenticationEnabled"], bool)
            assert "origins" in rp and isinstance(rp["origins"], list) and len(rp["origins"]) > 0
            assert "policy" in rp and isinstance(rp["policy"], dict)

            policy = rp["policy"]

            # 2. policy의 optional 필드: 있으면 타입/값 체크, 없으면 PASS
            for key in ["acceptableAuthenticators", "disallowedAuthenticators", "acceptableAttestationTypes"]:
                if key in policy:
                    assert isinstance(policy[key], list), f"{key} should be list"
                    assert len(policy[key]) > 0, f"{key} 리스트는 비어있을 수 없음"

            for key in ["allowCertifiedAuthenticatorsOnly", "enforceAttestation"]:
                if key in policy:
                    assert isinstance(policy[key], bool), f"{key} should be bool"

            # 3. acceptableAttestationTypes 값이 명세에 맞는지 체크 (있다면)
            attestation_allowed = {"basic", "self", "attestationCA", "anonymizationCA", "none"}
            if "acceptableAttestationTypes" in policy:
                for att_type in policy["acceptableAttestationTypes"]:
                    assert att_type in attestation_allowed, f"허용되지 않은 Attestation Type: {att_type}"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info(f"🟢 TEST PASS - 모든 RP 의 갯수는 {len(rps)}")

    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        # 에러 메시지를 그대로 출력
        print(f"❌ AssertionError: {e}")
        assert False, str(e)

    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_get_all_rpid_info:
    logger = LogGen.loggen()

     ############### base URL
    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    ############### client_id와 client_secret 을 이용해서 authorization 만들기
    # RP 이름과 비밀번호, RP URL
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

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_all_rpid_info_001(self):
        self.logger.info("#001 모든 RP 정보 조회")
        response_code, response_text = get_all_rpid_info_api(self.bUrl, self.admin_encoded_credentials)

        response_assertion(self, response_code, response_text)

    def test_all_rpid_info_002(self):
        self.logger.info("#002 PATCH 요청")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_003(self):
        self.logger.info("#003 DELETE 요청")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_004(self):
        self.logger.info("#004 HEAD 요청")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_005(self):
        self.logger.info("#005 OPTIONS 요청")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_006(self):
        self.logger.info("#006 admin 아닌 권한 - passkey:rp 으로 요청")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.rp_scopes)

        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.client_encoded_credentials
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_007(self):
        self.logger.info("#007 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.client_encoded_credentials
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_008(self):
        self.logger.info("#008 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"


        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.client_encoded_credentials
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_009(self):
        self.logger.info("#009 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.client_encoded_credentials
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_010(self):
        self.logger.info("#010 Basic + [(client id:client secret) 인코딩 값] 사이 공백")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_all_rpid_info_011(self):
        self.logger.info("#011 헤더에 [(client id:client secret) 인코딩 값] 오입력")
        response_code, response_text = get_all_rpid_info_api(
            self.bUrl, self.wrong_client_encoded_credentials
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False