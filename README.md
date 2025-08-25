# Python 3.13

### 2025-06-09 관련된 정보를 기재한 파일이 그 어디에도 없기에 추후 인력을 위해 기재
## 해당 문서가 무엇인지 알고 싶다면 [참고](https://docs.github.com/ko/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

---

## pip 패키지 설치

```bash
  # requests 설치
  pip install requests==2.32.3
```

```bash
  # Selenium 설치
  pip install selenium==4.33.0
```

```bash
  # pytest 설치
  pip install pytest==8.4.0
```

```bash
  # pytest-html 설치
  # report 파일을 생성에 필요한 라이브러리
  pip install pytest-html==4.1.1
```

---

## 테스트 진행

```bash
  # 일반적
  pytest testCase/admin_api/test_create_rpid_info_by_admin.py
```

```bash
  # log 표시 + log 파일 생성
  # 공통 유틸 함수를 사용, 최상위 경로에 'log' 디렉토리를 '직접' 생성해야 한다;
  pytest -o log_cli=true testCase/admin_api/test_create_rpid_info_by_admin.py
```

```bash
  # log 표시 + Report 파일 생성
  # pytest -o log_cli=true testCase/test_access_token.py --html=report/{{report_file_name}}.html --self-contained-html
  pytest -o log_cli=true testCase/admin_api/test_create_rpid_info_by_admin.py --html=report/"report_create_rpid_info_by_admin_$(date +%Y%m%d%H%M%S).html" --self-contained-html
```

---

## PyCharm IDE 사용 예시

> ## Command 실행 : 디버그 기능은 사용 못하니 주의
>> Run / Debug Configurations > Edit Configurations...
>> Add New Configuration > Shell Script > Execute : Script text
>> pytest Script 입력

> ## Pytest 실행 : 디버그 기능 사용 가능
```
>> Run / Debug Configurations > Edit Configurations...
>> Add New Configuration > Python tests > pytest
>> module > {{file_name}}.{{class_name}} ex) test_access_token.Test_access_token
>> Additional arguments > -o log_cli=true
>> Working directory > {{PycharmProjects_디렉토리_존재_경로}}/passkey_qa ex) /Users/testUser/PycharmProjects/passkey_qa
```

---

## Admin API 순차
```
> test_create_credential.py
> test_get_rp_credentials_by_admin.py
> test_get_rp_user_list_by_admin.py
> test_get_credential_base_userid_by_admin.py
> test_get_credentials_query_by_admin.py
> test_get_user_summary_by_admin.py
> test_delete_credential_by_admin.py
> test_create_rpid_info_by_admin.py
> test_register_client_basic_auth_by_admin.py
> test_check_origin_add_possibility_by_admin.py
> test_check_rpid_add_possibility_by_admin.py
> test_get_all_rpid_info_by_admin.py
> test_get_rpid_info_by_admin.py
> test_get_rp_origins_list_by_admin.py
> test_add_origin_by_admin.py
> test_delete_origin_by_admin.py
> test_get_client_clientid_basic_auth_by_admin.py
> test_get_client_list_basic_auth_by_admin.py
> test_get_policy_list_by_admin.py
> test_get_rp_option_by_admin.py
> test_update_option_by_admin.py
> test_update_policy_list_by_admin.py
> test_update_rpid_info_by_admin.py
> test_update_scope_basic_auth_client_by_admin.py
> test_update_secret_lifetime_basic_auth_client_by_admin.py
> test_update_client_secret_basic_auth_by_admin.py
> test_update_credential_status_by_admin.py
> test_delete_previous_client_secret_basic_auth_by_admin.py
> test_delete_client_basic_auth_by_admin.py
> test_delete_rpid_info_by_admin.py
```