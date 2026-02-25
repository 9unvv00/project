# project
# USB Physical Security System

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white">
  <img src="https://img.shields.io/badge/Security-OTP_Token-red?style=for-the-badge">
</div>

<br>

## Project Overview
> **"인가된 하드웨어와 일회용 암호(OTP)의 결합, 완벽한 물리 보안 시스템"**

본 프로젝트는 **특정 USB 장치의 볼륨 시리얼 번호(Volume Serial Number)**와 **매번 갱신되는 일회용 암호 토큰(OTP Token)**을 결합하여 PC의 잠금을 물리적으로 제어하는 파이썬 기반 보안 시스템입니다.

단순한 비밀번호 잠금이나 고정된 키 파일을 검증하는 방식을 넘어, **프로그램 실행 시마다 새로운 난수 키를 발급하고 종료 시 회수하는 동적 보안 아키텍처**를 적용했습니다.

<br>

## Preview
| **잠금 화면 (Matrix Rain)** |
|:---:|
| <img width="1920" height="1080" alt="스크린샷 2026-02-25 211744" src="https://github.com/user-attachments/assets/c4461019-c208-4aec-ae1e-e19eb4adf6a5" /> 

<br>

## Key Features

* **2-Factor 물리적 인증 (하드웨어 + 토큰)**
  * **1차 검증:** USB 드라이브의 고유 시리얼 번호(Volume Serial) 확인
  * **2차 검증:** 발급기(`setting.py`)가 생성한 일회용 토큰과 USB 내부의 `.key` 파일 데이터 교차 검증
  * 복제된 USB나 과거의 키 파일로는 절대 시스템에 접근할 수 없습니다.

* **강력한 시스템 제어 및 무력화 방지**
  * `Full Screen` & `Topmost` 속성으로 작업 관리자 외 접근 차단
  * 백그라운드 스레드를 통한 1초 단위 실시간 하드웨어 연결 상태 감시

* **동적 키 회수 및 관리자 백도어**
  * 우측 하단 미니 위젯을 통한 안전한 '관리자 종료' 지원
  * 시스템 종료 시 USB에 발급되었던 키 파일을 자동으로 **회수(삭제)**하여 탈취 위험 원천 차단
  * 개발자 전용 히든 단축키(`Ctrl+Shift+Q`) 비상 탈출 기능 내장

<br>

## System Architecture (Workflow)

1. **키 발급 (`setting.py`)**: 등록된 USB 삽입 확인 ➔ 32바이트 난수 토큰 생성 ➔ USB에 `unlock.key` 지급 및 로컬에 `local_token.dat` 저장 ➔ 메인 프로그램 자동 실행
2. **잠금 및 감시 (`computer_unlock.py`)**: 로컬 토큰 로드 ➔ 실시간 USB 감시 ➔ 시리얼 및 토큰 일치 시 잠금 해제, 불일치 시 즉각 잠금
3. **키 회수 (안전 종료)**: 관리자 비밀번호 입력 ➔ 검증 완료 시 USB 내부의 `.key` 파일 즉각 삭제 ➔ 시스템 종료

<br>

## Getting Started

### 1. Requirements
* Windows OS
* Python 3.11.x (권장)
* 필요한 라이브러리 설치:
```bash
pip install wmi pywin32

### 2. Configuration
`setting.py` 와 `computer_unlock.py` 의 상단 설정값을 본인의 환경에 맞게 수정합니다.
```python
# [설정 영역]
TARGET_SERIAL = "2EB405A7"          # 허용할 본인의 USB 볼륨 시리얼
KEY_FILE_NAME = "unlock.key"        # 발급할 키 파일 이름
ADMIN_PASSWORD = "1234"             # 관리자 종료용 비밀번호

### 3. Build to `.exe` (Optional)
사용 편의성을 위해 PyInstaller를 사용하여 실행 파일로 변환할 수 있습니다.
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile computer_unlock.py
pyinstaller --onefile setting.py

### 4. How to Use (Run)
프로그램 실행 및 실제 사용 방법입니다.

1. **USB 연결:** 관리자로 등록된 USB(시리얼이 일치하는 USB)를 PC에 꽂습니다.
2. **키 발급:** `setting.py` (또는 변환된 `setting.exe`)를 실행합니다.
3. **자동 감시:** USB 내부에 일회용 암호 키가 발급되며, 보안 시스템(`computer_unlock.py`)이 자동으로 백그라운드에서 시작됩니다.
4. **잠금 및 해제:** 이후 USB를 PC에서 뽑으면 즉시 화면이 잠기고, 다시 꽂으면 잠금이 해제됩니다.
5. **안전 종료:** 잠금 해제 상태에서 우측 하단의 `보안 종료` 위젯을 누르고 비밀번호를 입력하면, USB 안의 키가 회수되며 프로그램이 완전히 종료됩니다.
