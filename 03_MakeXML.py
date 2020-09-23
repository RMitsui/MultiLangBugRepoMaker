# -*- coding: utf-8 -*-
import itertools
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import Conf
from github import Github
from langdetect import detect

token = Conf.GITHUB_API_KEY
g = Github(token)

def make(fullname, nlang, plang):
    """与えられたバグ情報，PR情報から，XMLを生成する．

    Parameters
    ----------
    fullname : String
        リポジトリの名前．{username}/{reponame}の形式．
    nlang : String
        自然言語．
    plang : String
        プログラミング言語．

    Returns
    -------
    bugnum : int
        XMLに記載されたバグ数
    """
    reponame = fullname.split('/')[1]
    #バグリポジトリXMLを生成する
    os.makedirs('./BugRepository/'+nlang, exist_ok=True)
    os.makedirs('./BugRepository/'+nlang+'/'+plang, exist_ok=True)
    wf = open('./BugRepository/'+nlang+'/'+plang+'/'+reponame+'.xml',mode='w')
    wf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
    wf.write('<bugrepository name="'+reponame+'">\n')

    #バグ情報XMLから情報を取得する
    tree = ET.parse("./Bug/"+nlang+'/'+plang+"/"+fullname+".xml")
    root = tree.getroot()

    prtree = ET.parse("./Bug/"+nlang+'/'+plang+"/"+fullname+"_PR.xml")
    prroot = prtree.getroot()
    try:
        repo = g.get_repo(fullname)
    except:
        return 0

    #git logにより各コミットでの変更ファイルをgitlog.txtに出力する
    os.chdir("./Bug/"+nlang+'/'+plang+"/"+fullname+".git")
    gl = open("../gitlog.txt","w")
    subprocess.run(["git","log","--branches", "--name-status", "--oneline", "--all","--pretty=format:%H, %s, %ad"],encoding='UTF-8',stdout=gl)
    gl.close()
    os.chdir("./../../../../..")
    bugnum = 0

    #イシューのeventがreferencedとclosedのもののコミット(と変更ファイル)を取得しXMLに書く
    for bug in root:
        print(bug.find("id").text)
        bugid = bug.find("id").text
        issue = repo.get_issue(int(bugid))
        fixed = []

        title = charset(bug.find("title").text)
        if bug.find("body").text is None:
            body = ""
        else:
            body = charset(bug.find("body").text)
        created = charset(bug.find("created").text)
        closed = charset(bug.find("closed").text)

        try:
            if(detect(title) != nlang):
                if(body != ""):
                    bodynostack = re.sub('```(.*?)```','',body)
                    bodynourl = re.sub("https?://[\w!?/+\-_~=;.,*&@#$%()'[\]]+", '', bodynostack)
                    if(detect(body) != nlang):
                        print("\tNot " + nlang +".")
                        continue
                else:
                    print("\tNot " + nlang +".")
                    continue
        except:
            #たまにLangDetectExceptionが出る
            print("\tLangDetectException")
            continue

        #イシューのeventをなめる
        events = issue.get_events()
        for ev in events:
            if ev.event == "referenced" or ev.event == "closed":
                if ev.commit_id != None:
                    commitid = ev.commit_id
                    print("\tcid:" + commitid)
                    fixed.append(get_fixfiles(commitid,fullname,nlang,plang))

        #対象とするPRがあるか検索する(ぜんぶみる)
        prroot = prtree.getroot()
        for pr in prroot:
            if pr.find("to").text == bugid:
                prid = pr.find("number").text
                fixed.append(get_pr_fixfiles(prid,repo))
                break

        files = list(itertools.chain.from_iterable(fixed))
        files_uniq = list(set(files))
        if len(files_uniq) == 0:
            print("\tNone.")
            continue

        bugnum += 1
        wf.write('\t<bug id="'+bugid+'" opendate="'+created+'" fixdate="'+closed+'">\n')
        wf.write('\t\t<buginformation>\n')
        wf.write('\t\t\t<summary>'+escape(title)+'</summary>\n')
        wf.write('\t\t\t<description>'+escape(body)+'</description>\n')
        wf.write('\t\t</buginformation>\n')
        wf.write('\t\t<fixedfiles>\n')
        for file in files_uniq:
            wf.write('\t\t\t<file>')
            wf.write(file)
            wf.write('</file>\n')
        wf.write('\t\t</fixedfiles>\n')
        wf.write('\t</bug>\n')
    wf.write('<bugrepository>\n')
    wf.close()
    if(bugnum == 0):
        os.remove('./BugRepository/'+nlang+'/'+plang+'/'+reponame+'.xml')

    return bugnum


def get_fixfiles(commitid,fullname,nlang,plang):
    fixed = []
    #print(os.getcwd())
    logs = open("./Bug/"+nlang+"/"+plang+'/'+fullname.split('/')[0]+"/gitlog.txt","r")
    flag = False
    for line in logs:
        #print(line)
        if(commitid in line):
            flag = True
        if(flag and line == '\n'):
            break
        if("Merge pull request" in line):
            flag = False
        if(flag):
            if(line.split('\t')[0] == 'A' or line.split('\t')[0] == 'M'):
                filename = line.rstrip().split('\t')[1]
                #TODO:多言語対応
                if(filename.endswith(".java")):
                    fixed.append(filename)
                    print("\t\t"+filename)

    logs.close()

    return fixed


def get_pr_fixfiles(prid,repo):
    fixed = []
    print("\t"+ prid)
    pr = repo.get_issue(int(prid))
    prev = pr.get_events()

    for ev in prev:
        if ev.event == "merged":
            cmsha = ev.commit_id
            print("\tcid:" + cmsha +"(PR)")
            prcm = repo.get_commit(cmsha)
            for file in prcm.files:
                #TODO:多言語対応
                if(file.filename.endswith(".java")):
                    fixed.append(file.filename)
                    print("\t\t"+file.filename)

    return fixed


#XMLの文字コード調整用
def charset(text):
    return text.encode('ISO-8859-1').decode('UTF-8')


if __name__ == '__main__':
    nlang = sys.argv[1]
    plang = sys.argv[2]
    repos = open("./Bug/"+nlang+'/'+plang+"/ranking-"+nlang+"_"+plang+"_bug.txt","r")

    if(os.path.exists("./BugRepository/"+nlang+'/'+plang+"/"+nlang+"_"+plang+"_result.txt")):
        read = open("./BugRepository/"+nlang+'/'+plang+"/"+nlang+"_"+plang+"_result.txt","r")
        skipline = len(read.readlines())
        read.close()
        results = open("./BugRepository/"+nlang+'/'+plang+"/"+nlang+"_"+plang+"_result.txt","a")
        
    else:
        os.makedirs("./BugRepository/"+nlang+'/'+plang, exist_ok=True)
        results = open("./BugRepository/"+nlang+'/'+plang+"/"+nlang+"_"+plang+"_result.txt","w")
        skipline = 0
    while True:
        line = repos.readline().split(" ")

        if(skipline > 0):
            skipline = skipline - 1
            continue

        if(len(line) == 0):
            #空行
            break
        try:
            fullname = line[1].rstrip()
        except:
            break

        print("Repository: "+fullname)
        num = make(fullname, nlang, plang)
        results.write(str(num) + " " + fullname+"\n")

    repos.close()
    results.close()
