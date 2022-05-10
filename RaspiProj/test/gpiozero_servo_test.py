import time
from gpiozero import AngularServo

servoPin = 25

servo = AngularServo(servoPin, min_angle=0, max_angle=180)
servo.angle=0
time.sleep(2)
servo.angle=90
time.sleep(2)
servo.angle=180