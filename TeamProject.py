import RPi.GPIO as GPIO
import time
import smbus
import threading
import telegram   ##telegram api install --> python -m pip install --user  python-telegram-bot    
from flask import Flask, render_template, Response, request, redirect, url_for


from alert import alert
from message import send_message
from distance import distance

from subprocess import call
import numpy as np
import cv2

app = Flask(__name__)

# FLASK WEBPAGE
@app.route('/')
def main():
        while True:
            global is_stove_on
            global flag
            
            stove = is_stove_on
            tempValue = str(temp)[0:5]
            goaway = count

            if float(tempValue) < 30:
                stateString = "Temperature is not that high. It is fine!"
            else:
                stateString = "Temperature is Too high :( Please Turn it off"


            templateData = {
                'title':'Kitty Alarm',
                'stove' : stove, 
                'temp_value':tempValue,
                'state':stateString, 
                'goaway' : goaway,  ##alert count
            }
            
            return render_template('main.html',**templateData)  

# ROUTE FOR TURNING OF STOVE
@app.route('/StoveOff/', methods=['POST'])
def switch_off():
    global is_stove_on
    global flag
    # turn off the stove 
    #change value of TURN ON/OFF FLAG in jog
    print('the stove is off')
    is_stove_on=False
    GPIO.output(14,False)
    flag = 0
	
    video_thread = threading.Thread(target=recordVideo)
    video_thread.start()
	
    send_message(bot, chat_id,"stove is off")
    time.sleep(3)
    return redirect(url_for('main'))

# ROUTE FOR VIDEO
@app.route('/video/')
def video():
    return render_template('video.html')


# CAMERA WEBPAGE
def recordVideo():
    ## The duration in seconds of the video captured
        capture_duration = 15

        cap = cv2.VideoCapture(0)

        # set format and path for video
        fourcc = cv2.cv.CV_FOURCC(*'XVID')

        videoname = '/home/tea/Documents/practice_paola/kitty/webapp_dir/static/output2.avi'
        videoname2 = '/home/tea/Documents/practice_paola/kitty/webapp_dir/static/output2.mp4'
        out = cv2.VideoWriter(videoname,fourcc, 20.0, (640,480))

		# recording 
        start_time = time.time()
        while( int(time.time() - start_time) < capture_duration ):
            ret, frame = cap.read()
            if ret==True:
                frame = cv2.flip(frame,0)
                out.write(frame)
                cv2.imshow('frame',frame)

            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
		
		# changing video format
        command = "ffmpeg -i %s %s" % (videoname, videoname2)

def temperature():
    global temp
    bus.write_byte(addr,temp_reset)
    time.sleep(0.05)

    try : 
        while True : 
            if flag==1:
                bus.write_byte(addr,cmd_temp)
                time.sleep(0.26)

                for i in range(0,2,1):
                    data[i] = bus.read_byte(addr)
                val = data[0] << 8 | data[1]
                temp = -46.85+175.72/65536*val

                print("temperature:%.2f" %temp) 
                time.sleep(3)

    except IOError: 
        print("IOERROR")


def jog_on_off():
    global flag 
    global is_stove_on

	# stove starts off 
    flag=0
    curr_stat = 0
    stat = 0

    is_temp_thread_start=0   ##temp_thread flag --> to start temp_thread only once

	# turning stove on and off with jog center button 
    while True:
        curr_stat = GPIO.input(button)
        time.sleep(0.2)
        if curr_stat != stat:
            stat = curr_stat

        #for center led blinks
        if stat == 1:
            if flag == 0:
                print('the stove is on')
                is_stove_on=True

                GPIO.output(led1,True)
                flag = 1
                send_message(bot, chat_id,"stove is on")

                if (not is_temp_thread_start):
                    temp_thread.start()
                    is_temp_thread_start=1                

 

            else:
                print('the stove is off')
                is_stove_on=False
                GPIO.output(led1,False)
                flag = 0
                send_message(bot, chat_id,"stove is off")


def get_distance():
    global count
    while True:
        dist = abs(distance(GPIO_TRIGGER, GPIO_ECHO))

        if 0<dist<10:  ##if distance <30 --> alert
            alert(piezo_p, led2)
            count += 1

        if dist>10:
            piezo_p.ChangeDutyCycle(0)  ##if distance >30 --> alert off (volume 0)

        time.sleep(1.2)




if __name__ == '__main__' : 


    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    led1=14  ##stove
    led2=15  ##alert light
    piezo=13  ##alert sound

    button = 21  ##stove button
    flag = 0

    ##distance measurement
    GPIO_TRIGGER = 0
    GPIO_ECHO = 1

    ##GPIO setup
    GPIO.setup(led1, GPIO.OUT)
    GPIO.setup(led2, GPIO.OUT)
    GPIO.setup(piezo, GPIO.OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(button,GPIO.IN)

 

    piezo_p = GPIO.PWM(piezo, 100)  ##piezo_p == piezo pwm
    piezo_p.start(0)


    ##temperature measurement & flask web setup
    bus = smbus.SMBus(1)    
    addr = 0x40
    cmd_temp = 0xf3
    temp_reset = 0xfe
    soft_reset = 0xfe
    temp=0.0
    val=0
    data = [0,0]

    

    ##telegram api setup
    my_token = "1037431043:AAHGXv5PyCB1wIU93lcDRmmVs5-5lntY02o"
    bot = telegram.Bot(token=my_token)
    updates = bot.getUpdates()
    chat_id = 1054104702

    ##global init
    is_stove_on = False
    temp = 0.0
    count = 0


    #distance thread
    dist_thread = threading.Thread(target=get_distance)
    dist_thread.start()


    ##JOG thread
    jog_thread = threading.Thread(target=jog_on_off)
    jog_thread.start()


    ##temp thread
    temp_thread = threading.Thread(target=temperature)


    ##web
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=False)

