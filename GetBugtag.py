# -*- coding: utf-8 -*-
import datetime
import os
import re
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape

import Conf
from github import Github
from langdetect import detect

token = Conf.GITHUB_API_KEY

#入力file形式
#{reponame}

#出力file形式(txt)
#{\d*} {reponame}

def get_bugtag(filepath):
    """入力されたファイルに記載されたリポジトリの，
    1. Bug(bug)とラベル付けされたIssueの数とリポジトリの名前を，BugラベルIssue数の多い順に./Bug にtxtで出力する．
    2. 各リポジトリについて，バグ情報のうち修正ファイル以外の情報を./Bug/{username}/{reponame}.xmlに出力する．
    3. 各リポジトリについて，PRがどのIssueに紐付いているかを./Bug/{username}/{reponame}_PR.xmlに出力する．
    4. 各リポジトリについてgit logに必要な情報だけをcloneする(git clone --bare)．

    Parameters
    ----------
    filepath : String
        入力ファイルへのpath

    Returns
    -------
    outpath : String
        実行ファイルから出力ファイルへの相対path
    """
    g = Github(token)

    print("👉 バグとラベル付けされたイシューを選定し，バグ情報のXMLファイルを生成する．")
    f = open(filepath, "r")
    outpath = "./Bug/" + os.path.splitext(os.path.basename(filepath))[0] + "_bug.txt"
    w = open(outpath, "w")

    #自然言語
    nlang = os.path.splitext(os.path.basename(filepath))[0].split('_')[0].split('-')[1]

    while True:
        line = f.readline().split()
        if(len(line) == 0):
            #空行
            break
        name = line[0].strip()

        #ディレクトリ /Bug/{自然言語}，/Bug/{自然言語}/{ユーザ名}　を生成する
        os.makedirs("./Bug/" + nlang, exist_ok=True)
        os.makedirs("./Bug/" + nlang + "/" + name.split('/')[0], exist_ok=True)

        #バグ情報XMLを生成する
        isf = open("./Bug/" + nlang + "/" + name + ".xml", "w")
        isf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
        isf.write("<bugs>\n")

        #PRXMLを生成する
        prf = open("./Bug/" + nlang + "/" + name + "_PR.xml","w")
        prf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
        prf.write("<pullrequests>\n")

        #ファイルをなめる
        try:
            repo = g.get_repo(name)
            print(name)
            #Bugラベルの捜索
            repolabels = repo.get_labels()
            buglabel = None
            for label in repolabels:
                if("bug" in label.name or "Bug" in label.name):
                    buglabel = label
            if buglabel is None:
                #bugissueがない場合はBug以下に何も残さない．
                os.remove("./Bug/" + nlang + "/" + name + ".xml")
                os.remove("./Bug/" + nlang + "/" + name + "_PR.xml")
                try:
                    os.rmdir("./Bug/" + nlang + "/" + name.split('/')[0])
                except OSError as e:
                    #握潰
                    pass
                continue

            issues = repo.get_issues(state="closed",label=buglabel)
            bugissues = 0
            for issue in issues:
                title = removeControlCharacter(issue.title)
                if(issue.body != None):
                    body = removeControlCharacter(issue.body.replace("\n"," ").replace("\r",""))
                else:
                    body = ""

                if(not issue.pull_request):
                    print("\tIS#" + str(issue.number) + " " + title)
                    isf.write("\t<bug>\n")
                    isf.write("\t\t<id>" + str(issue.number) + "</id>\n")
                    isf.write("\t\t<title>" + escape(title) + "</title>\n")
                    if(issue.body != None):
                        isf.write("\t\t<body>" + escape(body) + "</body>\n")
                    else:
                        isf.write("\t\t<body></body>\n")
                    isf.write("\t\t<created>" + issue.created_at.strftime("%Y-%m-%d %H:%M:%S") + "</created>\n")
                    isf.write("\t\t<closed>" + issue.closed_at.strftime("%Y-%m-%d %H:%M:%S") + "</closed>\n")
                    isf.write("\t</bug>\n")
                    bugissues += 1
            isf.write("</bugs>\n")

            #PR情報
            pullrequests = repo.get_pulls(state="closed")
            for pr in pullrequests:
                title = removeControlCharacter(pr.title)
                if(pr.body != None):
                    body = removeControlCharacter(pr.body.replace("\n"," ").replace("\r",""))
                else:
                    body = ""
                #PRのmessageにfix,close,resolveがあればそのIssueと紐付ける
                mat = re.match(r"(fix(ed|es)*|close(s)*|resolve(s|d)*) #([0-9]+)",body)
                if(mat):
                    print("\tPR#" + str(pr.number) + " " + title)
                    print("\t\t-> #" + str(mat.group(5)))
                    prf.write("\t<pullrequest>\n")
                    prf.write("\t\t<number>" + str(pr.number) + "</number>\n")
                    prf.write("\t\t<title>" + escape(title) + "</title>\n")
                    if(issue.body != None):
                        prf.write("\t\t<body>" + escape(body) + "</body>\n")
                    else:
                        prf.write("\t\t<body></body>\n")
                    prf.write("\t\t<to>" + mat.group(5) + "</to>\n")
                    prf.write("\t</pullrequest>\n")
            prf.write("</pullrequests>\n")

            if(bugissues != 0):
                print("\t😃" + str(bugissues) + "件のイシューが検出されました．")
                w.write(str(bugissues) + " " + name + "\n")
                os.chdir("./Bug/" + nlang + "/" + name.split('/')[0])
                #git logを実行するために，各リポジトリの.gitファイルだけを取得する．
                if(os.path.exists("./" + name.split('/')[1] + ".git")):
                    #すでにあったら削除する
                    shutil.rmtree("./" + name.split('/')[1] + ".git")
                subprocess.run(["git", "clone", "--bare", "https://github.com/" + name])
                os.chdir("./../../..")
            else:
                #bugissueがない場合はBug以下に何も残さない．
                os.remove("./Bug/" + nlang + "/" + name + ".xml")
                os.remove("./Bug/" + nlang + "/" + name + "_PR.xml")
                try:
                    os.rmdir("./Bug/" + nlang + "/" + name.split('/')[0])
                except OSError as e:
                    #握潰
                    pass

        except:
            import traceback
            traceback.print_exc()

    prf.close()
    isf.close()
    f.close()
    w.close()

    #イシューの数順にソートしておく
    subprocess.run(["sort", "-nr", outpath, "-o", outpath])
    print("🎉 完了")
    return outpath


def removeControlCharacter(s):
    ret = ''
    for c in s:
        ord_num = ord(c)
        #制御文字
        if(ord_num <= 31):
            pass
        else:
            ret += c
    return ret

if __name__ == '__main__':
    filepath = sys.argv[1]
    get_bugtag(filepath)
