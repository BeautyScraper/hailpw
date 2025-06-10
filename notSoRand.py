import random
import re
import os
from pathlib import Path

def randomLine(fileName="test.txt"):
    try:
        # print("opening " + fileName)
        with open("files\\" + fileName,"r") as inF:
            try:
                selectedLine = random.choice(inF.readlines())
            except:
                selectedLine = 'Kuch Nahi'
            if selectedLine == 'Kuch Nahi' or random.randint(1,100) <= -1:
               os.system('start "" "files\%s"' % (fileName))
            # print("Selected Lines is " + selectedLine)
            while(re.search("\[(.*?)\]",selectedLine)):
                replaceMentStr = randomLine(re.search("\[(.*?)\]",selectedLine)[1] + ".txt")
                selectedLine = re.sub("(\[.*?\])",replaceMentStr,selectedLine,1)
    except FileNotFoundError or IndexError:
        # print("Setting default Line")
        if len(fileName.split(" ")) == 1:
            (open("files\\" + fileName,"w")).close()
        selectedLine = fileName.split(".")[0]
    # print("Returning " + selectedLine)
    return selectedLine.rstrip('\n')
    
def main():
    if not Path('files').is_dir():
        os.system("md files")
    return randomLine('start.txt')
    
if __name__ == '__main__':
    os.system("md files")
    line = randomLine("Static.txt")
    with open("result.txt","w") as file:
        file.write(line)

