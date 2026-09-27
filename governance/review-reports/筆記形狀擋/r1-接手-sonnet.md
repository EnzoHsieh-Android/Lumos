severity: major

## F1 [src:] 標籤跟既有 Check J-c 的既有語意撞名,規劃要求的逃生寫法會被既有機制打回票

severity: major
blocking: 是 —— 不改,任何帶 `regen:` 欄位的節點只要照這份 spec 寫 `[src:部署]` 這類逃生標籤,既有的 Check J-c 就會把它判成「幻覺證據」擋下,寫的人會卡在兩條規則互打、卻查不到原因

引句:「`FACT:` `FLOW:` `DEP:` 行要帶 `[src:部署]` `[src:資料庫]` `[src:生產]` `[src:外部]` `[src:人工]` 其中之一(d3)」

`[src:...]` 這個方括號標籤在本 repo 已經有一套現成、且語意完全不同的用法:`SRC_REF_RE = re.compile(r"\[src:\s*([^\]]+?)(?::(\d+(?:-\d+)?))?\s*\]")`(file: `scripts/lumos:4270`)專門解析「`[src:路徑]` 或 `[src:路徑:行號]`」這種**指到 repo 內某支檔案的證據指標**,只在節點 frontmatter 帶 `regen:` 欄位時生效(file: `scripts/lumos:4568-4570`),抽出的 token 直接餵給 `_validate_repo_ref` 驗是否存在,查不到就回 `missing`、由 Check J-c 印「`[src:{path}] 目標不存在(J-c dangling=幻覺證據)`」(file: `scripts/lumos:4600-4607`)。

我實際跑了這支函式驗證:
```
SRC_REF_RE.findall('FACT: 這件事只在生產環境成立 [src:部署]') → [('部署', '')]
_validate_repo_ref(repo_root, '部署', '')  → ('missing', '')
_validate_repo_ref(repo_root, '生產', '')  → ('missing', '')
```
也就是說,這份 spec 要求新寫的 `[src:部署]`/`[src:生產]` 這類「來源類別」標籤,一旦出現在帶 `regen:` 的節點裡,會被既有邏輯當成「指到一支叫『部署』的檔案」去驗,驗不到就報 dangling——兩套機制搶同一個方括號前綴、語意卻互斥(一個是「路徑指標」,一個是「固定五選一類別詞」)。目前圖譜裡沒有節點帶 `regen:`(`grep -rl '^regen:' docs/lumos-toolchain-knowledge` 0 筆),所以現在還不會炸,但 `regen` 是活著的既有機制(`Projects/from-scratch重生守衛_計劃`),spec 完全沒提到這個既有語意、也沒檢查過命名空間衝突,PRIOR-ART 一段列的五項借用形狀裡沒有這一條。要嘛換一個沒被佔用的前綴(如 `[src-kind:]`),要嘛在 Check J-c 那邊先排除這五個固定詞,兩條路都沒寫進 spec。

## F2 程式行號引用的偵測沒有借用既有的「唯一抽取器」,重複造第二套規則會踩到 repo 自己記錄過的教訓

severity: major
blocking: 是 —— 不改,note-shape 的偵測範圍(要不要求反引號包住、認不認 `#L` 錨點)全靠實作者自己猜,猜出來的規則跟既有 refcheck/每支檔有家共用的抽取器不一致時,不會有任何測試翻紅,漂移會悄悄發生

引句:「`路徑:數字`、`路徑#L數字`,而路徑是 repo 裡的程式檔或測試檔」

本 repo 已經有一支專門抽取「筆記裡用反引號寫的 `路徑:行號`」的函式 `_node_code_ref_tokens`,它的 docstring 明講:「★refcheck、改檔前推筆記、每支檔有家三處共用這一支★——推筆記認得的,跟每支檔有家認得的,一定一樣(兩套算法一定分岔,而分岔時沒有東西會翻紅;Projects/每支檔有家_計劃 [S7])」(file: `scripts/lumos:19856-19858`)。`_refcheck_scan`(file: `scripts/lumos:19882-19899`)就是拿這支函式配 `_validate_repo_ref` 做 G1 硬閘與 spec-trace 用的核對。這份 spec 的 PRIOR-ART 一段只列了 `_is_code_file`、`_visible_lines`、`_gate_event` 等五項既有形狀,唯獨漏了「偵測 `路徑:行號` 這個字串形狀」本身該借用哪一支——而這正是 repo 自己寫下「別各寫一份,會分岔」的那支。

兩個具體落差:
1. 既有抽取器只認**反引號包住**的 inline-code span(`INLINE_CODE_RE.findall(_strip_fences_text(text))`,file: `scripts/lumos:19861`),裸文字裡的 `scripts/lumos:123` 不算。spec 完全沒說 note-shape 是否要求反引號——寫散文提到 `foo.py:12` 沒加反引號要不要擋,規則沒定義。
2. 既有抽取器的後綴正則是 `_suffix_re = re.compile(r":([^/]+)$")`(file: `scripts/lumos:19859`),只認冒號行號,**不認 `#L數字`**這種 GitHub 錨點格式。spec 額外要求擋 `路徑#L數字`,這是既有抽取器完全沒有的新形狀,要嘛擴充既有共用函式(牽動 refcheck/每支檔有家/推筆記三個既有消費者的行為),要嘛另開一套只給 note-shape 用——兩條路都沒寫進做法,而後者正是文件自己警告過的分岔。

另外,「放行寫法:釘住版本的 `路徑@<提交>:數字`」也是全新語法。本 repo 現有的「釘住某次提交的 path:line」慣例(表態閘/bound-tests 的 satisfied 錨點)不是把提交編號寫進文字裡,而是 `_dispositions_split_path_line` 只切「最後一個冒號」拿 `path:line`(file: `scripts/lumos:29496-29509`),提交編號是外部帶進來的 `at_sha` 參數(`_validate_repo_ref(repo_root, p, line, at_sha=at_sha)`,file: `scripts/lumos:29746-29757`),不是文字內嵌 `@sha`。spec 發明的 `路徑@<提交>:數字` 這個 `@` 語法在全 repo 找不到第二個先例,卻自稱「全部借本 repo 既有形狀,不發明新做法」——這一條不成立。

## F3 治理帳鎖沒點名要借哪一支既有鎖,現成最接近的那支逾時是丟裸例外、跟 spec 承諾的行為矛盾

severity: major
blocking: 是 —— 不改,實作者要嘛照抄現成的 `_vault_write_lock` 逾時直接丟未捕捉的 `RuntimeError`(推送時噴一整段 traceback,不是乾淨的「擋下:」訊息,跟 spec 自己寫的行為矛盾),要嘛得自己另外設計一套逾時處理,而 spec 完全沒交代要選哪一條

引句:「等鎖逾時照既有 rc 協議印「擋下:…」回 2,不丟裸例外」

本 repo PRIOR-ART 段對其餘四項借用形狀都指名了具體函式(`_is_code_file`、`_visible_lines`、`lint_new.gate`、`_gate_event`),唯獨「治理帳檔案鎖」這一項完全沒點名要借哪一支既有鎖原語。全 repo 目前唯一的檔案寫入鎖是 `_vault_write_lock`(靠 `_excl_lock_try` 實作,file: `scripts/lumos:14229-14274`),它在等滿 60 秒後的行為是:
```
raise RuntimeError("等了 60 秒還輪不到寫入(同一個筆記庫有別的程序正在寫,或上一個寫入的程序卡住了),檔案沒動")
```
(file: `scripts/lumos:14263`)——這是一顆**沒有被任何呼叫端接住的裸例外**。我查了它現有的全部 9 個呼叫點(`scripts/lumos:5615, 9527, 9604, 9796, 14279, 14452, 14491, 21372`),全部都是 `with _vault_write_lock(...):` 直接用,沒有一處包 `try/except RuntimeError`。這跟 spec 要求的「印擋下、回 2、不丟裸例外」是相反的行為。如果實作直接把 `_gate_event`/`_codeloop_gov_log` 包進這支既有鎖卻不額外處理逾時例外,note-shape/code-loop 寫治理帳逾時時會讓 hook 直接因未捕捉例外中止,使用者看到的是 Python traceback 而不是設計要求的訊息;如果要另外接住例外,那是 spec 沒寫出來的新工作,PRIOR-ART 段「不採用新依賴、不發明新做法」的說法在這一項上站不住腳(至少要交代「借 `_excl_lock_try` 這支底層原語、自己包一層新的逾時處理」,而不是含糊帶過)。

## F4(minor)doctor 掃「閘上線後違規」沒點名要借用既有的上線點偵測機制

severity: minor
blocking: 否 —— 這是 PRIOR-ART 完整性的落差,不影響能不能做出來;實作者順著「每支檔有家」的既有先例類比就能填上,不會因此做錯決定

引句:「另外 doctor 對「已推上遠端、在閘上線之後」的提交跑一次 note-shape,有違規就列出來」

「每支檔有家」判定「閘上線之後」的機制是 `_NODEHOME_GOLIVE_MARK = "home check --staged"`(file: `scripts/lumos:22181`)配 `_nodehome_golive`(file: `scripts/lumos:22855-22861`,原理是 `git log -S<標記字串> -- scripts/hooks/pre-commit` 找「提交前掛鉤第一次包含這道檢查」的提交)與 `_nodehome_clamp_base`(file: `scripts/lumos:22864-22876`)。S9 需要同一種「這個 repo 的 note-shape 閘是什麼時候上線的」判斷,但 PRIOR-ART 段沒有把這支點名進借用清單,只在「兩條規則」段點名了 `_is_code_file`/`_visible_lines`/`_gate_event`。不點名不影響可行性(類比既有先例即可複製一份標記字串),但既然 CLAUDE.md 本身的紀律就是「借既有形狀、不發明新做法」,這裡少寫一項,遺漏本身就是本次覆核想抓的那類「看得出但没写」的洞。

---

## 逐節「已讀,無 finding」

〈白話/依據/PRIOR-ART/RETIRE-IF/REVISIT〉已讀,無 finding(除上面 F1-F4 外,PRIOR-ART 其餘四項〔①每支檔有家的閘、②`_is_code_file`、③`_visible_lines`、④`lint_new.gate`/`LUMOS_SKIP_LINT_NEW`〕逐條核對過:①的「起點=不在任何遠端分支上的最早提交的上一個提交,全部已在遠端就不查」跟 `scripts/hooks/pre-push:215-233` 的 `_hrange` 計算邏輯逐字對得上;②③的引用位置與用途跟 `scripts/lumos:6181-6210`、`scripts/lumos:3218` 一致;④的 `("block","warn","off")` 模式跟 `_LINT_NEW_GATE_MODES = ("block", "warn", "off")`(`scripts/lumos:20935`)一致)。

〈範圍與行〉已讀,無 finding——「★不用跟預設分支的分岔點★」的理由跟 `docs/lumos-toolchain-knowledge/Projects/prepush主幹範圍修法_計劃.md` 記錄的 2026-07-21 事故(main-direct 時 merge-base==HEAD 導致守衛靜默跳過)完全對得上;「★也不用 CI 既有代碼審那一步的空樹兜底★」跟 `.github/workflows/ci.yml:108-109` 目前 `code-loop gate` 步驟確實在 BEFORE 算不出來時退到 `EMPTY=4b825dc6...`(空樹)全掃的寫法一致,spec 刻意不重複這條路是合理的。

〈兩條規則〉除 F1、F2 外其餘已讀,無 finding——回傳碼 0/1/2 的約定跟 `cmd_set` 等既有子指令的 rc 慣例(`scripts/lumos:14291-14295` 一類的「擋下:...,回 2」寫法)一致;`note_shape.gate` 的 block/warn/off 三態與 `LUMOS_SKIP_NOTE_SHAPE` 跳過寫帳的形狀跟 `LUMOS_SKIP_LINT_NEW`/`LUMOS_SKIP_BOUND_TESTS` 的既有先例(`scripts/lumos:21479-21480`、`scripts/lumos:29215-29219`)一致。

〈治理帳寫入加鎖〉除 F3 外已讀,無 finding——「`_gate_event` 與 `_codeloop_gov_log` 現在都直接 append、沒有鎖」這句現況陳述本身查證屬實:兩支都是 `open(..., "a", ...)` 後直接寫,沒有任何鎖(file: `scripts/lumos:927-931`、`scripts/lumos:28816-28818`)。

〈紀律範本改寫〉〈消費專案的 CI〉已讀,無 finding——`lumos update` 屬既有分發機制(見使用者記憶「lumos 更新分發」),CI 檢查步驟需自行貼一次的說法跟現有「工具鏈自己的 CI 手動加那一步」慣例(`scripts/hooks/pre-push` 內對 `home check`/`code-loop check` 的呼叫都是各自的 hook/CI 各寫一次,不是 `lumos update` 同步範圍)一致。

〈條款 S1-S9〉已讀;S1/S2 對應的落差已併入上面 F1/F2;S3-S9 逐條核對測試點命名與規則本文一致,沒有另外發現獨立於 F1-F4 之外的缺口。

〈回退〉已讀,無 finding——順序自洽(先關 CI 步驟、再各專案關開關、再拆 hook 呼叫、鎖留著不退)沒有內部矛盾;第 4 點「治理帳的共用鎖留著」跟 F3 的疑慮不衝突(F3 是「怎麼做」的落差,不是「該不該做」)。

〈實務隱患〉已讀,無 finding——三個「已排除」類別(對外送出/不可逆/金流)的理由跟程式碼現況相符(note-shape 確實只讀 git/檔案,不送外部;擋下不產生提交、hook 不動工作目錄這件事在 `_gate_event` 系列的既有寫入路徑上找不到反例)。

〈誠實界線〉已讀,無 finding——「行號引用抽樣 12/12 樣本小」與「句型比對抽樣準度約三分之一」跟來源 Issue `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` 記錄的數字(68 行命中、12 抽樣、「目前沒有/只有 N 種」句型 75% 漂移但「準度撐不起硬擋」)一致,沒有誇大或漏引。

## 附上節點逐條判

- `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`:這是問題來源與 d1-d7 決策紀錄,不是被這份設計改動的既有系統,沒有可被破壞的行為/合約。spec 對 d1(不留存程式碼推得出的東西)、d3(現況出口收窄)、d5(要機械擋)、d7(拆兩份計劃)的引用跟該筆記 `decisions:` 欄位逐條核對一致;唯一的落差是 d3 決策內容原文只列「部署設定、資料庫實際值、生產觀測」三類,spec 的 `[src:]` 五類(多了外部、人工)沒有直接對到 d3 的 decisions 文字,但這五類跟 CLAUDE.md 正文「部署設定、feature flag、資料庫實際值、生產觀測、法規與人工核可」的既有分類吻合,不算破壞這篇筆記的決策,只是引用時該指向 CLAUDE.md 而非只掛 d3。
- `Systems/每支檔有家`:這篇沒有 `★INVARIANT★`/`★IRREVERSIBLE★`/`★CHECKPOINT★` 這類合約行(該節點全文掃過,零命中),所以沒有「宣稱的行為」會被這份新設計直接破壞。spec 對它的算法引用(起點推導、`_is_code_file`、`--staged`/`--diff` 分工)經比對 `scripts/hooks/pre-push:215-233`、`scripts/lumos:6181-6210` 後屬實,是正確的借用而非誤用。

## 總結

最嚴重 severity:major(F1、F2、F3);blocking 共 3 條(F1、F2、F3);另有 1 條 minor 不 blocking(F4)。
