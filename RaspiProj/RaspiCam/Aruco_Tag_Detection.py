#!/usr/bin/env python3
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
from gpiozero import Servo
import RPi.GPIO as GPIO

HIT_DELAY = 1

CORNER_DISTANCE_MIN = 1
ARUCO_CLEAR_DELAY = 1
FRAMERATE = 15
MAX_NUM_ARUCO_CODES = 8

SERVO_PIN=13
FRIENDLY_PIN=23 #green LED
ENEMY_PIN=24 #red LED
OBJECT_PIN =6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FRIENDLY_PIN,GPIO.OUT)
GPIO.setup(ENEMY_PIN,GPIO.OUT)
GPIO.setup(OBJECT_PIN,GPIO.OUT)

servo = Servo(SERVO_PIN)
servo.min()
time.sleep(1)
servo.detach()
#Blink LED function
def blinkLED(pinNum):
    GPIO.output(pinNum,1)
    time.sleep(1)
    GPIO.output(pinNum,0)

##boot indication
blinkLED(FRIENDLY_PIN)

# imshow will start the window thread if not already started, however,
# this give the window more time to initialize
#cv2.startWindowThread()

camera = PiCamera()
camera.resolution = (512, 400)
camera.framerate = FRAMERATE
rawCapture = PiRGBArray(camera)

idsHandled = []

# camera = cv2.VideoCapture(0)
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

# allow the camera to warmup
time.sleep(0.5)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    if len(idsHandled) >= MAX_NUM_ARUCO_CODES:
        break
    GPIO.output(OBJECT_PIN,0)
    image = frame.array
#while True:
#    _,image = camera.read()

    # convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # rotate image by 180 degrees
    image = cv2.rotate(image, cv2.ROTATE_180);

#    cv2.imshow('image', image)
#    cv2.waitKey(1)

    arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_6X6_250) #_ARUCO_ORIGINAL
    arucoParams = aruco.DetectorParameters_create()
    (cornerSets, ids, rejected) = aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

    print("\nids: ")
    print(ids)
    #print("\ncornerSets: ")
    #print(cornerSets)
    if len(cornerSets) > 0:
        for index in range(len(ids)):
            cornerSet = cornerSets[index]
            firstCornerX = cornerSet[0][0][0]
            secondCornerX = cornerSet[0][1][0]

            #print("\nfirst x: ")
            #print(firstCornerX)
            #print("\nsecond x: ")
            #print(secondCornerX)

            cornerDistance = abs(firstCornerX - secondCornerX)
            #print("\ndistance: ")
            #print(cornerDistance)

            if cornerDistance > CORNER_DISTANCE_MIN:
                currentId = ids[index]
                if currentId not in idsHandled:
                    GPIO.output(OBJECT_PIN,1)
                    
                    if currentId >= 10:
                        print("\nenemy detected")
                        servo.max()
                        time.sleep(HIT_DELAY)
                        servo.min()
                        time.sleep(HIT_DELAY)
                        servo.detach()
                        blinkLED(ENEMY_PIN)

                    else:
                        print("\nfriendly detected")
                        blinkLED(FRIENDLY_PIN)


                    idsHandled.append(currentId)
                else:
                    print("\ncode already handled")

                time.sleep(ARUCO_CLEAR_DELAY)
                GPIO.output(OBJECT_PIN,0)
            else:
                print("code too far")
                GPIO.output(OBJECT_PIN,0)


    rawCapture.truncate(0)
#    time.sleep(0.5)

print("shutting down")
#camera.release()
cv2.destroyAllWindows()



# TODO: optional send message to parralax to stop
