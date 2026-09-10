severity: major

### F1 `_set_about_code` 的存在檢查可被路徑穿越繞過,寫出 repo 外的路徑
severity: major
blocking: 是 — 新增的「路徑必須在 repo 裡存在」這道唯一防線,可用 `../` 繞出 repo 邊界寫入,直接違反函式自己宣稱的保證,且已用真實指令重現成功(rc=0、值真的寫入檔案)。
引句:「if not v or not (root / v).exists():」
1. 檢查只用 `(root / v).exists()`,沒有把結果限制在 `root` 之內(未 `resolve()` 後比較前綴/`os.path.commonpath`),`Path` 的 `/` 運算與 `.exists()` 對 `../` 一律照 OS 語意穿越。
2. 實測重現(/tmp 暫存 repo,root 下無 `.git`,走 `_vault_repo_root` 的 fallback 分支):`lumos --vault <v> set S about_code "../../../../../../etc/passwd"` → 印出 `✓ set Systems/S.md: about_code 已改成 ../../../../../../etc/passwd`,rc=0,檔案內容真的寫成 `about_code: ../../../../../../etc/passwd`;預期應是「擋下」rc=2。
3. 錯誤訊息本身寫「about_code 要填這個 repo 裡真的存在的路徑」,但實際檢查驗不到「在 repo 裡」這件事——這正是這個修法想關掉的那類「about_code 指到假地方、波及計算靜默失聯」,只是換了一種輸入就重新打開。
佐證:file: `scripts/lumos:10814` `_set_about_code` 的存在檢查,未對 `(root / v)` 做 `resolve()` 後的邊界比對。

### F2 「about_code 的唯一寫入口」宣稱不實——`append` 仍是一條活的寫入路徑
severity: minor
blocking: 否 — 可用 `set` 事後修正,不會造成不可逆資料損壞,但是新程式碼與新知識圖譜筆記裡明寫的斷言與實測行為矛盾(內部不一致例外)。
引句:「about_code 的唯一寫入口(2026-09-10)。」
1. 對套模板預設 `about_code: []` 的節點跑 `lumos append <node> about_code src/real.ts`,rc=0,寫出 `about_code:\n  - src/real.ts`——清單形,不是純量,append 完全沒被擋。
2. 這與 `_set_about_code` docstring 第一行「about_code 的唯一寫入口」、以及同批新增的 Issue 筆記「現在 `lumos set <節點> about_code <路徑>` 是唯一寫入口」直接矛盾——append 仍能把欄位寫回清單型。
3. 未觸及 `edit_fm_append`/`cmd_append`,這條舊路徑沒有被這次診斷或關閉,而是被文件/註解宣稱成「已經沒有了」。
佐證:file: `scripts/lumos:10803-10804` `_set_about_code` 的 docstring 首句;`edit_fm_append` 對 kind=="list" 的欄位不拒絕(未被本次 diff 觸碰)。

### F3 `_stack_changed_ok` 新參數三處呼叫只補了兩處,刪除行分支被漏掉
severity: minor
blocking: 否 — 目前吃不出可觀察差異(現況 vendored 檔全是 `.py`/`.md`/無副檔名,`_stack_key_for_file` 對 `.py` 沒登記任何棧),但是同一支函式簽章擴充後呼叫端沒有同步更新到底,屬內部不一致例外,仍要報。
引句:「刪除行不推進新檔行號;但它是「改動內容」——棧別觸發要看(拿掉 CancellationToken/timeout/key 也該問;」
1. `_pitfall_diff_collect` 裡處理「-」開頭刪除行那段(對應現在的 `scripts/lumos:17621`)仍是 `_stack_changed_ok(cur_file)`,未補 `_skip_vendored`;同一支函式另外兩處「+」新增行分支(現在的 `scripts/lumos:17629`、`17634`)都已補上 `_skip_vendored`。
2. 這代表:在消費專案的 diff 裡,vendored 檔案內部被刪掉的行仍會被塞進 `changed_lines`,供「棧別觸發」(表態閘 S2)使用,而同一批新增行已被過濾——語意上不對稱。
3. 目前不構成可翻紅場景是因為 vendored 清單裡沒有任何副檔名登記在 `_STACK_QUESTION_SPECS`/`_stack_key_for_file` 裡;一旦 vendored 清單日後納入有登記棧的副檔名(如把某個 `.ts` hook 也算進 `_VENDORED_DIRS`),這個漏改的呼叫點就會立刻讓「消費專案的第一次提交」重新在棧別追問裡看到工具鏈自己的檔。
佐證:file: `scripts/lumos:17621` 未更新的呼叫點;file: `scripts/lumos:17629` 與 `scripts/lumos:17634` 已補 `_skip_vendored` 的對照。

風險掃描清單那 1 條:誤報——`scripts/lumos:17562` 命中的 `open(` 是 `_stack_changed_ok` docstring 裡引用「命中 `open(...)`」這個現象本身的中文說明文字,不是真的檔案 I/O 呼叫;pitfalls 的逐行過濾只剝 `#`/`//`/`--`/`/*`/`*` 開頭的行與行內字串字面量,對 Python 三引號 docstring 內部沒有真正排除,屬於這支既有機制自己的天花板,不是本次 diff 新引入的邏輯錯誤。

總結:最高 severity major,blocking 共 1 條
