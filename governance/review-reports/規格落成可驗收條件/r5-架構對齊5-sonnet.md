severity: minor

## 一、分層與依賴方向

**對齊。** `cmd_spec_gate` 與 `_disposal_clause_step` 都直接呼叫新的共用檢查器 `_clause_check(plan, door)`（第四節），這跟本檔既有的層次一模一樣:`cmd_spec_trace`(`scripts/lumos:4718`)在第 4760 行直呼 `_clause_bindings_for`,`_disposal_clause_step`(`scripts/lumos:15736`)在第 15771 行也直呼同一支 `_clause_bindings_for`——兩個不同層(頂層指令／處置閘中層步驟)平行呼叫同一支共用低層函式,是本檔既有慣例,凍結稿的 `_clause_check` 只是在這支共用函式外面多包一層(句式+綁定+回退節),沒有改變「誰呼叫誰」的方向。支數解析「用 `run_cmd` 真跑一次再解析輸出」對照既有 `_ran_evidence_check` 的呼叫點(`scripts/lumos:25858`,先跑指令拿 `tail` 再送進解析函式),層次相同。doctor 新一段掛進 `run_doctor`(`scripts/lumos:974`)裡新增一個 `section("S12", …)`,跟既有 S1–S11(`scripts/lumos:1359`–`2171`)同一種「`run_doctor` 直接呼叫 `section()`/`warn()`/`ok()`」寫法,沒有另開一條 doctor 分支。

## 二、命名與錯誤處理

**大致對齊,一處 minor。** `_SPEC_GATE_SINCE` 跟既有 `_CLAUSE_GATE_SINCE`(`scripts/lumos:4599`)、`_LANDING_GATE_SINCE`(`scripts/lumos:15806`)同一個「`_XXX_GATE_SINCE` = ISO 時間字串,處置閘某一步不回溯」命名族,`cmd_spec_gate` 跟 `cmd_spec_trace`(`scripts/lumos:4718`)同一個 `cmd_<名>` 族,`_TRIGGER_STOPWORDS` 是本檔既有「大寫常數存字串表」慣例(如 `_MANUAL_MIN_CHARS`,`scripts/lumos:3403`)的自然延伸,凍結稿 S4 的「manual ≥4 字」跟 `_MANUAL_MIN_CHARS = 4` 數字一致。

minor 一處:停用詞擋下訊息(第 135 行「句首『在…』被當觸發詞,不是觸發請改寫或用主體開頭;若是常用詞,把它加進 `_TRIGGER_STOPWORDS`」)把「發生什麼／為何在意／怎麼改」揉進一句,不像既有 `cmd_spec_trace` 的兩段式印法(`scripts/lumos` 裡先印「為什麼在意:未標的條款沒人能機械判它做到沒,設計審處置閘會擋。」再另印一行「每條要嘛…」)或 `_ran_evidence_check` 的 `fix_hint` 分離寫法(`scripts/lumos:25699`,原因與操作分開講)。

引句:「表列不齊是已知的(r3 正確性席:「若不」「在場」「當機」「當初」都不在)——失敗模式是明確報錯不是靜默放行」

severity: minor

## 三、第二種做法

**沒有新的第二種做法;r4 那條 major 在半套裡兩處都處置了,但支數解析那半只是「承諾」,設計本身還沒補完。**

- `cmd_spec_gate` 與 `cmd_spec_trace`:不是同一件事的兩套。`cmd_spec_trace` 是唯讀報表(逐條印狀態、不擋、不跑測試);`cmd_spec_gate` 是會擋的閘(格式擋、缺綁定擋、回退節擋)並且真跑測試。凍結稿第 145 行明講「存在性走 `_clause_bindings_for`(處置閘第五步實際呼叫的那支)」,即綁定判斷仍收斂在同一支既有共用函式,沒有另外重寫一套判斷邏輯。
- 支數解析 vs `_RAN_EVIDENCE`:r4 那條 major 是「支數解析沒有收進 `_RAN_EVIDENCE` 逐棧實測表,是繞開既有紀律另開一條路」。凍結稿 PRIOR-ART 行(第 97 行)已改口「落地時收進 `_RAN_EVIDENCE` 逐棧表」,不再自建平行表——這條 major 名義上折了。但第三節「跑」本身(第 153 行)仍只寫了 unittest(`Ran N test(s)`)、pytest(failed+passed+skipped+error+xfail)兩種格式,完全沒交代 `_RAN_EVIDENCE` 現有另外三棧(swift-xctest/csharp-xunit/node-jest,`scripts/lumos:25696`–25716)在「N==0/N==1/N≥2」這個新判準下要怎麼收——即只是把「要收進去」寫成一句承諾,沒有把收法設計出來,跟 r4 指出的缺口(「沒交代這三棧在支數解析下走哪條路」)是同一個洞,只是不再構成「第二套結構」,降級成規格留白。⚠ 判準是否要再上升成 major 見文末錨定;我判定夠不上「引入第二種做法」,只算 minor。

引句:「解析支數:unittest `Ran N test(s)`(含 skipped)、pytest 的 failed+passed+skipped+error+xfail 相加」

severity: minor

- `_clause_check` 與 `_disposal_clause_step`:共用方向是 `_disposal_clause_step`(既有的處置閘中層步驟)去呼叫新的 `_clause_check`,不是反過來——這跟它現在呼叫 `_clause_bindings_for`(`scripts/lumos:15771`)的既有方向一致,沒有讓低層函式回頭呼叫高層編排函式,不是跨層直呼。對齊。
- 回退 sha 寫進計劃節 `## 回退`:跟既有回退慣例分兩套但不衝突——doctor 的 ★IRREVERSIBLE★/`[rollback:decisions]` 機制(`scripts/lumos:1339`)只認 `type: system` 節點,凍結稿是 `type: project`,依規則本來就不該用那套標記。改用散文 `## 回退` 節,跟同批拆出的兩篇姊妹計劃同款:`docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:124`、`docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md:85` 都有同名 `## 回退` 節。對齊,不是第二套。

## 四、落點

**對齊。** `lands_in` 兩篇(`Systems/design-loop`、`Systems/規格閘`)延續 r3/r4 已核過的分工判斷——r4 report 已明確記錄「兩篇夠用,沒有第三種記法」,凍結稿的「要動什麼」表(第 177 行)把 `cmd_spec_gate`、`_clause_check`、`_TRIGGER_STOPWORDS`、支數解析都指定進 `Systems/規格閘`(還不存在,要新開,符合 `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 的「新開用 `lumos new system <名> --code <檔> --responsibility`」慣例),`Systems/design-loop` 只管處置閘第五步那行不可變合約(`Systems/design-loop.md` 現有 ★INVARIANT★ KEY 行正是這行合約)。三篇計劃(本篇、`雙向門放行_計劃`、`逃逸自動記_計劃`)互相 `related` back-link 對稱,經核對 `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:16` 與 `docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md:24` 兩篇的 `related` 都指回本篇,是同批拆分計劃互相對稱連結的既有形狀,不是本篇獨創。

不對齊共 3 條,其中 major 0 條、minor 3 條。
