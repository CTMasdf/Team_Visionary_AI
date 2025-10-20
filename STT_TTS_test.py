import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

def speak(text, lang="ko"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang=lang)
        tts.save(fp.name)
        os.system(f"mpg321 {fp.name} > /dev/null 2>&1")  # 사운드 출력
        os.remove(fp.name)

# 음성 인식
r = sr.Recognizer()
with sr.Microphone() as source:
    print(" 말씀하세요:")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio, language="ko-KR")
    print("인식 결과:", text)
    speak(f"당신이 말한 내용은: {text} 입니다.")
    print("당신이 말한내용은:",text, "입니다.")
except Exception as e:
    print(" 인식 실패:", e)
    speak("죄송합니다. 인식하지 못했어요.")
