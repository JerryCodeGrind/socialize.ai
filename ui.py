import cv2
import re
from config import FRAME_WIDTH, FRAME_HEIGHT

def create_overlay(display_frame, face_roi, search_results):
    """Create an overlay with website results on the main display frame"""
    if not search_results or len(search_results) == 0:
        return display_frame
    
    # Make a copy to avoid modifying the original
    overlay_frame = display_frame.copy()
    
    # Create semi-transparent overlay background
    overlay = overlay_frame.copy()
    
    # Draw overlay
    overlay_width = FRAME_WIDTH // 2
    overlay_x = FRAME_WIDTH - overlay_width
    cv2.rectangle(overlay, (overlay_x, 0), (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0), -1)
    
    # Show results
    result_y = 30  # Start closer to top
    
    for result in search_results:
        snippet = result.get('snippet', '')
        
        # Skip if no snippet
        if not snippet:
            continue
            
        # Extract the name and overview first
        name = "Unknown"
        overview = "No identifiable personal information found."
        
        # Parse the snippet to extract name and overview
        lines = snippet.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("Name:"):
                name = line[5:].strip()
            elif line.startswith("Overview:"):
                overview = line[9:].strip()
        
        # Display the name and overview first
        cv2.putText(
            overlay,
            f"Name: {name}",
            (overlay_x + 10, result_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,  # Larger font for name
            (255, 255, 255),  # White color for name
            1
        )
        result_y += 25  # More space after name
        
        # Split overview into multiple lines if too long
        if len(overview) > 40:
            words = overview.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 40:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                cv2.putText(
                    overlay,
                    line,
                    (overlay_x + 10, result_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,  # Slightly smaller font for overview
                    (200, 200, 255),  # Light blue for overview
                    1
                )
                result_y += 20
        else:
            cv2.putText(
                overlay,
                overview,
                (overlay_x + 10, result_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,  # Slightly smaller font for overview
                (200, 200, 255),  # Light blue for overview
                1
            )
            result_y += 20
        
        # Add a title for tips
        cv2.putText(
            overlay,
            "Tips:",
            (overlay_x + 10, result_y + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 200),  # Light yellow for tips header
            1
        )
        result_y += 25  # Space after tips header
            
        # Extract individual jot notes from the snippet
        jot_notes = []
        
        # First try to find existing bullet points
        if "•" in snippet or "-" in snippet:
            lines = snippet.split('\n')
            for line in lines:
                if line.strip() and (line.strip().startswith("•") or line.strip().startswith("-")):
                    # Skip header lines
                    if "Tips for socializing" not in line:
                        # Remove the ??? characters that might appear
                        clean_line = line.replace("???", "").strip()
                        jot_notes.append(clean_line)
        
        # If no bullet points found, try to split by common separators
        if not jot_notes:
            for line in re.split(r'[-•]|\d+\.|\n', snippet):
                line = line.strip()
                if line and len(line) > 3 and "Tips for socializing" not in line and "Name:" not in line and "Overview:" not in line:
                    jot_notes.append(line)
        
        # Display each jot note on its own line
        for note in jot_notes:
            # Truncate long notes
            if len(note) > 40:  # Make max length shorter to ensure it fits
                note = note[:37] + "..."
                
            # Add a bullet point if it doesn't already have one
            if not (note.startswith("•") or note.startswith("-")):
                display_note = "• " + note
            else:
                display_note = note
                
            # Remove any question marks
            display_note = display_note.replace("???", "")
            
            # Calculate if text will extend beyond screen edge
            text_size = cv2.getTextSize(display_note, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
            if overlay_x + 10 + text_size[0] > FRAME_WIDTH:
                # If text would go off screen, truncate further
                max_width = FRAME_WIDTH - overlay_x - 20
                while text_size[0] > max_width and len(display_note) > 10:
                    display_note = display_note[:-4] + "..."
                    text_size = cv2.getTextSize(display_note, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
            
            cv2.putText(
                overlay,
                display_note,
                (overlay_x + 10, result_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,  # Smaller font
                (0, 255, 0),  # Green color for tips
                1
            )
            result_y += 20  # Less space between jot notes
            
            # Stop if running out of space
            if result_y > FRAME_HEIGHT - 10:
                break
        
        # Only process the first result with content
        break
    
    # Blend overlay with display frame
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, display_frame, 1 - alpha, 0, display_frame)
    
    return display_frame

def draw_detections(frame, detections):
    """Draw face detection boxes on the frame"""
    display_frame = frame.copy()
    active_face_roi = None
    
    for i, detection in enumerate(detections.get("predictions", [])):
        # Get coordinates
        x = detection["x"]
        y = detection["y"]
        width = detection["width"]
        height = detection["height"]
        
        # Calculate corners
        x1 = int(x - width/2)
        y1 = int(y - height/2)
        x2 = int(x + width/2)
        y2 = int(y + height/2)
        
        # Ensure within bounds
        h, w = display_frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w-1, x2), min(h-1, y2)
        
        # Store first face ROI
        if i == 0:
            active_face_roi = (x1, y1, x2, y2)
        
        # Draw rectangle
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        if "confidence" in detection:
            confidence = detection["confidence"]
            confidence_text = f"{confidence:.2f}"
            cv2.putText(
                display_frame, 
                confidence_text, 
                (x1, y1-5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 255, 0), 
                1
            )
    
    return display_frame, active_face_roi 