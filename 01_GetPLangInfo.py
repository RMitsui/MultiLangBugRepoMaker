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

def GetPlangInfo(filepath,th):
    """
    入力されたリポジトリのランキングの上位th番目までのリポジトリのプログラミング言語を付与して出力する．
    ディレクトリ./{prang}に，{入力ファイル名}_PLang.txtを出力する．(ex. .Java/ranking-ja_PLang.txt)

    Parameters
    ----------
    filepath : String
        リポジトリランキングの場所．
    th : int
        考慮する最大順位．filepathに書かれたth番目のリポジトリまでを検索対象とする．
    

    Returns
    ----------
    outpath : String
        実行ファイルから出力ファイル名への相対path.
    """
    g = Github(token)

    print("👉 選択された自然言語で書かれたイシューランキングからリポジトリのプログラミング言語情報を取得します．")

    #NLイシュー数ランキングを読む
    f = open(filepath,"r")
    #NLイシュー数ランキング(指定されたプ言語)を書く
    outpath = "./PLang/"+os.path.splitext(os.path.basename(filepath))[0]+"_PLang.csv"
    w = open(outpath,"w")

    #上位 th 位のリポジトリに対して
    i = 0
    while(1):
        if(i >= th):
            break
        line = f.readline().split()
        if(len(line) == 0):
            #空行の場合
            break
        num = int(line[0])
        name = line[1].strip()
        try:
            repo = g.get_repo(name)
            if(repo.language != None):
                w.write(str(num) + "," + name + "," + repo.language + "\n")
                print(str(num) + "," + name + "," + repo.language)
            else:
                th += 1
        except:
            th += 1
            #import traceback
            #traceback.print_exc()
        i += 1

    f.close()
    w.close()

    print("🎉 完了")
    return outpath

if __name__ == '__main__':
    filepath = sys.argv[1]
    if(len(sys.argv)>2):
        th = int(sys.argv[2])
    else:
        th = 50
    GetPlangInfo(filepath,th)
