import time
import random
import RPi.GPIO as GPIO 
from datetime import datetime
import sqlite3

LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

BUTTON_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

THRESHOLD = 650 

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
    return random.randint(0, 4095)
    
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
