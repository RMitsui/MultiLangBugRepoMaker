# MultiLangBugRepoMaker

## これはなに
- 自然言語NLで書かれたIssue数ランキングから，プログラミング言語PLで書かれたリポジトリ集合Repos(NL,PL)を取得
- Repos(NL,PL)に含まれる各リポジトリに対して，バグ情報をGitHubAPIを用いて収集し，バグ情報XMLを生成

## Require
> langdetect
> pygithub
pipとかでinstallできるはず

以下のようにgithubのtokenを記載した`Conf.py`を各pythonファイルと同じ階層に入れておく
```python:Conf.py
GITHUB_API_KEY = "トークン"
```

## Usage


## しくみ
~~命名規則ガバガバシリーズ~~
### Select_pLang.py
  - 入力されたリポジトリのランキングの上位th番目までに含まれるplangで書かれたリポジトリを抽出し，
    ディレクトリ./{prang}に，{入力ファイル名}_{plang}.txtを出力する．(ex. .Java/ranking-ja_java.txt)

    #### Parameters
    - filepath : String
        リポジトリランキングの場所．
    - th : int
        考慮する最大順位．filepathに書かれたth番目のリポジトリまでを検索対象とする．
    - plang : String
        対象とするプログラミング言語．表記に注意(java -> Java).

    #### Returns
    - outpath : String
        実行ファイルから出力ファイル名への相対path.
### Get_Bugtag.py
  - 入力されたファイルに記載されたリポジトリの，
    1. Bug(bug)とラベル付けされたIssueの数とリポジトリの名前を，BugラベルIssue数の多い順に./Bug にtxtで出力する．
    2. 各リポジトリについて，バグ情報のうち修正ファイル以外の情報を./Bug/{username}/{reponame}.xmlに出力する．
    3. 各リポジトリについて，PRがどのIssueに紐付いているかを./Bug/{username}/{reponame}_PR.xmlに出力する．
    4. 各リポジトリについてgit logに必要な情報だけをcloneする(git clone --bare)．

    #### Parameters
    - filepath : String
        入力ファイルへのpath

    #### Returns
    - outpath : String
        実行ファイルから出力ファイルへの相対path
### Make_xml.py
  - XMLを生成する．
  
    #### Parameters
    - fullname : String
        リポジトリの名前．{username}/{reponame}の形式．
    - nlang : String
        自然言語．

    #### Returns
    - bugnum : int
        XMLに記載されたバグ数
