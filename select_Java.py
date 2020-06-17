# -*- coding: utf-8 -*-
import Conf
from github import Github
import re
import os
import sys

token = Conf.GITHUB_API_KEY

#file入力形式
#{/n} {reponame}

def select_java(filepath,th,plang):
    g = Github(token)
    lang = plang
    #print("👉 Select Repositories written in "+ lang +" at least " +str(th) +" issues written in selected NL.")
    print("👉 選択された自然言語で書かれたイシューランキングの上から " +str(th) +"番目までのリポジトリから，プログラミング言語"+lang+"で書かれたリポジトリを抽出します．")

    #NLイシュー数ランキングを読む
    f = open(filepath,"r")
    #NLイシュー数ランキング(指定されたプ言語)を書く
    w = open("./"+lang+"/"+os.path.splitext(os.path.basename(filepath))[0]+"_" +lang+".txt","w")

    #上位 th 位のリポジトリに対して
    for i in range(th):
        line = f.readline().split()
        if(len(line)==0):
            #空行の場合
            break
        num = int(line[0])
        name = line[1].strip()
        try:
            repo = g.get_repo(name)
            if repo.language == lang:
                print(str(num) + " " + name)
                w.write(name+"\n")
        except:
            pass
            #import traceback
            #traceback.print_exc()

    f.close()
    w.close()
    return "./"+lang+"/"+os.path.splitext(os.path.basename(filepath))[0]+"_"+plang+".txt"

if __name__ == '__main__':
    filepath = sys.argv[1]
    if(len(sys.argv)>2):
        th = sys.argv[2]
    else:
        th = 50
    select_java(filepath,th)
