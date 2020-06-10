# -*- coding: utf-8 -*-

import buginfo
import os
import sys

def make(reponame, nlang):
    os.makedirs('./BugRepository/'+nlang, exist_ok=True)
    wf = open('./BugRepository/'+nlang+'/'+reponame+'.xml',mode='w')
    wf.write("testtest!")
    wf.close()


def get_issueinfo():
    pass


def get_fixfiles(issuenum):
    pass

if __name__ == '__main__':
    reponame = sys.argv[1].split('/')[1]
    nlang = sys.argv[2]
    make(reponame, nlang)
