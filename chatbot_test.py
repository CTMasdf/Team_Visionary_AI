# ------------------- 필요한 라이브러리 -------------------
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------- 환경 변수 & Gemini API -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ------------------- 대화 기록 관리 -------------------
HISTORY_FILE = "conversation_history.json"

def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_conversation_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

conversation_history = load_conversation_history()

def build_prompt():
    prompt = ""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Gemini"
        text = msg.get("text")
        if text:
            prompt += f"{role}: {text}\n"
    return prompt

# ------------------- Gemini API 응답 -------------------
def generate_response(user_input):
    conversation_history.append({"role": "user", "text": user_input})
    prompt = build_prompt()
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"Gemini 오류: {e}"
    conversation_history.append({"role": "model", "text": answer})
    save_conversation_history(conversation_history)
    return answer

# ------------------- 키보드 입력 기반 챗봇 -------------------
def chat_bot():
    print("💡 Gemini 챗봇 시작 (종료하려면 'exit' 입력)")
    while True:
        user_input = input(" You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "종료"]:
            print("대화를 종료합니다.")
            break

        answer = generate_response(user_input)
        print(" Gemini:", answer)

# ------------------- 실행 -------------------
if __name__ == "__main__":
    chat_bot()
