# r1 收貨紀錄(code-選擇點覆蓋套件正規式)

材料 r1-snapshot.patch(b38af9e6a..b543d974f,53 行)。兩席交回後才一次從逐字稿存檔,quote-check 兩份全錨。

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| a1 | 架構對齊 #1 | major | 同一條路徑已有共用 `_CHOICE_COV_PKG_RE`,修補另寫行內正規式,BOM 與反引號讀法不一致 | 折:抽 `_choice_cov_pkg_of`,兩處都用 |
| a2 | 架構對齊 #2 | major | PITFALL 寫「改成鄰居同款」不實 | 折:改寫成共用讀法 |
| g1 | 通才 #1 | minor | package 與名字之間換行讀不到 | 折:共用讀法收換行(只收空白與換行,不用會吞多行的 ^\s* 開頭) |
| g2 | 通才 #2 | minor | 同 a1 | 折(同一處修改) |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| a1 g2 | `re.search(r"^[ \t]*package[ \t]+([\w.]+)", "﻿package a.b", re.M)` 與 `_CHOICE_COV_PKG_RE` 對照 | HIT:前者 None、後者 a.b |
| g1 | `package\na.b` 餵兩種寫法 | HIT:`[ \t]+` 讀不到 |

## 先查世界

- PRIOR-ART:Kotlin 文法 packageHeader 是 `package` 關鍵字後接 identifier,中間允許換行(NL 是一般空白);來源 https://kotlinlang.org/spec/syntax-and-grammar.html 、 https://kotlinlang.org/spec/packages-and-imports.html 。採用:關鍵字與名字之間收 `[ \t\r\n]+`。
