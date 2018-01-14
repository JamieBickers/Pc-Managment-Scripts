import os
from os.path import isfile
from datetime import datetime
import random
import shutil
import xml.etree.ElementTree as ET
import time

def all_files():
    all_files_and_dirs = os.listdir("C:\\Users\\Jamie\\Desktop\\Gifs")
    no_dirs = []
    for f in all_files_and_dirs:
        if isfile("C:\\Users\\Jamie\\Desktop\\Gifs\\" + f):
            no_dirs.append(f)
    return no_dirs

def move_and_rename_file(file, new_name):
    shutil.move("C:\\Users\\Jamie\\Desktop\\Gifs\\" + file, "C:\\Users\\Jamie\\Desktop\\Gifs\\Handled\\" + new_name)

def get_new_file_name():
    with open("C:\\Users\\Jamie\\Desktop\\Gifs\\Database\\Seed.txt", "r") as seed_file:
        text_seed = seed_file.read()
        seed = int(text_seed)
    with open("C:\\Users\\Jamie\\Desktop\\Gifs\\Database\\Seed.txt", "w") as seed_file:
        seed_file.write(str(seed + 1))
    random.seed(seed)
    return str(random.randrange(0, 10000000000))
            
def add_file_data_to_database(file_type, file_new_name):
    tree = ET.parse("C:\\Users\\Jamie\\Desktop\\Gifs\\Database\\FileData.xml")
    root = tree.getroot()
    new_element = ET.Element("file", {'date': str(datetime.now()), 'name': file_new_name, 'type': file_type})
    root.append(new_element)
    tree.write("C:\\Users\\Jamie\\Desktop\\Gifs\\Database\\FileData.xml", xml_declaration=True)
    
def handle_all_files():
    files = all_files()
    for file in files:
        new_name = get_new_file_name()
        original_name, extension = os.path.splitext(file)
        add_file_data_to_database(original_name, new_name + extension)
        move_and_rename_file(file, new_name + extension)
            
def main():
    for i in range(0, 360):
        try:
			handle_all_files()
			time.sleep(10)
        except:
            time.sleep(10)
        
main()