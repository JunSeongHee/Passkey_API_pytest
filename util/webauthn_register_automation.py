import json, requests, base64, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from util.readProperties import readConfig
from util import jsonUtil
from apiGroup.authenticationAPI import useCredential
from apiGroup.registrationAPI import createCredential


class WRA:

    def run_webauthn_registration(self, logger, name, displayName):
        # Webauthn 등록
        result, driver = WRA.webAuthn_registration(self, name, displayName)

        # 결과 처리
        if "error" in result:
            logger.info(f"[❌] Registration failed: {result['error']}")
        else:
            logger.info('[✅] Registration successful!')
            # 결과를 data.json에 저장
            # 1. JSON 파일 열기 (읽기)
            with open('./testData/data.json', 'r') as file:
                data = json.load(file)

            # 2. abc 키 추가 또는 수정

            data['clientDataJson'] = result["response"]["clientDataJSON"]
            data['attestationObject'] = result["response"]["attestationObject"].rstrip("=")

            # 3. JSON 파일 다시 쓰기
            with open('./testData/data.json', 'w') as file:
                json.dump(data, file, indent=4)
        driver.quit()

    def run_webauthn_registration_and_Authentication(self, logger, name, displayName):
        # Webauthn 등록
        reg_result, driver = WRA.webAuthn_registration(self, name, displayName)

        if "error" in reg_result:
            logger.info(f"[❌] Registration failed: {reg_result['error']}")
            driver.quit()
            return

        logger.info('[✅] Registration successful!')
        # credential_id 추출 및 저장
        credential_id_b64url = reg_result["id"]
        global credential_id_bytes
        credential_id_bytes = WRA.b64url_decode(self, credential_id_b64url)

        # 결과 저장
        with open('./testData/data.json', 'r') as file:
            data = json.load(file)
        data['clientDataJson'] = reg_result["response"]["clientDataJSON"]
        clientDataJson = reg_result["response"]["clientDataJSON"]
        data['attestationObject'] = reg_result["response"]["attestationObject"].rstrip("=")
        attestationObject = reg_result["response"]["attestationObject"].rstrip("=")
        data['credentialId'] = credential_id_b64url
        with open('./testData/data.json', 'w') as file:
            json.dump(data, file, indent=4)

        # 데이터 준비
        transactionId = jsonUtil.readJson('data', 'transactionId')
        bUrl = readConfig.getValue('basic Info', 'bUrl')
        userId = jsonUtil.readJson('data', 'userId')
        token = jsonUtil.readJson('data', 'access Token')
        client_id = readConfig.getValue('basic Info', 'client_id')
        # 등록 결과 전송
        response_code, response_text = createCredential.registration_api_response(bUrl, transactionId, clientDataJson, attestationObject, userId, token, client_id)
        response_json = json.loads(response_text)
        if response_code == 200:
            logger.info('[✅] 등록 결과 전송 성공')
            jsonUtil.writeJson("data", "credentialId", response_json["data"]["authenticator"]["credentialId"])

        # 인증 옵션 요청
        response_code, response_text = useCredential.authentication_api(bUrl, userId, token, client_id)
        response_json = json.loads(response_text)
        auth_transactionId = response_json["data"]["transactionId"]
        options_str = response_json["data"]["options"]
        logger.info('[✅] 인증 옵션 요청 통과')
        time.sleep(1)
        # transaction ID와 options를 data.json 파일에 저장
        jsonUtil.writeJson('data', "auth_transactionId", auth_transactionId)
        jsonUtil.writeJson('data', "assertionOptions", options_str)

        # Webauthn 인증
        auth_result = WRA.webauthn_authentication(self, driver)

        if "error" in auth_result:
            logger.info(f"[❌] Authentication failed: {auth_result['error']}")
        else:
            logger.info('[✅] Authentication successful!')
            logger.info(auth_result)
            jsonUtil.writeJson("data", "clientDataJson_auth", auth_result["response"]["clientDataJSON"])
            jsonUtil.writeJson("data", "authenticatorData", auth_result["response"]["authenticatorData"])
            jsonUtil.writeJson("data", "signature", auth_result["response"]["signature"])
            jsonUtil.writeJson("data", "userHandle", auth_result["response"]["userHandle"])
            jsonUtil.writeJson("data", "id", auth_result["id"])
        driver.quit()
        time.sleep(1)

    def repeat_webauthn_registration_and_Authentication(self, n, logger, name, displayName):
        # Webauthn 등록
        reg_result, driver = WRA.webAuthn_registration(self, name, displayName)

        if "error" in reg_result:
            logger.info(f"[❌] Registration failed: {reg_result['error']}")
            driver.quit()
            return

        logger.info('[✅] Registration successful!')
        # credential_id 추출 및 저장
        credential_id_b64url = reg_result["id"]
        global credential_id_bytes
        credential_id_bytes = WRA.b64url_decode(self, credential_id_b64url)

        # 결과 저장
        with open('./testData/data.json', 'r') as file:
            data = json.load(file)
        data['clientDataJson'] = reg_result["response"]["clientDataJSON"]
        clientDataJson = reg_result["response"]["clientDataJSON"]
        data['attestationObject'] = reg_result["response"]["attestationObject"].rstrip("=")
        attestationObject = reg_result["response"]["attestationObject"].rstrip("=")
        data['credentialId'] = credential_id_b64url
        with open('./testData/data.json', 'w') as file:
            json.dump(data, file, indent=4)

        # 데이터 준비
        transactionId = jsonUtil.readJson('data', 'transactionId')
        bUrl = readConfig.getValue('basic Info', 'bUrl')
        userId = jsonUtil.readJson('data', 'userId')
        token = jsonUtil.readJson('data', 'access Token')
        client_id = readConfig.getValue('basic Info', 'client_id')

        # 등록 결과 전송
        response_code, response_text = createCredential.registration_api_response(bUrl, transactionId, clientDataJson,
                                                                                  attestationObject, userId, token,
                                                                                  client_id)
        response_json = json.loads(response_text)
        if response_code == 200:
            logger.info('[✅] 등록 결과 전송 성공')
            jsonUtil.writeJson("data", "credentialId", response_json["data"]["authenticator"]["credentialId"])
        # 인증 반복
        for i in range(1, n+2):
            # 인증 옵션 요청
            response_code, response_text = useCredential.authentication_api(bUrl, userId, token, client_id)

            if i == n+1:
                if response_code != 200:
                    assert True
                    logger.info("🟢🟢🟢 TEST PASS")
                    break
                else:
                    logger.info(f"[❌] TEST FAIL")
                    assert False

            response_json = json.loads(response_text)
            auth_transactionId = response_json["data"]["transactionId"]
            options_str = response_json["data"]["options"]
            logger.info(f'[✅] {i}회 인증 옵션 요청 통과')
            time.sleep(1)
            # transaction ID와 options를 data.json 파일에 저장
            jsonUtil.writeJson('data', "auth_transactionId", auth_transactionId)
            jsonUtil.writeJson('data', "assertionOptions", options_str)

            # Webauthn 인증
            auth_result = WRA.webauthn_authentication(self, driver)

            if "error" in auth_result:
                logger.info(f"[❌] Authentication failed: {auth_result['error']}")
            else:
                logger.info(f'[✅] {i}회 Authentication successful!')
                authenticatorData = auth_result["response"]["authenticatorData"]
                clientDataJson_auth = auth_result["response"]["clientDataJSON"]
                signature = auth_result["response"]["signature"]
                userHandle = auth_result["response"]["userHandle"]
                credentialId = auth_result["id"]
            # 인증 결과 전송
            response_code, response_text = useCredential.authentication_api_response(bUrl, auth_transactionId, authenticatorData,
                                                                                     clientDataJson_auth, signature,
                                                                                     userHandle, credentialId, token, client_id)
            if response_code == 200:
                logger.info(f'###########################################################[✅]  {i}회 인증 결과 전송 통과 ')

            time.sleep(1)
        driver.quit()



    def b64url_decode(self, data):
        rem = len(data) % 4
        if rem > 0:
            data += '=' * (4 - rem)
        return base64.urlsafe_b64decode(data.encode('utf-8'))

    def webAuthn_registration(self, name, displayName):
        # WebDriver 및 Virtual Authenticator 설정
        chrome_options = Options()
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--remote-allow-origins=*")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 900)

        # WebAuthn 기능 활성화
        driver.execute_cdp_cmd("WebAuthn.enable", {})

        # 가상 인증기 생성
        driver.execute_cdp_cmd("WebAuthn.addVirtualAuthenticator", {
            "options": {
                "protocol": "ctap2",
                "transport": "internal",
                "hasResidentKey": True,
                "hasUserVerification": True,
                "isUserVerified": True
            }
        })

        # WebAuthn 등록 자동화 함수
        # 사이트 접속
        url = readConfig.getValue("basic Info", "client_url")
        driver.get(url)
        ################################################# WebAuthn 등록 옵션 구성
        # options 처리
        options = jsonUtil.readJson("data", "options")
        options_json = json.loads(options)
        userId = WRA.b64url_decode(self, options_json["user"]["id"])
        jsonUtil.writeJson('data', "userId", options_json["user"]["id"])
        challenge = WRA.b64url_decode(self, options_json["challenge"])
        #####################################################################

        # 브라우저에서 실행할 JS 코드 생성
        script = f"""
            const bufferToBase64url = (buffer) => {{
                const binary = String.fromCharCode(...new Uint8Array(buffer));
                const base64 = btoa(binary);
                return base64.replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
            }};
            const options = {{
                publicKey: {{
                    rp: {{
                        name: "SKT QA 006 - RP1",
                        id: "{readConfig.getValue("basic Info", "client_id")}"
                    }},
                    user: {{
                        id: new Uint8Array({list(userId)}),
                        name: "{name}",
                        displayName: "{displayName}"
                    }},
                    challenge: new Uint8Array({list(challenge)}),
                    pubKeyCredParams: [
                        {{ type: "public-key", alg: -7 }},
                        {{ type: "public-key", alg: -257 }}
                    ],
                    timeout: 60000,
                    excludeCredentials: [],
                    authenticatorSelection: {{
                        authenticatorAttachment: "platform",
                        residentKey: "required",
                        userVerification: "required"
                    }},
                    attestation: "none",
                    extensions: {{
                        credProps: true
                    }}
                }}
            }};

            return navigator.credentials.create(options).then((cred) => {{
                return {{
                    id: cred.id,
                    rawId: btoa(String.fromCharCode(...new Uint8Array(cred.rawId))),
                    type: cred.type,
                    response: {{
                        clientDataJSON: bufferToBase64url(cred.response.clientDataJSON),
                        attestationObject: bufferToBase64url(cred.response.attestationObject)
                    }}
                }};
            }});
            """

        # JS 실행 결과 받기
        result = driver.execute_async_script(f"""
                const callback = arguments[0];
                (async () => {{
                    const result = await (async () => {{
                        {script}
                    }})();
                    callback(result);
                }})();
            """)
        return result, driver

    def webauthn_authentication(self, driver):

        # === 인증 준비 ===
        assertionOptions = jsonUtil.readJson("data", "assertionOptions")
        assertion_json = json.loads(assertionOptions)
        challenge_auth = WRA.b64url_decode(self, assertion_json["challenge"])

        # === 인증 수행 ===
        auth_script = f"""
                       const bufferToBase64url = (buffer) => {{
                           const binary = String.fromCharCode(...new Uint8Array(buffer));
                           const base64 = btoa(binary);
                           return base64.replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
                       }};

                       const options = {{
                           publicKey: {{
                               challenge: new Uint8Array({list(challenge_auth)}),
                               timeout: 60000,
                               rpId: "{readConfig.getValue("basic Info", "client_id")}",
                               allowCredentials: [{{
                                   type: "public-key",
                                   id: new Uint8Array({list(credential_id_bytes)})
                               }}],
                               userVerification: "required"
                           }}
                       }};

                       return navigator.credentials.get(options).then((assertion) => {{
                           return {{
                               id: assertion.id,
                               rawId: btoa(String.fromCharCode(...new Uint8Array(assertion.rawId))),
                               type: assertion.type,
                               response: {{
                                   clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
                                   authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
                                   signature: bufferToBase64url(assertion.response.signature),
                                   userHandle: assertion.response.userHandle 
                                       ? bufferToBase64url(assertion.response.userHandle) : null
                               }}
                           }};
                       }});
                   """

        auth_result = driver.execute_async_script(f"""
                       const callback = arguments[0];
                       (async () => {{
                           const result = await (async () => {{ {auth_script} }})();
                           callback(result);
                       }})();
                   """)
        return auth_result
