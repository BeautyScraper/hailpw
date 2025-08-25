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

def random_line(npath):
    newpath = Path('files') /  Path(npath)
    if newpath.with_name(newpath.stem).is_dir():
        newpath = newpath.with_name(newpath.stem)
        files = []
        for f in newpath.iterdir():
            if f.is_file() and f.suffix == '.txt':
                try:
                    if re.search('\((\d+)\)',f.name):
                        freq = int(re.search('\((\d+)\)',f.name).group(1))
                    else:
                        freq = 1
                except Exception as e:
                    # breakpoint()
                    pass
                for _ in range(freq):
                    files.append(f) 

        if files:
            selected_file = random.choice(files)
            return return_entire_string_after_replacing_patterns(selected_file)[0] , selected_file.stem
        
    if newpath.is_file():
       return randomLine_helper(newpath.with_suffix('.txt').name)[0] , None
    else:
       return newpath.stem , None

        # print(newpath)
        # pass
        # breakpoint()
def preprocess_content(content):
    pattern = re.compile("\*\*(\d+)")
    for match in pattern.finditer(content):
        content = content[:match.start()] + content[match.end():]
    return content

def return_entire_string_after_replacing_patterns(filepath:Path):
    with open(filepath, "r") as file:
        content = file.read()
        # content = preprocess_content(content)
        # Preprocess the entire content as a single line with newline
        
        # Replace patterns like [something] recursively
        pattern = re.compile("\[([^\[]*?)\]")
        while pattern.search(content):
            match = pattern.search(content)
            stringfromfile = match.group(1)
            if '||' not in stringfromfile and ' ' not in stringfromfile:
                try:
                    replacement = random_line(stringfromfile + ".txt")[0]
                    # pass
                    # print("Hlle")
                except Exception as e:
                    print(e)

                    breakpoint()
                    pass
            else:
                replacement = random.choice(stringfromfile.split('||'))
            content = content[:match.start()] + replacement + content[match.end():]
        return content.rstrip('\n') , None

def randomLine_helper(fileName="test.txt"):
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
                    replaceMentStr = random_line(stringfromfile + ".txt")[0]
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
    return selectedLine.rstrip('\n') , None
    
def main():
    if not Path('files').is_dir():
        os.system("md files")
    return random_line('start.txt')
    
if __name__ == '__main__':
    os.system("md files")
    line = random_line("gemini.txt")[0]
    print(line)
    # with open("result.txt","w") as file:
    #     file.write(line)

