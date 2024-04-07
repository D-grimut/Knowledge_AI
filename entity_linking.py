import spacy
import os
import platform
from spacy.language import Language

nlp = spacy.load("en_core_web_sm")

@Language.component("filter_links_component")
def filter_links(doc):

    filtered_entities = []

    for ent in doc.ents:
        if (ent._.label_ not in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"] and ent._.url_wikidata is not None and ent._.nerd_score > 0.4):
            filtered_entities.append(ent)
    
    return doc

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

def tokenize_files(file_list):
    for file in file_list:
        # Open files in encoding UTF-8
        with open(file, 'r', encoding="utf8") as f:
            cont = f.read()
            # Doc to send
            doc = nlp(cont)
            print(doc)

def main():
    
    # Import NLP and add fishing pipeline
    
    nlp.add_pipe('entityfishing')
    nlp.add_pipe('filter_links_component', name="filter_URI_links", after='entityfishing')

    # Get directory and get files
    curr_dir = os.getcwd()
    file_list = get_files(curr_dir)

    # Tokenize files
    tokenize_files(file_list)


if __name__ == "__main__":
    main()