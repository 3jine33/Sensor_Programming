import time
import RPi.GPIO as GPIO

# turns on alert (sound and light when cat comes near)

def alert(piezo_p, led2) :
    print("Go away, kitty!")

    ##siren (piezo & led2)
    piezo_p.ChangeDutyCycle(90)
    GPIO.output(led2, True)
    piezo_p.ChangeFrequency(329)    
    time.sleep(0.5)

    GPIO.output(led2, False)
    piezo_p.ChangeFrequency(261)
    time.sleep(0.5)
    piezo_p.ChangeDutyCycle(0)
