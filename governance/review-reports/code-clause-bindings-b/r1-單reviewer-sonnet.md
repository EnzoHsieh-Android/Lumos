severity: blocker

# code-clause-bindings-b r1 — 驗收 code-clause-bindings r3 折入 6 條(h1–h6)+ 掃 delta 新洞——單reviewer

被審(凍結):`r1-snapshot.patch`(全量,1283 行)+ `r1-delta.patch`(381 行)。前輪留痕:`code-clause-bindings/r3-intake.md`、三份 r3 席報告。
方法:工作樹 `scripts/lumos`/`scripts/test_lumos.py` 有另一 session 未提交的改動(git status 顯示 `MM`),一律不碰;用 `git show HEAD:scripts/lumos` 取凍結狀態複製到 `/tmp/r1check`(blob `f2e598527848f4e9b746c015e8a897e145f38dff`,與 delta patch 尾狀態一致),只在沙盒操作。`python3 test_lumos.py -k clause` 於沙盒全綠(69 passed)。另用 `_load_lumos_inproc()` 對 `clause_bindings` 純函式與 `loop status --disposal` 全流程各自寫一次性 repro(驗完即棄),並額外取 r3 折入前一版(commit `efe7659^`)同樣沙盒化,做「修前 vs 修後」對照。

LUMOS-IMPACT: Lumos/main..HEAD

## 六條逐一驗

**h1(哪些字看得見沿用 `_visible_lines`+`INLINE_CODE_RE`)修好**。純函式餵圍欄範例(`` ```\n- [S23] 圍欄裡的範例 [test:t_ok]\n``` ``)確認 S23 完全不進 `defined`/`fallback`;未閉合反引號案例(`` - [S26] 未閉合反引號 `[S27] 範例 [test:t_ok] ``)驗證「一行一條」把整段(含 `[test:t_ok]`)算給 S26,S27 只落 undefined,做不出 N1 那種「範例偷走真條款 manual 標籤」。
引句:「★哪些字看得見=沿用全檔唯一那份實作★(_visible_lines 逐行 fence 切換 + INLINE_CODE_RE 剝行內反引號;r3 架構席:自寫第二份正則」

**h2(清單前綴多認 `+ • — · 1)`;零條定義只在「像清單項卻不認得」時擋)修了但引入新洞,見 Finding 1**。`_CLAUSE_LISTLIKE_RE = r"^\W*\[S(\d+)\]"` 用 `\W`(非「文字」字元)判「像清單項」,任何字母/CJK 字/數字開頭的枚舉前綴(`a.`、`一、`)一律判「不像清單項」而不是「不認得的清單寫法」,於是整份計劃靜默跳過整個閘。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\W*\[S(\d+)\]")」

**h3(一行一條:定義行只認第一個 [SN])修好**。讀碼確認 `seg = line[ms[0].end():]` 把整行(到行尾)都算給 lead 那個 id,後面出現的 `[SN]` 一律走 `fallback.setdefault(..., (no, ""))` 空段,對照 r3 single-reviewer N1(反引號偷段)的重現路徑已不成立(驗證見 h1)。
引句:「seg = line[ms[0].end():]          # 一行一條:這一行 [SN] 之後全部是它的(後面再出現的 [SN] 是引用,不切段)」

**h4(同編號定義兩次 → duplicate → 擋)修好**。`t_clause_bindings_states`(S28)與 `t_disposal_clause_gate`(cg-o)在沙盒都綠,duplicate 正確擋閘;唯一殘餘是 `cmd_spec_trace` 人讀輸出對 duplicate 顯示的符號跟 rc 不一致,見 Finding 2(minor,不影響 rc)。
引句:「dup.setdefault(cid, []).append(no)   # 同編號在兩行都寫成定義 → 重複(r3 外家席:第二筆沒標會漏過)」

**h5(handoff --json 索引錯 total null)修好**。讀碼確認 `err` 真值時直接短路成 `None`,不會先算 `len(rows)` 再被覆蓋出 0;`t_handoff_clause_pointer_only` 新增的 `total is None and index_error` 斷言沙盒綠。
引句:「c["total"] = None if err else len(rows)   # 索引建不起來時各態算不出,不報 0(r3 外家席 minor)」

**h6(docstring 六種 fail)修好**。逐一核對 `_disposal_clause_step` 函式體裡實際 `return "fail"` 的六個出口(ts 讀不動 / 非 .md 審材 / 索引建不起來 / listlike 零條定義 / 重複定義 / 有未標條款),跟 docstring 枚舉的六種一一對應,無漏列也無多列。
引句:「fail 六種:設計審審材不是 .md / 首筆帳 ts 讀不動 / 測試索引建不起來 / [SN] 像清單項卻是不認得的寫法(零條定義)/ 條款編號重複定義 / 任一條款未標;」

## delta 引入的新洞

### Finding 1
severity: blocker
blocking: 是——計劃裡用字母/CJK 字起頭的枚舉寫驗收條款(`a.`/`一、` 這類真實常見的列表慣例)、完全沒標 `[test:]`/`[manual:]`,處置閘從「格式看不懂就擋」靜默退化成「視同沒用這個功能」放行,直接違反 design-loop.md 自己記的 ★INVARIANT★(計劃有 [SN] 時任一條款定義行沒標就不得 PASS)。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\W*\[S(\d+)\]")」
file: `scripts/lumos:4052`(`_CLAUSE_LISTLIKE_RE` 定義)、擋點在 `scripts/lumos:13460-13467`
最小重現(沙盒對照,已實跑):計劃正文只有 `a. [S1] 甲條款,沒有測試也沒有 manual\nb. [S2] 乙條款,一樣沒標\n`(全字母前綴、零 [test:]/[manual:])。r3 折入前(`efe7659^`)跑 `loop status <id> --disposal` 得 `rc=1`、印「計劃裡有 [SN] 字樣但沒有一條在行首定義……看不懂的寫法不放行」;同一份輸入在本輪凍結狀態(HEAD)跑同一條指令,`rc=0`、印「計劃只在散文/標題裡提到 [SN] 2 次,沒有條款定義行,視同 opt-in 未啟用」、`✅ DISPOSAL GATE PASS`——同輸入、修前擋修後放,是這批 delta 自己造成的迴歸,不是舊帳。

### Finding 2
severity: minor
blocking: 否——`cmd_spec_trace` 的 rc 計算讀的是 `untagged`(已含 "duplicate"),跟顯示符號是兩條互不相干的路徑,duplicate 案例的 rc 仍正確為 1,只有人讀那一行的圖示跟意思對不上。
引句:「mark = "✓" if (b and b["state"] in ("bound", "manual")) else ("✗" if (b and b["state"] == "untagged") else "⚠")」
file: `scripts/lumos:4226`(state 只比對 `"untagged"`,沒把新增的 `"duplicate"` 一起算進 `✗` 分支,duplicate 條款人讀時顯示成 `⚠` 而非 `✗`)

## 總結

最嚴重 severity:blocker(Finding 1)。blocking 條數:1。
