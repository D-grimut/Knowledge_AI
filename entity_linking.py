import spacy
import os

# Import NLP and add fishing pipeline
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('entityfishing')

def get_files(dir):
    # Get all files and their directories
    file_list = []
    for root, dirs, files in os.walk(dir):
        if ("COMP" in root):
            for file in files:
                file_preped = root + "\\" + file
                file_list.append(file_preped)     

    return file_list

def tokenize_files(file_list):
    for file in file_list:
        # Open files in encoding UTF-8
        with open(file, 'r', encoding="utf8") as f:
            cont = f.read()
            # Doc to send
            doc = nlp(cont)

            # Tokenize document
            for token in doc:
                print(token.text, token.lemma_, token.pos_, token.dep_)

            # SpacyFishing
            for ent in doc.ents:
                print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score))

def main():
    # Get directory and get files
    curr_dir = os.getcwd()
    file_list = get_files(curr_dir)

    # Tokenize files
    tokenize_files(file_list)

if __name__ == "__main__":
    main()