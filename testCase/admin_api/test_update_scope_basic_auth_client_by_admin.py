import base64
import json
import pytest
import requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_auth_client_scopes_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    scopes: list = None,
    method: str = "PATCH",
    content_type: str = 'application/json;charset=UTF-8',
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}/scopes"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": content_type
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": content_type
        }

    body = {
        "scopes": scopes
    }
    response = requests.request(
        method, url, headers=headers, data=json.dumps(body)
    )
    return response.status_code, response.text

def update_auth_client_scopes_no_clientid_api(
    base_url: str,
    admin_encoded_credentials,
    scopes: list,
    method: str = "PATCH",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients//scopes"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": "application/json;charset=UTF-8"
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": "application/json;charset=UTF-8"
        }

    body = {
        "scopes": scopes
    }
    response = requests.request(
        method, url, headers=headers, data=json.dumps(body)
    )
    return response.status_code, response.text

def update_auth_client_clientid_custom_payload_api(
    base_url: str,
    admin_encoded_credentials,
    client_id: str,
    payload,
    method: str = "PATCH",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/clients/{client_id}/scopes"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}',
            "Content-Type": "application/json;charset=UTF-8"
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}',
            "Content-Type": "application/json;charset=UTF-8"
        }

    response = requests.request(
        method, url, headers=headers, json=json.dumps(payload)#payload
    )
    return response.status_code, response.text

def response_assertion(self, scope, response_code:str, response_text:str):
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

        # 필수 필드 체크
        assert client["clientId"] == self.rpId, "clientId 값 불일치"
        assert isinstance(client["scopes"], list), "scopes 리스트여야 함"
        assert set(client["scopes"]) == set(scope), "scopes 값 불일치"
        assert isinstance(client["clientSecretCreatedAt"], str), "clientSecretCreatedAt은 RFC3339 문자열"
        if "clientSecretExpiresInSeconds" in client:
            assert isinstance(client["clientSecretExpiresInSeconds"], int) and client["clientSecretExpiresInSeconds"] > 0

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_update_auth_client_scopes:
    logger = LogGen.loggen()

    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id')
    client_secret = readConfig.getValue('basic Info', 'client_secret')
    client_url = readConfig.getValue('basic Info', 'client_url')
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

    admin_update_scopes = ["passkey:admin"]
    rp_update_scopes = ["passkey:rp"]
    rp_update_scopes1 = ["passkey:rp:migration"]
    rp_update_scopes2 = ["passkey:rp", "passkey:rp:migration"]

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_update_auth_client_scopes_001(self):
        self.logger.info("#001 Client에 부여된 Scope 업데이트 : passkey:admin 권한")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.admin_update_scopes
        )

        response_assertion(self, self.admin_update_scopes, response_code, response_text)

    def test_update_auth_client_scopes_002(self):
        self.logger.info("#002 Client에 부여된 Scope 업데이트 : passkey:rp 권한")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.rp_update_scopes
        )

        response_assertion(self, self.rp_update_scopes, response_code, response_text)

    def test_update_auth_client_scopes_003(self):
        self.logger.info("#003 Client에 부여된 Scope 업데이트 : passkey:rp:migration 권한")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.rp_update_scopes1
        )

        response_assertion(self, self.rp_update_scopes1, response_code, response_text)

    def test_update_auth_client_scopes_004(self):
        self.logger.info("#004 Client에 부여된 Scope 업데이트 : passkey:rp, passkey:rp:migration 권한")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.rp_update_scopes2
        )

        response_assertion(self, self.rp_update_scopes2, response_code, response_text)

    def test_update_auth_client_scopes_005(self):
        self.logger.info("#005 scopes - 미존재값으로 전송: 서버에서 string 값인지만 체크(200 에러)")

        scopes = ["invalid:scope"] # 서버에서 string 값인지만 체크함

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scopes,
            #self.client_secret_expires_in_second
        )
        response_assertion(self, scopes, response_code, response_text)

    def test_update_auth_client_scopes_006(self):
        self.logger.info("#006 scopes - 중복값 전송: 중복된 값일 경우, 한개로 처리(200 에러)")

        scopes =  ["passkey:rp", "passkey:rp"]  # 중복된 값일 경우, 한개로 처리

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scopes,
            #self.client_secret_expires_in_second
        )

        response_assertion(self, self.rp_update_scopes, response_code, response_text)

    def test_update_auth_client_scopes_007(self):
        self.logger.info("#007 scopes 누락(400 에러)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_scopes)

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_008(self):
        self.logger.info("#008 scopes 빈 배열(200)")

        scope = []

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_scopes)

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scope
        )
        check_response_code = 200

        response_assertion(self, scope, response_code, response_text)

    def test_update_auth_client_scopes_009(self):
        self.logger.info("#009 client id 누락 전송(400 에러)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_update_scopes)

        response_code, response_text = update_auth_client_scopes_no_clientid_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rp_update_scopes
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_010(self):
        self.logger.info("#010 미존재하는 client id 전송(400 에러)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_update_scopes)

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            "testtest123.com",
            self.rp_update_scopes
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_011(self):
        self.logger.info("#011 client id " " 공백 전송(400 에러)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_update_scopes)

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            " ",
            self.rp_update_scopes
        )
        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_012(self):
        self.logger.info("#012 GET 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            method="GET"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_013(self):
        self.logger.info("#013 POST 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_014(self):
        self.logger.info("#014 PUT 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_015(self):
        self.logger.info("#015 DELETE 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_016(self):
        self.logger.info("#016 HEAD 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            method="HEAD"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_017(self):
        self.logger.info("#017 OPTIONS 요청")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_018(self):
        self.logger.info("#018 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
            content_type="application/gzip"
        )
        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_019(self):
        self.logger.info("#019 admin 아닌 권한 - passkey:rp")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, self.rp_update_scopes)

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_update_scopes
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답값 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_update_auth_client_scopes_020(self):
        self.logger.info("#020 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_update_scopes
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답값 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_021(self):
        self.logger.info("#021 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_seconds
        )
        check_response_code = 403 # 401 응답값 옮

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_022(self):
        self.logger.info("#022 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.client_encoded_credentials,
            self.rpId,
            self.rp_update_scopes
        )
        check_response_code = 403 # 401 응답값 옮

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_023(self):
        self.logger.info("#023 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            space_yes=True
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_024(self):
        self.logger.info("#024 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.wrong_client_encoded_credentials,
            self.rpId,
            self.rp_update_scopes,
            #self.client_secret_expires_in_second
        )
        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_auth_client_scopes_025(self):
        self.logger.info("#025 scopes 공백(400)")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.client_name, scopes=self.rp_scopes)

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes= " "
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_auth_client_scopes_026(self):
        self.logger.info("#026 scopes 잘못된 타입으로 전송- 전송(200 에러)")

        scopes = 12345 # 서버에서는 scope 이 문자열인지만 체크함

        response_code, response_text = update_auth_client_scopes_api(
            self.bUrl,
            self.admin_encoded_credentials,
            self.rpId,
            scopes=scopes,
            #self.client_secret_expires_in_second
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

