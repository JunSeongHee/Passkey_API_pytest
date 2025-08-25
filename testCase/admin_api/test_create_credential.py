import base64, json, pytest, requests, time
from apiGroup.createCredentialAdminAPI import user_server_api

def test_credential_flow():
    user_server_api.registration_api()
    user_server_api.create_publickeyCredential()
    user_server_api.registration_api_response()
    time.sleep(3)
    user_server_api.authentication_api()
    user_server_api.get_publickeyCredential()
    user_server_api.authentication_api_response()
    time.sleep(3)

# def test_credential_flow():
#     for i in range(10):
#         print(f"\n[🔥] {i + 1}번째 credential flow 실행 중")
#         user_server_api.registration_api()
#         user_server_api.create_publickeyCredential()
#         user_server_api.registration_api_response()
#         time.sleep(3)
#         user_server_api.authentication_api()
#         user_server_api.get_publickeyCredential()
#         user_server_api.authentication_api_response()
#         time.sleep(3)

# @pytest.mark.parametrize("i", range(10))
# def test_credential_flow(i):
#     user_server_api.registration_api()
#     time.sleep(1)
#     user_server_api.create_publickeyCredential()
#     time.sleep(1)
#     user_server_api.registration_api_response()
#     time.sleep(3)
#     user_server_api.authentication_api()
#     time.sleep(1)
#     user_server_api.get_publickeyCredential()
#     time.sleep(1)
#     user_server_api.authentication_api_response()
#     time.sleep(3)

# from serverAPI_withJarApiServer import server_api
# @pytest.mark.parametrize("i", range(30))
# def test_001():
#     server_api.registration_api()
#     server_api.create_publickeyCredential()
#     server_api.registration_api_response()
#     time.sleep(3)
#     server_api.authentication_api()
#     server_api.get_publickeyCredential()
#     server_api.authentication_api_response()