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

def grades_extract():
    data = {}

    with open('grades.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        
        for row in reader:
            name = row[0]
            grade_474 = row[1]
            grade_354 = row[2]
        
            data[name] = {"GCS_143" : grade_474, "GCS_132" : grade_354}
    
    return data

def create_course_graph(course_list):
    # Create a graph
    graph = Graph()
    
    # Create new Namespace
    unid = Namespace("http://uni.com/data/")
    uni = Namespace("http://uni.com/schema#")

    # Bind Namespaces
    graph.bind("unid", unid)
    graph.bind("uni", uni)

    data_grades = grades_extract()

    for key, values in course_list.items():
        graph.add((unid[key], RDF.type, uni.Course))

        unid_val = values["Title"]
        graph.add((unid[key], uni.subject, unid[unid_val]))

        unid_val = values["Class Units"]
        graph.add((unid[key], uni.credits, unid[unid_val]))

        unid_val = values["Course number"]
        graph.add((unid[key], uni.ID, unid[unid_val]))

    for name, grades in data_grades.items():
        #initialize classes
        grade_474 = grades["GCS_143"]
        grade_354 = grades["GCS_132"]
        graph.add((unid[grade_474], RDF.type, uni.Grade))
        graph.add((unid[grade_354], RDF.type, uni.Grade))
        graph.add((unid[name], RDF.type, uni.Student))
        graph.add((unid[name], FOAF.firstName, uni.Student))

        #connection grade to course
        graph.add((unid[grade_474], uni.grade_obtained_in, unid["GCS_143"]))
        graph.add((unid[grade_354], uni.grade_obtained_in, unid["GCS_132"]))

        #connection course to grade
        graph.add((unid["GCS_143"], uni.grades, unid[grade_474]))
        graph.add((unid["GCS_132"], uni.grades, unid[grade_354]))

        #connection grade to name
        graph.add((unid[grade_474], uni.grade_from, unid[name]))
        graph.add((unid[grade_354], uni.grade_from, unid[name]))
        
        #connection name to grade
        graph.add((unid[name], uni.grade_obtained, unid[grade_474]))
        graph.add((unid[name], uni.grade_obtained, unid[grade_354]))

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