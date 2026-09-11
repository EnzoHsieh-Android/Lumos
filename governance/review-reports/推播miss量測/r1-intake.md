preflight-4: ran

# r1 收貨紀錄(推播miss量測)

## 首輪前掃(便宜 agent,四類固定清單)

- 掃描對象:計劃筆記修正前的副本。結果:未定義的詞 2、壞引用 0、範圍自相矛盾 1、機械宣稱驗語意 13 句中 11 句屬實、1 句部分屬實、1 句不屬實。
- ①③ 直接修真檔,不算 findings:
  - 「edit 卷」沒解釋 → S2 補一句是推播品質評測題庫 `governance/eval/retrieval-goldset.json` 裡「編輯時推播」那份題目,由 refresh_labels.py 維護(編排者開檔確認 `edit` 鍵存在、23 題)。
  - 「建議二」本文沒交代 → 緣起補一句建議二是什麼、為什麼要零命中數。
  - 〈承認的限制〉標題說每條附回頭條件,「位置偏差」沒附 → 補事件入口(任何要拿本儀器輸出改推播排序的計劃,設計審先交代位置偏差)。
- ④ 語意類命中(修真檔,修改前→後逐條留痕;都不動核心裁定,不升級為 finding):

| 句子 | 修改前 | 修改後 | 編排者重現 |
|---|---|---|---|
| S3 零命中判法 | 輸出含「無節點符合」或命中數為 0 | 文字輸出結尾那行是「(共 0 篇候選」,或 `--json` 的 `candidates` 是 0;兩種都對不上記「判不出」 | HIT:`lumos search "zzqxj不存在的詞"` 印「(共 0 篇候選,照相關性排序…」,`--json` 印 `"candidates": 0`;「無節點符合條件」是 `lumos query` 的字樣 |
| S2 規則內 | 正文用反引號寫到 F 的路徑——跟 impact 抓直連同一條規則 | 用現在的圖譜跑 `lumos impact --file F --json`,出現在 direct 就算(完整路徑+檔名唯一時的檔名比對兩條規則,直接問 impact 不另寫) | HIT:`_impact_reverse_lookup` 有 body-inline-code 與 basename-match 兩條;`impact --json` 的 direct 帶 hit 種類 |

- 編排者順手補(不是前掃命中):S2 加「事後才有」一類(筆記在那次編輯之後才新建,不算 miss);〈承認的限制〉加「用現在的圖譜判當時的推播」一條並接 REVISIT:2026-09-17。

## r1 收貨

- 派五席:通才-sonnet、邊界-sonnet、整合-sonnet、架構對齊-sonnet、外家否決-codex。★外家否決席缺席★:Codex 帳號額度到 17:25 才重置,那之後先給代碼審第三輪;本迴圈 standard 分級外家席是「缺席要註明」,本輪照此註明,r2 補派。
- 四份報告:三份的格式不合(兩份總結句寫成「severity:值」、一份把 ⚠ 填進嚴重度欄),退回原席自己改(只動那一行);改完 report-normalize 全數通過。quote-check 四份全數錨定;refcheck 全對得上;seat-check 派工單材料欄沒被認到(vacuous)。
- 編排者判讀:四席多處獨立指到同一件事(推播第四段、分數行解析、週跑位置、查詢字串隱私、題庫銜接),依「多席獨立一致」直接折,不派辯方。

## 機械重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| A1 | 讀 `build_ranked_context`:有「守衛面參考——這 N 篇」段;`inject_ranked_context` 註明 lane-only 也注入 | HIT |
| C1 | 同 A1 | HIT |
| A2 | 讀 `PIN_LINE` 與 hook 的分數行格式 `{分數} {種類詞} 節點`:可選 ★TAG★ 群組隔不開種類詞 | HIT |
| B1 | 同 A2 | HIT |
| B3 | 讀 `inject_additional_context` / `inject_ranked_context`:空集合直接 return 不輸出;recount 以附件建列 | HIT |
| B2 | 讀 `scan_file`:讀取窗口 `j > anchor[0]` 沒有上界 | HIT |
| C9 | 讀 `t_lens_recount_classify`:用 SourceFileLoader 載 recount.py,沒有 `_need_src` | HIT |
| A7 | `/usr/bin/time -p` 跑 recount.py 全量 27 秒;`lumos impact --file scripts/lumos --json` 1.7 秒 | HIT |
| D1 | 讀 `governance/autonomous-loop.sh` 的 `run_replay`:獨立週戳、`%G-W%V`、模組失敗不蓋戳 | HIT |
| C5 | 同 D1;每日治理只呼叫自主迴圈 | HIT |

其餘各條(A3–A6、A8、A9、B4–B8、C2–C4、C6–C8、C10、D2–D4)是文件缺陷或設計取捨,讀計劃與對照檔即可判,照席位所附 file:line 核過。

## 處置

- 31 條全折(accepted 0、refuted 0):S1 改四段解析、S2 錨點改成編輯本身與讀取窗口、分類先中先算、事後才有、題庫銜接改成「本案只交清單,另案」並接 REVISIT、S3 改寫成新配對段、S4 移到自主迴圈週期觀測段照 run_replay 慣例並改成上週增量、查詢字串只進本機、新增 S5 測試守門;限制與實務隱患補齊實測數字。
- 編排者自補(不是席位發現):S2 讀取正規化——既有程式只拿檔名比對推播清單,miss 要比對整個圖譜。
