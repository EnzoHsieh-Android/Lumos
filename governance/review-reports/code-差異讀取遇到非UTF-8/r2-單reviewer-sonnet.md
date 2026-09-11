severity: major

### F3 `_sp_run_text` 這個泛型 git 輸出包裝在守衛與三支新測試視野外,讀非 UTF-8 git 輸出仍會崩潰
severity: major
blocking: 是 — 讀 git 輸出的文字模式呼叫仍可能對非 UTF-8 內容丟 `UnicodeDecodeError`,且完全逃過這次新增的守衛測試,牴觸診斷筆記「每一個都加 errors=」的完整性宣稱
引句:「工具裡每一個用文字模式讀 git 輸出的呼叫都要帶 errors=」
file: `scripts/lumos:940-942` `_sp_run_text(cmd)` 定義為 `_sp.run(cmd, capture_output=True, text=True).stdout.strip()`,沒有 `errors=`;守衛的判別邏輯先看呼叫的第一個參數是不是字面含 `"git"`,不是的話才退回看「所在函式原始碼是否含 `"git"` 字面值」——這個函式本身的原始碼完全沒出現 `"git"` 字樣,兩道判別都落空
file: `scripts/lumos:884` 唯一呼叫點 `_sp_run_text(["git", "-C", str(root), "rev-parse", "HEAD"])` 才是真正把 git 指令傳進去的地方,但守衛只逐一檢查 `subprocess.run/check_output/Popen/call/check_call` 這幾個函式名,`_sp_run_text(...)` 這個呼叫式本身不在名單裡,同樣掃不到
1. 在 /tmp 用當前 `scripts/lumos` 建一個 repo、commit 一支含 `\xff\xfe` 位元組的檔案,直接呼叫 `m._sp_run_text(["git","-C",str(root),"show","HEAD:bad.bin"])`。
2. 實測結果:`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 4: invalid start byte`,當場翻紅(已用 in-proc 載入實測,非臆測)。
3. 且對現在的 `scripts/lumos` 跑守衛的偵測邏輯(`t_every_text_mode_git_call_tolerates_undecodable_output` 內部的 `_text_git_calls_missing_errors`),回傳 `bad == []`——守衛判定「全部乾淨」,完全沒發現這處缺口;目前唯一呼叫點的輸出恰好是 `rev-parse HEAD`(固定 ASCII hex)不會現場觸發,但這正是診斷筆記明講「不設例外清單」要防的那種情境:換一個 git 子指令重用這個包裝,問題就會現形而守衛看不見。

F1:修到 — `cmd_test_layers`(scripts/lumos:759-761)補上 `errors="replace"`,新測試 `t_git_readers_survive_non_utf8_filenames` 用 Big5 檔名重現該路徑,在 /tmp 複本把這行的 `errors="replace"` 拿掉重跑,`test-layers 照樣給提醒` 斷言當場翻紅(`git diff 失敗('utf-8' codec can't decode byte 0xa4...)`),證明這次補的正是 r1 指出的真正缺口(檔名型,非內容型)。
F2:修到 — `_delguard_confidence`(scripts/lumos:17544)補上 `errors="replace"`,`t_diff_readers_survive_non_utf8_content` 新增的「刪除守衛的全域搜尋讀得動非 UTF-8 內容」斷言在 /tmp 複本拿掉該行修法後翻紅,證明有測試真正釘住。

總結:最高 severity major,blocking 共 1 條
