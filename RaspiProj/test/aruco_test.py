from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
from gpiozero import Servo

SERVO_PIN = 25
HIT_DELAY = 3
CORNER_DISTANCE_MIN = 60
ARUCO_CLEAR_DELAY = 1
FRAMERATE = 5
MAX_NUM_ARUCO_CODES = 8

servo = Servo(SERVO_PIN)
servo.min()
servo.detach()

# imshow will start the window thread if not already started, however,
# this give the window more time to initialize
cv2.startWindowThread()

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
    
    image = frame.array
#while True:
#    _,image = camera.read()

    # convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # rotate image by 180 degrees
    image = cv2.rotate(image, cv2.ROTATE_180);

    #cv2.imshow('image', image)
    #cv2.waitKey(1)

    arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_6X6_250) #_ARUCO_ORIGINAL
    arucoParams = aruco.DetectorParameters_create()
    (cornerSets, ids, rejected) = aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

    print("\nids: ")   
    print(ids)
    print("\ncornerSets: ")
    print(cornerSets)
    
    if len(cornerSets) > 0:
        for index in range(len(ids)):
            cornerSet = cornerSets[index]
            firstCornerX = cornerSet[0][0][0]
            secondCornerX = cornerSet[0][1][0]
            
            print("\nfirst x: ")   
            print(firstCornerX)
            print("\nsecond x: ")
            print(secondCornerX)
            
            cornerDistance = abs(firstCornerX - secondCornerX)
            print("\ndistance: ")
            print(cornerDistance)
        
            if cornerDistance > CORNER_DISTANCE_MIN:
                currentId = ids[index]                
                if currentId not in idsHandled:
                    if currentId >= 10:
                        print("enemy detected")
                        # TODO: turn on red LED
                        servo.max()
                        setvo.detach()
                        time.sleep(HIT_DELAY)
                        servo.min()
                        servo.detach()
                    else:
                        print("friendly detected")
                        # TODO: turn on green LED
                    
                    idsHandled.append(currentId)  
                else:
                    print("code already handled")
                
                time.sleep(ARUCO_CLEAR_DELAY)
            else:
                print("code too far")
        
    
    rawCapture.truncate(0)
#    time.sleep(0.5)

print("shutting down")
#camera.release()
cv2.destroyAllWindows()

# TODO: optional send message to parralax to stop
