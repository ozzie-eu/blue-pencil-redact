# imports
import fitz
import re
import json
import sys
import getopt

from fitz.fitz import Outline

class Redactor:

    # static methods work independent of class object
    @staticmethod
    def get_sensitive_data(lines, pattern):
    
        """ Function to get all the lines """

        for line in lines:
        
            # matching the regex to each line
            if re.search(pattern, line, re.IGNORECASE):
                search = re.search(pattern, line, re.IGNORECASE)                
                yield search.group(0)

    # constructor
    def __init__(self, pathInput, pathOutput):
        self.path = pathInput
        self.pathOut = pathOutput

    def redaction(self):
    
        # load the patterns to search for
        with open( "patterns.json ") as f:
            data = f.read()
        patterns = json.loads(data)

        # opening the pdf
        doc = fitz.open(self.path)
        
        # iterating through pages
        for page in doc:
        
            # _wrapContents is needed for fixing
            # alignment issues with rect boxes in some
            # cases where there is alignment issue
            page.wrap_contents()

            for key in patterns:            
                # getting the rect boxes which consists the matches of regex
                sensitive = self.get_sensitive_data(page.getText("text")
                                                    .split( "\n "),patterns[key])
                for data in sensitive:
                    areas = page.searchFor(data)
                    
                    # drawing outline over sensitive datas
                    [page.addRedactAnnot(area, fill = (0, 0, 0)) for area in areas]

            # applying the redaction
            page.apply_redactions()
            
        # saving it to a new pdf
        if (len(self.pathOut) == 0):
            doc.save("redacted.pdf")
        else:
            doc.save(self.pathOut)

        print("Successfully redacted")

def main(argv):
    inputfile =  ""
    outputfile =  ""
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print("redactor.py -i <inputfile> -o <outputfile> ")
        sys.exit(2)

    for opt, arg in opts:
        if opt ==  "-h":
            print("Usage: test.py -i <inputfile> -o <outputfile> ")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if (len(inputfile)>0):
        # replace it with name of the pdf file
        redactor = Redactor(inputfile, outputfile)
        redactor.redaction()
    else:
        print("No input file, nothing to do.")


# driver code for testing
if __name__ == "__main__":

    main(sys.argv[1:])

