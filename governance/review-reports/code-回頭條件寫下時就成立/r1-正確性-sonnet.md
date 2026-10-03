severity: major

## F1 工作目錄模式:沒提交的重複行被標成「寫下時就已成立」(判錯方向)
severity: major
blocking: 是
引句:「n = sum(1 for _no, _t, pr in extract(tx)[0] if tuple(pr["conds"]) == conds)」
引句:「sha, why = hist[f["path"]].birth(conds, f["kind"])」
佐證: `scripts/lumos:32101`(`_probe_lines`,只抽條件行,不看現在這份是不是只有一行)

具體失敗場景:
1. 已提交的 Pay.md 有一行 `REVISIT:[when-file:src/a.py][by:2099-12-31] one`,a.py 在,條件已成立。
2. 工作目錄再加一行同條件但還沒提交的 `... two uncommitted`。
3. `lumos drift scan --json`(disk 模式):`_drift_born_conds` 從工作目錄文字拿到兩行都是同一組條件;`birth()` 只數 HEAD 那一版的行數(n==1,不是 >1),所以兩行都往前走到同一個舊提交。
4. 實測輸出:第 16 行與第 17 行的 born 都是 `{'state': 'true', 'commit': '2ac70c7a…'}`。第 17 行是剛寫、沒提交的,卻被說成「在 2ac70c7 進主線、第一次出現在這篇時就成立」。正確結果是 unknown「還沒提交(推送時會判)」,也違反計劃做法 4(現在這一行的條件組不在 HEAD 版裡 → 判不了)。
5. 根因:disk 模式從沒拿「現在這份」去比「HEAD 那一版」同組條件的行數;只有 `--at` 模式因為 i=0 那版就是現在這份才碰巧守住。
6. 測試沒釘到:`t_drift_born_unknown` 的「還沒提交」只用整篇新筆記(`why == "歷史查不到這篇"` 那條路),沒有「已提交的筆記裡加一行同條件」。

最小重現:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/probe1.py`(`python3.14 probe1.py` 於 rw 目錄,看 "disk dup:" 那行)。
修法方向:disk 模式下,把現在這份(tenv)同組條件的行數也算進去,不等於 HEAD 版行數就判不了。

## F2 中間某版那行壞掉(解析不到)再修好:訊息說「第一次出現在這篇時就成立」但其實不是
severity: minor
blocking: 否
引句:「"第一次出現在這篇時就成立——它從寫下就沒在等任何事;改成真的會發生的條件,或刪掉")」
佐證: 計劃〈天花板〉只列了「刪掉再寫回」,沒講「改壞再修」。

具體失敗場景(已實測):
1. 提交 w0 寫下條件(a.py 不存在,不成立);下一提交把 `REVISIT:` 改成 `REVISIT `(解析不到);再加 a.py;最後把行修回原樣。
2. `birth()` 走到「壞掉那一版」n==0 就停,born 取修好那一版(cfc6d7b),在該版 a.py 已在 → `state: true`。
3. 輸出說「第一次出現在這篇時就成立、從寫下就沒在等任何事」,但這條在 w0 寫下時不成立、確實等過事。誤標方向同 F1,但屬計劃「這一世」的設計取捨,只是訊息措辭比事實強;措辭改成「這一世的開頭」即可。⚠ 是否算設計內,由裁決者定。

## 圖譜固定席
- 派工尾端沒有附固定席筆記(LUMOS-IMPACT 只有範圍);自查這次改動牽連的 `Systems/存量漂移守衛`、`Systems/筆記內容審`:兩篇都沒有 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 合約行,diff 不破壞其宣稱的行為。
- `_note_status_seq` 改用 `_note_versions`:非複製情況下與舊版等價(新舊解析對 M/R 都取新路徑;舊解析在不帶 --first-parent 的合併提交會把下一個 sha 當路徑,新解析略過,屬修正)。複製(C)那一種是計劃宣告的行為變更。
- scan 是讀指令、不寫治理帳(lumos-cli-read d1):`_drift_born_annotate` 只讀 git,沒有寫帳;不影響。
- 同篇多條共用 `_DriftBornHistory` 快取:`texts`/`pairs` 只增不改,多條互不污染;只有 `self.err` 共用,但每次回 False 前都會重設。

## 本案特定鏡頭 4(解析與走訪)
- `_git_log_sha_status_paths`:實跑 `git log --follow --first-parent --format=%H --name-status -z`,格式為 `sha\0\nM\0path\0` / `sha\0\nR100\0old\0new\0` / `C100\0old\0new\0`,解析取 R、C 的新路徑正確;沒有檔案列的提交被略過;路徑 token 都在「狀態位」被 `i += 1+n` 吃掉,不會被當成 40 碼 sha(路徑帶 vault 前綴也不可能整串是 40 碼十六進位)。
- 中間被刪又加回:D 那版 `sha:path` 讀回 None → break,born 是加回那一版(S2 ③ 實測綠)。改名同時改內容(R<100)照跟,路徑用該提交當時的路徑。含 `[`、`*`、中文的檔名實測 born 正常。
- 預算:`--budget 0.0001` 實測 scan 正常結束;`git log --follow` 每篇一次、單次上限固定 20 秒(`_lens_git` 預設),預算剩不到 20 秒時最多多出一次呼叫,未能在小型倉庫重現超時,不列 finding。

## 驗收條款對照
- S1 `t_drift_born_true_scan`:釘住 true/false、commit 等於寫下那版、已表態照印、RULE 撤除條件;綠(22 項全綠)。
- S2 `t_drift_born_identity`:改文字/搬位置/改名、改條件、刪掉再寫回、側分支合併、複製五情境各有斷言,真的釘住條款。
- S3 `t_drift_born_unknown`:兩行同條件、非 UTF-8、淺層、partial、超上限、非 git 都有;**缺口**:「工作目錄裡還沒提交的行」只測整篇新筆記,沒測「已提交筆記裡新增的行」(F1 因此漏過)。
- S4 `t_drift_born_reads_stop_at_boundary`:釘住「最多讀 32 版」;只驗到整批粒度,條款文字「碰到邊界就停」在 chunk 內不會提早停,與計劃一次 32 版的敘述一致。
- S5 `t_note_versions_stop_at_copy`:停在複製、改名照跟、狀態序列不混來源翻轉、解析器合併提交略過都有斷言,釘住。

總結:最高等級 major
