# project
# 🔐 USB Physical Security System [Matrix Theme]

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white">
  <img src="https://img.shields.io/badge/Security-OTP_Token-red?style=for-the-badge">
</div>

<br>

## 📌 Project Overview
> **"인가된 하드웨어와 일회용 암호(OTP)의 결합, 완벽한 물리 보안 시스템"**

본 프로젝트는 **특정 USB 장치의 볼륨 시리얼 번호(Volume Serial Number)**와 **매번 갱신되는 일회용 암호 토큰(OTP Token)**을 결합하여 PC의 잠금을 물리적으로 제어하는 파이썬 기반 보안 시스템입니다.

단순한 비밀번호 잠금이나 고정된 키 파일을 검증하는 방식을 넘어, **프로그램 실행 시마다 새로운 난수 키를 발급하고 종료 시 회수하는 동적 보안 아키텍처**를 적용했습니다.

<br>

## 📸 Preview
| **🔒 잠금 화면 (Matrix Rain)** | **⛔ 접근 거부 (Access Denied)** |
|:---:|:---:|
| <img src="./assets/matrix_preview.gif" width="400" alt="Matrix Rain Effect"> | <img src="./assets/access_denied.png" width="400" alt="Access Denied Screen"> |

*(여기에 실행 화면 캡처나 GIF를 추가하세요)*

<br>

## ✨ Key Features

* **🛡️ 2-Factor 물리적 인증 (하드웨어 + 토큰)**
  * **1차 검증:** USB 드라이브의 고유 시리얼 번호(Volume Serial) 확인
  * **2차 검증:** 발급기(`setting.py`)가 생성한 일회용 토큰과 USB 내부의 `.key` 파일 데이터 교차 검증
  * 복제된 USB나 과거의 키 파일로는 절대 시스템에 접근할 수 없습니다.

* **🚫 강력한 시스템 제어 및 무력화 방지**
  * `Full Screen` & `Topmost` 속성으로 작업 관리자 외 접근 차단
  * 백그라운드 스레드를 통한 1초 단위 실시간 하드웨어 연결 상태 감시

* **🔑 동적 키 회수 및 관리자 백도어**
  * 우측 하단 미니 위젯을 통한 안전한 '관리자 종료' 지원
  * 시스템 종료 시 USB에 발급되었던 키 파일을 자동으로 **회수(삭제)**하여 탈취 위험 원천 차단
  * 개발자 전용 히든 단축키(`Ctrl+Shift+Q`) 비상 탈출 기능 내장

<br>

## ⚙️ System Architecture (Workflow)

1. **키 발급 (`setting.py`)**: 등록된 USB 삽입 확인 ➔ 32바이트 난수 토큰 생성 ➔ USB에 `unlock.key` 지급 및 로컬에 `local_token.dat` 저장 ➔ 메인 프로그램 자동 실행
2. **잠금 및 감시 (`computer_unlock.py`)**: 로컬 토큰 로드 ➔ 실시간 USB 감시 ➔ 시리얼 및 토큰 일치 시 잠금 해제, 불일치 시 즉각 잠금
3. **키 회수 (안전 종료)**: 관리자 비밀번호 입력 ➔ 검증 완료 시 USB 내부의 `.key` 파일 즉각 삭제 ➔ 시스템 종료

<br>

## 🚀 Getting Started

### 1. Requirements
* Windows OS
* Python 3.11.x (권장)
* 필요한 라이브러리 설치:
```bash
pip install wmi pywin32
