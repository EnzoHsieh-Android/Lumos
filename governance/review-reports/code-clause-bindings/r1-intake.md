# code-clause-bindings r1 — 收貨與編排者機械重現

preflight-4: n/a(code 迴圈)

分級 standard(單 reviewer 算人數,＋架構對齊、外家否決 Codex terra/xhigh)。被審的是 條款綁測試算進度 [S1]+[S3] 的實作(clause_bindings 七態、spec-trace 條款表與裁決、handoff 一行、處置閘第五步)+ 5 支測試。
★這批動的是設計審的處置閘本身★——弄壞會讓所有設計審過不了、或該擋的靜默放行。

## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 單reviewer-sonnet | ✅ 全數錨定 | ok 11(2 條「missing」是多行號合寫格式,檔在) | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok 17(1 條同上) | 觀測 |
| 外家否決-codex | ✅ 全數錨定(正規化:去行尾雙空白、去重複印出的第二份) | ok 27 | 觀測 |

## ★審材混進別人的碼(單reviewer F9)★

凍結 patch 裡有 `_lumos_config_near_vault`/`_scope_policy`/cmd_lint scope 檢查/`t_lint_scope_policy`——不是本案的,是另一個 session(工具分類計劃)在同一工作樹上還沒提交的段落,被我的 `git add` 掃進 commit。
處置:`reset --soft` 拆回,用 hunk 分類(關鍵字)只 stage 我的 7+2 段、別人的 3+1 段留回工作樹,重做 commit 802fdad;我的測試在拆後的樹上仍綠。**第五型並行事故第三次,記憶已有條目,這次還是踩到——因為我只看 `git diff --stat` 沒逐段看內容。**

## 編排者自己重現的(≥major 一律自己查過才折)

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| f1 只在範例/引用出現的 id 被當條款、讓閘 FAIL | 單 F1 blocker、Codex C4 | 純函式餵「### [S1] 真條款 [test:t_ok]\n寫法例如 `[S9] …`」→ S9 untagged → 閘 FAIL | **HIT** → fallback-only id 標 undefined,不算條款 |
| f2 表格列不算定義行 | 單 F2 | lead 正則字元類沒有 `\|` | **HIT** → 加進去 |
| f3 顯式 root 被 env 反推蓋掉 | 架 A1、單 F3 | 讀 `_clause_bindings_for` 與呼叫端 6703 的 `_dsp_root` 規則 | **HIT** → root 贏 |
| f4 cutoff 字串比日期依時區判不同 + 當日制 | 單 F4、架 A5 | ts=2026-09-08T20:00-05:00(真 UTC 09-09)→ 舊碼判「早於」;`_SEV_WRITESIDE_CUTOFF` 註解明寫隔日制 | **HIT** → `_loop_ts_key` 換算、隔日 09-09、壞 ts fail-closed |
| f5 .patch 跳過只看副檔名可繞 | Codex C1 | `_disposal_clause_step(…, "design.patch")` → skip | **HIT** → 看 `_roster_kind`,設計審非 .md → FAIL |
| f6 `[manual: ]` 空字串算靠人 | Codex C2 | `- [S1] 甲 [manual: ]` → manual → 閘 PASS | **HIT** → <4 字視同未標 |
| f7 `[manual:]` 宣稱同家族卻沒進 INV_TAG_RE | 架 A4 | 讀 3027-3037 標記叢與 3381 獨立軸慣例 | **HIT** → 搬到叢裡、收進 INV_TAG_RE |
| f8 docstring/help/四份文件仍講舊語意 | 單 F5/F6、架 A2、Codex C3 | grep 六處 | **HIT** → 全改 |
| f9 spec 讀不到的處置跟 G3 不一致 | 架 A3 | 讀 13522 vs 我的 13440 | HIT(實務上 G3 先擋)→ 措辭對齊、仍 fail-closed |
| f10 同一句提醒兩種排版 | 架 A6 | 對照兩處 | HIT → spec-trace 改兩行 |
| f11 閘測試沒有真索引的「綁了→過 / 懸空→只提醒」 | 單 F7 | 讀測試:兩個判定 case 都只用 manual | **HIT** → `_clause_repo` 真索引補兩 case |
| f12 「只被提到」態沒走過真索引 | 單 F8 | fixture 只有 t_ok/t_gone | HIT → fixture 加註解提到的名字 |
| f13 審材混進別人的碼 | 單 F9 | 見上節 | HIT → 拆 commit |

## 折入的十三條(去重後)

f1 undefined 態(單 F1、Codex C4)/ f2 表格列(單 F2)/ f3 root 優先序(架 A1、單 F3)/ f4 cutoff 隔日+UTC+壞 ts(單 F4、架 A5)/
f5 迴圈類型判跳過(Codex C1)/ f6 manual ≥4 字(Codex C2)/ f7 標記家族(架 A4)/ f8 文件六處(單 F5、單 F6、架 A2、Codex C3)/
f9 讀不到措辭(架 A3)/ f10 提醒排版(架 A6)/ f11 真索引閘測試(單 F7)/ f12 mentioned 整合(單 F8)/ f13 拆 commit(單 F9)。
翻紅釘四個:manual 空也算(5 紅)/ 回到副檔名判(2 紅)/ 字串比日期(2 紅)/ 非定義也當條款(4 紅)。折完 8 個子集 757 案例全綠。
★INVARIANT★ 文字隨語意改了,已另派乾淨 agent 重審(結果見 r2 intake)。

## 我判錯、被席位糾正的

- 我以為「範例行不算定義」就夠——席位證明它仍會被當成一條待標條款,而那正是我自己計劃裡的寫法。
- 我把 `root` 與 `env` 的優先序寫反,跟同一支函式其餘四步相反,兩席獨立抓到。
- 我對 cutoff 用了字串比對,同一支檔案裡 `_loop_ts_key` 的說明就寫著這種錯法。
- 我第三次把別人未提交的段落掃進 commit。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=單reviewer-sonnet(全錨、算人數、最高 blocker)。

## 處置

13 條**全部折入,accepted 為空**——輪內有 blocker,依規則 accepted 必空。r2 派全新席驗收修復與掃 delta。

(本檔在此之後不再修改。)
