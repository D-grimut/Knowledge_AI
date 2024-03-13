import os
import csv

from rdflib import URIRef, Namespace, Graph, Literal
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
    file_list = {}

    # Go through directory of current application and get file names
    for root, dirs, files in os.walk(dir):

        if("COMP" in root):
            lecture_number = 0 #simple counter for lecture number TODO: change to dinmaic through MLP extraction or other means in part 2
            lecture = "Lecture_"
            class_name = os.path.basename(root) #assuming dir name = cource name
            file_list[class_name] = {}

            for file in files:
                file_preped = root + "\\" + file
                file_uri = create_URI(file_preped)
                
                file_list[class_name][lecture + str(lecture_number)] = file_uri
                lecture_number += 1

    return file_list

def create_URI(file):

    # Go through file list and create URI, then append it to a namespace
    # Converts name to valid URI after check

    # Fix URI errors saying invalid URI
    file_nospace = file.replace(" ", "%20")
    file_front = file_nospace.replace("\\", "/")

    namespace = Namespace("file:///" + file_front)

    uri_ref = URIRef(namespace)

    return uri_ref

def grades_extract():
    data = {}

    with open('grades.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        
        for row in reader:
            id = row[0]
            fname = row[1]
            lname = row[2]
            email = row[3]
            grade_474 = row[4]
            grade_354 = row[5]
        
            data[id] = {
                "fname" : fname,
                "lname" : lname,
                "email" : email,
                "grade_GCS_143" : grade_474, 
                "grade_GCS_132" : grade_354
                }
    
    return data

#method to manualy create (temprary) lectures - this will be removed in part 2 when we know how to create them dinamicaly using NLP
def dummy_lectures(graph, unid, uni, dbo, material_URIs):
    
    #TODO: finish this method
    graph.add((unid.Concordia, RDF.type, dbo.University))
    graph.add((unid.Concordia, uni.name, Literal("Concordia")))


# TODO: Add Dummy Lectures, Dummy topics, Dummy course material (including outlines for each course)
def create_course_graph(course_list):
    # Create a graph
    graph = Graph()
    
    # Create new Namespace
    unid = Namespace("http://uni.com/data/")
    uni = Namespace("http://uni.com/schema#")
    dbo = Namespace("http://dbpedia.org/ontology/")

    # Bind Namespaces
    graph.bind("unid", unid)
    graph.bind("uni", uni)
    graph.bind("dbo", dbo)

    data_grades = grades_extract()
    uni_dummy = URIRef("https://dbpedia.org/data/Concordia_University")

    #Creating Dummy University - Concordia
    graph.add((unid.Concordia, RDF.type, dbo.University))
    graph.add((unid.Concordia, uni.uni_dblink, uni_dummy))
    graph.add((unid.Concordia, uni.name, Literal("Concordia")))

    # Adding Courses to the graph - Concordia ONLY
    for key, values in course_list.items():
        graph.add((unid[key], RDF.type, uni.Course))

        unid_val = values["Title"]
        graph.add((unid[key], uni.subject, unid[unid_val]))

        unid_val = values["Class Units"]
        graph.add((unid[key], uni.credits, unid[unid_val]))

        unid_val = values["Course number"]
        graph.add((unid[key], uni.ID, unid[unid_val]))

        graph.add((unid[key], uni.offered_in, unid.Concordia))
        graph.add((unid.Concordia, uni.offers, unid[key]))

    # Adding students and gardes to the RDF graph
    for id, student_data in data_grades.items():
        
        fname = student_data['fname']
        lname = student_data['lname']
        email = student_data['email']

        #initialize classes
        grade_474 = student_data["grade_GCS_143"] + "_" + id
        grade_354 = student_data["grade_GCS_132"] + "_" + id

        #making garde entities
        graph.add((unid[grade_474], RDF.type, uni.Grade))
        graph.add((unid[grade_474], uni.grade_value, Literal(student_data["grade_GCS_143"])))
        graph.add((unid[grade_354], RDF.type, uni.Grade))
        graph.add((unid[grade_354], uni.grade_value, Literal(student_data["grade_GCS_132"])))

        #making student entities
        graph.add((unid[fname], RDF.type, uni.Student))
        graph.add((unid[fname], FOAF.firstName, Literal(fname)))
        graph.add((unid[fname], FOAF.lastName, Literal(lname)))
        graph.add((unid[fname], FOAF.mbox, Literal(email)))
        graph.add((unid[fname], uni.student_ID, Literal(id)))

        #connection grade to course
        graph.add((unid[grade_474], uni.grade_obtained_in, unid["GCS_143"]))
        graph.add((unid[grade_354], uni.grade_obtained_in, unid["GCS_132"]))

        #connection course to grade
        graph.add((unid["GCS_143"], uni.grades, unid[grade_474]))
        graph.add((unid["GCS_132"], uni.grades, unid[grade_354]))

        #connection grade to name
        graph.add((unid[grade_474], uni.grade_from, unid[fname]))
        graph.add((unid[grade_354], uni.grade_from, unid[fname]))
        
        #connection name to grade
        graph.add((unid[fname], uni.grade_obtained, unid[grade_474]))
        graph.add((unid[fname], uni.grade_obtained, unid[grade_354]))

    # Serialize graph
    graph.serialize(destination="dummy_data.ttl", format='turtle')

# Get current dir
curr_dir = os.getcwd()

# Get file names
URI_list = get_files(curr_dir)
for lect, val in URI_list.items():
    print(lect, "------------", val)
# Graph creation
create_course_graph(get_course_info())