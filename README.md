# Webcam Drowning Detection

A real-time webcam-based drowning detection system using YOLO11 and Flask.

## Features

- Real-time object detection via webcam
- Flask-based API server
- Web interface for live detection
- Audio alerts for detections

## Setup

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Place your YOLO model file (`best.pt`) in the project directory

3. Run the server:
```bash
python server.py
```

4. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

- `GET /` - Serves the web interface
- `POST /predict` - Receives base64-encoded image and returns detections

## Project Structure

- `server.py` - Flask server with YOLO inference
- `index.html` - Web interface for webcam detection
- `best.pt` - YOLO model file
- `alarm.mp3` - Alert sound file
- `requirements.txt` - Python dependencies

