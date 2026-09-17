severity: blocker
# 外部審稿意見 — 極端輸入視角(第 4 版)

severity: blocker

## 審查範圍與方法
逐節讀 `/tmp/規格落成可驗收條件-r4.md`(全文,frontmatter 到結尾);對照 `scripts/lumos` 中已落地部分(`_ci_step_is_test`、`_plans_in_range`、`_door_for_loop`、`cmd_canary` 的 `--finding-severity`/`--finding-kind` 解析、`INV_TAG_RE`)與 `docs/.ci-log.jsonl` 實際列;`_section_lines`/`_excluded_line`/`cmd_spec_gate`/`_clause_check`/`_DOOR_RULE_VERSION` 尚未落地(進度段自承「等設計審過閘」),對這部分僅能評設計文字本身是否自洽、會不會誤判。

---

### Finding 1 — `--finding-severity` 允許部分覆蓋,可靜默壓下輪級 major 的逃逸記錄
severity: blocker
blocking: 是——這是已經上線(r2 折入)的程式行為,不是未來工作;直接可用來讓「輪級 major、code 型」的一筆逃逸不進帳,而逃逸帳是本案唯一的糾錯機制(RETIRE-IF ① 承重牆)。
spec 哪一節:第五節「逃逸自動記」代碼審來源那列,及 `[S22]`。
問題:`--finding-kind` 要求 `set(kinds) == F`(全集覆蓋,見 `scripts/lumos:5983`「要每條發現各標一個」),但 `--finding-severity` 只驗 `set(sevs) <= F`(子集即可,`scripts/lumos:6000`)。因此呼叫者可以只給非關鍵發現的 severity(例如只標一筆 clean 的 spec 型發現),把真正 major 的 code 型發現整條從 `finding_severities` 字典裡漏掉。`scripts/lumos:6198-6205` 的判定 `_hit = any(v in ("major","blocker") and kinds.get(k)=="code" for k,v in _sevs.items())` 只掃給出的 key,漏掉的 key 直接不參與判斷——結果是 `_sevs is not None`(precision 標成看似高信心的 `finding`),但 `_hit=False`,逃逸不記,且沒有任何地方要求「給了 finding_severity 就要覆蓋全集」。`t_escape_auto_code_finding_severity`(scripts/test_lumos.py:31418 起)四個案例全部給的是完整 f1,f2 兩筆,沒有測過「只給其中一筆、漏掉那條真正 major 的」這個部分覆蓋情境。
引句:「若代碼審沒給逐條嚴重度,則逃逸帳應退回輪級判準記帳並標 precision 為 round [test:t_escape_auto_code_finding_severity]」
file: `scripts/lumos:5990-6001`(驗證只做子集檢查)、`scripts/lumos:6198-6207`(判定只掃給出的鍵)、`scripts/test_lumos.py:31418-31450`(既有測試全給滿集,未覆蓋部分覆蓋情境)

---

### Finding 2 — 「實務隱患節」標題剝離規則沒涵蓋 `(五)實務隱患` 這種括號前綴編號
severity: major
blocking: 否——判不到節就退回「當單向門」,是失敗安全方向(over-block),不會靜默放行,但會讓明明合格的雙向門計劃被錯判成單向門(逼人審查),違背本案「機械可辨識」的核心承諾,且這正是本篇自己列出的已知變體之一。
spec 哪一節:第一節「硬單向門」段內 `_section_lines` 定義。
問題:規則明講「標題去掉序號前綴(「五、」「5.」)與括號後綴後以「實務隱患」開頭」,只處理「文字+頓號/句點」式前綴與「尾端括號」;但同段自己舉的 8 種變體例子包含「## 五、實務隱患」,而題目指定要測的另一形狀「## (五)實務隱患」是「括號包住的編號當前綴」,不在「序號前綴」枚舉的兩種寫法裡,也不是「括號後綴」(括號在前不在後)。照字面實作,這種標題不會被剝出「實務隱患」開頭,整節找不到,四類已排除行也就找不到,雙向門永遠判不成。
引句:「只認二級標題 `##`,標題去掉序號前綴(「五、」「5.」)與括號後綴後以「實務隱患」開頭」

---

### Finding 3 — pytest 支數解析「N failed / N passed 相加」漏算 skipped/error,會讓 N≥2 的防護被繞過
severity: major
blocking: 是——這會讓 `[S32]`(篩選匹配到兩支以上要擋下)這個防護在特定情境下失效,屬於靜默放行(把本該擋的「-k 撞到多支」誤判成乾淨的單支紅)。
spec 哪一節:第四節「跑」,「紅」的判準。
問題:文字明講只解析並相加 `failed` 與 `passed` 兩個數字當作 N。但 pytest 摘要行可以是「1 failed, 2 skipped in 0.01s」——如果 `run_cmd` 的 `-k` 篩選實際匹配到 3 支(1 支真失敗、2 支被跳過,例如平台相關的條件跳過),`failed+passed = 1+0 = 1`,N 被算成 1,滿足「N==1 且失敗」,判成紅,直接放行——但實際上是多支撞名、跟本節後面自己承認的「158 組名字互為子字串」是同一種攻擊面,只是用 skipped 而不是同名撞出第二支通過檢查。spec 沒有提到 skipped/error/xfailed 要不要計入分母,這是一個沒堵住的洞,不是「已知殘餘」段落裡承認的那個(那個講的是同名子字串,不是 skip 漏算)。
引句:「解析測試工具輸出裡的支數(unittest 的 `Ran N test(s)`、pytest 的 `N failed / N passed` 相加),**N==1 且失敗才算紅**」

---

### Finding 4 — keeps 既存性檢查用純日期 `--before=<created>`,同日提交的合法 keeps 測試會被誤擋
severity: minor
blocking: 否——失敗方向是過度嚴格(把本該過的擋下),不是靜默放行,只是造成作者困惑、需要人工排查「明明測試在,為什麼說不存在」。
spec 哪一節:第三節「綁定規則」,keeps 既存性檢查。
問題:frontmatter 的 `created` 只有日期(如 `2026-09-17`),沒有時間與時區。`git log -1 --before=<created>` 在 git 裡對純日期字串會解讀成「該日 00:00:00」(以本機/git 設定時區為準),意味著計劃建立當天(不論建立在當天幾點)所有同一天提交的測試一律被排除在「建立前」之外。若某支 keeps 測試恰好與計劃在同一天但更早的時間點提交(常見情境:當天上午先補測試、下午才寫計劃),`git log -1 --before=<created>` 會找不到任何提交,判成「找不到提交」而擋下——這是一個合法案例被誤判成攻擊案例。spec 沒有處理「同日」這個邊界,也沒說要不要用 `created` 加時間戳或改用「plan 檔案自己第一次入 git 歷史的 commit」當基準。
引句:「取測試檔在 `created` 日期之前的最後一次提交(`git log -1 --before=<created> --format=%H -- <測試檔>`)」

---

### Finding 5 — 條款區塊指紋的「正規化」未定義,順序無關性與內容敏感性的界線不清楚
severity: minor
blocking: 否——不管往哪個方向定,都不是靜默放行(頂多多擋一次要求重跑規格閘),但目前寫法連實作者都無法唯一決定行為,兩種合理實作會給出不同的假陽性/假陰性組合。
spec 哪一節:第四節,雙向門放行留痕的「條款區塊指紋」。
問題:文字只說「全部 `[S]` 定義行正規化後串起來的 sha256」,沒定義「正規化」具體剝掉什麼——是否剝空白、是否剝 `[keeps]` 標記本身、多個 `[S]` 是否按 `SN` 排序後再串接。若不排序直接按文件出現順序串接,則兩條 `[S]` 互換位置(內容一字不變,純粹搬動段落順序)會讓 sha256 改變,`[S24]`/`[S31]` 就會誤判成「條款改了」而擋下推送(過度嚴格,非漏洞,但跟 `[S31]`「只改條款以外內容仍有效」的精神不一致——條款順序也不算內容變更,理應也視為有效,但文字沒明講)。若正規化包含 `[test:]` 測試名但不含 `[keeps]`,重新標記 keeps 而不動測試名是否要算「條款變了」也沒回答。
引句:「**條款區塊的指紋**(全部 `[S]` 定義行正規化後串起來的 sha256,不是整檔」

---

### Finding 6 — `_ci_step_is_test` 用 `;` 切多步的假設,已被本 repo 真實 CI 帳的截斷步驟名打破
severity: minor
blocking: 否——目前這筆真實資料剛好被正確判成「不是測試步」(False),不是現正發生的誤判;但這證明「`;` 只分隔不同步驟名」的假設在本 repo 現實資料裡不成立,是脆弱的隱含前提,換一種截斷方式就可能反過來誤判成測試步(靜默放行)或漏記真測試步失敗(靜默漏記)。
spec 哪一節:第五節 CI 來源表格,`_ci_step_is_test`。
問題:`docs/.ci-log.jsonl:64` 的真實 `failed_step` 值是 `"test/code-loop gate (push 後盾;體檢"`——這個 `;` 不是「多步驟用 `;` 串接」的分隔符,而是單一步驟名本身因為某種截斷(GitHub Actions 步驟名過長被切斷,或步驟描述本身含分號)而混進去的文字。程式碼對它 `split(";")` 之後會拆成 `"test/code-loop gate (push 後盾"` 與 `"體檢"` 兩個假分段,分別再各自判斷是否含 test/測試關鍵字。這次剛好兩段都判不到(所以整體 False,正確排除),但這是巧合而非設計保證——如果某天某個真正的測試步驟名恰好在被截斷處前後湊出「test」或「測試」字樣,就會被誤判成測試步(進而誤記逃逸)或誤判成非測試步(漏記真逃逸)。
file: `docs/.ci-log.jsonl:64`(真實資料)、`scripts/lumos:22360-22370`(`_ci_step_is_test` 實作)

---

## 逐節走查(未在上面列出 finding 的節)

- frontmatter/decisions(d1–d12):已讀,無 finding——決策鏈本身的前後訂正(538 篇→34/40/34)已由 r1 三席重驗,不在本席範圍內重查。
- 「為什麼」表格:已讀,無 finding。
- 「兩層要分開」:已讀,無 finding——規格書/條款分層本身沒有極端輸入疑慮,翻譯範例自洽。
- 第一節「門怎麼判」其餘部分(`_excluded_line` 前綴借用 `_CLAUSE_LEAD_RE` 字元集 vs 自建窄正則兩案並存):⚠ 這個實作分歧本身已被 r3 架構對齊席指出但未定案,不重複列為新 finding。
- 第二節「條款句式」停用詞表:已讀,無 finding——文法本身承認「表列不齊是已知的」且失敗模式是明確報錯,行為誠實。
- 第三節「[keeps] 標記家族」`INV_TAG_RE` 尚缺分支:已讀,無 finding——這是設計文件自己列出的待辦(「落地要加一個裸標籤分支」),我用 `grep` 核對 `scripts/lumos:3408` 確認現況正則確實沒有裸 `keeps` 分支,與 spec 陳述一致,不是新洞。
- 第四節「殘餘」段落(158 組子字串撞名):已讀,無 finding——已誠實承認且靠 N≥2 擋。
- 第六節「退場條件」:已讀,無 finding——三個數字已明講「是拍的」,誠實界線段也承認。
- 「進度」「要動什麼」:已讀,無 finding。
- 「驗收條款」33 條:逐條檢查文法(觸發子句/主體/應/[test:])未發現額外的極端輸入洞;`[S22]`/`[S34]` 的 precision 語意問題已併入 Finding 1。
- 「回退」節:已讀,無 finding——sha 待填有 REVISIT 盯,已有機制接住。
- 「誠實界線」「REVISIT」兩則:已讀,無 finding。
- 「審計修正紀錄」:已讀,無 finding——純歷程記錄。

---

## 總結
最嚴重 severity:blocker(Finding 1)。
blocking 計數:2 條(Finding 1、Finding 3)。

**白話總結**:這輪從「刁鑽輸入」角度看,前三輪已經把「節的邊界」「keeps 後門」「CI 步驟名」這幾類大洞堵了,第 4 版本身沒有新的結構性破口。但我找到兩個會讓機制「悄悄失效」而不是「明確擋下」的洞(都是要害):一是已經上線的逃逸記錄功能,可以只標一部分發現的嚴重度、把真正該記的那條漏掉,帳面看起來很精細(precision=finding)其實是空的;二是規格閘打算用的「紅測試支數」解法,對 pytest 的 skipped 測試沒算進去,會讓本來該擋的「篩選撞到好幾支」情況被誤判成乾淨的單支紅而放行。這兩個都建議在落地/修補時一併處理,其餘找到的問題都是「會誤擋、不會誤放」,風險低但值得記一筆。
