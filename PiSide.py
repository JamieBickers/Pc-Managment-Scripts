import os
import shutil
import xml.etree.ElementTree as ET
import time
import smtplib
from mimetypes import guess_type
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from multiprocessing import Process
import utilities
import RPi.GPIO as GPIO

PATH_OF_DATABASE = "/" + os.path.join("home", "pi", "Desktop", "Gifs")
SERVER_PASSWORD = utilities.read_password_from_file()

def server_call(route_extension, body={}):
    """Wrapper for the server call with pre read password."""
    return utilities.standard_post_server_call(route_extension, SERVER_PASSWORD, body)

def all_new_files():
    """Returns all files that have not been handled."""
    return utilities.all_files(PATH_OF_DATABASE)

def move_file(file):
    """Moves a file to the 'Handled' folder."""
    file_path = os.path.join(PATH_OF_DATABASE, file)
    new_file_path = os.path.join(PATH_OF_DATABASE, "Handled", file)
    shutil.move(file_path, new_file_path)

def add_file_to_database(file_name):
    """Add file to the pi database."""
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
    """Move all files and add them to the database."""
    #try:
    files = all_new_files()
    for file in files:
        add_file_to_database(file)
        move_file(file)
    #except:
        #pass

#=================================================================================

def start_pc():
    """Start the pc by activating a relay."""
    print("starting...")
    GPIO.output(18, GPIO.LOW)
    time.sleep(1)
    GPIO.output(18, GPIO.HIGH)

def carry_out_action(action):
    """Start the pc if requested by server."""
    if action == "startup":
        start_pc()

def listen_for_actions():
    """Repeatedly listens for new actions on the server and acts on them."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, GPIO.HIGH)
    for _ in range(0, 360):
        #try:
        last_action = server_call("getPcState", {"Actions": ["startup"]})
        carry_out_action(last_action)
        #except:
            #pass

        time.sleep(10)

#=======================================================================================

def file_with_max_score(scores):
    """Return the file with the most matching tags, or the empty string if no files match."""
    best_score = max(scores.values())
    if best_score == 0:
        return ""
    for file in scores.keys():
        if scores[file] == best_score:
            return file

def search_for_matching_gif(tags):
    """Search the database for a file matching the tags."""
    tree = ET.parse("/" + os.path.join(PATH_OF_DATABASE, "Database", "FileData.xml"))
    root = tree.getroot()
    scores = {}
    for entry in root:
        scores[entry.attrib["name"]] = 0
        for child in entry:
            if child.text in tags:
                scores[entry.attrib["name"]] += 1
    return file_with_max_score(scores)

def construct_email_message(tags):
    """Build an email message containing a file matching the tags, or the database."""
    file_name = search_for_matching_gif(tags)
    if not file_name:
        file_to_attach = "" + os.path.join(PATH_OF_DATABASE, "Database", "FileData.xml")
        subject = "No Match Found"
    else:
        file_to_attach = "/" + os.path.join(PATH_OF_DATABASE, "Handled", file_name)
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
        file_name_without_path = os.path.basename(file_name)
        attachment.add_header('Content-Disposition', 'attachment', file_name=file_name_without_path)
        message.attach(attachment)

    return message

def search_for_gif_and_send(tags):
    """Search for a matching file and send it."""
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

def send_files_on_request():
    """Repeatedly check for file requests and execute them."""
    for _ in range(0, 360):
        #try:
        all_file_requests = server_call("getGifs")
        if all_file_requests:
            for tags in all_file_requests:
                search_for_gif_and_send(tags)
        #except:
            #pass
        time.sleep(10)

#=========================================================================================

def run_loops_in_parallel():
    """Run the three main loops in parallel."""
    if __name__ == "__main__":
        action_listener = Process(target=listen_for_actions)
        action_listener.start()
        file_listener = Process(target=handle_all_files)
        file_request_listener = Process(target=send_files_on_request)
        file_listener.start()
        file_request_listener.start()
        action_listener.join()
        file_listener.join()
        file_request_listener.join()

run_loops_in_parallel()
