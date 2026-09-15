severity: major

本席鏡頭:只餵奇怪的東西,看它怎麼壞。全部在自己的臨時目錄(`/tmp/mw-audit.*`)裡真的跑
`governance/eval/retrieval_eval_multiword.py`,不動 repo。以下每條都是真的執行出來的結果,
指令與輸出貼在條目底下。

---

## 1. `contaminated()` 對題庫檔形狀不對,直接裸拋例外(不是清楚報錯)

引句:「q = pool[cid]["query"]」

`contaminated()` 是這次新增的函式,`main()` 一開始就無條件呼叫它(不管是量測還是
`--rebuild-pool`)。它完全沒有檢查 `pool[cid]` 是不是字典、有沒有 `"query"` 鍵,
碰到就直接讓 `KeyError`/`TypeError` 往外炸,印出一整段 Python traceback。

實測(某一題整個沒有 `query` 欄位):
```
$ cat pool_noquery.json
{"M01": {"query": "斑馬 條紋", "pool": []}, "M02": {"pool": []}}
$ python3 governance/eval/retrieval_eval_multiword.py --pool pool_noquery.json --vault vault --rebuild-pool out.json
Traceback (most recent call last):
  ...
  File ".../retrieval_eval_multiword.py", line 112, in contaminated
    q = pool[cid]["query"]
KeyError: 'query'
```
題庫檔案形狀不對(頂層是陣列而不是物件)也是同樣裸炸:
```
$ echo '["斑馬","條紋"]' > pool_list.json
$ python3 .../retrieval_eval_multiword.py --pool pool_list.json --vault vault --rebuild-pool out.json
TypeError: list indices must be integers or slices, not str
```
對照組:同一支檔案裡的 `load_labels()` 對「標註檔形狀不對」處理得很仔細,會印
`ERROR: 標註檔 ... 不是「節點→分數」的對應,讀不下去` 這種清楚訊息並乾淨結束
(`SystemExit`)。`contaminated()` 明明是同一批改動、同樣面對「使用者手改 JSON 可能改壞」
的情境,卻完全沒有比照辦理——這是新增程式碼自己就沒做到自己另一半程式碼定下的標準。

severity: major
blocking: 是

---

## 2. 查詢字串拆詞後變空(全空白)時,`rebuild_pool` 崩潰

引句:「sc[k] = min(cs)」

`cooccur_top(terms)` 裡:
```python
cs = [v.count(t) for t in terms]
if all(cs):
    sc[k] = min(cs)
```
當 `terms = q.split()` 因為查詢是空白字串而變成空清單 `[]` 時,`cs = []`。
Python 的 `all([])` 對空清單回傳 `True`(空集合上的全稱命題恆真),所以
`if all(cs):` 誤判成「每個詞都有出現」,接著 `min([])` 直接丟 `ValueError`。

實測(查詢是三個全形空白):
```
$ python3 -c "import json; json.dump({'M01': {'query': '   ', 'pool': []}}, open('pool_ws_q.json','w'))"
$ python3 .../retrieval_eval_multiword.py --pool pool_ws_q.json --vault vault --rebuild-pool out.json
Traceback (most recent call last):
  File ".../retrieval_eval_multiword.py", line 150, in rebuild_pool
    s3 = cooccur_top(terms)
  File ".../retrieval_eval_multiword.py", line 141, in cooccur_top
    sc[k] = min(cs)
ValueError: min() iterable argument is empty
```
(空字串 `""` 不會走到這裡,因為 `""` 是任何字串的子字串,會先被污染守衛擋下——
但純空白 / 全形空白字串不是任何一篇筆記的逐字子字串,能繞過污染守衛,一路撞進這裡。)
題庫檔案一旦有人手殘打成空白或斷詞後整個吃空,`--rebuild-pool` 直接壞掉。

severity: major
blocking: 是

---

## 3. 「先寫暫存再換名」的暫存檔名不含 PID,同一輸出路徑被兩份同時寫會互撞

引句:「tmp = path.with_suffix(path.suffix + ".tmp")」

`write_json_atomic` 的暫存檔名只由目標路徑決定(`<目標>.tmp`),沒有 PID / uuid /
`tempfile` 這類唯一化。docstring 宣稱「中途中斷不會在樹上留下半份檔」,但這個保證只在
「同時只有一份行程在寫同一個目標」時成立。

實測(兩個行程各自寫暫存、再各自換名,模擬真實的時間差):
```
$ python3 race_harness.py A out.json 2   &   # 先寫入 tmp,睡 2 秒才 replace
$ sleep 0.5
$ python3 race_harness.py B out.json 0.2 &   # 較晚寫入 tmp(蓋掉 A 的暫存內容)、較快 replace
$ wait
B replaced
Traceback (most recent call last):
  File "race_harness.py", line 12, in <module>
    os.replace(tmp, path)
FileNotFoundError: [Errno 2] No such file or directory: '.../race_out.json.tmp' -> '.../race_out.json'
--- 最終內容 ---
{"who": "B", "stage": "first-write"}
```
行程 B 把行程 A 還沒 replace 的暫存檔整個蓋掉,A 之後 `os.replace` 找不到自己的暫存檔,
直接 `FileNotFoundError` 崩潰;而 B 的資料悄悄成為最終結果,A 那一份跑出來的東西整份
消失、沒有任何錯誤訊息說「你的結果被別人蓋掉了」。這正是原始需求文件裡明講「這套評測
出過非 UTF-8 中斷那類事故」同一等級的風險——會在兩個人同時重組候選池,或同一份
CI/排程重疊跑的時候發生,而且是最壞的一種:一邊裸崩潰,一邊悄悄吃掉別人的結果。

severity: major
blocking: 是

---

## 4. `os.replace` 覆蓋既有檔案時,原檔案的權限位元會被換掉

引句:「os.replace(tmp, path)」

`os.replace` 用暫存檔(預設 umask 建立)去換掉目標檔,不會保留目標檔原本的權限。

實測:
```
$ echo '{}' > out_perm.json; chmod 600 out_perm.json
$ ls -la out_perm.json
-rw-------@ 1 enzo  wheel    3 ... out_perm.json
$ python3 .../retrieval_eval_multiword.py --pool pool2.json --vault vault --rebuild-pool out_perm.json
✓ 候選池重組好了:...
$ ls -la out_perm.json
-rw-r--r--@ 1 enzo  wheel  166 ... out_perm.json
```
原本 `600`(僅擁有者可讀寫)的檔案被換成 `644`(所有人可讀),沒有任何提示。
對這支工具目前輸出的內容(候選池)風險不高,但假如 `--rebuild-pool` 指到一份被特意
收緊過權限的檔案,這支工具會悄悄把它鬆綁。

severity: minor
blocking: 否

---

## 5. 寫入中斷(磁碟滿/被砍)會在目錄裡留下孤兒 `.tmp` 檔,且完全沒有診斷訊息

引句:「先寫暫存再換名——中途中斷不會在樹上留下半份檔(改共用檔的家規)。」

用 `ulimit -f 0`(檔案大小上限 0,模擬寫入被系統擋下)重跑 `--rebuild-pool`:
```
$ (ulimit -f 0; python3 .../retrieval_eval_multiword.py --pool pool2.json --vault vault --rebuild-pool out_disk_full2.json); echo rc=$?
rc=153        # 128+25=SIGXFSZ,行程被系統訊號直接殺掉,Python 連例外都來不及印
$ ls -la out_disk_full2.json*
-rw-r--r--@ 1 enzo  wheel  0 ... out_disk_full2.json.tmp
```
目標檔 `out_disk_full2.json` 本身確實沒被動到(這點做對了),但目錄裡多了一個 0 位元組
的 `out_disk_full2.json.tmp`,不會自動清掉,而且整個過程沒印出任何一行訊息——連一句
「寫失敗」都沒有,行程就是安靜地消失、只留下 rc=153 和一顆空殼檔。docstring 講的
「不會在樹上留下半份檔」在這個情境下不成立:半份檔(0 位元組的 `.tmp`)確實留下來了,
只是沒有換到正式檔名而已。

severity: minor
blocking: 否

---

## 6. `load_labels` 宣稱要修「標註值害它拋 TypeError」,但只修了巢狀格式那一種,單純打錯型別(字串)仍然裸崩潰

引句:「餵含各評審意見那份會在算相關數時拿字典去跟數字比大小,直接拋 TypeError,」

這段 docstring 講的正是這次改動要解決的問題——標註值型別不對時,程式應該給清楚錯誤
而不是裸拋 `TypeError`。但 `load_labels` 實際只驗了兩件事:`per_node` 是不是字典、
巢狀格式有沒有 `final` 鍵。除此之外,`v` 到底是不是數字完全沒驗,原封不動塞進
`flat[node] = v`。

實測(標註值被手誤打成字串 "2"/"0" 而不是數字 2/0——這正是「值是字串不是數字」這種
最常見的手改 JSON 失誤):
```
$ cat labels_str.json
{"M01": {"Systems/A.md": "2", "Systems/B.md": "0"}}
$ python3 .../retrieval_eval_multiword.py --labels labels_str.json --pool pool.json --vault vault -k 5
Traceback (most recent call last):
  File ".../retrieval_eval_multiword.py", line 224, in main
    n_rel = sum(1 for v in all_rels if v >= 1)
TypeError: '>=' not supported between instances of 'str' and 'int'
```
這跟這次修的那個 bug 是同一個物種(標註檔型別不對 → 裸拋 TypeError),只是換了一種
更容易手誤踩到的形狀。`load_labels` 的 docstring 讓人以為「標註檔的型別問題」這一類
已經處理掉了,但其實只覆蓋了它動手修的那一種形狀,量測路徑上還是同一種裸崩潰,而且
崩潰點離 `load_labels` 有一段距離(在 `main()` 算 `n_rel` 那裡),不看 traceback
不容易想到是標註檔的問題。

severity: major
blocking: 是

---

## 7. `--vault` 打錯路徑(不存在/是檔案/是空目錄)時,`--rebuild-pool` 照樣印「✓ 成功」,產出一份看起來正常、其實全是 0 候選的池

引句:「print(f"✓ 候選池重組好了:{len(newpool)} 題、共 {tot} 筆候選 → {a.rebuild_pool}")」

`contaminated()` 和 `rebuild_pool()` 讀語料都是 `vp.rglob("*.md")`,路徑不存在、
或指到一個檔案而不是目錄時,`rglob` 就是安靜地回傳空結果,不丟例外。於是整條路徑
一路綠燈跑到底,最後印出「✓ 候選池重組好了」。

實測(vault 路徑根本不存在):
```
$ python3 .../retrieval_eval_multiword.py --pool pool2.json --vault no_such_vault_dir --rebuild-pool out_novault.json
✓ 候選池重組好了:1 題、共 0 筆候選 → out_novault.json
  M01 斑馬 條紋 計數             池   0 筆(拆詞臂前10 0、逐詞前3 0、三詞同篇前10 0)
rc=0
```
`--vault` 打成一個檔案(不是目錄)也是一樣的「✓ 成功、0 筆」。

這正是需求裡點名的最壞情況:「不是清楚報錯,也不是拋看不懂的例外,而是安靜地產出一份
錯的東西」。而且這支工具的核心賣點就是「污染守衛」——專門防「查得到但不報錯、數字
看起來正常其實是假的」這一類問題;同一支檔案裡卻沒有對「語料來源本身就是空的/打錯路徑」
做一樣等級的把關。10 題全部印出「池 0 筆」時人可能會注意到,但如果只是 vault 快照的
子目錄被搬動、只影響其中幾題,產出的檔案會是「多數題正常、少數題悄悄變 0」,跟污染守衛
要防的那種「看起來正常其實是假的」是同一種風險。

severity: major
blocking: 是

---

## 造過的其他壞輸入(沒問題,列出來備查)

- 語料目錄裡放非 UTF-8 位元組檔(`Systems/Bad.md` 塞入 `\xff\xfe` 開頭的壞位元組):
  `contaminated()`/`rebuild_pool()` 用 `errors="replace"` 讀,沒有崩潰、正常略過亂碼那篇。
  這點做對了,也確實接住了 repo 記憶裡提到的「非 UTF-8 中斷」那一類事故(這支工具本身
  沒有重演)。
- 語料目錄裡放符號連結繞回自己(`Systems/loop -> vault_symloop`):本機 Python 版本的
  `Path.rglob` 沒有跟進符號連結目錄遞迴,20 秒內正常跑完,沒有卡死或無窮遞迴。
- 標註值超出 0/1/2 範圍(999、-5):不會崩潰,但也完全不驗證,999 會被當成「非常相關」
  直接吃進 nDCG/MRR 計算——這比較像資料品質問題,沒有明顯的「錯的行為」,故沒有另開一條。
- 極長查詢字串(3500 字):不會崩潰,只是印出來的那一行極醜(單行洗版),不影響正確性。
- 全形空白分隔的多詞查詢(`斑馬　條紋　計數`):Python `str.split()` 把全形空白視為
  空白字元,拆詞結果跟半形空白一樣,沒有問題。
- `--pool` 有給、`--vault` 沒給(或反過來):被 `argparse` 的 `required=True` 擋在最前面,
  不會跑到新程式碼。
- 同時給 `--labels` 與 `--rebuild-pool`:`--rebuild-pool` 分支較早 `return`,`--labels`
  被無聲忽略——但 `--rebuild-pool` 的 help 文字本來就寫明「★不量測、不碰標註★」,
  行為與文件一致,不算 bug。
