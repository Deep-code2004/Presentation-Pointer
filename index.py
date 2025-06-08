import os
import cv2
from cvzone.HandTrackingModule import HandDetector  # Ensure cvzone is installed
import numpy as np

width = 1280
height = 700
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
hs, ws = int(120), int(213)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False

detector = HandDetector(detectionCon=0.8, maxHands=1)

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

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        indexFinger = lmList[8][0], lmList[8][1]
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold:
            annotationStart = False

            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                print("Left")
                if imgNumber > 0 and not buttonPressed:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1

            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages) - 1 and not buttonPressed:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1

        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 15, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 15, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)

        else:
            annotationStart = False

        if fingers == [0, 1, 0, 0, 1]:
            if annotations and annotationNumber >= 0:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    # Draw annotations
    for i in range(len(annotations)):
        for j in range(1, len(annotations[i])):
            cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

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
        imgNumber = (imgNumber + 1) % len(pathImages)
    elif key == ord('p'):
        imgNumber = (imgNumber - 1) % len(pathImages)

cap.release()
cv2.destroyAllWindows()