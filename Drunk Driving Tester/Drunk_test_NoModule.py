import time
import random

# 술 마심 여부 판단 기준값
THRESHOLD = 650   # 0~4095 범위 가정 / 650 이상일 시 음주 측정

def read_channel(channel): # 실제 센서 대신 0~4095 사이 랜덤값 반환
    return random.randint(0, 4095)

try:
    while True:
        raw_value = read_channel(0)
        if raw_value > THRESHOLD:
            print(f"{raw_value} Drunk dirver")
        else:
            print(f"{raw_value} PASS")
        time.sleep(1)

except KeyboardInterrupt:
    print("Test End")
