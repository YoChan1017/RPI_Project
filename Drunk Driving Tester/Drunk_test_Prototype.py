import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 1350000

def read_channel(channel):
    cmd = 0b11000000 | (channel << 3)
    adc = spi.xfer2([cmd, 0, 0])
    value = ((adc[0] & 0x01) << 11) | (adc[1] << 3) | (adc[2] >> 5)
    return value

# 술 마심 여부를 판단할 기준값 (실험적으로 조정 필요)
THRESHOLD = 650   # 0 ~ 4095 사이 값 / 알콜 솜 기준 600~700 이상으로 설정

try:
    while True:
        raw_value = read_channel(0)
        if raw_value > THRESHOLD:
            print("Drunk dirver")
        else:
            print("PASS")
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
    print("TEST END")
