from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import MySQL
import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import threading


app = Flask(__name__)
averageForce = MySQL.AverageForce()
TrainMange = MySQL.TrainingManager()
flag = False
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Myoware 데이터 읽기를 위한 설정
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = DigitalInOut(board.D5)
mcp = MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP3008.P0)  # MCP3008의 채널 0에 Myoware 연결

# 플래그 및 스레드 초기화
flag = True


@app.route('/')  # 메인 페이지
def main():
    return render_template("main.html")

@app.route('/userguide')
def userguide():
    return render_template("userguide.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/pretrain')
def pretrain():
    return render_template("pretrain.html")

@app.route('/training')
def training():
    return render_template("training.html")

@app.route('/graph')
def graph():
    return render_template("graph.html")

@app.route('/training/history')  # 훈련 현황 보여주기
def history():
    try:
        history_data = averageForce.getHistory()

        if not history_data:
            return jsonify({"status": "error", "message": "No training history found."}), 404

        return jsonify({
            "status": "success",
            "message": "Training history retrieved successfully.",
            "data": history_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred while retrieving the training history: {str(e)}"
        }), 500



@app.route('/training/average-force/save', methods=['POST'])  # 평균 힘 저장
def avg_force_save():
    try:
        force = request.json.get('force')

        if not force:
            return jsonify({
                "status": "error",
                "message": "No force value provided."
            }), 400

        averageForce.saveForce(force)
        return jsonify({
            "status": "success",
            "message": "Average force saved successfully."
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while saving the average force. Please try again later."
        }), 500



@app.route('/training/set-reps', methods=['POST'])  # 세트 및 횟수 설정
def set_reps():
    try:
        # 요청 본문에서 세트, 횟수, 휴식 값을 가져옵니다.
        sets = request.json.get('sets')
        reps = request.json.get('reps')
        rest = request.json.get('rest')

        # 세트, 횟수, 휴식 값이 모두 제공되었는지 확인
        if sets is None or reps is None or rest is None:
            return jsonify({
                "status": "error",
                "message": "Missing one or more parameters (sets, reps, rest)."
            }), 400

        # 세트, 횟수, 휴식 값이 유효한 지 확인
        if not isinstance(sets, int) or not isinstance(reps, int) or not isinstance(rest, int):
            return jsonify({
                "status": "error",
                "message": "Sets, reps, and rest must be integers."
            }), 400

        if sets <= 0 or reps <= 0 or rest <= 0:
            return jsonify({
                "status": "error",
                "message": "Sets, reps, and rest must be positive numbers."
            }), 400

        # 세트, 횟수, 휴식 값을 설정하는 로직 (예시로 TrainingManager 객체 사용)
        TrainMange.setReps(sets, reps, rest)

        # 성공적으로 설정되었을 경우 200 상태 코드와 메시지 반환
        return jsonify({
            "status": "success",
            "message": "Sets, reps, and rest successfully updated."
        })

    except Exception as e:
        # 예외가 발생한 경우 500 상태 코드와 오류 메시지 반환
        return jsonify({
            "status": "error",
            "message": "An error occurred while setting reps. Please try again later."
        }), 500

@app.route('/training/process/start', methods=['POST'])  # 훈련 시작하기
def process_start():
    return handle_process("start")

@app.route('/training/process/stop', methods=['POST'])  # 훈련 중단하기
def process_stop():
    return handle_process("stop")

def handle_process(action):
    global flag
    try:
        if action == "start":
            flag = True
            socketio.start_background_task(emit_sensor_data)
            message = "Process started successfully."
        elif action == "stop":
            flag = False
            message = "Process stopped successfully."
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid action specified."
            }), 400

        return jsonify({
            "status": "success",
            "message": message
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while handling the process. Please try again later."
        }), 500


def emit_sensor_data():
    global flag
    while flag:
        # 센서 값 읽기
        sensor_value = chan.value  # 16비트 정수 값 (0~65535)
        voltage = chan.voltage  # 전압 값 (0~3.3V)

        # 소켓 이벤트 송신
        socketio.emit('sensor_data', {'value': sensor_value, 'voltage': voltage})
        print(f"Sensor Value: {sensor_value}, Voltage: {voltage:.2f}V")
        time.sleep(1)

if __name__ == '__main__':
    # 센서 데이터 스레드 실행
    sensor_thread = threading.Thread(target=emit_sensor_data)
    sensor_thread.start()

    try:
        socketio.run(app, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        flag = False
        sensor_thread.join()
        print("Shutting down server.")


