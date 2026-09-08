# 審查有沒有用記帳 r1 — 收貨與編排者機械重現

preflight-4: ran

分級 standard(通才 / 接手的人 / 簡化守護者 算人數,＋架構對齊、外家否決)。被審的是「讓審查有沒有用變成機器數得出的帳」的設計提案。

## 前掃(preflight-4)——乾淨 agent 只給原始問題

十一條機械宣稱:八條符合、一條部分符合、一條不符合、一條查無依據。全部在凍快照之前修進真檔:

| 類 | 命中 | 修改前 → 修改後 |
|---|---|---|
| ④ 部分 | 「對今天 14 份席報告實算,自動數跟手填一致」 | 我量的是下午那 14 份(全是 SOP 格式);前掃對早上 8 份重算,嚴重度嵌在標題裡、機器數到 0;驗收輪 2 份把前輪已折平的舊項連舊 severity 留著,數會多 → 改寫成「下午 18 份 16 份一致;三種格式;驗收輪舊項要排除」,並在 [S1] 加 SOP:已折平項寫 `severity: resolved`、自動數排除它 |
| ④ 查無依據 | 「不回填 154 份舊卷證」 | 154 是同事轉述、查不到算法 → 改成自己數的:席報告 846 份、帳上 783 個相異路徑 |
| ④ 不符合 | 「canary 帳幾 MB」 | 實量約 1 MB |
| ② 位置 | 「code-loop skill 第 8 步已有 escape 那句」 | 它是第 8 步之後的獨立段落 → 照實寫 |
| ① 未定義 | DORA | 當場展開 |

八條符合的:1216 筆、refute 0/1216、`--findings` 在 skill 寫存活條數、駁回沒有 id、逃逸帳今天第 1 筆、SOP 每條一行 severity、gov --stats 三段都在、disposal 尾端觀測段在。


## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 通才-sonnet | ⚠ 12 句 1 句錨不到(頓號寫成逗號,「為什麼」段引句,不掛 finding) | ok 20 | 觀測 |
| 接手的人-sonnet | ✅ 全數錨定 | ok 13 | 觀測 |
| 簡化守護者-sonnet | ✅ 全數錨定 | ok 23 | 觀測 |
| 架構對齊-sonnet | ✅ 全數錨定 | ok 14 | 觀測 |
| 外家否決-codex(terra/medium) | ✅ 全數錨定(正規化:去重複印出的第二份、引句全形括號改半形、一句含『』巢狀截到巢狀前) | ok 7 | 觀測 |

## 編排者自己重現的(≥major 一律自己查過才折)

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| a1 自動數在真實格式上數到 0 | 通才 F1 blocker、接手 F2 blocker、簡化 F1 blocker、通才 F2/F3、接手 F1/F3、架構 major | 開 code-enforcement-obs/r1-通才.md(三條全嵌標題)、code-batch13 四席(`- [major]` 列表)、-b 驗收輪架構席(留舊項);讀 `_report_severities`(fullmatch 獨立行,禁第二份) | **HIT** → ★不自動數★,改必填 `--reported`,解析只當下限守衛 |
| a2 報 8 → 存活 9 算術倒退 | 通才 F5 blocker | 對 -b r1 帳:三席 reported 0+2+6=8,findings_set 9,i9 是我自踩 | **HIT** → `--self-found-set` |
| a3 駁回清單可灌大、不驗 | Codex #2、通才 F4、接手 F6 | 讀既有 sets 的寫側驗證只驗集合關係 | **HIT** → 必帶(none 可)、id 對 intake、理由含實字、讀側不印比率 |
| a4 舊帳缺欄位只有「報」印 ?,其他四格會偽裝成數字 | Codex #1 | 讀舊列(無 findings_set) | **HIT** → 五格各判 |
| a5 選填=沒人填 | 接手 F4、簡化(確認)、架構 minor | refute_verdicts 0/1216 | **HIT** → 必填 |
| a6 `severity: resolved` 不在值域 | Codex #3、架構 minor | 讀 `_SEV_ORDER`/`_report_severities` | HIT → 不引入新值,舊項不留 severity 行 |
| a7 ci-wait 紅燈提醒是噪音 | 簡化 F6 | ci 帳 12 紅 0 逃逸 | HIT → 不加 |
| a8 逃逸帳無輪次 | 簡化 F5 | 讀 `cmd_loop_escape` rec | HIT → 印「迴圈累計」 |
| a9 「每輪一行」歧義 | 接手 F8 ⚠ | 讀 disposal 只取最新輪 | HIT → 明寫「問閘的這一輪」 |
| a10 「駁回」會被讀成審查員錯 | 接手 F5 | — | HIT → 一律寫「編排者重現不到」 |
| a11 樣本太少也印總數 | 接手 F7 | 227 迴圈 45% 兩週無帳 | HIT → K<5 印提醒 |
| a12 段內比率 Σ折/Σ報 | 接手 F6 | — | HIT → 段首第二句 |
| a13 --findings 仍被 light/gate 硬依賴 | 通才 F8、簡化 F3 | 讀 6775/6850 | HIT → 明寫不動、不鼓勵省略 |
| a14 design-loop 逃逸句位置 | 通才 F7 | 讀 SKILL 步驟 10 | HIT → 步驟 10 後獨立段 |
| a15 兩本帳分段可行 | 通才 F6、Codex(確認) | 讀 `_render_gov_stats` 段落結構 | HIT(可行)→ 照既有段落慣例 |
| a16 回放模式觀測尾 | 接手 F9/F10 | 讀既有慣例 | HIT → 凍結/回放不印觀測尾 |

## 折入的十六條

a1–a16 全折,accepted 為空(輪內有 blocker)。碼層的翻紅釘留給實作(t_canary_reported_required / t_canary_refuted_set / t_gov_stats_review_yield)。

## 我判錯、被席位糾正的

- 我以為席報告數得出「報幾條」——只對我自己下午那批 SOP 格式成立;三席各拿一種今天真的在用的格式打穿,而且我的計劃裡那句「嵌在標題的早就被寫側擋」是錯的(寫側只要求至少一行宣告)。
- 我又把一條回頭條件寫在句中(REVISIT 不在行首),前一案剛被三席抓過同一件事——這次自己在折入時發現、改成獨立行。

## 留痕紀律

★這一份在按下記帳之前寫完★。carrier=接手的人-sonnet(全錨、算人數、最高 blocker)。

## 處置

16 條全部折入,accepted 為空。折入改了 S1 的核心做法(自動數→必填),★派 r2 驗收折入★。

(本檔在此之後不再修改。)
