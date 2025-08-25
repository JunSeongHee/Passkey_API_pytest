import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from apiGroup.controlrpIdAPI import controlRPID
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_user_summary_custom_params_api(
    base_url: str,
    admin_encoded_credentials,
    params,
    method: str = "GET",
    space_yes: bool = False
):
    url = f"{base_url}/admin/v1/users/summary"
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

        # 필수: id
        assert "id" in body and body["id"], "응답에 id 없음 또는 빈 값"

        # data 객체
        assert "data" in body and isinstance(body["data"], dict), "응답에 data 없음 또는 객체 아님"
        data = body["data"]

        # pageInfo
        assert "pageInfo" in data and isinstance(data["pageInfo"], dict), "data에 pageInfo 없음"
        pageInfo = data["pageInfo"]
        for field in ["page", "size", "totalElements", "totalPages"]:
            assert field in pageInfo, f"pageInfo에 {field} 없음"

        # content 리스트
        assert "content" in data and isinstance(data["content"], list), "data에 content 없음 또는 리스트 아님"
        content = data["content"]

        for user in content:
            # 필수값
            for field in ["rpId", "userId", "credentials"]:
                assert field in user and user[field] is not None, f"content에 {field} 없음 또는 None"
            # credentials 구조
            assert "active" in user["credentials"] and isinstance(user["credentials"]["active"], list), "credentials.active 필수"
            assert "inactive" in user["credentials"] and isinstance(user["credentials"]["inactive"], list), "credentials.inactive 필수"

            # Optional: 성공/실패/날짜 필드
            if "successCount" in user:
                assert isinstance(user["successCount"], int), "successCount int"
            if "failCount" in user:
                assert isinstance(user["failCount"], int), "failCount int"
            for dt_field in ["registrationDate", "firstAuthenticated", "lastAuthenticated", "lastAuthenticationFailed"]:
                if dt_field in user:
                    assert isinstance(user[dt_field], str), f"{dt_field}는 str (datetime) 이어야 함"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        print(f"❌ AssertionError: {e}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_get_user_summary:
    logger = LogGen.loggen()

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

    no_exist_rpId = readConfig.getValue('Admin Info', 'no_exist_clientId')
    #rpId = readConfig.getValue('basic Info', 'user_rpId') # portal.stg-passkey.com
    rpId = client_id = readConfig.getValue('Admin Info', 'client_id')
    #readConfig.getValue('basic Info', 'credential_rpId') # devocean.

    # rp - portal.stg-passkey.com
    #rpId = readConfig.getValue('basic Info', 'credential_rpId')
    # rp - naver.com
    #rpId = readConfig.getValue('basic Info', 'client_id')
    # userId, 날짜 조건 등 테스트 환경에 따라 입력 (None 가능)
    userId = "6hxIAvwo-O39tOd8_P6s6LvAB6f-UZu8IDTaPjxQ99M" #jsonUtil.readJson('data', 'userId')
    credentialId = "2xxgVt0BFNdtC3ANdYCnRLNW3S12GB88GCD0oUlsSIk"

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('naver', 'clientId')
        cls.clientsecret = jsonUtil.readJson('naver', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_get_user_summary_001(self):
        self.logger.info("#001 다양한 조건으로 User Summary 정보 Page 단위 조회")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_002(self):
        self.logger.info("#002 다양한 조건으로 User Summary 정보 Page 단위 조회 - 모든 파라미터 누락")

        params = {}
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_003(self):
        self.logger.info("#003 다양한 조건으로 User Summary 정보 Page 단위 조회 - rpIp 만으로 조회")

        params = {
            "rpId" : self.client_id
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_004(self):
        self.logger.info("#004 다양한 조건으로 User Summary 정보 Page 단위 조회 - userId 만으로 조회")

        params = {
            "userId" : self.userId
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_005(self):
        self.logger.info("#005 다양한 조건으로 User Summary 정보 Page 단위 조회 - dateField(registrationDate)만으로 조회")

        params = {
            "dateField" : "registrationDate"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_006(self):
        self.logger.info("#006 다양한 조건으로 User Summary 정보 Page 단위 조회 - dateField(firstAuthenticated) 만으로 조회")

        params = {
            "dateField" : "firstAuthenticated"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_007(self):
        self.logger.info("#007 다양한 조건으로 User Summary 정보 Page 단위 조회 - dateField(lastAuthenticated) 만으로 조회")

        params = {
            "dateField" : "lastAuthenticated"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_008(self):
        self.logger.info("#008 다양한 조건으로 User Summary 정보 Page 단위 조회 - dateField (lastAuthenticationFailed) 만으로 조회")

        params = {
            "dateField" : "lastAuthenticationFailed"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_009(self):
        self.logger.info("#009 다양한 조건으로 User Summary 정보 Page 단위 조회 - from 만으로 조회")

        params = {
            "from" : "2025-06-01"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_010(self):
        self.logger.info("#010 다양한 조건으로 User Summary 정보 Page 단위 조회 - to 만으로 조회")

        params = {
            "to" : "2025-07-16"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_011(self):
        self.logger.info("#011 다양한 조건으로 User Summary 정보 Page 단위 조회 - page 만으로 조회")

        params = {
            "page" : 0
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_012(self):
        self.logger.info("#012 다양한 조건으로 User Summary 정보 Page 단위 조회 - size 만으로 조회")

        params = {
            "size" : 50
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_013(self):
        self.logger.info("#013 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort 로만 조회 (200 응답)")

        params = {
            "sort" : "userId,asc"
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_014(self):
        self.logger.info("#014 다양한 조건으로 User Summary 정보 Page 단위 조회 - rpId + userId 조회")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_015(self):
        self.logger.info("#015 다양한 조건으로 User Summary 정보 Page 단위 조회 - rpId + userId 조회")

        params = {
            "userId" : self.userId,
            "dateField" : "lastAuthenticationFailed",
            "from" : "2025-05-01",
            "to" : "2025-07-16"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_016(self):
        self.logger.info("#016 다양한 조건으로 User Summary 정보 Page 단위 조회 - - rpid + dateField+ from/to 조회")

        params = {
            "rpId" : self.client_id,
            "dateField" : "lastAuthenticated",
            "from" : "2025-05-01",
            "to" : "2025-07-16"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_017(self):
        self.logger.info("#017 다양한 조건으로 User Summary 정보 Page 단위 조회 - - rpid + dateField+ from/to 조회")

        params = {
            "userId" : self.userId,
            "dateField" : "firstAuthenticated",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "sort" : "userId,asc"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_018(self):
        self.logger.info("#018 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - page = 1 조회")
        params = { "page" : 1 }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_019(self):
        self.logger.info("#019 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - size = 0 조회")
        params = { "size" : 0 }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_020(self):
        self.logger.info("#020 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - size = 1 조회")
        params = { "size" : 1 }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_021(self):
        self.logger.info("#021 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = registrationDate,asc 설정")

        params = { "sort" : "registrationDate,asc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_022(self):
        self.logger.info("#022 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - userId,desc 설정")
        params = { "sort" : "userId,asc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_023(self):
        self.logger.info("#023 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = credential,desc&userId,asc 설정")
        params = { "sort" : "credential,desc", "sort" : "userId,asc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_024(self):
        self.logger.info("#024 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = signCount,desc&lastAuthenticated,desc 설정")
        params = { "sort" : "signCount,desc", "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_025(self):
        self.logger.info("#025 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc 설정")
        params = { "sort" : "userId,asc", "sort" : "successCount,desc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_026(self):
        self.logger.info("#026 Query Parameters 를 이용하여 다양한 조건에 따른 Credential 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc&lastAuthenticated,desc 설정")
        params = { "sort" : "userId,asc", "sort" : "successCount,desc", "sort" : "lastAuthenticated,asc" }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_027(self):
        self.logger.info("#027 미존재 rpId 전송 - rpId 200 전송 확인(빈 content 전송)")

        if controlRPID.get_specific_rpid_info_api(self.bUrl, self.admin_encoded_credentials, self.no_exist_rpId) == 200:
            controlRPID.delete_rpId_api(self.bUrl, self.admin_encoded_credentials, self.no_exist_rpId)

        params = {
            "rpId" : self.no_exist_rpId
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_028(self):
        self.logger.info("#028 page = -1, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : -1
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_029(self):
        self.logger.info("#029 page 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : "10"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_030(self):
        self.logger.info("#030 page 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "page" : 1.5
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_user_summary_031(self):
        self.logger.info("#031 size = -10, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        params = {
            "size" : -10
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_032(self):
        self.logger.info("#032 size 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "size" : "10"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_033(self):
        self.logger.info("#033 size 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "size" : 10.5
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_034(self):
        self.logger.info("#034 sort 프로퍼티 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : ",desc"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_035(self):
        self.logger.info("#035 sort 정렬 값 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : "userId,"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_036(self):
        self.logger.info("#036 sort 잘못된 타입(list) 정렬, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : [ "userId", "asc" ]
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_037(self):
        self.logger.info("#037 sort 잘못된 포맷2 (빈문자열로 구성 ,,) - page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : ",,"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_038(self):
        self.logger.info("#038 sort " " 공백 적용, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : " "
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_039(self):
        self.logger.info("#039 sort 잘못된 조합1 (배열 타입 정렬), page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")

        params = {
            "sort" : "userId,desc",
            "sort" : "successCount,asc"
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_040(self):
        self.logger.info("#040 sort 중복 또는 충돌되는 sort 조건, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"userId,asc",
            "sort" :"userId,desc"
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_user_summary_041(self):
        self.logger.info("#041 rpId 공백 기입 - 400 에러 반환 확인")

        params = {
            "rpId" : " "
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_042(self):
        self.logger.info("#042 미존재 userId 전송 - 400 에러 반환 확인")
        params = {
            "userId" : "652ed"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_get_user_summary_043(self):
        self.logger.info("#043 userId 공백 기입 - 400 에러 반환 확인")

        params = {
            "userId" : " "
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_044(self):
        self.logger.info("#044 dateField invalid 타입(int) 전송 - 400 에러 반환 확인")

        params = {
            "dateField" : 1
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_045(self):
        self.logger.info("#045 dateField 미존재 값 전송 - 400 에러 반환 확인")

        params = {
            "dateField" : "invalidField"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_046(self):
        self.logger.info("#046 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "2025/07/01"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_047(self):
        self.logger.info("#047 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "01-07-2025"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_048(self):
        self.logger.info("#048 from 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "from" : "20250710"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_049(self):
        self.logger.info("#049 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "2025/07/01"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_050(self):
        self.logger.info("#050 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "01-07-2025"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_051(self):
        self.logger.info("#051 to 날짜 포맷 오류 - 400 에러 반환 확인")

        params = {
            "to" : "20250710"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )
        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_052(self):
        self.logger.info("#052 sort 지원하지 않는 프로퍼티, 400 에러 반환 확인")

        params = {
            "sort" : "invalidField,asc"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_053(self):
        self.logger.info("#053 sort 미존재 정렬 값, 400 에러 반환 확인")

        params = {
            "sort" : "credentialId,wrong"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_054(self):
        self.logger.info("#054 sort 잘못된 타입(int) 정렬, 400 에러 반환 확인")

        params = {
            "sort" : 12345
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_055(self):
        self.logger.info("#055 sort 잘못된 포맷1(userId,asc,desc), 400 에러 반환 확인")

        params = {
            "sort" : "userId,asc,desc"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_056(self):
        self.logger.info("#056 sort 잘못된 포맷3 (구분자가 ,가 아닌 ;일 때), 400 에러 반환 확인")

        params = {
            "sort" : "userId;asc"
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_057(self):
        self.logger.info("#057 sort 잘못된 조합2 (& 로 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"successCount,desc&userId,asc"
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_058(self):
        self.logger.info("#058 sort 잘못된 조합3 (credentialId,desc,userId,asc), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc,userId,asc"
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_059(self):
        self.logger.info("#059 POST 요청")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_060(self):
        self.logger.info("#060 PUT 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_061(self):
        self.logger.info("#061 DELETE 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_062(self):
        self.logger.info("#062 HEAD 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="HEAD"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_063(self):
        self.logger.info("#063 OPTIONS 요청")
        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }

        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_064(self):
        self.logger.info("#064 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_065(self):
        self.logger.info("#065 admin 아닌 권한 - passkey:rp:migration")

         # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_066(self):
        self.logger.info("#066 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.client_encoded_credentials, params=params
        )
        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_067(self):
        self.logger.info("#067 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
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

    def test_get_user_summary_068(self):
        self.logger.info("#068 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, params=params, space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_user_summary_069(self):
        self.logger.info("#069 헤더에 [(client id:client secret) 인코딩 값] 오입력")

        params = {
            "rpId" : self.client_id,
            "userId" : self.userId,
            "dateField" : "registrationDate",
            "from" : "2025-05-01",
            "to" : "2025-07-16",
            "page" : 0,
            "size" : 100,
            #"sort" : "rpId.asc" # 한개의 응답값만 가져오므르 에러 발생함 여러개의 credential 을 가지고 있는 userId 필요
        }
        response_code, response_text = get_user_summary_custom_params_api(
            self.bUrl, self.wrong_client_encoded_credentials, params=params
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


