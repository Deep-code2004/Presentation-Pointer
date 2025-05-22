import os
import cv2
from cvzone.HandTrackingModule import HandDetector  # Ensure cvzone is installed
import numpy as np
# Desired dimensions for the presentation and webcam feed
width = 1280
height = 700
folderPath = "Slides"

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)  # Set webcam width
cap.set(4, height)  # Set webcam height

# Load slide images
if not os.path.exists(folderPath):
    print(f"Error: Folder '{folderPath}' does not exist.")
    exit()

pathImages = sorted(os.listdir(folderPath), key=len)
if not pathImages:
    print("Error: No images found in the 'Slides' folder.")
    exit()

# print("Loaded slides:", pathImages)

imgNumber = 0
hs, ws = int(120), int(213)  # Height and width of the small image (webcam feed)
gestureThreshold = 300  # Threshold for gesture detection
# Initialize HandDetector
buttonPressed =False
buttonCounter = 0
buttonDelay = 30
anntations = [] #empty list


detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img cv2.flip(img, 1)
    if not success:
        print("Failed to capture image from webcam.")
        break

    # Detect hands in the webcam feed
    hands, img = detector.findHands(img)# Draw hand landmarks on the webcam feed
    cv2.line(img,(0, gestureThreshold),(width, gestureThreshold),(0,255,0),10)
    if hands: 
        hand = hands[0]
        fingers = detector.fingersUp(hand)# Check which fingers are up
        cx, cy = hand['center']
        lmList = hand['lmList']
        
        indexFinger = lmList[8][0], lmList[8][1]
        xVal = int(np.interp(lmList[8][0],[width//2,w],[0,width]))
        yVal = int(np.interp(lmList[8][1],[150,height-150],[0,height]))
        indexFinger = xVal , yVal
        
        if cy <=gestureThreshold: #if hand is above the threshold
           if fingers == [1, 0, 0, 0, 0]: #if only the index finger is up
                print("Left")
                buttonPressed = True 
                if imgNumber>0:
                    buttonPressed = True
                    imgNumber -= 1
                
            if fingers == [0, 0, 0, 0, 1]: #if only the index finger is up
                print("Right")  
                buttonPressed = True 
                if imgNumber< len(pathImages) - 1:
                     buttonPressed = True
                     imgNumber += 1
            
        if fingers == [0,1,1,0,0]:
            cv2.circle(imgCurrent, indexFinger, 15,(0,0,255), cv2.FILLED) 
        if fingers == [0,1,0,0,0]:
            cv2.circle(imgCurrent, indexFinger, 15,(0,0,255), cv2.FILLED) 
            annotations.append(indexFinger)         
    if buttonPressed:
       buttonCounter +=1
       if buttonCounter> buttonDelay:   
            buttonCounter = 0
            buttonPressed = False      


    for i in range (len(annotations)):                  
        cv2.line(imgCurrent,annotation[i-1],annotations[i],(0,0,200),12)
    if hands:
        for hand in hands:
            print(f"Hand detected: {hand['type']}")  # Print hand type (left or right)
            print(f"Landmarks: {hand['lmList']}")  # Print landmarks
            print(f"Bounding Box: {hand['bbox']}")  # Print bounding box

    # Resize the webcam feed to the desired small size

    imgSmall = cv2.resize(img, (ws, hs))
    # Load the current slide image
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    
    

    if imgCurrent is None:
        print(f"Failed to load image: {pathFullImage}")
        break

    # Resize the slide image to the desired presentation size
    imgCurrent = cv2.resize(imgCurrent, (width, height))

    # Ensure imgCurrent is large enough to hold imgSmall
    h, w, _ = imgCurrent.shape
    if hs <= h and ws <= w:
        # Place imgSmall in the upper-right corner of imgCurrent
        imgCurrent[0:hs, w - ws:w] = imgSmall
    else:
        print("Warning: imgCurrent is too small to fit imgSmall. Skipping this frame.")
        continue

    # Display the images
    cv2.imshow("Webcam Feed", imgSmall)  # Resized webcam feed
    cv2.imshow("Presentation", imgCurrent)  # Presentation with overlay

    # Handle keypresses
    key = cv2.waitKey(1)
    if key == ord('q'):  # Quit
        break
    elif key == ord('n'):  # Move to the next slide
        imgNumber = (imgNumber + 1) % len(pathImages)
    elif key == ord('p'):  # Move to the previous slide
        imgNumber = (imgNumber - 1) % len(pathImages)

cap.release()
cv2.destroyAllWindows()