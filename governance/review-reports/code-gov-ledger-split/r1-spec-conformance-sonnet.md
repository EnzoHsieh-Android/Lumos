severity: minor

# 治理帳例行紀錄分流 對答案報告(spec vs /tmp/code-gls-r1.patch)

## F1 〈做法〉7 圖譜同步漏掉 lumos-cli-read 的使用紀錄帳檔名
severity: minor
blocking: 否
引句:「(2026-10-04 起使用紀錄與例行治理觀察改寫不進版控的 .usage-local / .governance-local,」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:34,37,58,117,140`——spec〈做法〉7 圖譜一項寫「[[Systems/retrieval-ranking]]、[[Systems/lumos-cli-read]] 與 [[Verification/2026-08-21_工具鏈體檢修復批]] 裡使用紀錄帳的檔名」要改;retrieval-ranking、工具鏈體檢修復批、reversibility-governance-ledger(count 標記已改 7 並含 GOV_LOCAL_LOG_NAME)都已動,但 lumos-cli-read 仍寫 context/show 寫 usage-log 事件帳、doctor --ci 寫 governance-log,沒提新檔名(此條不在 patch 內,是對 repo 現況 grep 的結果)。屬文件同步縮水,不影響行為。

## 已實作
- 做法1 白名單:`_GOV_LOCAL_PAIRS`(patch 約 53-64 行)含 doctor-run/ran、ledger-growth/fast、nodehome-check+drift-check/passed、note-shape/hinted、delguard/ok、spec-gate/spec-gate-run、daily-wrapper 五種、note-reread 三種;check-* warned 22 個閘逐一列、無前綴比對,且與 repo 內 run_doctor 實際寫 warned 的閘一一核對相符(check-j 未列);bound-tests、code-loop、fix-check、design-loop 皆不在名單。
- 做法1 判定:`_gov_routes_local` 兩欄位須為 str、`ev.get("hard") is False` 且 pair 在名單(patch 128-134)。
- 做法2 防漂移釘:`t_gov_split_pairs_drift` 三項檢查(閘名在 _KNOWN_GATES、每組有寫入點、三判定閘不在名單)。
- 做法3 檔名路徑:常數 `GOV_LOCAL_LOG_NAME`/`USAGE_LOCAL_LOG_NAME`,單一取路徑函式 `_docs_local_log_path(docs_dir, name)`;三個寫入器(_gate_event 用 docs、_append_governance_log 用 vault.parent、_usage_log 用 env.vault.parent)都用它。
- 做法4 寫入器:_gate_event 決定路徑後照舊寫、失敗回 False;_append_governance_log 逐筆分 tracked/local,兩本各自開檔各自吞錯;_usage_log 改寫新檔、舊檔不動;`_BOOKKEEPING_FILES` 與 `_COCHANGE_DEFAULT_EXCLUDE` 加兩新檔名並保留舊名。
- 做法5 忽略規則:根 .gitignore 加兩行;`_scaffold_project` 加兩行(共用 `_LOCAL_LOG_IGNORE_LINES` 常數);`_ensure_docs_gitignore` 由 `_init_additive_setup` 呼叫,docs/ 不存在不動、不存在建只含兩行加註解、存在逐行比對(rstrip、不去行首空白)、二進位追加、沿用 CRLF、尾端補換行;doctor `_local_ledger_doctor_msgs` 用 ls-files + `check-ignore -q` 回 1 才提醒,其他值不提醒。
- 做法6 讀者:cmd_gov 抽出 `_gov_row` 並多 load 本機帳;S18 `_doctor_metric_lines` 任一本存在就讀、oldest 只取版控帳;spec-gate 段後半改走 `_gov_ledger_rows_by_time`(帶時區比、解析不了排最前、同時間保持讀入順序、版控帳在前);判定類讀者與帳本成長段未動;本機帳加只看大小的軟提醒(共用 _LEDGER_MB_CAP)。
- 做法7 測試:doctor-run 既有測試改讀本機帳(patch 約 5977 hunk)並新增 `_gov_events_all`、`_gov_since` 輔助;圖譜 reversibility-governance-ledger / retrieval-ranking / 體檢修復批、手冊 reference.md、兩個 REVISIT 計劃在 repo 內都已含新檔名(不在 patch,grep 確認);scaffold 與 `_pull_source_or_abort` 註解已同步。
- S1 `t_gov_split_routine_goes_local`、S2 `t_gov_split_decisions_stay_tracked`(含 skipped-flag、unfilterable、shallow-skip、drift-check warned、code-loop 留痕只靠版控帳)、S3 `t_gov_split_readers_union`、S4 `t_gov_split_local_write_failure`、S5 `t_gov_split_ignore_rule`、S6 `t_gov_split_pairs_drift`:六支測試都在 patch 內且名稱與 spec 的 [test:] 相符。

## 多做
無(patch 內非 spec 對應的行為變更:無;_BOOKKEEPING_FILES 與 cochange 排除清單加新檔名屬 spec 做法4 明列範圍內)。

## ⚠ 交編排者
- [S3] 條款含 S18 度量兩本合算,`t_gov_split_readers_union` 只驗 `_gov_ledger_rows_by_time` 與 `gov --stats` 載入源,未直接驗 S18(`_doctor_metric_lines`)與 spec-gate 段的合併結果,也未驗「帳本成長段只讀版控帳」;實作本身符合,只是測試覆蓋比條款窄,是否算縮水請裁。
- 圖譜/手冊同步不在 patch 內,以上依 repo 現況 grep 判斷。

縮水+未實作共 1 條
