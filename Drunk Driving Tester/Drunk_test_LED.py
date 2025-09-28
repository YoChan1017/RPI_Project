import spidev
import time
import RPi.GPIO as GPIO   # GPIO 제어용

# SPI 초기화
spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 250000

# GPIO 초기화
LED_PIN = 17  # PIN 11
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

def read_channel(channel):
    cmd = 0x18 | channel  
    r = spi.xfer2([1, cmd << 3, 0])
    value = ((r[1] & 0x0F) << 8) | r[2]
    return value

# 술 마심 여부 판단 기준값
THRESHOLD = 2650

try:
    while True:
        raw_value = read_channel(0)
        adc = spi.xfer2([0b11000000, 0, 0])
        print(f"Raw SPI data: {adc}")
        
        if raw_value > THRESHOLD:
            print("Drunk dirver")
            GPIO.output(LED_PIN, GPIO.HIGH)  # LED 켜기
        else:
            print("PASS")
            GPIO.output(LED_PIN, GPIO.LOW)   # LED 끄기
        
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()
    print("TEST END")
