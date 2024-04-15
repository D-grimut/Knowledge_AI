import os
import csv
import pandas as pd
import platform
import csv
from rdflib import OWL, RDFS, XSD, URIRef, Namespace, Graph, Literal
from rdflib.namespace import FOAF, RDF
from SPARQLWrapper import SPARQLWrapper, JSON


def populate_cource_arr(key_name, title_name, file, enc=None):

    courses = {}

    with open(file, mode='r', encoding=enc) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:

            for key, value in row.items():
                if (row[title_name]):
                    new_val = row[title_name].replace(" ", "_")

                courses[row[title_name]] = row[key_name]

    return courses


def get_course_info(curr_dir):

    data = {}
    index = {}

    catalog = ""
    data_catalog = ""

    if platform.system() == 'Windows':
        catalog = curr_dir + "\KB Data\CATALOG.csv"
        data_catalog = curr_dir + "\KB Data\CU_SR_OPEN_DATA_CATALOG.csv"
    else:
        catalog = curr_dir + "/KB Data/CATALOG.csv"
        data_catalog = curr_dir + "/KB Data/CU_SR_OPEN_DATA_CATALOG.csv"

    course_list = populate_cource_arr("Key", "Title", catalog)
    course_list_cred = populate_cource_arr(
        "Course ID", "Long Title", data_catalog, "utf-16")

    for key, val in course_list.items():
        if (key in course_list_cred and key in course_list):
            index[course_list_cred[key]] = course_list[key]

    with open(catalog, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:

            for key, value in row.items():

                if value in course_list:
                    if (row["Title"]):
                        new_val = row["Title"].replace(" ", "_")

                        course_num = -1
                        try:
                            int_value = int(
                                row["Course number"].replace('\xa0', ''))
                            course_num = int_value
                        except ValueError:
                            course_num = -1

                    description = row["Description"]

                    if (description.strip() == 0):
                        description = "This course does not have a description in the available database"

                    data[row["Key"]] = {
                        "Course code": row["Course code"],
                        "Course number": course_num,
                        "Title": new_val,
                        "Website": row["Website"],
                        "Description": description
                    }

    with open(data_catalog, mode='r', encoding="utf-16") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:

            for key, value in row.items():
                if value in index:
                    course_id = index[value]
                    data[course_id]["Class Units"] = row["Class Units"]
    return data


def get_files(dir):
    file_list = {}

    # Go through directory of current application and get file names
    for root, dirs, files in os.walk(dir):

        if ("COMP" in root):
            lecture_number = 0  # simple counter for lecture number TODO: change to dinmaic through MLP extraction or other means in part 2
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

# Since the data extraction process for grades and student info is the same, we use only one function


def student_info_extract(file):
    data = {}

    student_info = pd.read_csv(file)

    for index, row in student_info.iterrows():

        curr_student = -1

        for column_name, value in row.items():

            if (column_name == "ID"):
                curr_student = value
                data[curr_student] = {}
            else:
                data[curr_student][column_name] = value

    return data


def lecture_graph(graph, get_files):
    unid = Namespace("http://uni.com/data/")
    uni = Namespace("http://uni.com/schema#")
    dbo = Namespace("http://dbpedia.org/ontology/")

    graph.bind("unid", unid)
    graph.bind("uni", uni)
    graph.bind("dbo", dbo)

    for course, course_content in get_files.items():
        if "Lectures" in course:
            for lec_num, lec_cont_uri in course_content.items():

                # Change lec_name
                lec_name = lec_cont_uri[lec_cont_uri.find("Lectures/")+9:-4]

                lec_uri = ""

                if platform.system() == 'Windows':
                    lec_uri = course[:course.find("\\")].replace(
                        ' ', '%20') + "_" + lec_name
                else:
                    lec_uri = course[:course.find(
                        "/")].replace(' ', '%20') + "_" + lec_name

                lec_uri = lec_uri.replace('%20', '_')

                lec_num_formatted = lec_num[lec_num.find("_")+1:]

                # Add lecture
                graph.add((unid[lec_uri], RDF.type, uni.Lecture))

                # Add lecture number
                graph.add((unid[lec_uri], uni.lecture_number, Literal(
                    lec_num_formatted, datatype=XSD.integer)))

                lec_name = lec_name.replace('%20', " ")

                # Add lecture name
                graph.add((unid[lec_uri], uni.lecture_name, Literal(lec_name)))

                # Add has lecture
                graph.add((unid[course[course.find("-")+1:-9]],
                          uni.has_lecture, unid[lec_uri]))

                # Add lecture content entity
                graph.add((lec_cont_uri, RDF.type, uni.Slides))

                # Attach lecture content entity to the lecture
                graph.add((unid[lec_uri], uni.has_content, lec_cont_uri))

        elif "Labs" in course:
            for lec_num, lec_cont_uri in course_content.items():

                # Change lec_name
                lec_name = lec_cont_uri[lec_cont_uri.find("Labs/")+5:-4]

                lec_uri = ""

                if platform.system() == 'Windows':
                    lec_uri = course[:course.find("\\")].replace(
                        ' ', '%20') + "_" + lec_name
                else:
                    lec_uri = course[:course.find(
                        "/")].replace(' ', '%20') + "_" + lec_name

                lec_uri = lec_uri.replace('%20', '_').replace("#", "")

                lec_num_formatted = lec_num[lec_num.find("_")+1:]

                # Add lecture
                graph.add((unid[lec_uri], RDF.type, uni.Labs))

                # Add lecture number
                graph.add((unid[lec_uri], uni.lecture_number, Literal(
                    lec_num_formatted, datatype=XSD.integer)))

                lec_name = lec_name.replace('%20', " ")

                # Add lecture name
                graph.add((unid[lec_uri], uni.lecture_name, Literal(lec_name)))

                # Add has lecture
                graph.add((unid[course[course.find("-")+1:-5]],
                          uni.has_lecture, unid[lec_uri]))

                # Attach lecture content entity to the lecture
                graph.add((unid[lec_uri], uni.has_content, lec_cont_uri))

        elif "Tutorials" in course:
            for lec_num, lec_cont_uri in course_content.items():

                # Change lec_name
                lec_name = lec_cont_uri[lec_cont_uri.find("Tutorials/")+10:-4]

                lec_uri = ""

                if platform.system() == 'Windows':
                    lec_uri = course[:course.find("\\")].replace(
                        ' ', '%20') + "_" + lec_name
                else:
                    lec_uri = course[:course.find(
                        "/")].replace(' ', '%20') + "_" + lec_name

                lec_uri = lec_uri.replace('%20', '_')

                lec_num_formatted = lec_num[lec_num.find("_")+1:]

                # Add lecture
                graph.add((unid[lec_uri], RDF.type, uni.Tutorials))

                # Add lecture number
                graph.add((unid[lec_uri], uni.lecture_number, Literal(
                    lec_num_formatted, datatype=XSD.integer)))

                lec_name = lec_name.replace('%20', " ")

                # Add lecture name
                graph.add((unid[lec_uri], uni.lecture_name, Literal(lec_name)))

                # Add has lecture
                graph.add((unid[course[course.find("-")+1:-10]],
                          uni.has_lecture, unid[lec_uri]))

                # Attach lecture content entity to the lecture
                graph.add((unid[lec_uri], uni.has_content, lec_cont_uri))
        else:
            co = course_content['Lecture_0']
            gcs = co[co.find('-')+1:-21]

            graph.add((unid[gcs], uni.outline, unid[co]))


def create_course_graph(course_list, get_files, curr_dir):
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

    grades_path = ""
    students_path = ""

    if platform.system() == 'Windows':
        grades_path = curr_dir + "\KB Data\grades.csv"
        students_path = curr_dir + "\KB Data\students.csv"
    else:
        grades_path = curr_dir + "/KB Data/grades.csv"
        students_path = curr_dir + "/KB Data/students.csv"

    data_grades = student_info_extract(grades_path)
    data_students = student_info_extract(students_path)

    uni_dummy = URIRef("https://dbpedia.org/data/Concordia_University")

    # Creating Dummy University - Concordia
    graph.add((unid.Concordia, RDF.type, dbo.University))
    graph.add((unid.Concordia, uni.uni_dblink, uni_dummy))
    graph.add((unid.Concordia, uni.name, Literal("Concordia")))
    graph.add((unid.Concordia, OWL.sameAs, URIRef(
        "https://dbpedia.org/resource/Concordia_University")))
    graph.add((unid.Concordia, OWL.sameAs, URIRef(
        "https://www.wikidata.org/entity/Q326342")))

    # Adding Courses to the graph - Concordia ONLY
    for key, values in course_list.items():
        graph.add((unid[key], RDF.type, uni.Course))

        unid_val = values["Title"]
        graph.add((unid[key], uni.subject, Literal(unid_val)))

        if ("Class Units" in values):
            unid_val = values["Class Units"]
            graph.add((unid[key], uni.credits, Literal(
                unid_val, datatype=XSD.decimal)))

        unid_val = values["Course number"]
        graph.add((unid[key], uni.ID, Literal(unid_val, datatype=XSD.integer)))

        unid_val = values["Description"]
        graph.add((unid[key], uni.description, Literal(unid_val)))

        website = values["Website"]

        if (len(website) > 0):
            graph.add((unid[key], RDFS.seeAlso, URIRef(website)))

        graph.add((unid.Concordia, uni.offers, unid[key]))

    # Adding course lectures
    lecture_graph(graph, get_files)

    # --------------------- ADDING TOPICS MANUALLY ---------------------------------
    # Adding 2 topics
    graph.add((unid['Deep_Learning'], RDF.type, uni.Topic))
    graph.add((unid["Engineering_Practices"], RDF.type, uni.Topic))

    # Add topic name
    graph.add((unid['Deep_Learning'], uni.topicName, Literal("Deep Learning")))
    graph.add((unid["Engineering_Practices"], uni.topicName,
              Literal("Engineering Practices")))

    # Add topic link
    graph.add((unid['Deep_Learning'], uni.linked_to, URIRef(
        "https://www.wikidata.org/entity/Q197536")))
    graph.add((unid["Engineering_Practices"], uni.linked_to,
              URIRef("https://www.wikidata.org/entity/Q2920267")))

    # Add topic provenance
    graph.add((unid['Deep_Learning'], uni.provenance,
              unid['COMP_474_6741-GCS_143_Machine_Learning_for_Intelligent_Systems']))
    graph.add((unid["Engineering_Practices"], uni.provenance,
              unid['COMP_354-GCS_132_Project_Management_Concepts']))

    # Add has topic
    graph.add((unid['GCS_143'], uni.has_topic, unid['Deep_Learning']))
    graph.add((unid['GCS_132'], uni.has_topic, unid["Engineering_Practices"]))

    # Adding Topic DBPedia links
    graph.add((unid['GCS_143'], OWL.sameAs, URIRef(
        "https://dbpedia.org/resource/Deep_learning")))
    graph.add((unid['GCS_132'], OWL.sameAs, URIRef(
        "https://www.wikidata.org/entity/Q11023")))

    # # --------------------- ADDING ADDITIONAL RESOURCES MANUALLY ---------------------------------
    # COMP 474
    graph.add((URIRef("https://plato.stanford.edu/entries/artificial-intelligence/"),
               RDF.type, uni.OtherLectureMaterial))
    graph.add((unid['COMP_474_6741-GCS_143_Intelligent_Agents'], uni.has_content,
              URIRef("https://plato.stanford.edu/entries/artificial-intelligence/")))
    # COMP 354
    graph.add((URIRef("https://business.adobe.com/blog/basics/waterfall#:~:text=The%20Waterfall%20methodology%20%E2%80%94%20also%20known,before%20the%20next%20phase%20begins."),
               RDF.type, uni.OtherLectureMaterial))
    graph.add((unid['COMP_354-GCS_132_Viable_Software_Plan'], uni.has_content,
              URIRef("https://business.adobe.com/blog/basics/waterfall#:~:text=The%20Waterfall%20methodology%20%E2%80%94%20also%20known,before%20the%20next%20phase%20begins.")))

    # Adding students to the graph
    for student_id, student_info in data_students.items():

        fname = student_info['Fname']
        lname = student_info['Lname']
        email = student_info['email']

        # making student entities
        graph.add((unid[str(student_id)], RDF.type, uni.Student))
        graph.add((unid[str(student_id)], FOAF.firstName, Literal(fname)))
        graph.add((unid[str(student_id)], FOAF.lastName, Literal(lname)))
        graph.add((unid[str(student_id)], FOAF.mbox, Literal(email)))
        graph.add((unid[str(student_id)], uni.student_ID, Literal(student_id)))

    # Adding students and grades to the RDF graph
    for student_id, grades in data_grades.items():

        pass_grade = "D"

        for cource_id, grade in grades.items():

            # making garde entities
            garde_uri = grade + "_" + str(student_id)
            graph.add((unid[garde_uri], RDF.type, uni.Grade))
            graph.add((unid[garde_uri], uni.grade_value, Literal(grade)))

            if (grade <= pass_grade):
                graph.add((unid[str(student_id)],
                          uni.completed, unid[cource_id]))

            # connection grade to course
            graph.add(
                (unid[garde_uri], uni.grade_obtained_in, unid[cource_id]))

            # connection name to grade
            graph.add((unid[str(student_id)],
                      uni.grade_obtained, unid[garde_uri]))

    # Serialize graph - TTL
    graph.serialize(destination="knowldge_base_turtle.ttl", format='turtle')

    # Serialize graph - nTriples
    graph.serialize(destination="knowldge_base_ntriples.nt", format='nt')


def runAllQueries(curr_dir):
    # Setup database connection
    # To connect to your database, change "data" to whatever your database name is in fuseki.
    endpoint_url = "http://localhost:3030/dummy_data_1"

    # Connect our database connection to SPARQL
    sparql = SPARQLWrapper(endpoint_url)

    # Get current files in directory + get files

    query_dir = ""

    if platform.system() == 'Windows':
        query_dir = curr_dir + "\Queries"
    else:
        query_dir = curr_dir + "/Queries"

    files = os.listdir(query_dir)

    # Get content of every file and add them to query statement
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(query_dir, file), "r") as f:
                # Read file content
                cont = f.read()

                # SPARQL Query
                sparql.setQuery(cont)
                sparql.setReturnFormat(JSON)
                results = sparql.queryAndConvert()

                # Name CSV file
                file_name = f"{file[:-4]}-out.csv"

                # Get only keys from results
                keys = []
                query = results['results']['bindings']

                for q in query:
                    for key in q.keys():
                        if key not in keys:
                            keys.append(key)

                # Write to CSV file
                with open(file_name, 'w', newline='') as csvfile:
                    trip_counter = 0

                    # Open writer and add keys
                    writer = csv.writer(csvfile)
                    writer.writerow(keys)

                    # Get results like before
                    query = results['results']['bindings']

                    # Add values from keys if they exist
                    for q in query:
                        row = []
                        for k in keys:
                            if k in q:
                                row.append(q[k]['value'])
                        trip_counter += 1
                        writer.writerow(row)

                    # Add number of triples returned
                    row.clear()
                    row.append(f"Number of triples: {trip_counter}")
                    writer.writerow(row)


def main():
    # Get current dir
    curr_dir = os.getcwd()

    # Graph creation
    create_course_graph(get_course_info(curr_dir),
                        get_files(curr_dir), curr_dir)

    # Run queries and output them to files
    # runAllQueries(curr_dir)


if __name__ == "__main__":
    main()
