# -*- coding: utf-8 -*-
import sys
import argparse

import Select_Java
import Get_Bugtag
import Check_ICLinking

parser = argparse.ArgumentParser(description="指定された自然言語・プログラミング言語のバグリポジトリを生成する．")
parser.add_argument('-n','--natural_lang',help='自然言語 (default:ja)',required=True)
parser.add_argument('-p','--prog_lang',help='プログラミング言語(default:Java)',default='Java')
parser.add_argument('-t','--threshold',help='その言語で書かれたIssue数の最小値(これ以下のものは考慮しない．default:50)',type=int,default=50)
parser.add_argument('-v','--verbose',help='実行中に色々表示する(未実装)',action='store_true')


#動作をまとめる
def Run():
    args = parser.parse_args()
    nlang = args.natural_lang
    plang = args.prog_lang
    th = args.threshold

    print("👉 " + nlang + " でIssueが書かれている " + plang + " で開発されたリポジトリからBugRepositoryを生成します．")
    lankpath = "../lang/ranking/ranking-"+nlang+".txt"
    repo_plang = Select_Java.select_java(lankpath,th,nlang)
    repo_plang_bug = Get_Bugtag.get_bugtag(repo_plang)
    repo_plang_bug_ICLink = Check_ICLinking.check_ICLinking(repo_plang_bug)
    #XMLつくる
    print("Finished!")


if __name__ == '__main__':
    Run()
