import os
import re

def extract_logger_infos_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[❌] 파일 열기 실패: {file_path} -> {e}")
        return []

    # 패턴을 완화하여 다양한 spacing/coding 스타일 허용
    pattern = r'self\.logger\.info\(\s*[\'"]\s*(#\d{3}.*?)\s*[\'"]\s*\)'
    matches = re.findall(pattern, content)

    if matches:
        print(f"[✅] {file_path} 에서 {len(matches)}개 추출됨")
        for m in matches:
            print(f"   └▶ {m}")
    else:
        print(f"[⚠️] {file_path} 에서 패턴 미발견")

    return matches

def save_logger_infos_to_file(original_py_path, logger_infos, output_dir):
    base_name = os.path.basename(original_py_path).replace(".py", "")
    output_file = os.path.join(output_dir, f"logger_info_{base_name}.txt")

    try:
        with open(output_file, 'w', encoding='utf-8') as out:
            for line in logger_infos:
                out.write(line + '\n')
        print(f"[💾] 저장 완료: {output_file}")
    except Exception as e:
        print(f"[❌] 저장 실패: {output_file} -> {e}")

def extract_and_save_all(folder_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    found_any = False

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                print(f"[🔍] 검사 중: {full_path}")
                logger_infos = extract_logger_infos_from_file(full_path)
                if logger_infos:
                    found_any = True
                    save_logger_infos_to_file(full_path, logger_infos, output_dir)

    if not found_any:
        print("⚠️ 유효한 logger 메시지를 찾지 못했습니다. 패턴을 다시 확인해주세요.")

if __name__ == '__main__':
    input_folder = 'testCase/admin_api'  # 현재 위치 기준 상대 경로
    output_folder = 'logger_info_outputs'

    extract_and_save_all(input_folder, output_folder)
