severity: minor

整體判斷:這次修補沒有弄壞既有功能。我在 spec-gate-nondo 跑了三組測試子集,結果如下:

| 關鍵字 | 通過 | 失敗 |
|---|---|---|
| `zero_width` | 41 | 0 |
| `nogo` | 309 | 0 |
| `loop_next` | 107 | 0 |

其中沒有跑 `-k loop_status`、`disposal`。

以下是兩條 minor,都是修補沒做到宣稱的地方,不擋推送。

severity: minor
blocking: 否 — 只有作者刻意夾字元才會繞過,而且「夾一個空白就繞過」本來就存在,這條不是新破口,只是「整類拿掉」的說法不成立
引句:「另加不歸 Cf 但一樣看不見的:變體選擇符」
問題:`_strip_zero_width` 號稱整類拿掉隱形字元,但名單之外還有看不見或近乎看不見的字元沒拿掉。r8 說的「同一族第三次被換個字元打穿」的結構沒變,只是名單變長。
具體失敗情境:我用 `_door_keyword_hits` 實測,下列字元夾進「退款」或「payment」中間,命中都是空的,計劃仍會被判成風險低:
- 蒙古文自由變體選擇符 U+180B 與 U+180F
- 高棉固有母音 U+17B4
- 盲文空白 U+2800
- 物件替代字元 U+FFFC
- 組合重音 U+0301
- 藏文 U+0F0B
- 不換行空白 U+00A0

對照組:U+2060、U+00AD、U+2064、U+061C、tag 字元和音樂記號 U+1D173(都是 Cf),都被正確拿掉。
佐證:``scripts/lumos: `scripts/lumos:5021` ``(`_strip_zero_width`)與 `scripts/lumos:8141`(`_door_scan_text`)。
建議:計劃和 docstring 不要寫「整類」,改成「名單內」。或者承認字面比對擋不完,把天花板寫進計劃的撤除條件。

severity: minor
blocking: 否 — 要帳檔真的有壞行才觸發,而且單人依序操作的威脅模型下接受
引句:「讀帳讀不懂的行在索引那一頭就跳過(跟 (a) 同一個接法」
問題:(b) 出口改走 `_disposal_judge` 之後,呼叫時沒傳 `bad_linenos`,帳上讀不懂的行不再讓處置閘 fail-closed。這是行為退步:修補前 (b) 叫 `cmd_loop_status`,遇到壞行直接 rc2,它的訊息是「審查記錄檔有 N 行讀不懂,沒辦法確定最後一輪是哪輪」。現在同一份帳,`loop status --disposal` 仍是 rc2,但推送前的 (b) 出口可能放行。這是我讀程式推得的,沒有造帳實跑。
具體失敗情境:最新一輪的 major 席列因磁碟截斷變成壞行。(b) 看不到那一列,只剩較早的乾淨輪,處置閘判收斂,推送放行。`ctx["skipped"]` 只在「已經擋下」時附一句,放行時完全沒有訊號。
佐證:``scripts/lumos: `scripts/lumos:13558` ``(`_disposal_judge` 呼叫 `_loop_status_disposal` 時用 `len(bad_linenos)`)與 `_nogo_full_review_gate` 內的 `_disposal_judge(...)` 呼叫。
建議:(b) 把 `ctx["skipped"]` 當 `n_badlines` 傳進去,跟 `loop status --disposal` 對齊。或者放行時也把「跳過 N 行」印出來。

已讀,無 finding:
- `_disposal_judge` 抽出:`loop next` 以前由 `cmd_loop_status` 做的 `--spec` 為空檢查,在 `loop next` 上游(`spec is None` 的 gate-pending 分支)已經攔掉。`loop status --disposal` 的輸出與退出碼語意不變。
- `cmd_loop_status` 讀不懂的行改成 rc2:legacy 與 panel 模式不看壞行數,只有 settle 與處置閘 fail-closed,所以其他模式不受影響。原本會崩潰的非物件行和超深巢狀行,現在算壞行,是改善。
- 逐行讀取 `_ledger_physical_lines`:我用 1、2、3、5、64 位元組五種區塊大小,各隨機 3000 次,含 `\r`、`\r\n`、多位元組中文。切行結果、行號、位元組起點都跟 `_LEDGER_LINE_RE_B.split` 完全一致,沒有不一致。
- `_strip_zero_width` 對 search 與 `_cjk_bigrams`:四個呼叫端都只拿去掉後的字串做比對,不改寫使用者文字,整類刪除成立。`❤️` 去掉 U+FE0F 後仍是原文的子字串,不會漏。效能:2M 個中文字約 0.39 秒,1MB 計劃掃一遍約 0.36 秒。
- 六處改用 `_under_root`:結果跟原寫法逐一相同。`_hooks_path_dir`、`_events_main_trusted`、`cmd_rule_check`、`cmd_dispatch_lens_spec`、`_severity_check_row`、`reviewed_spec` 都是「絕對路徑照用,相對路徑接在根底下」。`root=None` 時從原本的 TypeError 變成回傳相對路徑,不是退步。
- 門規則版本 7 與既有風險低留痕:留痕裡的 `door_rule` 比目前低,只在重判結果變高時才提示「規則較舊」。重判仍是低的留痕,不受版本號影響。
- 接上主線 a132aa6e:沒看到跟推送前收集、通才鏡頭有互相影響的呼叫點。`_spec_gate_ledger_index` 與 `_canary_ledger_rows` 新增的參數都有預設值。
- 記憶體:`_spec_gate_full_row` 讓非 code- 編號的帶輪次列整列保留。以本庫的帳實測是 4535 列裡留 1812 列,約 1.7MB,可接受。

最高等級 minor,blocking 0 條。
