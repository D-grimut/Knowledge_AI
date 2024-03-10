from rdflib import Graph, Namespace
from rdflib.namespace import FOAF, RDF
import csv

graph = Graph()

unid = Namespace("http://uni.com/data/")
uni = Namespace("http://uni.com/schema#")

graph.bind("unid", unid)
graph.bind("uni", uni)

data = {}

with open('grades.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    
    for row in reader:
        name = row[0]
        grade_474 = row[1]
        grade_354 = row[2]
    
        data[name] = {"GCS_143" : grade_474, "GCS_132" : grade_354}

print(data)

for name, grades in data.items():
    graph.add((unid[name], RDF.type, uni.Student))
    graph.add((unid[name], FOAF.firstName, uni.Student))
    grade_474 = grades["GCS_143"]
    grade_354 = grades["GCS_132"]
    graph.add((unid[grade_474], RDF.type, uni.Grade))
    graph.add((unid[grade_354], RDF.type, uni.Grade))
    graph.add((unid["GCS_132"], ))

