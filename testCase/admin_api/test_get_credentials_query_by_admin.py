import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_credentials_query_custom_params_api(
        base_url: str,
        admin_encoded_credentials,
        params,
        method: str = 'GET',
        space_yes: bool = False
):
    url = f"{base_url}/admin/v1/credentials"
    if space_yes:
        headers = {
            'Authorization': f'Basic{admin_encoded_credentials}'
        }
    else:
        headers = {
            'Authorization': f'Basic {admin_encoded_credentials}'
        }

    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def response_assertion(self, response_code:str, response_text:str):
    check_response_code = 200

    try:
        assert response_code == check_response_code, f"❌ Status code is {response_code} not {check_response_code}"
        body = json.loads(response_text)
        assert "id" in body and isinstance(body["id"], str) and body["id"].strip(), "❌ 'id' is missing or invalid"
        # data
        assert "data" in body and isinstance(body["data"], dict), "❌ 'data' object is missing or invalid"

        # pageInfo
        page_info = body["data"].get("pageInfo")
        assert page_info is not None and isinstance(page_info, dict), "❌ 'pageInfo' is missing or invalid"
        assert isinstance(page_info.get("page"), int), "❌ 'page' is missing or not an integer"
        assert isinstance(page_info.get("size"), int), "❌ 'size' is missing or not an integer"
        assert isinstance(page_info.get("totalElements"), int), "❌ 'totalElements' is missing or not an integer"
        assert isinstance(page_info.get("totalPages"), int), "❌ 'totalPages' is missing or not an integer"

        # content list
        content_list = body["data"].get("content")
        assert isinstance(content_list, list), "❌ 'content' is missing or not a list"

        for user in content_list:
            assert "rpId" in user and isinstance(user["rpId"], str) and user["rpId"].strip(), "❌ 'rpId' missing or invalid"
            assert "userId" in user and isinstance(user["userId"], str) and user["userId"].strip(), "❌ 'userId' missing or invalid"

            # optional fields (nullable)
            for field in ["successCount", "failCount"]:
                if field in user:
                    assert isinstance(user[field], int), f"❌ '{field}' should be int"

            for field in ["registrationDate", "firstAuthenticated", "lastAuthenticated", "lastAuthenticationFailed"]:
                if field in user:
                    assert isinstance(user[field], str), f"❌ '{field}' should be string (RFC3339 format)"

            # credentials
            # assert "credentials" in user and isinstance(user["credentials"], dict), "❌ 'credentials' missing or invalid"
            # credentials = user["credentials"]
            # for state in ["active", "inactive"]:
            #     assert state in credentials and isinstance(credentials[state], list), f"❌ '{state}' credential list missing or invalid"
            #     for cred in credentials[state]:
            #         assert isinstance(cred, str), f"❌ credential in '{state}' list is not a string"
        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, f"Exception: {e}, Response: {response_text}"

class Test_get_credentials_query:
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

    no_exist_rpId = readConfig.getValue('Admin Info', 'no_exist_clientId')

    userId = jsonUtil.readJson('credential_user', 'userId')
    credentialId = jsonUtil.readJson("credential_user", "credentialId")
    aaguid = jsonUtil.readJson("credential_user", "aaguid")

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('naver', 'clientId')
        cls.clientsecret = jsonUtil.readJson('naver', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_get_credentials_query_001(self):
        self.logger.info("#001 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - 모든 파라미터 전송")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            "sort" : "rpId,asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_002(self):
        self.logger.info("#002 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - 모든 파라미터 누락 (200 응답)")
        params = {}

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_003(self):
        self.logger.info("#003 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - rpId 로만 조회 (200 응답)")

        params = {
            "rpId" : self.client_id
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_004(self):
        self.logger.info("#004 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - userId 로만 조회 (200 응답)")

        params = {
            "userId" : self.userId
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_005(self):
        self.logger.info("#005 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - credentialId 로만 조회 (200 응답)")

        params = {
            "credentialId" : self.credentialId
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_006(self):
        self.logger.info("#006 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - active 로만 조회 (200 응답)")

        params = {
            "active" : True
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_007(self):
        self.logger.info("#007 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - active 로만 조회 (200 응답)")

        params = {
            "active" : False
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_008(self):
        self.logger.info("#008 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - aaguid 로만 조회 (200 응답)")

        params = {
            "aaguid" : self.aaguid
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_009(self):
        self.logger.info("#009 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - dateField=lastStatusChanged 로만 조회 (200 응답)")

        params = {
            "dateField" : "lastStatusChanged"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_010(self):
        self.logger.info("#010 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - dateField=registrationDate 로만 조회 (200 응답)")

        params = {
            "dateField" : "registrationDate"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)


    def test_get_credentials_query_011(self):
        self.logger.info("#011 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - dateField=lastAuthenticated 로만 조회 (200 응답)")

        params = {
            "dateField" : "lastAuthenticated"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_012(self):
        self.logger.info("#012 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - dateField=lastAuthenticationFailed 로만 조회 (200 응답)")

        params = {
            "dateField" : "lastAuthenticationFailed"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_013(self):
        self.logger.info("#013 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - from 으로만 조회 (200 응답)")

        params = {
            "from" : "2025-06-01"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_014(self):
        self.logger.info("#014 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - to 로만 조회 (200 응답)")

        params = {
            "to" : "2025-07-16"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_015(self):
        self.logger.info("#015 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - page 로만 조회 (200 응답)")

        params = {
            "page" : 0
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_016(self):
        self.logger.info("#016 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - size 로만 조회 (200 응답)")

        params = {
            "size" : 50
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_017(self):
        self.logger.info("#017 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort 로만 조회 (200 응답)")

        params = {
            "sort" : "userId,asc"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_018(self):
        self.logger.info("#018 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - rpId + userId 조회")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_019(self):
        self.logger.info("#019 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - rpId + active=false 조회")
        params = {
            "rpId" : self.client_id,
            "active" : False
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_020(self):
        self.logger.info("#020 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - rpid + dateField+ from/to 조회")
        params = {
            "rpId" : self.client_id,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_021(self):
        self.logger.info("#021 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - userId+ credentialId 조회")
        params = {
            "userId" : self.userId,
            "credentialId" : self.credentialId
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_022(self):
        self.logger.info("#022 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - credentialId + active = true 조회")
        params = {
            "credentialId" : self.credentialId,
            "active" : True
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_023(self):
        self.logger.info("#023 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - userId+ dateField+ from/to 조회")
        params = {
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_024(self):
        self.logger.info("#024 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - credentialId + dateField+ from/to 조회")
        params = {
            "credentialId" : self.credentialId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_025(self):
        self.logger.info("#025 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - page = 1 조회")
        params = { "page" : 1 }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_026(self):
        self.logger.info("#026 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - size = 0 조회")
        params = { "size" : 0 }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_027(self):
        self.logger.info("#027 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - size = 1 조회")
        params = { "size" : 1 }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_028(self):
        self.logger.info("#028 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = registrationDate,asc 설정")

        params = { "sort" : "registrationDate,asc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_029(self):
        self.logger.info("#029 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - userId,asc 설정")
        params = { "sort" : "userId,asc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_030(self):
        self.logger.info("#030 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = credential,desc&cosePublicKey,desc 설정")
        params = { "sort" : "credentialId,desc", "sort" : "cosePublicKey,desc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_031(self):
        self.logger.info("#031 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = signCount,desc&lastAuthenticated,desc 설정")
        params = { "sort" : "signCount,desc", "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_032(self):
        self.logger.info("#032 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc 설정")
        params = { "sort" : "userId,asc", "sort" : "successCount,desc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_033(self):
        self.logger.info("#033 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc&lastAuthenticated,desc 설정")
        params = { "sort" : "userId,asc", "sort" : "successCount,desc", "sort" : "lastAuthenticated,asc" }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_034(self):
        self.logger.info("#034 미존재 rpId 전송 - rpId 200 전송 확인(빈 content 전송)")

        params = {
            "rpId" : self.no_exist_rpId
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_035(self):
        self.logger.info("#035 aaguid 공백 기입 - 필수값이 아니므로 None 값으로 인식하여 200 응답 확인")

        params = {
            "aaguid" : " "
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_036(self):
        self.logger.info("#036 page = -1, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : -1
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_037(self):
        self.logger.info("#037 page 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : "10"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_038(self):
        self.logger.info("#038 page 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : 1.5
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_039(self):
        self.logger.info("#039 size = -10, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "size" : -10
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_040(self):
        self.logger.info("#040 size 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "size" : "10"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_041(self):
        self.logger.info("#041 size 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "size" : 10.5
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_042(self):
        self.logger.info("#042 sort 프로퍼티 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : ",desc"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_043(self):
        self.logger.info("#043 sort 정렬 값 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : "credentialId,"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_044(self):
        self.logger.info("#044 sort 잘못된 타입(list) 정렬, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : [ "userId", "asc" ]
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_045(self):
        self.logger.info("#045 sort 잘못된 포맷2 (빈문자열로 구성 ,,) - page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : ",,"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_046(self):
        self.logger.info("#046 sort 공백 적용, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : " "
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_047(self):
        self.logger.info("#047 sort 잘못된 조합1 (배열 타입 정렬), page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : "credentialId,desc",
            "sort" : "attestationFormats,asc"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_048(self):
        self.logger.info("#048 sort 중복 또는 충돌되는 sort 조건, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"userId,asc",
            "sort" :"userId,desc"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_credentials_query_049(self):
        self.logger.info("#049 rpId 공백 기입 - 400 에러 반환 확인")

        params = {
            "rpId" : " "
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_050(self):
        self.logger.info("#050 미존재 userId 전송 - 400 에러 반환 확인")

        params = {
            "userId" : "652ed"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_051(self):
        self.logger.info("#051 userId 공백 기입 - 400 에러 반환 확인")

        params = {
            "userId" : " "
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_052(self):
        self.logger.info("#052 미존재 credentialId 전송 - 400 에러 반환 확인")

        params = {
            "credentialId" : "652ed"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_053(self):
        self.logger.info("#053 credentialId 공백 기입 - 400 에러 반환 확인")

        params = {
            "credentialId" : " "
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_054(self):
        self.logger.info("#054 미존재 aaguid 전송 - 400 에러 반환 확인")

        params = {
            "aaguid" : "652ed"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_055(self):
        self.logger.info("#055 active invalid 타입(int) 전송 - 400 에러 반환 확인")

        params = {
            "active" : 5
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_056(self):
        self.logger.info("#056 dateField invalid 타입(int) 전송 - 400 에러 반환 확인")

        params = {
            "dateField" : 1
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_057(self):
        self.logger.info("#057 dateField 미존재 값 전송 - 400 에러 반환 확인")

        params = {
            "dateField" : "invalidField"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_058(self):
        self.logger.info("#058 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "2025/07/01"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_059(self):
        self.logger.info("#059 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "01-07-2025"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_060(self):
        self.logger.info("#060 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "20250710"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_061(self):
        self.logger.info("#061 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "2025/07/01"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_062(self):
        self.logger.info("#062 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "01-07-2025"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_063(self):
        self.logger.info("#063 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "20250710"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_064(self):
        self.logger.info("#064 sort 지원하지 않는 프로퍼티, 400 에러 반환 확인")

        params = {
            "sort" : "invalidField,asc"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_065(self):
        self.logger.info("#065 sort 미존재 정렬 값, 400 에러 반환 확인")

        params = {
            "sort" : "credentialId,wrong"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_066(self):
        self.logger.info("#066 sort 잘못된 타입(int) 정렬, 400 에러 반환 확인")

        params = {
            "sort" : 12345
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_067(self):
        self.logger.info("#067 sort 잘못된 포맷1(userId,asc,desc), 400 에러 반환 확인")

        params = {
            "sort" : "userId,asc,desc"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_068(self):
        self.logger.info("#068 sort 잘못된 포맷3 (구분자가 ,가 아닌 ;일 때), 400 에러 반환 확인")

        params = {
            "sort" : "userId;asc"
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_069(self):
        self.logger.info("#069 sort 잘못된 조합2 (& 로 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc&userId,asc"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_070(self):
        self.logger.info("#070 sort 잘못된 조합3 (credentialId,desc,userId,asc), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc,userId,asc"
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_071(self):
        self.logger.info("#071 POST 요청")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_072(self):
        self.logger.info("#072 PUT 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_073(self):
        self.logger.info("#073 DELETE 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_074(self):
        self.logger.info("#074 HEAD 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_075(self):
        self.logger.info("#075 OPTIONS 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_076(self):
        self.logger.info("#076 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_077(self):
        self.logger.info('#077 admin 아닌 권한 - passkey:rp:migration')

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_078(self):
        self.logger.info("#078 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )
        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_079(self):
        self.logger.info("#079 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_080(self):
        self.logger.info("#080 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_credentials_query_081(self):
        self.logger.info("#081 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "credentialId" : self.credentialId,
            "active" : True,
            "aaguid" : self.aaguid,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_credentials_query_custom_params_api(
            self.bUrl, self.wrong_client_encoded_credentials, params=params
        )

        check_response_code = 401 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False