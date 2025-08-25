import base64, json, pytest, requests

from apiGroup.controlclientAPI import controlClient
from util import jsonUtil
from util.customLogger import LogGen
from util.readProperties import readConfig

def get_rp_user_list_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        page: int,
        size: int,
        sort: str,
        method: str = 'GET',
        space_yes: bool = False
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users"
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

def get_rp_credentials_custom_params_api(
        base_url: str,
        admin_encoded_credentials,
        rpId: str,
        params,
        method: str = 'GET'
):
    url = f"{base_url}/admin/v1/rps/{rpId}/users"
    headers = {
        'Authorization': f'Basic {admin_encoded_credentials}',
    }

    response = requests.request(method, url, headers=headers, params=params)
    return response.status_code, response.text

def get_rp_user_list_no_rpid_api(
        base_url: str,
        admin_encoded_credentials,
        page: int,
        size: int,
        sort: str,
        method: str = 'GET'
):
    url = f"{base_url}/admin/v1/rps//users"
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

        assert "id" in body and body["id"], "응답에 id 없음 또는 빈 값"

        # data 객체 필수
        assert "data" in body and isinstance(body["data"], dict), "응답에 data 없음 또는 객체 아님"
        data = body["data"]

        # pageInfo 필수 및 내부 필드
        assert "pageInfo" in data and isinstance(data["pageInfo"], dict), "data에 pageInfo 없음"
        pageInfo = data["pageInfo"]
        for field in ["page", "size", "totalElements", "totalPages"]:
            assert field in pageInfo, f"pageInfo에 {field} 없음"

        # content 필수 (리스트)
        assert "content" in data and isinstance(data["content"], list), "data에 content 없음 또는 리스트 아님"
        content = data["content"]
        # userId 개수 확인
        user_ids = [user["userId"] for user in content if "userId" in user]
        user_count = len(user_ids)

        self.logger.info(f"✅ 조회된 사용자 수 (userId 기준): {user_count}")
                    # 각 content item 검증 (있을 때만)
        for user in content:
            # 필수값
            for field in ["rpId", "userId"]:
                assert field in user and user[field], f"content에 {field} 없음 또는 빈 값"
            # Optional 값 (있으면 타입만 체크)
            for num_field in ["successCount", "failCount"]:
                if num_field in user:
                    assert isinstance(user[num_field], int), f"{num_field}는 int여야 함"
            for dt_field in ["registrationDate", "firstAuthenticated", "lastAuthenticated", "lastAuthenticationFailed"]:
                if dt_field in user:
                    assert isinstance(user[dt_field], str), f"{dt_field}는 str (datetime) 이어야 함"

        self.logger.info(f"body : {json.dumps(body, indent=2, ensure_ascii=False)}")
        self.logger.info("🟢 TEST PASS")
    except AssertionError as e:
        self.logger.error(f"❌ 테스트 실패: {e} - {response_text}")
        assert False, str(e)
    except Exception as e:
        self.logger.error(f"❌ 응답 구조 파싱 실패: {e}")
        assert False, "응답 구조가 올바르지 않음"

class Test_get_rp_user_list:
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

    @classmethod
    def setup_class(cls):
        cls.clientid = jsonUtil.readJson('naver', 'clientId')
        cls.clientsecret = jsonUtil.readJson('naver', 'clientSecret')

        cls.logger.info(f"cls.clientid {cls.clientid}, cls.clientsecret - {cls.clientsecret}")

        re_credentials = f"{cls.clientid}:{cls.clientsecret}"
        cls.client_encoded_credentials = base64.b64encode(re_credentials.encode("utf-8")).decode("utf-8")
        cls.wrong_client_encoded_credentials = cls.client_encoded_credentials + "_wrong_credentials"

    def test_get_rp_user_list_001(self):
        self.logger.info("#001 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회")

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, page=0, size=200, sort="registrationDate,desc"
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_002(self):
        self.logger.info("#002 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - PATH param 값 미설정 : default 값으로 전송")

        params = {}

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_003(self):
        self.logger.info("#003 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - page = 1 설정")

        params = { "page" : 1 }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_004(self):
        self.logger.info("#004 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - page = 999 설정")

        params = { "page" : 999 }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_005(self):
        self.logger.info("#005 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - size = 0 설정")

        params = { "page" : 0, "size" : 0 }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_006(self):
        self.logger.info("#006 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - size = 1 설정")

        params = { "page" : 0, "size" : 1 }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_007(self):
        self.logger.info("#007 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - size = 100 설정")

        params = { "page" : 0, "size" : 100 }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_008(self):
        self.logger.info("#008 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = registrationDate,asc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "registrationDate,asc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_009(self):
        self.logger.info("#009 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - size = registrationDate,desc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "registrationDate,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_010(self):
        self.logger.info("#010 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = successCount,asc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "successCount,asc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_011(self):
        self.logger.info("#011 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = userId,asc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "userId,asc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_012(self):
        self.logger.info("#012 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = userId,desc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "userId,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_013(self):
        self.logger.info("#013 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = lastAuthenticated,desc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_014(self):
        self.logger.info("#014 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = lastAuthenticated,asc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "lastAuthenticated,asc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_015(self):
        self.logger.info("#015 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = failCount,desc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "failCount,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_016(self):
        self.logger.info("#016 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = lastAuthenticationFailed,desc 설정")

        params = { "page" : 0, "size" : 20, "sort" : "lastAuthenticationFailed,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_017(self):
        self.logger.info("#017 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = signCount,desc&lastAuthenticated,desc 설정 설정")

        params = { "page" : 0, "size" : 200, "sort" : "signCount,desc", "sort" : "lastAuthenticated,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_018(self):
        self.logger.info("#018 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc 설정")

        params = { "page" : 0, "sort" : "userId,asc", "sort" : "successCount,desc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_019(self):
        self.logger.info("#019 RP (RP ID)를 기반으로 등록된 User 정보를 Page 단위로 조회 - sort = userId,asc&successCount,desc&lastAuthenticated,desc 설정")

        params = { "page" : 0, "size" : 200, "sort" : "userId,asc", "sort" : "successCount,desc", "sort" : "lastAuthenticated,asc" }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )
        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_020(self):
        self.logger.info("#020 미존재 rpId 전송 - rpId 200 전송 확인(빈 content 전송)")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.no_exist_clientId ,page=0, size=20, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_021(self):
        self.logger.info("#021 page = -1, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=-1, size=10, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_022(self):
        self.logger.info("#022 page 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="10", size=10, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_023(self):
        self.logger.info("#023 page 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=1.5, size=10, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_024(self):
        self.logger.info("#024 size = -10, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=-10, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_025(self):
        self.logger.info("#025 size 값 문자열 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size="10", sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_026(self):
        self.logger.info("#026 size 값 float 타입 오류, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10.5, sort="userId,asc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_027(self):
        self.logger.info("#027 sort 프로퍼티 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = ",desc"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_028(self):
        self.logger.info("#028 sort 정렬 값 누락, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = "userId,"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_029(self):
        self.logger.info("#029 sort 잘못된 타입(list) 정렬, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort =  [ "userId", "asc" ]
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_030(self):
        self.logger.info("#030 sort 잘못된 포맷2 (빈문자열로 구성 ,,) - page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = ",,"
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_031(self):
        self.logger.info("#031 sort " " 공백 적용, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = " "
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_032(self):
        self.logger.info("#032 sort 중복 또는 충돌되는 sort 조건, page/size/sort 잘못된 값 전달 시, default 값으로  전송되므로 200 응답 전송 확인")
        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"userId,asc",
            "sort" :"userId,desc"
        }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )

        response_assertion(self, response_code, response_text)

    def test_get_rp_user_list_033(self):
        self.logger.info("#033 rpId 미기입 - 404 에러 반환 확인")
        response_code, response_text = get_rp_user_list_no_rpid_api(
            self.bUrl, self.admin_encoded_credentials, page=0, size=20, sort="credentialId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_034(self):
        self.logger.info("#034 rpId 공백 기입 - 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, " " ,
            page=0, size=20, sort="userId,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False


    def test_get_rp_user_list_035(self):
        self.logger.info("#035 sort 지원하지 않는 프로퍼티, 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = "invalidField,asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_036(self):
        self.logger.info("#036 sort 미존재 정렬 값, 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = "credentialId,wrong"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_037(self):
        self.logger.info("#037 sort 잘못된 타입(int) 정렬, 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = 12345
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_038(self):
        self.logger.info("#038 sort 잘못된 포맷1(userId,asc,desc), 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = "userId,asc,desc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_039(self):
        self.logger.info("#039 sort 잘못된 포맷3 (구분자가 ,가 아닌 ;일 때), 400 에러 반환 확인")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page=0, size=10, sort = "userId;asc"
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_040(self):
        self.logger.info("#040 sort 잘못된 조합1 (배열 타입 정렬), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" : "credentialId,desc",
            "sort" : "attestationTypes,asc"
        }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_041(self):
        self.logger.info("#041 sort 잘못된 조합2 (& 로 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc&userId,asc"
        }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_042(self):
        self.logger.info("#042 sort 잘못된 조합3 (credentialId,desc,userId,asc), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc,userId,asc"
        }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_043(self):
        self.logger.info("#043 sort 잘못된 조합4 (dict 타입과 연결), 400 에러 반환 확인")

        params = {
            "page" : 0,
            "size" : 10,
            "sort" :"credentialId,desc",
            "sort" :"authenticatorDisplayInfo,asc"
        }

        response_code, response_text = get_rp_credentials_custom_params_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id, params=params
        )

        check_response_code = 400

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_044(self):
        self.logger.info("#044 POST 요청")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="0", size=20, sort="successCount,asc", method="POST"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_045(self):
        self.logger.info("#045 PUT 요청")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="0", size=20, sort="successCount,asc", method="PUT"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_046(self):
        self.logger.info("#046 DELETE 요청")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="0", size=20, sort="successCount,asc", method="DELETE"
        )

        check_response_code = 405

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_047(self):
        self.logger.info("#047 HEAD 요청")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="0",
            size=20, sort="successCount,asc", method="HEAD"
        )

        check_response_code = 200 # 400 응답 오고 있음

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}, response_text - {response_text}")
            assert False

    def test_get_rp_user_list_048(self):
        self.logger.info("#048 OPTIONS 요청")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,page="0", size=20, sort="successCount,asc", method="OPTIONS"
        )

        check_response_code = 200

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_049(self):
        self.logger.info("#049 admin 아닌 권한 - passkey:rp")

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.client_encoded_credentials, self.client_id ,page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_050(self):
        self.logger.info("#050 admin 아닌 권한 - passkey:rp:migration")

        # migration 권한 부여 시도
        update_result = controlClient.update_client_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.client_encoded_credentials, self.client_id ,page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_051(self):
        self.logger.info("#051 admin 아닌 권한 - passkey:rp, passkey:rp:migration")

        update_result = controlClient.update_client_rp_migration_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.client_encoded_credentials, self.client_id ,page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_052(self):
        self.logger.info("#052 권한 없이 요청")

        update_result = controlClient.update_client_no_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)
        assert update_result == 200, "❌ client scope 업데이트 실패로 테스트 중단"

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.client_encoded_credentials, self.client_id ,
            page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 403

        update_result = controlClient.update_client_re_scopes_api(self.bUrl, self.admin_encoded_credentials, self.client_id)

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_053(self):
        self.logger.info("#053 Basic + [(client id:client secret) 인코딩 값] 사이 공백 누락")

        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.admin_encoded_credentials, self.client_id ,
            page="0", size=20, sort="credentialId,asc", space_yes=True
        )

        check_response_code = 401

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False

    def test_get_rp_user_list_054(self):
        self.logger.info("#054 헤더에 [(client id:client secret) 인코딩 값] 오입력")
        response_code, response_text = get_rp_user_list_api(
            self.bUrl, self.wrong_client_encoded_credentials, self.client_id ,page="0", size=20, sort="credentialId,asc"
        )

        check_response_code = 401 # 401??

        if response_code == check_response_code:
            assert True
            self.logger.info("🟢 TEST PASS")
        else:
            self.logger.info(f"❌ Status code is {response_code} not {check_response_code}")
            assert False