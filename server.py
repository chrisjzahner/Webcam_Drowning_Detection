from ultralytics import YOLO
from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import base64
import time

app = Flask(__name__)

# Load model
print("Loading model...")
MODEL_PATH = "best_m_200.pt"
model = YOLO(MODEL_PATH)
print("Model loaded, moving to CPU...")
model.to("cpu")
print("Model ready!")

CONF_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Drowning-specific confidence threshold (higher to reduce false positives)
DROWNING_CONF_THRESHOLD = 0.65

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

        # Apply higher confidence threshold for drowning class
        if cls_name.lower() == "drowning" and conf < DROWNING_CONF_THRESHOLD:
            continue  # Skip this detection if confidence is too low

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
    import os
    import ssl
    
    # Check if SSL certificates exist
    cert_file = "cert.pem"
    key_file = "key.pem"
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # Create SSL context
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            
            print("🔒 Starting server with HTTPS on port 5000")
            print("   Access at: https://192.168.86.81:5000")
            print("   ⚠️  You'll see a security warning - click 'Advanced' then 'Proceed'")
            app.run(host="0.0.0.0", port=5000, debug=False, ssl_context=context, threaded=True, use_reloader=False)
        except Exception as e:
            print(f"Error with SSL: {e}")
            print("Falling back to HTTP...")
            app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    else:
        print("⚠️  SSL certificates not found. Running without HTTPS.")
        print("   To enable HTTPS (required for iOS), run: python generate_cert.py")
        print("   Then restart the server.")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
