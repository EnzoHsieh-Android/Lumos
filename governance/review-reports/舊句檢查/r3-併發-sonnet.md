severity: minor

# r3 併發與資源鏡頭(併發-sonnet)

量測環境:`git clone --shared /Users/enzo/rtb-mainwt`(rtb,666 提交、2756 檔、275 支 .py)與 clone-ns(工具鏈,588 篇圖譜);直譯器 3.14.6;腳本在 `os-r3/w/`(m.py、rx.py、real.py、e2e.py、wr.py),全程唯讀。

## 量測摘要(供各 finding 引用)

- **m1 端到端冷快取**(用既有 `_drift_list`/`_nodehome_cat_blobs`/`_drift_py_names` 照 spec 順序模擬:列檔、diff、批次讀改到的檔、剖兩版、再批次讀並剖整個終點語料):rtb 範圍 30 提交 6.7 秒、範圍 300 提交(2515 檔動、254 支程式 .py)7.4 秒;工具鏈範圍 30 提交 6.3 秒、範圍 300 提交 5.9 秒。git 部分(ls-tree、diff、cat-file)全部加起來不到 0.3 秒,時間幾乎全是 `ast.parse`。離 30 秒預算有 4 倍餘裕,粗候選先算、冷快取都不構成 blocking。
- 讀圖譜:`_drift_tree_env` rtb 0.07 秒、工具鏈 0.14 秒(588 篇);spec 說「多讀一次算在 30 秒裡」成立,可忽略。
- 掃筆記的一條交替正則(照 spec 的 ASCII 邊界寫法,全部名稱都通過名稱先篩、逐行 search):
  - 真實名稱:刪整支 `scripts/test_lumos.py`(候選 1577、先篩後 1008 個)掃工具鏈圖譜 6.0 秒;刪整支 `scripts/lumos`(1128 → 526)2.6 秒,跟 r2 的數字對得上。
  - 名稱全是圖譜詞彙拼出來、每個都過先篩的合成集合:工具鏈圖譜 200 個 1.1 秒、500 個 2.6 秒、1000 個 5.1 秒、2000 個 16.9 秒;rtb 圖譜 2000 個 5.2 秒。2000 之後明顯超線性(每筆名稱多出來的分支讓每個位置都多試一輪)。
- 治理帳寫入:`_gate_event` 是 `open("a")` 加一次 `f.write`。在 3.14.6 用會計數的 FileIO 替身實測,單行 2 KB、9 KB、20 KB、140 KB、300 KB 都只有 1 次 `write(2)`(3.14 的 `io.DEFAULT_BUFFER_SIZE` 是 131072,不是 spec 寫的 8 KB)。所以並行追加不交錯這件事在 4 KB 以上也成立,4 KB 是政策值不是原子性的邊界。
- 工具鏈治理帳現在 14,700,626 位元組,跟 spec 說的 14.7 MB 一致。

## 逐項答覆(使用者指名的鏡頭)

- 快取放 `~/.cache/lumos/drift-defs/`、多 repo 與多工作樹共用:鍵是 sha256(blob 編號|schema|py 主次版),值只由 blob 內容決定,跨 repo、跨工作樹共用正確;每個 blob 一支檔加 `mkstemp` 唯一暫存名加 `os.replace`,兩個推送同時寫同一支內容相同,不壞;`_lens_cache_read` 讀端驗擁有者與 group/other 不可寫我核對過與 spec 描述一致。已讀,無 blocking。
- 14 天淘汰:`_note_audit_work_dir` 的清舊檔是 `try: stat/unlink; except OSError: pass`,兩個行程同時刪同一支不會丟例外;`mkstemp` 暫存檔 mtime 是新的,不會被誤刪;「讀不更新 mtime」造成同一批一起寫的檔同一天一起到期(每 14 天一次冷跑,工具鏈 6 秒、rtb 7 秒),可接受。已讀,無 blocking。
- 兩個推送同時寫、一次推送兩筆帳、一行 4 KB:見 F1、F2、F5、F6。
- m1 自己 30 秒與粗候選先算:見上面量測摘要與 F3、F4,冷快取最壞 7.4 秒。
- ★INVARIANT★ 逐條:`Systems/guard-kill` 兩條(rc 優先序、`--json` stdout 純度)只管 `lumos guard kill`,m1 不碰,不影響;`Systems/reversibility-governance-ledger` 的合約行只是 INVARIANT_RE 形狀的一致性(平行路),m1 不新增合約行也不改那支掃描,不影響;`Systems/lumos-cli-write` 這個 clone 裡沒有 ★INVARIANT★ 行(grep 為空)。

## F1 帳一行 4 KB 的丟法接不到全部欄位,而且誰來量沒寫
severity: minor
blocking: 否
引句:「還超過 4 KB 就先從只列出、再從要處理尾端丟」
file: `scripts/lumos:1147`
file: `scripts/lumos:15825`
1. `_gate_event` 自己組事件:`note` 同時寫成 `detail`(整句結論寫兩次)、加 `ts`、`commit`、`hard`、`nodes`,呼叫端只傳 `extra`,看不到最後那一行多長。spec 沒寫「整行」由誰量、怎麼量;照字面只量 `extra` 的實作會漏掉 `note` 的雙份與 `nodes`。
2. `nodes` 最多 50 個(要處理那幾篇)、中文路徑每個約 45 至 65 位元組,單獨就是 2.3 至 3.3 KB,再加基礎欄位約 0.8 KB,rows 全丟光都可能還在 4 KB 上下;spec 的丟法只丟 rows,`nodes` 與 `oversize_paths` 不在丟的範圍裡,也沒寫丟光後還超過怎麼辦(迴圈終止條件未定義)。
3. 因為上面實測 3.14 單次寫到 300 KB 都是一個 `write(2)`,超過 4 KB 不會交錯,後果只是「rows 白丟或行比預期長」,所以判 minor。
4. 建議:兩處擇一寫明——(a) 把「事件最終長度」交給共用的建事件函式回報,超過就先丟 rows、再截 `nodes` 到前 N 個;(b) 直接把上限改成 8 KB 並寫明依據是「3.14 單次寫入不交錯」。順帶把〈做法〉裡「Python 預設 8 KB 緩衝」改成實測值,免得日後讀的人以為 8 KB 是硬界線。

## F2 「同一次推送 c1–c5 與 m1 都擋會算兩次」在 gov 的去重之後不成立
severity: minor
blocking: 否
引句:「算兩次是照實記,不併成一筆」
file: `scripts/lumos:7307`
file: `scripts/lumos:28296`
1. `cmd_gov` 讀 `.governance-log.jsonl` 後用 `(commit, frozenset(nodes), gate, kind, token)` 去重;帳裡的 `token` 只有 canary blocked 與 code-loop dispositions 才有值,drift-check 的事件 token 恆為空。
2. core 的 blocked 事件 `nodes` = 要處理那幾篇(`_drift_report_must`,`sorted({f["path"][:-3] …})`),`m1` 的 blocked 事件 `nodes` 也是要處理那幾篇。同一篇筆記同時被 c 類與 `m1` 列成要處理(例:一篇 Systems 摘要既有壞的回頭條件、又提到消失的名稱),或兩邊都只有「判不了」(`nodes` 都是空集合),兩筆的鍵完全相同,`gov`、`gov --stats` 的計數折成一筆。
3. 所以 spec 這句「照實記」只對原始帳成立,對 `gov` 的統計不成立;RETIRE-IF 與〈做法〉4 都直接 grep 原始帳(`"check": "old-sentence"`),量準度不受影響,所以不是 blocking。
4. 建議:二選一——`m1` 事件加 `token`(例:`old-sentence`),並把 `_gov` 的 token 對映補一行;或把這句改成「gov 統計可能把同一提交、同一組筆記的 c 類與 m1 事件折成一筆,量 m1 一律讀原始帳」。另外 `--nags` 的 `(gate, node)` 也不分 c 類與 `m1`,同一篇 14 天內一次 c 類提醒加一次 `m1` 提醒會被算成「連續喊」,一併寫進同一句。

## F3 「程式檔批次讀 0–1」跟「先算粗候選、再剖語料」的寫死順序對不起來
severity: minor
blocking: 否
引句:「程式檔批次讀 0–1、讀筆記 2」
file: `scripts/lumos:23981`
1. 〈做法〉1 的讀取段說沒命中的與沒副檔名的「全部放進同一次 `_nodehome_cat_blobs`」,行程數寫「程式檔批次讀 0–1」;但〈做法〉3 把順序寫死:先只剖改到的檔兩版算粗候選,粗候選非空才去取終點整個語料。要不要讀語料的那批要等粗候選算完才知道,所以有粗候選的推送必然是兩次批次讀(改到的檔一次、語料沒命中與剖不動檔的文字比對一次),上限是 2 不是 1。
2. S5 只比「改到 3 支與 30 支 `.py` 時 git 呼叫次數一樣」與「全命中是 0 次」,兩次也過得了測試,所以不會翻紅,但〈做法〉的計數與 S5 的敘述給實作者的是兩個數字。
3. 另一個資源面的點:`_nodehome_cat_blobs` 把整個 `cat-file --batch` 的 stdout 收進記憶體、再切成 bytes 串列(約兩份),而 4 MB 上限是讀進來之後才判的。冷快取的大 repo 一次讀進所有沒命中的 .py(100 MB 量級就是 200 MB 上下的原始碼記憶體),且「時間到之前剖好的留著」意味著沒剖完的部分下一次又整批讀一次。既有 `_nodehome_cat_blobs_capped` 可以先用 `--batch-check` 問大小。這不是現況風險(rtb 冷讀 0.06 秒、原始碼 8 MB),⚠ 只在誠實界線補一句「批次讀不設上限,量級 100 MB 以內」並給重量條件。
4. 建議:行程數改寫成「程式檔批次讀 0–2(改到的檔一次、語料沒命中一次)」,S5 的計數斷言同步寫成上限 2。

## F4 定義快取的 schema 靠人記得加一,沒有機械守衛
severity: minor
blocking: 否
引句:「抽法任何一次改動就把 `_DRIFT_M1_DEFS_SCHEMA` 加一」
1. r1 併發席 F2 要的是「抽法改了舊快取要失效」,這一版折成 schema 常數加 S5 測「常數改了就不命中」;但沒有任何測試在抽法(`_drift_py_names(m1=True)`)行為變了而常數沒加時翻紅。漏加的後果是舊快取被當現況,「名稱還定義著」被錯放或錯報,最長持續一個 TTL(14 天),且看起來像正常輸出、沒有錯誤訊息。
2. 專案偏好機械守衛(記憶「寧可機械擋」「散落同步要守衛」)。建議 S5 補一支:用固定的一組輸入檔(模組層指派、拆包、旗標各一)算 `_drift_py_names(txt, m1=True)` 的輸出雜湊,釘在測試裡,並在測試訊息寫「這個雜湊變了就要把 `_DRIFT_M1_DEFS_SCHEMA` 加一」。

## F5 快取的併發宣稱與「快取是不是真的在用」都沒有被釘住或觀測
severity: minor
blocking: 否
引句:「兩個推送同時寫同一支,內容相同、後替換的贏,不壞也不丟」
1. 〈做法〉與〈實務隱患〉都拿「暫存名唯一加 `os.replace`」擋住併發寫,S5 一個條款也沒有兩個行程同時寫、或寫的同時另一個行程清舊檔的案例;既有 r1 已在同 repo 找到固定暫存名被互搶的前例(`_write_lf`)。至少要有一個把 `mkstemp` 換成固定名就翻紅的測試(例:兩個執行緒同時寫同鍵、讀回不是壞 JSON;或斷言目錄裡沒有殘留的 `.tmp`)。
2. `_trusted_private_dir` 要求 `~/.cache`、`~/.cache/lumos` 整條路徑都不是 symlink(家目錄本身除外)。用 dotfiles 管理員把 `~/.cache` 連到別處的機器,快取會靜默整個關掉,S5 寫的「快取目錄不可信…當沒有快取照常跑」正是這條路。此時每次推送都是冷跑(工具鏈約 6 秒、rtb 約 7 秒),沒有任何訊號告訴人;帳裡也沒有 hit、miss、off 的欄位,兩週後量到 timeout 偏高時分不出是 repo 真的大還是快取沒開。
3. 建議:治理帳加兩個整數欄位 `parsed`(這次實際剖了幾支)與 `cache_hits`,快取整個不可用時 `cache_hits` 記 null;REVISIT 那天用它們把「時間到」分成「大」與「沒快取」兩類。

## F6 效能數字的適用範圍
severity: minor
blocking: 否
引句:「合成 2 萬個名稱:不先篩 119.3 秒、先篩 2.6 秒」
1. 那兩個 2.6 秒是「名稱全都不在圖譜詞彙裡、先篩後幾乎沒剩」的情形。名稱全是圖譜詞彙拼出來、每個都過先篩的合成集合,我量到 1000 個 5.1 秒、2000 個 16.9 秒(工具鏈圖譜)、3000 個上下就撞 30 秒。真實名稱刪整支 `scripts/test_lumos.py`(先篩後 1008 個)是 6.0 秒,離門檻還遠,所以現況沒問題;但〈做法〉2 與 r2 那段「先篩讓最壞情況 2.6 秒」讀起來是上界,實際上界是「過先篩的名稱數」而不是「先篩前的名稱數」。
2. 「有快取後約 0.3 秒」(〈實務隱患〉效能)只在推送沒動到大檔時成立:每次改到 `scripts/lumos`(2.2 MB)的推送,終點那一版是新 blob、必然沒快取,剖一次約 1 秒;工具鏈最常見的推送正是這種。仍遠低於 30 秒,只是數字要改成「動到大檔時再加約 0.3 秒/MB」。
3. 建議:把這兩處改成「上限看過先篩的名稱數,實測約 3000 個過 30 秒;動到大檔的推送即使快取全熱也要剖新 blob」;不需改設計。(名稱過多可以改成「一般識別字那組用 ASCII 詞集合逐詞查表、旗標與路徑那組才用正則」,結果與整字正則相同、成本線性;這是選配,不列 blocking。)

## F7 治理帳 Issue 已在等「新的寫入者」清單,這份計劃沒去登記
severity: minor
blocking: 否
引句:「一行在 Python 預設 8 KB 緩衝內會一次寫出,兩個推送同時追加才不會交錯」
file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md`
1. 那篇 Issue(status: open,REVISIT 2026-10-11)明寫「寫帳頻率會變高的計劃要算成受影響的使用者」,並已把存量漂移守衛的兩個寫入者列進去。`m1` 是新增一條「每次有程式改動的推送必寫一筆」的常態寫入,寫帳頻率比 c 類(只有要處理才寫)高得多,卻沒有回頭登記,Issue 的 10-11 回頭看時會漏算。
2. 本計劃〈併發〉只論快取,沒提到帳的並行;上面實測支持「單行單次寫入、不交錯」的結論,但那是 `open("a")` 這條路的實務行為,不是規格保證(Issue 也這樣寫),應該在 `related` 或〈實務隱患〉帳的體積段補一句連到那篇 Issue。

已讀,無 finding 的節:〈範圍〉、〈做法〉2 各小節(整字、撤除節、句內字眼、分層)、〈做法〉4、〈與參考實作的刻意差異〉、〈條款〉S1–S4、S7–S17、〈回退〉。這些節沒有併發或資源面的具體失敗場景。

最高等級:minor;blocking 共 0 條
