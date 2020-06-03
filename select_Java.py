# -*- coding: utf-8 -*-
import Conf
from github import Github
import re
import os
import sys

token = Conf.GITHUB_API_KEY

#file入力形式
#{/n} {reponame}

def select_java(filepath):
    g = Github(token)

    th = 50
    if(sys.argv[2] != None):
        th = int(sys.argv[2])
    lang = 'Java'
    print("Select Repositories written in "+ lang +" at least " +str(th) +" issues written in selected NL.")
    f = open(filepath,"r")
    w = open("./"+lang+"/"+os.path.splitext(os.path.basename(filepath))[0]+"_java.txt","w")

    while True:
        line = f.readline().split()
        if(len(line)==0):
            break
        num = int(line[0])
        name = line[1].strip()
        try:
            if (num > th):
                repo = g.get_repo(name)
                if repo.language == lang:
                    print(str(num) + " " + name)
                    w.write(name+"\n")
            else:
                break
        except:
            pass
            #import traceback
            #traceback.print_exc()

    f.close()
    w.close()
    return "./"+lang+"/"+os.path.splitext(os.path.basename(filepath))[0]+"_java.txt"

if __name__ == '__main__':
    filepath = sys.argv[1]
    select_java(filepath)
