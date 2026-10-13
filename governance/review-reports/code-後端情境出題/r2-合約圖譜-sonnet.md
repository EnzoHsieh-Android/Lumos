severity: minor

我只讀了丙區的修補差異,沒讀 r1 開頭的任何檔。範圍是技能文件、知識筆記和卷證遮蔽。這輪的修補是否有效、正常路徑是否還成立、兩版同一案例各是什麼結果,先講結論:

- 本區沒有 blocker 或 major。
- 有 3 條 minor,都是筆記與程式對不上。
- 筆記宣稱的行為(閘擋法、`--stage`、效能題數、測試名)大致都對得上程式。

**問一:原問題修好了嗎?**

- **遮罩修復:**
  - 修前 `c960f6de`:6 個卷證檔有本機家目錄(`git grep -l '/Users/enzo' c960f6de -- governance/eval/qo-ablation-2026-10`)。
  - 修後 `112ad15f`:同一命令無輸出。
  - 我把 `r2-丙-repair.patch` 的卷證段逐行對照,把 `/Users/<名>` 換成 `~` 後與修後行完全一致,零差異,所以沒有改到原意。
- **解析器與閘的修復:**
  - 我把修後版的 `scripts/test_lumos.py` 放到修前樹執行。
  - `t_backend_qo_parser_robust` 是 1 passed、2 failed,`t_backend_qo_gate_fail_closed` 的 ①② 紅,對應 `1. [Q1]`、`### 待決問題`、`[狀態:待查。]` 等案例。
  - 修後 `-k t_backend_qo` 是 57 passed、0 failed,退出碼 0。
  - 所以筆記寫的「後兩條修之前就是紅的」屬實。
- **其他筆記主張:**
  - Kotlin 效能題從 8 題變 10 題,與 `_STACK_QUESTION_SPECS['kt']` 實數 10(含 `kt-springdata`、`kt-springhttp`、`kt-extcode`)一致。
  - `req-duplicate` 觸發詞含「提交」,與 `_REQUIREMENT_FACETS` 一致。
  - 筆記裡點名的 14 個測試名在修後版都找得到定義。
  - 兩條 `REVISIT:2027-04-12`、`RULE`(帶 `[retire:人裁]` 與 `[until:]`)和五篇筆記的 `lumos lint` 沒有新錯誤。`codex-harness` 的 2 個 FACT 警告是舊的。
  - 驗證筆記說「沒有任何寫檔工具」成立:在 `results/` 和 `results-mini/` 的 54 個結果檔裡沒有 Edit 或 Write,只出現在 `results-aborted/`。`RULE` 說的「受測 AI 在主機起了資料庫容器」,在 aborted 那場有 `docker run -d --name order-pg`,屬實。

**問二:修補處的正常、錯誤與相鄰路徑還成立嗎?**

- 正常路徑(`## 待決問題`、`## 3. 待決問題`、`## 待決問題(…)`、`## 待決問題:`)修前修後都解析到題目。
- `pitfalls --stage 需求` 在不帶 `--stage` 時輸出一字不差,不認得的階段與 `--diff` 並用回 2,測試也綠。
- 相鄰路徑有缺口,見下面三條 finding。

**問三:同一案例兩版結果**

見各條 finding。

---

severity: minor
blocking: 否
歸因:有證據的修復回歸。這輪把規格閘擋法放寬,但沒更新規格閘的家筆記。

引句:「規格閘只看狀態(標阻塞的需求或架構題沒結、標阻塞卻寫錯狀態或階段、題目行看不懂,一律擋)」

- 規格閘的家筆記沒跟著改。`Systems/規格閘.md` 仍寫只擋「標阻塞、階段是需求或架構、狀態是待查或待人」的題,沒提寫錯狀態、階段和看不懂的題目行也擋。
- 案例是一份計劃含 `- [Q1] … [狀態:待查。][阻塞]`,另有一行看不懂的 `看不懂 [阻塞] 孤行`。
  - 修前:`pending_questions_blocking_gate` 回 `[]`。
  - 修後:回 `['Q1', None]`。
  - 命令是在兩版的 `scripts/lumos` 上呼叫 `parse_pending_questions` 再呼叫該函式。
  - 修後 spec-gate 會回 1,家筆記卻說不擋。
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:86`
- file: `scripts/lumos:7045`(修後)
- 計劃筆記第 56 行「擋的是:有標阻塞、階段是需求或架構、狀態是待查或待人的題」也沒更新,和第 58 行並存,內部不一致。

---

severity: minor
blocking: 否
歸因:有證據的原有漏查。修前修後行為相同,不是這輪引入,但這輪新寫的筆記主張超出了程式。

引句:「解析看不懂就報、阻塞相關寫錯就擋,不靜默略過」

- 同一份筆記還寫「標題層級不限、前面可有編號」,程式只認阿拉伯數字編號(`_PQ_HEAD_RE` 的 `[\d.、]+`)。
- 案例檔 `plan.md` 含 `## 三、待決問題` 與 `- [Q1] … [狀態:待人][阻塞]`。
  - 工作目錄 `scratchpad/e2e`,命令 `python3.14 ../<版>/scripts/lumos pitfalls plan.md --repo . --stage 需求`。
  - 修前輸出「待決問題(0 題…)」,修後輸出相同,退出碼 0。
  - 函式層面 `parse_pending_questions` 回 `None`,閘判 held 0,所以阻塞題整題消失、規格閘放行。
- 其他同樣整節被略過的標題:`## 附:待決問題`、`## (三) 待決問題`、`## A. 待決問題`、`## 3) 待決問題`、`##待決問題`。這和筆記說要消除的症狀(阻塞題整題消失)同形。
- 要不要認這些標題是設計取捨;但筆記的「不靜默略過」和「前面可有編號」應收窄成「只認阿拉伯數字編號」,否則會誤導寫計劃的人。
- file: `scripts/lumos:6918`

---

severity: minor
blocking: 否
歸因:未判定。這些是舊句,這輪補了近鄰句卻沒順手對齊。

引句:「子命令:輔助計分、產生盲評包(隱去受測者、組別、場次並打亂,對照表另存)、兩位評分員一致率、最後統計」

- 這行漏了 `adj-pack` 和 `merge`。程式檔頭和 parser 一共 6 個子命令:score、packets、agree、adj-pack、merge、final。
- 同篇還有兩處對不上:
  - 「規格閘那一側的寧可擋(…跨篇決策連結照那篇判)」把跨篇連結檢查歸到規格閘,但它在 lint 側。測試 ③ 跑的是 `lint`,計劃筆記第 58 行也明講決策存在性只放 lint。
  - 「這次 72 場人工逐場核對」把甲組 18 場算了兩次。小實驗評分池的 36 場裡有 18 場是沿用正式輪甲組,不重跑,所以不重複的場次是 36 + 18 = 54。
- file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:446`

---

**固定席節點逐條判斷**

這份丙區差異只動文件、卷證和帳本,沒動 `scripts/lumos` 的實作。

| 節點 | 判斷 | 原因 |
|---|---|---|
| `codex-harness`(家) | 不影響 | 只新增 `RULE` 與 `REVISIT` 行,格式合規,`lint` 0 error;事實屬實。 |
| `lumos-cli-read` ★INVARIANT★ | 不影響 | 與 search 排除 superseded 無關。 |
| `bound-tests-gate` ★INVARIANT★ | 不影響 | 合約是重跑綁定測試,本區未改合約綁定。 |
| `design-loop` ★INVARIANT★ | 不影響 | 計劃的 `[SN]` 條款定義沒動。 |
| `guard-kill` ★INVARIANT★ | 不影響 | 與 guard kill 無關。 |
| `lumos-cli-lifecycle` ★INVARIANT★ | 不影響 | 與 re-inject 無關。 |
| `授權與歸屬` ★INVARIANT★ | 不影響 | 本區未動授權檔或檔頭。 |
| `測試假綠形態` ★INVARIANT★ | 不影響 | 新測試有現場成立的證據:修前樹上翻紅,見問一。 |

**未驗範圍**

- 筆記聲稱「用卷證標註重算兩輪最後判定,結果與原本一字不差」,我沒重跑。
- 「引號、heredoc 內的路徑字樣會多算」等計分器已知誤判形狀,我沒逐一驗。
- 技能文件 `02`、`05`、`INDEX.md`、`reference.md` 的措辭,我只與 `spec-gate` 與 `pitfalls --stage` 的程式行為對照過,沒跑完整的 `lumos doctor`。
- `r2-manifest.json` 是 0 條 claims,沒有可導引的命中位置。

總結:最嚴重 minor;blocking 共 0 條。
