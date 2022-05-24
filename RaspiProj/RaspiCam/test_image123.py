from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (512, 400)

rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, "bgr")
image = rawCapture.array
# image = cv2.imread('image2.jpg',cv2.IMREAD_COLOR)

# convert to grayscale
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# filter out noise
image = cv2.bilateralFilter(image, 11, 17, 17)

# Get edges
image = cv2.Canny(image, 30, 200)

# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)