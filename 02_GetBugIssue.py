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

def GetBugIssue(filepath, selectedPLang):
    """入力されたファイルに記載されたリポジトリの，
    1. Bug(bug)とラベル付けされたIssueの数とリポジトリの名前を，BugラベルIssue数の多い順に./Bug にtxtで出力する．
    2. 各リポジトリについて，バグ情報のうち修正ファイル以外の情報を./Bug/{NLang}/{username}/{reponame}.xmlに出力する．
    3. 各リポジトリについて，PRがどのIssueに紐付いているかを./Bug/{NLang}/{username}/{reponame}_PR.xmlに出力する．
    4. 各リポジトリについてgit logに必要な情報だけをcloneする(git clone --bare)．

    Parameters
    ----------
    filepath : String
        入力ファイルへのpath

    SelectedPLang : String
        選択するプログラミング言語．Noneの場合全ての言語

    Returns
    -------
    outpath : String
        実行ファイルから出力ファイルへの相対path
    """
    g = Github(token)

    print("👉 Bugまたはbugとラベル付けされたイシューを選定し，バグ情報のXMLファイルを生成します．")
    
    #自然言語
    nlang = os.path.splitext(os.path.basename(filepath))[0].split('_')[0].replace("ranking-","")

    f = open(filepath, "r")
    os.makedirs("./Bug/" + nlang, exist_ok=True)
    os.makedirs("./Bug/" + nlang + "/" + selectedPLang, exist_ok=True)
    outpath = "./Bug/" + nlang + "/" + selectedPLang + "/" + os.path.splitext(os.path.basename(filepath))[0].split("_")[0] + "_" + selectedPLang + "_bug.txt"

    maxl = 0

    #ranking-{NL}_{PL}_bug.txtがあればgrepで各リポジトリの行数を出しておく(resume機能)
    if(os.path.exists(outpath)):
        bugFile = open(outpath, 'r')
        repos = bugFile.readlines()
        for repo in repos:
            #print(["grep", repo.split(' ')[1], filepath, '-n'])
            lis = subprocess.check_output(["grep", repo.split(' ')[1].rstrip(), filepath, '-n'],text=True)
            print(lis)
            li = lis.split(':')[0].rstrip()
            if(maxl < int(li)):
                maxl = int(li)
        bugFile.close()
        exists = True
    else:
        exists = False

    w = open(outpath, 'a')
   
    print("選択されたプログラミング言語: " + selectedPLang)

    while True:
        line = f.readline().split(",")
        if(len(line) == 0):
            #空行
            break
        try:
            name = line[1].strip()
            plang = line[2].strip()
        except:
            break

        if(maxl > 0):
            maxl = maxl - 1
            continue

        if(selectedPLang != None and selectedPLang != plang):
            continue

        #ディレクトリ /Bug/{自然言語}，/Bug/{自然言語}/{ユーザ名}　を生成する
        
        os.makedirs("./Bug/" + nlang + "/" + plang + "/" + name.split('/')[0], exist_ok=True)

        #バグ情報XMLを生成する
        isf = open("./Bug/" + nlang + "/" + plang + "/" + name + ".xml", "w")
        isf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
        isf.write("<bugs>\n")

        #PRXMLを生成する
        prf = open("./Bug/" + nlang + "/" + plang + "/" + name + "_PR.xml","w")
        prf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
        prf.write("<pullrequests>\n")

        #ファイルをなめる
        try:
            repo = g.get_repo(name)
            print("Repository: " + name)

            #Bugラベル取得
            repolabels = repo.get_labels()
            buglabel = []
            for label in repolabels:
                if("bug" in label.name or "Bug" in label.name):
                    buglabel.append(label.name)

            #Bugラベルがない場合このリポジトリを無視
            if len(buglabel)==0:
                #Bug以下に何も残さない
                os.remove("./Bug/" + nlang + "/" + plang + "/" + name + ".xml")
                os.remove("./Bug/" + nlang + "/" + plang + "/" + name + "_PR.xml")
                try:
                    os.rmdir("./Bug/" + nlang + "/" + plang + "/" + name.split('/')[0])
                except OSError as e:
                    #握潰
                    pass
                continue

            #Bugラベルが付いたIssue取得
            issues = repo.get_issues(state="closed", labels=buglabel)
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

            if(bugissues != 0):
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
                        if(pr.body != None):
                            prf.write("\t\t<body>" + escape(body) + "</body>\n")
                        else:
                            prf.write("\t\t<body></body>\n")
                        prf.write("\t\t<to>" + mat.group(5) + "</to>\n")
                        prf.write("\t</pullrequest>\n")
                prf.write("</pullrequests>\n")

                print("\t😃" + str(bugissues) + "件のイシューが検出されました．")
                w.write(str(bugissues) + " " + name + "\n")
                os.chdir("./Bug/" + nlang + "/" + plang + "/" + name.split('/')[0])
                #git logを実行するために，各リポジトリの.gitファイルだけを取得する．
                if(os.path.exists("./" + name.split('/')[1] + ".git")):
                    #すでにあったら削除する
                    shutil.rmtree("./" + name.split('/')[1] + ".git")
                subprocess.run(["git", "clone", "--bare", "https://github.com/" + name])
                os.chdir("./../../../..")
            else:
                #bugissueがない場合はBug以下に何も残さない．
                os.remove("./Bug/" + nlang + "/" + plang + "/" + name + ".xml")
                os.remove("./Bug/" + nlang + "/" + plang + "/" + name + "_PR.xml")
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
    selectPL = None
    if(len(sys.argv) > 2):
        selectPL = sys.argv[2]
    GetBugIssue(filepath, selectPL)
