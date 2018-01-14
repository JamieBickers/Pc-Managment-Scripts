import imaplib
import email
import time
from datetime import datetime
from dateutil.parser import parse
import RPi.GPIO as GPIO
import time

def start_pc():
    print("starting...")
    GPIO.output(18, GPIO.LOW)
    time.sleep(1)
    GPIO.output(18, GPIO.HIGH)
    
def time_of_last_startup_email():
    server= imaplib.IMAP4_SSL("imap.gmail.com")
    server.login("jamiebickerspcmanager@googlemail.com", "yM05YkJWGirq")
    server.select()
    response, emails = server.search(None, "(SUBJECT 'startup')")
    first = emails[0].split()[-1]
    response, data = server.fetch(first, "(RFC822)")
    decoded = data[0][1].decode("utf-8")
    message = email.message_from_string(decoded)
    date = message["Date"].replace(",", " ").replace(":", " ")[:-6] # put it into the format that can be read below
    date_object = datetime.strptime(date, "%a %d %b %Y %H %M %S")
    return date_object

def read_last_startup_time_from_file():
    with open("/home/pi/Desktop/StartupHandledTimes.txt") as file:
        date = file.read()
        return parse(date)
        
def write_last_startup_time_to_file(date):
    with open("/home/pi/Desktop/StartupHandledTimes.txt", "w") as file:
        file.write(str(date))

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, GPIO.HIGH)
    try:
        handled_times = [read_last_startup_time_from_file()]
    except:
        handled_times = []
    for i in range(0, 360):
        try:
            time_of_email = time_of_last_startup_email()
            difference = datetime.now()-time_of_email
            if difference.total_seconds() < 180:
                if time_of_email not in handled_times:
                    start_pc()
                    handled_times = [time_of_email]
                    write_last_startup_time_to_file(time_of_email)
        except:
            pass
        
        time.sleep(10)

main()