import spacy
import os
import platform
from rdflib import OWL, RDFS, XSD, URIRef, Namespace, Graph, Literal
from rdflib.namespace import FOAF, RDF
from spacy.language import Language

nlp = spacy.load("en_core_web_sm")

def platform_extension():
    if platform.system() == 'Windows':
        return "\\"
    else:
        return "/"

def get_files(dir):
    # Get all files and their directories
    file_list = []
    for root, dirs, files in os.walk(dir):
        if ("COMP" in root):
            for file in files:
                file_preped = root + platform_extension() + file
                file_list.append(file_preped)     

    return file_list

def post_process(doc):
    file_named_entities = {}

    for ent in doc.ents:
        if (ent.label_ not in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"] and ent._.url_wikidata is not None and ent._.nerd_score > 0.4):

            if ent.text in file_named_entities and ent._.nerd_score <= file_named_entities[ent.text]["sim_score"]:
                continue

            file_named_entities[ent.text] = {"qid" :  ent._.kb_qid,
                                           "url" : ent._.url_wikidata,
                                           "sim_score" : ent._.nerd_score
                                           }       
    return file_named_entities

def process_files(file_list):
    filtered_entities = {}

    for file in file_list:
        # Open files in encoding UTF-8
        with open(file, 'r', encoding="utf8") as f:

            file_name = os.path.basename(file)
            cont = f.read()
            # Doc to send
            doc = nlp(cont)
            filtered_entities[file_name] = post_process(doc)
    
    return filtered_entities

def topics_graph(file_list):
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

    for file, ents in process_files(file_list).items():
        file_nospace = file.replace(' ', '_')

        graph.add((unid[file_nospace], RDF.type, uni.Lecture))

        for topic, vals in ents.items():
            topic_nospace = topic.replace(' ', '_')
            topic_nobs = topic_nospace.replace('\\', '%5C')

            graph.add((unid[topic_nobs], RDF.type, uni.Topic))

            graph.add((unid[topic_nobs], uni.topicName, Literal(topic)))

            graph.add((unid[topic_nobs], uni.linked_to, URIRef(vals["url"])))

            graph.add((unid[file_nospace], uni.has_content, unid[topic_nobs]))

    graph.serialize(destination="topics_turtle.ttl", format='turtle')
    graph.serialize(destination="topics_ntriples.nt", format='nt')

def main():
    
    # Import NLP and add fishing pipeline
    nlp.add_pipe('entityfishing')

    # Get directory and get files
    curr_dir = os.getcwd()
    file_list = get_files(curr_dir)

    topics_graph(file_list)

    # Tokenize files  
    # Keep this commented to not re-write to the text file, very long
    # with open("topics.txt", 'w', newline='', encoding="utf8") as tf:
    #     for file, ents in process_files(file_list).items():
    #         tf.write("\n")
    #         tf.write(file)
    #         tf.write("------------------------------------------------------------------\n")
    #         for topic, vals in ents.items():
    #             tf.write(topic)
    #             tf.write(" -- ")
    #             tf.write(vals["url"])
    #             tf.write("\n")

if __name__ == "__main__":
    main()