import json, base64, requests, os
from util import jsonUtil
from util.readProperties import readConfig

class publickeyCredential:
    apiServerUrl = readConfig.getValue("basic Info", "apiServerUrl")

    # COSE 알고리즘 매핑 (Registration에서만 사용)
    COSE_ALG_MAP = {
        -7: "ES256",
        -35: "ES384",
        -36: "ES512",
        -37: "PS256",
        -38: "PS384",
        -39: "PS512",
        -257: "RS256",
        -258: "RS384",
        -259: "RS512",
        -65535: "RS1",  # RSNULL → RS1 으로 변경
        -8: "EdDSA"
    }

    @staticmethod
    def credentialCreate(options):

        options = json.loads(options)
        transformed = publickeyCredential.transform_options(options)
        print("transformed options : ", transformed)
        # JAR API SERVER로 호출
        url = f"{publickeyCredential.apiServerUrl}/api/register"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=options, headers=headers)
        # 결과 출력
        print("\n [✅ Register] status_code : ", response.status_code)
        response_json = response.json()
        print("response:", json.dumps(response_json, indent=2, ensure_ascii=False))
        return response_json

    @staticmethod
    def credentialGet(assertionOptions):
        # ## 데이터 가져오는 부분 (향후 입력 변수 처리)
        # filePath = f'../testData/data.json'
        # with open(os.path.abspath(filePath), 'r') as file:
        #     json_data = json.load(file)
        #     assertionOptions = json_data["assertionOptions"]

        opts = json.loads(assertionOptions) if isinstance(assertionOptions, str) else assertionOptions

        # allowCredentials 타입 변환 (hyphen → underscore, then upper)
        for cred in opts.get("allowCredentials", []):
            type_str = cred.get("type", "")
            cred["type"] = type_str.replace('-', '_').upper()

            # 3. userVerification, timeout, extensions 키 변환
        if "userVerification" in opts:
            opts["userVerification"] = opts["userVerification"].upper()

        if "extensions" in opts:
            ext = opts["extensions"]
            if "credProps" in ext:
                ext["CRED_PROPS"] = ext.pop("credProps")

        # API 호출
        url = f"{publickeyCredential.apiServerUrl}/api/authenticate"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=opts, headers=headers)

        print("[✅ Authentication] status_code:", response.status_code)
        print("response:", json.dumps(response.text, indent=2))
        return response.json()

    @staticmethod
    def transform_options(opts):
        # 타입 변환
        for cred in opts["pubKeyCredParams"]:
            cred["type"] = "PUBLIC_KEY"
            cred["alg"] = publickeyCredential.COSE_ALG_MAP.get(cred["alg"], cred["alg"])
        for desc in opts["excludeCredentials"]:
            desc["type"] = "PUBLIC_KEY"
        # authenticatorSelection 대문자 변환
        sel = opts["authenticatorSelection"]
        sel["authenticatorAttachment"] = sel["authenticatorAttachment"].upper()
        sel["residentKey"] = sel["residentKey"].upper()
        sel["userVerification"] = sel["userVerification"].upper()
        # attestation
        opts["attestation"] = opts["attestation"].upper()
        # extensions 키 변환
        ext = opts.get("extensions", {})
        if "credProps" in opts.get("extensions", {}):
            opts["extensions"]["CRED_PROPS"] = opts["extensions"].pop("credProps")
        return opts


# options = {"rp": {"name": "localhost", "id": "localhost"}, "user": {"id": "J2NlbnRlcmhvJzonY2VudGVyaG9AbmF2ZXIuY29tJw", "name": "centerho@naver.com", "displayName": "centerho"},"challenge": "ERU36j60whnX5Ggo9Fx-yoFe6hP1I6xeKJzooNxVoJU", "pubKeyCredParams": [{"type": "PUBLIC_KEY", "alg": "ES256"}, {"type": "PUBLIC_KEY", "alg": "ES384"}, {"type": "PUBLIC_KEY", "alg": "ES512"}, {"type": "PUBLIC_KEY", "alg": "PS256"}, {"type": "PUBLIC_KEY", "alg": "PS384"}, {"type": "PUBLIC_KEY", "alg": "PS512"}, {"type": "PUBLIC_KEY", "alg": "RS256"}, {"type": "PUBLIC_KEY", "alg": "RS384"}, {"type": "PUBLIC_KEY", "alg": "RS512"}, {"type": "PUBLIC_KEY", "alg": "RS1"}, {"type": "PUBLIC_KEY", "alg": "EdDSA"}], "timeout": 200000, "excludeCredentials": [], "authenticatorSelection": {"authenticatorAttachment": "PLATFORM", "residentKey": "REQUIRED", "userVerification": "REQUIRED"}, "attestation": "NONE", "extensions": {"CRED_PROPS": True}}
# pk = publickeyCredential()
# pk.credentialCreate(options)