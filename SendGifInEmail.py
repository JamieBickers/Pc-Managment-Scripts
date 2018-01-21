import imaplib
import email
import time
from datetime import datetime
from dateutil.parser import parse
from smtplib import SMTP
import smtplib
   
def last_email():
    server= imaplib.IMAP4_SSL("imap.gmail.com")
    server.login("jamiebickerspcmanager@googlemail.com", "yM05YkJWGirq")
    server.select()
    response, emails = server.search(None, "ALL")
    first = emails[0].split()[-1]
    response, data = server.fetch(first, "(RFC822)")
    decoded = data[0][1].decode("utf-8")
    message = email.message_from_string(decoded)
    date = message["Date"].replace(",", " ").replace(":", " ")[:-6] # put it into the format that can be read below
    date_object = datetime.strptime(date, "%a %d %b %Y %H %M %S")
    subject = message["Subject"]
    return EmailData(date_object, subject)

def read_last_startup_time_from_file():
    with open("/home/pi/Desktop/GifsHandledTimes.txt") as file:
        date = file.read()
        return parse(date)
        
def write_last_startup_time_to_file(date):
    with open("/home/pi/Desktop/GifsHandledTimes.txt", "w") as file:
        file.write(str(date))
        
#stub
def search_for_matching_gif(tags):
    return "9460750496.jpg"

def test_email():
    TO = 'bickersjamie@googlemail.com'
    SUBJECT = 'TEST MAIL'
    TEXT = 'Here is a message from python.'
    
    # Gmail Sign In
    gmail_sender = "jamiebickerspcmanager@googlemail.com"
    gmail_passwd = 'yM05YkJWGirq'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)
    
    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])
    
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print ('email sent')
    except:
        print ('error sending mail')
    
    server.quit()
        
def search_for_gif_and_send(tags):
    file_name = search_for_matching_gif(tags)
    TO = ["jamie@jamiebickers.com"]
    FROM = "jamiebickerspcmanager@googlemail.com"
#    email_text = """\  
#    From: %s  
#    To: %s  
#    Subject: %s
#    
#    %s
#    """ % (FROM, TO, "hello", "world")

    message = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (FROM, ", ".join(TO), "hello", file_name)
    
    print(message)
    server = SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(FROM, "yM05YkJWGirq")
    server.sendmail(FROM, TO, message)

def main():
    try:
        handled_times = [read_last_startup_time_from_file()]
    except:
        handled_times = []
    for i in range(0, 360):
        try:
            email = last_email()
            time_since_email = datetime.now()-email.time
            if time_since_email.total_seconds() < 180:
                if email.time not in handled_times:
                    handled_times = [email.time]
                    write_last_startup_time_to_file(email.time)
                    search_for_gif_and_send(email.tags)
        except:
            pass
        
        time.sleep(10)

#main()
#search_for_gif_and_send(["a", "b", "c"])
test_email()

class EmailData:
    def __init__(self, time, tags):
        self.time = time
        self.tags = tags.split(" ")