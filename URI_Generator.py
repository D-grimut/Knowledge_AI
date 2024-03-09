import os
import csv

from rdflib import URIRef, Namespace
from rdflib.term import _is_valid_uri
from urllib.parse import quote_plus

# Steps
# 1- Get course info from dataset TODO
# 2- Get content DONE
# 3- Give URIs DONE
# 4- Chanage csv for letter grades DONE
# 5- Manually create triples for grades TODO

def get_course_info():
    course_list = ["GCS_132", "GCS_143", "GCS_165"]

    data = {}

    with open("CATALOG.csv", mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            for key, value in row.items():
                if value in course_list:
                    data[row["Key"]] = {
                        "Course code": row["Course code"],
                        "Course number": row["Course number"],
                        "Title": row["Title"], 
                    }

    return data

def get_files(dir):
    file_list = []

    # Go through directory of current application and get file names
    for root, dirs, files in os.walk(dir):
        if("COMP" in root):
            for file in files:
                file_list.append(root + "\\" + file)

    return file_list

def create_URI(file_list):
    URI_list = []

    # Go through file list and create URI, then append it to a namespace
    # Converts name to valid URI after check
    for file in file_list:
        # Fix URI errors saying invalid URI
        file_nospace = file.replace(" ", "%20")
        file_front = file_nospace.replace("\\", "/")

        namespace = Namespace("file:///" + file_front)

        uri_ref = URIRef(namespace)

        URI_list.append(uri_ref)

    return URI_list


# Get current dir
curr_dir = os.getcwd()

# Get file names
files = get_files(curr_dir)

# Create and print URIs
URI_list = create_URI(files)

print(get_course_info())