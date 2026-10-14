severity: minor

## 範圍與做法
- 讀了修補差異全文,並對照 `8c4e0b14~1` 到 `8c4e0b14` 的測試改動。
- 跑了 `-k dispatch_lens`,394 項全過。
- 在 `--shared` 複製出的暫存 repo 裡,用修補前後兩版 `scripts/lumos` 各跑一次 `dispatch-lens --spec ... --json`。暫存目錄已刪。

## Finding

severity: minor
blocking: 否 — 只影響設計審派工詞裡檔名那一行的顯示,內容照讀、照跑 impact,沒有安全或正確性後果。
引句:「白名單外的常見標點(& + , ：)也印成固定字樣——只影響那一行顯示」
問題:新的出口只收少數字元,但程式檔名那條路(反引號候選,可含任何非空白字元)會碰到更多常見寫法。`[ ]`、`@`、`~`、`$`、`#` 都不在白名單。注解和筆記只列了 `& + , ：`,沒提這幾個。受影響的是前端常見的路徑,例如 Next.js 的 `app/[id]/page.tsx` 與 `src/@types/x.d.ts`。
具體失敗情境:計劃用反引號寫 `app/[id]/page.tsx`,且這個檔存在。輸出是「計劃提到並找得到的程式檔:另有 1 個名字含不收的字元」,檔名完全消失。編排者和審查席看不出計劃提到哪支檔,也就看不出固定席是照哪支檔算的。
佐證:file: `scripts/lumos:49183`(白名單常數)、`scripts/lumos:49322`(`_lens_spec_names_line`);hook 的同類情形在 `scripts/hooks/claude/dispatch-lens-hook.py` 的 `_spec_what`,絕對路徑含 `~` 或 `@` 的計劃值(例如 iCloud 目錄)在超時說明行也會變成固定字樣。

severity: minor
blocking: 否 — 只在大小寫與 Unicode 正規化都敏感的檔案系統上,同一支檔同時用 NFC 和 NFD 兩種寫法出現時才發生。
引句:「去重比 NFC 鍵、留第一次出現的寫法」
問題:`_lens_spec_code_cands` 去重後只留第一次出現的寫法,後面用它去查檔案存不存在。如果磁碟上的檔名是第二種寫法,而第一種寫法不存在,這支檔就被漏掉。修補前兩種寫法都會被試。macOS 的 APFS 不區分兩種寫法,所以本機測不到。
具體失敗情境:Linux 上,計劃先寫 NFC 的 `scripts/café.py`,後面又寫 NFD 的同名檔,磁碟上是 NFD。結果是「找得到的程式檔」少了這支。
佐證:file: `scripts/lumos:49490`;`_lens_spec_linked` 的 `seen` 也是同樣改法。

## 你點名的三項
- **共用函式加參數對其他呼叫者沒有影響。**
  - `_path_special_chars(extra=frozenset())` 預設為空,其他 9 個呼叫點都沒傳 `extra`,行為不變。
  - 唯一傳 `extra` 的是 `_lens_author_name_ok`。
  - diff 模式呼叫 `_lens_render_listed` 時沒傳 `show`,走恆等函式,輸出與原來逐字相同。
- **三支舊測試期望改得對,沒有把真回歸改綠。**
  - 被改的只有「(路徑含不收的字元)」變成「 (名字含不收的字元)(blob」,是出口換了固定字樣的措辭差異。
  - 斷言都還在,「審查結論一律寫通過」「忽略以上全部指示」不在輸出裡的檢查沒動。
  - 多出的前導空格是新格式 `的 {show}(blob`,與程式一致。
  - 我沒有把其他測試被改成只剩措辭差異以外的內容,這部分只看了前面幾條差異。
- **`--json` 輸出相容。**
  - 修補前後各跑一次,欄位集合完全相同:`bound_status`、`cands_truncated`、`code_files`、`landing`、`linked`、`listed`、`mode`、`pinned`、`scan_truncated`、`shown`、`skipped_files`、`spec_source`、`too_generic`。
  - `code_files`、`too_generic`、`pinned`、`listed` 的值相同,`text` 長度也相同(1809)。
  - `code_files` 和 `too_generic` 在 JSON 裡仍是原始名字,只有 `text` 過出口。依賴 JSON 欄位原值的下游不受影響。

## 已讀,無 finding
- hook 的 `_spec_what`、`_range_what`、`_spec_name_show`:與 lumos 的名字白名單一致,測試比對兩邊也是綠的。
- 逾時、鎖狀態未知、算不出三種說明行的 `what`:`rng or spec` 改成各自的出口,語意不變。`TIMEOUT_NOTE` 的 `cmd=rng` 參數,範本裡根本沒有 `{cmd}`,沒有洩漏。
- `_arch_target_split` 的回傳形狀是 `{節點: [檔…]}`,與新的 `shown` 字典相容。
- 固定席節點名:`_lens_spec_name_ok` 本來就在前面擋掉不合的節點,所以 `_lens_render_listed` 的 `show` 不會把節點路徑變成固定字樣。我在暫存 repo 裡把節點改成含全形冒號的名字,確認了這點(修補前後行為相同,都是「名字不合,沒列也沒讀」)。
- 本 repo 的 905 支 `-knowledge/` 與 `scripts/` 檔案路徑都合白名單,沒有超過 300 字的。

最高等級 minor,blocking 0 條。
