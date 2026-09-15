severity: major

# 這一席做了什麼(方法交代)

沒有相信作者「每一支都驗過拆掉會翻紅」這句話,自己動手做了以下驗證(全部在
`/tmp/mw-review*` 臨時目錄跑,沒有動 repo 裡的任何檔案):

1. 把 `governance/eval/retrieval_eval_multiword.py`、`retrieval_eval.py`、
   `scripts/test_lumos.py`、`scripts/lumos` 複製到 `/tmp/mw-review/`,先確認四支新測試
   在乾淨版本上全綠(`python3 scripts/test_lumos.py -k mw_` → 18 passed, 0 failed)。
2. 逐一對 `retrieval_eval_multiword.py` 做四種「拿掉某段修法」的手術,每次都在同一份
   臨時複本上改、單獨重跑對應測試,看是不是乾淨地報紅(不是整輪掛掉)。
3. 另外複製了 `docs/lumos-toolchain-knowledge` 到 `/tmp/mw-review2/`,對
   `t_mw_queries_absent_from_vault` 做「往一篇真實筆記裡塞入題庫查詢字串」的正面驗證。
4. 針對本席鏡頭特別要查的「重組候選池有三個來源」,額外做了一次作者沒做過的手術:
   把來源二、三整個拔掉(只留來源一),驗四支測試還過不過。

## 四項手術結果

| 手術 | 指令/改法 | 結果 |
|---|---|---|
| 拿掉「重組候選池時不接受污染」的 `return 2` | 刪掉 `if a.rebuild_pool: ...return 2` 那 3 行 | `t_mw_rebuild_pool_refuses_contamination` 乾淨翻紅 2 條(rc2 斷言、半份池檔斷言) |
| 拿掉 `load_labels` 裡取 `v["final"]` 那段 | 把 `if isinstance(v, dict): ...v = v["final"]` 整段換成直接 `flat[node]=v` | `t_mw_labels_accept_both_shapes` 乾淨翻紅 3 條 |
| 拿掉 `rnd.shuffle(pool)` | 刪掉 `rnd = random.Random(...)` 與 `rnd.shuffle(pool)` 兩行 | `t_mw_pool_order_is_not_rank` 乾淨翻紅 1 條(池序==名次序) |
| 往 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md` 塞入 M01 的查詢字面 | `echo` 追加一行含「合約 綁定 測試」 | `t_mw_queries_absent_from_vault` 乾淨翻紅 1 條,並正確點出是哪一篇 |
| ★本席加做★:`rebuild_pool` 裡把來源二、三整段清空(`s2=[]; s3=[]`,只留來源一) | | **四支測試全綠,一條都沒紅**(15 passed, 0 failed, 1 skipped) |

前四項證實作者的「拆掉會翻紅」宣稱屬實,不是空話。第五項是本席自己加做的手術,
挖出了一個作者沒宣稱、也沒測到的洞——見下面 major 那條。

---

## 發現

引句:「s2 = list(dict.fromkeys(sum([term_top(t) for t in terms], [])))」
把這一行連同下一行 `s3 = cooccur_top(terms)` 一起改成 `s2 = []` / `s3 = []`(即候選池只剩
「現行系統自己撈到的前十」這一個來源,完全不聯集逐詞出現次數前三、三詞同篇前十),
重跑 `python3 scripts/test_lumos.py -k mw_`,四支新測試（含 `t_mw_pool_order_is_not_rank`）
**全部維持通過**,`15 passed, 0 failed`,一條紅都沒有。也就是說:這批改動的核心賣點
——diff 自己的註解寫得很清楚,「前兩個來源合起來仍有一半來自現行系統」「量出來會讓
新系統看起來更差,與本專案已踩過四次的『拿不同批互比』同一族」——這個三來源聯集本身,
沒有任何一支測試在守。`t_mw_pool_order_is_not_rank` 只驗證了「順序不是名次序」與
「兩次跑結果一樣」,並沒有驗證「池子裡真的聯集了三個來源撈到的東西」;測資剛好是
三個詞都出現在全部三篇筆記裡,所以只用來源一,池子大小、內容都不會變小,四支測試因此
對「有沒有來源二、三」完全無感。以後如果有人在重構時不小心把 `term_top`/`cooccur_top`
兩條線接掉(例如改參數順序、改 import、或效能優化時誤刪),會安靜地把「更好系統的候選
被遺漏、量出來偏向舊系統」這個本專案已經踩過四次的老問題原封不動地帶回來,而且不會有
任何測試發現。
severity: major
blocking: 是

引句:「check("★池的順序不是名次序★", p1 != rank[:len(p1)], f"池={p1} 名次={rank}")」
這條斷言的可靠性依賴測試夾具湊巧有效:`_mk_mw_fixture` 固定造 3 篇筆記(A/B/C),
三個詞在這批資料下三個來源會聯集出同樣的 3 篇,所以池子只有 3 個元素。3 個元素的
隨機排列共有 3!=6 種,其中恰有 1 種等於「名次序」——也就是說,`rnd.shuffle` 的結果
撞上「剛好排出跟名次序一樣」的機率約 1/6,並非結構性不可能。這次因為
`hashlib.sha256(q + POOL_SALT)` 對這個具體查詢字串算出來的種子沒有撞上,測試才通過;
不是因為「打散」這件事被結構性驗證過。往後如果有人改了 `POOL_SALT`、改了查詢字串,
或夾具本身要換題目,約 1/6 的機率會讓這條測試在沒有任何程式碼退步的情況下無端翻紅
(而不是因為 shuffle 真的被拿掉)。不是本次改動的功能性 bug,是測試設計本身有一點靠運氣;
比較穩的作法是把夾具的候選數撐大(例如 5~6 篇不同命中度的筆記),把「巧合排回名次序」
的機率壓到可忽略。
severity: minor
blocking: 否

---

## 逐項回答鏡頭指定的六個問題

1. **測試斷言的東西是不是被測程式自己算出來的?**
   `t_mw_labels_accept_both_shapes`、`t_mw_rebuild_pool_refuses_contamination`、
   `t_mw_pool_order_is_not_rank` 都是呼叫真實模組(`load_labels`/子行程跑腳本)取得結果
   後,拿寫死的期望值比對,不是重算被測邏輯,沒有「自證」問題。
   `t_mw_queries_absent_from_vault` 例外:它是把 `contaminated()` 裡「`q in txt`」那段
   邏輯自己在測試裡重寫了一遍,並不是呼叫模組的 `contaminated()` 函式本身。這意味著
   它守住的是「repo 現在這份真實圖譜資料乾不乾淨」這件事(這點是真守衛,已用正面注水
   驗證過,見上表),但**不會**在 `contaminated()` 函式本身寫錯(例如改成只比對檔名、
   或誤用正規表示式導致漏判)時抓到——因為測試根本沒呼叫那支函式。這個落差本身沒有
   到 major 的程度(因為 `t_mw_rebuild_pool_refuses_contamination` 有間接呼叫到
   `contaminated()` 並驗證了它會擋下污染),放在這裡供記錄,不另開一條。

2. **夾具餵的資料,踩得到要防的那條路嗎?**
   踩得到。`_mk_mw_fixture(contaminate=True)` 造的 `D.md` 確實含查詢字面「斑馬 條紋 計數」
   全文,經手術驗證(拿掉 `return 2`)後兩條相關斷言確實翻紅、且不拿掉時確實正確擋下
   並印出「D.md」,不是空跑。

3. **斷言夠不夠嚴?有沒有「不拋例外就算過」這種鬆斷言?**
   沒看到這種鬆斷言。四支測試的斷言都是具體值比對(dict 相等、rc 數值、字串包含、
   檔案存在與否),`t_mw_labels_accept_both_shapes` 裡唯一一處 try/except 是刻意把
   `SystemExit` 接住轉成字串再拿去跟期望值比對,不是拿「有沒有丟例外」本身當斷言。

4. **拆掉修法真的會紅嗎?**
   會,四項手術結果見上表,三項是作者聲稱有驗過的修法(全部乾淨翻紅、不拖垮整輪),
   第四項(污染插入到真實圖譜)也翻紅且正確點名。

5. **有沒有哪一條行為沒有測試守著?——「重組候選池」段**
   - 來源一(`search_files(..., any_terms=True)[:10]`):有測(`t_mw_pool_order_is_not_rank`
     裡拿它跟 `mw_rank_order` 比對順序)。
   - 來源二(`term_top`,逐詞出現次數前 3)、來源三(`cooccur_top`,三詞同篇前 10)、
     以及「三者聯集」這個動作本身:**沒有任何測試守**,見上面 major 那條,已用手術實測
     驗證(拔掉後四支測試全綠)。
   - 寫檔(`write_json_atomic`):有測(`out2.exists()` 為 False、`out.exists()` 為 True,
     間接驗證了有寫、且失敗路徑不留半份檔)。原子寫入機制本身(先寫 `.tmp` 再 `os.replace`)
     沒有專門測「寫到一半中斷」這種情境,但這是沿用專案既有慣例(`atomic-write-shared-files`
     那條記憶提到的手法),不是這次新引入的風險,不另開發現。

6. **測試本身會不會壞別人的?**
   不會。四支新測試全部用 `tempfile.mkdtemp(prefix="gctl-mw-"/"gctl-mwlab-")` 造獨立臨時
   目錄,跟既有測試套件的慣例一致(套件本身管理暫存根目錄,紅了才保留現場);沒有寫入
   `docs/lumos-toolchain-knowledge` 或任何共用夾具,只有 `t_mw_queries_absent_from_vault`
   讀取(唯讀)真實圖譜與 `governance/eval/multiword/mw-pool.json`,不寫入。沒發現殘留檔案
   或共用狀態污染的問題。

---

## 效能宣稱查核(可反駁宣稱,已查)

- 「沒有任何 async、沒有並行」:`grep -n "async def\|await \|asyncio"` 對
  `retrieval_eval_multiword.py` 掃出 0 筆命中,屬實。
- 「528 篇共 5.5 MB」:`find docs/lumos-toolchain-knowledge -iname "*.md" | wc -l` = 528,
  `cat` 全部內容 `wc -c` = 5,795,188 bytes ≈ 5.8 MB,與宣稱的「528 篇、5.5 MB」量級相符
  (略有出入應是估讀方式差異,不影響「函式範圍內一次性讀進記憶體、跑完即可釋放」這個
  定性結論;不到需要開發現的程度)。
- 「一萬六千次字串掃描」:題庫 10 題,`contaminated()` 每題掃 528 篇 ≈ 5,280 次;
  `rebuild_pool`(只在 `--rebuild-pool` 才跑)的 `term_top` 每題約 3 個詞、各掃 528 篇,
  10 題 ≈ 15,840 次,量級與宣稱的「約一萬六千次」吻合,屬實。
