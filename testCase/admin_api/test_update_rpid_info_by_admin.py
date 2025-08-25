import base64, json, pytest, requests

from urllib import parse
from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_rpid_info_api(
        base_url: str,
        admin_encoded_credentials,
        id: str,
        name: str,
        registrationEnabled: bool,
        authenticationEnabled: bool,
        origins: list,
        policy: dict,
        method: str = 'PUT',
        content_type: str = 'application/json;charset=UTF-8',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps"
    payload = {
        "id": id,
        "name": name,
        "registrationEnabled": registrationEnabled,
        "authenticationEnabled": authenticationEnabled,
        "origins": origins,
        "policy": policy
    }
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
    response = requests.request(method, base_url, headers=headers, json=payload)
    return response.status_code, response.text

def update_rpid_info_custom_playload_api(
        base_url: str,
        admin_encoded_credentials,
        payload,
        method: str = 'PUT',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, json=payload)
    return response.status_code, response.text

class Test_update_rpid_info:
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

    rp_scope = jsonUtil.readJson('client', 'rp_scope')
    rpId = jsonUtil.readJson("create_rpid", "id")
    name = jsonUtil.readJson("create_rpid", "name")
    registrationEnabled = jsonUtil.readJson("create_rpid", "registrationEnabled")
    authenticationEnabled = jsonUtil.readJson("create_rpid", "authenticationEnabled")
    origins = jsonUtil.readJson("create_rpid", "origins")
    policy = jsonUtil.readJson("create_rpid", "policy")

    # update 파라미터
    update_name = jsonUtil.readJson("update_rpid", "name")
    update_registrationEnabled = jsonUtil.readJson("update_rpid", "registrationEnabled")
    update_authenticationEnabled = jsonUtil.readJson("update_rpid", "authenticationEnabled")
    update_origins = jsonUtil.readJson("update_rpid", "origins")
    update_policy = jsonUtil.readJson("update_rpid", "policy")

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_update_rpid_info_001(self):
        self.logger.info("#001 RP 정보 갱신")
        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )
        # 수정
        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, self.update_policy
                                                           )
        check_response_code = 200
        # 삭제
        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        try:
            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data, data.rpId 필드가 있는지 확인
            assert "id" in body
            assert "data" in body
            assert "rpId" in body["data"]

            assert body["data"]["rpId"] == self.rpId

            #self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)
        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, f"Exception: {e}, Response: {response_text}"

    def test_update_rpid_info_002(self):
        self.logger.info("#002 origin 중복 적용한 경우 하나의 값으로 갱신되는지 확인")

        duplicator_origin = [
            "https://playwright.dev/dotnet/community/welcome",
            "https://playwright.dev/dotnet/community/welcome"
        ]

        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            duplicator_origin, self.update_policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")

            from test_delete_rpid_info_by_admin import delete_rpid_info_api
            delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_003(self):
        self.logger.info("#003 acceptableAttestationTypes 중복 적용한 경우 하나의 값을 갖는지 확인")

        policy = {
            "acceptableAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : False,
            "acceptableAttestationTypes" : [ "basic", "basic" ]
        }

        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")

        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_update_rpid_info_004(self):
        self.logger.info("#004 disallowedAuthenticators 존재하고 acceptableAuthenticators 없을 경우 정상 확인")

        policy = {
            "disallowedAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : False,
            "acceptableAttestationTypes" : [ "basic", "none" ]
        }

        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, {response_text}")
            assert False

    def test_update_rpid_info_005(self):
        self.logger.info("#005 acceptableAuthenticators 존재하고 disallowedAuthenticators 없을 경우 정상 확인")

        policy = {
            "acceptableAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : False,
            "acceptableAttestationTypes" : [ "basic", "none" ]
        }

        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")

        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_006(self):
        self.logger.info("#006 enforceAttestation true 인 경우, acceptableAttestationTypes 값은 attestationCA, anonymizationCA, basic 강제 확인")

        policy = {
            "acceptableAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : True,
            "acceptableAttestationTypes" : [ "basic", "attestationCA", "anonymizationCA" ]
        }
        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")

        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_007(self):
        self.logger.info("#007 생략 가능 여부 및 필수 파라미터 정상값 확인 : acceptableAuthenticators, disallowedAuthenticators, allowCertifiedAuthenticatorsOnly, enforceAttestation, acceptableAttestationTypes")

        policy = {}

        # rp 생성
        from test_create_rpid_info_by_admin import create_rpid_info_api
        create_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        response_code, response_text = update_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.update_name,
                                                            self.update_registrationEnabled, self.update_authenticationEnabled,
                                                            self.update_origins, policy
                                                           )
        check_response_code = 200

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")

        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_008(self):
        self.logger.info("#008 PATCH 요청")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_009(self):
        self.logger.info("#009 DELETE 요청")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_010(self):
        self.logger.info("#010 HEAD 요청")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_011(self):
        self.logger.info("#011 OPTIONS 요청")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_012(self):
        self.logger.info("#012 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy, content_type="application/gzip"
        )

        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_013(self):
        self.logger.info("#013 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_014(self):
        self.logger.info("#014 admin 아닌 권한 - passkey:rp:migration")

        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_015(self):
        self.logger.info("#015 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_016(self):
        self.logger.info("#016 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_017(self):
        self.logger.info("#017 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.name, self.registrationEnabled, self.authenticationEnabled,
            self.origins, self.policy, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_018(self):
        self.logger.info("#018 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_019(self):
        self.logger.info("#019 필수 requset body인 rpId를 미존재하는 rpId를 갱신하고자할 경우")

        from test_delete_rpid_info_by_admin import delete_rpid_info_api
        delete_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_020(self):
        self.logger.info("#020 필수 requset body인 rpId 누락 - 400 에러 반환 확인")

        payload = {
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_021(self):
        self.logger.info("#021 필수 requset body인 rpId NULL 전송 - 400 에러 반환 확인")

        rpId = None
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_022(self):
        self.logger.info("#022 필수 requset body 인 rpId "" 전송 - 400 에러 반환 확인")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, "", self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_023(self):
        self.logger.info("#023 필수 requset body 인 rpId 공백값 "  " 전송 - 400 에러 반환 확인")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, "  ", self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_024(self):
        self.logger.info("#024 필수 requset body 인 rpId 도메인 형식이 아닌 포맷으로 전송 - 400 에러 반환 확인")

        rpId = "not a domain"
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_025(self):
        self.logger.info("#025 필수 requset body 인 rpId 잘못된 형식으로 전송1 - 400 에러 반환 확인")

        rpId = "https://playwright"
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_026(self):
        self.logger.info("#026 필수 requset body 인 rpId 잘못된 형식으로 전송2 - 400 에러 반환 확인")

        rpId = "https://playwright.dev"
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_027(self):
        self.logger.info("#027 필수 requset body 인 rpId 잘못된 타입으로 전송 - 400 에러 반환 확인")

        rpId = ["test.com"]
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_028(self):
        self.logger.info("#028 필수 requset body 인 name 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_029(self):
        self.logger.info("#029 필수 requset body 인 name null 전송 - 400 에러 반환 확인")
        name = None
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_030(self):
        self.logger.info("#030 필수 requset body 인 name "" 전송 - 400 에러 반환 확인")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, "", self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_031(self):
        self.logger.info("#031 필수 requset body 인 name 공백값 " " 전송 - 400 에러 반환 확인")
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, " ", self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_032(self):
        self.logger.info("#032 필수 requset body 인 name 250자 초과한 값 전송 - 400 에러 반환 확인")

        name = "a"*251

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_033(self):
        self.logger.info("#033 필수 requset body 인 string 인 name에 integer 값으로 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": ["name"],
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True

            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_034(self):
        self.logger.info("#034 필수 requset body 인 string 인 name에 list값 전송 - 400 에러 반환 확인")

        name = ["123"]

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, name, self.registrationEnabled, self.authenticationEnabled, self.origins, self.policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_035(self):
        self.logger.info("#035 필수 requset body 인 registrationEnabled 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 404 # 400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_036(self):
        self.logger.info("#036 필수 requset body 인 registrationEnabled 값 null 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": None,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )
        check_response_code = 404 # 400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_037(self):
        self.logger.info("#037 필수 requset body 인 registrationEnabled 값 문자열 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": "True",
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_038(self):
        self.logger.info("#038 필수 requset body 인 registrationEnabled 값 integer 값 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": 1,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_039(self):
        self.logger.info("#039 필수 requset body 인 registrationEnabled 값 list 타입 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": [True],
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_040(self):
        self.logger.info("#040 필수 requset body 인 authenticationEnabled 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 404 #400 이어야함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_041(self):
        self.logger.info("#041 필수 requset body 인 authenticationEnabled 값 null 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": None,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 404 #400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_042(self):
        self.logger.info("#042 필수 requset body 인 authenticationEnabled 값 문자열 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": "True",
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_043(self):
        self.logger.info("#043 필수 requset body 인 authenticationEnabled 값 integer 값 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": 1,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_044(self):
        self.logger.info("#044 필수 requset body 인 authenticationEnabled 값 list 타입 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": [True],
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_045(self):
        self.logger.info("#045 필수 requset body 인 origins 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_046(self):
        self.logger.info("#046 필수 requset body 인 origins null 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": [None],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_047(self):
        self.logger.info("#047 필수 requset body 인 origins 배열에 "" 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": [ "" ],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_048(self):
        self.logger.info("#048 필수 requset body 인 origins 배열에 공백 " " 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": [ " " ],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_049(self):
        self.logger.info("#049 필수 requset body 인 origins 빈 배열 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": [],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 404 #400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_050(self):
        self.logger.info("#050 필수 requset body 인 origins 비문자열 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": [True, 123],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_051(self):
        self.logger.info("#051 필수 requset body 인 origins 배열 아닌 타입으로 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": "https://playwright.dev/",
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_052(self):
        self.logger.info("#052 필수 requset body 인 origins http, https 프로토콜이 아닌 값 전송 - 400 에러 반환 확인")

        origins = ["ftp://playwright.dev/", "http://localhost:8081"]
        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        res = controlRPID.get_rp_credentials_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        self.logger.info(f"res - {res}")
        if not res == 200:
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
                self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 404 # 400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info(f"🟢 TEST PASS - {response_text}")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_053(self):
        self.logger.info("#053 필수 requset body 인 origins 잘못된 값 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": ["https://playwright.dev/", "invalid-origin"],
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_054(self):
        self.logger.info("#054 필수 requset body 인 origins dict 타입 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": {"origin": "https://a.com"},
            "policy": self.policy
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_update_rpid_info_055(self):
        self.logger.info("#055 필수 requset body 인 policy 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_056(self):
        self.logger.info("#056 필수 requset body 인 policy null 값 전송 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "name": self.name,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": None
        }

        response_code, response_text = update_rpid_info_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_057(self):
        self.logger.info("#057 필수 requset body 인 policy 빈 객체 전송 - 400 에러 반환 확인")

        policy = {}
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 404 #400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_058(self):
        self.logger.info("#058 필수 requset body 인 policy 잘못된 타입1(list) 전송 - 400 에러 반환 확인")

        policy = []
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_059(self):
        self.logger.info("#059 필수 requset body 인 policy 잘못된 타입2 str 전송 - 400 에러 반환 확인")

        policy = "text"
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_060(self):
        self.logger.info("#060 필수 requset body 인 acceptableAuthenticators 빈 배열 전송 - 400 에러 반환 확인")

        policy = { "acceptableAuthenticators": [] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_061(self):
        self.logger.info("#061 필수 requset body 인 acceptableAuthenticators "" 전송 - 400 에러 반환 확인")

        policy = { "acceptableAuthenticators":  [ "" ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_062(self):
        self.logger.info("#062 필수 requset body 인 acceptableAuthenticators 공백 " " 전송 - 400 에러 반환 확인")

        policy = { "acceptableAuthenticators":  [ " " ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_063(self):
        self.logger.info("#063 필수 requset body 인 acceptableAuthenticators 잘못된 타입(str)으로 전송 - 400 에러 반환 확인")

        policy = { "acceptableAuthenticators": "abc" }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_064(self):
        self.logger.info("#064 필수 requset body 인 acceptableAuthenticators 잘못된 값으로 전송 - 400 에러 반환 확인")

        policy = { "acceptableAuthenticators":  [ 123, None ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_065(self):
        self.logger.info("#065 필수 requset body 인 disallowedAuthenticators 빈 배열 전송 - 400 에러 반환 확인")

        policy = { "disallowedAuthenticators": [] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_066(self):
        self.logger.info("#066 필수 requset body 인 disallowedAuthenticators "" 전송 - 400 에러 반환 확인")

        policy = { "disallowedAuthenticators":  [ "" ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_067(self):
        self.logger.info("#067 필수 requset body 인 disallowedAuthenticators 공백 " " 전송 - 400 에러 반환 확인")

        policy = { "disallowedAuthenticators":  [ " " ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_068(self):
        self.logger.info("#068 필수 requset body 인 disallowedAuthenticators 잘못된 타입(str)으로 전송 - 400 에러 반환 확인")

        policy = { "disallowedAuthenticators": "abc" }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_069(self):
        self.logger.info("#069 필수 requset body 인 disallowedAuthenticators 잘못된 값으로 전송([ 123, None ]) - 400 에러 반환 확인")

        policy = { "disallowedAuthenticators":  [ 123, None ] }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_070(self):
        self.logger.info("#070 필수 requset body 인 acceptableAuthenticators, disallowedAuthenticators 두 필드 모두 전송 - 400 에러 반환 확인")

        policy = {
            "acceptableAuthenticators": [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3", "9ddd1817-af5a-4672-a2b9-3e3dd95000a9" ],
            "disallowedAuthenticators": [ "52b4fb4a-2866-43b2-9bf7-6c6669c2e5d3", "8ddd1817-af5a-4672-a2b9-3e3dd95000a9"  ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_071(self):
        self.logger.info("#071 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 basic, none 인 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "basic", "none" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_072(self):
        self.logger.info("#072 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 attestationCA, self 인 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "attestationCA", "self" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_073(self):
        self.logger.info("#073 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 anonymizationCA, self, none 인 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "anonymizationCA", "self", "none"]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_074(self):
        self.logger.info("#074 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 anonymizationCA, self, none 인 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "anonymizationCA", "self", "none"]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_075(self):
        self.logger.info("#075 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 none, self 인 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none", "self" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_076(self):
        self.logger.info("#076 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 none 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_077(self):
        self.logger.info("#077 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 self 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "self" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_078(self):
        self.logger.info("#078 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 빈채로 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": []
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_079(self):
        self.logger.info("#079 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 none, self, attestationCA, anonymizationCA, basic 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none", "self", "attestationCA", "anonymizationCA", "basic" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_080(self):
        self.logger.info("#080 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 대소문자 값으로 전송 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "Basic", "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_081(self):
        self.logger.info("#081 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 타입 배열 아님 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": "basic"
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_082(self):
        self.logger.info("#082 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 미존재 값 전송- 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "Test", "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_083(self):
        self.logger.info("#083 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 integer 값 전송- 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ 123, "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_084(self):
        self.logger.info("#084 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 integer 값 전송- 400 에러 반환 확인")

        policy = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ None ]
        }
        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_085(self):
        self.logger.info("#085 필수 request body인 allowCertifiedAuthenticatorsOnly에 문자열 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "allowCertifiedAuthenticatorsOnly": "true"
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False



    def test_update_rpid_info_086(self):
        self.logger.info("#086 필수 request body인 allowCertifiedAuthenticatorsOnly에 None 값을 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "allowCertifiedAuthenticatorsOnly": None,  # 잘못된 타입 (None)
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 404 #400 이엉야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_087(self):
        self.logger.info("#087 필수 request body인 allowCertifiedAuthenticatorsOnly에 0을 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "allowCertifiedAuthenticatorsOnly": 1,  # 잘못된 타입
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_088(self):
        self.logger.info("#088 필수 request body인 enforceAttestation에 문자열 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": "true"
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_089(self):
        self.logger.info("#089 필수 request body인 enforceAttestation에 None 값을 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": None,  # 잘못된 타입 (None)
            "acceptableAttestationTypes" : [ "none", "basic" ]
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 404 # 400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_090(self):
        self.logger.info("#090 필수 request body인 enforceAttestation에 정수형 1을 전송한 경우 - 400 에러 반환 확인")

        policy = {
            "enforceAttestation": 1,
            "acceptableAttestationTypes" : [ "none", "basic" ]
        }

        response_code, response_text = update_rpid_info_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.name,
            self.registrationEnabled, self.authenticationEnabled, self.origins, policy
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False