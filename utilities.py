import os
from os.path import isfile
import json
import requests

def read_password_from_file():
    """Read the password needed for server authentication from file."""
    with open("Password.txt") as file:
        password = file.read().strip()
    return password

def standard_post_server_call(route_extension, password, body):
    """Standard server call, returns empty string if response is empty."""
    url = "https://jamie-bickers-personal-website.herokuapp.com/api/private/" + route_extension
    body["password"] = password
    header = {'content-type': 'application/json'}
    request = requests.post(url, data=json.dumps(body), headers=header)
    return json.loads(request.content.decode("utf-8")) if request.content else ""

def all_files(path):
    """Returns all files in the path and no directories."""
    all_files_and_dirs = os.listdir(path)
    no_dirs = []
    for file in all_files_and_dirs:
        if isfile(os.path.join(path, file)):
            no_dirs.append(file)
    return no_dirs