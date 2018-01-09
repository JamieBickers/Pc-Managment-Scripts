import imaplib
import email
import time
from datetime import datetime
import RPi.GPIO as GPIO
import time

def startPc():
    print("starting...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(18, GPIO.LOW)
    
for i in range(0, 1):
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
    difference = datetime.now()-date_object
    if difference.total_seconds() < 180:
        startPc()
    time.sleep(1)