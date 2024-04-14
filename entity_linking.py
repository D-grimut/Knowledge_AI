import json
import spacy
import os
import platform
from spacy.matcher import Matcher
from spacy.language import Language
from spacy.tokens import Span

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


# Create Matcher
@Language.component("ner_matcher")
def create_matcher(doc):
    matcher = Matcher(nlp.vocab)
    pattern = [{'POS': 'PROPN', 'OP': '+'},
               {'POS': 'ADP', 'OP': '*'},
               {'POS': 'PROPN', 'OP': '*'}]

    matcher.add("ner_identifier", [pattern])

    included_tokens = set()

    spans = []
    for match_id, start, end in matcher(doc):
        if any(token.i in included_tokens for token in doc[start:end]):
            continue

        string_id = nlp.vocab.strings[match_id]
        spans.append((start, end, string_id))
        
        included_tokens.update(range(start, end))

    doc.ents = [Span(doc, start, end, label=label) for start, end, label in spans]
    return doc

# Filtering named topic entities
def post_process(doc):
    file_named_entities = {}

    for ent in doc.ents:
        if (ent._.url_wikidata is not None and ent._.nerd_score > 0.4):

            if ent.text in file_named_entities and ent._.nerd_score <= file_named_entities[ent.text]["sim_score"]:
                continue
            
            file_named_entities[ent.text] = {"qid" :  ent._.kb_qid,
                                           "url" : ent._.url_wikidata,
                                           "sim_score" : ent._.nerd_score
                                           }       
    return file_named_entities

def process_files(file_list, nlp):
    filtered_entities = {}
    course_name = ""

    for file in file_list:

        directory_parts = file.split(platform_extension())
        
        if(course_name == "" or course_name not in directory_parts):
            for part in directory_parts:
                if "COMP" in part:
                    course_name = part
                    break
                
            filtered_entities[course_name] = {}
            
        # Open files in encoding UTF-8
        with open(file, 'r', encoding="utf8") as f:

            file_name = os.path.basename(file)
            cont = f.read()
            # Doc to send
            doc = nlp(cont)
            filtered_entities[course_name][file_name] = post_process(doc)
    
        return filtered_entities

def main():
    
    # Import NLP and add fishing pipeline
    nlp.add_pipe("ner_matcher")
    nlp.add_pipe('entityfishing', last=True)

    # Get directory and get files
    curr_dir = os.getcwd()
    file_list = get_files(curr_dir)

    data = process_files(file_list, nlp)
    
    with open("topics.json", 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

if __name__ == "__main__":
    main()