severity: minor

## Q1 分層與依賴方向

對齊。`_report_findings_missing_severity` 是模組層級的私有函式(底線開頭),定義緊接在呼叫端 `_report_normalize_issues` 之後,尾端由它自己 `issues.extend(_report_findings_missing_severity(lines, _top))` 呼叫(scripts/lumos:7238),跟鄰居 `_report_severities`(scripts/lumos:7174)一樣是「私有 helper 被同檔 public-ish 函式呼叫」的形狀,沒有跨層直呼。它重用既有的可見行掃描器 `_visible_lines(lines, keep_fenced=False)`(scripts/lumos:7252)與既有的宣告行正則 `_SEV_DECL_LINE_RE`(scripts/lumos:7259),不是另開一套判可見性/判宣告行的邏輯。`cmd_loop_next` 那段只是把既有字串常數 `caught|missed` 換成 `none`,呼叫路徑、參數傳遞完全沒變。

引句:「issues.extend(_report_findings_missing_severity(lines, _top))」

## Q2 命名與錯誤處理

對齊。回傳值形狀跟鄰居一致:`_report_normalize_issues` 全程用 `list[(行號, 原因, 行)]`(如 scripts/lumos:7215、7233、7237 的 `issues.append((no, "...", ln))`),新函式回的 `out.append(cur)` 裡 `cur = (no, "...", ln)`(scripts/lumos:7258)是同一個三元組形狀,拼接後 `_report_normalize_issues` 的呼叫端不用改任何解包邏輯。訊息文字風格(中文說明 + 括號補充「要人做什麼」)跟既有訊息(scripts/lumos:7215「檔首第一個非空行要是檔級 severity...」、scripts/lumos:7237「嚴重度要寫成獨立一行...」)一致。命名 `_FINDING_VERIFIED_WORDS`、`_report_findings_missing_severity` 遵守全檔 `_SEV_*`/`_report_*` 前綴慣例。

引句:「cur = (no, "這條發現沒有自己的一行 severity: <值>(檔首判成非 clean 時,每個 F 段都要有;要請審查席自己補)", ln)」

## F1 verified-words 清單跟既有 SOP 用詞不一致,是另一套沒對齊的詞彙

severity: minor
blocking: no

`_FINDING_VERIFIED_WORDS = ("已驗過", "沒問題", "無 finding", "已讀", "已看")`(scripts/lumos:7242)用來判「這個 F 段是不是已驗過、不用掛 severity」。但全檔唯一寫明「沒問題的段落該怎麼標」的 SOP 原文在 `_CODEX_AGENT_INSTRUCTIONS`(scripts/lumos:17270)——「沒問題的節寫「已讀,無 finding」」,是逗號連接的固定組合語,不是任一詞單獨出現就算數。新函式把它拆成「已讀」「無 finding」兩個可以各自單獨命中的子字串,又多加了三個 SOP 沒提過的同義詞(「已驗過」「沒問題」「已看」)。同一個「這段免填 severity」的判準,現在在檔案兩處各講一套詞彙、彼此沒有連動,以後改 SOP 用詞(例如把「已讀」改別的字)不會有人記得同步這條 tuple。不是跨層直呼、也不是另建掃描機制(`any(w in ln for w in ...)` 這個寫法在 scripts/lumos:7731 已有先例),結構上沒錯,只是詞彙來源沒對齊既有唯一權威定義,故判 minor。

引句:「_FINDING_VERIFIED_WORDS = ("已驗過", "沒問題", "無 finding", "已讀", "已看")」

## Q3 第二種做法

沒有發現引入專案裡原本沒有的獨立做法。可見行掃描沿用 `_visible_lines`(scripts/lumos:7216 一線之隔的同函式已在用)、宣告行判定沿用 `_SEV_DECL_LINE_RE`(scripts/lumos:7172,唯一定義,註解本身就寫著「原本逐字複製了五處,值域改一字要改五處」,新碼沒有重犯這個坑)、子字串批次比對 `any(w in ln for w in (...))` 在 scripts/lumos:7731 已有先例、累加器初始化 `out, cur = [], None` 在 scripts/lumos:22894 已有先例。`cmd_loop_next` 的 `canary record none` 用法在 scripts/lumos:18036 已是既有寫法,不是新發明。F1 提到的詞彙分裂算是「判準來源不統一」而非結構上的第二套機制,已計入 F1、不重複列在這裡。

引句:「for no, ln in _visible_lines(lines, keep_fenced=False):」

不對齊共 1 條,其中 major 0 條
