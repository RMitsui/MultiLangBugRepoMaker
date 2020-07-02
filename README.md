# MultiLangBugRepoMaker

## これはなに
- 自然言語NLで書かれたIssue数ランキングから，プログラミング言語PLで書かれたリポジトリ集合Repos(NL,PL)を取得
- Repos(NL,PL)に含まれる各リポジトリに対して，バグ情報をGitHubAPIを用いて収集し，バグ情報XMLを生成

- 生成するバグリポジトリはBugLocatorで読み込める形式
  - 実際に読み込ませる前にはFixedFileが本当に存在するか確認する必要あり
    - 存在しないファイルをFixedFileとして渡すと落ちるバグ(多分)があるため
    
- ranking-{自然言語PL}.txtは

## Require
> langdetect

> pygithub

pipとかでinstallできるはず

以下のようにgithubのtokenを記載した`Conf.py`を各pythonファイルと同じ階層に入れておく
```python:Conf.py
GITHUB_API_KEY = "トークン"
```

## Usage
![shikumi](https://user-images.githubusercontent.com/43768808/86399542-64eb6280-bce2-11ea-9599-906aaa9efee0.png)

## しくみ


- SelectPLang.py
  - 与えられたリポジトリ群から，あるプログラミング言語(PL)で開発されたものを抽出する．
  - 入力:ある自然言語(NL)で書かれたイシュー数リポジトリランキング(ranking-{PL}.txt)
  - 出力:NLで書かれたイシュー数リポジトリ(PLで開発)ランキング(ranking-{PL}_{NL}.txt)

- GetBugtag.py
  - 入力されたファイルに記載されたリポジトリの，
    1. Bug(bug)とラベル付けされたIssueの数とリポジトリの名前を，BugラベルIssue数の多い順に./Bug にtxtで出力する．
    2. 各リポジトリについて，バグ情報のうち修正ファイル以外の情報を./Bug/{username}/{reponame}.xmlに出力する．
    3. 各リポジトリについて，PRがどのIssueに紐付いているかを./Bug/{username}/{reponame}_PR.xmlに出力する．
    4. 各リポジトリについてgit logに必要な情報だけをcloneする(git clone --bare)．
  - 入力:NLで書かれたイシュー数リポジトリ(PLで開発)ランキング(ranking-{PL}_{NL}.txt)
  - 出力:
    - Bug(bug)とラベル付けされたIssueの数リポジトリランキング(ranking-{PL}_{NL}_bug.txt)
    - 各リポジトリの修正ファイル情報を除くバグ情報({reponame}.xml)
    - 各リポジトリのPRとIssueの紐付き情報({reponame}_PR.xml)

- MakeXML.py
  - 与えられたリポジトリ名から，XMLを生成する．(バグ情報，PR情報が所定のフォルダにあることが前提)
  - 入力:リポジトリ名
  - 出力:そのリポジトリのバグリポジトリ(XML)

- RunMLBRMaker.py
  - 上記機能をまとめて実行する．
  - 入力:ある自然言語(NL)で書かれたイシュー数リポジトリランキング(ranking-{PL}.txt)
  - 出力:入力のうち，PLで開発されたリポジトリの，Bugとラベル付けされたIssueに対する修正ファイルの一覧(バグリポジトリ)
