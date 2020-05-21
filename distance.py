import RPi.GPIO as GPIO
import time

# measuring distance between stove and cat

def distance(GPIO_TRIGGER, GPIO_ECHO):
    ##send wave signal 
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StopTime = 0 
    StartTime = 0

    ##cnt --> for fix error
    cnt=0
    while GPIO.input(GPIO_ECHO) == 1:
        StartTime = time.time()
        cnt+=1
        if cnt>2000 : 
            return 100


    cnt=0
    while GPIO.input(GPIO_ECHO) == 0:
        StopTime = time.time()
        cnt+=1
        if cnt>2000 : 
            return 100



    TimeElapsed = StopTime-StartTime

    distance = (TimeElapsed*34300) / 2

    return distance
