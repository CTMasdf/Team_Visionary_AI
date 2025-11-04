import RPi.GPIO as GPIO
import time

# --- 핀 설정 (BCM 기준) ---
CLK = 17   # Rotary Encoder CLK 핀
DT = 18    # Rotary Encoder DT 핀
SW = 27    # Rotary Encoder 버튼 핀

GPIO.setmode(GPIO.BCM)

# 입력 핀 + 내부 풀업 사용
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 초기 상태 읽기
clkLastState = GPIO.input(CLK)
counter = 0  # 회전 카운터 변수

try:
    while True:
        # 현재 CLK 입력 읽기
        clkState = GPIO.input(CLK)
        dtState = GPIO.input(DT)

        # 회전 방향 체크 (CLK 신호 변화 시 판단)
        if clkState != clkLastState:
            # DT가 CLK와 다른 경우 → 시계 방향 (CW)
            if dtState != clkState:
                counter += 1
                print(f"CW (시계 방향) → Counter: {counter}")
            # 같은 경우 → 반시계 방향 (CCW)
            else:
                counter -= 1
                print(f"CCW (반시계 방향) → Counter: {counter}")

            # 마지막 CLK 상태 업데이트
            clkLastState = clkState

        # 버튼 누르면 카운터 초기화
        if GPIO.input(SW) == 0:
            counter = 0
            print("Button Pressed → Counter Reset to 0")
            time.sleep(0.2)  # 디바운스
        
        # CPU 부하 방지용 딜레이
        time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nGPIO Cleaned Up. Program End.")
