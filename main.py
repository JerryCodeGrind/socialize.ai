import cv2
import os
import threading
import json
from config import FRAME_WIDTH, FRAME_HEIGHT
from face_detection import detect_in_background, extract_face_image
from ui import create_overlay, draw_detections
from search import search_face_in_background

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Set dimensions for video frame
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Variables for detection and search management
cached_detections = {"predictions": []}
detection_active = False
search_active = False
search_results = []
search_face_img = None
search_status = ""
show_results_overlay = False

# Main loop
while True:
    # Capture frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    
    # Start detection if not active
    if not detection_active:
        detection_active = True
        
        # Save current frame
        temp_file = "temp_frame.jpg"
        cv2.imwrite(temp_file, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        # Define callback
        def detection_callback(results, detection_complete=False):
            global cached_detections, detection_active
            if results is not None:
                cached_detections = results
            if detection_complete:
                detection_active = False
        
        # Start detection in thread
        threading.Thread(target=detect_in_background, args=(temp_file, detection_callback)).start()
    
    # Create display frame and draw detection boxes
    display_frame, active_face_roi = draw_detections(frame, cached_detections)
    
    # Always force show overlay if we have results regardless of button press
    if search_results and active_face_roi and not search_active:
        display_frame = create_overlay(display_frame, active_face_roi, search_results)
    elif search_active:
        # Show a "Searching..." indicator while active
        cv2.putText(
            display_frame,
            "Searching...",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1
        )
    
    # Display frame
    cv2.imshow("Face Analysis", display_frame)
    
    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('r') and not search_active:
        # Check for faces
        if cached_detections.get("predictions"):
            # Extract face image
            face_img, face_roi = extract_face_image(frame, cached_detections["predictions"][0])
            
            # Store face image and ROI
            search_face_img = face_img.copy()
            active_face_roi = face_roi
            
            # Start search
            search_active = True
            show_results_overlay = True  # Ensure overlay is visible
            
            # Define callback
            def search_callback(status=None, results=None, search_complete=False):
                global search_status, search_results, search_active, show_results_overlay
                if status is not None:
                    search_status = status
                if results is not None:
                    search_results = results
                    show_results_overlay = True
                if search_complete:
                    search_active = False
            
            # Start search in thread
            threading.Thread(target=search_face_in_background, args=(face_img, search_callback)).start()
    elif key == ord('h'):
        # Toggle results overlay
        show_results_overlay = not show_results_overlay

# Clean up
if os.path.exists("temp_frame.jpg"):
    try:
        os.remove("temp_frame.jpg")
    except:
        pass

cap.release()
cv2.destroyAllWindows() 