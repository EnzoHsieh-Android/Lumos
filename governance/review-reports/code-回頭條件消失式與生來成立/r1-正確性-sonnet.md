severity: major

審查範圍:/tmp/code-revB-r1.patch 全部 11 個檔,repo 在 scratchpad 的 rw 工作樹(HEAD 3590d1cd)。實驗都在 scratchpad/exp 與一份複製目錄做,沒動 repo。既有測試 `-k when_gone` 26 項、`-k drift_when` 37 項、`-k reinject/license/guard_kill_rc/slim_uninstall_manifest` 全綠。

## 發現

**C1 反引號檢查會誤殺「正文提到 when-gone: 字樣」的合格回頭條件行**
severity: major
blocking: 是 — 提交時把合格的 REVISIT 條件行報成「條件寫錯」擋下,而手冊自己教的寫法(提到寫法時用行內程式碼包起來)正好會踩到
引句:「if "`" in s[m.end():len(s) if end < 0 else end]:」

1. 輸入:`REVISIT:[when-file:src/x.py][by:2099-01-01] 補 `when-gone:路徑` 的說明`。條件標記本身是 `when-file`,完全合格;說明文字用行內程式碼提到 `when-gone:`。
2. 走到哪:`_ns_revisit_cond_viol(ln, rest)` 把整行原文 `ln` 交給 `_probe_gone_backtick_err`;它對原文裡**每一個** `when-gone:` 出現處(不管是不是條件標記)都往後找第一個 `]`;這行後面沒有 `]`(end < 0),就檢查「從 `when-gone:` 之後到整行結尾」有沒有反引號,而那段正好含這個 span 自己的收尾反引號。
3. 壞在哪:最小重現(`m` = 載入 scripts/lumos 的模組):
   `m._ns_revisit_violations("REVISIT:[when-file:src/x.py][by:2099-01-01] 補 `when-gone:路徑` 的說明", "body", True)` 回 `[('條件寫錯', ..., 'when-gone 的字串不能含反引號(會被當成行內程式碼剝掉);…')]`。
   另兩個同族輸入也中:`REVISIT:[when-gone:src/x.py][by:2099-01-01] 補 `when-gone:` 說明`(本身是合格的 when-gone,說明裡再提一次);`REVISIT:[when-file:src/x.py][by:2099-01-01] 補 when-gone: 說明 `x``(說明裡有裸的 `when-gone:` 加任何後面的行內程式碼)。對照:`...補 `[when-gone:路徑]` 的說明` 沒事(因為 `]` 先到)。
   實驗檔 scratchpad/exp/t2.py。
4. 為什麼測試沒抓到:`t_drift_when_gone_grammar` ① 只測「反引號在標記內」的陽性,沒測「標記外正文提到 when-gone:」的陰性。
5. 修法方向:只在「真正解析成條件標記」的位置檢查(例如只看 `[when-gone:` 開頭、且要有收尾 `]` 才檢查),不要對裸字串 `when-gone:` 做掃描。

**C2 撤除條件的 when-gone 字串含 `]` 被放行,實際評估的是被截斷的字串**
severity: minor
blocking: 否 — 不會擋錯人也不會誤放行推送,只是撤除條件悄悄換成較短的字串;REVISIT 那條路同樣的字串其實也沒被明擋,但至少不是計劃宣稱「兩條路要求一致」要保證的事
引句:「err = _probe_check_value(k, val)[1] or (_probe_gone_backtick_err(v) if k == "gone" else None)」

1. 輸入:`RULE:… [retire:when-gone:a.py::x[1]y]`(程式碼裡很常見的 `arr[0]` 這種字串)。
2. 走到哪:`slot_parse` 允許值內有成對方括號,`_slot_retire_err("when-gone:a.py::x[1]y")` 回 None(合格);推送判定改走 `_retire_lines` → `_probe_parse("[when-gone:a.py::x[1]y]")`,標記正則 `[^\]\n]*` 在第一個 `]` 結束。
3. 壞在哪:實跑 `_probe_parse` 得 `conds=[('gone','a.py::x[1')]`、errs 空。作者寫的字串是 `x[1]y`,實際判的是 `x[1`:檔裡改成 `x[1]z` 時撤除條件應成立卻不成立。計劃〈做法〉1 與手冊都寫「字串不能含 `]`」,`_probe_gone_err` 沒擋 `]`(只靠標記切分),撤除條件這條路也沒補。實驗檔 scratchpad/exp/t3.py、t4.py。

**C3 git 模式讀原始位元組沒有大小上限,200MB 的檔讀進記憶體後才判「超過 2 MB」**
severity: minor
blocking: 否 — 只在有人對巨大檔寫帶字串的 when-gone 時才出現,而既有的 symbol/test 讀檔也是同一支無上限的批次讀(不是這次新引入的讀法)
引句:「self._raw.update(zip(todo, blobs))」

1. 輸入:提交裡有 ~200MB 文字檔 `big.txt`,筆記寫 `REVISIT:[when-gone:big.txt::zzz][by:2099-12-31] …`,推送改到 big.txt。
2. 走到哪:`prefetch` → `_read_raw`(git 分支)→ `_drift_cat` → `_nodehome_cat_blobs`(無上限版,不是 `_nodehome_cat_blobs_capped`)。上限 `_DRIFT_GONE_MAX_BYTES` 只在讀完以後由 `_drift_gone_text` 比;只有 disk 分支在讀之前看 `st_size`。
3. 量測:`/usr/bin/time -l python3.14 scripts/lumos drift check --diff …` 最大駐留記憶體 1,137,754,112 bytes(約 5.6 倍檔案大小),peak footprint 1.24 GB。計劃「實作」一節寫的是「工作目錄模式讀原始位元組前先看檔案大小」,git 模式(推送判定、CI)沒有對應的事前截斷,而推送判定正是會跑在 CI 小機器上的那條。實驗檔 scratchpad/exp/x2.py。

**C4 三條宣稱的分支沒有任何測試走到:「讀不出」「超過上限」、工作目錄模式(scan)的 when-gone**
severity: minor
blocking: 否 — 程式現在實跑是對的(我另手動跑過 scan,見下方「沒問題的項目」),只是回歸時不會紅
引句:「return None, "讀不出"」

1. 驗收條款 S1 明列「讀不出 應判不了」,〈做法〉3 寫了「單檔上限…超過判不了」與工作目錄模式的行為;`t_drift_when_gone_evaluates` 的五個判不了輸入是資料夾、NUL、LFS、Big5、連結檔,沒有「讀不出」(b 為 None)也沒有「太大」,而且全程只用 `_drift_probe_tree(root, tip)` 的 git 模式,從沒建過 `where == "disk"` 的樹。
2. 變異實驗(複製到 scratchpad/exp/rwm 改,不動 repo):把 `_drift_gone_text` 的 `b is None → "讀不出"` 與 `_DRIFT_RAW_TOO_BIG` 兩個分支拿掉,並把 disk 分支的 `st_size` 事前截斷改成直接 `read_bytes()`,`python3.14 scripts/test_lumos.py -k when_gone` 仍是 26 passed, 0 failed。這三個修法改回去都不會紅,違反固定席「還原翻紅釘」的要求(被測路徑要有前置斷言證明走到)。
3. 另外 S5 寫「doctor Check D 不報」,測試 ⑤ 只比對字串 `when-gone:路徑[::字串]` 是否出現在 CLAUDE.md/AGENTS.md,沒有跑 Check D;我手動跑 `scripts/lumos doctor` 的 [D] 兩項是綠的,所以現況成立,只是測試守得比條款弱。

**C5 RETIRE-IF 與 REVISIT:2026-12-03 指定的量測法數不到「還沒成立的 when-gone」**
severity: minor
blocking: 否 — 影響的是兩個月後「零使用就拿掉這個鍵」的判斷依據,不影響現在的行為
引句:「用 `lumos drift scan --json` 數回頭條件與 RULE 撤除條件裡實際解析出的 `gone` 條件」

1. 計劃的 RETIRE-IF 與 REVISIT 都要求用 `lumos drift scan --json` 數「實際解析出的 gone 條件」。
2. 實跑:scratchpad/exp/x3b.py 在一個筆記裡放 6 條 when-gone(含一條仍在、尚未成立的 `[when-gone:src/a.py::time.time()]`),`drift scan --json` 只輸出 `findings`(成立的 3 條)與 `problems`(判不了的 2 條),那條「正常、尚未成立」的第 1 條完全不在輸出裡。每條都等著對的 when-gone 正是最健康的使用,卻數成零。
3. 結果:兩個月後照這個指令數,一個全部條件都還在等的專案會數出 0,觸發「零使用拿掉」。計劃自己在〈寫下時就成立〉那篇也記了「發現的字典沒有帶條件解析結果」,同一個限制沒套到這裡。

## 沒問題的項目

逐 hunk 走過、跟作者宣稱一致的部分(我實際跑過的標 ✓):

- ✓ 驗收條款 S1 的成立判定:檔在/刪掉、資料夾、連結檔、子模組(用合成樹)、字串在/不在;NUL、LFS、Big5、資料夾加字串都判不了且訊息講原因。
- ✓ S2:推送刪字串或刪檔點名「讓條件成立了」且不附「找不到」提示;新寫而字串本來就不在點名「已經成立」;新寫而路徑不在終點才多附提示。我另跑了改名(舊路徑消失,條件成立,點名)、NFD 檔名(條件寫 NFC、git 裡是 NFD,刪檔照樣點名)、帶 BOM 的檔(字串比對正確)。
- ✓ S3/S4:路徑 `/` 開頭、`..`、`a\..\x.py`、`..\x`、字串空、標記內反引號都報錯;`::` 從第一個切;字串反斜線原樣、兩端空白去掉;`[when-gone:src/lib/]` 尾斜線正規化成 `src/lib`、`src//a.py` 正規化成 `src/a.py`。撤除條件跟 REVISIT 共用 `_probe_check_value`,`..\x` 兩邊都擋。
- ✓ 候選篩選:`path in touched` 加「以它為前綴」覆蓋刪素材檔與刪素材資料夾(非程式檔不會被一般篩選吃掉);改名兩端都在 touched。
- ✓ 工作目錄模式 scan:未暫存的刪除、不存在的路徑算消失,Big5 檔與連結檔帶字串判不了且講原因(x3.py 實跑)。
- ✓ `_DriftProbeTree.present` 的資料夾前綴推導(`rsplit("/", i)`)對多層路徑正確;`_drift_cond_split(v, k)` 的新參數不影響 symbol/test 的既有呼叫(prefetch 傳 symbol/test 的 k 走舊切法)。
- ✓ 新舊互讀:舊版工具讀到 `when-gone` 會當「不認得的條件鍵」(計劃〈相容〉已寫明);RULE 撤除條件現在會轉反斜線,過去放行的 `when-file:..\x` 現在被擋,這是計劃明寫的行為變更。
- ✓ 訊息改寫「讀不出或讀不準的程式檔或筆記」:全 repo 沒有其他地方比對舊字串(grep 過 scripts/lumos、test_lumos.py、skills)。
- ✓ CLAUDE.md/AGENTS.md 只差撤除條件那一句,doctor [D] 一致;範本長了 45 bytes,doctor 對範本膨脹的警示是既有狀態。
- 沒查到問題但不確定的:`touched` 的路徑是否一律 NFC 沒追到 `_nodehome_name_status` 原始碼,NFD 刪檔實測有點名,故暫不列為問題。

## 固定席節點

- bound-tests-gate [INVARIANT]:這份 diff 沒碰 code-loop check 對合約測試逐支真跑的邏輯;改動集中在存量漂移評估與解析,與該合約綁的 `t_bound_tests_g…` 無交集。不影響。
- guard-kill [INVARIANT 兩條]:rc 優先序與 `--json` 單行輸出都在 guard kill 的程式路徑,diff 沒動。不影響。
- 授權與歸屬 [INVARIANT 兩條]:沒動 `_VENDORED_TOOLKIT`、沒動 scripts/lumos 檔頭的 SPDX 與 MIT 全文;被複製的 scripts/templates/graph-discipline.md 只改了一行內文、原有 SPDX 註解不變。不影響。
- 測試假綠形態 [INVARIANT]:「還原翻紅釘要有前置斷言證明被測路徑走到」——這份 diff 的新測試在 push 路徑與 retire 路徑符合(③ 刪檔不附提示、⑤ 新寫附提示可以區分),但在 C4 指出的三個分支違反。
- lumos-cli-read [INVARIANT]:search 排除 superseded 的行為,diff 沒碰。不影響。
- lumos-deinit / lumos-cli-lifecycle [INVARIANT]:re-inject 只覆蓋 sentinel 之間的 body;本次對 CLAUDE.md/AGENTS.md 的改動全在紀律區塊 body 內,`-k reinject` 48 項全綠。不影響。
- design-loop [INVARIANT]:處置閘第五步針對設計審迴圈的審材與 `[SN]` 綁定;本計劃的 S1 到 S5 都有 `[test:]` 綁定且測試方法存在(實跑通過)。不影響。
- pitfalls-code-loop [RISK]:風險分級邏輯沒動。不影響。
- 其餘「超出上限只列名」的節點(loop-convergence-recording、reversibility-governance-ledger、lumos-deinit、節點範圍與索引守衛、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim-*、雙向門放行、規格落成可驗收條件、逃逸自動記、core-invariant-baseline、judge-severity-gate):沒有內容可判,從 diff 看不出牽連;其中「節點範圍與索引守衛」與本案相關的只有存量漂移守衛家筆記與筆記內容閘各補一行 WHY,沒有改既有合約行。

最高 severity: major
