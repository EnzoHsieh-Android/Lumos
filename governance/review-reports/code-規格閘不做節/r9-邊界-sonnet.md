severity: major

檢查範圍:`_strip_zero_width`、`_ledger_physical_lines`、`-std` 出口的編號邊界,以及相關測試。我寫了隨機測試,也在實驗目錄複製程式做了一次破壞測試。

## finding 1:整類刪除沒蓋到 Cf 以外的看不見字元,「危險詞夾隱形字元就判風險低」第四次被換字元打穿

severity: major
blocking: 是 — 計劃正文夾一個沒被刪的看不見字元,危險詞就逃出關鍵字掃描,風險高的計劃被判風險低而不派審。
引句:「另加不歸 Cf 但一樣看不見的:變體選擇符 U+FE00–FE0F 與 U+E0100–E01EF、組合字形連接符 U+034F、韓文填充字 U+115F、U+1160、U+3164、U+FFA0」
問題:補丁把這一步當成「整類」刪除,實際只蓋 Unicode 類別 Cf 加手列的清單。Unicode 的 Default_Ignorable 字元還有一批不是 Cf、也不在 `_INVISIBLE_EXTRA`,現在原樣留著:
- 蒙古文自由變體選擇符 U+180B、U+180C、U+180D、U+180F(類別 Mn)。
- 高棉文固有母音 U+17B4、U+17B5(類別 Mn)。
- 未指派但屬 Default_Ignorable 的 U+2065、U+FFF0–FFF8、U+E0000、U+E0002–E001F、U+E0080–E00FF、U+E01F0–E0FFF(類別 Cn)。
- 點字空白 U+2800(類別 So),畫面上是一格空白。

具體失敗情境:我在 spec-gate-nondo 實跑 `_door_keyword_hits`,測資是「本計劃會實作退X款流程」與「we will implement payX ment gateway」(X 代表夾進去的字元,兩句各夾一個)。
- X 為基準(不夾)、U+200B、U+FE0F:命中(金流 退款、payment)。
- X 為 U+180B、U+17B4、U+2065、U+FFF0、U+E0000、U+2800:兩句都回空。

這 6 個碼位都是我在 patch 之外另外試的,補丁自己的測試表沒有。實際走法是計劃正文寫「實作退\u180b款」,門判風險低,推送前不要求設計審。

佐證:
- file: `scripts/lumos:5018`(`_INVISIBLE_EXTRA` 定義)
- file: `scripts/lumos:5041`(`_strip_zero_width` 的判斷式)
- file: `scripts/lumos:8144`(`_door_scan_text`)

測試只列 24 個碼位(`_INVISIBLE_CASES`),不含上述任何一個,所以改壞不會紅,漏洞也看不到。

修法建議:改用 Default_Ignorable_Code_Point 的完整範圍表(含 180B–180F、17B4–17B5、2065、FFF0–FFF8、E0000–E0FFF 全段),並加 U+2800。測試改成逐碼位掃整張表,不要手列。

## finding 2:區塊結尾剛好是 `\r` 時「等下一塊」的守衛,測試完全沒測到

severity: minor
blocking: 否 — 現行程式對,是測試保護不到;守衛被改壞時,錯的只有壞行行號的提示。
引句:「區塊結尾剛好是 \r 時先不切,等下一塊看是不是 \r\n。」
問題:`t_canary_ledger_streams_one_core` 的夾具(`size` 變數那一段)全是單獨的 `\r`,整檔沒有 `\n`,也沒有 `\r\n`。所以 `\r\n` 剛好被 64KB 邊界切開的情形沒人測。

實測:
- 在實驗目錄複製 scripts,拿掉 `if blk and m.end() == len(buf) and m.group() == b"\r":` 那三行,跑 `-k ledger_streams`,9 項全綠。
- 同一份被改壞的程式,用隨機位元組(區塊 1 到 16 位元組、3000 組亂數,對照 `_ledger_lines` 整本切法)測,1360 組不一致。例子是 `\r\n` 被切開時多出一個空行,後面的行號全部偏 1,`bad` 回報的壞行號會錯。
- 原版程式碼:6 種區塊大小各 3000 組,行號、內容、起點位移全部一致,0 不一致。

佐證:file: `scripts/test_lumos.py:64687`(夾具),file: `scripts/lumos:13900`(`_ledger_physical_lines`)。

修法建議:加一個用小的 `_LEDGER_READ_BLOCK` 或把 `\r\n` 剛好放在 64KB 邊界的測試,檢查行號。

## finding 3:`_ledger_physical_lines` 對單行很長的帳是二次方時間

severity: minor
blocking: 否 — 要有一行帳大到數十 MB 才會明顯,正常帳列到不了。
引句:「buf, base, no, scan = b"", 0, 0, 0   # scan:buf 裡從哪裡開始找換行(一行跨好幾塊時不從頭重找)」
問題:`buf += blk` 每塊都複製整個累積的 buf,所以時間隨單行長度的平方增長。`scan` 避免了重複搜尋,但沒避免重複複製。舊的 `for chunk in f` 是線性。

實測單行、無換行:
- 8MB:0.29 秒
- 16MB:0.57 秒
- 32MB:2.05 秒
- 64MB:11.3 秒(舊寫法同尺寸約毫秒級)

另外,純 `\r` 行尾 64MB(約 2200 萬行)要 18.8 秒,全空行 32MB 要 32 秒。這部分每行一次 yield 與切片是線性,只是常數大。

修法建議:用 `bytearray` 或區塊串列,等找到換行再 join。

## finding 4:計劃檔名本身以 `-std` 結尾時,與另一份計劃的 `-std` 完整審共用同一個帳上編號

severity: minor
blocking: 否 — 目前 346 份計劃筆記沒有檔名以 `-std` 結尾的,且擋下訊息仍指得到出口,只是會誤擋。
引句:「std_id = loop_id + "-std"」
問題:計劃 A 的 `-std` 完整審編號是 `A-std`,計劃 `A-std_計劃` 自己的輕量審編號也是 `A-std`。兩者在 `ctx["by_loop"]` 裡同一格。結果:
- `A-std` 計劃的輕量審一看到帶輪次的列就走「判不了」,一律被導去 `A-std-std`。
- A 的完整審若抓過 major,會讓 `A-std` 計劃的輕量審永久失效。
- 反過來,`A-std` 計劃的輕量審列會讓 A 的 (b) 出口回「審的是 A-std,不是這份計劃」。

審材路徑比對擋住了跨計劃放行,沒有繞過,只有誤擋。這個編號慣例本身沒有分隔,`_spec_gate_full_row` 的 `lp.endswith("-std")` 也同樣分不開。

佐證:file: `scripts/lumos:9476`(`_spec_gate_push_light` 的 `std_id` 那行),file: `scripts/lumos:9261`(`_spec_gate_full_row`)。這是靜態推導,我沒實跑。

## 已讀,無 finding

- `_ledger_physical_lines` 的切行規則:用隨機位元組對照 `_ledger_lines` 整本切法,區塊大小 1、2、3、4、7、16 位元組各 3000 組(含 `\r\n` 跨區塊、結尾剛好 `\r`、空行、最後一行沒換行、中文位元組),行號、內容、起點位移全部一致。
- 非 UTF-8 時例外位置換算(`off + e.start`)與整本解碼時一致;`_loop_status_read` 的壞行、非物件行、超深巢狀行改記行號,沒看到行為倒退。
- `_under_root` 收齊六處:席報告路徑、`reviewed_spec`、`core.hooksPath`、worktree 的 gitdir、lint 樣本、派工鏡頭的計劃路徑。對照舊拼法語意相同(空字串、非字串輸入的行為也一樣)。
- Cf 整類刪除對其他呼叫者:
  - `_cjk_bigrams`:中文字對沒被誤切,夾軟連字號、詞連接符時字對與乾淨查詢一樣。
  - `_cjk_nospace_hint`、`cmd_search` 的空白判斷:只拿去掉後的字串做判斷,不改寫使用者的字。
  - 阿拉伯數字符號 U+0600–0605、軟連字號在非中文用法被刪,只影響查詢比對,威脅模型只顧中英文,不算 finding。
  - `s.isascii()` 的短路是對的。
- `-std` 出口的 NFC 分組:索引的 key 用 `nfc(lp)`,查表用的 `loop_id` 也 NFC,NFD 計劃名對得上。改名、偽造帳列是計劃 d1 已記的天花板。
- `t_zero_width_strip_callers_ok` 第 ② 項(`_cjk_nospace_hint` 回非 None)對這次改動不敏感:`_ANY_SPACE_RE` 本來就不含這些字元,改壞也綠。第 ① 項(字對相等)有效。不另算 finding。

最高等級 major,blocking 1 條。
