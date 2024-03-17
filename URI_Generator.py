import os
import csv
import pandas as pd
from rdflib import XSD, URIRef, Namespace, Graph, Literal
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

            path_name = root[root.find('COMP'):]
            file_list[path_name] = {}

            for file in files:
                file_preped = root + "\\" + file
                file_uri = create_URI(file_preped)
                
                file_list[path_name][lecture + str(lecture_number)] = file_uri
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

#Since the data extraction process for grades and student info is the same, we use only one function
def student_info_extract(file):
    data = {}

    student_info = pd.read_csv(file)
    
    for index, row in student_info.iterrows():

        curr_student = -1

        for column_name, value in row.items():

            if(column_name == "ID"):
                curr_student = value
                data[curr_student] = {}
            else:
                data[curr_student][column_name] = value

    return data

#method to manualy create (temprary) lectures - this will be removed in part 2 when we know how to create them dinamicaly using NLP
def dummy_lectures(graph, unid, uni, dbo, material_URIs):
    
    #TODO: finish this method
    graph.add((unid.Concordia, RDF.type, dbo.University))
    graph.add((unid.Concordia, uni.name, Literal("Concordia")))


# TODO: Dummy topics
def create_course_graph(course_list, get_files):
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

    
    data_grades = student_info_extract("grades.csv")
    data_students = student_info_extract("students.csv")

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

        graph.add((unid.Concordia, uni.offers, unid[key]))

    # Adding course lectures 
    for course, course_content in get_files.items():
        if "Lectures" in course:
            for lec_num, lec_cont_uri in course_content.items():
                
                # Change lec_name
                lec_name = lec_cont_uri[lec_cont_uri.find("Lectures/")+9:-4]
                lec_uri = course[ :course.find("/")].replace(' ', '%20') + "_" + lec_name
                lec_uri = lec_uri.replace('%20', '_')

                # Add lecture
                graph.add((unid[lec_uri], RDF.type, uni.Lecture))

                # Add lecture number
                graph.add((unid[lec_uri], uni.lecture_number, Literal(lec_num[lec_num.find("_")+1:], datatype=XSD.integer)))

                # Add lecture name
                graph.add((unid[lec_uri], uni.lecture_name, Literal(lec_name)))

                # Add has lecture
                graph.add((unid[course[course.find("-")+1:-9]], uni.has_lecture, unid[lec_uri]))

                # Add lecture content entity
                graph.add((lec_cont_uri, RDF.type, uni.Slides))

                # Attach lecture content entity to the lecture
                graph.add((unid[lec_uri], uni.has_content, lec_cont_uri))

    # Adding students to the graph
    for student_id, student_info in data_students.items():

        fname = student_info['Fname']
        lname = student_info['Lname']
        email = student_info['email']

        #making student entities
        graph.add((unid[str(student_id)], RDF.type, uni.Student))
        graph.add((unid[str(student_id)], FOAF.firstName, Literal(fname)))
        graph.add((unid[str(student_id)], FOAF.lastName, Literal(lname)))
        graph.add((unid[str(student_id)], FOAF.mbox, Literal(email)))
        graph.add((unid[str(student_id)], uni.student_ID, Literal(student_id)))

    # Adding students and gardes to the RDF graph
    for student_id, grades in data_grades.items():
        
        pass_grade = "D"

        for cource_id, grade in grades.items():
            #making garde entities
            garde_uri = grade + "_" + str(student_id)
            graph.add((unid[garde_uri], RDF.type, uni.Grade))
            graph.add((unid[garde_uri], uni.grade_value, Literal(grade)))

            #connection grade to course
            graph.add((unid[garde_uri], uni.grade_obtained_in, unid[cource_id]))

            #connection name to grade
            graph.add((unid[str(student_id)], uni.grade_obtained, unid[garde_uri]))

    # Serialize graph
    graph.serialize(destination="dummy_data.ttl", format='turtle')

# Get current dir
curr_dir = os.getcwd()

# Graph creation
create_course_graph(get_course_info(), get_files(curr_dir))