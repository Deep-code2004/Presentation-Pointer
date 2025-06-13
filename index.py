import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Medium presentation size
width = 800
height = 500
folderPath = "Slides"

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

if not os.path.exists(folderPath):
    print(f"Error: Folder '{folderPath}' does not exist.")
    exit()

pathImages = sorted(os.listdir(folderPath), key=len)
if not pathImages:
    print("Error: No images found in the 'Slides' folder.")
    exit()

imgNumber = 0
hs, ws = int(100), int(160)  # Webcam overlay size
gestureThreshold = 350       # Lower line for gestures
buttonPressed = False
buttonCounter = 0
buttonDelay = 30

# Each slide has its own annotations
all_annotations = [[] for _ in pathImages]
annotationStart = False

detector = HandDetector(detectionCon=0.8, maxHands=1)

# Center the presentation window (adjust screen_width/height if needed)
cv2.namedWindow("Presentation", cv2.WINDOW_NORMAL)
cv2.namedWindow("Webcam Feed", cv2.WINDOW_NORMAL)
screen_width = 1366
screen_height = 768
cv2.moveWindow("Presentation", (screen_width - width) // 2, (screen_height - height) // 2)
cv2.moveWindow("Webcam Feed", 0, 0)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    if not success:
        print("Failed to capture image from webcam.")
        break

    # Load the current slide image
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    if imgCurrent is None:
        print(f"Failed to load image: {pathFullImage}")
        break
    imgCurrent = cv2.resize(imgCurrent, (width, height))

    # Detect hands in the webcam feed
    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    annotations = all_annotations[imgNumber]

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        indexFinger = lmList[8][0], lmList[8][1]
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        # Slide navigation gestures (above threshold line)
        if cy <= gestureThreshold:
            annotationStart = False

            # Left gesture (thumb up)
            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                if imgNumber > 0 and not buttonPressed:
                    buttonPressed = True
                    imgNumber -= 1

            # Right gesture (pinky up)
            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                if imgNumber < len(pathImages) - 1 and not buttonPressed:
                    buttonPressed = True
                    imgNumber += 1

        # Draw pointer (index and middle finger up)
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 15, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        # Draw annotation (only index finger up)
        elif fingers == [0, 1, 0, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 15, (0, 0, 255), cv2.FILLED)
            if not annotationStart:
                annotationStart = True
                annotations.append([indexFinger])
            else:
                annotations[-1].append(indexFinger)
        else:
            annotationStart = False

        # Undo gesture (index and pinky up)
        if fingers == [0, 1, 0, 0, 1]:
            if annotations:
                annotations.pop(-1)
                buttonPressed = True

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    # Draw annotations
    for annotation in annotations:
        for j in range(1, len(annotation)):
            cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

    # Place webcam feed in the upper-right corner
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    if hs <= h and ws <= w:
        imgCurrent[0:hs, w - ws:w] = imgSmall
    else:
        print("Warning: imgCurrent is too small to fit imgSmall. Skipping this frame.")
        continue

    cv2.imshow("Webcam Feed", imgSmall)
    cv2.imshow("Presentation", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('n'):
        if imgNumber < len(pathImages) - 1:
            imgNumber += 1
    elif key == ord('p'):
        if imgNumber > 0:
            imgNumber -= 1

cap.release()
cv2.destroyAllWindows()