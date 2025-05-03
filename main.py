import cv2
width = 1280
height = 720
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

while True:
  success, img =cap.read()
  cv2.imshow("Image", img)
  key = cv2.waitKey(1)
  if key == ord('q'):
    break