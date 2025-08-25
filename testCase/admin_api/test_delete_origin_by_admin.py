import base64, json, pytest, requests, time

from urllib import parse
from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def delete_origin_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        origin: str,
        method: str = 'DELETE',
        space_yes: bool = False
):
    params = {
        "origin": origin
    }
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins"

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

def delete_origin_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        origin: str,
        method: str = 'DELETE'
):
    params = {
        "origin": origin
    }
    base_url = f"{base_url}/admin/v1/rps//origins"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}'
    }
    response = requests.request(method, base_url, headers=headers, params=params)
    return response.status_code, response.text

def delete_origin_custom_playload_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        params,
        method: str = 'DELETE',
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins"

    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}'
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

        #assert body["data"]["rpId"] == self.rpId

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")

    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        # 에러 메시지를 그대로 출력
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, f"Exception: {e}, Response: {response_text}"

class Test_delete_orgin:
    logger = LogGen.loggen()

    ############### base URL
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

    rpId = jsonUtil.readJson("create_rpid", "id")
    name = jsonUtil.readJson("create_rpid", "name")
    registrationEnabled = jsonUtil.readJson("create_rpid", "registrationEnabled")
    authenticationEnabled = jsonUtil.readJson("create_rpid", "authenticationEnabled")
    origins = jsonUtil.readJson("create_rpid", "origins")
    policy = jsonUtil.readJson("create_rpid", "policy")

    del_origin = "https://playwright.dev/dotnet/docs/intro"

    scopes = [ "passkey:rp" ]

    @classmethod
    def setup_class(cls):
        if not controlClient.get_clientid_api(cls.bUrl, cls.admin_encoded_credentials, cls.rpId) == 200:
            controlClient.create_client_api(cls.bUrl, cls.admin_encoded_credentials, cls.rpId, cls.name, cls.scopes)

        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_delete_origin_001(self):
        self.logger.info("#001 origin 삭제")

        if not controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy)
            controlRPID.add_origin_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin)

        if controlRPID.check_origin_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin):
            controlRPID.add_origin_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin)

        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, self.del_origin
        )

        response_assertion(self, response_code, response_text)

    def test_delete_origin_002(self):
        self.logger.info("#002 rpId 미기입 시 404 에러 반환 확인")
        response_code, response_text = delete_origin_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, self.del_origin
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_003(self):
        self.logger.info("#003 미존재 rpId 전송 시, 404 에러 반환 확인")
        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, "abcabcabcd.or.kr", self.del_origin
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_delete_origin_004(self):
        self.logger.info("#004 rpId 공백 기입 시 404 에러 반환 확인")
        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, " ", self.del_origin
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_rpid_info_005(self):
        self.logger.info("#005 PUT 요청")
        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_rpid_info_006(self):
        self.logger.info("#006 PATCH 요청")
        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_rpid_info_007(self):
        self.logger.info("#007 OPTIONS 요청")
        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.del_origin, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_008(self):
        self.logger.info("#008 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.del_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_009(self):
        self.logger.info("#009 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.del_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.del_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_011(self):
        self.logger.info("#011 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = delete_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.del_origin
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_012(self):
        self.logger.info("#012 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        if not controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )

        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, self.del_origin, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_013(self):
        self.logger.info("#013 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        if not controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )

        response_code, response_text = delete_origin_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId, self.del_origin
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_014(self):
        self.logger.info("#014 필수 body 미기입")

        params = {}

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400 #405 나오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_015(self):
        self.logger.info("#015 필수 body - origins 미기입")

        params = {
            "origins": []
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400 #405 나오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_016(self):
        self.logger.info("#016 필수 body - origins "" 적용")

        params = {
            "origins": [ "" ]
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_017(self):
        self.logger.info("#017 필수 body - origins " " 공백 적용")

        params = {
            "origins": [ " " ]
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_018(self):
        self.logger.info("#018 필수 body - origins 잘못된 형식 적용")

        params = {
            "origins": [ "not-a-url" ]
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_019(self):
        self.logger.info("#019 필수 body - origins 잘못된 타입 str 적용")

        params = {
            "origins": "https://playwright.dev/python/"
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_020(self):
        self.logger.info("#020 필수 body - origins 잘못된 타입 dict 적용")

        params = {
            "origins": { "https://playwright.dev/dotnet/" : "https://playwright.dev/dotnet/docs/docker" }
        }

        response_code, response_text = delete_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_021(self):
        self.logger.info("#021 필수 body - 한개만 존재하는 origins 를 삭제하고자 하는 경우")

        if not controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )

        original_origins = self.origins[:]  # 리스트 복사
        first_origin = original_origins[0]
        origins_to_delete = original_origins[1:]

        for origin in origins_to_delete:
            self.logger.info(f"🗑️ Delete origin: {origin}")
            controlRPID.delete_origin_api(self.bUrl, self.admin_encoded_credentials, self.rpId, origin)
            time.sleep(0.3)  # 삭제 API 딜레이 보정 (optional)

        rest_origin = controlRPID.get_rp_origins_list_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, rest_origin
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_022(self):
        self.logger.info("#022 필수 body - 존재하지 않는 origins 삭제")

        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy)

        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, "https://test.com"
        )

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_delete_origin_023(self):
        self.logger.info("#023 필수 body - 존재하지 않는 origins 삭제")

        rpId = "sk.co.kr"
        name = "SKCO"
        origins = ["http://localhost:8081", "https://sk.co.kr/"]
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(self.bUrl, self.admin_encoded_credentials, rpId, name, self.registrationEnabled, self.authenticationEnabled, origins, self.policy)

        response_code, response_text = delete_origin_api(
            self.bUrl, self.admin_encoded_credentials, rpId, "ftp://sk.co.kr"
        )

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, rpId)

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

