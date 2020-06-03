# -*- coding: utf-8 -*-
import sys

import Select_Java
import Get_Bugtag
import Check_ICLinking

#動作をまとめる
def Run(lang):
    print("Selected Language: "+ lang)
    lankpath = "../lang/ranking/ranking-"+lang+".txt"
    repo_java = Select_Java.select_java(lankpath)
    repo_java_bug = Get_Bugtag.get_bugtag(repo_java)
    repo_java_bug_ICLink = Check_ICLinking.check_ICLinking(repo_java_bug)
    #XMLつくる
    print("Finished!")


if __name__ == '__main__':
    lang = sys.argv[1]
    Run(lang)
