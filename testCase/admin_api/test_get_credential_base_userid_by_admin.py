import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_credential_base_userid_api(
    base_url: str,
    admin_encoded_credentials,
    rpId: str,
    userId: str,
    page: int,
    size: int,
    sort: str,
    method: str = 'GET',
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}'
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }
    params = {
        "page": page,
        "size": size,
        "sort": sort
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def get_credential_base_userid_custom_params_api(
    base_url: str,
    admin_encoded_credentials,
    rpId: str,
    userId: str,
    params,
    method: str = 'GET'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users/{userId}/credentials"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }

    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def get_credential_base_userid_no_rpid_api(
    base_url: str,
    admin_encoded_credentials,
    userId: str,
    page: int,
    size: int,
    sort: str,
    method: str = 'GET'
):
    url = f"{base_url}/admin/v1/rps//users/{userId}/credentials"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    params = {
        "page": page,
        "size": size,
        "sort": sort
    }
    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def get_credential_base_userid_no_userid_api(
    base_url: str,
    admin_encoded_credentials,
    rpId: str,
    page: int = 0,
    size: int = 10,
    sort: str = "credentialId,desc",
    method: str = 'GET'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users//credentials"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }
    params = {
        "page": page,
        "size": size,
        "sort": sort
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

        # pageInfo 기본 검증
        assert "pageInfo" in data, "data에 pageInfo 없음"
        pageInfo = data["pageInfo"]
        for field in ["page", "size", "totalElements", "totalPages"]:
            assert field in pageInfo, f"pageInfo에 {field} 없음"

        # content 리스트 검증
        assert "content" in data, "data에 content 없음"
        content = data["content"]
        assert isinstance(content, list), "content는 리스트여야 함"

        if content:
            for cred in content:
                for field in [
                    "rpId", "userId", "credentialId", "aaguid", "userVerifyingCredential",
                    "userPresenceCredential", "discoverableCredential", "multiDeviceCredential",
                    "attestationTypeInUsed", "attestationTypes", "attestationFormat", "attestationFormats",
                    "transports", "cosePublicKey", "successCount", "failCount", "signCount", "backedUp",
                    "status", "registrationDate"
                ]:
                    assert field in cred, f"credential에 {field} 없음"
                assert cred["rpId"] == self.client_id, f"rpId 불일치: {cred['rpId']} != {self.client_id}"
                assert cred["userId"] == self.userId, f"userId 불일치: {cred['userId']} != {self.userId}"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")

    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"


class Test_get_credential_base_userid:
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

    userId = jsonUtil.readJson('credential_user', "userId") or {}

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('naver', 'clientId')
        cls.clientsecret = jsonUtil.readJson('naver', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_get_credential_base_userid_001(self):
        self.logger.info("#001 RP+UserId 기반 Credential 목록 조회")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId,
            page=0, size=10, sort="userId,desc"
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_002(self):
        self.logger.info("#002 RP+UserId 기반 Credential 목록 조회 - PATH param 값 미설정 : default 값으로 전송")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = {}

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_003(self):
        self.logger.info("#003 RP+UserId 기반 Credential 목록 조회 - page = 1 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 1 }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_004(self):
        self.logger.info("#004 RP+UserId 기반 Credential 목록 조회 - page = 999 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 999 }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_005(self):
        self.logger.info("#005 RP+UserId 기반 Credential 목록 조회 - size = 0 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 0 }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_006(self):
        self.logger.info("#006 RP+UserId 기반 Credential 목록 조회 - size = 1 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 1 }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_007(self):
        self.logger.info("#007 RP+UserId 기반 Credential 목록 조회 - size = 100 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 100 }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_008(self):
        self.logger.info("#008 RP+UserId 기반 Credential 목록 조회 - sort = registrationDate,asc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "registrationDate,asc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_009(self):
        self.logger.info("#009 RP+UserId 기반 Credential 목록 조회 - sort = registrationDate,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "registrationDate,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_010(self):
        self.logger.info("#010 RP+UserId 기반 Credential 목록 조회 - sort = aaguid,asc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "aaguid,asc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_011(self):
        self.logger.info("#011 RP+UserId 기반 Credential 목록 조회 - sort = signCount,asc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "signCount,asc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_012(self):
        self.logger.info("#012 RP+UserId 기반 Credential 목록 조회 - sort = userId,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "userId,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_013(self):
        self.logger.info("#013 RP+UserId 기반 Credential 목록 조회 - sort = lastAuthenticated,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_014(self):
        self.logger.info("#014 RP+UserId 기반 Credential 목록 조회 - sort = cosePublicKey,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "cosePublicKey,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_015(self):
        self.logger.info("#015 RP+UserId 기반 Credential 목록 조회 - sort = failCount,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "failCount,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_016(self):
        self.logger.info("#016 RP+UserId 기반 Credential 목록 조회 - sort = credential,desc&cosePublicKey,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "credential,desc", "sort" : "cosePublicKey,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_017(self):
        self.logger.info("#017 RP+UserId 기반 Credential 목록 조회 - sort = signCount,desc&lastAuthenticated,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "signCount,desc", "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_018(self):
        self.logger.info("#018 RP+UserId 기반 Credential 목록 조회 - sort = userId,asc&successCount,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "userId,asc", "sort" : "successCount,desc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_019(self):
        self.logger.info("#019 RP+UserId 기반 Credential 목록 조회 - sort = userId,asc&successCount,desc&lastAuthenticated,desc 설정")

        # 필수 값이 없을 때 skip (pytest의 skip)
        if not self.userId:
            pytest.skip("user_info 또는 rpId/userId 값이 없어 테스트를 건너뜁니다.")

        params = { "page" : 0, "size" : 200, "sort" : "userId,asc", "sort" : "successCount,desc", "sort" : "lastAuthenticated,asc" }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_020(self):
        self.logger.info("#020 미존재 rpId 전송 - rpId 200 전송 확인(빈 content 전송)")

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_clientId, self.userId, page=0, size=20, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_021(self):
        self.logger.info("#021 미존재 userId 전송 - 미존재 userId 200 전송 확인(빈 content 전송)")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, "63fdhhfdjfj" ,page=0, size=20, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_022(self):
        self.logger.info("#022 page = -1, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=-1, size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_023(self):
        self.logger.info("#023 page 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page="10", size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_024(self):
        self.logger.info("#024 page 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=1.5, size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_025(self):
        self.logger.info("#025 size = -10, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=-10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_026(self):
        self.logger.info("#026 size 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size="10", sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_027(self):
        self.logger.info("#027 size 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10.5, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_028(self):
        self.logger.info("#028 sort 프로퍼티 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = ",desc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_029(self):
        self.logger.info("#029 sort 정렬 값 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = "credentialId,"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_030(self):
        self.logger.info("#030 rpId 미기입 - 404 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, self.userId, page=0, size=20, sort="credentialId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_031(self):
        self.logger.info("#031 rpId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, " ", self.userId ,page=0, size=20, sort="credentialId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_032(self):
        self.logger.info("#032 userId 미기입 -  userId 200 전송 확인")
        response_code, response_text = get_credential_base_userid_no_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, page=0, size=20, sort="credentialId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False



    def test_get_credential_base_userid_033(self):
        self.logger.info("#033 userId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, " " ,page=0, size=20, sort="credentialId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_034(self):
        self.logger.info("#034 page = -1, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=-1, size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_035(self):
        self.logger.info("#035 page 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page="10", size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_036(self):
        self.logger.info("#036 page 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=1.5, size=10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_037(self):
        self.logger.info("#037 size = -10, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=-10, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_038(self):
        self.logger.info("#038 size 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size="10", sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_039(self):
        self.logger.info("#039 size 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10.5, sort="credentialId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_040(self):
        self.logger.info("#040 sort 프로퍼티 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = ",desc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_041(self):
        self.logger.info("#041 sort 정렬 값 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = "credentialId,"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_042(self):
        self.logger.info("#042 sort 지원하지 않는 프로퍼티, 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = "invalidField,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_043(self):
        self.logger.info("#043 sort 미존재 정렬 값, 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = "credentialId,wrong"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_044(self):
        self.logger.info("#044 sort 잘못된 타입(list) 정렬, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort =  [ "userId", "asc" ]
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_045(self):
        self.logger.info("#045 sort 잘못된 타입(int) 정렬, 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page=0, size=10, sort = 12345
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_046(self):
        self.logger.info("#046 sort 잘못된 포맷1(userId,asc,desc), 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=0, size=10, sort = "userId,asc,desc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_047(self):
        self.logger.info("#047 sort 잘못된 포맷2 (빈문자열로 구성 ,,) - page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=0, size=10, sort = ",,"
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_048(self):
        self.logger.info("#048 sort 잘못된 포맷3 (구분자가 ,가 아닌 ;일 때), 400 에러 반환 확인")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=0, size=10, sort = "userId;asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_049(self):
        self.logger.info("#049 sort " " 공백 적용, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, page=0, size=10, sort = " "
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_050(self):
        self.logger.info("#050 sort 잘못된 조합1 (배열 타입 정렬), page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" : "credentialId,desc",
            "sort" : "attestationTypes,asc"
        }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_051(self):
        self.logger.info("#051 sort 잘못된 조합2 (& 로 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc&userId,asc"
        }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_052(self):
        self.logger.info("#052 sort 잘못된 조합3 (credentialId,desc,userId,asc), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc,userId,asc"
        }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_053(self):
        self.logger.info("#053 sort 잘못된 조합4 (dict 타입과 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc",
            "sort" :"authenticatorDisplayInfo,asc"
        }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_054(self):
        self.logger.info("#054 sort 중복 또는 충돌되는 sort 조건, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"userId,asc",
            "sort" :"userId,desc"
        }

        response_code, response_text = get_credential_base_userid_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credential_base_userid_055(self):
        self.logger.info("#055 POST 요청")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc", method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_056(self):
        self.logger.info("#056 PUT 요청")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc", method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_057(self):
        self.logger.info("#057 DELETE 요청")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc", method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_058(self):
        self.logger.info("#058 HEAD 요청")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc", method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_059(self):
        self.logger.info("#059 OPTIONS 요청")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc", method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_060(self):
        self.logger.info("#060 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc"
        )
        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_061(self):
        self.logger.info("#061 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.client_encoded_credentials, self.client_id , self.userId, page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_062(self):
        self.logger.info("#062 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, self.userId, page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_063(self):
        self.logger.info("#063 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.client_encoded_credentials, self.client_id, self.userId, page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_064(self):
        self.logger.info("#064 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")
        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, self.userId,
            page="0", size=20, sort="credentialId,asc", space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credential_base_userid_065(self):
        self.logger.info("#065 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        response_code, response_text = get_credential_base_userid_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.client_id, self.userId, page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 401 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False