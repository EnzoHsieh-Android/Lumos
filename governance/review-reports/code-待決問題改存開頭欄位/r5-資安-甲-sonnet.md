severity: major

**發現 1:旗幟序列的放行可以整段藏任意 ASCII,等於沒擋**

severity: major
blocking: 是
引句:「return i > 0 and v[i - 1] == "\U0001F3F4" and len(run) >= 2 and run[-1] == "\U000E007F" and all(ord(x) < 0xE007F for x in run[:-1])」
file: `scripts/lumos`(patch 第 112 行,`_pq_flag_run_ok`;呼叫端是 `_pq_bad_char`)

- **攻擊路徑**:攻擊者是陌生 repo 的作者。他在計劃筆記的 `pending_questions` 裡寫 `text: "要不要加快取 🏴<U+E0020–E007E 的標籤字拼成一段 ASCII 指令>U+E007F"`。
- 目前的檢查只要求三件事:前面緊接 U+1F3F4、長度至少 2、以 U+E007F 收尾。標籤字的數量和內容都不限,不必是真的旗幟子標籤(例如 gbeng、gbsct、gbwls)。
- 我用 `unicodedata` 驗過,標籤字屬於 Cf,所以是 `_PATH_SPECIAL_CATS` 本來要擋的類別,現在被這條旗幟規則放行。
- 這份題目文字會被 `lumos pitfalls --stage` 和 `[spec-gate]` 印到終端,也就是進到 AI 的上下文。人眼看不到,AI 讀得到,等於隱形的提示注入。
- 這正是 docstring 自己說要防的事(「標籤字整段放行可藏人看不見、AI 讀得到的 ASCII 指令」)。
- **同類**:U+E0100 以後的異體選擇符屬於 Mn,不在 `_PATH_SPECIAL_CATS` 裡,所以整段不受任何檢查。一串異體選擇符可以編碼任意位元組,同樣是隱形資料通道。
- **建議**:旗幟序列只放行白名單(三個英國子地區標籤);異體選擇符只在前面緊接可見字元時放行,並限制長度。

**發現 2:推送前提醒把筆記路徑原樣印到終端**

severity: minor
blocking: 否
引句:「print(f"{P} 提醒:{rel} 的待決問題清單無法判定(第 {ne[0][0]} 行:{ne[0][1]});進實作前 lumos spec-gate 會擋")」
file: `scripts/lumos`(patch 第 515 行,`_pq_push_remind`;同函式第 518 行也印 `{rel}`)

- **攻擊路徑**:攻擊者在 repo 的圖譜資料夾放一個檔名帶 ESC 或 OSC 序列的 `xxx_計劃.md`,檔內寫一份讀不懂的 `pending_questions`。
- 受害者推送時,`git diff --name-only` 搭配 `core.quotePath=false` 會回原始檔名。`rel` 直接由這個檔名算出來,沒有經過 repr 或 ascii 跳脫。
- 結果是在受害者的終端機執行任意跳脫序列,例如改視窗標題,或用游標移動蓋掉上一行的提醒。
- 同一份 patch 對題號、鍵名都用了 `ascii()` 或 `!r`,唯獨路徑漏了。
- 這是縱深防禦,影響只到終端顯示。
- **建議**:印出前用 `ascii()` 或過濾控制字元。

**各類檢查結果**

1. 不可信輸入流到危險操作:
   - 符號連結筆記不會讓寫入落到庫外。`_write_lf` 是在同資料夾寫暫存檔再 `os.replace`,替換的是連結本身,不會跟著連結寫到目標檔。`_vault_lock_held_for` 對資料夾做 realpath,指到庫外的符號連結資料夾會被前綴比對擋下。已看,無。
   - 命令列參數寫進筆記:鍵限制在 `_PQ_KEYS`,值經 `_pq_bad_char`(擋換行類字元)和 `_yaml_quote`,寫後再讀回驗證。已看,無。
   - git 範圍:開頭是 `-` 的範圍被擋,兩端經 `_lens_full_sha`,`-z` 輸出搭配 `--end-of-options`。已看,無。
2. 權限與守衛繞過:惡意 repo 的計劃檔由作者自己控制,本來就能選擇不宣告阻塞題,這不算新增的洞。解析失敗時規格閘是失敗即阻擋(fail-closed)。寫入鎖的檢查沒有可利用的繞過路徑。已看,無。
3. 密鑰與個資:已看,無。
4. 加密與傳輸:已看,無。
5. 執行邊界:`_guard_dispatch` 外層只是把例外轉成錯誤訊息。已看,無。
6. 行動端:不適用。
7. 新依賴:無(只用了標準庫的 `unicodedata`)。

發現 1 是旗幟序列放行可被濫用來藏字,屬 major、建議擋下;發現 2 是路徑未跳脫的終端注入,屬 minor。其餘各類已看,無。
