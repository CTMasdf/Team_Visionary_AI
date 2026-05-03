✨ Visionary AI
AI-based Assistive System for the Visually Impaired
Visionary AI는 시각장애인의 독서와 주변 환경 인식을 지원하기 위한 AI 기반 음성 안내 보조 시스템입니다.
Raspberry Pi, Camera Module, OCR, Gemini API, STT/TTS를 활용하여 책 읽기, 책 요약, 주변 상황 인식, 질문 응답 기능을 제공합니다.

📌 Project Overview
본 프로젝트는 카메라 기반 이미지 인식, OCR, 생성형 AI, 음성 입출력 기술을 활용하여 시각장애인이 책의 내용을 듣거나 주변 환경 정보를 음성으로 안내받을 수 있도록 지원하는 것을 목표로 합니다.
사용자는 로터리 엔코더와 버튼을 통해 원하는 기능 모드를 선택할 수 있으며, 시스템은 카메라와 마이크로 입력된 정보를 분석한 뒤 TTS 음성 안내로 결과를 제공합니다.

🎯 Development Purpose
시각장애인은 독서 활동이나 일상생활에서 주변 사물과 환경 정보를 직접 확인하기 어렵습니다. 기존 보조 기술은 특정 디지털 환경이나 제한된 콘텐츠에 의존하는 경우가 많아, 실제 생활 속 다양한 상황을 지원하는 데 한계가 있습니다.
Visionary AI는 이러한 문제를 해결하기 위해 책 읽기, 책 요약, 주변 상황 인식, 질문 응답 기능을 하나의 임베디드 보조 시스템으로 구현하고자 했습니다.

🧩 Main Features
OCR-based Book Reading
카메라로 촬영한 책 또는 문서의 텍스트를 인식하고 음성으로 출력합니다.
AI Book Summary
인식된 문서 내용을 생성형 AI를 활용하여 핵심 내용 중심으로 요약합니다.
Surrounding Environment Recognition
카메라로 촬영한 주변 환경을 분석하고 사물, 사람, 공간 정보를 음성으로 안내합니다.
Question Answering Mode
사용자의 음성 질문을 인식하고 AI 응답을 생성하여 음성으로 제공합니다.
Voice Guidance System
STT/TTS 기반 음성 입출력을 통해 시각장애인이 화면 없이도 기능을 사용할 수 있도록 지원합니다.
Accessible User Interface
로터리 엔코더, 푸시 버튼, 점자 버튼을 활용하여 직관적인 조작이 가능하도록 설계했습니다.

🎬 Demo Videos
EYECHO prototype was tested with four operating modes: Question Mode, Environment Recognition Mode, Book Summary Mode, and Book Reading Mode.
Each mode is selected using a rotary encoder, and the result is delivered through TTS-based voice guidance.
Mode	Verified Operation	Demo
Question Mode	음성 질문 입력 후 AI 응답 생성 및 TTS 출력	YouTube
Environment Recognition Mode	카메라 입력 기반 주변 상황 인식 및 음성 안내	YouTube
Book Summary Mode	책 이미지 촬영 후 AI 기반 핵심 내용 요약 및 음성 출력	YouTube
Book Reading Mode	책 페이지 이미지 인식 후 텍스트 음성 출력	YouTube

🛠 Tech Stack
Software
Python
Raspberry Pi OS
Google Gemini API
Tesseract OCR
STT / TTS
GPIO Control
Hardware
Raspberry Pi 4
Camera Module
Rotary Encoder
Push Button
Microphone
Speaker
3D Printed Case
Interface / Communication
GPIO
Wi-Fi
Voice I/O
Camera Input

🏗 System Architecture
User Input
Voice Input
Button Input
Encoder Input
Input Devices
Camera Module
Microphone
Rotary Encoder
Push Button
Raspberry Pi Processing
Mode Selection Logic
OCR Processing
Gemini API Request
STT Processing
TTS Output
Output
Voice Guidance through Speaker

🔄 Operation Flow
사용자가 로터리 엔코더로 기능 모드를 선택합니다.
버튼 입력을 통해 선택한 모드를 실행합니다.
카메라 또는 마이크를 통해 입력 데이터를 수집합니다.
OCR 또는 Gemini API를 활용하여 정보를 분석합니다.
분석 결과를 TTS로 변환합니다.
스피커를 통해 사용자에게 음성 안내를 제공합니다.

👥 Team
Role	Responsibility
Team Leader	전체 프로젝트 기획 및 시스템 구조 설계
Hardware Integration	Raspberry Pi 기반 기능 통합 및 장치 연동
AI / Software	OCR, Gemini API, STT/TTS 기능 구현
Product Design	3D 모델링 및 외관 케이스 제작
System Test	카메라 모듈 연동 및 전체 시스템 테스트

🙋‍♂️ My Role
팀장 | 5인 프로젝트
전체 프로젝트 기획 및 시스템 구조 설계
Raspberry Pi 기반 기능 통합 및 동작 검증
Camera Module 연동 및 영상 입력 테스트
3D 모델링 기반 외관 케이스 설계 및 제작
하드웨어 조립 및 전체 시스템 통합 테스트

📷 Prototype
완성품 사진, 개발 과정 사진, 시스템 구성도 이미지를 추가할 예정입니다.
Recommended image files
images/prototype_front.jpg
images/prototype_inside.jpg
images/system_architecture.png
images/test_scene.jpg

📁 Project Structure
Recommended repository structure
README.md
src/main.py
src/camera.py
src/ocr.py
src/gemini_api.py
src/stt.py
src/tts.py
src/gpio_control.py
hardware/circuit_diagram.png
hardware/case_model.stl
images/prototype.jpg
docs/project_report.pdf

✅ Expected Effects
시각장애인의 독서 접근성 향상
주변 환경 정보 인식을 통한 일상생활 편의성 개선
음성 기반 인터페이스를 통한 직관적인 사용성 제공
저비용 임베디드 플랫폼을 활용한 보조기기 구현 가능성 확인
AI Vision, OCR, STT/TTS, 임베디드 시스템 통합 경험 확보

📌 Project Period
2025.09 ~ 2025.12

📎 Links
Demo Playlist: EYECHO Demo Videos
Question Mode: YouTube
Environment Recognition Mode: YouTube
Book Summary Mode: YouTube
Book Reading Mode: YouTube

📝 License
This project is developed for educational and capstone design purposes.
