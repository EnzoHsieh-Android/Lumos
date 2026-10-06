severity: major

席名:邊界-r3-sonnet。鏡頭:邊界與輸入(空值、無法編碼字元、行尾、超長輸入、特殊檔案類型)。
實跑材料:在臨時目錄用 test_lumos.py 的 _cr_repo/_cr_loop 造帳(設 LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26),沒碰 repo 檔與真帳。`-k t_cap_retro_r2` 34 項全綠。
查過沒問題的角落(不列 finding):超長 evidence 路徑、evidence 含 NUL、超長目錄鏈(--check 與處置閘都不丟堆疊);帳上 U+2028/U+2029/U+0085 與只有 \r 的行尾;回顧檔是 FIFO/懸空捷徑/資料夾(--check 叫人移除);治理帳是 FIFO(不卡);argv 非 UTF-8 的 --note(cap-decision 與 --skip 回 2);帳上輪次含孤立代理字元(cap-decision 回 2);已有人裁的迴圈用非 UTF-8 的 --round 記新一輪(擋下回 2、不丟堆疊)。

### F1 治理帳是捷徑時,人裁照記成功、讀的一側看不到,擋點全部放行 (修補引起)
severity: major
blocking: 是 — 寫帳回「✓ 已記人裁」、之後 `loop retro`、`canary record` 卻當沒有人裁紀錄;fail-closed 的閘變成靜默放行,而且指令還印成功。

- 輸入:`docs/.governance-log.jsonl` 是指向 repo 內另一檔的符號連結(例如共用帳)。
- 走到哪:`cap-decision` → `_gate_event` 用 `open(path, "a")` 追加(跟隨捷徑,寫進目標檔);讀的一側 `_retro_gov_events` 這輪改成 `_retro_read_bytes` → `_regular_own_fd`,該函式帶 O_NOFOLLOW,遇到捷徑回 None → `return []`。
- 壞在哪:同一本帳,寫的一側跟隨捷徑、讀的一側拒絕捷徑。改之前讀用 `Path.read_bytes()`(會跟隨),這是 r2 把讀治理帳改走 `_regular_own_fd` 引入的退化。連帶 `_ledger_tail_needs_newline` 也不跟隨捷徑,捷徑指向的檔缺檔尾換行時照樣黏行(r1 併發席那個洞在捷徑帳上重開)。
引句:「raw, _err = _retro_read_bytes(Path(root) / "docs" / GOV_LOG_NAME, limit=None)」
佐證行:file: `scripts/lumos:1446`(`_gate_event` 追加用 `open(path, "a", ...)`,跟隨捷徑)
佐證行:file: `scripts/lumos:13082`(`_retro_gov_events` 讀側)
重現(臨時 repo,把 docs/.governance-log.jsonl 換成指向 shared-gov.jsonl 的捷徑):
```
lumos loop cap-decision crx --decision extra-round --note "人裁決定破例再開一輪看最後修正" --repo <root>
  → rc=0 "✓ 已記人裁:crx extra-round(帳上輪次 r1, r2, r3)"(目標檔 405 位元組,事件確實寫進去)
lumos loop retro crx --check --repo <root>
  → rc=2 "擋下:crx 沒有人裁紀錄——要先記人裁"
lumos canary record none --loop crx --round r4 ...
  → rc=0(應被 cap-retro-missing 擋下)
```
腳本:`/private/tmp/claude-501/-Users-enzo-rtb-production-agent-demo/f81e262d-8877-4d56-8771-2146d9df2e96/scratchpad/e1.py`

### F2 帳尾檢查改用 os.pread,Windows 沒有這支,所有治理帳寫入直接 AttributeError (修補引起)
severity: minor
blocking: 否 — 只在 Windows 發生,且沒能在 Windows 上實跑(用刪掉 os.pread 模擬),依規則自降一級。

- 輸入:任何非空的治理帳,在沒有 `os.pread` 的平台(Windows)。
- 走到哪:`_gate_event`、`_append_governance_log`、`_drift_ledger_append` 追加前都呼叫 `_ledger_tail_needs_newline`;這輪把原本的 `seek`+`read` 換成 `os.pread`,例外只接 OSError。
- 壞在哪:`os.pread` 在 Windows 不存在,丟 AttributeError,不被接住,整個寫帳(含 pre-push 的 `_gate_event`)崩潰。同檔明確考慮 Windows(`scripts/lumos:16539` 為 Windows 缺 killpg 寫了 AttributeError 退路),`_regular_own_fd` 也用 `hasattr(os, "getuid")` 防護,只有這處沒防。
引句:「return size > 0 and os.pread(fd, 1, size - 1) != b"\n"」
佐證行:file: `scripts/lumos:1518`
佐證行:file: `scripts/lumos:16539`
重現(模擬):`del os.pread` 後呼叫 `m._ledger_tail_needs_newline(<非空檔>)` → `AttributeError: module 'os' has no attribute 'pread'`;不刪時回 False。腳本 `.../scratchpad/e2.py`。未能在真 Windows 重現。

### F3 卷證資料夾是 repo 內的捷徑:提示叫人跑 --template --write,指令一律拒絕,提示不變 (修補引起)
severity: minor
blocking: 否 — 人可以改手寫回顧檔繞過,但提示與拒絕訊息互相不指路,正是 r2 第 4 組想消除的死路。

- 輸入:`governance/review-reports/<編號>` 是指向 repo 內別處(例如 `shared/crx`)的捷徑,已記人裁、回顧檔不存在。
- 走到哪:處置閘第八步印 `_cap_retro_fix_cmd(..., 'none')`,它只 lstat 回顧檔本身(不存在)→ 回 `lumos loop retro crx --template --write`;照貼後 `--write` 新增的資料夾檢查 `os.path.islink(d)` 為真 → 回 2 並印「是捷徑、或解析後不在 repo 根底下」。
- 壞在哪:拒絕訊息沒給出口(沒說改手寫、或把資料夾換成實體目錄),`_cap_retro_fix_cmd` 也沒把「資料夾本身是捷徑」納入判斷,再問一次閘提示原封不動。
引句:「是捷徑、或解析後不在 repo 根底下——不在那裡建回顧檔」
佐證行:file: `scripts/lumos:13355`(`_cap_retro_fix_cmd` 只看回顧檔位置,不看資料夾)
重現:`.../scratchpad/e5.py`:資料夾換成捷徑後 `loop status crx --disposal` 印 `lumos loop retro crx --template --write`;執行兩次皆 rc=2;再問閘提示不變。

### F4 筆記宣稱治理帳寫入器遇到編碼錯誤都回「寫不進去」,doctor --ci 的 `_append_governance_log` 仍丟 UnicodeEncodeError
severity: minor
blocking: 否 — 觸發需要事件字串含孤立代理字元(例如檔名含非 UTF-8 位元組、被 surrogateescape 還原),本審沒能指出 doctor 事件實際會帶未清洗的字串。

- 輸入:`_append_governance_log(vault, [{"gate":"ci","kind":"x","note":"檔名\udcff壞"}])`。
- 走到哪:版控帳那一支 `with open(path, "a", encoding="utf-8") as f: f.write(text)` 外面只接 `except OSError`。
- 壞在哪:丟 UnicodeEncodeError 出去(r2 只改了 `_gate_event` 與 `_local_ledger_append`)。loop-retro.md 筆記寫「治理帳寫入器遇到編碼錯誤回『寫不進去』不丟堆疊」,對這支不成立。
引句:「帶不能編碼的字串(孤立代理字元)也算寫不進去,不丟堆疊」
佐證行:file: `scripts/lumos:1600-1604`
重現:`.../scratchpad/e4.py` → `raised UnicodeEncodeError`。

總結:最嚴重 major,blocking 1 條
