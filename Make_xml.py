# -*- coding: utf-8 -*-

import buginfo
import os
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
    os.makedirs('./BugRepository/'+nlang, exist_ok=True)
    wf = open('./BugRepository/'+nlang+'/'+reponame+'.xml',mode='w')
    wf.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\n")
    wf.write('<bugrepository name="'+reponame+'">\n')


    tree = ET.parse("./Bug/"+nlang+"/"+fullname+".xml")
    root = tree.getroot()
    repo = g.get_repo(fullname)
    os.chdir("./Bug/"+nlang+"/"+fullname+".git")
    gl = open("../gitlog.txt","w")
    subprocess.run(["git","log","--branches", "--name-status", "--oneline", "--all","--pretty=format:%H, %s, %ad"],encoding='UTF-8',stdout=gl)
    gl.close()
    os.chdir("./../../../..")
    for bug in root:
        print(bug.find("id").text)
        bugid = bug.find("id").text
        issue = repo.get_issue(int(bugid))
        events = issue.get_events()
        fixed = []
        for ev in events:
            if ev.event == "referenced" or ev.event == "closed":
                if ev.commit_id != None:
                    commitid = ev.commit_id
                    print("cid:" + commitid)
                    #fixed.append(get_fixfiles(commitid,fullname,nlang))
                    fixed.append(get_fixfiles(commitid,fullname,nlang))

        #print(charset(bug.find("title").text))
        #print(charset(bug.find("body").text))
        title = charset(bug.find("title").text)
        body = charset(bug.find("body").text)
        created = charset(bug.find("created").text)
        closed = charset(bug.find("closed").text)
        files = list(itertools.chain.from_iterable(fixed))
        print(files)
        if len(files) == 0:
            continue
        wf.write('\t<bug id="'+bugid+'" opendate="'+created+'" fixdate="'+closed+'">\n')
        wf.write('\t\t<buginformation>\n')
        wf.write('\t\t\t<summary>'+title+'</summary>\n')
        wf.write('\t\t\t<description>'+escape(body)+'</description>\n')
        wf.write('\t\t</buginformation>\n')
        wf.write('\t\t<fixedfiles>\n')
        for file in files:
            wf.write('\t\t<file>')
            wf.write(file)
            wf.write('</file>\n')
        wf.write('\t\t</fixedfiles>\n')
        wf.write('\t</bug>\n')
    wf.write('<bugrepository>\n')
    wf.close()



def get_commit(sha):
    pass

def get_issueinfo():
    pass


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
                fixed.append(line.split('\t')[1].replace("\n",""))

    print(fixed)

    logs.close()
    #git log --grep='#' --branches --name-status --oneline --pretty=format:"%H, %s, %ad" > ~/Documents/Lab/2020/gitlog.txt
    return fixed

def charset(text):
    return text.encode('ISO-8859-1').decode('UTF-8')

if __name__ == '__main__':
    reponame = sys.argv[1].split('/')[1]
    nlang = sys.argv[2]
    fullname = sys.argv[1]
    make(reponame, nlang)
