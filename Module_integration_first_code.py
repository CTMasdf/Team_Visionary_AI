#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------
# 📌 라즈베리파이 AI 비서 프로젝트
# - 엔코더로 모드 변경 (책 읽기 / 요약 / 환경 인식 / 질문)
# - 버튼으로 음성 재생 / 배속 조절
# - 카메라 캡처 후 Gemini 분석, TTS 출력
# - 질문 모드에서는 음성 녹음 → Gemini 답변
# ------------------------------

import os, time, threading, tempfile, json, re
import RPi.GPIO as GPIO
from gtts import gTTS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import speech_recognition as sr
import pygame
from pydub import AudioSegment

# ====== GPIO 핀 설정 ======
CLK_PIN = 17        # 엔코더 CLK
DT_PIN = 18         # 엔코더 DT
SW_PIN = 27         # 엔코더 버튼(사진 찍기 / 질문 종료)
BTN_PLAYSTOP = 22   # 재생/일시정지 버튼
BTN_SPEED = 23      # 배속 변경 버튼

IMAGE_PATH = "/home/pi/chatbot_project/capture.png"
HISTORY_FILE = "/home/pi/chatbot_project/conversation_history.json"

TTS_LANG = "ko"     # TTS 언어 한국어

# ✅ Gemini API 환경 변수 로드
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Gemini 모델 선택 + 안전 설정 해제
GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

# ===== 상태 변수 =====
encoder_counter = 0             # 엔코더 카운트로 모드 결정 (0~39)
current_mode = "book_read"      # 기본 모드: 책 읽기
conversation_history = []       # 이전 대화 기록 저장
question_buffer = ""            # 질문 음성 누적 텍스트

# TTS 배속 단계
voice_speed = 1.0
speed_steps = [1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 0.5]

# 오디오 상태
play_lock = threading.Lock()
last_tts_text = ""
pygame.mixer.init()
current_sound = None
paused = False

# ===== 화면 출력 (버퍼 딜레이 방지) =====
def safe_print(*args, **kwargs):
    print(*args, **kwargs, flush=True)

# ===== 대화 히스토리 불러오기 =====
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

# ===== 대화 히스토리 저장 =====
def save_history(hist):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False, indent=2)
    except:
        pass

conversation_history = load_history()

# ===== 카메라 촬영 =====
def take_picture():
    safe_print("📸 사진 촬영 시도")
    try:
        import subprocess
        subprocess.run(["rpicam-still","-e","png","-o",IMAGE_PATH], check=True, timeout=10)
        safe_print("✅ 사진 저장 완료")
        with open(IMAGE_PATH,"rb") as f: return f.read()
    except Exception as e:
        safe_print("⚠️ 촬영 실패:", e)
        return None

# ===== Gemini 호출 =====
def query_gemini(prompt, img_bytes=None):
    inputs = [prompt]
    if img_bytes:  # 이미지가 있으면 포함
        inputs.append({"mime_type":"image/png","data":img_bytes})

    try:
        resp = GEMINI_MODEL.generate_content(inputs, safety_settings=SAFETY_SETTINGS)
        if getattr(resp, "candidates", None):
            return resp.text
    except Exception as e:
        return f"Gemini 오류: {e}"

# ===== TTS 텍스트 정리 =====
def clean_text_for_tts(text):
    return re.sub(r"[\*\~\-\#]", "", text).strip() if text else ""

# ===== 오디오 정지 =====
def stop_audio():
    global paused, current_sound
    with play_lock:
        if current_sound:
            current_sound.stop()
        paused = False

# ===== TTS 파일 생성 =====
def _generate_tts_file(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            path = f.name
        gTTS(text=text, lang=TTS_LANG).save(path)
        return path
    except:
        return None

# ===== TTS + 배속 + 재생 (세그폴트 방지 방식) =====
def tts_and_play(text, speed=1.0):
    global last_tts_text, current_sound, paused
    last_tts_text = text or ""
    stop_audio()
    mp3_path = _generate_tts_file(text)
    if not mp3_path: return

    try:
        sound = AudioSegment.from_file(mp3_path)  # mp3 불러오기
        new_rate = int(sound.frame_rate * speed) # 배속 적용
        sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_rate})
        sound = sound.set_frame_rate(44100)

        speed_path = mp3_path.replace(".mp3", "_speed.mp3")
        sound.export(speed_path, format="mp3")   # 임시 파일 저장

        current_sound = pygame.mixer.Sound(speed_path) # pygame으로 재생
        current_sound.play()
        paused = False

        while pygame.mixer.get_busy(): time.sleep(0.1)
        current_sound = None
        os.remove(mp3_path); os.remove(speed_path)
    except Exception as e:
        safe_print("🔊 재생 오류:", e)

# ===== 재생 / 일시정지 =====
def toggle_play_pause():
    global paused
    if current_sound:
        if paused:
            current_sound.play()
            paused = False
        else:
            pygame.mixer.pause()
            paused = True
    elif last_tts_text:
        tts_and_play(last_tts_text, speed=voice_speed)

# ===== 배속 변경 =====
def change_speed():
    global voice_speed
    idx = speed_steps.index(voice_speed) if voice_speed in speed_steps else 0
    voice_speed = speed_steps[(idx + 1) % len(speed_steps)]
    tts_and_play(f"{voice_speed}배속입니다.")
    safe_print(f"🎵 배속 → {voice_speed}")

# ===== 이미지 기반 응답 모드 처리 =====
def handle_capture():
    img = take_picture()
    if not img:
        tts_and_play("사진을 찍지 못했습니다.")
        return
    
    # 모드별 Gemini 프롬프트
    if current_mode == "book_read":
        prompt = "이 사진은 책 페이지입니다. 가능한 한 정확하게 읽어줘."
    elif current_mode == "book_summary":
        prompt = "이 책 내용을 핵심만 요약해줘."
    elif current_mode == "question_mode":
        prompt = question_buffer
    else:
        prompt = "주변 환경을 간단히 설명해줘."

    resp = query_gemini(prompt, img if current_mode!="question_mode" else None)
    conversation_history.append({"role":"user","parts":prompt})
    conversation_history.append({"role":"model","parts":resp})
    save_history(conversation_history)
    tts_and_play(clean_text_for_tts(resp), speed=voice_speed)

# ===== 질문 음성 녹음 =====
def record_question():
    global question_buffer
    r = sr.Recognizer()
    question_buffer = ""
    safe_print("🎤 음성 질문 시작 (버튼 누르고 있는 동안)")

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while GPIO.input(SW_PIN)==0:
            try:
                audio = r.listen(source, phrase_time_limit=3)
                text = r.recognize_google(audio, language="ko-KR")
                question_buffer += " " + text
                safe_print("녹음:", text)
            except: pass

    question_buffer = question_buffer.strip()
    return question_buffer

# ===== 엔코더 모드 변경 =====
def encoder_polling_worker():
    global encoder_counter, current_mode
    last_clk = GPIO.input(CLK_PIN)
    last_dt = GPIO.input(DT_PIN)

    while True:
        clk = GPIO.input(CLK_PIN)
        dt = GPIO.input(DT_PIN)
        if clk != last_clk: # 엔코더 회전 감지
            encoder_counter += 1 if dt != clk else -1
            encoder_counter %= 40  # 0~39 순환

            # 카운터 영역별 모드 설정
            if encoder_counter < 10: new_mode = "book_read"
            elif encoder_counter < 20: new_mode = "book_summary"
            elif encoder_counter < 30: new_mode = "env"
            else: new_mode = "question_mode"

            if new_mode != current_mode:
                current_mode = new_mode
                safe_print(f"🔀 모드 변경 → {current_mode}")
                mode_text = {
                    "book_read":"책 읽기 모드입니다.",
                    "book_summary":"책 요약 모드입니다.",
                    "env":"주변 상황 인식 모드입니다.",
                    "question_mode":"질문 모드입니다."
                }
                tts_and_play(mode_text[current_mode])

        last_clk = clk
        time.sleep(0.01)

# ===== 엔코더 버튼 동작 =====
def sw_polling_worker():
    global question_buffer
    last_state = GPIO.input(SW_PIN)

    while True:
        state = GPIO.input(SW_PIN)

        if state==0 and last_state==1:  # 버튼 눌림
            if current_mode=="question_mode":
                record_question()
            else:
                handle_capture()

        elif state==1 and last_state==0:  # 버튼 뗌 → 질문 전송
            if current_mode=="question_mode" and question_buffer:
                img = take_picture() if "사진" in question_buffer else None
                resp = query_gemini(question_buffer, img)
                conversation_history.append({"role":"user","parts":question_buffer})
                conversation_history.append({"role":"model","parts":resp})
                save_history(conversation_history)
                tts_and_play(clean_text_for_tts(resp), speed=voice_speed)
                question_buffer = ""

        last_state = state
        time.sleep(0.05)

# ===== 재생 / 배속 버튼 =====
def button_control_worker():
    last_play = GPIO.input(BTN_PLAYSTOP)
    last_speed = GPIO.input(BTN_SPEED)

    while True:
        play = GPIO.input(BTN_PLAYSTOP)
        speed = GPIO.input(BTN_SPEED)

        if play==0 and last_play==1:
            toggle_play_pause()
            time.sleep(0.25)

        if speed==0 and last_speed==1:
            change_speed()
            time.sleep(0.25)

        last_play, last_speed = play, speed
        time.sleep(0.05)

# ===== 메인 실행 =====
def main():
    safe_print("=== Raspberry Pi Assist Bot 시작 ===")
    GPIO.setmode(GPIO.BCM)
    for p in [CLK_PIN, DT_PIN, SW_PIN, BTN_PLAYSTOP, BTN_SPEED]:
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 각각 별도 스레드로 실행
    threading.Thread(target=button_control_worker, daemon=True).start()
    threading.Thread(target=encoder_polling_worker, daemon=True).start()
    threading.Thread(target=sw_polling_worker, daemon=True).start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        safe_print("종료")
    finally:
        stop_audio()
        GPIO.cleanup()
        safe_print("GPIO 정리 완료")

if __name__ == "__main__":
    main()
