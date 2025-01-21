from flask import Flask, jsonify, Response
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import os
import random

# Suppress YOLO logging
import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Camera setup
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 3)

# YOLO model setup
current_dir = os.path.dirname(os.path.abspath(__file__))
weights_path = os.path.join(current_dir, "yolo-Weights", "ppe.pt")
model = YOLO(weights_path, verbose=False)

def count_objects(boxes, class_id):
    return sum(1 for box in boxes if int(box.cls[0]) == class_id)

def calculate_percentage(num_people, count):
    return int((100 / num_people) * (num_people - count)) if num_people > 0 else 0

data_to_send = {
    "person_count": 0,
    "mask_count": 0,
    "vest_count": 0,
    "total": 0
}

def generate_frames():
    global data_to_send
    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 480))
        results = model(frame)

        for result in results:
            boxes = result.boxes
            num_people = count_objects(boxes, class_id=2)  # Assuming 2 is the person class ID
            mask_count = calculate_percentage(num_people, count_objects(boxes, class_id=3))
            vest_count = calculate_percentage(num_people, count_objects(boxes, class_id=4))

            data_to_send = {
                "total": 5 - num_people,  # Replace 5 with the total capacity if needed
                "person_count": num_people,
                "mask_count": mask_count,
                "vest_count": vest_count
            }

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().numpy()
                conf = box.conf[0]
                cls = box.cls[0]
                label = f"{model.names[int(cls)]} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the API backend!"})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/change-variable', methods=['POST'])
def change_variable():
    global cameraNum
    cameraNum = random.randint(1, 10)
    return jsonify({'new_value': cameraNum})

@app.route('/get_data', methods=['GET'])
def get_data():
    global data_to_send
    return jsonify(data_to_send)  # Send all data as JSON

if __name__ == '__main__':
    app.run(debug=True)
