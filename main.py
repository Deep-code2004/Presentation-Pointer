import cv2
import os
width = 1280
height = 720
folderPath = "Slides"

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

while True:
  success, img =cap.read()
  
  
  
  cv2.imshow("Image", img)
  key = cv2.waitKey(1)
  if key == ord('q'):
    break