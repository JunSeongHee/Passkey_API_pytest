import base64, json, pytest, requests

from urllib import parse
from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def delete_credential_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        userId: str,
        credentialId: str,
        method: str = 'DELETE',
        content_type: str = 'application/json;charset=UTF-8',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials/{credentialId}"
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
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text

def delete_credential_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        userId: str,
        credentialId: str,
        method: str = 'DELETE',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps//users/{userId}/credentials/{credentialId}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text

def delete_credential_no_userid_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        credentialId: str,
        method: str = 'DELETE',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/users//credentials/{credentialId}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text

def delete_credential_no_credentials_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        userId: str,
        method: str = 'DELETE',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials/{''}"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers)
    return response.status_code, response.text

class Test_delete_credential:
    logger = LogGen.loggen()

    ############### base URL
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

    # userId = jsonUtil.readJson("credential_user", "userId")
    # credentialId = jsonUtil.readJson("credential_user", "credentialId")

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

    def test_delete_credential_001(self):
        self.logger.info("#001 RP 삭제")

        #controlRPID.get_rp_credentials_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id,
            self.userId, self.credentialId
        )
        check_response_code = 200

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data, data.rpId 필드가 있는지 확인
            assert "id" in body
            assert "data" in body
            assert "credentialId" in body["data"]

            self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            assert False, str(e)
        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, f"Exception: {e}, Response: {response_text}"

    def test_delete_credential_002(self):
        self.logger.info("#002 rpId 미기입 - 404 에러 반환 확인")

        response_code, response_text = delete_credential_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, self.userId, self.credentialId
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_003(self):
        self.logger.info("#003 미존재 rpId 전송 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_clientId, self.userId, self.credentialId
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_004(self):
        self.logger.info("#004 rpId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, " ", self.userId, self.credentialId
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_005(self):
        self.logger.info("#005 userId 미기입 - 404 에러 반환 확인")
        response_code, response_text = delete_credential_no_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.credentialId
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_006(self):
        self.logger.info("#006 미존재 userId 전송 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, "63fdhhfdjfj", self.credentialId
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_007(self):
        self.logger.info("#007 userId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, " " , self.credentialId
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_008(self):
        self.logger.info("#008 credentialId 미기입 - 404 에러 반환 확인")
        response_code, response_text = delete_credential_no_credentials_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_009(self):
        self.logger.info("#009 미존재 credentialId 전송 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, "aaa"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_010(self):
        self.logger.info("#010 credentialId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId , " "
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_011(self):
        self.logger.info("#011 GET 요청")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, self.credentialId, method="GET"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_012(self):
        self.logger.info("#012 POST 요청")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, self.credentialId, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_013(self):
        self.logger.info("#013 PUT 요청")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, self.credentialId, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_014(self):
        self.logger.info("#014 HEAD 요청")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, self.credentialId, method="HEAD"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_015(self):
        self.logger.info("#015 OPTIONS 요청")
        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, self.credentialId, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_016(self):
        self.logger.info("#016 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_credential_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , self.userId, self.credentialId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_017(self):
        self.logger.info("#017 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_credential_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, self.userId, self.credentialId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_018(self):
        self.logger.info("#018 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_credential_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, self.userId, self.credentialId
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_019(self):
        self.logger.info("#019 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_credential_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , self.userId, self.credentialId
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_020(self):
        self.logger.info("#020 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = delete_credential_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,
            self.userId, self.credentialId, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_021(self):
        self.logger.info("#021 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = delete_credential_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.client_id , self.userId, self.credentialId
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False
