import time
import spidev
import RPi.GPIO as GPIO
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
import os
import cv2
import face_recognition
import numpy as np

load_dotenv()

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

LED_PIN = 17
BUTTON_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

THRESHOLD = 3650

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("DB connect")
except mysql.connector.Error as err:
    print(f"DB connect fail: {err}")
    exit(1)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS drunk_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME,
        user_name VARCHAR(255),
        value VARCHAR(50),
        message VARCHAR(255)
    )
""")
conn.commit()

stream_url = "http://192.168.137.1:5000/video"
cap = cv2.VideoCapture(stream_url)                # cap = cv2.VideoCapture(0)    =    Local

if not cap.isOpened():
    print("[ERROR] 카메라를 열 수 없습니다. IP 스트림 주소 확인하세요.")
    conn.close()
    exit(1)
print("[INFO] 카메라가 준비되었습니다.")

known_face_encodings = []
known_face_names = []

try:
    cursor.execute("SELECT name, encoding FROM faces")
    db_faces = cursor.fetchall()
    
    if not db_faces:
        print("[WARNING] 데이터베이스에 등록된 얼굴이 없습니다. 사용자 등록을 먼저 해주세요.")
    else:
        for name, encoding_blob in db_faces:
            known_face_names.append(name)
            known_face_encodings.append(np.frombuffer(encoding_blob, dtype=np.float64))
        print(f"[INFO] {len(known_face_names)}명의 등록된 얼굴 정보를 로드했습니다.")
        
except mysql.connector.Error as err:
    print(f"[ERROR] 'faces' 테이블을 읽는 중 오류 발생: {err}")
    print("사용자 등록을 먼저 하여 데이터베이스가 생성되었는지 확인하세요.")
    conn.close()
    cap.release()
    exit(1)


def read_channel(channel):
    if not (0 <= channel <= 7):
        return -1

    start_bit = 0b00000110
    second_byte = (channel & 0b111) << 6
    response = spi.xfer2([start_bit, second_byte, 0x00])
    
    result = ((response[1] & 0x0F) << 8) | response[2]
    return result

def log_to_db(user, value, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] User: {user} | Value: {value} | {message}")

    cursor.execute(
        "INSERT INTO drunk_log (timestamp, user_name, value, message) VALUES (%s, %s, %s, %s)",
        (timestamp, user, str(value), message)
    )
    conn.commit()

def identify_user(known_encodings, known_names):
    ret, frame = cap.read()
    if not ret or frame is None:
        print("[WARN] 카메라에서 프레임을 읽지 못했습니다.")
        return "Unknown"

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    name = "Unknown"
    
    if face_encodings:
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

    print(f"[INFO] 사용자 식별: {name}")
    return name

print("현재 장소에 대한 측정 기준값(THRESHOLD)을 설정합니다 (10초간 대기)...")
samples = []
start_time = time.time()

while time.time() - start_time < 10:
    value = read_channel(0)
    samples.append(value)
    voltage = (value / 4095.0) * 5.0
    print(f"[Baseline] Raw: {value} | Voltage: {voltage:.2f} V")
    time.sleep(1)

if samples:
    THRESHOLD = (sum(samples) // len(samples)) + 500
else:
    print("[WARNING] 기준값 측정 실패. 기본값 3650 사용.")

print(f"\n=== 기준값(THRESHOLD) 설정 완료: {THRESHOLD} ===\n")
print("- 버튼을 눌러 측정을 시작하세요 -")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("버튼 입력 감지, 측정을 시작합니다.")
            
            user_name = "Unknown"
            if known_face_names:
                user_name = identify_user(known_face_encodings, known_face_names)
            else:
                print("[INFO] 등록된 얼굴이 없어 사용자 식별을 건너뜁니다.")

            raw_value = read_channel(0)
            value_str = f"{raw_value} / {THRESHOLD}"
            
            if raw_value > THRESHOLD:
                log_to_db(user_name, value_str, "Drunk driver")
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                log_to_db(user_name, value_str, "PASS")
                GPIO.output(LED_PIN, GPIO.LOW)

            time.sleep(1)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[INFO] 종료 중... 리소스 정리.")
    GPIO.cleanup()
    conn.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 정리 완료.")
