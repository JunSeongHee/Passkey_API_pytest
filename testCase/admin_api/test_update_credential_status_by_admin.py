import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_credential_status_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        userId: str,
        credentialId: str,
        status: str,
        method: str = 'PATCH',
        content_type: str = 'application/x-www-form-urlencoded',
        space_yes: bool = False
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials/{credentialId}"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            'Content-Type': content_type
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            'Content-Type': content_type
        }
    params = {
        "status": status
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def update_credential_status_custom_params_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        userId: str,
        credentialId: str,
        param,
        method: str = 'PATCH',
        content_type: str = 'application/x-www-form-urlencoded'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials/{credentialId}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }

    response = requests.request(method, url, headers=headers, params=param)
    return response.status_code, response.text

def update_credential_status_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        userId: str,
        credentialId: str,
        status: str,
        method: str = 'PATCH',
        content_type: str = 'application/x-www-form-urlencoded'
):
    url = f"{base_url}/admin/v1/rps//users/{userId}/credentials/{credentialId}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    params = {
        "status": status
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def update_credential_status_no_userid_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        credentialId: str,
        status: str,
        method: str = 'PATCH',
        content_type: str = 'application/x-www-form-urlencoded'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users//credentials/{credentialId}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    params = {
        "status": status
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def update_credential_status_no_credentialid_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        userId: str,
        status: str,
        method: str = 'PATCH',
        content_type: str = 'application/x-www-form-urlencoded'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials//"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    params = {
        "status": status
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"
        body = json.loads(response_text)

        # 필수 응답 필드 검증
        assert "id" in body, "응답에 id 없음"
        assert "data" in body, "응답에 data 없음"
        data = body["data"]

        # credentialId 기본 검증
        assert "credentialId" in data, "data에 credentialId 없음"
        res_credentialId = data["credentialId"]
        assert res_credentialId == self.credentialId, f"응답 credentialId 불일치: {res_credentialId} != {self.credentailId}"
        
        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e} - {response_text}")
        assert False, "응답 구조가 올바르지 않음"

class Test_update_rp_credentials:
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
    logger.info(f"admin_encoded_credentials - {admin_encoded_credentials}")

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('naver', 'clientId')
        cls.clientsecret = jsonUtil.readJson('naver', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

        controlRPID.get_rp_credentials_api(cls.bUrl, cls.admin_encoded_credentials, cls.client_id)

        cls.userId = jsonUtil.readJson("credential_user", "userId")
        cls.credentialId = jsonUtil.readJson("credential_user", "credentialId")
    
    def test_update_credential_status_001(self):
        self.logger.info("#001 RP User의 Credential 상태를 비활성화 (inactive) 상태로 변경 - 정상 파라미터 전송")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, status="inactive"
        )
        response_assertion(self, response_code, response_text)

    def test_update_credential_status_002(self):
        self.logger.info("#002 RP User의 Credential 상태를 활성화 (active) 상태로 변경 - 정상 파라미터 전송")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, status="active"
        )
        response_assertion(self, response_code, response_text)

    def test_update_credential_status_003(self):
        self.logger.info("#003 rpId 누락 - 404 에러 반환 확인")

        response_code, response_text = update_credential_status_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, self.userId, 
            self.credentialId, status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_004(self):
        self.logger.info("#004 미존재 rpId 전송 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_clientId, 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_005(self):
        self.logger.info("#005 rpId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, " ", self.userId, 
            self.credentialId, status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_006(self):
        self.logger.info("#006 userId 미기입 - 404 에러 반환 확인")
        response_code, response_text = update_credential_status_no_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.credentialId, status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_007(self):
        self.logger.info("#007 미존재 userId 전송 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, 
            self.client_id, "63fdhhfdjfj", self.credentialId
            , status="active"
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_008(self):
        self.logger.info("#008 userId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            " " , self.credentialId, status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_009(self):
        self.logger.info("#009 credentialId 미기입 - 404 에러 반환 확인")
        response_code, response_text = update_credential_status_no_credentialid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.userId, status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_010(self):
        self.logger.info("#010 미존재 credentialId 전송 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.userId, "aaa", status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_011(self):
        self.logger.info("#011 credentialId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.userId , " ", status="active"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_012(self):
        self.logger.info("#012 status 미기입 - 400 에러 반환 확인")

        param = {}

        response_code, response_text = update_credential_status_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, param=param
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_013(self):
        self.logger.info("#013 status 존재하지 않은 값 - 400 에러 반환 확인")

        param = { 
            "status": "invalid"
        }

        response_code, response_text = update_credential_status_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, param=param
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_014(self):
        self.logger.info("#014 status ' ' 공백 적용 - 400 에러 반환 확인")

        param = { 
            "status": " "
        }

        response_code, response_text = update_credential_status_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, param=param
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_015(self):
        self.logger.info("#015 GET 요청")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active", method="GET"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_016(self):
        self.logger.info("#016 POST 요청")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active", method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_017(self):
        self.logger.info("#017 PUT 요청")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active", method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_018(self):
        self.logger.info("#018 HEAD 요청")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.userId, self.credentialId, status="active", method="HEAD"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_019(self):
        self.logger.info("#019 OPTIONS 요청")
        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, 
            self.userId, self.credentialId, status="active", method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_020(self):
        self.logger.info("#020 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_021(self):
        self.logger.info("#021 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_022(self):
        self.logger.info("#022 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_023(self):
        self.logger.info("#023 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_024(self):
        self.logger.info("#024 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId, status="active", space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_credential_status_025(self):
        self.logger.info("#025 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_credential_status_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.client_id , 
            self.userId, self.credentialId, status="active"
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False
