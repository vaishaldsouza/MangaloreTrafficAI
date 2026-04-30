from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import cv2, numpy as np
from ultralytics import YOLO
import base64

router = APIRouter()
model = YOLO("yolov8n.pt")  # auto-downloads COCO pretrained

VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

@router.post("/detect")
async def detect_vehicles(file: UploadFile = File(...)):
    img_bytes = await file.read()
    arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    results = model(frame)[0]
    
    counts = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
    detections = []

    for box in results.boxes:
        cls = int(box.cls)
        if cls not in VEHICLE_CLASSES:
            continue
        label = VEHICLE_CLASSES[cls]
        counts[label] += 1
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detections.append({
            "label": label,
            "confidence": round(float(box.conf), 2),
            "bbox": [x1, y1, x2, y2]
        })

    # Annotated image as base64
    annotated = results.plot()
    _, buf = cv2.imencode(".jpg", annotated)
    img_b64 = base64.b64encode(buf).decode()

    return JSONResponse({
        "total": sum(counts.values()),
        "counts": counts,
        "detections": detections,
        "annotated_image": img_b64
    })
