severity: major

## F1 條件標記的「行內反引號不算」規則,借用清單漏列全檔唯一的剝碼函式,可能被實作成第二套反引號解析

severity: major
blocking: 是 — 條件解析若照借用清單只用 `_visible_lines`(只剝圍欄)去做,會漏做行內反引號剝除,範例句裡 `` `[when-file:...]` `` 這種示範文字會被誤判成真條件(或反過來,實作者為了滿足「行內程式碼裡的標記都不算」這條要求,自己手刻第二套反引號正則),兩種結果都是錯的系統行為。
引句:「⑥可見行判定借 `_visible_lines`(跳過圍欄)」

1. §0 規定「圍欄內的行、表格行、行內程式碼(一對反引號)裡的標記都不算——那是範例」,但 PRIOR-ART/借用清單第⑥項只寫「可見行判定借 `_visible_lines`(跳過圍欄)」,只借了圍欄剝除,沒有借「行內反引號」剝除那一半。
2. `scripts/lumos` 裡「哪些字看得見」是明確的兩函式配對:`_visible_lines`(行層級,只管圍欄與跨行註解)+ `_strip_inline_markup`(行內層級,管雙反引號 span、單反引號 span、未閉合反引號截斷),兩者已合成 `_strip_code_text`;程式碼原文的告誡是「★全檔唯一★,別在別處自寫第二份(條款綁定 -b r2 架構席:三條規則散在 clause_bindings 裡就是第二份)」(`scripts/lumos:166`,`scripts/lumos:184`)。
3. §0 沒有把 `_strip_inline_markup`/`_strip_code_text` 列進借用清單,也沒有在〈自建〉清單裡明講「行內反引號剝除另外自己刻」——是完全遺漏,不是刻意排除。條件標記解析器要滿足 S9(「只認正文與摘要的可見行(不含圍欄、表格、行內程式碼)」),照現在寫法最可能的實作路徑是另開一個正則去剝行內反引號,正好複製這個檔案已經明文記過一次的架構事故形狀。
4. 修法很直接:借用清單第⑥項改成「借 `_strip_code_text`(圍欄+行內反引號一次剝)」,或明講「借 `_visible_lines` 做圍欄、再借 `_strip_inline_markup` 逐行剝反引號」。

## F2 「同一行」判定自認「既有工具沒有可借的」,但 `_notelines_new`/`_notelines_range_added` 已經做了同一件事,而且正是筆記形狀擋與筆記內容審共用的那一支

severity: major
blocking: 是 — S9 要求 check 對「舊行只擋起點不成立、終點成立」、「新寫而終點已成立的只列出」,這個新舊行判定若照 PRIOR-ART 宣稱的「既有工具沒有可借的」重新刻一套 git 改名追蹤+逐提交新增行比對邏輯,很容易在合併提交、改名同時改寫內容等邊界情況上跟既有那一支(已經被兩輪代碼審打磨過)走不同語意,導致同一行在 drift check 跟筆記形狀擋/筆記內容審裡被判成不同的「新/舊」,擋的時機互相矛盾。
引句:「考試指令——既有工具沒有可借的。」

1. §0「「同一行」怎麼認」段落描述的演算法是:「先用 git 的改名偵測把終點的筆記路徑對回起點的路徑,再看起點那篇裡有沒有**一字不差**(去頭尾空白)的同一行;有就是舊行,沒有就算這次新寫的。」
2. `scripts/lumos:23601` 的 `_notelines_range_added` 已經做了完全一樣的事:對範圍內每個提交做改名偵測(`_renames`/`_carry`,用 `git diff --name-status -M`)、把改名前寫的行搬到終點路徑鍵下、逐提交累積「這個提交自己新增的行文字」集合;`_notelines_new`(`scripts/lumos:23690`)的文件字串明講這是「筆記形狀擋與筆記內容審共用」的那一支。也就是說,判斷「一篇筆記裡的某一行,是不是這次範圍新寫的」這件事,已經有一支被兩層閘共用、跑過代碼審多輪修過邊界(合併提交、側分支改名、上線點前後)的既有實作。
3. PRIOR-ART 借用清單①-⑦逐項列了很細的借用(推送起點、樹讀取器、測試判定、版面計算…),獨獨「同一行」判定被歸進〈自建〉,而且明講「既有工具沒有可借的」——這句話跟 2 對不上:能借的東西存在,只是沒被點名。
4. 這不是吹毛求疵的風格差異:drift check 需要對 TIP 版本裡「每一行帶條件標記的行」分類新/舊,而 `_notelines_new` 目前只回傳「新行」清單(`notes`/`texts_by`),沒有直接暴露「給一行文字,判它新不新」的介面——要接上確實要動一點既有函式(例如多回傳 `texts_by` 或加一個查詢介面),但這和「既有工具沒有可借的,只能自己重刻整套改名偵測邏輯」是完全不同等級的工作與風險。照 PRIOR-ART 現在寫法,實作者沒有理由不從零開始寫第二套「這行是不是新寫的」判法。
5. 修法:PRIOR-ART 改成「借 `_notelines_new`/`_notelines_range_added` 的改名追蹤與逐提交新增行集合(必要時擴充回傳值暴露給呼叫端做逐行查詢),不重建 git 改名偵測」。

## F3(minor)`lumos drift ack` 寫 `governance/drift-acks.jsonl` 沒有點名複用既有的「寫入+讀回自驗」硬化原語

severity: minor
blocking: 否 — 寫入失敗最壞結果是使用者以為表態成功、下次推送仍被擋,當場就會發現、不會造成資料損毀或誤放行(跟 canary-record 那次「回報成功但沒落盤」的事故不同等級)。
引句:「寫進 `governance/drift-acks.jsonl`(加進簿記豁免),每筆存:路徑、行的原文、種類、理由、日期、表態時的小標題與行號(只供人讀)。」

1. `scripts/lumos:8209` 的 `_jsonl_append_verified(path, rec, key_field, key_value)` 是專門為「append 一行 JSONL 後讀回自驗」寫的共用硬化原語,文件字串點名出身是「2026-07-28 record 回報成功未落盤事故」,現在已經被 canary-log、code-loop 記錄、另一個 dedup_key 用途(`scripts/lumos:27172`)等至少五個呼叫點共用。
2. 〈做法〉第 0 節對 `drift ack` 只講寫進哪支檔、加進簿記豁免,沒有點名要不要借這支自驗原語;PRIOR-ART 借用清單裡也沒提到它。表態檔的正確性直接決定 c1 擋不擋,值得跟既有的「寫入+讀回自驗」對齊,而不是留給實作者自己決定要不要驗。
3. 修法:PRIOR-ART 或〈做法〉第 0 節補一句「表態檔寫入借 `_jsonl_append_verified`」,或者明講「不借,理由是失敗即刻可見、風險比 canary-record 低」——兩者都比現在的沉默好。

## 其餘節次:已讀,無 finding

- §0 推送範圍起點/上線點截斷(借 `_lens_push_base` + `_nodehome_clamp_base(mark=..., hook=_NOTELINES_PREPUSH)`):實地核對 `scripts/lumos:22967`(`_nodehome_clamp_base`)、`scripts/lumos:24407`(`_note_audit_resolve`),spec 明確要求照筆記內容審那一處用推送前掛鉤的標記(不是筆記形狀擋用的提交前掛鉤標記),跟程式碼現況（`_NOTE_SHAPE_GOLIVE_MARK` 找 `scripts/hooks/pre-commit`、`_NOTE_AUDIT_GOLIVE_MARK` 找 `scripts/hooks/pre-push`)完全對得上,沒有借錯層。
- §0 測試檔判定「借 `_nodehome_is_test`,並照它的要求先用那棵樹的全部路徑算版面(`_nodehome_layout`)再傳進去」:核對 `scripts/lumos:22453`(`_nodehome_is_test(path, layout=({}, {}))`)與 `scripts/lumos:22402`(`_nodehome_layout`),簽章與呼叫順序要求完全對上,spec 正確理解了這支函式不能只傳路徑、必須先算版面。
- §0/落點 治理帳寫入:新閘名 `drift-check` 走 `_KNOWN_GATES` 單一登記點(`scripts/lumos:6604`)、事件走既有 `_gate_event`/`_gate_event_or_warn`(`scripts/lumos:856`起)——沒有另開治理帳寫入函式,也沒有繞過名單檢查,落點節也正確點名要去 `Systems/reversibility-governance-ledger` 補登記,跟既有唯一寫入器的設計一致。
- 〈做法〉第1節 settle 寫入順序與鎖:「整個 settle 包在 `_vault_write_lock` 裡」、「補救路徑」與 spec 自己引用的「照 `cmd_set`」比對過 `scripts/lumos:14300`(`cmd_set` 用同一把鎖包住讀改寫)與 `scripts/lumos:14251`(`_vault_write_lock` 本身可重入,docstring 明講「同一個程序巢狀拿同一把鎖直接過」)——沒有另開第二種鎖(程式碼本身就警告過:「第三輪另開了一套 flock,是專案裡第二種鎖」,是已修過的舊坑,spec 沒有重犯)。
- 〈實務隱患〉併發段:表態檔與 drift-check 事件的「多寫入者無鎖」風險,spec 沒有自己發明一套新鎖去補,而是明講「這篇 Issue([[Issues/治理帳多個寫入者都沒上鎖]])2026-10-11 回頭看時把這兩個寫入者也算進去,整體怎麼修由那篇決定」——正確做法是掛進既有已追蹤的架構欠款清單,不是就地另開一套修法。
- doctor Z 段命名:核對現有 `section("...")` 呼叫(`G`、`L`、`M`、`T`、`R`、`S`、`I`、`H`、`K`、`D`、`V`、`P`、`Y`、`N`、`J`、`W`、`F`,以及 `S1`–`S15` 一組)沒有用過 `Z`,`Z` 是空的字母,spec 開一個新字母給一組獨立於既有 S-叢集(規格閘/放行/合約清單)的新檢查,跟「段名取新增序非畫面序」的既有慣例(見 `scripts/lumos:1908` E4 的註解)一致,沒有踩到既有段落。
- `governance/drift-acks.jsonl` 登記進「簿記豁免」:核對 `_BOOKKEEPING_FILES`(`scripts/lumos:20348`)是單一來源清單,且已有先例是 `governance/` 根目錄下的單一檔案(`governance/anchor-baseline.json`),不是只收 `docs/` 底下的檔——spec 要新增一個同形狀的條目,沒有另開判準。
- `LUMOS_SKIP_DRIFT_CHECK=1`「只認 1」:對照 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:24097`)、`LUMOS_SKIP_NOTE_AUDIT`(`scripts/lumos:24804`)、`LUMOS_SKIP_BOUND_TESTS`(`scripts/lumos:31044`)——這幾支都是各自在呼叫端手刻 `== "1"` 判斷,沒有共用的旗標讀取函式,spec 的寫法（各閘各自刻、只認字面 "1"）跟這個既有慣例一致,不是引入新做法。
- `.lumos/config.json` 的 `drift_check.gate` 讀法:對照 `_note_shape_config`(`scripts/lumos:23501`)、`_note_audit_config`(`scripts/lumos:24199`),兩者文件字串互相標明「照 XX 的讀法」——這個專案對「每個閘自己刻一支同形狀的 config reader」是刻意的既有慣例(不是共用一支泛用 reader),spec 沒有講怎麼讀 `drift_check.gate`,但也沒有講錯,留給實作照抄這個既有樣板是正確方向,不需要另外挑毛病。
- `lumos drift exam` 不併入既有 `lumos drift-history`(`scripts/lumos:4647`):兩者目的不同(drift-history 是「無固定答案的長期取樣校準」,drift exam 是「對固定考卷算擋到/點到/誤報」),spec 在 PRIOR-ART 裡明講「跟既有的 `drift-history`…不重疊:那支量『符號還在不在』,本計劃不碰符號存在性」,而且程式碼裡本來就有多支各自獨立的评分/校驗指令（`cmd_severity_check`、`cmd_seat_check`、`cmd_quote_check`、`cmd_link_candidates`),「一個評測需求配一支新指令」是這個專案既有的做法,不是 spec 引入的新模式。
- `when-symbol`/`when-test` 這種「條件成立要看程式裡有沒有這個符號/測試」,跟本輪範圍明講移出去的「丙」(健檢符號/測試存在性,見 [[Projects/舊句偵測實驗_計劃]])看起來相關但不是同一機制:「丙」是無提示、對全庫筆記做啟發式掃描找「疑似過期的舊句」；`when-symbol`/`when-test` 是作者主動寫下的單一斷言、只在那一行生效,spec 也在 PRIOR-ART 明講兩者不重疊、不碰符號存在性掃描本身。誠實界線一節也如實承認 `when-symbol` 對非 Python 是整字比對、有提早成立吞事件的已知限制,並排進 REVISIT——沒有殘留依賴「丙」的文字,不算本輪要報的殘留問題。
- 落點節(`[[Systems/存量漂移守衛]]`(新開)/`筆記內容閘`/`筆記內容審`/`guard-kill`/`reversibility-governance-ledger`):跟每支函式改動實際落在哪支既有模組（第一層 `_ns_check_line` 一類的規則、第二層 `_note_audit_items`、settle 的 `cmd_guard_settle`、治理帳閘名單)一一對得上,沒有把改動寫錯家。

## 〈審計修正紀錄〉r2 修補落地驗收

抽核以下幾筆 r2 折入項目,逐條在正文與考卷檔案裡核對到,認定「已折入」的說法屬實:

1. 「B3 的失效提交也寫錯…讓『開工』成立的是 f183cd8,已改」:`governance/eval/drift-exam/rtb-2026-09-28.json` 裡 B3 的 `invalidating_commits` 確實只剩 `["f183cd8"]`,`governance/eval/drift-exam/README.md`〈更正紀錄〉也留了同一句說明;用唯讀 clone `git -C rtb-exam show f183cd8` 重驗:該提交新增 `docs/rtb-production-agent-demo-knowledge/Projects/RTB_Phase12一鍵展示與HTML報告_計劃.md`,frontmatter 就是 `status: doing`,跟「Phase 12 開工」的判定條件一致。
2. `rtb-2026-09-28-probes.json` 裡 A7/B4 的 `event_commit: "0ffba7d"`、`why` 講「在 execution.py 新增 MAX_INCREASE_NUMERATOR」:唯讀重驗 `git -C rtb-exam show 0ffba7d -- '*execution.py'`,確實新增一行 `MAX_INCREASE_NUMERATOR = 1`,跟考卷描述一致。
3. B2 的 `why`「後半(改接外部模型)沒有明確的檔或名稱可寫,考試只用前半」:對照〈誠實界線〉「原本一句話講兩個觸發(考卷 B2),後半沒有明確的檔或名稱可寫就寫不成條件」——正文與改寫檔用語一致,沒有走回 r1 版本「硬拆兩行」的舊寫法。
4. 「lands_in 加 guard-kill、新增〈落點〉節」:frontmatter `lands_in` 確實列了 `Systems/guard-kill`,正文有獨立的〈落點〉一節逐一說明五篇筆記各自管什麼。
5. 「回退節…不准單獨還原守衛紀錄」:〈回退〉節裡「guard settle 的改寫」一段確實寫了「不要單獨用 git 還原守衛紀錄」並解釋原因(退回 pending 但家筆記已是正式行、舊程式沒有補救路徑)。
6. r2「判錯的」項(F7 誤指「其他家筆記」,實際限制是「settle 只處理第一篇家筆記」):〈誠實界線〉裡確實是「settle 只處理守衛紀錄第一篇家筆記的預告行」的正確表述,沒有沿用被判錯的說法。

沒發現 r2 折入清單裡的項目「說已折但正文找不到」的情形。

最嚴重等級 major,blocking 共 2 條。
