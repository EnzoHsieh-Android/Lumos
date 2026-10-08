severity: major

審查範圍:/tmp/code-born-r2.patch 全部 hunk;scripts/lumos 真碼對照;在 /tmp/born-r2-work 另開臨時 repo 與複製的 scripts(sc1 還原終點重複檢查、sc2 還原措辭、sc3 還原停在複製)實測,沒動 repo。
走過的輸入:歷史 31/32/33/64/65 版(跨 32 版批次邊界)、恰好 6/7/8 個不同寫下提交(工作目錄與 --at HEAD)、改名未提交、刪掉再建、側分支合併、--at 舊提交、--budget 極小、空/怪文字餵 _probe_lines/_retire_lines(不丟例外)、簽章提交加 log.showSignature。拆分前後控制流(提早 return、預算/上限計數、旗標)逐行對過,沒找到不等價處。

## F1 設了 log.showSignature 時,簽章提交的檔案列會被記到上一個提交名下,寫下那一版追錯、把寫下時不成立的說成「寫下時就已成立」
severity: major
blocking: 是
引句:「toks = [t.strip("\n") for t in raw.decode("utf-8", errors="surrogateescape").split("\0")]」
引句:「d = _lens_git(ctx["root"], "show", "-s", "--format=%cs", sha)」
佐證: `scripts/lumos:40407`(_lens_git 不加任何簽章旗標,_ns_git 走同一支)
佐證: `scripts/lumos:29995`(_note_versions 的 git log 沒有 --no-show-signature)
失敗場景:
1. 使用者本機 `log.showSignature=true`(簽章提交的人常設),歷史裡有已簽章的提交。git 在 `--format=%H -z` 的輸出前面塞 `gpg: Signature made…` 幾行(我實測確認走 stdout),那個提交的編號 token 變成「gpg 文字加換行加編號」。
2. `_git_log_sha_status_paths` 對這個 token 做 `_LENS_SHA_RE.fullmatch` 失敗;此時 `cur` 還是上一個(較新的、沒簽章的)提交,接著的 `M`、路徑 token 就以 `(上一個提交編號, 簽章提交那時的路徑, "M")` 收進去。結果簽章提交整個消失,上一個提交重複出現一次。
3. `_DriftBornHistory.birth` 往回走:重複的那一筆內容一樣、仍有這行,再往下是更舊且沒有這行的版本就停,寫下那一版變成「較新的那個提交」而不是真正寫下它的簽章提交。若真正寫下那一版條件不成立、較新那一版才成立(例如簽章提交先寫 REVISIT、下一個提交才補上 src/a.py),輸出變成 state=true,正是計劃說最糟的「標錯」。
4. 同一個設定下,`show -s --format=%cs` 的 stdout 前面也帶 gpg 幾行,`d.stdout.strip()` 整串進 `born.date`,文字輸出那一行被劈成多行(`起連續出現在這篇` 前面括號裡塞進 gpg 訊息)。
5. `_note_status_seq`(舊呼叫端)共用同一支解析,簽章提交同樣被吃掉或記到別人名下(舊解析是靜默丟掉,新解析是錯記)。
最小重現(腳本 /tmp/born-r2-work/e6.py,先 `GNUPGHOME=/tmp/born-r2-work/gh` 的測試金鑰已建):
```
without showSignature: ('false', True)      # 寫下那一版=簽章提交 S,條件當時不成立
with showSignature: {'state': 'true', 'commit': '8715c0c…(= P,不是 S)', 'date': '2026-10-03', 'why': None}
```
另單獨驗證日期:`git -C /tmp/born-r2-work/sig show -s --format=%cs HEAD 2>/dev/null` 輸出 5 行(4 行 gpg 加日期)。
前提誠實講:需要使用者本機設 log.showSignature=true 且有簽章提交;CI 乾淨環境不會中。修法一個旗標(`--no-show-signature` 或 `-c log.showSignature=false`)加在 _note_versions 與取日期那兩個 git 呼叫;更保險是解析時 token 不是編號就把整個提交判不了,而不是沿用上一個 cur。

## F2 t_note_versions_stop_at_copy 沒有「現場成立」的前置斷言(測試假綠形態)
severity: minor
blocking: 否
引句:「check("①版本清單停在複製那一版", [s_ for s_, _q in vs] == [cp], vs)」
佐證: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`(★INVARIANT★ 還原翻紅釘須配前置斷言)
佐證: `scripts/test_lumos.py` 的 t_drift_born_identity ⑤ 有「前提:git 把 T 認成從 Pay2 複製來」,同一支修法的另一根釘有,這根沒有
失敗場景:
1. 這支測試靠 git 把 B_計劃 認成 A_計劃 的複製;①②③ 的期望值(`[cp]`、`[None,"done"]`、`len(vs)==2`)在「git 根本沒認出複製」的環境(相似度門檻、不同 git 版本、內容被改短)下一樣成立,`break` 那一段完全沒被走到,測試照樣綠。
2. 我實測在這台(git 2.43)把 `if st == "C": break` 拿掉,①②③ 都翻紅,所以現場此刻成立;缺的是把「現場成立」釘成斷言,讓環境不同時翻成「前提不成立」而不是靜默綠。
最小重現:在 t_note_versions_stop_at_copy 補 `_nh_git(root,"log","--follow","--format=","--name-status","-1","--",bp)` 看輸出開頭是否 C,與 identity ⑤ 同形;目前沒有。

## 圖譜鏡頭:固定席逐條判定
- Systems/lumos-cli-read(d1 讀指令不寫治理帳):新增的 _drift_born_* 只呼叫 git log/show/cat-file 與讀工作目錄,沒有任何 _append_governance_log 或寫檔,drift scan 仍不寫帳;不影響。search 排除 superseded 的合約與這份 diff 無關。
- Systems/bound-tests-gate:code-loop check 對固定席合約綁的測試真跑;diff 沒動任何綁定測試的名稱,新測試 t_drift_born_*、t_note_versions_stop_at_copy 是新增;`-k drift_born` 5 支、`-k note_versions` 全綠(本輪實跑);不影響。注意 governance/anchor-baseline.json 的 test_lumos.py 雜湊已隨測試檔更新,note 有寫原因。
- Systems/guard-kill:guard kill rc 優先序與 --json 一行 JSON 的合約:diff 不碰 guard kill;drift scan --json 仍是單一 JSON 物件(只多 findings[].born);不影響。
- Systems/授權與歸屬:diff 沒動 scripts/lumos 檔頭的 SPDX 與 MIT 全文,也沒新增 vendored 授權檔;不影響。
- Systems/測試假綠形態:見 F2;另 t_drift_born_true_scan(④前提)、t_drift_born_identity(⑤前提)、t_drift_born_unknown(各子情境直接斷言 why 字樣)有現場前提,還原終點重複檢查與還原措辭兩處我實測各自翻紅(sc1:t_drift_born_unknown ①工作目錄兩行;sc2:t_drift_born_true_scan ①措辭);唯獨 t_note_versions_stop_at_copy 缺。
- Systems/lumos-cli-lifecycle:re-inject sentinel 合約與這份 diff 無關;不影響。
- Systems/design-loop:處置閘第五步(審材須為 .md 計劃)與這份 diff 無關;計劃檔本身是 .md;不影響。
- Systems/pitfalls-code-loop(★RISK★):diff 不改 pitfalls/code-loop 判定邏輯;不影響。
- 家 Systems/存量漂移守衛:新增的 WHY 行帶 [出處:] [因:] [test:t_drift_born_true_scan],與實作一致(不用 blame、只看第一父鏈、不確定判不了、上限 6);筆記內容審.md 新增的 PITFALL 帶 [出處:][根因 缺?] 這屬於筆記形狀歸另一席,不在本鏡頭。

## 已驗證沒壞的路徑(供編排者參考)
- 終點重複檢查:還原後 t_drift_born_unknown 的「工作目錄兩行」斷言翻紅,r1 修法有測試守。
- birth 三元組(提交, 原因, 第一版就沒有)只有 _drift_born_one 一個呼叫點:err 路徑旗標一律 False,不會被改寫成「還沒提交」;只有 got 為 None 才帶 True,工作目錄模式才改寫;--at 模式忽略旗標、保留「歷史查不到這篇/那一版的這篇找不到這一行」。
- 預算:_drift_born_over(>=)與 _left()(<=0)等價;預算用完後每條都回「超過預算」,不丟例外;evals 計數把失敗的樹也算一格,第 6 個允許、第 7 個「超過上限」(實測 6/7/8 筆各別得 0/1/2 個 unknown)。
- 批次邊界 31/32/33/64/65 版,寫下那一版都追對。
- 同一篇多條共用 pairs/texts 快取:某條走到 err 版本時其他條走相同快取回相同 err,不互相污染;probe 與 retire 兩種抽取各用自己的 extract,同組條件不互相算進重複。

總結:最高等級 major
