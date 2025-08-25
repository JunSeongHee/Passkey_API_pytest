import json, os

def writeJson(fileName, key, value):
    # 1. JSON 파일 열기 (읽기)
    filePath = f'./testData/{fileName}.json'
    with open(os.path.abspath(filePath), 'r') as file:
        data = json.load(file)

    # 2. abc 키 추가 또는 수정
    data[f'{key}'] = value

    # 3. JSON 파일 다시 쓰기
    with open(f'./testData/{fileName}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def writeJsonBulk(fileName, dict_obj):
    """
    저장하고자 하는 key-value 쌍 전체 (기존 값은 overwrite)
    writeJsonBulk('options_list', body) 또는 writeJsonBulk('options_list', body['data'])
    """
    filePath = f'./testData/{fileName}.json'
    
    # 파일을 덮어쓰기
    with open(filePath, 'w', encoding='utf-8') as file:
        json.dump(dict_obj, file, indent=2, ensure_ascii=False)

def readJson(fileName, key):
    filePath = f'./testData/{fileName}.json'
    with open(os.path.abspath(filePath), 'r') as file:
        json_data = json.load(file)
        return json_data[key]
