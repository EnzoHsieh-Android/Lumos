preflight-4: n/a(code 迴圈)

# r1 收貨留痕(code-兩席相反時端出張力)

| id | 席 | 命令/查證 | 結果(HIT/MISS) | 處置 |
|---|---|---|---|---|

外家席缺席留痕:Codex `lumos_reviewer_code`(gpt-5.6-terra xhigh)讀完審材後撞到用量上限("You've hit your usage limit… try again at 8:02 PM"),沒有產出報告(raw 逐字稿 2191 行、91,314 tokens、無 severity 行)。standard 分級的外家席是 note-if-absent:本輪收斂結論降級成「單家族視角下未發現」,pass 留痕 note 寫明缺席;同 Issues/外家席長期缺席仍照跑loop 記過的前科。
| A1 | 架構對齊 | `grep -c 'errors="replace"' scripts/lumos`=多處;`_tension_read_norm` 嚴格 decode 且 docstring 講理由 | HIT:確實偏離既有讀檔慣例,理由在函式 docstring(r1 設計審邊界席 B6) | 放行(accepted):刻意偏離且已寫明為什麼——候選要分得出「讀到了沒命中」跟「根本沒讀到」 |
| A2 | 架構對齊 | `grep -n 'rsplit(":", 1)\[0\]' scripts/lumos` → 21644(_one)、22108(check 印法)兩處手刻 path 切分 | HIT:既有 `_dispositions_split_path_line` 已算出同一個 path,兩處重刻 | 折:兩處改用 `_dispositions_split_path_line(s)[0]`(席標 ⚠ 判不準;編排者裁:major 一律折,而且改法一行) |
| R1 | 單reviewer | 讀 `_ev` 21616-21632:cfg_broken/平台索引壞的分支回「無法驗證…」,外層再包「證據對不上:」 | HIT:訊息變成「證據對不上:無法驗證…」雙重否定;rc 不變 | 折:外層改成「why 以『無法驗證』開頭就不再包『證據對不上』」,satisfied 與 tension 兩處同改 |
| A1(覆核) | 編排者 | `grep -c 'read_text(encoding="utf-8")' scripts/lumos`=60、`grep -n UnicodeDecodeError`=9 處 except(14533 `except (OSError, UnicodeDecodeError):` 與本案 16908 同型;14291 註解「非 UTF-8 檔原本直接 traceback」) | MISS:席稱「本檔壓倒性 replace、這支跟鄰居不一樣」不成立——嚴格讀+接 UnicodeDecodeError 是本檔既有的另一種做法,不是第二種 | 列 refuted-set(不折不放行);函式 docstring 的理由照留 |

記帳失誤留痕:單reviewer 第一筆 canary record 漏帶 --round(落成 __seq0.1),帳不能撤;同席同內容再記一筆帶 --round r1,判定看 r1。
換編號重記:原編號 code-兩席相反時端出張力 的帳同時有帶輪次與不帶輪次的紀錄,判定閘拒讀(帳不能撤);改用 code-兩席相反時端出張力-v2 重記 r1 兩席,卷證仍在本目錄。
