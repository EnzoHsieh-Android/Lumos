severity: major

審稿範圍:spec 全文(`/tmp/舊句兩道轉擋-r3.md`)對照 `aspidochelone-reread-block` 的 `scripts/lumos`、`scripts/hooks/pre-push`、`governance/reread-verdicts/` 5 份真實紀錄。實驗檔在 `/tmp/lumos-seat-work/舊句兩道轉擋/邊界3-sonnet/`(t1、t3、t4、t5),都是 import 真實函式後實際執行。派工沒附固定席節點,所以沒有「破壞節點合約」要判的項目。

### F1 比對字串可以是空字串,會把整篇筆記所有規則類條目都判成「被點出」
severity: major
blocking: 是
判準:照字面實作,判定紀錄裡一列只要 `quote` 非空、`text` 是空白行,就會誤擋同一篇的每一條規則類條目;而判定者把行號抓偏一行就能造出這種輸入。

- spec 段落:〈重讀:候選與兩層〉第二層「逐列決定比對字串」那條,以及 S12。
  引句:「兩者都是空字串 → 這一列點不出任何行,略過」
  S12 的測試只涵蓋 `quote` 與 `text` 都空。
- 輸入:判定紀錄一列 `{"line": 7, "quote": "某個被改動弄舊的句子", "text": ""}`。`text` 是空白行或檔尾那個空行,`quote` 不是 `text` 的子字串。
- 壞在哪:
  - 依 spec,`quote` 不是 `text` 的子字串,所以改用 `text` 去頭尾空白,得到 `""`。
  - 這時 `quote` 非空,「兩者都空」不成立,不會略過。
  - `""` 是任何一行的子字串,於是「含它的每一個實體行」等於全部摘要行,每條規則類條目都算被點出,全部要處理。
  - `drift ack` 的前置條件「某列比對字串出現在這一條」同樣被 `""` 滿足,所以逃生口不會擋。
- 這個輸入進得了紀錄:
  - file: `scripts/lumos:34873` 寫入時 `r["text"] = lines[r["line"]-1] if r["line"] <= len(lines) else ""`。
  - file: `scripts/lumos:34604` 的 `筆記行數` 是 `len(text.split("\n"))`,所以檔尾空行也算合法行號。
  - file: `scripts/lumos:34670` 的 `_note_reread_rows` 只檢查行號範圍,不驗 `quote` 是否在該行。
- 實驗:`python3.14 -I t4.py`,note 為 9 行(含空行)、規則在第 4、5 行,兩列行號 7 和 9 都被收下:
  ```
  7 '' cmp= '' hits summary lines: [3, 4, 5]
  9 '' cmp= '' hits summary lines: [3, 4, 5]
  ```
- 修法方向:「略過」的條件改成看最後選定的比對字串是否為空。`text` 退回路線另設最短字數,或乾脆用該列 `line` 對 `note_blob` 定位條目,再對到頂端版。

### F2 單行 summary 的規則條目:第二層會擋,但 `drift ack --kind reread` 表態不了
severity: major
blocking: 是
判準:擋下訊息印出的逃生指令照貼會回 2,這個條目只剩改筆記或環境變數略過兩條路,違反「兩層可表態處理」的合約。

- spec 段落:
  - 〈第二層〉:「用 `_note_summary_entries` 同一套讀法(…單行 summary 整個值算一條)」
  - 〈照留表態〉:「行號要是一條摘要條目的開頭行(跟 retire 一樣,記整條)」
  - 兩邊用的是不同的讀法。
- 輸入:筆記 `summary: "RULE:單行規則 [依據:人] [since:2026-01-01] [retire:人裁] [until:2027-01-01]"`(單行),被判定紀錄點出。
- 壞在哪:
  - file: `scripts/lumos:4027` 的 `_note_summary_entries` 會把它列成第 3 行的一條。
  - file: `scripts/lumos:37453` 的 `_drift_ack_line_err` 和 file: `scripts/lumos:37444` 的 `_drift_ack_text` 都寫死 `kind == "retire"`,用 `_ns_summary_logical`,而它對單行 summary 回 `{}`。
  - 所以 `drift ack <節點> 3 --kind reread` 被「不是摘要裡一條的第一行」擋成 rc 2。
  - 就算放行,`_drift_ack_text` 會記實體行 `summary: "RULE:…"`,對不上檢查端的整條原文,表態永遠不涵蓋。
  - spec 的「要一起改」清單沒提這兩支函式,只靠「跟 retire 一樣」一句話。
- 實驗:`python3.14 -I t1.py`
  ```
  single logical: {}
  single entries: {3: 'RULE:單行規則 [依據:人] …'}
  single ack_line_err retire: x.md 第 3 行不是摘要裡一條的第一行——…
  single ack_text: 'summary: "RULE:單行規則 [依據:人] …"'
  ```
- 修法方向:`_drift_ack_line_err` 與 `_drift_ack_text` 對 reread 改走 `_note_summary_entries`,並補一條單行 summary 的驗收條款。

### F3 比對字串太泛會誤擋同一篇的其他條目(真實筆記就有)
severity: minor
blocking: 否
判準:被點出的條目以外也被擋,誤報率偏高,但每條都能表態。

- spec 段落:第二層「找出含它的每一個實體行」,`quote` 下限只有 6 個字。
- 輸入:判定者的 `quote` 剛好是欄位字串或共用的測試綁定,例如 `[test:t_memory_sweep_core]`。
- 壞在哪:`docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md` 裡這個字串出現在 7 條不同條目。引句 ≥6 字又是 `text` 的子字串,就用它比對,結果 7 條規則類條目全部要處理。紀錄本身有 `line` 與 `note_blob`,可以精確定位,spec 卻完全不用。
- 查證:
  ```
  grep -o "\[test:[^]]*\]" Systems/記憶過期清掃.md | sort | uniq -c
  ```
  最高的是 `7 [test:t_memory_sweep_core]`。

### F4 `text` 欄缺漏或不是字串時,一份壞紀錄會讓整個推送被「沒預料的例外」擋住
severity: minor
blocking: 否
判準:spec 的判不了條件寫成「`quote`/`text` 都不是字串」,只缺一邊的列不在其中。

- spec 段落:引句:「某列不是物件或 `quote`/`text` 都不是字串 → 判不了」
- 輸入:一列有字串 `quote` 但沒有 `text`(或 `text` 是 null)。
- 壞在哪:實作到「`quote` 是否為 `text` 的子字串」時會丟 `TypeError`,落進「沒預料的例外」,block 模式下整個推送回 1,而不是只處理那一份紀錄。
- ⚠ 這份紀錄要手改才造得出來,所以只標 minor。

### F5 規則條目任何一次編輯都讓已有的表態失效,而舊紀錄永久還在
severity: minor
blocking: 否
判準:例行維護動作(補 `[confirmed:]` 日期)就會讓擋下重現,要重新表態一次。

- spec 段落:
  - 引句:「同一路徑、同一條目原文(整條,接續行併回後去頭尾空白)」
  - 引句:「判定紀錄只增不減」
- 輸入:判定紀錄點出規則條目 E,作者表態後,再把 E 的 `[confirmed:]` 往後改一天。
- 壞在哪:
  - 表態鍵是整條原文,日期一改鍵就換了。
  - 引句還在,而第二層讀的是該筆記的全部歷史紀錄,不分是不是這次推送的指紋,所以又擋。
  - 這是設計取捨,spec 寫了「改掉比對字串才放行」,沒寫「表態遇到條目編輯會失效」。
- ⚠ 屬於可接受的摩擦,建議在〈實務隱患〉補一句。

### F6 摘要區裡「沒前綴的行」的歸屬,兩處規則不一致
severity: minor
blocking: 否
判準:第二層的歸屬規則與它聲稱沿用的讀法對同一輸入給出不同答案。

- spec 段落:
  - 引句:「實體行落在某條目的開頭行到下一條目之前,就屬於那一條」
  - 同一段又說用 `_note_summary_entries` 同一套讀法。
- 輸入:
  ```
  summary: |-
    RULE:甲…

    無前綴行 含引句XYZ
    WHY:乙…
  ```
- 壞在哪:`_note_summary_entries` 只把更深縮排的行接回條目,所以「無前綴行」不屬於 RULE 甲。依 spec 的位置規則卻屬於,引句落在那行就會擋 RULE 甲。
- 實驗:`python3.14 -I t3.py` 輸出 `{4:…, 7:…, 8:…}`,5 到 6 行不歸任何一條。

### F7 `_note_reread_show` 把不同的非 UTF-8 路徑轉成同一字串,第二層會張冠李戴
severity: minor
blocking: 否
判準:極端輸入下兩篇筆記共用一批紀錄。

- spec 段落:引句:「取 `note` 欄經 `_note_reread_show` 轉換後等於這篇路徑同一轉換的」
- 輸入:兩篇筆記路徑分別含 `\xff` 與 `\xfe` 位元組。這種路徑照 spec 仍是合法候選,控制字元才被排除。
- 實驗:`python3.14 -I t5.py`
  ```
  'a\udcffb.md' -> 'a�b.md'
  'a\udcfeb.md' -> 'a�b.md'
  ```
  兩個路徑撞成同一字串。
- 修法方向:比對用原始字串(JSON 能無損帶替身字元),顯示才過 `_note_reread_show`。

### F8 寫入端不限紀錄大小,讀取端卻拒收超過 256 KB 的檔
severity: minor
blocking: 否
判準:`reread-record` 寫得出的檔,下次推送在 block 模式下就判不了。

- spec 段落:引句:「單檔上限 256 KB、全部上限 8 MB;單檔超過、…判不了」
- 壞在哪:file: `scripts/lumos:34873` 的 `text` 不截斷,`quote`/`why` 才截到 500。寫入沒有大小檢查,而讀取是 `n > max_bytes` 才排除,剛好 256 KB 還能讀,超過就判不了。
- 觸發條件要很多列或超長行,實際不太會出現。
- ⚠ 恢復路徑是 `git rm` 該檔,會讓第一層要求重判,代價較高。

### F9 判不了的分類沒涵蓋 `_NoteRereadStop` 的所有來源
severity: minor
blocking: 否
判準:實作者要自己猜每個 raise 點該回 1 還是 0。

- spec 段落:〈回傳碼與判不了〉三類清單。
- 例子:file: `scripts/lumos:34957` 前後的「推送範圍的起點算不出來」(`_PUSH_START_UNKNOWN`)是 git 查詢失敗。spec 只明列「`undecidable`、逾時、判定紀錄讀不了…、沒預料的例外」,這一個只能靠類推歸到判不了。
- 另一個要補的是 file: `scripts/hooks/pre-push:541` 目前只把 130 交給 `pp_stop_if_signaled`,spec 改成 128 以上。這是行為變化(OOM 被殺會停整支推送),建議在 CHANGELOG 一併寫明。

### 實務隱患鏡頭(逐類)
- 金流:無。只動本機掛鉤與回傳碼(spec 已排除,我同意)。
- 不可逆:無。表態檔只追加,擋下可用環境變數或設定回復。
- 對外送出:既有風險,spec 已寫。判定要把筆記全文和 diff 交給外部模型,現在變成必經步驟,有保密要求的專案要設 warn 或 off。
- 守衛面:有。F1、F2 就是守衛本身的誤擋與逃生口失效。
- 並行會談:spec 沒提主程式 `scripts/lumos` 每個提交都會改,第一層對共用工作樹的分支指紋會一直變。這已在〈第一層的成本〉承認,不另標。
- 數字查證:5 份紀錄共 7855 位元組、5 份,與 spec 的「約 7.8 KB」吻合。另外真實紀錄的列對照後,規則類條目為 0 的宣稱成立:第 1 份唯一命中的第 57 行在 frontmatter 之外,屬於正文,不算數。

已讀,無 finding 的段落:〈開關〉、〈照留表態〉的 `_DRIFT_BOUND_KINDS` 取捨、〈掛鉤與 CI〉的 CI 維持不帶 `--gate`、〈回退〉、REVISIT 日期(2026-10-09 加 56 天為 2026-12-04)。

最嚴重的是 F1(比對字串為空時整篇規則條目全被判成點出)與 F2(單行 summary 條目表態不了),blocking 共 2 條。
