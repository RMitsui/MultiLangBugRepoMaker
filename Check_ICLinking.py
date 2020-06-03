# -*- coding: utf-8 -*-
import Conf

import re
import os
import sys
import subprocess

from langdetect import detect
from github import Github
token = Conf.GITHUB_API_KEY

def check_ICLinking(filepath):
    g = Github(token)
    file = sys.argv[1]

    print("Select Repositories where issue-commit linking applied.")
    f = open(file,"r")
    w = open("./IC-linked/"+os.path.splitext(os.path.basename(filepath))[0]+"_iclink.txt","w")

    #nl = os.path.splitext(os.path.basename(filepath))[0].split('_')[0].split('-')[1]

    while True:
        line = f.readline().split()
        if(len(line)==0):
            break
        name = line[1].strip()
        num = line[0]
        try:
            repo = g.get_repo(name)
            print(name)
            commits = repo.get_commits()
            bugfix = 0
            for commit in commits:
                message = commit._rawData['commit']['message']
                if('#' in message or 'fix' in message or 'Fix' in message or 'Bug' in message or 'bug' in message):
                    print("\t"+message.replace('\r\n','').replace('\n',''))
                    bugfix+=1
        except:
            #pass
            import traceback
            traceback.print_exc()
        if(bugfix != 0):
            w.write(str(num) +" "+str(bugfix)+" "+name+"\n")

    f.close()
    w.close()
    #subprocess.run(["sort", "-nr", "./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt", "-o" ,"./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt"])
    return "./IC-linked/"+os.path.splitext(os.path.basename(filepath))[0]+"_iclink.txt"

if __name__ == '__main__':
    filepath = sys.argv[1]
    check_ICLinking(filepath)
