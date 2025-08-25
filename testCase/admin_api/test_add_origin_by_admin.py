import base64, json, pytest, requests

from urllib import parse
from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def add_origin_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        origin: str,
        method: str = 'POST',
        content_type: str = 'application/json;charset=UTF-8',
        space_yes: bool = False
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins"
    payload = {
        "origin": origin
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

def add_origin_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        origin: str,
        method: str = 'POST',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps//origins"
    payload = {
        "origin": origin
    }
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, json=payload)
    return response.status_code, response.text

def add_origin_custom_playload_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        payload,
        method: str = 'POST',
        content_type: str = 'application/json;charset=UTF-8'
):
    base_url = f"{base_url}/admin/v1/rps/{rpId}/origins"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
        'Content-Type': content_type
    }
    response = requests.request(method, base_url, headers=headers, json=payload)
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

    finally:
        if response_code == 200:  # 실제로 RP가 생성된 경우만 삭제 시도
            del_code, del_resp = controlRPID.delete_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId
            )
            if del_code == 200:
                self.logger.info(f"🧹 RP ID 삭제 성공: {self.rpId}")
            else:
                self.logger.warning(f"⚠️ RP ID 삭제 실패({del_code}): {del_resp}")

class Test_add_origin:
    logger = LogGen.loggen()

   ############### base URL
    bUrl = readConfig.getValue('Admin Info', 'bUrl')
    ############### client_id와 client_secret 을 이용해서 authorization 만들기
    # RP 이름과 비밀번호, RP URL
    admin_client_id = readConfig.getValue('Admin Info', 'clientId')
    admin_client_secret = readConfig.getValue('Admin Info', 'clientSecret')

    client_id = readConfig.getValue('Admin Info', 'client_id') # naver.com
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

    add_origin = "https://playwright.dev/dotnet/docs/intro"
    same_origin = "https://playwright.dev/"

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('client', 'clientId')
        cls.clientsecret = jsonUtil.readJson('client', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_add_orgin_001(self):
        self.logger.info("#001 RP 정보에 Origin을 추가")

        if controlRPID.check_rpid_add_possibility_api(self.bUrl, self.admin_encoded_credentials, self.rpId):
            controlRPID.create_rpId_api(
                self.bUrl, self.admin_encoded_credentials, self.rpId,
                self.name, self.registrationEnabled, self.authenticationEnabled,
                self.origins, self.policy
            )


        response_code, response_text = add_origin_api(
                    self.bUrl, self.admin_encoded_credentials,
                    self.rpId, self.add_origin
        )

        response_assertion(self, response_code, response_text)

    def test_add_orgin_002(self):
        self.logger.info("#002 rpId 누락 - 404 에러 반환 확인")
        response_code, response_text = add_origin_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, self.add_origin
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_003(self):
        self.logger.info("#003 미존재 rpId 전송 - 404 에러 반환 확인")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_clientId, self.add_origin
        )

        check_response_code = 404

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_004(self):
        self.logger.info("#004 rpId 공백 기입 - 404 에러 반환 확인")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, " ", self.add_origin
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_005(self):
        self.logger.info("#005 PUT 요청")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.add_origin, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_006(self):
        self.logger.info("#006 PATCH 요청")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.add_origin, method="PATCH"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_007(self):
        self.logger.info("#007 OPTIONS 요청")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.add_origin, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_add_orgin_008(self):
        self.logger.info("#008 미지원 Content-Type인 application/gzip 요청")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, self.add_origin, content_type="application/gzip"
        )

        check_response_code = 415

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_009(self):
        self.logger.info("#009 admin 아닌 권한 - passkey:rp 으로 요청")

        if not controlClient.get_clientid_api(self.bUrl, self.admin_encoded_credentials, self.rpId) == 200:
            controlClient.create_client_api(self.bUrl, self.admin_encoded_credentials, self.rpId, self.name, self.rp_scope)

        response_code, response_text = add_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.add_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_010(self):
        self.logger.info("#010 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = add_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.add_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_011(self):
        self.logger.info("#011 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = add_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.add_origin
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_012(self):
        self.logger.info("#012 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = add_origin_api(
            self.bUrl, self.client_encoded_credentials, self.rpId, self.add_origin
        )

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.rpId)

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_013(self):
        self.logger.info("#013 Basic + [(client id:client secret) 인코딩 값] 사이 공백")
        response_code, response_text = add_origin_api(
            self.bUrl, self.admin_encoded_credentials,
            self.rpId, self.add_origin, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_014(self):
        self.logger.info("#014 헤더에 [(client id:client secret) 인코딩 값] 오입력")
        response_code, response_text = add_origin_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.rpId, self.add_origin
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_015(self):
        self.logger.info("#015 필수 body - origin 누락")

        payload = json.dumps({})

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_016(self):
        self.logger.info("#016 필수 body - origins 미기입")

        payload = json.dumps({
            "origins": []
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400 #405 나오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_017(self):
        self.logger.info("#017 필수 body - origins '' 적용")

        payload = json.dumps({
            "origins": [ "" ]
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_018(self):
        self.logger.info("#018 필수 body - origins ' ' 공백 적용")

        payload = json.dumps({
            "origins": [ " " ]
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_019(self):
        self.logger.info("#019 필수 body - origins 잘못된 형식 적용")

        payload = json.dumps({
            "origins": [ "not-a-url" ]
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_020(self):
        self.logger.info("#020 필수 body - origins 잘못된 타입 str 적용")

        payload = json.dumps({
            "origins": "https://playwright.dev/python/"
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_021(self):
        self.logger.info("#021 필수 body - origins 잘못된 타입 dict 적용")

        payload = json.dumps({
            "origins": { "https://playwright.dev/dotnet/" : "https://playwright.dev/dotnet/docs/docker" }
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_origins_list_022(self):
        self.logger.info("#022 필수 body - 존재하는 origins 추가")

        payload = json.dumps({
            "origins": self.same_origin
        })

        response_code, response_text = add_origin_custom_playload_api(
            self.bUrl, self.admin_encoded_credentials, self.rpId, payload=payload
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False