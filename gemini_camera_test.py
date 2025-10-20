import os
import subprocess
import time
import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold # 안전 설정을 위해 추가

# ------------------- 환경 변수 & Gemini API -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ------------------- 경로 설정 -------------------
IMAGE_PATH = "/home/pi/chatbot_project/capture.png" # PNG로 변경
HISTORY_FILE = "conversation_history.json"


# ------------------- 대화 기록 관리 -------------------
def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_conversation_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)

conversation_history = load_conversation_history()

# ------------------- 텍스트 입력 (STT 대체) -------------------
def get_user_input(prompt=""):
    """사용자로부터 키보드 입력을 받습니다."""
    if prompt:
        print(prompt, end="")
    try:
        text = input()
        print("력된 텍스트:", text)
        return text
    except EOFError:
        return ""
    except KeyboardInterrupt:
        return ""

# ------------------- 텍스트 출력 (TTS 대체) -------------------
def print_text_response(text):
    """Gemini의 응답을 콘솔에 출력합니다."""
    print("Gemini:", text)
    # tts를 위한 코드 제거: os.system("mpg321 -q response.mp3")

# ------------------- Gemini API -------------------
def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        # 텍스트 응답의 안전성 필터링은 일반 대화에서도 발생할 수 있으므로 확인
        if response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason.name
            print(f"❌ Gemini Safety Block Reason (Text): {reason}")
            return f"죄송해요. 대화 내용이 안전 정책({reason})에 위배되어 답변할 수 없어요."
        return response.text
    except Exception as e:
        return f"Gemini 오류: {e}"

def build_prompt():
    prompt = ""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Chatbot"
        
        # parts가 문자열 또는 리스트일 수 있으므로 처리
        text_content = msg.get('parts')
        if isinstance(text_content, list):
            # 리스트에 여러 요소가 있을 수 있으나, 여기서는 텍스트만 처리한다고 가정
            text_content = " ".join([part for part in text_content if isinstance(part, str)])
        elif not isinstance(text_content, str):
            text_content = "" # 문자열이 아니면 빈 문자열로 처리

        prompt += f"{role}: {text_content}\n"
    return prompt

# ------------------- 사진 촬영 -------------------
def take_picture():
    # Raspberry Pi 환경에서 rpicam-still 명령어가 실행되어야 합니다.
    # PNG 형식으로 저장하도록 -e png 옵션 추가
    subprocess.run(["rpicam-still", "-e", "png", "-o", IMAGE_PATH])
    print("사진 촬영 완료:", IMAGE_PATH)

#------------------- 사진 촬영 및 Gemini 질의 -------------------
def ask_gemini_about_image():
    if not os.path.exists(IMAGE_PATH):
        return "사진이 존재하지 않습니다."
    
    with open(IMAGE_PATH, "rb") as f:
        image_data = f.read()
        
    try:
        # 안전 설정을 추가 (모든 카테고리에 대해 BLOCK_NONE 시도)
        # PROHIBITED_CONTENT는 이 설정으로 해제되지 않을 수 있음을 유의
        safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }

        # 텍스트와 이미지 데이터를 함께 전달
        response = model.generate_content(
            ["방금 찍은 사진에 대해  2줄 이내로 설명해줘. 이 사진은 일반적인 사물 사진이며, 어떤 유해한 내용도 포함하고 있지 않습니다.", 
             {"mime_type": "image/png", "data": image_data}], # MIME 타입을 image/png로 변경
            safety_settings=safety_settings # 안전 설정 추가
        )
    except Exception as e:
        # API 연결 또는 기타 일반 오류 처리
        return f"Gemini API 호출 중 오류 발생: {e}"

    # 응답 안전성 필터 확인
    if response.prompt_feedback.block_reason:
        reason = response.prompt_feedback.block_reason.name
        print(f"Gemini Safety Block Reason: {reason}")
        return f"죄송해요. 사진의 내용이 안전 정책({reason})에 위배되어 답변할 수 없어요."
    
    if not response.candidates:
        # 다른 이유로 후보가 반환되지 않은 경우 처리
        return "죄송해요. Gemini가 이 사진에 대한 적절한 답변을 생성하지 못했어요."

    # 응답 텍스트 반환
    return response.text

## ------------------- 명령어 처리 -------------------
def handle_command(user_text):
    if "사진" in user_text and ("찍" in user_text or "촬영" in user_text):
        # 1. 사진 촬영
        take_picture()
        # 2. Gemini에게 사진 설명 요청 및 답변 받기
        answer = ask_gemini_about_image()
        # 사진 관련 응답은 대화의 흐름(conversation_history)에 저장하지 않음.
    else:
        # 일반 대화: 대화 기록에 추가
        conversation_history.append({"role": "user", "parts": user_text})
        prompt = build_prompt()
        answer = generate_response(prompt)
        conversation_history.append({"role": "model", "parts": answer})
        save_conversation_history()

    # TTS 대신 텍스트로 출력
    print_text_response(answer)

# ------------------- 챗봇 메인 루프 (키보드 입력) -------------------
def chat_bot():
    print("--------------------------------------------------")
    print("아이봇 텍스트 챗봇 시작. 질문을 입력해주세요.")
    print("    ('사진 찍어줘' 또는 '종료'를 입력하여 기능을 사용하세요)")
    print("--------------------------------------------------")
    
    while True:
        question = get_user_input("사용자 입력: ")
        
        if not question:
            continue

        if "종료" in question or "그만" in question or "exit" in question.lower():
            print_text_response("대화를 종료합니다. 안녕히 계세요!")
            break

        handle_command(question)

# ------------------- 실행 -------------------
if __name__ == "__main__":
    chat_bot()
