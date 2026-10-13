severity: major

審查範圍是 5242975c 對 ff6565ec 的修補,實驗在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-邊界輸入-sonnet/`(repo 為修後、repo_before 為修前)。共 7 條:3 條擋合併、4 條不擋。

**圖譜固定席回應**
- `Systems/lumos-cli-write.md`:「帳任一步失敗用同一 fh 截回原長度」那句,我用 RLIMIT_FSIZE 實測不成立(見 1)。這句掛的 `t_qfm_r8_signoff_and_write_refusal` 是假檔案把手,自己先 flush,抓不到真實緩衝殘留。
- `Projects/待決問題改存開頭欄位_計劃.md` 的蒙古變體選擇符寫「只准一個」。程式其實是每個選擇符各接一個蒙古字母、整體受總量限制,同一值放兩個也過。依程式碼為準,這是筆記措辭不精確。
- `Systems/規格閘.md` 的「文法表外的每一種寫法都判無法判定」:見 2,引號鍵加空白、flow 內帶 anchor/tag 的鍵、`-<tab>` 目前會靜默漏掉,與這句不符。
- `Systems/lumos-cli-read.md`:沒發現過期。已刪除的 `_pq_decisions_section`、`_pq_scalar_list_section`、`_pq_top_key`、`_PQ_BLOCK_HEADER_RE`、`_write_symlink_reason` 在 docs 與 scripts 都搜不到殘留。

1. 簽核帳寫到一半失敗,截回原長度也失敗,帳留半行,下一筆正常簽核被黏壞。
引句:「fh.truncate(log_pos)」
file: `scripts/lumos:9145`
severity: major
blocking: 是
- 原因:`BufferedWriter.truncate` 會先 flush 殘留緩衝,磁碟寫滿時又失敗一次,所以截回動作本身沒做成。
- 重現(RLIMIT_FSIZE 模擬寫滿):`python3.14 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-邊界輸入-sonnet/fsize.py repo`
- 修後輸出:`簽核帳還原失敗:[Errno 27] File too large;帳可能留有半行`,帳多出 40 位元組。
- 再簽核一次:帳出現解析不了的行 `{"ts": "...", "node": "P{"ts": "...", ... "note": "第二次正常簽核"...}`,後面那筆好簽核一起壞掉。
- 修前(同命令跑 `fsize.py repo_before`):帳長度差 0,筆記已還原。
- 歸因:有證據的修復回歸。

2. 性質甲:引號鍵「鍵 空白 冒號」、flow 內帶 anchor/tag 的鍵、`-<tab>` 起頭的整題,在清單外靜默消失。
引句:「if j < 0 or t[j + 1:j + 2] != ":" or t[j + 2:j + 3] not in」
file: `scripts/lumos:7152`
severity: major
blocking: 是
⚠ 實際會有人這樣寫的機率低,但這正是性質甲點名要擋的形狀。
- 重現:在 `pending_questions` 清單前或後放下列任一行,`pq_parse` 都回 0 個錯誤。
  - `"id" : Q2`
  - `"text" : x`
  - `'stage' : x`
  - `foo: {&a text: x}`
  - `foo: {!!str id: Q2}`
  - `foo: {"id" : Q2}`
  - `-<tab>id: Q2`
- 對照:`"id": Q2`(冒號緊貼)與 `ID : Q2`(沒加引號)都會被擋。
- 修前同樣 22 組變形輸入(含 `? text`),上面這幾條全判無法判定。
- 修前驗證:`cd /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-邊界輸入-sonnet && python3.14 -c "import sys;sys.path.insert(0,'.');from hb import LB;print(LB.pq_parse(['title: t','\"id\" : Q2','pending_questions:','  - id: Q1','    text: a','    class: c','    stage: 需求','    status: 待查'],2)[2][:1])"`
- 歸因:有證據的修復回歸。清單外改成只看鍵名後,舊的整行文法拒讀被拿掉,鍵名判斷沒補上這幾種寫法。

3. 清單外逐行掃描對重複 `- ` 是平方級耗時。
引句:「text, prefixes = text[2:].lstrip(" "), prefixes + 1」
file: `scripts/lumos:7205`
severity: major
blocking: 是
⚠ 需要超大單行,但 lint、spec-gate、pre-commit 都會讀這份開頭欄位。
- 重現:`["- "*300000+"x: 1"]` 後接任一題,跑 `pq_parse`。
- 修後耗時:30 萬字元 5.3 秒、60 萬字元 20.4 秒(8 萬字元 0.3 秒)。
- 修前同樣輸入:0.00 秒。
- 歸因:有證據的修復回歸。`_pq_line_mapping`、`_pq_questionish_key`、`_pq_structure_marker_problem` 每剝一次 `- ` 就複製整個字串。
- 同一輪其他極端輸入都正常:20 萬行 0.64 秒、200 萬字元 `[` 巢狀瞬間、2 萬題 0.35 秒。

4. 「看不見字元」總量上限會誤擋真實長文。
引句:「return hidden > limit or sum(1 for c in v if _pq_is_default_ignorable(c)) > _PQ_DICP_TOTAL_MAX」
file: `scripts/lumos:7065`
severity: minor
blocking: 否
- 波斯文 192 字、含 10 個 ZWNJ 的一句正常問句被擋,訊息是「值裡看不見的字元太多」。一般波斯文每個「می‌」與「ها」都帶 ZWNJ,長一點的段落都會超過 8 個。
- 僧伽羅文 99 字、12 個 ZWJ 同樣被擋。
- emoji 方面:6 個家庭 emoji(18 個 ZWJ)、17 個 ❤️(17 個 FE0F)、9 個以上彩虹旗都超過總量 16 被擋。
- 修前 `_strict_scalar` 全放行,修後被擋。
- 歸因:有證據的修復回歸。計劃已有 2026-11-13 的 REVISIT,這裡只補實測樣本。

5. 預設全擋的看不見字元,會擋掉合法書寫。
引句:「def _pq_dicp_kind_ok(v, i):」
file: `scripts/lumos:7028`
severity: minor
blocking: 否
⚠ 這是政策取捨,不是實作錯。
- 被擋的合法寫法:
  - 希伯來文與阿拉伯文的 RLM/LRM/ALM/雙向隔離符(U+200F、U+200E、U+061C、U+2068)
  - 高棉文與泰文用 ZWSP(U+200B)分詞
  - 日文人名用的異體字序列(葛 + U+E0100)
  - 蒙古文 U+180E
  - 馬拉雅拉姆舊式詞尾 ZWJ
  - 波斯文數字後接 ZWNJ
- 修前也擋(同樣的 `_strict_scalar` 輸入)。
- 歸因:有證據的原有漏查。要不要放行屬於人裁。

6. 私用區與未指派碼位不受任何限制,也算進可見字數。
引句:「值裡第一個不准出現的字元；DICP 預設全擋，只放行規格列出的合法位置。」
file: `scripts/lumos:7082`、`scripts/lumos:35765`
severity: minor
blocking: 否
⚠ 這些字元在多數字型是方框而非隱形,風險程度未定。
- `_strict_scalar("x"+"\ue000"*200)`、`"x"+"\u0378"*200`、`"a\ufdd0b"`、`"a\U0001ffffb"` 都通過。
- 原因:`_PATH_SPECIAL_CATS` 只含 Cc/Cf/Zl/Zp/Cs,沒有 Co 與 Cn,而性質乙要擋「任意、高容量的看不見通道」。
- 修前同樣通過。
- 歸因:有證據的原有漏查。

7. `decision-amend` 對換行的處理不一致。
引句:「if len((str(v) + "x").splitlines()) > 1:」
file: `scripts/lumos:21271`
severity: minor
blocking: 否
- `decision-amend --text` 含 `\n`:靜默把換行壓成空白,內容變成「丙 stage: 架構 text: x」,rc 0。
- 含 `\r` 或 `\x85`:被拒,rc 2。
- 修前三種都 rc 0。
- 性質丙只點名 `decision-add`,所以這是原有路徑的殘留。
- 歸因:有證據的原有漏查。

**三問**
- ① 原問題的修復效果:
  - 性質甲的主體有效。同形字、零寬字元、`Id`/`iD`、`id: |`、`|2`/`|+` 等怪標頭、block scalar 內容縮排邊界、`- ` 加兩空白,都照規則處理,各案例以實跑為準。
  - 用 lumos 自己的指令以各種順序組合造筆記,每一步跑 lint 與 `spec-gate --no-run` 都讀得懂。涵蓋 append、decision-add(含 `text: x` 這類內容)、decision-amend、decision-supersede、question-add、question-set、summary-line、signoff、guard bind,以及 set 對 10 個允許欄位帶 11 種惡意值的掃描。
  - 1259 份真實 md 在最前與最後插入一題都讀得懂,另有 60 份副本實跑 `question-add` 都讀得懂。
  - 性質丙中,符號連結與 `nlink>1` 對 signoff、set、append、question-add、decision-add、guard bind、`new` 回掛都乾淨拒寫,目標不變,控制字元已清洗。
  - 性質乙的 13 個語系、國旗、鍵帽、膚色、家庭、職業、❤️‍🔥、🏳️‍⚧️、🐦‍🔥 這類新 emoji 都放行。
  - 反例是上面 1 到 3。
- ② 相鄰路徑:
  - 正常路徑仍成立:簽核成功仍印兩行,筆記庫的 `load_raw_for_edit` 讀取、BOM、CRLF 拒絕照舊。
  - 異常路徑有缺口:帳檔是目錄時訊息誤寫「多個硬連結」(目錄的 nlink 本來就大於 1),是訊息不準的小瑕疵。
  - 其他寫入點沒走 `_write_refusal_reason`:report-normalize、`22732` 附近的 os.replace 改寫、guard 新建檔。這些修前也沒走,不算回歸。
- ③ 同一案例修前與修後:
  - 帳寫滿(1):修前還原成功,修後留 40 位元組半行。
  - `"id" : Q2` 與 `{&a text: x}`(2):修前判無法判定,修後靜默通過。
  - 60 萬字元 `- ` 行(3):修前 0.00 秒,修後 20.4 秒。
  - 長波斯文(4):修前放行,修後被擋。
  - RLM、ZWSP、PUA(5、6):修前修後都一樣。

總結:性質丙的簽核回滾在真實寫滿時反而比修前差,性質甲的鍵名判斷漏掉引號鍵加空白等寫法且有平方級耗時,這三條要先處理。
