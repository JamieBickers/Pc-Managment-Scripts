import os
from os.path import isfile
from datetime import datetime
import random
import shutil
import xml.etree.ElementTree as ET
import time

PATH_OF_DATABASE = "/" + os.path.join("home", "pi", "Desktop", "Gifs")

def all_files():
    all_files_and_dirs = os.listdir(PATH_OF_DATABASE)
    no_dirs = []
    for f in all_files_and_dirs:
        if isfile(os.path.join(PATH_OF_DATABASE, f)):
            no_dirs.append(f)
    return no_dirs

def move_file(file):
    shutil.move(os.path.join(PATH_OF_DATABASE, file), os.path.join(PATH_OF_DATABASE, "Handled", file))

def add_file_to_database(file_name):
    pc_tree = ET.parse(os.path.join(PATH_OF_DATABASE, "Database", "FileData.xml"))
    pc_root = pc_tree.getroot()
    pi_tree = ET.parse(os.path.join(PATH_OF_DATABASE, "Database", "PiFileData.xml"))
    pi_root = pi_tree.getroot()

    for child in pc_root:
        if child.attrib["name"] == file_name:
            pi_root.append(child)
            pi_tree.write(os.path.join(PATH_OF_DATABASE, "Database", "PiFileData.xml"), xml_declaration=True)
            return
    raise ValueError("File is not in database.")

def handle_all_files():
    files = all_files()
    for file in files:
        add_file_to_database(file)
        move_file(file)
            
def main():
    for i in range(0, 360):
        try:
            handle_all_files()
            time.sleep(10)
        except:
            time.sleep(10)
        
