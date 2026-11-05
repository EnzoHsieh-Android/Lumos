# r3 收貨紀錄(推送只跑受影響測試)

## 收貨

- 六席全數交回、格式與引句全過:正確性 5、邊界 4、流程 7、合約圖譜 4、通才 5、架構對齊 5(其中第 5 條是報告結尾重複的總結等級,不是獨立發現),共 30 條。
- 主結論:r2 為了補「沒開 PR 就沒 CI」而讓 CI 推任何分支都跑,這一步把 gates 的後盾閘、沒有本機 main 的環境、逐次推送的增量範圍(後推的純文件提交只跑文件子集,綠燈蓋掉前面紅的全套)、同提交多 ref 排隊一起帶進來;主線判法綁遠端名,是 `_note_reread_mainline_names` 已經淘汰的舊形狀;`suite=full` 分不出「算不出範圍」也會被降級。

## 先查世界(使用者 2026-11-05 裁「收不乾淨的你就上網釐清方向」)

- PRIOR-ART: CI 觸發常規——push 只限預設分支、pull_request 不限,避免同提交跑兩次;沒開 PR 的分支沒有 CI 是公認接受的代價(https://adamj.eu/tech/2025/05/14/github-actions-avoid-simple-on/ 、https://docs.publishing.service.gov.uk/manual/test-and-build-a-project-with-github-actions.html 、https://github.com/rubygems/rubygems/commit/924d916a73 )。採用:CI 不改(本 repo 本來就是這個形狀),r2–r3 的「CI 推任何分支都跑」整段拿掉。
- PRIOR-ART: GitHub 必過檢查要在 PR 最新的頭提交上過,舊提交的結果不算(https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks )。採用:合併一律走 PR、對 PR 頭提交 `ci-wait` 判定 green;PR 事件一律全套,帳本提交也會在新頭上再跑一次全套,所以頭提交一定有全套。
- PRIOR-ART: pre-push 只跑快的、掛鉤可被繞過、CI 才是擋的那道(https://dev.to/jameson/pre-push-hooks-42g5 、https://pypi.org/project/prepush-ci/ )。採用,與本篇方向一致。

## 逐條去向(28 折、2 放行、0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 正1 | 正確性 #1 | 主線改用 `_note_reread_mainline_names`(固定名 + 候選分支名,不看遠端名);S4 補「沒有任何遠端追蹤 ref 時推 main 也是 true」 |
| 正2 | 正確性 #2 | 新欄位 `suite_computed`,算不出範圍照全套;S2、S5 |
| 正3 | 正確性 #3 | 範圍刪除(CI 不改) |
| 正4 | 正確性 #4 | 範圍刪除(CI 不改,gates 不會在功能分支跑) |
| 正5 | 正確性 #5 | 旗標改成只有 `--pushed-ref`、寫明只判主線不改 `--diff` |
| 邊1 | 邊界 #1 | 範圍刪除(CI 不改);合併改看 PR 頭提交,PR 事件一律全套 |
| 邊2 | 邊界 #2 | 同正1 |
| 邊3 | 邊界 #3 | 範圍刪除(CI 不改) |
| 邊4 | 邊界 #4 | 〈實務隱患〉改寫:舊版不認得旗標 → argparse 拒絕 → `pf_json` 空 → 全套,連純文件推送也全套 |
| 流1 | 流程 #1 | 範圍刪除(CI 不改,不會有沒本機 main 的功能分支 CI) |
| 流2 | 流程 #2 | 同邊1 |
| 流3 | 流程 #3 | 範圍刪除(不改觸發樣式) |
| 流4 | 流程 #4 | 範圍刪除(CI 不改) |
| 流5 | 流程 #5 | 〈實務隱患〉時間一條寫明同時執行上限與 `ci-wait` 逾時不等於綠 |
| 流6 | 流程 #6 | 訊息寫明合併前等 PR 頭提交判定 green;記憶與歷史紀錄的處理寫進〈不做〉;全域那句仍是 Q1(放行,見下) |
| 流7 | 流程 #7 | RETIRE-IF 改數 PR 頭提交 shards 工作的結論,另記上線前基準 |
| 合1 | 合約圖譜 #1 | 範圍刪除(CI 不改,gates 照舊只在 main 與 PR 跑) |
| 合2 | 合約圖譜 #2 | 範圍刪除(不改 ci.yml,`t_secev_s32_ci_tag_job` 等不受影響) |
| 合3 | 合約圖譜 #3 | 做法 4 補 pitfalls-code-loop;ci.yml 註解不改所以不用同步 |
| 合4 | 合約圖譜 #4 | 〈不做〉寫明歷史紀錄不改 |
| 通1 | 通才 #1 | 同正1 |
| 通2 | 通才 #2 | 同邊1 |
| 通3 | 通才 #3 | 範圍刪除(CI 不改) |
| 通4 | 通才 #4 | 〈回退〉逐處列做法 4 的每一處 |
| 通5 | 通才 #5 | 同流7 |
| 架1 | 架構對齊 #1 | 同正1 |
| 架2 | 架構對齊 #2 | 同正5;掛鉤用 `pp_q` 引號 |
| 架3 | 架構對齊 #3 | 掛鉤讀新欄位用現有 `grep` 寫法(做法 2) |
| 架4 | 架構對齊 #4 | 做法 4 補 pitfalls-code-loop;主線判定的家是筆記內容閘那篇,兩邊互連於實作時寫 |
| 架5 | 架構對齊 #5 | 放行:報告結尾重複的總結等級行,不是獨立發現 |

放行理由:
- 流6 的全域那一句:全域 CLAUDE.md 在 repo 外,改它要使用者點頭,仍列 Q1;訊息已寫明合併前要等 CI 判定 green,與全域「要等 CI 結果出來才回報完成」不衝突。
- 架5:同上表。

refuted: none
