severity: minor

# r2 併發資源席(sonnet)——最壞時序鏡頭

範圍:diff /tmp/code-capretro-r2.patch 的 scripts/lumos 全部 hunk;現檔查證。

## 沒找到問題的項目(含實測,供收貨端對照)
- 補換行與併發追加:`_ledger_tail_needs_newline` 的 "\n" 跟新事件在同一次寫入(版控帳 `open("a")` 一次 f.write、本機帳一次 os.write),所以不會有「補換行一次、事件一次」被別人插進中間。實測:殘行尾(`{"half": 1`)的帳,16 行程併發 64 筆 `_gate_event`,三次都是 64 筆可解析、0 空行、1 條殘行,沒有新的黏行。理論上兩個行程同時看到殘尾會各補一個 "\n"、中間多一個空行;讀側(`_drift_jsonl_iter`、`_retro_gov_events`、`_canary_ledger_scan`)都跳過空行,無害,不標。
- `_retro_read_bytes`:fstat 非一般檔、fstat 失敗、read 失敗三條路徑 fd 都關(finally 或明確 close);regular file 上 O_NONBLOCK 在本機檔系統不會短讀或 EAGAIN,迴圈讀到 EOF 或超限才停,讀不全的情況未構造出來。
- `--template --write` 兩人同時建:O_EXCL 保證只有一個贏,輸家得 rc 2 與「已存在」,贏家寫完整份;沒有兩邊都成功。
- 效能:`_loop_records` 改版後每次整本解析並保留全部編號的列。以真帳(3 MB、3039 列)量:舊 0.092s/峰值 14 MB,新 0.094s/峰值 25 MB,時間不變、記憶體約 1.7 倍;`canary record` 帶 --orchestrator 與 --regression-set 時最多讀 3 次、新一輪還多讀治理帳(19 MB,`_retro_gov_events` 0.06s)。線性成長、目前量級無失敗場景,不標。
- canary-audit ★INVARIANT★「回報成功一定落盤」:本 diff 沒動 `_jsonl_append_verified` 與讀回自驗;新擋點在寫入之前回 2,不印 ✓ 行,不改變「成功⟺落盤可讀回」。固定席 Issues/canary-record未落盤事件 同理。判:未被破壞。

### F1 --template --write 在編碼失敗時留下 0 位元組回顧檔,之後 --template --write 與 --check 都卡死 (修補引起)
severity: minor
blocking: 否 — 需要審查帳或治理帳裡本來就有孤立代理字元(手改帳),一般流程到不了;但一旦中了,殘檔不會自己消失
- 輸入:審查帳某列 `"auditor": "s1\ud800"`(JSON 轉義的孤立代理字元;帳是手改或外來合併進來的),cap-decision 照常成功(rounds 不含它)。
- 走到哪:`loop retro crx --template --write` → 骨架 `context.reports[].auditor` 帶孤立代理字元 → O_EXCL 已建出回顧檔 → `text.encode("utf-8")` 丟 UnicodeEncodeError(不是 OSError,外面只接 OSError)→ 堆疊 → finally 關 fd,但檔留在原地。
- 壞在哪:殘留 0 位元組 cap-retro.json。再跑 `--template --write` 回「已經存在,不覆寫」(rc 2),`--check` 回「不是合法 JSON」;用戶得手動 rm。編碼應該在 os.open 之前做(或失敗時 unlink 自己剛建的檔)。不加 --write 的 `--template` 同一輸入也丟堆疊(舊行為,同根因)。
引句:「                data = text.encode("utf-8")」
佐證行:file: `scripts/lumos:13609-13616`(現檔,`os.open(... O_EXCL ...)` 在 13606 行附近,encode 在 try 內但只接 OSError)
重現:
```
python3 setup.py r r3   # 造 3 輪迴圈;把 canary 帳 auditor 改成 "s1\ud800"
lumos --vault r/docs/kg loop cap-decision crx --decision extra-round --note "人裁決定破例再開一輪看最後修正" --repo r   # rc0
lumos --vault r/docs/kg loop retro crx --template --write --repo r
  → UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 821
ls -la r/governance/review-reports/crx/cap-retro.json   → 0 位元組
lumos ... --template --write → 擋下:回顧檔已經存在 ;--check → 不是合法 JSON(JSONDecodeError)
```
(臨時目錄 /private/tmp/claude-501/t1,未動 repo。)

### F2 補換行的檢查是「先 stat 再 open」,而且開檔沒帶 O_NOFOLLOW/O_NONBLOCK (修補引起)
severity: minor
blocking: 否 — 要在 stat 與 open 之間把帳檔換成管線,需要對 docs/ 有寫權限的另一個行程;⚠ 時序未能重現
- 輸入:帳檔在 `os.stat` 判為一般檔之後、`open(path, "rb")` 之前被換成沒有寫者的 FIFO。
- 走到哪:`_ledger_tail_needs_newline` → `open(path, "rb")` 阻塞到永遠;寫入器本體(`_local_ledger_append` / `_regular_own_fd`)正是為了避開這個「先檢查再開」才在開檔時帶 O_NOFOLLOW|O_NONBLOCK(其 docstring 明寫「不先檢查再開;2 r1 併發席」),新輔助函式又寫回同一種模式,而且在寫入器之前執行,把保護繞過去。
- 壞在哪:`lumos` 指令(含 pre-commit/pre-push 掛鉤呼叫的路徑)卡死而不是回 False。修法:用 `_regular_own_fd`-式的一次開檔(O_RDONLY|O_NOFOLLOW|O_NONBLOCK)再 fstat 判 S_ISREG。
引句:「        if not _stat.S_ISREG(st.st_mode) or st.st_size == 0:」
佐證行:file: `scripts/lumos:1339-1356`(`_regular_own_fd`,正確寫法)
重現:未能重現(競態);結構證據見上。

### F3 cap-decision 遇到帶孤立代理字元的 round 在版控帳寫入時丟堆疊
severity: minor
blocking: 否 — 只在審查帳被手改成含孤立代理字元的輪次時發生;不寫半行(TextIOWrapper 編碼失敗發生在寫入前,實測帳尾無殘行)
- 輸入:審查帳某列 `"round": "r3\ud800"`,輪數到上限。
- 走到哪:`cmd_loop_cap_decision` → `_gate_event` 版控帳分支 `open(path,"a")` + `f.write(line)`,只接 OSError。
- 壞在哪:UnicodeEncodeError 堆疊(實測 `'utf-8' codec can't encode character '\ud800' in position 311`),人裁沒記也沒有「沒記到」的提示;與 r1 邊界席對 retro 檔/輸出路徑做的代理字元防護不一致(`_retro_safe` 只用在印出與回顧檔,rounds 寫帳這條沒有)。S17「帳壞不丟堆疊」的精神在這條路徑沒落實。
引句:「        with open(path, "a", encoding="utf-8") as f:」
佐證行:file: `scripts/lumos:1502`(現檔 `_gate_event` 版控帳寫入)
重現:
```
python3 setup.py r r3(第 3 輪 round 改成 "r3\ud800")
lumos --vault r/docs/kg loop cap-decision crx --decision extra-round --note "人裁決定破例再開一輪看最後修正" --repo r
  → File ".../scripts/lumos", line 1502, in _gate_event  f.write(line)
    UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' ...
```

## 圖譜鏡頭
- Systems/canary-audit ★INVARIANT★ 回報成功⟺落盤:未破(見上)。
- Systems/design-loop、lumos-cli-lifecycle、lumos-cli-read 等 ★INVARIANT★:本席範圍(併發/資源)內未見被本 diff 破壞;未逐條跑綁定測試(只准單測,未跑)。

總結:最嚴重 minor,blocking 0 條
