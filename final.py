#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================
# Raspberry Pi AI 비서 프로젝트
# 엔코더: 모드 변경
# 버튼: 재생/일시정지, 배속 변경
# 카메라 촬영 → Gemini 분석 → TTS 출력
# 질문 모드: 음성 녹음 → Gemini 답변
# 전원: 슬라이드 스위치 OFF → 시스템 정상 종료
# ==============================

import os
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
os.environ["FFPROBE_BINARY"] = "/usr/bin/ffprobe"

import time, threading, tempfile, json, re
import RPi.GPIO as GPIO
from gtts import gTTS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import speech_recognition as sr

# pydub import + 경로 강제 설정
from pydub import AudioSegment
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"

import pygame

# ===== GPIO =====
CLK_PIN = 17
DT_PIN = 18
SW_PIN = 27
BTN_PLAYSTOP = 22
BTN_SPEED = 23
#POWER_PIN = 5  # 슬라이드 스위치 (선택)

IMAGE_PATH = "/home/aaaa/capture.png"
HISTORY_FILE = "/home/aaaa/conversation_history.json"
TTS_LANG = "ko"

# ===== Gemini API =====
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

# ===== 상태 =====
encoder_counter = 0
current_mode = "book_read"
conversation_history = []
question_buffer = ""
speed_steps = [1.0, 1.5, 2.0]
voice_speed = 1.0

# ===== 오디오 초기화 =====
pygame.mixer.quit()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

play_lock = threading.Lock()
current_sound = None
paused = False
last_tts_text = ""

def safe_print(*args, **kwargs):
    print(*args, **kwargs, flush=True)

# ===== 대화 히스토리 =====
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def save_history(hist):
    try:
        with open(HISTORY_FILE,"w",encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False, indent=2)
    except: pass

conversation_history = load_history()

# ===== 카메라 =====
def take_picture():
    safe_print("사진 촬영 시도")
    try:
        import subprocess
        subprocess.run(["rpicam-still","-e","png","-o",IMAGE_PATH], check=True, timeout=9)
        safe_print("사진 저장 완료")
        with open(IMAGE_PATH,"rb") as f: return f.read()
    except Exception as e:
        safe_print("촬영 실패:", e)
        return None

# ===== Gemini 관련 =====
def build_prompt(user_text, img_bytes=None):
    """설명서 기반 시스템 프롬프트와 사용자 질문/이미지를 포함"""
    
    system_instruction = (
        "당신은 라즈베리 파이 기반의 시각장애인용 AI 비서 '아이코(EYEHCO)'입니다. "
        "모든 응답은 한국어로 친절하게 작성하세요.\n"
        "사용자는 책 읽기, 책 요약, 주변 인식, 질문 모드 등을 수행하며, "
        "사용법, 모드, 버튼, 촬영, 배속 등을 묻는 질문에는 친절하게 설명합니다.\n\n"
        
        "아이코의 기능 및 사용법 요약:\n"
        "1. 모드 선택: 기기 좌측 로터리 스위치를 돌려서 선택 가능\n"
        "   - 책 읽기 모드: 책 내용을 읽음\n"
        "   - 책 요약 모드: 책 내용을 요약\n"
        "   - 주변 인식 모드: 주변 사물과 상황을 분석하여 음성 안내\n"
        "   - 질문 모드: 사용자의 질문을 음성으로 기록하고 답변 제공\n"
        "2. 사진 촬영: 로터리 스위치를 눌러 촬영 가능\n"
        "   - 질문 모드에서는 스위치를 누른 상태에서 말하면 질문이 녹음되고, "
        "   스위치를 떼면 질문이 전송되어 답변이 나옵니다.\n"
        "3. 음성 재생/정지: 기기 정면 위쪽 버튼으로 제어\n"
        "4. 음성 배속 변경: 기기 정면 아래쪽 버튼으로 조절 (느리게/보통/빠르게 순환)\n"
        "5. 질문에 답할 때는 항상 친절하고 이해하기 쉽게 설명\n"
        "6. 모든 기능은 시각장애인 사용자를 기준으로 안내\n"
    )
    
    # 사용자 질문과 결합
    inputs = [system_instruction + "\nUser: " + user_text]
    
    # 이미지가 있다면 함께 전송
    if img_bytes:
        inputs.append({"mime_type":"image/png","data":img_bytes})
    
    return inputs

# ===== Gemini API =====
def query_gemini(prompt, img_bytes=None):
    """사용자 질문과 이미지를 기반으로 Gemini 모델 응답 받기"""
    inputs = build_prompt(prompt, img_bytes)
    try:
        resp = GEMINI_MODEL.generate_content(inputs, safety_settings=SAFETY_SETTINGS)
        if getattr(resp, "candidates", None):
            safe_print("\n[챗봇 응답]\n", resp.text, "\n")
            return resp.text
    except Exception as e:
        safe_print("Gemini 오류:", e)
        return "Gemini와 연결할 수 없습니다."


# ===== TTS =====
def clean_text_for_tts(text):
    return re.sub(r"[\*\~\-\#]", "", text).strip() if text else ""

def stop_audio():
    global paused, current_sound
    with play_lock:
        if current_sound:
            current_sound.stop()
            current_sound = None
        paused = False

def _generate_tts_file(text, speed=1.0):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            path = f.name
        gTTS(text=text, lang=TTS_LANG).save(path)
        sound = AudioSegment.from_file(path)
        new_rate = int(sound.frame_rate * speed)
        sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_rate})
        sound = sound.set_frame_rate(44100)
        speed_path = path.replace(".mp3", "_speed.mp3")
        sound.export(speed_path, format="mp3")
        os.remove(path)
        return speed_path
    except Exception as e:
        safe_print("TTS 생성 오류:", e)
        return None

def tts_and_play(text, speed=None):
    global current_sound, paused, last_tts_text, voice_speed
    last_tts_text = text or ""
    if speed is None:
        speed = voice_speed
    stop_audio()
    mp3_path = _generate_tts_file(text, speed=speed)
    if not mp3_path: return

    def play_thread(path):
        global current_sound, paused
        try:
            with play_lock:
                current_sound = pygame.mixer.Sound(path)
                current_sound.play()
                paused = False
            while pygame.mixer.get_busy():
                time.sleep(0.05)
        except Exception as e:
            safe_print("재생 오류:", e)
        finally:
            current_sound = None
            if os.path.exists(path):
                os.remove(path)

    threading.Thread(target=play_thread, args=(mp3_path,), daemon=True).start()

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

def change_speed():
    global voice_speed
    idx = speed_steps.index(voice_speed) if voice_speed in speed_steps else 0
    voice_speed = speed_steps[(idx+1)%len(speed_steps)]
    tts_and_play(f"{voice_speed}배속입니다.")
    safe_print(f"배속 → {voice_speed}")

# ===== 모드 처리 =====
def handle_capture():
    img = take_picture()
    if not img:
        tts_and_play("사진을 찍지 못했습니다.")
        return

    if current_mode=="book_read":
        prompt="이 사진은 책 페이지입니다. 가능한 한 정확하게 읽어줘. (읽기만 해)"
    elif current_mode=="book_summary":
        prompt="이 책 내용을 핵심만 요약해줘."
    elif current_mode=="question_mode":
        prompt=question_buffer
    else:
        prompt="주변 환경을 간단히 설명해줘."

    if current_mode in ["book_read","book_summary","env"]:
        tts_and_play("AI 챗봇으로부터 응답받는 중입니다. 잠시만 기다려 주세요.", speed=voice_speed)

    resp = query_gemini(prompt, img if current_mode!="question_mode" else None)
    conversation_history.append({"role":"user","parts":prompt})
    conversation_history.append({"role":"model","parts":resp})
    save_history(conversation_history)
    tts_and_play(clean_text_for_tts(resp), speed=voice_speed)

# ===== 질문 음성 =====
def record_question():
    global question_buffer
    r = sr.Recognizer()
    question_buffer=""
    safe_print("음성 질문 시작 (버튼 누르고 있는 동안)")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while GPIO.input(SW_PIN)==0:
            try:
                audio = r.listen(source, phrase_time_limit=3)
                text = r.recognize_google(audio, language="ko-KR")
                question_buffer += " "+text
                safe_print("녹음:", text)
            except: pass
    question_buffer = question_buffer.strip()
    return question_buffer

# ===== 엔코더 모드 =====
def encoder_polling_worker():
    global encoder_counter, current_mode
    last_clk = GPIO.input(CLK_PIN)
    last_dt = GPIO.input(DT_PIN)
    direction_buffer = []
    stable_time = time.time()
    while True:
        clk = GPIO.input(CLK_PIN)
        dt = GPIO.input(DT_PIN)
        if clk != last_clk:
            if time.time()-stable_time>0.02:
                stable_time=time.time()
                direction=1 if dt!=clk else -1
                direction_buffer.append(direction)
                if len(direction_buffer)>3: direction_buffer.pop(0)
                if len(direction_buffer)==3 and len(set(direction_buffer))==1:
                    encoder_counter=(encoder_counter+direction_buffer[0])%40
                    direction_buffer.clear()
                    if encoder_counter<10: new_mode="book_read"
                    elif encoder_counter<20: new_mode="book_summary"
                    elif encoder_counter<30: new_mode="env"
                    else: new_mode="question_mode"
                    if new_mode!=current_mode:
                        current_mode=new_mode
                        safe_print(f"모드 변경 → {current_mode}")
                        mode_text={
                            "book_read":"책 읽기 모드입니다.",
                            "book_summary":"책 요약 모드입니다.",
                            "env":"주변 상황 인식 모드입니다.",
                            "question_mode":"질문 모드입니다."
                        }
                        tts_and_play(mode_text[current_mode])
        last_clk=clk
        time.sleep(0.002)

# ===== 버튼 =====
def sw_polling_worker():
    global question_buffer
    last_state = GPIO.input(SW_PIN)
    while True:
        state = GPIO.input(SW_PIN)
        if state==0 and last_state==1:
            if current_mode=="question_mode":
                tts_and_play("질문하세요.", speed=voice_speed)
                record_question()
            else:
                handle_capture()
        elif state==1 and last_state==0:
            if current_mode=="question_mode" and question_buffer:
                tts_and_play("AI 챗봇이 응답 중입니다.", speed=voice_speed)
                img = take_picture() if "사진" in question_buffer else None
                resp = query_gemini(question_buffer,img)
                conversation_history.append({"role":"user","parts":question_buffer})
                conversation_history.append({"role":"model","parts":resp})
                save_history(conversation_history)
                tts_and_play(clean_text_for_tts(resp), speed=voice_speed)
                question_buffer=""
        last_state=state
        time.sleep(0.05)

def button_control_worker():
    last_play = GPIO.input(BTN_PLAYSTOP)
    last_speed = GPIO.input(BTN_SPEED)
    while True:
        play = GPIO.input(BTN_PLAYSTOP)
        speed = GPIO.input(BTN_SPEED)
        if play==0 and last_play==1: toggle_play_pause(); time.sleep(0.25)
        if speed==0 and last_speed==1: change_speed(); time.sleep(0.25)
        last_play,last_speed=play,speed
        time.sleep(0.05)

# ==============================================
# Main
# ==============================================
def main():
    safe_print("=== Raspberry Pi Assist Bot 시작 ===")
    
    GPIO.setmode(GPIO.BCM)
    for p in [CLK_PIN, DT_PIN, SW_PIN, BTN_PLAYSTOP, BTN_SPEED]:
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    tts_and_play("안녕하세요. AI 비서를 시작합니다.", speed=voice_speed)

    threading.Thread(target=button_control_worker, daemon=True).start()
    threading.Thread(target=encoder_polling_worker, daemon=True).start()
    threading.Thread(target=sw_polling_worker, daemon=True).start()
    #threading.Thread(target=power_switch_worker, daemon=True).start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        safe_print("종료")
    finally:
        stop_audio()
        GPIO.cleanup()
        safe_print("GPIO 정리 완료")

if __name__=="__main__":
    main()



