severity: major

審查範圍:r1-docs.patch 對照 HEAD 690f544f。程式部分我只拿來查證,沒有審。我用 `lumos lint` 跑了 6 篇動到的筆記,都是 0 問題。計劃 11 條驗收條款(S1 到 S11)綁的 11 支測試都存在,測試內的 check 標籤也逐條對得上條款。計劃裡的函式、常數、環境變數、旗標名都對得上程式。

## Findings

### 1. 計劃自己承諾「同一個提交改掉」的說明處沒改,05 手冊還寫著舊的擋下原因
severity: major
blocking: 是
引句:「風險高計劃要寫預期值表並簽核,推送前會查;本 repo 的」
file:line:
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/templates/graph-discipline.md:88`
- `/Users/enzo/harness/lumos-highrisk-evidence/skills/lumos-project-notes/commands/05-設計審查迴圈.md:12`
- `/Users/enzo/harness/lumos-highrisk-evidence/skills/lumos-project-notes/commands/INDEX.md:19`
- `/Users/enzo/harness/lumos-highrisk-evidence/skills/lumos-design-loop/reference.md:535`

具體失敗場景:
- 計劃〈做法〉第 6 點明列要改的檔,patch 沒碰這幾處。我 grep 過,這 4 檔加上 `skills/lumos-design-loop/templates.md` 的「預期值」都是 0 筆。
- 本 repo 的 `CLAUDE.md` 與 `AGENTS.md` 也沒重新注入。
- 接手者照 05 手冊第 12 行操作:它寫「風險高:rc1=句式/綁定/回退節/相依回歸有缺;紅綠只印」。實際上風險高、有新行為條款、建立日在 2026-11-06 之後的計劃,沒表、表格式不對,`spec-gate` 也回 rc1。
- 使用者專案的注入範本(第 88 行)只說「風險高再進實作前的審查迴圈」。使用者專案裡的 AI 不會知道要先寫表、要簽,到推送前才被擋。
- 計劃說要寫進 lumos-project-notes 的表格範例(`單筆消費 1000 元`)也沒進任何 skill 檔,只在程式的 `_EXPECTED_EXAMPLE` 常數(`scripts/lumos:14410`)。skill 手冊裡沒有「條款欄不加方括號」這條說明。
- 重現指令:`grep -c 預期值 scripts/templates/graph-discipline.md skills/lumos-project-notes/commands/05-設計審查迴圈.md skills/lumos-project-notes/commands/INDEX.md skills/lumos-design-loop/reference.md skills/lumos-design-loop/templates.md`,回傳全是 0。

### 2. Systems/規格閘 同一篇筆記裡版本號互相打架
severity: minor
blocking: 否
引句:「_NOGO_SKIP_LOGIC_VERSION 8、_DOOR_RULE_VERSION 16」
file:line:
- `/Users/enzo/harness/lumos-highrisk-evidence/docs/lumos-toolchain-knowledge/Systems/規格閘.md:38` 的 KEY 行寫 `_DOOR_RULE_VERSION=14`。
- 程式 `scripts/lumos:13862` 是 16,`lumos spec-gate --door-rule` 實測印 `door_rule=16`。

具體失敗場景:這個 patch 在同一篇新增一行寫 16,第 38 行卻仍是 14 且沒有日期。接手者讀到兩個「現在值」。14 在這個 patch 之前就已落後(當時是 15),這次又加了一層矛盾。第 38 行應補「以程式碼為準」或更新到 16。

### 3. Systems/規格閘 的負責範圍與風險高流程描述沒跟著改
severity: minor
blocking: 否
引句:「規格閘查格式(不合 rc1),推送前規格閘查整張表的指紋有沒有對得上的 expected-signed 簽核」
file:line:
- `/Users/enzo/harness/lumos-highrisk-evidence/docs/lumos-toolchain-knowledge/Systems/規格閘.md:8`(`responsibility:` 欄)
- 同檔 `:39` 與 `:85`

具體失敗場景:
- 計劃寫「Systems/規格閘(負責範圍補預期值表檢查與推送前查簽)」,patch 只改了 `updated` 與新增 WHY,`responsibility` 沒動。
- 第 39 行 KEY 寫「風險高照半套:紅綠只印不擋、回退節照擋、指路 loop next」,第 85 行的流程描述也沒提預期值表與簽核。
- 單看這兩行,風險高的擋法漏了表格檢查,與同檔新 WHY 不一致。「紅綠只印不擋」本身仍成立,所以只是漏列。

## 六篇必答節點

- **Systems/規格閘**:受影響,見 finding 2、3。新增的 WHY 與 PITFALL 形狀都對,都有出處、因、test 這些必有鍵。
- **Systems/bound-tests-gate**:不影響。它的 ★INVARIANT★ 管的是 code-loop check 對固定席合約測試逐支真跑,這個 diff 不碰那段。圖譜裡只有 svg 檔被列進牽連。
- **Systems/reversibility-governance-ledger**:不影響既有合約。新 WHY 與程式一致:閘 `signoff`、kind `expected-signed`、hard=False,但 `(signoff, expected-signed)` 不在 `_GOV_LOCAL_PAIRS`,所以寫進版控帳,推送前才讀得到。欄位型別表(`_GOV_FIELD_TYPES`)的加法也與筆記一致。第 31 行的 KEY 只講舊的 signoff 流程,沒講 `--expected` 走治理帳。這只是漏寫,沒有矛盾,不另立 finding。
- **Systems/lumos-cli-read**:不影響。它的 ★INVARIANT★ 是 `search` 排除 superseded 節點,與本案無關。
- **Projects/規格落成可驗收條件_計劃**:不影響。「半套只印不擋」那句對風險高的紅綠仍成立。d9「不補人簽門」管的是風險低四行已排除理由的自我認證,新計劃 d10 已明寫兩者對象不同。
- **Projects/雙向門放行_計劃**:不影響。patch 加的補述是「風險高照半套(2026-11-04 起…另要預期值表與簽核)」,與程式一致。

## 其他照文件走過一遍的項目

這些都一致,不另立 finding:
- 指令:`lumos signoff <計劃> --expected --note`。
- 旗標:`--by`、`--ref` 帶 `--expected` 回 rc2。
- 生效日:2026-11-06。
- 環境變數:`LUMOS_HIGH_RISK_EVIDENCE_SINCE`。
- origin:human 與 ai,AI 簽放行並印一行提示。
- 擋下訊息三種開頭:帳讀不到、有預期值表原因、只有風險低原因。
- 版本號:程式是 `_NOGO_SKIP_LOGIC_VERSION` 8、`_DOOR_RULE_VERSION` 16。

總結:全份最高 major
