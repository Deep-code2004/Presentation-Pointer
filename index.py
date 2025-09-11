import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import re
import time

# --- CONSTANTS AND CONFIGURATION ---
WIDTH = 800
HEIGHT = 500
FOLDER_PATH = "Slides"

WEBCAM_OVERLAY_WIDTH = 160
WEBCAM_OVERLAY_HEIGHT = 100

GESTURE_THRESHOLD = 350
BUTTON_DELAY = 1.5  # seconds for button debounce
DRAWING_CIRCLE_RADIUS = 15
DRAWING_LINE_THICKNESS = 12

# --- HELPER FUNCTIONS ---

def natural_sort(l):
    """Sorts strings naturally (e.g., 1, 2, 10 instead of 1, 10, 2)."""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def setup_camera(width, height):
    """Initializes and configures the webcam."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    return cap

def load_slides(folder_path):
    """Loads and returns a sorted list of image paths from the specified folder."""
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return None
    
    path_images = natural_sort(os.listdir(folder_path))
    if not path_images:
        print(f"Error: No images found in '{folder_path}' folder.")
        return None
    
    # Filter for image files
    image_paths = [os.path.join(folder_path, img) for img in path_images if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_paths:
        print(f"Error: No valid image files found in '{folder_path}'.")
        return None

    return image_paths

def draw_annotations(img, annotations):
    """Draws all annotations on the current slide image."""
    for annotation in annotations:
        for j in range(1, len(annotation)):
            cv2.line(img, annotation[j - 1], annotation[j], (0, 0, 200), DRAWING_LINE_THICKNESS)

def main():
    """Main function to run the presentation assistant."""
    cap = setup_camera(WIDTH, HEIGHT)
    if cap is None:
        return

    image_paths = load_slides(FOLDER_PATH)
    if image_paths is None:
        return
    
    # Each slide has its own annotations
    all_annotations = [[] for _ in image_paths]
    annotation_start = False
    
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    
    img_number = 0
    button_pressed = False
    last_button_time = 0

    cv2.namedWindow("Presentation", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Webcam Feed", cv2.WINDOW_NORMAL)

    # Set initial window positions
    screen_width, screen_height = 1366, 768  # Common screen size for centering
    cv2.moveWindow("Presentation", (screen_width - WIDTH) // 2, (screen_height - HEIGHT) // 2)
    cv2.moveWindow("Webcam Feed", 0, 0)
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        
        # Flip the image for a more natural feel
        img = cv2.flip(img, 1)

        # Load the current slide image and resize to fit the presentation window
        path_full_image = image_paths[img_number]
        img_current = cv2.imread(path_full_image)
        if img_current is None:
            print(f"Failed to load image: {path_full_image}")
            break
        img_current = cv2.resize(img_current, (WIDTH, HEIGHT))

        hands, img_processed = detector.findHands(img, flipType=False) # Use flipType=False to match the flipped image

        # Draw a visual guide for the gesture threshold line
        cv2.line(img_processed, (0, GESTURE_THRESHOLD), (WIDTH, GESTURE_THRESHOLD), (0, 255, 0), 5)

        annotations = all_annotations[img_number]

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cy = hand['center'][1]
            lmList = hand['lmList']
            
            # Map hand coordinates to the presentation window for drawing
            x_val = int(np.interp(lmList[8][0], [WIDTH // 2, WIDTH], [0, WIDTH]))
            y_val = int(np.interp(lmList[8][1], [150, HEIGHT - 150], [0, HEIGHT]))
            index_finger = (x_val, y_val)

            # Check for debounce
            current_time = time.time()
            if current_time - last_button_time < BUTTON_DELAY:
                # Show a visual indicator that gestures are on cooldown
                cv2.putText(img_current, "Processing...", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                button_pressed = False
            
            # Slide navigation gestures (above threshold line)
            if cy <= GESTURE_THRESHOLD and not button_pressed:
                # Previous gesture (thumb up)
                if fingers == [1, 0, 0, 0, 0]:
                    if img_number > 0:
                        img_number -= 1
                        button_pressed = True
                        last_button_time = current_time
                        cv2.putText(img_current, "Previous Slide", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Next gesture (pinky up)
                elif fingers == [0, 0, 0, 0, 1]:
                    if img_number < len(image_paths) - 1:
                        img_number += 1
                        button_pressed = True
                        last_button_time = current_time
                        cv2.putText(img_current, "Next Slide", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Drawing/pointing gestures (below threshold line)
            if cy > GESTURE_THRESHOLD:
                # Pointer gesture (index and middle finger up)
                if fingers == [0, 1, 1, 0, 0]:
                    cv2.circle(img_current, index_finger, DRAWING_CIRCLE_RADIUS, (0, 0, 255), cv2.FILLED)
                    annotation_start = False
                
                # Drawing gesture (only index finger up)
                elif fingers == [0, 1, 0, 0, 0]:
                    cv2.circle(img_current, index_finger, DRAWING_CIRCLE_RADIUS, (0, 0, 255), cv2.FILLED)
                    if not annotation_start:
                        annotation_start = True
                        annotations.append([index_finger])
                    else:
                        annotations[-1].append(index_finger)
                
                # Undo gesture (index and pinky up)
                elif fingers == [0, 1, 0, 0, 1] and not button_pressed:
                    if annotations:
                        annotations.pop()
                        button_pressed = True
                        last_button_time = current_time
                        cv2.putText(img_current, "Undo", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                else:
                    annotation_start = False

        # Draw annotations on the slide
        draw_annotations(img_current, annotations)
        
        # Place webcam feed in the upper-right corner of the presentation
        img_small = cv2.resize(img, (WEBCAM_OVERLAY_WIDTH, WEBCAM_OVERLAY_HEIGHT))
        h, w, _ = img_current.shape
        img_current[0:WEBCAM_OVERLAY_HEIGHT, w - WEBCAM_OVERLAY_WIDTH:w] = img_small
        
        cv2.imshow("Webcam Feed", img_processed)
        cv2.imshow("Presentation", img_current)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()