import re
import subprocess
import os
from urllib.parse import urlparse
import shutil
from pathlib import Path
import hashlib

def alreadyNotDownloaded(fileName, Id):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        fp = open(dir_path + "\\list\\%s.txt" % fileName, "r")
        print("openening file name %s for checking id %s" % (fileName, Id))
    except(FileNotFoundError):
        return True
    data = fp.read()
    fp.close()
    if Id in data:
        print("%s already cntains %s" % (fileName, Id))
        return False
    else:
        return True

def downloadCompleteRegister(fileName, Id,removeLine = False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("Writing file name %s for id %s" % (fileName, Id))
    try:
        line_prepender(dir_path + "\\list\\%s.txt" % fileName, Id)
    except FileNotFoundError as e:
        with open(dir_path + "\\list\\%s.txt" % fileName, 'w') as f:
            pass
            line_prepender("list\\%s.txt" % fileName, Id)

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

def gdurls(urls,dirpath='',file2dnames = None,ids='',connections=4):
    temp = Path(dirpath).parent / re.sub('[^0-9a-zA-Z\.]+', '_', Path(dirpath).name) 
    dirpath = str(temp)
    if file2dnames is None:
        file2dnames = [re.search('.*\.[^ ]*', x.split('/')[-1])[0] for x in urls]
    if ids == '':
        ids = urls[:]
    # breakpoint()
    digest = hashlib.md5(''.join(ids).encode('utf-8')).hexdigest()
    filename = urlparse(urls[0]).netloc + '_SG.txt'

    if alreadyNotDownloaded(filename, digest):
        gdurls_helper(urls,file2dnames,ids,connections,dirpath)
        downloadCompleteRegister(filename, digest)

def gdurls_helper(urls,file2dnames,ids,connections=4,dirpath=''):    
    for url,fname,id in zip(urls,file2dnames,ids):
        generic_downloader(url,fname,id,connections,dirpath)

def generic_downloader(singleurl,file2dname,id='',connections=4,dirpath=''):
    # breakpoint()
    filename = urlparse(singleurl).netloc + '.txt'
    savepath = r'D:\paradise\stuff\new\hott'
    if dirpath != '':
        savepath = dirpath
    # fpath = Path(fpath)
    if id == '':
        id = singleurl.split('/')[-1]
    if alreadyNotDownloaded(filename, id):
        ariaDownload(singleurl, savepath, file2dname, connections)
        downloadCompleteRegister(filename, id)

def ariaDownload(url,downPath,filename,connections=4):
    # import pdb;pdb.set_trace()
    temp_path = r'c:\dumpinGGrounds\aria'
    # breakpoint()
    # downPath  = 
    Path(temp_path).mkdir(exist_ok=True,parents=True)
    Path(downPath).mkdir(exist_ok=True,parents=True)
    filename = re.sub('[^0-9a-zA-Z\.]+', '_', filename)
    subprocess.run(['aria2c','-l', r'C:\temp\arialog.txt' , '-UMozilla/5.0' ,'--dir', temp_path, '-o', filename,'-x', str(connections) , url.strip()],capture_output=False)
    # if not 'download completed' in str(x):
    #     # breakpoint()
    #     raise Exception('aria2c file downloading failed')
    print(f'{filename} downloaded successfully and now being moved to {downPath}')
    try:
        shutil.move(Path(temp_path)/filename, Path(downPath)/filename)
    except FileNotFoundError as e:
        print("File not found")
        # breakpoint()
    # dfile = Path(temp_path) / filename
    # if dfile.is_file():
    #    shutil.move(dfile,downPath)
    # else:
    #     raise "url not working"
    #     breakpoint()
def noteItDown(fppath,content,id,website):
    if alreadyNotDownloaded(website,id):
        with open(fppath, 'a+') as fp:
            fp.write(content+'\n') 
        downloadCompleteRegister(website,id)
    return