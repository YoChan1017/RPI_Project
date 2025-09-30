import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 250000

def read_channel(channel):
    cmd = 0x18 | channel  
    r = spi.xfer2([1, cmd << 3, 0])
    value = ((r[1] & 0x0F) << 8) | r[2]
    return value

# 술 마심 여부를 판단할 기준값 (실험적으로 조정 필요)
THRESHOLD = 2650   # 0 ~ 4095 사이 값 / 1차 테스트 결과 기준 기본 수치 1200 이하, 알콜측정 3000이상으로 중간 값 설정

try:
    while True:
        raw_value = read_channel(0)
        adc = spi.xfer2([0b11000000, 0, 0])
        print(f"Raw SPI data: {adc}")
        
        if raw_value > THRESHOLD:
            print("Drunk dirver")
        else:
            print("PASS")
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
    print("TEST END")


