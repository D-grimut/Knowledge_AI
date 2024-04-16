import os
import platform
import re
from tika import parser

class FileParser:

    def __init__(self, curr_dir) -> None:
        self.curr_dir = curr_dir

    # Method that makes the API call to Apache Tika to parse the file to plain text
    def extract_text(self, pdf_path):
        raw = parser.from_file(pdf_path)
        return raw['content']

    def platform_extension(self):
        if platform.system() == 'Windows':
            return "\\"
        else:
            return "/"
    
    # method to remove all new lines, tabs and encoded charachters from the text 
    def clean_text(self, text):

        clean = re.sub(r'\\n|[\n\r]+|[^\x00-\x7F]+', '', text)
        return clean


    def chnage_to_plain_text(self):

        # Go through directory of current application and get file names
        for root, _, files in os.walk(self.curr_dir):

            if ("COMP" in root):
                for file in files:

                    platform_separator = self.platform_extension()
                    file_path = root +  platform_separator + file
                    file_name, ext = os.path.splitext(file_path)

                    # Skip any files that is already in plane text -  no need parse it
                    if(ext.lower() == ".txt"):
                        continue
                    
                    text_content = self.extract_text(file_path)
                    text_content = self.clean_text(text_content)
                    new_file_path = file_name + ".txt"

                    with open(new_file_path, 'w', encoding="utf8") as f:
                        f.write(text_content)
                    
                    os.remove(file_path)

def main():
    # Get current dir
    curr_dir = os.getcwd()
    plain_text_parser = FileParser(curr_dir)
    plain_text_parser.chnage_to_plain_text()

if __name__ == "__main__":
    main()