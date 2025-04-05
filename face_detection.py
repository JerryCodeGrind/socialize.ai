import cv2
from inference_sdk import InferenceHTTPClient
import threading
import os
from config import ROBOFLOW_API_KEY

# Initialize client
roboflow_client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

# Initialize local face detector as backup
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_locally(image_path):
    """Use OpenCV to detect faces locally"""
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        return {"predictions": []}
        
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Format predictions to match Roboflow format
    predictions = []
    for (x, y, w, h) in faces:
        # Convert to center format
        center_x = x + w/2
        center_y = y + h/2
        
        predictions.append({
            "x": center_x,
            "y": center_y,
            "width": w,
            "height": h,
            "confidence": 0.9  # Default confidence
        })
    
    return {"predictions": predictions}

def detect_in_background(frame_filename, callback):
    """Run face detection in a separate thread"""
    try:
        # Use the Roboflow workflow API
        result = roboflow_client.run_workflow(
            workspace_name="uyfjgk",
            workflow_id="custom-workflow",
            images={
                "image": frame_filename
            },
            use_cache=True # cache workflow definition for 15 minutes
        )
        
        # Check if we have predictions and format them properly
        if result and "predictions" in result:
            callback(result)
        else:
            # Fall back to local detection if no predictions
            local_detections = detect_locally(frame_filename)
            callback(local_detections)
            
    except Exception as e:
        print(f"Roboflow workflow error: {e}")
        
        # Fallback to local detection
        try:
            print("Falling back to local face detection")
            local_detections = detect_locally(frame_filename)
            callback(local_detections)
        except Exception as local_e:
            print(f"Local detection error: {local_e}")
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