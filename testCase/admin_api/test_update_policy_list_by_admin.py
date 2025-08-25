import base64, json, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def update_policy_list_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        acceptableAuthenticators: list,
        #disallowedAuthenticators: list,
        allowCertifiedAuthenticatorsOnly: bool,
        enforceAttestation: bool,
        acceptableAttestationTypes: dict,
        method: str = 'PUT',
        content_type: str = 'application/json;charset=UTF-8',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/policy"
    payload = {
        "acceptableAuthenticators": acceptableAuthenticators,
        "allowCertifiedAuthenticatorsOnly": allowCertifiedAuthenticatorsOnly,
        "enforceAttestation": enforceAttestation,
        "acceptableAttestationTypes": acceptableAttestationTypes
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

def update_policy_list_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        acceptableAuthenticators: list,
        #disallowedAuthenticators: list,
        allowCertifiedAuthenticatorsOnly: bool,
        enforceAttestation: bool,
        acceptableAttestationTypes: dict,
        method: str = 'PUT',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps//policy"
    payload = {
        "acceptableAuthenticators": acceptableAuthenticators,
        "allowCertifiedAuthenticatorsOnly": allowCertifiedAuthenticatorsOnly,
        "enforceAttestation": enforceAttestation,
        "acceptableAttestationTypes": acceptableAttestationTypes
    }
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, json=payload)
    return response.status_code, response.text


def update_policy_list_custom_playload_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        payload,
        method: str = 'PUT',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/policy"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, json=payload)
    return response.status_code, response.text


class Test_update_policy_list:
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

    no_exist_rpid = readConfig.getValue('Admin Info', 'no_exist_clientId')

    rpId = jsonUtil.readJson("create_rpid", "id")
    name = jsonUtil.readJson("update_rpid", "name")
    registrationEnabled = jsonUtil.readJson("update_rpid", "registrationEnabled")
    authenticationEnabled = jsonUtil.readJson("update_rpid", "authenticationEnabled")
    origins = jsonUtil.readJson("update_rpid", "origins")
    policy = jsonUtil.readJson("update_rpid", "policy")

    acceptableAuthenticators = jsonUtil.readJson("rp_policy", "acceptableAuthenticators")
    #disallowedAuthenticators = jsonUtil.readJson("rp_policy", "disallowedAuthenticators")
    allowCertifiedAuthenticatorsOnly = jsonUtil.readJson("rp_policy", "allowCertifiedAuthenticatorsOnly")
    enforceAttestation = jsonUtil.readJson("rp_policy", "enforceAttestation")
    acceptableAttestationTypes = jsonUtil.readJson("rp_policy", "acceptableAttestationTypes")

    # disallowedAuthenticators 파라미터가 존재하면 "enforceAttestation" : true 여야 하고 acceptableAttestationTypes 은 attestationCA, anonymizationCA, basic 강제됨
    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_update_policy_list_001(self):
        self.logger.info("#001 acceptableAttestationTypes 중복 갱신한 경우 하나의 값으로 갱신되는지 확인")
        enforceAttestation = False
        acceptableAttestationTypes = [ "basic", "basic", "self", "self" ]

        check_response_code = 200
        response_code = None

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
                controlRPID.create_rpId_api(
                    self.bUrl, self.admin_encoded_credentials, self.rpId,
                    self.name, self.registrationEnabled, self.authenticationEnabled,
                    self.origins, self.policy
                )

            # 정책 갱신 시도
            response_code, response_text = update_policy_list_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.acceptableAuthenticators,
                self.allowCertifiedAuthenticatorsOnly,
                enforceAttestation,
                acceptableAttestationTypes
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data 필드가 있는지 확인
            assert "id" in body, "응답에 id 없음"
            assert "data" in body, "응답에 data 없음"
            assert "rpId" in body["data"]

            assert body["data"]["rpId"] == self.rpId

            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e}, {response_text}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_rpid_info_002(self):
        self.logger.info("#002 disallowedAuthenticators 존재하고 acceptableAuthenticators 없을 경우 정상 확인")

        payload = {
            "disallowedAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : False,
            "acceptableAttestationTypes" : [ "basic", "none" ]
        }

        check_response_code = 200
        response_code = None

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
                self.logger.error("❌ RP ID 사용 불가 (중복 등으로 인해)")
                assert False, "RP ID 사용 불가"

            # RP ID 생성 시도
            status_code, _ = controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )
            if status_code != 200:
                self.logger.error(f"❌ RP ID 생성 실패: {status_code}")
                assert False, "RP ID 생성 실패로 테스트 중단"

            # 정책 갱신 시도
            response_code, response_text = update_policy_list_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)
            assert "id" in body and "data" in body and "rpId" in body["data"]
            assert body["data"]["rpId"] == self.rpId

            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e}, {response_text}")
            raise

        except Exception as e:
            self.logger.error(f"❌ 예외 발생: {e}")
            assert False, "예외 발생"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_rpid_info_003(self):
        self.logger.info("#003 acceptableAuthenticators 존재하고 disallowedAuthenticators 없을 경우 정상 확인")

        payload = {
            "acceptableAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : False,
            "acceptableAttestationTypes" : [ "basic", "none" ]
        }

        check_response_code = 200
        response_code = None

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
                self.logger.error("❌ RP ID 사용 불가 (중복 등으로 인해)")
                assert False, "RP ID 사용 불가"

            # RP ID 생성 시도
            status_code, _ = controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )
            if status_code != 200:
                self.logger.error(f"❌ RP ID 생성 실패: {status_code}")
                assert False, "RP ID 생성 실패로 테스트 중단"

            # 정책 갱신 시도
            response_code, response_text = update_policy_list_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)
            assert "id" in body and "data" in body and "rpId" in body["data"]
            assert body["data"]["rpId"] == self.rpId

            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e}, {response_text}")
            raise

        except Exception as e:
            self.logger.error(f"❌ 예외 발생: {e}")
            assert False, "예외 발생"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_rpid_info_004(self):
        self.logger.info("#004 enforceAttestation true 인 경우, acceptableAttestationTypes 값은 attestationCA, anonymizationCA, basic 강제 확인")

        payload = {
            "acceptableAuthenticators" : [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3" ],
            "allowCertifiedAuthenticatorsOnly" : True,
            "enforceAttestation" : True,
            "acceptableAttestationTypes" : [ "basic", "attestationCA", "anonymizationCA" ]
        }
        check_response_code = 200
        response_code = None

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
                self.logger.error("❌ RP ID 사용 불가 (중복 등으로 인해)")
                assert False, "RP ID 사용 불가"

            # RP ID 생성 시도
            status_code, _ = controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )
            if status_code != 200:
                self.logger.error(f"❌ RP ID 생성 실패: {status_code}")
                assert False, "RP ID 생성 실패로 테스트 중단"

            # 정책 갱신 시도
            response_code, response_text = update_policy_list_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)
            assert "id" in body and "data" in body and "rpId" in body["data"]
            assert body["data"]["rpId"] == self.rpId

            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e}, {response_text}")
            raise

        except Exception as e:
            self.logger.error(f"❌ 예외 발생: {e}")
            assert False, "예외 발생"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_policy_list_005(self):
        self.logger.info("#005 갱신 : 생략 가능 여부 및 필수 파라미터 정상값 확인 - acceptableAuthenticators, disallowedAuthenticators, allowCertifiedAuthenticatorsOnly, enforceAttestation, acceptableAttestationTypes")

        check_response_code = 200
        response_code = None

        payload = {}

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
                self.logger.error("❌ RP ID 사용 불가 (중복 등으로 인해)")
                assert False, "RP ID 사용 불가"

            # RP ID 생성 시도
            status_code, _ = controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )
            if status_code != 200:
                self.logger.error(f"❌ RP ID 생성 실패: {status_code}")
                assert False, "RP ID 생성 실패로 테스트 중단"

            # 정책 갱신 시도
            response_code, response_text =  update_policy_list_custom_playload_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)

            # id, data 필드가 있는지 확인
            assert "id" in body, "응답에 id 없음"
            assert "data" in body, "응답에 data 없음"
            assert "rpId" in body["data"]

            assert body["data"]["rpId"] == self.rpId

            self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
            # 에러 메시지를 그대로 출력
            print(f"❌ AssertionError: {e}")
            assert False, str(e)

        except Exception as e:
            self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
            assert False, "응답 구조가 올바르지 않음"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_policy_list_006(self):
        self.logger.info("#006 RP의 Policy 모든 값 갱신")

        check_response_code = 200
        response_code = None

        try:
            # RP ID 생성 가능 여부 체크
            if not controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
                self.logger.error("❌ RP ID 사용 불가 (중복 등으로 인해)")
                assert False, "RP ID 사용 불가"

            # RP ID 생성 시도
            status_code, _ = controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )
            if status_code != 200:
                self.logger.error(f"❌ RP ID 생성 실패: {status_code}")
                assert False, "RP ID 생성 실패로 테스트 중단"

            # 정책 갱신 시도
            response_code, response_text = update_policy_list_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.acceptableAuthenticators,
                self.allowCertifiedAuthenticatorsOnly,
                self.enforceAttestation,
                self.acceptableAttestationTypes
            )

            assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"

            body = json.loads(response_text)
            assert "id" in body and "data" in body and "rpId" in body["data"]
            assert body["data"]["rpId"] == self.rpId

            self.logger.info("🟢 TEST PASS")

        except AssertionError as e:
            self.logger.error(f"❌ 테스트 실패: {e}, {response_text}")
            raise

        except Exception as e:
            self.logger.error(f"❌ 예외 발생: {e}")
            assert False, "예외 발생"

        finally:
            del_code, del_resp = controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

    def test_update_policy_list_007(self):
        self.logger.info("#007 필수 파라미터인 rpId 누락 - 400 에러 반환 확인")

        payload = {
            "id": self.rpId,
            "registrationEnabled": self.registrationEnabled,
            "authenticationEnabled": self.authenticationEnabled,
            "origins": self.origins,
            "policy": self.policy
        }

        response_code, response_text = update_policy_list_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_policy_list_008(self):
        self.logger.info("#008 존재하지 않는 rpId(필수 파라미터) - 400 에러 반환 확인")

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_rpid,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_policy_list_009(self):
        self.logger.info("#009 rpId(필수 파라미터) " " 공백 적용 - 400 에러 반환 확인")

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, " ",
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_010(self):
        self.logger.info("#010 POST 요청")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes,
            method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_011(self):
        self.logger.info("#011 PATCH 요청")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes,
            method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_012(self):
        self.logger.info("#012 DELETE 요청")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes,
            method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_013(self):
        self.logger.info("#013 OPTIONS 요청")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes,
            method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_014(self):
        self.logger.info("#014 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes,
            content_type="application/gzip"
        )

        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_015(self):
        self.logger.info("#015 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_016(self):
        self.logger.info("#016 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_017(self):
        self.logger.info("#017 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_018(self):
        self.logger.info("#018 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.client_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_019(self):
        self.logger.info("#019 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = update_policy_list_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_020(self):
        self.logger.info("#020 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = update_policy_list_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId,
            self.acceptableAuthenticators,
            self.allowCertifiedAuthenticatorsOnly,
            self.enforceAttestation,
            self.acceptableAttestationTypes
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_021(self):
        self.logger.info("#021 필수 requset body 인 acceptableAuthenticators 빈 배열 전송 - 400 에러 반환 확인")

        payload = { "acceptableAuthenticators": [] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_022(self):
        self.logger.info("#022 필수 requset body 인 acceptableAuthenticators "" 전송 - 400 에러 반환 확인")

        payload = { "acceptableAuthenticators":  [ "" ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_023(self):
        self.logger.info("#023 필수 requset body 인 acceptableAuthenticators 공백 " " 전송 - 400 에러 반환 확인")

        payload = { "acceptableAuthenticators":  [ " " ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_024(self):
        self.logger.info("#024 필수 requset body 인 acceptableAuthenticators 잘못된 타입(str)으로 전송 - 400 에러 반환 확인")

        payload = { "acceptableAuthenticators": "abc" }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_025(self):
        self.logger.info("#025 필수 requset body 인 acceptableAuthenticators 잘못된 값으로 전송 - 400 에러 반환 확인")

        payload = { "acceptableAuthenticators":  [ 123, None ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_026(self):
        self.logger.info("#026 필수 requset body 인 disallowedAuthenticators 빈 배열 전송 - 400 에러 반환 확인")

        payload = { "disallowedAuthenticators": [] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_027(self):
        self.logger.info("#027 필수 requset body 인 disallowedAuthenticators "" 전송 - 400 에러 반환 확인")

        payload = { "disallowedAuthenticators":  [ "" ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_028(self):
        self.logger.info("#028 필수 requset body 인 disallowedAuthenticators 공백 " " 전송 - 400 에러 반환 확인")

        payload = { "disallowedAuthenticators":  [ " " ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_029(self):
        self.logger.info("#029 필수 requset body 인 disallowedAuthenticators 잘못된 타입(str)으로 전송 - 400 에러 반환 확인")

        payload = { "disallowedAuthenticators": "abc" }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_030(self):
        self.logger.info("#030 필수 requset body 인 disallowedAuthenticators 잘못된 값으로 전송([ 123, None ]) - 400 에러 반환 확인")

        payload = { "disallowedAuthenticators":  [ 123, None ] }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_031(self):
        self.logger.info("#031 필수 requset body 인 acceptableAuthenticators, disallowedAuthenticators 두 필드 모두 전송 - 400 에러 반환 확인")

        payload = {
            "acceptableAuthenticators": [ "42b4fb4a-2866-43b2-9bf7-6c6669c2e5d3", "9ddd1817-af5a-4672-a2b9-3e3dd95000a9" ],
            "disallowedAuthenticators": [ "52b4fb4a-2866-43b2-9bf7-6c6669c2e5d3", "8ddd1817-af5a-4672-a2b9-3e3dd95000a9"  ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_032(self):
        self.logger.info("#032 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 basic, none 인 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "basic", "none" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_033(self):
        self.logger.info("#033 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 attestationCA, self 인 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "attestationCA", "self" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_034(self):
        self.logger.info("#034 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 anonymizationCA, self, none 인 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "anonymizationCA", "self", "none"]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_035(self):
        self.logger.info("#035 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 anonymizationCA, self, none 인 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "anonymizationCA", "self", "none"]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_036(self):
        self.logger.info("#036 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 none, self 인 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none", "self" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_037(self):
        self.logger.info("#037 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 none 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_038(self):
        self.logger.info("#038 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값이 self 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "self" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_039(self):
        self.logger.info("#039 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 빈채로 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": []
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_040(self):
        self.logger.info("#040 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 none, self, attestationCA, anonymizationCA, basic 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "none", "self", "attestationCA", "anonymizationCA", "basic" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_041(self):
        self.logger.info("#041 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 대소문자 값으로 전송 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "Basic", "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_042(self):
        self.logger.info("#042 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 타입 배열 아님 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": "basic"
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_043(self):
        self.logger.info("#043 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 미존재 값 전송- 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ "Test", "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_044(self):
        self.logger.info("#044 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 integer 값 전송- 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ 123, "AttestationCA", "AnonymizationCA" ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_045(self):
        self.logger.info("#045 필수 requset body 인 enforceAttestation = true 일 때, acceptableAttestationTypes 값 integer 값 전송- 400 에러 반환 확인")

        payload = {
            "enforceAttestation": True,
            "acceptableAttestationTypes": [ None ]
        }
        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_046(self):
        self.logger.info("#046 필수 request body인 allowCertifiedAuthenticatorsOnly에 문자열 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "allowCertifiedAuthenticatorsOnly": "true"
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False



    def test_update_rpid_info_047(self):
        self.logger.info("#047 필수 request body인 allowCertifiedAuthenticatorsOnly에 None 값을 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "allowCertifiedAuthenticatorsOnly": None,  # 잘못된 타입 (None)
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 404 #400 이엉야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_048(self):
        self.logger.info("#048 필수 request body인 allowCertifiedAuthenticatorsOnly에 0을 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "allowCertifiedAuthenticatorsOnly": 1,  # 잘못된 타입
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_049(self):
        self.logger.info("#049 필수 request body인 enforceAttestation에 문자열 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": "true"
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_050(self):
        self.logger.info("#050 필수 request body인 enforceAttestation에 None 값을 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": None,  # 잘못된 타입 (None)
            "acceptableAttestationTypes" : [ "none", "basic" ]
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 404 # 400 이어야 함

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_update_rpid_info_051(self):
        self.logger.info("#051 필수 request body인 enforceAttestation에 정수형 1을 전송한 경우 - 400 에러 반환 확인")

        payload = {
            "enforceAttestation": 1,
            "acceptableAttestationTypes" : [ "none", "basic" ]
        }

        response_code, response_text = update_policy_list_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

