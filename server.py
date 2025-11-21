from ultralytics import YOLO
from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import base64
import time

app = Flask(__name__)

# Load model
MODEL_PATH = "best.pt"
model = YOLO(MODEL_PATH)
model.to("cpu")

CONF_THRESHOLD = 0.4
IOU_THRESHOLD = 0.45

# ---------------------------
# ROUTE 1: SERVE INDEX.HTML
# ---------------------------
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")


# ---------------------------
# ROUTE 2: PREDICT
# ---------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if "image" not in data:
        return jsonify({"error": "No image sent"}), 400

    # Decode base64 string
    try:
        img_str = data["image"].split(",")[1]
        img_bytes = base64.b64decode(img_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except:
        return jsonify({"error": "Bad image decode"}), 400

    # YOLO inference
    t0 = time.time()
    results = model.predict(img, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
    t1 = time.time()

    detections = []
    res = results[0]

    for box in res.boxes:
        xyxy = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = res.names[cls_id]

        detections.append({
            "x1": xyxy[0],
            "y1": xyxy[1],
            "x2": xyxy[2],
            "y2": xyxy[3],
            "conf": conf,
            "class_id": cls_id,
            "class_name": cls_name
        })

    return jsonify({
        "detections": detections,
        "inference_time_ms": (t1 - t0) * 1000
    })


# ---------------------------
# START SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
