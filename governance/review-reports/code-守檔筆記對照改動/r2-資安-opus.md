severity: minor

# 代碼審 r2 資安-opus(回頭重讀守檔筆記:第 1 輪四條資安修法的繞過測試)

實驗都在 `hcc-r2-work-資安-opus/repo`(對 negguard 的 `git clone --shared`,HEAD 94c1e82f)裡跑:`exp.py` 直接載入 clone 裡的 `scripts/test_lumos.py`,借它的 `_rr_repo`、`_rr_prepare`、`_rr_index_add` 造小專案,工具用 clone 裡的 `scripts/lumos`,以 `/opt/homebrew/bin/python3` 執行,暫存目錄設在自己的工作目錄底下。

## F1 控制字元過濾沒擋 U+2028/U+2029:帶這種字元的筆記路徑照樣寫進要提交的治理帳,之後 `lumos gov` 每次跑都會當掉
severity: minor
blocking: 否
引句:「_NOTE_REREAD_CTRL_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")」
file: `scripts/lumos:27348`(reread-check 的 reminded 事件,nodes 與 note 寫進 `_note_reread_show` 過的路徑;`_esc_clean` 只換 C0、DEL、C1,不動 U+2028)
file: `scripts/lumos:1228`(`_gate_event` 用 `ensure_ascii=False` 寫 JSONL,U+2028 會原樣落盤)
file: `scripts/lumos:7264`(`cmd_gov` 的 load 用 `splitlines()` 切行,`mapper(json.loads(line))` 只接 ValueError/KeyError,切出來的碎片如果是合法 JSON 但不是物件,`d.get` 就丟 AttributeError)
file: `scripts/lumos:9300`(同一份程式另一個讀帳的地方,2026-09-07 已補上「合法 JSON 但不是物件要跳過」,`cmd_gov` 沒補)

1. 第 1 輪 F2 修法的用意是不讓路徑裡的字元打穿「一行一筆」的結構(項目檔頭、終端)。新加的 `_NOTE_REREAD_CTRL_RE` 與 `_note_reread_show` 只涵蓋 C0/DEL/C1。Python 的 `str.splitlines()` 還會在 U+2028(LINE SEPARATOR)和 U+2029 切行,而這兩個字元都不在過濾範圍內。項目檔頭沒事,因為解析檔頭用的 `re.M` 只認 `\n`,實測攻擊不成立,見下方「查過」。出事的是治理帳。
2. 重現:攻擊者在同一段範圍裡提交一篇 `docs/kg-knowledge/Systems/X [1] .md`(內容照抄 A,about_code 寫 src/a.py),同時改 src/a.py。受害者推送時,推送前掛鉤跑 reread-check:
   ```
   gov before: 0
   check rc 0 '回頭重讀提醒:…有 2 篇…\n  docs/kg-knowledge/Systems/X [1] .md  (對照指紋 bbd1ec16ce0a9c9f)…'
   raw log line count(\n): 1  splitlines fragments: ['[1]', '.md"], "note": "沒對照 2 篇、…Systems/X']
   gov after rc 1
     File ".../scripts/lumos", line 7264, in load
       rows.append(mapper(json.loads(line)))
     File ".../scripts/lumos", line 7271, in <lambda>
       load(".governance-log.jsonl", lambda d: {"ts": d.get("ts", ""), ...
   AttributeError: 'list' object has no attribute 'get'
   ```
   用 `\n` 切,這筆事件還是一行;用 `splitlines()` 切,就碎成 7 段,其中 `[1]` 是合法 JSON 但不是物件。
3. `docs/.governance-log.jsonl` 是要提交的簿記檔。這一行一旦跟著下一次帳本提交進版控,拉到它的每一份 clone 跑 `lumos gov`(含 `--stats`、`--nags`)都會 traceback,要手修帳本才會好。同一招在 reread-record 的事件也成立(它的 nodes 直接寫項目檔頭的「筆記路徑」)。改修之前的 94e28375 也一樣會寫原樣路徑,所以這是第 1 輪修法沒掃乾淨的同族問題,不是這次新開的洞。`gov` 是唯讀報表,不在推送路徑上,所以定 minor。
4. 修法(二選一或都做):`_NOTE_REREAD_CTRL_RE`(或 `_esc_clean`)把 `  ` 也算進去;`cmd_gov` 的 load 比照 9300 行補 `isinstance(d, dict)`。其他把使用者可控路徑寫進 nodes 的閘也是同一族,可以一起看。

## 查過、沒有洞的部分(不算 finding)
- **符號連結換一層放**:在真的 `.lumos/note-audit/` 資料夾裡預先提交兩個符號連結,一個是算好名字的項目檔 `reread-8e2b0f51ce720f42-claude.md`,指到 repo 外的 victim.txt,另一個是 `.gitignore`,指到 repo 外一個還不存在的路徑(ls-tree 看到兩筆 120000)。跑 prepare 的結果是 rc0,victim.txt 內容仍是 ORIGINAL,repo 外沒多出檔案;工作目錄裡那兩個連結被換成一般檔。原因是 `_write_lf` 走「暫存檔再 os.replace」,換掉的是連結本身,不會順著連結寫出去;清檔也跳過連結。`.lumos` 或 `.lumos/note-audit` 本身是連結的情況,新測試已經涵蓋。
- **硬連結**:git 沒辦法提交硬連結。本機手動把 `.lumos/note-audit/old.md` 硬連結到 repo 外一個 30 天前的 diary.md,prepare 清掉的只是這一個連結,repo 外的 diary.md 還在、內容也沒變。
- **競態**(檢查之後才換成連結):另開一條執行緒不停把 `.lumos/note-audit` 在真資料夾與「指到 repo 外的連結」之間切換,同時連跑 60 次 prepare。rc 分布是 0:45、1:11、2:4。repo 外 200 支 30 天前的 .md 一支都沒被刪,但多了 `.gitignore` 與一份項目檔,可見從檢查到寫檔之間的空檔確實存在。不過要利用它,得有另一個本機程序在那幾毫秒內動你的工作目錄;這樣的程序本來就能直接刪檔,提交連結這種攻擊方式做不到這件事,所以不列。
- **Unicode 控制字元與項目檔頭**:筆記名 `E 對照指紋: <B 的指紋> Z.md` 讓 prepare 產出一份檔頭。解析結果是那篇自己的對照指紋 201a8ffa07812171,不是 B 的 18055c7b660a769d,因為 `re.M` 只在 `\n` 切行,偽造不成立。U+0085(NEL)在 C1 範圍內,會被跳過並印出一句說明。U+202E(雙向覆寫)會原樣進終端,只是顯示上的障眼法:工具產的項目檔與派工都照真實路徑走,沒有錯的行為。
- **簿記豁免(`_codeloop_record_valid`)**:以下幾種都判失效,符合預期:搬進簿記資料夾同時把副檔名改成 `.JSON`;改名成 `.PY`;去掉副檔名;把程式檔換成指向簿記資料夾的符號連結;只改程式檔權限;本機設了 `diff.renames=copies` 再 mv;本機設了 `diff.relative=true` 再改程式。原因是 `--no-renames` 讓被搬走的舊路徑一定會出現在清單裡。仍然判有效的只有兩種:在簿記資料夾裡**新增** `.PY`、無副檔名的腳本,以及在簿記資料夾裡放 gitlink(子模組)。這兩種都沒有動到簿記資料夾外的任何檔,而 repo 裡也沒有東西會執行簿記資料夾裡的檔。本 repo 那幾個簿記資料夾裡現有的檔都不是程式副檔名,所以新規則不會讓既有的帳本提交失效。
- **連結成子模組**:把 `.lumos/note-audit` 或 `governance/reread-verdicts` 提交成 gitlink,checkout 出來是空的真資料夾,守衛照常放行,也寫不出 repo。
- **另一條「沒讀過卻算已對照」的路**:check 只比對已提交紀錄的檔名。範圍內的提交者直接提交一個 `governance/reread-verdicts/<B 的指紋>-<時間>-<32 位十六進位>.json`,就能讓 B 被算成已對照。這是計劃刻意的設計(只讀檔名、只提醒不擋、信任提交者),不是 F2 修法有錯,所以不列。

最高等級:minor
