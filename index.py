import cv2
import os
from cvzone.HandTrackingModule import HandDetector

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

print("Loaded slides:", pathImages)

imgNumber = 0
hs, ws = int(120), int(213)  # Height and width of the small image (webcam feed)

# Initialize HandDetector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image from webcam.")
        break

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