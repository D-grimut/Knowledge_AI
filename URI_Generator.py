import os

from rdflib import URIRef, Namespace
from rdflib.term import _is_valid_uri
from urllib.parse import quote_plus

class InvalidURIRef(Exception):
    pass

def get_files(dir):
    file_list = []

    # Go through directory of current application and get file names
    for root, dirs, files in os.walk(dir):
        if("COMP" in root):
            for file in files:
                file_list.append(file)

    return file_list

def create_URI(file_list):
    URI_list = []
    namespace = Namespace("file://home/roboprof/")

    # Go through file list and create URI, then append it to a namespace
    # Converts name to valid URI after check
    for file in file_list:
        uri_ref = URIRef(file)
        name_uri_ref = namespace + uri_ref
        if(_is_valid_uri(name_uri_ref)):
            URI_list.append(name_uri_ref)
        else:
            valid_uri = quote_plus(name_uri_ref)
            URI_list.append(valid_uri)

    return URI_list


# Get current dir
curr_dir = os.getcwd()

# Get file names
files = get_files(curr_dir)

# Create and print URIs
URI_list = create_URI(files)

for uri in URI_list:
    print(uri + "\nIs this a valid URI: " + str(_is_valid_uri(uri)))