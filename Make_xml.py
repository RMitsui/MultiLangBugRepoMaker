# -*- coding: utf-8 -*-

import buginfo
import os
import re
import sys
import xml.etree.ElementTree as ET
import Conf
import subprocess
import itertools
from github import Github
from xml.sax.saxutils import escape
token = Conf.GITHUB_API_KEY
fullname = ''
g = Github(token)


def make(reponame, nlang):
    #バグリポジトリXMLを生成する
    os.makedirs('./BugRepository/'+nlang, exist_ok=True)
    wf = open('./BugRepository/'+nlang+'/'+reponame+'.xml',mode='w')
    wf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
    wf.write('<bugrepository name="'+reponame+'">\n')

    #バグ情報XMLから情報を取得する
    tree = ET.parse("./Bug/"+nlang+"/"+fullname+".xml")
    root = tree.getroot()

    prtree = ET.parse("./Bug/"+nlang+"/"+fullname+"_PR.xml")
    prroot = prtree.getroot()

    repo = g.get_repo(fullname)

    #git logにより各コミットでの変更ファイルをgitlog.txtに出力する
    os.chdir("./Bug/"+nlang+"/"+fullname+".git")
    gl = open("../gitlog.txt","w")
    subprocess.run(["git","log","--branches", "--name-status", "--oneline", "--all","--pretty=format:%H, %s, %ad"],encoding='UTF-8',stdout=gl)
    gl.close()
    os.chdir("./../../../..")

    #イシューのeventがreferencedとclosedのもののコミット(と変更ファイル)を取得しXMLに書く
    for bug in root:
        print(bug.find("id").text)
        bugid = bug.find("id").text
        issue = repo.get_issue(int(bugid))
        fixed = []

        #イシューのeventをなめる
        events = issue.get_events()
        for ev in events:
            if ev.event == "referenced" or ev.event == "closed":
                if ev.commit_id != None:
                    commitid = ev.commit_id
                    print("\tcid:" + commitid)
                    fixed.append(get_fixfiles(commitid,fullname,nlang))

        title = charset(bug.find("title").text)
        body = charset(bug.find("body").text)
        created = charset(bug.find("created").text)
        closed = charset(bug.find("closed").text)

        #対象とするPRがあるか検索する(ぜんぶみる)
        prroot = prtree.getroot()
        for pr in prroot:
            if pr.find("to").text == bugid:
                prid = pr.find("number").text
                fixed.append(get_pr_fixfiles(prid,repo))
                break

        files = list(itertools.chain.from_iterable(fixed))
        files_uniq = list(set(files))
        if len(files) == 0:
            print("None.")
            continue

        wf.write('\t<bug id="'+bugid+'" opendate="'+created+'" fixdate="'+closed+'">\n')
        wf.write('\t\t<buginformation>\n')
        wf.write('\t\t\t<summary>'+escape(title)+'</summary>\n')
        wf.write('\t\t\t<description>'+escape(body)+'</description>\n')
        wf.write('\t\t</buginformation>\n')
        wf.write('\t\t<fixedfiles>\n')
        for file in files_uniq:
            wf.write('\t\t<file>')
            wf.write(file)
            wf.write('</file>\n')
        wf.write('\t\t</fixedfiles>\n')
        wf.write('\t</bug>\n')
    wf.write('<bugrepository>\n')
    wf.close()


def get_fixfiles(commitid,fullname,nlang):
    fixed = []
    #print(os.getcwd())
    logs = open("./Bug/"+nlang+"/"+fullname.split('/')[0]+"/gitlog.txt","r")
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
                fixed.append(line.rstrip().split('\t')[1])
                print("\t\t"+line.rstrip().split('\t')[1])

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
                fixed.append(file.filename)
                print("\t\t"+file.filename)

    return fixed



#XMLの文字コード調整用
def charset(text):
    return text.encode('ISO-8859-1').decode('UTF-8')

if __name__ == '__main__':
    reponame = sys.argv[1].split('/')[1]
    nlang = sys.argv[2]
    fullname = sys.argv[1]
    make(reponame, nlang)
