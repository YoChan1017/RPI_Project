import time
import spidev
import RPi.GPIO as GPIO 
from datetime import datetime
import sqlite3

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

BUTTON_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DB_FILE = "drunk_log.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        value TEXT,
        message TEXT
    )
""")
conn.commit()

def read_channel(channel): 
    if not (0 <= channel <= 7):
        return -1

    start_bit = 0b00000110
    second_byte = (channel & 0b111) << 6
    response = spi.xfer2([start_bit, second_byte, 0x00])
    print(response)
    
    result = ((response[1] & 0x0F) << 8) | response[2]
    return result

# 10초간 현재 장소/환경에 대한 평균 수치 측정
print("Measuring baseline for 10 seconds...")

samples = []
start_time = time.time()
while time.time() - start_time < 10:
    value = read_channel(0)
    samples.append(value)
    voltage = (value / 4095.0) * 5.0
    print(f"[Baseline] Raw: {value} | Voltage: {voltage:.2f} V")
    time.sleep(1)
THRESHOLD = (sum(samples) // len(samples)) + 500

print(f"\n=== Baseline THRESHOLD set to: {THRESHOLD} ===\n")
    
def log_to_db(value, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {value} / {message}")
    
    cursor.execute("INSERT INTO log (timestamp, value, message) VALUES (?, ?, ?)",
                   (timestamp, str(value), message))
    conn.commit()

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            raw_value = read_channel(0)
            
            if raw_value > THRESHOLD:
                log_to_db(raw_value, "Drunk driver")
                GPIO.output(LED_PIN, GPIO.HIGH) 
            else:
                log_to_db(raw_value, "PASS")
                GPIO.output(LED_PIN, GPIO.LOW)

            time.sleep(1)
        else:
            time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
    conn.close()

