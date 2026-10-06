severity: major

席名:併發資源-r3-sonnet(資源與併發鏡頭)。實跑環境:把 scripts/ 複製到暫存目錄,在副本裡加測試函式跑,沒碰 repo 與真帳。

### F1 治理帳被換成符號連結時,寫的一方照寫、讀的一方當沒有人裁紀錄,人裁整個失效(修補引起)
severity: major
blocking: 是 — 已實跑重現:`cap-decision` 回成功,但三個擋點與處置閘全部看不到那筆人裁,新一輪照樣記進帳
- 輸入:`docs/.governance-log.jsonl` 是指向 repo 內別處檔案的符號連結(多個 worktree 共用同一本帳、或把帳放到共用位置的做法)。
- 走到哪:寫入端 `_gate_event` 的版控帳分支用 `open(path, "a")`,會跟隨捷徑,所以 `cap-decision` 寫得進去、回 0 並印「已記人裁」。讀取端 `_retro_gov_events` 在第二輪從 `read_bytes()` 改成走 `_retro_read_bytes` → `_regular_own_fd`,後者帶 O_NOFOLLOW,遇捷徑回 None,`_retro_gov_events` 隨即回 `[]`。
- 壞在哪:`[]` 等於「沒有人裁紀錄」。實測:`cap-decision` 回 0、真檔多了 405 位元組;接著 `loop retro --template` 回 2 說「沒有人裁紀錄」;`canary record none --round r4`(應被擋)回 0 照記;處置閘第八步印「—(沒有人裁紀錄,不需要回顧)」。第一輪(`read_bytes()`)這條路會跟隨捷徑、擋得住。第二輪為了擋管線,把「不跟隨捷徑」一併套到治理帳,卻沒讓寫的一方跟讀的一方一致。
- 引句:「raw, _err = _retro_read_bytes(Path(root) / "docs" / GOV_LOG_NAME, limit=None)」
- 佐證行:file: `scripts/lumos:13082`(讀端);file: `scripts/lumos:1502`(寫端 open(path, "a") 跟隨捷徑);file: `scripts/lumos:1339`(_regular_own_fd 的 O_NOFOLLOW)
- 重現(暫存副本裡的測試,輸出):
  - 建 `_cr_repo()` + `_cr_loop(c)`,把 `docs/.governance-log.jsonl` 換成指向 `shared-gov.jsonl` 的捷徑,執行 `_cr_decide(c)`、`_cr_retro(c,"--template")`、`_cr_record(c,"r4")`、`_cr_gate(c)`。
  - 輸出:`DECIDE rc 0 ✓ 已記人裁:crx extra-round` / `real size 405` / `TEMPLATE rc 2 擋下:crx 沒有人裁紀錄` / `RECORD r4 rc 0` / `GATE ['[disposal] 跑滿回顧: —(沒有人裁紀錄,不需要回顧)']`。
- 另:同一支函式遇到「治理帳讀不到」(權限、非一般檔)一律回 `[]` 當沒有人裁,不分「沒有帳」與「帳讀不動」,這條 fail-open 路徑本來就有,第二輪只是多開了捷徑這個入口。

### F2 建檔中途被中斷會留下 0 位元組殘檔,而提示叫人跑 `--check`,沒有出口
severity: minor
blocking: 否 — 人手動刪檔即可,不影響帳與閘的判定;但違反計劃〈三〉「提示不互相叫對方先做」的出口要求
- 輸入:`--template --write` 在 `os.open(... O_EXCL)` 建好檔之後、`os.write` 完成之前被打斷(Ctrl-C、SIGKILL、當機)。第二輪補的 `os.unlink` 只在 `os.write` 回短寫或丟 OSError 時才跑,被信號殺掉的程序跑不到。
- 走到哪:殘留的空檔或半截檔存在。再跑 `--template --write` → O_EXCL 回 FileExistsError,印「已經存在,不覆寫」,後面接 `_cap_retro_fix_cmd(...,'none')`;該函式看到檔存在就回「回顧檔已在、還沒記:`--check` 過了再 `--record`」。
- 壞在哪:`--check` 對空檔印「回顧檔不是合法 JSON(JSONDecodeError)」,沒有任何一句叫人刪掉重建;`canary record` 擋下與處置閘也只重複同一句「回顧檔已在、還沒記」。實測(副本裡先寫 0 位元組檔):`W rc 2 …回顧檔已在、還沒記:lumos loop retro crx --check…`、`CHECK rc 1 ✗ 回顧檔不是合法 JSON`、處置閘第八步 ✗ 並印同一句。使用者只能自己猜要 `rm`。同樣,另一支程序在 O_EXCL 建檔與寫入之間跑 `--check` 會看到空檔而報「不是合法 JSON」(短暫)。
- 引句:「return f"回顧檔已在、還沒記:{_retro_cmd(loop_id, '--check')} 過了再 {_retro_cmd(loop_id, '--record')}"」
- 佐證行:file: `scripts/lumos:13373`(提示);file: `scripts/lumos:13653`(O_EXCL 建檔);file: `scripts/lumos:13192`(--check 對壞檔的原因文字不帶出口)
- 重現:副本測試 `_cr_decide(c)` 後 `p.write_bytes(b"")`,執行 `loop retro crx --template --write` / `--check` / `canary record ... r4` / 處置閘,輸出如上。

## 查過、沒找到問題的地方
- `_ledger_tail_needs_newline` 改走 `_regular_own_fd(require_owner=False)`:`_gate_event`、`_append_governance_log`、`_drift_ledger_append` 三個呼叫者行為一致;fstat 後 pread(size-1) 用同一個 fd,沒有先查再開的縫;兩個寫入者同時看到缺換行各補一個,只多一個空行,讀側都跳過空行。
- `_regular_own_fd` 多接 `ValueError`(路徑含空位元組)只讓回傳更保守,另兩個呼叫者(`_local_ledger_append`、`.gitignore` 寫入處)都已處理 None。
- `_gate_event` 非本機帳分支接 `UnicodeEncodeError`:TextIOWrapper 先整段編碼才寫,不會寫出半行。
- `_ledger_lines` 加 `\r`:`loop status` 讀帳先經 `read_text`(已把 `\r`、`\r\n` 轉成 `\n`),不會多切;`_canary_ledger_scan`、`_retro_gov_events` 讀位元組端 `json.dumps` 本來就跳脫 `\r`。
- `--template --write` 的落點檢查:`islink(d)` 加 `realpath` 前綴比對(含上層 `governance` 是捷徑的情形)會擋;檢查到 O_EXCL 開檔之間仍有被換掉的縫,但需要同機有寫入權的對手,跟計劃〈誠實界線〉記的信任等級相同,不另標。

總結:最嚴重 major,blocking 1 條
