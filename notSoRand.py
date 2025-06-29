import random
import re
import os
from pathlib import Path

def preprocess_lines(lines):
    updated_lines = []
    for line in lines:
        if '#' in line:
            try:
                get_freq = int(line.split('#')[0])
            except ValueError:
                get_freq = 1
            for c in range(get_freq):
                updated_lines.append(line.split('#')[1]) 
        else:
            updated_lines.append(line)
    return updated_lines

def randomLine(fileName="test.txt"):
    try:
        # print("opening " + fileName)
        with open("files\\" + fileName,"r") as inF:
            try:
                allLines = inF.readlines()
                allLines = preprocess_lines(allLines)
                selectedLine = random.choice(allLines)
            except:
                selectedLine = 'Kuch Nahi'
            if selectedLine == 'Kuch Nahi' or random.randint(1,100) <= -1:
               os.system('start "" "files\%s"' % (fileName))
            # print("Selected Lines is " + selectedLine)
            while(re.search("\[([^\[]*?)\]",selectedLine)):
                stringfromfile = re.search("\[([^\[]*?)\]",selectedLine)[1]
                # if stringfromfile != "@self":
                #     stringfromfile = selectedLine
                # stringfromfile = pstringfromfile
                if not '||' in stringfromfile:
                    replaceMentStr = randomLine(stringfromfile + ".txt")
                else:
                    replaceMentStr = random.choice(stringfromfile.split('||'))
                    # breakpoint()
                selectedLine = re.sub("\[([^\[]*?)\]",replaceMentStr,selectedLine,1)
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
    line = randomLine("test.txt")
    print(line)
    # with open("result.txt","w") as file:
    #     file.write(line)

