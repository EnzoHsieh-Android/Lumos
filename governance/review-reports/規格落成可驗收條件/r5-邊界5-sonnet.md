severity: blocker

## 逐節審查

**Frontmatter/decisions(d1–d13)**:已讀,無 finding——d13 拆分理由與 lands_in 內部一致,decisions 鏈的 superseded_by 指向都能對上。

**PRIOR-ART / RETIRE-IF**:已讀,無 finding。

**兩層要分開**:已讀,無 finding——規格書與驗收條款分層界線清楚,翻譯範例具體。

---

### F1. 支數解析的「N」在本 repo 自己的測試工具上不是「測試支數」而是「斷言數」,S6–S8 的分支邏輯會系統性誤判

severity: blocker

blocking: 是——判準:此非邊角案例,而是本 repo 唯一配置的 `run_cmd`(`.lumos/config.json` 的 `test_profile: python` / `run_cmd: python3 scripts/test_lumos.py -k {method}`)在每一次 spec-gate/處置閘第五步「跑」的步驟上都會踩到,屬於「這份 repo 自己的 11 條驗收條款」跑起來就會遇到的必然情形,不是要特別構造的極端輸入。

spec §三第 3 點規劃:條款一律真跑一次、依 N 值印紅/綠/弱證據/需唯一化。但本 repo 的 `scripts/test_lumos.py` 的 `check()` 函式(scripts/test_lumos.py:78-85)每呼叫一次斷言就 `PASS += 1`,不是每個 `t_*` 測試函式跑完才 +1;而一支 `t_*` 測試函式內部常呼叫 `check()` 數十次(例:S1–S11 這種行為鎖定測試慣例上一支函式含多條 check)。最終摘要行 `f"\n{PASS} passed, {FAIL} failed{tail}"`(scripts/test_lumos.py:29435)裡的數字因此是「斷言計數」,不是「-k 篩到幾支測試函式」。用 `_RAN_EVIDENCE["python"]` 的正則 `[1-9]\d*\s+passed` 去抓這個數字當「篩選到幾支」,一支測試若含 5 條斷言就會被誤判成 N≥2 印「篩選匹配到 N 支,測試名要唯一」(S7),即使 `-k` 精準命中且唯一。

引句:「N==1 → 印紅或綠;N==0 → 印「弱證據:一支都沒跑到」;N≥2 → 印「篩選匹配到 N 支,測試名要唯一」

file: `scripts/test_lumos.py:78-85`(check() 逐斷言累加 PASS,不是逐測試函式)
file: `scripts/test_lumos.py:29435`(摘要行用累積 PASS/FAIL 印「N passed, N failed」)
file: `.lumos/config.json`(`test_profile: python`,`run_cmd: python3 scripts/test_lumos.py -k {method}`)

---

### F2. spec 宣稱支援「unittest `Ran N test(s)`」樣式,但 `_RAN_EVIDENCE` 表裡沒有任何一個 profile 對應這個樣式

severity: major

blocking: 否——判準:spec 自己已承認「支數解析是新寫的」,屬未實作範圍,不構成與既有機制矛盾,可在落地時一併定義,不必卡這輪設計審;但若不在落地前把這個字面差距釘清楚,會複製 F1 的失敗模式。

現有 `_RAN_EVIDENCE` 只有四個 profile(swift-xctest/csharp-xunit/node-jest/python),其中 `python` 對應的樣式是 `[1-9]\d*\s+passed`(pytest 風格「N passed」),不是 stdlib `unittest` 直接跑出的「Ran N test(s) in Xs」——後者字面上完全不含 `passed`,不會被現有任何一條 regex 命中。真的用 `python -m unittest` 的消費專案,依現制會落回 `_bound_tests_filter_probe` 備援(只能判「有沒有跑」不能判 N),不會走到 spec 承諾的 N==0/1/≥2 三分支。

引句:「解析支數**:unittest `Ran N test(s)`(含 skipped)、pytest 的 failed+passed+skipped+error+xfail 相加」

file: `scripts/lumos:25696-25720`(`_RAN_EVIDENCE` 只有 4 個 profile,無 unittest 樣式)

---

### F3. 「全部計劃都要有回退節」與既有「無 [SN] 就整步 skip」的判定路徑矛盾,會讓不用 [S] 格式的計劃靜默不被要求回退節

severity: blocker

blocking: 是——判準:這是規則本身寫不寫得出「怎麼判」的問題,不是實作細節;兩種讀法(universal vs opt-in-only)會導向完全不同的程式行為,且其中一種讀法會讓 §二明文承諾的規則對一整批計劃(不寫 [S] 的)失效卻不出聲,正是本輪要防的「靜默放行」。

§二明寫「全部計劃都當單向門,所以全部要有」回退節,但 §四要共用的檢查器是綁在既有 `_disposal_clause_step` 之上(「沿用」`_clause_bindings_for`),而該函式現有邏輯在 `SPEC_CLAUSE_RE.search(text)` 找不到任何 `[SN]` 時直接 `return "skip"`,連帶不會跑到之後任何檢查(包含新加的回退節檢查)。固定席節點 `Systems/design-loop.md` 的 INVARIANT 行也明列「無 [SN]…跳過」為既有不可變合約的一部分。若 `_clause_check(plan, door)` 繼承這個早退分支(最自然的重用寫法就是繼承),沒有 [S] 條款的計劃就永遠不會被檢查有沒有「## 回退」——與 §二的「全部要有」直接矛盾;若不繼承,又跟現有 INVARIANT 的既定行為衝突,兩者都沒在 spec 裡挑明要選哪一個。**對固定席節點的影響**:會改到 `Systems/design-loop.md` 該行 INVARIANT 描述的判定範圍,這是 spec 自己承認要動的合約行(§四言明「要綁測試加審計」),但新合約草稿(§四引用)同樣沒把這個矛盾寫進去,等於帶著同一個洞被搬進新合約文字。

引句:「每份計劃要有「## 回退」節,內容 ≥20 字含實字(r1 邊界席:「非空」會被一個標點放行)——全部計劃都當單向門,所以全部要有」

file: `scripts/lumos:15768-15770`(`if not SPEC_CLAUSE_RE.search(text): print(...); return "skip"`)
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:39`(INVARIANT 明列「無 [SN]…跳過」)

---

### F4. 「## 回退」節的偵測方式未定義是否走本 repo 唯一的圍欄判定工具,標題比對規則(精確/前綴/包含)也未寫死

severity: major

blocking: 否——判準:這是新程式落地前該補的一處規格空白,不是跟既有機制矛盾,可以在動工時定義清楚,不必卡本輪設計審;但若空白帶著走,寫測試 spec 範例(例如本篇自己的「## 回退」節)被貼進另一篇計劃的程式碼圍欄示範時就會誤判。

本 repo 對「圍欄內文字不算數」已有唯一權威實作 `_visible_lines`/`_strip_fences_text`,且明文規定「剝圍欄一律走 `_strip_fences_text`」,因為曾經有人各自另寫正則導致漂移誤報被抓到。§二/§四都沒說「## 回退」節的搜尋要不要先過這道剝圍欄,也沒定義撞到「## 回退與復原」這種前綴相同但語意不同的標題、或同一份計劃出現兩個「## 回退」節時算哪一個、字數怎麼算(取第一個/取最後一個/加總)。

引句:「每份計劃要有「## 回退」節,內容 ≥20 字含實字」

file: `scripts/lumos:160-166`(`_visible_lines` 頭部註解:「★全檔唯一的 fenced-code 判定實作★」)
file: `scripts/lumos:2465-2466`(「剝圍欄一律走 `_strip_fences_text`」,曾因誤用另一正則造出假漂移)

---

### F5. `_clause_check(plan, door="one-way")` 的簽名只帶計劃檔一個輸入,無法實作 S10 要求的「迴圈首筆帳」不回溯判斷,`lumos spec-gate <計劃.md>` 的 CLI 用法也沒有任何迴圈/時間輸入

severity: blocker

blocking: 是——判準:這不是實作細節,而是 spec 自訂的函式介面與其自己要求的行為對不上——沒有輸入來源就無法判斷「首筆帳」時間,implementer 必須擅自加參數才能兜得起來,等於這條驗收條款(S10)在目前這份 spec 裡是不可實作的。

現行 `_disposal_clause_step(rows, spec, root, env, loop_id=...)` 靠呼叫端傳入的 `rows`(帳上各筆的 `ts`)去算「迴圈首筆帳」是否早於 `_CLAUSE_GATE_SINCE`,才能判斷要不要 skip(scripts/lumos:15754-15759)。但 §四給的新簽名 `_clause_check(plan, door="one-way")` 只有 `plan` 一個參數,完全沒有 `rows`/`loop_id`/`ts` 這類輸入;而 §三定義的獨立指令 `lumos spec-gate <計劃.md>` 的 CLI 用法同樣只吃一個計劃檔路徑,沒有帶迴圈識別碼。S10 卻要求「規格閘與處置閘第五步」都要能判斷「閘上線前第一筆帳的迴圈」——這個判斷所需的資料來源在新簽名裡完全消失了。此外固定席節點 `Systems/design-loop.md` 的 INVARIANT 明寫「首筆帳在 2026-09-09T00:00+08:00 之後」是既有合約的一部分判準,§四聲明要改寫這行合約(已預期、有綁測試),但改寫草稿裡同樣沒有交代 S10 的輸入從哪來,是把舊合約裡「怎麼拿到 ts」這塊資訊一起丟掉了。

引句:「[S10] 在閘上線前第一筆帳的迴圈上,規格閘與處置閘第五步應跳過句式檢查 [test:t_spec_gate_not_retroactive]」

file: `scripts/lumos:15736-15759`(`_disposal_clause_step` 靠呼叫端傳入的 `rows` 算 ts,新簽名沒有對應輸入)
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:39`(既有 INVARIANT 的「首筆帳」判準來源就是這批 `rows`)

---

### F6. `[manual:]` 只認半形冒號,全形冒號 `[manual：…]` 會被現有正則完全忽略、落回「沒標」的通用錯誤訊息,S4 沒有針對這個輸入形態給診斷提示

severity: major

blocking: 否——判準:結果仍是擋下(fail-closed),不是靜默放行,只是診斷訊息不精準,屬於 UX 缺口而非正確性缺口,不必卡本輪;但既有的停用詞表(§一)已經示範了「常見輸入誤判要給出可操作的錯誤訊息」這個標準,manual 冒號沒有比照辦理,值得在落地時一起補。

`MANUAL_REF_RE = re.compile(r"\[manual:\s*([^\]]*)\]")`(scripts/lumos:3402)只認半形 ASCII 冒號。中文輸入法打「manual：」很容易帶出全形冒號,這種寫法完全不會被此正則捕捉到,於是條款會被判成「untagged/沒標」,印出的是通用訊息「每條要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗]」,使用者看不出是冒號全形半形的問題。§一的停用詞表已經承諾「擋下時訊息要說『句首『在…』被當觸發詞…』,不能只印『格式看不懂』」,manual 冒號沒有對應的診斷升級,標準不一致。

引句:「[S4] 若條款的 manual 標記不足 4 字含實字,則規格閘應擋下 [test:t_spec_gate_manual_min_chars]」

file: `scripts/lumos:3402`(`MANUAL_REF_RE` 只認半形冒號 `:`)

---

### F7. S11 doctor 段「有條款的計劃比例」在零份有條款計劃時的印法未定義 ⚠

severity: minor

blocking: 否——判準:未落地功能的邊角案例,無具體現成程式碼可佐證會不會真的除以零崩潰,只是規格文字沒交代,影響範圍小(頂多是 doctor 那一段輸出異常,不影響閘的擋/放行判定)。

⚠ spec 只說「健檢應印出有條款的計劃比例」,沒說分母為 0(閘剛上線、還沒有任何計劃掛 [SN])時要印什麼(0%/N/A/略過整段)。判不準,標記待落地時定義。

引句:「[S11] 當健檢跑時,健檢應印出有條款的計劃比例與每份計劃的紅綠弱證據數 [test:t_doctor_spec_gate_stats]」

---

### 其餘章節

**一、條款句式(文法/停用詞)**:已讀,無 finding——r1–r3 已自己抓到「期間」鎖死、停用詞表不齊等問題並修正,目前文法定義內部一致,「句首命中即視為無條件型」與「不合文法印格式看不懂」的失敗模式確實是明確報錯而非靜默放行,經追蹤觸發子句/無條件型的判定條件沒有找到會落入第三種未定義狀態的路徑。

**二、綁定與回退節**(除 F3/F4/F6 外其餘):已讀,無 finding——「懸空只提醒不擋」沿用既有語意且有翻紅釘鎖著,一致。

**三、新閘 `lumos spec-gate`**(除 F1/F2/F7 外其餘):已讀,無 finding——第 1、2 步(句式/綁定)的擋/不擋界線清楚;不留痕、不寫帳的宣告與「半套沒有放行這件事」一致。

**四、處置閘第五步共用檢查器**(除 F3/F5 外其餘):已讀,無 finding——三條不回溯常數(`_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE`/`_SPEC_GATE_SINCE`)彼此職責分工清楚寫明「與本案無關」的邊界。

**進度 / 要動什麼**:已讀,無 finding。

**實務隱患**:已讀,無 finding——「已排除:不可逆」的推理成立,因為新增的回退節硬性要求受既有 `_CLAUSE_GATE_SINCE`/新 `_SPEC_GATE_SINCE` 不回溯保護,進行中迴圈不會被追溯性地新增擋下條件(前提是 F5 的輸入來源缺口被補上)。

**驗收條款 S1/S2/S3/S5/S9**:已讀,無 finding(S9 併入 F5、S4 併入 F6、S6–S8 併入 F1、S10 併入 F5、S11 併入 F7 討論)。

**回退 / 誠實界線 / 審計修正紀錄**:已讀,無 finding——「回退基準 sha:(待填)」與 REVISIT 行已明寫接電條件,誠實界線段落對文法鬆與散文收斂自我指涉的坦承與帳面數字一致。

---

## 總結

severity: blocker
blocking 3 條(F1、F3、F5)。
