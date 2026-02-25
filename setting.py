import os
import wmi
import secrets
import subprocess
import sys
import json

# ===========================================
KEY_FILE_NAME = "unlock.key"        # 발급할 키 파일 이름
CONFIG_FILE = "security_config.json"# PC에 저장할 시리얼 & 토큰 정보
LOCKER_SCRIPT = "computer_unlock.exe" # 실행할 잠금 프로그램
# ==========================================

def run_setting():
    print("=" * 50)
    print("보안 시스템 설정 및 키 발급 실행 중")
    print("=" * 50)
    
    c = wmi.WMI()
    usb_disks = c.Win32_LogicalDisk(DriveType=2)
    
    if not usb_disks:
        print("연결된 USB를 찾을 수 없습니다. USB를 꽂은 후 다시 실행해주세요.")
        input("엔터 키를 누르면 종료합니다...")
        return

    # 첫 번째로 발견된 USB를 마스터 키로 지정
    target_drive = usb_disks[0].DeviceID
    target_serial = usb_disks[0].VolumeSerialNumber

    print(f"[{target_drive}] 드라이브(시리얼: {target_serial})를 보안 키로 등록합니다.")

    # 1. 고유 키 생성
    new_token = secrets.token_hex(32)

    # 2. USB에 .key 파일 지급
    usb_key_path = os.path.join(target_drive + "\\", KEY_FILE_NAME)
    try:
        with open(usb_key_path, "w", encoding="utf-8") as f:
            f.write(new_token)
        print("-> USB에 1회용 키 파일 지급 완료")
    except Exception as e:
        print(f"-> 키 파일 지급 실패: {e}")
        return

    # 3. 로컬 PC에 검증용 데이터(시리얼 + 토큰) 저장
    config_data = {
        "serial_number": target_serial,
        "token": new_token
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        print("-> 검증용 로컬 설정 데이터 생성 완료")
    except Exception as e:
        print(f"-> 로컬 데이터 저장 실패: {e}")
        return

# 4. computer_unlock.py 자동 실행
    print("\n보안 프로그램을 백그라운드에서 시작합니다...")
    try:
        # PyInstaller로 묶였을 때와 아닐 때의 경로를 모두 정확히 잡기 위한 코드
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
        locker_path = os.path.join(current_dir, LOCKER_SCRIPT)
        
        
        command = f'start "" "{locker_path}"'
        subprocess.Popen(command, shell=True, cwd=current_dir)
        
        print("시스템 보안이 활성화되었습니다. 설정 창은 3초 뒤 자동으로 닫힙니다.")
        import time
        time.sleep(3)
    except Exception as e:
        print(f"프로그램 실행 실패: {e}")
        input("엔터 키를 누르면 종료합니다...")

if __name__ == "__main__":
    run_setting()