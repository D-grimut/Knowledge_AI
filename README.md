# Project Assignment #1

### Welcome to our project assignment #1

This project is destined to create a chatbot using course inforamtion that we inputted. For the first part of this assignment, we needed to gather the information and format it for future reference.

Here are the following contents of the assignment as well as their respective descriptions:

- COMP 354-GCS_132 folder
  -   This folder contains all of the course materials (lectures, labs, tutorials, and course outline)
  -   It's content is used to create the triples and knowledge base
  
- COMP 474_6741-GCS_143 folder
  -   This folder contains all of the course materials (lectures, labs,and course outline)
  -   It's content is used to create the triples and knowledge base

- Queries folder
  - This folder contains all of the queries, seperated into files named q1.txt - q13.txt
  - These files are used to run the queries in the program

- Query Outputs
  - This folder contains all of the query outputs, seperated into files named q1-out.csv - q13-out.csv
  - These files show the output of the queries, formated into a CSV format
  
- KB Data Folder 
  - This is the folder that contains all the resources that we need to parse to begin creating the knoweldge graphs
  - There resources are different to the resources found in the Cources foulder as these resources contain only CSV data we use to retrieve information about different classes and students prior to their creation.
  - This folder contains the folowing files: CATALOG.csv, CU_SR_OPEN_DATA_CATALOG.csv, grades.csv, students.csv
  - These files are the main source of information used to create the triples
  - The program gathers and formats the information to ensure the quality of the data
  - These files are read for specific informations such as cource number, description, website, credits, etc. To create the 
    triples.

- dummy_data_ntriples.nt, knowldge_base_turtle.ttl, knowldge_base_ntriples.nt
  - These are the outputs of our graph once we serialize it
  - They come in 2 formats: n-triples format and turtle format

- RDFS Vocab folder
  - This folder contains the vocab.ttl fil which is our RDFS vocabulary defined for this project
  - This file is used as the vocabulary of our graph
  - Used for the definitions for the triples

- URI_Generator.py
  - Python file used as the main file in the program, this file generates all the RDF triples when ran, and creates the
    knowldge_base_turtle.ttl and knowldge_base_ntriples.nt files that contain the triples.
  - Formats all of the data into dictionaries, adds the triples to the graph and serializes it. Also connects 
    to Fuseki Server to run the queries

To ensure that the program runs smoothly, please follow the instructions below:

- Run the URI_Generator.py, this file will generate the knoweldge base.

- After having generated the graph, to run all the querries, follow these steps:

  - Open and run Fuseki Server
  - Note the name of the dataset (bottom left of the image, in this case, "data")
  ![image](https://github.com/D-grimut/Knowledge_AI/assets/48657408/911ce926-fbd9-4da5-a6a8-412931d618b9)
  - Upload into Fuseki Server the generated knoweldge base in the previous step.
  - Go to line 292 where the runAllQueries() method is
  - Find the endpoint_url variable and change the data part of (http://localhost:3030/data) to the name found in Fuseki Server
  - In the main method, runAllQueries() might be commented, due to it creating many .csv files for the outputs. Make sure to uncomment it
  - The files will be created in the main directory and not the Query Ouputs folder

- To make sure Spacy can be run, run the following commands in the terminal:
  - pip install Spacy
  - python -m spacy download en_core_web_sm
  - pip install spacyfishing 
