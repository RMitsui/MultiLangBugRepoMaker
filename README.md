# MultiLangBugRepoMaker

## これはなに
- 自然言語NLで書かれたIssue数ランキングから，プログラミング言語PLで書かれたリポジトリ集合Repos(NL,PL)を取得
- Repos(NL,PL)に含まれる各リポジトリに対して，バグ情報をGitHubAPIを用いて収集し，バグ情報XMLを生成

- 生成するバグリポジトリは少し手を加えればBugLocatorで読み込める形式
  - 実際に読み込ませる前にはFixedFileが本当に存在するか確認する必要あり
    - 存在しないファイルをFixedFileとして渡すと落ちるバグ(多分)があるため
  - /区切りではなく.区切りにする必要あり
  - org等のドメイン以前の文字列を削除する必要あり

## Require
> langdetect

> pygithub

pipとかでinstallできるはず

以下のようにgithubのtokenを記載した`Conf.py`を各pythonファイルと同じ階層に入れておく
```python:Conf.py
GITHUB_API_KEY = "トークン"
```

## Usage
あとでかく

- 対応言語
```
af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
```

## しくみ
![shikumi](https://user-images.githubusercontent.com/43768808/86399542-64eb6280-bce2-11ea-9599-906aaa9efee0.png)
この図から少し変更あり

- 01_GetPLangInfo.py
  - リポジトリの言語を取得する

- 02_GetBugIssue.py
  - 各リポジトリのBugラベルが付いたIssueを収集する
  
- 03_MakeXML.py
  - 上記情報を用いてxml形式のバグリポジトリを生成する
