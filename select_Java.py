# -*- coding: utf-8 -*-
import Conf
from github import Github
import re
import os
import sys

token = Conf.GITHUB_API_KEY

#file入力形式
#{/n} {reponame}

def select_java():
    g = Github(token)
    file = sys.argv[1]
    th = 50
    if(sys.argv[2] != None):
        th = int(sys.argv[2])
    lang = 'Java'
    print("Select Repositories written in "+ lang +" at least " +str(th) +" issues written in selected NL.")
    f = open(file,"r")
    w = open("./"+lang+"/"+os.path.splitext(os.path.basename(file))[0]+"_java.txt","w")

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

if __name__ == '__main__':
    select_java()
