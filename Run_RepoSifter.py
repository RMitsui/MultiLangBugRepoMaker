# -*- coding: utf-8 -*-
import sys
import argparse

import Select_Java
import Get_Bugtag
import Make_xml
#import Check_ICLinking

parser = argparse.ArgumentParser(description="指定された自然言語・プログラミング言語のバグリポジトリを生成する．")
parser.add_argument('-n','--natural_lang',help='自然言語 (default:ja)',required=True)
parser.add_argument('-p','--prog_lang',help='プログラミング言語(default:Java)',default='Java')
parser.add_argument('-t','--threshold',help='その言語で書かれたIssue数ランキングの上からn番目までを考慮する．(これ以下のものは考慮しない．default:50)',type=int,default=50)
parser.add_argument('-v','--verbose',help='実行中に色々表示する(未実装)',action='store_true')


#動作をまとめる
def Run():
    args = parser.parse_args()
    nlang = args.natural_lang
    plang = args.prog_lang
    th = args.threshold

    print("👉 " + nlang + " でIssueが書かれている " + plang + " で開発されたリポジトリからBugRepositoryを生成します．")
    lankpath = "../lang/ranking/ranking-"+nlang+".txt"
    repo_plang = Select_Java.select_java(lankpath,th,plang)
    print("🎉 完了")
    repo_plang_bug = Get_Bugtag.get_bugtag(repo_plang)
    print("🎉 完了")
    #repo_plang_bug_ICLink = Check_ICLinking.check_ICLinking(repo_plang_bug)
    #XMLつくる
    f = open(repo_plang_bug,"r")
    w = open("./BugRepository/ranking-"+nlang+"_"+plang+"_bugrepo.txt","w")
    while True:
        line = f.readline().split()
        if(len(line)==0):
            #空行
            break
        reponame = line[1].rstrip()
        bugnum = Make_xml.make(reponame,nlang)
        w.write(str(line[0]) +" "+ str(bugnum) + + reponame +"\n")

    f.close()
    w.close()
    print("🎉 完了")
    print("🎊生成が終了しました！")


if __name__ == '__main__':
    Run()
