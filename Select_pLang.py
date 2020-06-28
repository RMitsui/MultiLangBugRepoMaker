# -*- coding: utf-8 -*-
import os
import re
import sys

import Conf
from github import Github

token = Conf.GITHUB_API_KEY

#入力file形式
#{\d*} {reponame}

#出力file形式
#{reponame}

def select_plang(filepath,th,plang):
    """
    入力されたリポジトリのランキングの上位th番目までに含まれるplangで書かれたリポジトリを抽出し，
    ディレクトリ./{prang}に，{入力ファイル名}_{plang}.txtを出力する．(ex. .Java/ranking-ja_java.txt)

    Parameters
    ----------
    filepath : String
        リポジトリランキングの場所．
    th : int
        考慮する最大順位．filepathに書かれたth番目のリポジトリまでを検索対象とする．
    plang : String
        対象とするプログラミング言語．表記に注意(java -> Java).

    Returns
    ----------
    outpath : String
        実行ファイルから出力ファイル名への相対path.
    """
    g = Github(token)

    print("👉 選択された自然言語で書かれたイシューランキングの上位 "\
    + str(th) +"番目までのリポジトリから，プログラミング言語" + plang + "で書かれたリポジトリを抽出します．")

    #NLイシュー数ランキングを読む
    f = open(filepath,"r")
    #NLイシュー数ランキング(指定されたプ言語)を書く
    outpath = "./"+plang+"/"+os.path.splitext(os.path.basename(filepath))[0]+"_"+plang+".txt"
    w = open(outpath,"w")

    #上位 th 位のリポジトリに対して
    for i in range(th):
        line = f.readline().split()
        if(len(line) == 0):
            #空行の場合
            break
        num = int(line[0])
        name = line[1].strip()
        try:
            repo = g.get_repo(name)
            if(repo.language == plang):
                print(str(num) + " " + name)
                w.write(name + "\n")
        except:
            pass
            #import traceback
            #traceback.print_exc()

    f.close()
    w.close()

    return outpath

if __name__ == '__main__':
    filepath = sys.argv[1]
    if(len(sys.argv)>2):
        th = sys.argv[2]
    else:
        th = 50
    select_plang(filepath,th)
