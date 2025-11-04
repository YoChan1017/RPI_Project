# [노트BOOK에서 실행] webcam_server.py
from flask import Flask, Response
import cv2

app = Flask(__name__)

# 노트북의 기본 카메라(0번)를 엽니다.
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # 카메라에서 프레임 읽기
        success, frame = cap.read()
        if not success:
            break
        else:
            # 프레임을 JPEG 이미지로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            # 바이트 스트림으로 변환
            frame_bytes = buffer.tobytes()
            
            # HTTP 스트림 형식으로 전송
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    # generate_frames 함수가 생성하는 스트림을 응답으로 보냄
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # '0.0.0.0'은 모든 IP에서의 접속을 허용합니다.
    # 포트는 5000번을 사용합니다.
    print("스트리밍 서버 시작: http://<노트북_IP>:5000/video")
    app.run(host='0.0.0.0', port=5000, debug=False)