severity: minor

第 2 輪(整合席,三個月後接手者立場)結論:沒有 blocker 或 major。三條 minor 都是文件對不上程式或測試守不到的缺口,程式行為本身站得住。

**驗證範圍**
- 固定版本:修前 409ab14f、修後 6e10ae5b。
- 實驗放在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/整合-sonnet/`,其中 `repo` 是修後、`before` 是修前。
- 探針腳本在 scratchpad(`probe1.py`、`probe2.py`、`probe3.py`、`mut.py`)。

---

**1. 驗收條款 S6、S8 與修補後的程式不一致,天花板三也漏列部分複製**
severity: minor
blocking: 否
引句:「而且 repo 不是淺複製時,規格閘應照樣存那支測試的紅燈版」
- 失敗場景:
  - 修補在 `_redbase_on_branch` 加了「`extensions.partialClone` 有值就整批照留」。
  - 部分複製的 repo 不是淺複製,但程式對它不丟、不存紅燈版。
  - 條款 S6 照字面讀,這種 repo 應該存,與程式相反。
  - 條款 S8 的清單(淺複製、git 叫不起來、過了截止時間、超過上限)沒有部分複製,卻列了「git 叫不起來」。
  - 綁定的 `t_redbase_branch_rows_fallback_keeps` 沒有任何「git 叫不起來」案例,只有「過了截止時間」走到同一個 `r is None` 分支。
  - 天花板三只寫淺複製、git 逾時、超過 200 個,沒寫部分複製。
  - 三個月後的人照條款判斷部分複製專案會得到錯的預期。
- 歸因:有證據的修復回歸。這是修補加了部分複製的行為,條款與天花板沒跟著改,屬文件漂移。
- claim:部分複製的 repo 裡,「不是祖先、提交不存在」的紀錄照留,與 S6 字面相反。
  - input:`probe3.py` 建 git 專案、設 `extensions.partialClone=origin`、治理帳被忽略,放一筆 `head_sha=ab*20`、`ref=featB` 的判綠事件,在 featB 上呼叫 `_redbase_branch_rows(W,"甲",None,"ignored")`。
  - expected:按 S6 字面應丟(得 0 筆)。
  - case_source:我自己補的探針,另有 `t_redbase_branch_rows_fallback_keeps` 的「部分複製」三條。
  - before(409ab14f):kept=0。
  - after(6e10ae5b):kept=1,stderr 印「1 筆紀錄判不了是不是這條分支的…照舊算進來」。
  - comparison:行為是修補刻意改的(計劃做法 1d),條款沒同步。
- 查證命令:`python3.14 <scratchpad>/probe3.py <repo或before目錄> <新目錄>`。

**2. 天花板漏列「從別條功能分支切出、延續同一份計劃」的分支,判綠保護會失效**
severity: minor
blocking: 否
引句:「if isinstance(ref, str) and ref and name and ref != name:」
- 失敗場景:
  - featA 上判綠,再從 featA 頂端切 featB 繼續做。
  - featA 的提交是 featB 的祖先,但名字不同就被丟,「判綠過的不存紅燈版」在 featB 失效。
  - featB 之後同一支測試判紅,會存下實作後的版本當紅燈版。
  - 條款 S1 字面就是「分支名不同照存」,所以這是設計取捨。
  - 天花板一只列壓提交、rebase、改名,天花板二、四也沒列這個。
- 歸因:有證據的原有漏查。修前與修後都一樣,不是修補造成。
- claim:祖先為真但分支名不同的紀錄被丟。
  - input:`probe2.py`,featA 提交 c1,featB 由 featA 切出,事件 `ref=featA`、`head_sha=c1`,治理帳被忽略。
  - expected:若「祖先才算本分支」為準應留 1 筆。
  - case_source:我自己補的探針。
  - before:kept=0。
  - after:kept=0。
  - 另確認 `git merge-base --is-ancestor featA HEAD` 回 0。
  - comparison:前後相同。
- 查證命令:`python3.14 <scratchpad>/probe2.py <repo或before目錄> <新目錄>`。

**3. 「治理帳判不了是否被忽略就不過濾」這條分支沒有任何測試守**
severity: minor
blocking: 否
引句:「if ignored == "ignored":」
- 失敗場景:
  - 計劃做法 1 寫「不是被忽略(進版控或判不了)就到此為止」。
  - 把條件改成 `if ignored != "not":`(判不了也過濾)後,相關測試全綠:
    - `t_spec_gate_redbase_green_tracked_unfiltered` 2 支
    - `t_spec_gate_redbase_green_other_branch` 10 支
    - `t_redbase_branch_rows_fallback_keeps` 12 支
    - `t_spec_gate_redbase_written_on_red` 35 支
  - S7 只守「進版控」。
  - 日後有人把 unknown 也納入過濾,不會有測試翻紅。
- 歸因:有證據的原有漏查。修前 409ab14f 的程式與測試(`before`)套同一個改壞也全綠(2/10/7 passed)。
- 對照:把條件改成 `if True:`,S7 會紅(`S7 帳進版控…不存紅燈版` ✗)。所以 S7 守得住「一律過濾」,守不住「unknown 要不要過濾」。

---

**計劃做法對程式**

| 項目 | 對到的程式 | 對到的測試 |
|---|---|---|
| 做法 1 分支名函式 | `_redbase_branch_name`,不用 `--short` | S2 同名 tag 案例 |
| 寫入兩處 `ref` | `_spec_gate_record` 與 `_redbase_note_green` | S1「記下分支名」 |
| 讀取過濾 a/b/c/d/e | `_redbase_on_branch` | S6、S8 |
| 上限先問最新 | `reversed` 與 `dict.fromkeys` | S8「超過上限」 |
| 截止時間在問祖先前起算 | `_redbase_branch_rows` 內自建 | 無獨立案例,作者的「改壞 H3」才有 |
| 做法 2 | `t_name_collision_scales` | 見下,守得住 |
| 做法 3 | `_TG_CONST_PAT` 三引號 | S4 |
| 做法 4 寫回的五處筆記 | 逐句核對,與程式一致 | 無 |

- 條款綁定:`spec-trace` 顯示 8 條全綁、懸空 0。
- 筆記驗證:七個相關節點 `lumos lint` 都是 0 問題。
- 新舊 `_TG_LIMITS`:`t_tq_guard_cli_contract` 99 支通過,逐字比對成立。
- 已確認為真的句子:
  - `_tg_ident` 的說明,呼叫端確實是 `_tg_ws_keep_strings` 傳 `_tg_ws_collapse`。
  - `_TG_LIT_PAT` 與 `_C_STRIP_PAT` 差別的註解,對得上 `_C_STRIP_PAT` 的樣式。
  - 「三引號 5 處一起生效」,`_TG_LIT_PAT` 確實 5 處用到。
  - 「head_sha 在還沒有提交的 repo 會寫成字面 HEAD」,實測屬實。
  - 「端到端驗收事件已用 `ref` 記分支名」,屬實(`android-e2e` 用 `ref=marker_branch`)。
- 搜尋過的詞:`判綠`、`整本帳`、`分岔點`、`15 秒`、`_TG_CONST_PAT`、`_redbase_branch_rows`、`淺複製`、`部分複製`、`串接`。除上面三條外沒有別處因這次改動變假。
  - 規格閘紅燈測試快照計劃第 78 行(`_TG_LIMITS` 的「抓不到新增」列舉)沒補「治理帳被忽略的專案」那句,屬歷史列舉。我講不出具體誤導場景,所以不立條。

**本案特定鏡頭**
- `ref` 欄位:
  - 全檔搜 `.get("ref")`,讀取端只有簽核帳、二次意見這類與規格閘無關的功能,加上這次新增的 `_redbase_on_branch`。
  - `_spec_gate_gov_index` 把整筆事件複製成 `rec` 後只讀 `loop`、`kind`,不受影響。
  - `lumos gov --stats` 在含 `ref` 的帳上正常。
  - 計劃回退節的「沒有讀取端會誤讀它」屬實。
- REVISIT 與天花板:
  - REVISIT 2027-05-03 的「本機 0.3 秒」與實測一致(`t_name_collision_scales` 0.3s)。
  - 天花板一到四與程式一致,但漏列第 2 條的情形、天花板三漏部分複製(第 1 條)。

---

**三問回答**

**① 原問題修復效果的行為證據**(修前程式 + 修後測試的結果)

| 案例 | 修前 | 修後 | 結論 |
|---|---|---|---|
| G3 同名 tag 的 S2 案例 | ✗ 存了紅燈版 | ✓ | 修復有效 |
| G4 部分複製三條 | ✗(`[]`、沒印說明、連了遠端) | ✓ | 修復有效 |
| G5 超過上限先問最新 | ✗(只回 `['3e5f17f1…']`) | ✓ | 修復有效 |
| G1 淺複製真祖先 rc 1 | ✓ | ✓ | 行為沒變,只補了案例,不算修復效果 |
| G2 撞名測試守快取 | 舊測試在「快取守衛被拿掉」的程式上仍 4 passed | 新測試 ✗,515 個不同物件 | 測試修復有效 |

- G2 的改壞做法:把 `_join` 的 `if key not in self._joined:` 改成 `if True:`。
- G6(不把回傳值塞進共用模組)我只看了程式,沒做改壞驗證。

**② 修補處的正常、錯誤、相鄰路徑**
- 正常路徑:完整 repo 裡祖先留、非祖先與不存在的提交丟,均通過。
- 錯誤路徑:
  - 過了截止時間、超過上限、淺複製、部分複製都照留並印說明。
  - 「git 叫不起來」沒有獨立案例(見第 1 條)。
- 相鄰路徑:
  - 治理帳進版控不過濾,S7 守住。
  - 預設參數呼叫 `_redbase_branch_rows(rr)` 行為不變,`t_spec_gate_redbase_written_on_red` 通過。
  - `unknown` 狀態沒守(第 3 條)。

**③ 新發現在修前、修後的結果**
- 第 1 條:修前丟、修後留,是修補刻意改的行為,條款文字沒跟上。
- 第 2 條:修前與修後都丟。
- 第 3 條:修前與修後的測試都守不到。

---

**固定席節點逐條判**
- `lumos-cli-read`:這份 diff 不碰 search 與 superseded 濾網,不影響。
- `測試假綠形態`:新測試大多有前置斷言(S3、S7、淺複製、部分複製、S9 的 gb5)。
  - 例外是 S6 的 gb3(同名重開),只靠後面的 `redbase in rec`,沒有前置證明判綠事件寫了。
  - 實測把 `_redbase_note_green` 改成不寫後,S1 的「別條分支判綠過:新分支跑紅照存」與 S6 gb3 照樣 ✓,同一支測試裡只有「記下分支名」與 S2 同分支案例翻紅。
  - 這條 INVARIANT 沒被破壞,但 gb3 這句本身不獨立。我講不出能讓整支測試仍全綠的具體改壞,所以不立條。
- `design-loop`:新計劃 8 條款全綁定,符合處置閘第五步,不影響。
- `guard-kill`:`_name_collision_reason` 只改測試,rc 優先序與 JSON 純度不動,不影響。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`:只多一個既有可選欄位,不動記帳語意,不影響。
- `lumos-cli-lifecycle`(re-inject)這份 diff 沒碰,不影響。
- 其餘只列名的節點(`bound-tests-gate`、規格閘相關計劃等):看不出被破壞,不影響。

---

**已驗證通過的主張**
- `-k redbase` 186 passed、`-k tq_guard` 410 passed、`-k t_name_collision` 22 passed、`t_tq_guard_cli_contract` 99 passed、`t_spec_gate_redbase_green` 共 12 passed、`t_tq_guard_string_comma_args` 24 case(改壞時 23 passed、1 failed)。
- 改壞三處皆翻紅:
  - 把 `_TG_CONST_PAT` 拿掉三引號段,S4 ✗。
  - 把過濾條件改成 `if True:`,S7 ✗。
  - 拿掉 `_join` 快取守衛,S3 的 ② ✗。

**未驗範圍**
- `-k spec_gate`(106 支)在我交卷時仍在背景跑,輸出在 `.../整合-sonnet/sg.out`,未等到結果。
- 全套測試未跑、Windows 路徑未驗。
- 真實慢遠端、時鐘倒退未驗(只驗了作者的留記號腳本)。
- G6 只看程式,沒做改壞驗證。

**暫存清理**
- 已刪:我造成的 `gctl-run-4d3k1su6`(刪前 lsof 確認無程序開啟)。
- 未刪:`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下其他 `gctl-run-*` 目錄分不出哪些是我的,留給編排者判斷。
- 席目錄 `/private/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/整合-sonnet` 留給編排者刪。刪之前先確認背景的 `test_lumos.py -k spec_gate` 已結束。

最嚴重等級是 minor,blocking 共 0 條。
