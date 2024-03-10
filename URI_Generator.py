import os
import csv

from rdflib import URIRef, Namespace, Graph
from rdflib.namespace import FOAF, RDF
from rdflib.term import _is_valid_uri
from urllib.parse import quote_plus

def get_course_info():
    course_list = ["GCS_132", "GCS_143", "GCS_165"]
    course_list_cred = ["005411", "005484", "040355"]

    data = {}
    index = {}

    for i, course in enumerate(course_list):
        index[course_list_cred[i]] = course   

    with open("CATALOG.csv", mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:

            for key, value in row.items():

                if value in course_list:
                    if(row["Title"]):
                        new_val = row["Title"].replace(" ", "_")
                        
                    data[row["Key"]] = {
                        "Course code": row["Course code"],
                        "Course number": row["Course number"],
                        "Title": new_val, 
                    }

    with open("CU_SR_OPEN_DATA_CATALOG.csv", mode='r', encoding="utf-16") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            
            for key, value in row.items():
                if value in course_list_cred:
                    course_id = index[value]
                    data[course_id]["Class Units"] = row["Class Units"]
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

def create_course_graph(course_list):
    # Create a graph
    graph = Graph()
    
    # Create new Namespace
    unid = Namespace("http://uni.com/data/")
    uni = Namespace("http://uni.com/schema#")

    # Bind Namespaces
    graph.bind("unid", unid)
    graph.bind("uni", uni)

    for key, values in course_list.items():
        graph.add((unid[key], RDF.type, uni.Course))

        unid_val = values["Title"]
        graph.add((unid[key], uni.subject, unid[unid_val]))

        unid_val = values["Class Units"]
        graph.add((unid[key], uni.credits, unid[unid_val]))

        unid_val = values["Course number"]
        graph.add((unid[key], uni.ID, unid[unid_val]))

    # Serialize graph
    graph.serialize(destination="dummy_data.ttl", format='turtle')

# Get current dir
curr_dir = os.getcwd()

# Get file names
files = get_files(curr_dir)

# Create and print URIs
URI_list = create_URI(files)

# Graph creation
create_course_graph(get_course_info())