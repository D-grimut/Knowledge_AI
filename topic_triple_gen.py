from rdflib import OWL, RDFS, XSD, URIRef, Namespace, Graph, Literal
from rdflib.namespace import FOAF, RDF
from spacy.language import Language
import json
import platform

def platform_extension():
    if platform.system() == 'Windows':
        return "\\"
    else:
        return "/"

# querry check on the graph to see if topics exist
def topic_existance_check(topic_uri, graph):
    query = f"""
    prefix unid: <http://uni.com/data/>
        ask where 
        {{unid:{topic_uri} ?p ?o}}
    """
    return graph.query(query)

# parse json file into dictionary
def get_topics_from_json():
    data = {}
    with open("topics.json", 'r') as f:
        data = json.load(f)
    return data

# Adding topics triples
def topics_graph(topic_dict):
    # Create a graph
    graph = Graph()
    graph.parse("knowldge_base_turtle.ttl")

    # Create new Namespace
    unid = Namespace("http://uni.com/data/")
    uni = Namespace("http://uni.com/schema#")
    dbo = Namespace("http://dbpedia.org/ontology/")

    # Bind Namespaces
    graph.bind("unid", unid)
    graph.bind("uni", uni)
    graph.bind("dbo", dbo)


    for course, files in topic_dict.items():

        course_URI = course[course.find("-")+1:]
        lecture_prefix = course.replace(' ', '_')

        for provenance, topics in files.items():
            prov_name = provenance[0:-4].replace(' ', '_')

            for topic, vals in topics.items():

                topic_name = topic.replace(' ', '_')
                lecture_provenance = lecture_prefix + "_" + prov_name
                
                # if topic does not exist, create and add it to the graph
                if(not topic_existance_check(topic_name, graph)):
                    graph.add((unid[topic_name], RDF.type, uni.Topic))

                    graph.add((unid[topic_name], uni.topicName, Literal(topic_name)))

                    graph.add((unid[topic_name], uni.linked_to, URIRef(vals["url"])))

                    graph.add((unid[course_URI], uni.has_topic, unid[topic_name]))

                graph.add((unid[topic_name], uni.provenance, unid[lecture_provenance]))
                
    graph.serialize(destination="topics_turtle_TEST.ttl", format='turtle')
    graph.serialize(destination="topics_ntriples_TEST.nt", format='nt')

def main():
    
    topic_dict = get_topics_from_json()
    topics_graph(topic_dict)

if __name__ == "__main__":
    main()
