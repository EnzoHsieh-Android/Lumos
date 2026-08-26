# r1-intake — 首輪排乾(2026-08-26)

排乾員(便宜 agent)固定清單掃描結果與處置。命中 4 條,全屬排乾類直接修真檔,不算 findings;佐證均經排乾員實際開檔重現(HIT)。

1. 未定義詞(存在類):「信封」「尾文」全庫無他篇使用 → 當場在正文加一句定義。HIT:圖譜 grep 0 篇。
2. 範圍自相矛盾(語意類):[S4] 要印「燒 $X」但資料源 canary 帳無美元欄(cost_cli_args 刻意只送 --tokens/--wallclock-min;file: `governance/autonomous_loop/orchestrator_result.py:54`)。
   修正前:「資料源=canary 帳的 auto-* 迴圈(成本)+ note 裡的結局分類」
   修正後:[S3] note 增帶 `usd=<金額>`(note 自由文字,不發明新欄),[S4] 美元與結局分類都從 note 解析。HIT:`docs/.canary-log.jsonl` 四筆 auto-* 皆無 usd 欄。
3. 機械宣稱(存在類):成本落帳起算日寫 08-24,實為 08-23 15:16 第一筆 → 改 08-23。HIT:canary-log ts。
4. 機械宣稱(語意類):「既有讀者全用 .get() 容錯」字面假(add_gaps 對 weakness 直索引;file: `governance/autonomous_loop/backlog.py:19`)。
   修正前:「既有讀者全用 .get() 容錯」
   修正後:「會讀分數類欄位的路徑都用 .get() 容錯(weakness 是必有鍵、直索引,不受新欄影響)」。相容性結論不變。
   兩條語意類修正皆未觸及核心裁定,依前掃分流直接修真檔。

其餘特驗子項(decay 無呼叫點/160 筆 153 筆 0.5 分/exit 1 無 requeue/兩筆 gap 實丟/line_notify 可復用)逐條屬實,收據見排乾員報告(session 留痕)。
