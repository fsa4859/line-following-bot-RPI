import RPi.GPIO as GPIO
import time

servoPin = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(2.5)

print("waiting for one second")
time.sleep(1)
print("Rotating at intervals of 12 degrees")

servo.ChangeDutyCycle(10)
time.sleep(2)
servo.ChangeDutyCycle(0)

servo.stop()
GPIO.cleanup()
print("all clean")
