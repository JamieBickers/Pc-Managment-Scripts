import os
from os.path import isfile
from datetime import datetime
import random
import shutil
import xml.etree.ElementTree as ET
import time
import subprocess
from multiprocessing import Process
import requests
import json

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

def get_last_action(password):
    url = "https://jamie-bickers-personal-website.herokuapp.com/api/private/getPcState"
    data = {"Password": password, "Actions": ["shutdown", "sleep", "hibernate"]}
    header = {'content-type': 'application/json'}
    request = requests.post(url, data=json.dumps(data), headers=header)
    return json.loads(request.content) if request.content else ""
    
def carry_out_action(action):
    if action == "shutdown":
        os.system("shutdown -s")
    elif action == "sleep" or action == "hibernate":
        os.system("shutdown.exe /h")
        
def read_password_from_file():
    with open("Password.txt") as file:
        password = file.read()
    return password
    
def listen_for_actions():
    password = read_password_from_file()
    for _ in range(0, 60):
        try:
            last_action = get_last_action(password)
            carry_out_action(last_action)
        except:
            pass

        time.sleep(60)

if __name__ == "__main__":
    action_listener = Process(target=listen_for_actions)
    action_listener.start()
    file_listener = Process(target=listen_for_new_files)
    file_listener.start()
    action_listener.join()
    file_listener.join()