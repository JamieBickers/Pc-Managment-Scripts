import imaplib
import email
import time
from datetime import datetime
from dateutil.parser import parse
import smtplib
from email.mime.multipart import MIMEMultipart
import os
from mimetypes import guess_type
from email.mime.base import MIMEBase
from email.encoders import encode_base64
import xml.etree.ElementTree as ET
   
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
    #with open("/home/pi/Desktop/GifsHandledTimes.txt") as file:
    with open("/" + os.path.join("Users", "Jamie", "Desktop", "TestTimes.txt")) as file:
        date = file.read()
        return parse(date)
        
def write_last_startup_time_to_file(date):
    #with open("/home/pi/Desktop/GifsHandledTimes.txt", "w") as file:
    with open("/" + os.path.join("Users", "Jamie", "Desktop", "TestTimes.txt"), "w") as file:
        file.write(str(date))
    
# return "" if no match is found
def file_with_max_score(scores):
    best_score = max(scores.values())
    if best_score == 0:
        return ""
    for file in scores.keys():
        if scores[file] == best_score:
            return file

def search_for_matching_gif(tags):
    tree = ET.parse("/" + os.path.join("Users", "Jamie", "Desktop", "Gifs", "Database", "FileData.xml"))
    root = tree.getroot()
    scores = {}
    for entry in root:
        scores[entry.attrib["name"]] = 0
        for child in entry:
            if child.text in tags:
                scores[entry.attrib["name"]] += 1
    return file_with_max_score(scores)

def construct_email_message(tags):      
    file_name = search_for_matching_gif(tags)
    if (file_name == ""):
        file_to_attach = "" + os.path.join("Users", "Jamie", "Desktop", "Gifs", "Database", "FileData.xml")
        subject = "No Match Found"
    else:
        file_to_attach = "/" + os.path.join("Users", "Jamie", "Desktop", "Gifs", "Handled", file_name)
        subject = 'Requested Gif'
        
    message = MIMEMultipart()
    message["Subject"] = subject
    message['From'] = "jamiebickerspcmanager@googlemail.com"
    message['To'] = 'bickersjamie@googlemail.com'
        
    mimetype, encoding = guess_type(file_to_attach)
    mimetype = mimetype.split('/', 1)
    with open(file_to_attach, 'rb') as file_t:
        attachment = MIMEBase(mimetype[0], mimetype[1])
        attachment.set_payload(file_t.read())
        file_t.close()
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', file_name=os.path.basename(file_name))
        message.attach(attachment)
        
    return message

def search_for_gif_and_send(tags):
    gmail_sender = "jamiebickerspcmanager@googlemail.com"
    gmail_password = 'yM05YkJWGirq'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_password)
    message = construct_email_message(tags)
    
    #try:
    server.send_message(message)
    #except:
        #pass
    
    server.quit()

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

main()

class EmailData:
    def __init__(self, time, tags):
        self.time = time
        self.tags = tags.split(" ")