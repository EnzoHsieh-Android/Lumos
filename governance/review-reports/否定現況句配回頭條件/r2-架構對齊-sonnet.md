severity: minor

整體:已讀全篇並對照 scripts/lumos。掛點(`_note_shape_eval` 加關鍵字參數、`cmd_note_shape` 早退、`_note_shape_doctor_lines` 在 `if ci: return out` 之前)、子開關另寫一支讀法(照 `_note_audit_config` 每道閘各自一支的做法)、字眼表獨立不共用 `NEG_LEXICONS`(照 `_DRIFT_M1_HIST_WORDS` 的「抄自、不引用」與 test_lumos.py 的逐字釘加 `ref.is_file()` 跳過)、提醒標頭帶開關名,都對得上既有做法,沒有引入第二種做法或跨層直呼。以下皆為 minor。

## F1 子開關要等 eval 跑完才讀,關掉了還是會先算提醒、出錯還會印「沒跑完」
severity: minor
blocking: 否
引句:「讀 `note_shape.negation`、組字樣、印出這三步也包在同一個 try 裡」
file: `scripts/lumos:25445`
1. 既有做法:`cmd_note_shape` 在呼叫 `_note_shape_eval` 之前先讀 `note_shape.gate`,`off` 就直接 return 0(scripts/lumos:25445-25450),關掉的東西不會被算。
2. spec 的順序:提醒判定在 `_note_shape_eval` 裡(〈做法〉3 第一條),讀 `note_shape.negation` 排在 eval 之後那個 try 裡。`negation=off` 時 `_ns_negation_hints` 仍每行跑正則;若它丟例外,`error` 被記下,接著印「否定現況句提醒這次沒跑完」給一個已經關掉它的人。
3. 改法:在 gate 讀取旁邊(eval 之前)先讀 negation,`off` 就不傳 `hints`;spec 沒寫這個順序,照字面會做成上述行為。

## F2 「傳進來的容器當出參」的先例指錯地方
severity: minor
blocking: 否
引句:「`gov_events` 也是這種「傳進來的容器當出參」的先例」
file: `scripts/lumos:1324`
1. `gov_events` 是 `cmd_doctor` 內的區域 list(scripts/lumos:1324),同函式內 append;跨函式是用回傳值(scripts/lumos:4920 的 `回 (errs, warns, gov_events)`),不是傳進來的出參。
2. 全檔真有的出參先例是 `_loop_status_disposal(..., result_out=None)`(scripts/lumos:19671)與 `_rules_ids_from_json(data, out=None)`(scripts/lumos:21827)。做法本身可行,但實作者照 spec 找先例會找不到;建議改指 `result_out`。

## F3 「warn」在同一個 note_shape 物件下有兩種語意、既有 docstring 與帳的說法沒同步
severity: minor
blocking: 否
引句:「為什麼不做成 violations 帶一個嚴重度」
file: `scripts/lumos:25380`
1. 既有:`gate=warn` 的提醒是 violations、標頭「提醒(note_shape.gate=warn,不擋)」、寫治理帳 `warned`(scripts/lumos:25472-25476),`cmd_note_shape` docstring 明講「有違規(擋下,或 warn 模式的提醒)與跳過才寫治理帳」。
2. spec 新增的 `negation=warn` 也叫「提醒」「warn」,但不進 violations、不寫帳、走另一個出口。決策理由(violations 有三個消費端)成立,不算第二種做法;但 spec 的〈回退〉〈範圍〉沒列「改 `cmd_note_shape` docstring、Systems 節點裡『warn 一律落帳』的說法」,實作後 docstring 與帳的語意會互相矛盾。
3. 兩個提醒同一次提交都出現時(gate=warn 加 negation=warn),標頭都以「提醒」開頭,讀的人分不出是哪一道;spec 字樣有帶 `note_shape.negation=warn` 可分辨,所以只是文件要同步。

## F4 「去掉列表記號」沒指名用哪一支,量測程式與既有函式各有一套
severity: minor
blocking: 否
引句:「去掉列表記號後以 `RETIRE-IF:` 開頭的行」
file: `scripts/lumos:26673`
1. 既有:`_REVISIT_MARK_RE` 認 `- * +`、`1.` `1)`、`>`(scripts/lumos:26673),`_revisit_split` 用它;spec 同一節第一條對 REVISIT 行也是走 `_revisit_split`。
2. 量測程式 `excluded_v3` 自己寫 `re.sub(r"^(?:[-*+]\s+)", ...)`(governance/eval/negation-revisit/neg_revisit_measure.py:243、245),只認 `- * +`。`1. RETIRE-IF: …還沒…` 兩邊判定不同。
3. spec 又要求 S9 對同一批例句「逐句相同」且正式工具「照搬」;若實作者照「照搬」抄第二份 regex,就是 `_strip_inline_markup` 註解點名禁止的「全檔唯一」以外的第二份。應在 spec 寫明正式工具用 `_REVISIT_MARK_RE`、並把量測程式對齊(或在〈與參考實作的刻意差異〉列這一條)。

## F5 使用說明只列一頁,既有的兩處開關說明沒列入
severity: minor
blocking: 否
引句:「`lumos-project-notes` skill 寫回圖譜那頁補細節」
file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:8`
1. 既有先例:`drift_check.old_sentence` 的開關與行為同時寫進 skills 的 04 與 08(commands/04-自檢與健康.md:12、commands/08-自動跑的.md:7)。
2. `note_shape.gate` 目前寫在 03 第 8 行(說「整個專案先只提醒:`note_shape.gate` 設 warn」),08 第 5 行寫 pre-commit「前四項擋」(note-shape 是其中一項)。新增只提醒的輸出與 `note_shape.negation` 後,這兩處會變成不完整。
3. spec 〈範圍〉③ 只提 03 那段教寫法;沒提要在 03 第 8 行與 08 第 5 行補一句提醒與子開關。

## F6 提醒段與 block 尾句、治理帳的先後,跟既有 block 分支的結構沒對上
severity: minor
blocking: 否
引句:「有違規時先印違規段、再印提醒段(block 的回 1 在兩段都印完之後)」
file: `scripts/lumos:25462`
1. 既有 `cmd_note_shape`:印完違規行後,在 `if mode == "block":` 分支內先印尾句「內容還在工作目錄,改完再提交…」、寫 `blocked` 帳、`return 1`(scripts/lumos:25462-25470);warn 分支寫 `warned` 帳(scripts/lumos:25472-25475)。
2. spec 要求提醒段插在違規段之後、`return 1` 之前,但沒說 block 尾句在提醒段之前或之後。照字面,提醒段可能夾在違規行與「為什麼擋」尾句之間,或尾句之後才印。建議明寫:提醒段印在尾句之後、帳寫完之後(提醒失敗也不影響帳),不然實作者要自己拆那個 if 分支。

最高等級:minor;blocking 共 0 條
