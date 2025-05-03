import cv2
import os
width = 1280
height = 720
folderPath = "Slides"

cap = cv2.VideoCapture(0)
cap.set(3, width)  # Set width
cap.set(4, height)  # Set height

pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

imgNumber = 0

while True:
    success, img = cap.read()
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    
    # Resize the images to the desired width and height
    img = cv2.resize(img, (width, height))
    imgCurrent = cv2.resize(imgCurrent, (width, height))
    
    cv2.imshow("Image", img)
    cv2.imshow("Presentation", imgCurrent)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break