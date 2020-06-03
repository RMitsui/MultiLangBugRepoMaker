# -*- coding: utf-8 -*-
import Conf

import re
import os
import sys
import subprocess

from langdetect import detect
from github import Github
token = Conf.GITHUB_API_KEY

def get_bugtag():
    g = Github(token)
    file = sys.argv[1]

    print("Select Repositories with issues tagged as bug")
    f = open(file,"r")
    w = open("./Bug/"+os.path.splitext(os.path.basename(file))[0]+"_bug.txt","w")

    #nl = os.path.splitext(os.path.basename(file))[0].split('_')[0].split('-')[1]

    while True:
        line = f.readline().split()
        if(len(line)==0):
            break
        name = line[0].strip()
        try:
            repo = g.get_repo(name)
            print(name)
            issues = repo.get_issues(state="closed")
            bugissues = 0
            for issue in issues:
                for label in issue.labels:
                    if("bug" in label.name or "Bug" in label.name):
                        title = issue.title
                        print("\t" + title)
                        #print(detect(title))
                        bugissues+=1
            print(bugissues)
            if(bugissues != 0):
                w.write(str(bugissues) + " " + name + "\n")

        except:
            #pass
            import traceback
            traceback.print_exc()

    f.close()
    w.close()
    subprocess.run(["sort", "-nr", "./Bug/"+os.path.splitext(os.path.basename(file))[0]+"_bug.txt", "-o" ,"./Bug/"+os.path.splitext(os.path.basename(file))[0]+"_bug.txt"])

if __name__ == '__main__':
    get_bugtag()
