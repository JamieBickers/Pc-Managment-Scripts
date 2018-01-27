import os
from os.path import isfile
from datetime import datetime
import random
import shutil
import xml.etree.ElementTree as ET
import time
import subprocess
import imaplib
import email
from dateutil.parser import parse
from multiprocessing import Process
import requests
import json

path_of_last_handled_time = "/" + os.path.join("Users", "Jamie", "Desktop", "PcManagmentScripts", "LastHandledTime.txt")
path_of_gifs_folder = "/" + os.path.join("Users", "Jamie", "Desktop", "Gifs")

def all_files():
    all_files_and_dirs = os.listdir(path_of_gifs_folder)
    no_dirs = []
    for f in all_files_and_dirs:
        if isfile(os.path.join(path_of_gifs_folder, f)):
            no_dirs.append(f)
    return no_dirs

def move_and_rename_file(file, new_name):
    shutil.move(os.path.join(path_of_gifs_folder, file), os.path.join(path_of_gifs_folder, "Handled", new_name))

def get_new_file_name():
    path_of_seed = os.path.join(path_of_gifs_folder, "Database", "Seed.txt")
    with open(path_of_seed, "r") as seed_file:
        text_seed = seed_file.read()
        seed = int(text_seed)
    with open(path_of_seed, "w") as seed_file:
        seed_file.write(str(seed + 1))
    random.seed(seed)
    return str(random.randrange(0, 10000000000))
    
def add_file_data_to_database(file_name, file_new_name):
    path_of_database = os.path.join(path_of_gifs_folder, "Database", "FileData.xml")
    tree = ET.parse(path_of_database)
    root = tree.getroot()
    new_element = ET.Element("file", {"date": str(datetime.now()), "name": file_new_name})
    tags = os.path.splitext(file_name)[0].split()
    for tag in tags:
        tag_element = ET.Element("tag")
        tag_element.text = tag
        new_element.append(tag_element)     
    root.append(new_element)
    tree.write(path_of_database, xml_declaration=True)
    
def handle_all_files(files):
    for file in files:
        new_name = get_new_file_name()
        original_name, extension = os.path.splitext(file)
        add_file_data_to_database(original_name, new_name + extension)
        move_and_rename_file(file, new_name + extension)
        
def move_to_pi_and_delete():
    subprocess.Popen(["powershell.exe", ".\MoveFilesToPiAndDelete.ps1"])
            
def listen_for_new_files():
    for _ in range(0, 360):
        files = all_files()
        try:
            handle_all_files(files)
            time.sleep(10)
        except:
            time.sleep(10)
          
    if len(os.listdir(os.path.join(path_of_gifs_folder, "Handled"))) > 5:
        move_to_pi_and_delete()
    
def get_last_email():
    server= imaplib.IMAP4_SSL("imap.gmail.com")
    server.login("jamiebickerspcmanager@googlemail.com", "yM05YkJWGirq")
    server.select()
    response, emails = server.search(None, "ALL")
    first = emails[0].split()[-1]
    response, data = server.fetch(first, "(RFC822)")
    decoded = data[0][1].decode("utf-8")
    message = email.message_from_string(decoded)
    unformatted_date = message["Date"].replace(",", " ").replace(":", " ")[:-6] # put it into the format that can be read below
    date = datetime.strptime(unformatted_date, "%a %d %b %Y %H %M %S")
    subject = message["Subject"]
    return EmailData(date, subject)

def read_last_email_time_from_file():
    try:
        with open(path_of_last_handled_time) as file:
            date = file.read()
            return parse(date)
    except:
        return None
        
def write_last_email_time_to_file(date):
    with open(path_of_last_handled_time, "w") as file:
        file.write(str(date))
        
def act_on_email(parameters):
    if len(parameters) == 1:
        parameter = parameters[0].lower()
        if parameter == "shutdown":
            os.system("shutdown -s")
        elif parameter == "sleep" or parameter == "hibernate":
            os.system("shutdown.exe /h")

def get_last_action():
    url = "https://jamie-bickers-personal-website.herokuapp.com/api/private/getPcState"
    data = {"AuthorizationDetails": {"Username": "bickersjamie@googlemail.com", "Password": "5KofF3!W^1NQ"},
            "Actions": ["shutdown", "sleep", "hibernate"]}
    header = {'content-type': 'application/json'}
    request = requests.post(url, data=json.dumps(data), headers=header)
    print(request.content)
    
# helper for debugging only
def send_action():
    url = "https://jamie-bickers-personal-website.herokuapp.com/api/private/pcState"
    data = {"AuthorizationDetails": {"Username": "bickersjamie@googlemail.com", "Password": "PASSWORD"},
            "Action": "shutdown"}
    header = {'content-type': 'application/json'}
    request = requests.post(url, data=json.dumps(data), headers=header)
    print(request)

def carry_out_action(action):
    if action == "shutdown":
        os.system("shutdown -s")
    elif action == "sleep" or action == "hibernate":
        os.system("shutdown.exe /h")
    
def listen_for_actions():
    for _ in range(0, 60):
        try:
            last_action = get_last_action()
            carry_out_action(last_action)
        except:
            pass

        time.sleep(60)

def listen_for_emails():
    last_handled_time = read_last_email_time_from_file()
    for _ in range(0, 60):
        try:
            last_email = get_last_email()
            time_difference = datetime.now()-last_email.time
            if time_difference.total_seconds() < 180 and last_email.time != last_handled_time:
                last_handled_time = last_email.time
                write_last_email_time_to_file(last_email.time)
                act_on_email(last_email.parameters)
        except:
            pass
        
        time.sleep(60)
        
class EmailData:
    def __init__(self, time, subject):
        self.time = time
        self.parameters = subject.split(" ")

if __name__ == "__main__":
    email_listener = Process(target=listen_for_emails)
    email_listener.start()
    file_listener = Process(target=listen_for_new_files)
    file_listener.start()
    email_listener.join()
    file_listener.join()