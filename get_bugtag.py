# -*- coding: utf-8 -*-
import Conf

import re
import os
import sys
import subprocess
import datetime

from xml.sax.saxutils import escape
from langdetect import detect
from github import Github
token = Conf.GITHUB_API_KEY

def get_bugtag(filepath):
    g = Github(token)

    print("👉 Select Repositories with issues tagged as bug")
    f = open(filepath,"r")
    w = open("./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt","w")

    nl = os.path.splitext(os.path.basename(filepath))[0].split('_')[0].split('-')[1]

    while True:
        line = f.readline().split()
        if(len(line)==0):
            break
        name = line[0].strip()
        print(os.getcwd())
        os.makedirs("./Bug/"+nl,exist_ok=True)
        os.makedirs("./Bug/"+nl+"/"+name.split('/')[0],exist_ok=True)
        isf = open("./Bug/"+nl+"/"+name+".xml","w")
        isf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
        isf.write("<bugs>\n")
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
                        isf.write("\t<bug>\n")
                        isf.write("\t\t<id>"+str(issue.number)+"</id>\n")
                        isf.write("\t\t<title>"+title+"</title>\n")
                        if(issue.body != None):
                            isf.write("\t\t<body>"+escape(issue.body.replace("\n"," ").replace("\r",""))+"</body>\n")
                        else:
                            isf.write("\t\t<body></body>\n")
                        isf.write("\t\t<created>"+issue.created_at.strftime("%Y-%m-%d %H:%M:%S")+"</created>\n")
                        isf.write("\t\t<closed>"+issue.closed_at.strftime("%Y-%m-%d %H:%M:%S")+"</closed>\n")
                        isf.write("\t</bug>\n")
                        #print(detect(title))
                        bugissues+=1
            isf.write("</bugs>\n")
            print(bugissues)
            if(bugissues != 0):
                w.write(str(bugissues) + " " + name + "\n")
                os.chdir("./Bug/"+nl+"/"+name.split('/')[0])
                subprocess.run(["git","clone","--bare", "https://github.com/"+name])
                os.chdir("./../../..")
            else:
                os.remove("./Bug/"+nl+"/"+name+".xml")
                try:
                    os.rmdir("./Bug/"+nl+"/"+name.split('/')[0])
                except OSError as e:
                    pass

        except:
            #pass
            import traceback
            traceback.print_exc()
    isf.close()
    f.close()
    w.close()
    subprocess.run(["sort", "-nr", "./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt", "-o" ,"./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt"])
    return "./Bug/"+os.path.splitext(os.path.basename(filepath))[0]+"_bug.txt"

if __name__ == '__main__':
    filepath = sys.argv[1]
    get_bugtag(filepath)
