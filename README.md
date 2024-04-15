# Project Assignment #1

### Welcome to our project assignment #1

This project is destined to create a chatbot using course inforamtion that we inputted. For the first part of this assignment, we needed to gather the information and format it for future reference.

# File Description

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

- pre_processing.py
  - Python file that reads all of the course contents in the program (COMP 354 and COMP 474) and converts it to plain text files.

- entity_linking.py
  - Python file to link Wikidata URLs to the topics found in the plain text files.
  - It filters the data to specific needs of the program

- topic_triple_gen.py
  - Python file to create the finalized triples for the knowledge base.
  - This will create knowldge_base_turtle.ttl and knowldge_base_ntriples.nt as files.

- All .yml files
  - These files are config files for the Rasa chatbot
  - Do not touch them

- topics.json
  - JSON file that saves all of the filtered content from entity_linking.py for future use.
  - Data saved here for time effeciency.

# Running the program

To ensure that the program runs smoothly, please follow the instructions below:

## Installing Spacy
- To make sure Spacy can be run, run the following commands in the terminal:
  - pip install spacy
  - python -m spacy download en_core_web_sm
  - pip install spacyfishing 

## Running the .py files
- Run pre_processing.py, this file will process the course content into plain text files.
- Run URI_Generator.py, this file will generate the knoweldge base.
- Run entity_linking.py, this file will create a JSON file with all of the filtered data to be used for the final file.
- Run topic_triple_gen.py, this file uses the JSON file to create the triples for the topics and links them to the first knowledge base.

At the end, there should be a .ttl and .nt file with the knowledge base.

## Running Fuseki Server
- After having generated the graph, to run all the querries, follow these steps:
  - Open and run Fuseki Server.
  - Note the name of the dataset (bottom left of the image, in this case, "Data").
  - Because the path is hardcoded in the rasa py script - please make a data set and call it "Data" in Fuseki
  ![image](https://github.com/D-grimut/Knowledge_AI/assets/48657408/911ce926-fbd9-4da5-a6a8-412931d618b9)
  - Upload into Fuseki Server the generated knoweldge base in the previous step.
  - Find the endpoint_url variable and change the data part of (http://localhost:3030/Data) to the name found in Fuseki Server.

## Using Rasa Chatbot
- To ensure that the Rasa Chatbot works as intended, follow these steps:
  - Open a terminal and write the following commands:
    - pip install rasa
    - rasa train
  - Open Fuseki Server where the query dataset is named /Data. If that dataset does not exist, create it.
  - Upload knowledge_base_turtle.ttl to the query database
  - Open 2 terminal windows. Write 1 command per terminal:
    - rasa run actions
    - rasa shell

Once these steps are done, converse with Rasa chatbot!
