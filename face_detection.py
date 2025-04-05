import cv2
from inference_sdk import InferenceHTTPClient
import threading
from config import ROBOFLOW_API_KEY, FACE_DETECTION_MODEL

# Initialize client
roboflow_client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

def detect_in_background(frame_filename, callback):
    """Run face detection in a separate thread"""
    try:
        detections = roboflow_client.infer(
            frame_filename, 
            model_id=FACE_DETECTION_MODEL
        )
        
        if "predictions" in detections:
            callback(detections)
        else:
            callback({"predictions": []})
    except Exception as e:
        callback({"predictions": []})
    
    callback(None, detection_complete=True)

def extract_face_image(frame, detection):
    """Extract face region from frame as an image"""
    x = detection["x"]
    y = detection["y"]
    width = detection["width"]
    height = detection["height"]
    
    margin = 20
    x1 = max(0, int(x - width/2) - margin)
    y1 = max(0, int(y - height/2) - margin)
    x2 = min(frame.shape[1] - 1, int(x + width/2) + margin)
    y2 = min(frame.shape[0] - 1, int(y + height/2) + margin)
    
    face_img = frame[y1:y2, x1:x2]
    return face_img, (x1, y1, x2, y2) 