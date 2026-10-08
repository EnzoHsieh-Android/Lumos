preflight-4: ran

# r1 收貨紀錄(漂移修法補強)

## 前置掃描(派席之前)

便宜席(sonnet 5.5)照固定清單掃①未定義的詞②壞引用③範圍矛盾④機械宣稱驗語意,報告原樣存 `r1-preflight.md`。①②③與存在類命中直接修計劃,不算 findings;④語意對不上的逐條修改前→後:

| # | 修改前 | 修改後 |
|---|---|---|
| 1 | 借既有 `_vendored_state` / `_vendored_skip` 在提交時判工具檔 | `_vendored_skip` 要 diff 範圍、提交時用不了;改成 `_is_toolchain_repo` 先判,再 `_vendored_state(root, "")[0]` 讀索引;`_delguard_parse_diff` 加 `skip` 參數兩遍共用;拆除工具鏈的提交寫進界線並加 REVISIT |
| 2 | `git show --name-only --diff-filter=A <提交>` | 加 `-c core.quotePath=false`、`-z`、`--format=`,用 `_nodehome_split_z` 拆(不關 quotePath 中文目錄名會被跳脫、永遠比不到;不加 --format= 會混進提交標頭);合併提交落到退回路徑寫進找法順序 |
| 3 | 同提交找到就用它 | 跟計劃名比對有交集只列交集;沒交集列全部、超過 3 個標明由人挑 |
| 4 | c1 只講 TEST、WHY 兩種「轉正後說法」 | 四種各自的辨認寫清楚,放 guard 區段共用判定 `_guard_prose_settled`,guard settle 那句「找不到」一起改(範圍③改寫) |
| 5 | c4 寫入「形狀擋(自由文字)」、`_conditions_rewrite` 回兩值 | check lambda 由 drift 端組;不送筆記形狀擋(開頭欄位不在範圍),各項由 `_conditions_rewrite` 擋空值多行佔位字、再過 `_drift_one_line`;`--values` 的 argparse、`_DRIFT_FIX_OPTS`、`_DRIFT_FIX_ALLOWED` 寫明 |
| 6 | (註記)工具檔清單與同提交更新的情形 | 不矛盾,不改 |

其他:修復帳 c4 加 `reports`、`reports_via` 欄位,RETIRE-IF 改量這個(①-1);`template_used` 寫明比對法(①-2);c3 理由三種寫法都接「;理由:」(③-1);`c4 --values --dry-run` 照慣例不做乾淨檢查(③-2);set 錯誤訊息整句原樣回傳、set 照原樣印(③-3);回退寫明 `_drift_c4_print` 一起改回(③-4)。

## 席位收貨

- 7 席全交(正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex gpt-5.6-sol medium,唯讀沙盒),等完成通知、ls 確認後才讀;clone-ns 的 reflog 只有編排者自己的提交。
- report-normalize 7 份合格;quote-check 7 份對 r1-snapshot.md 全錨定。
- 發現 51 條:正確性 9、邊界 13、接手 10、併發 6、回滾 6、架構對齊 6、外家否決 1;major 17 條(機器數各報告獨立 severity 行)。
- 多席獨立報到的同一件:c4 `--values` 寫完才驗、人寫的新值含三個關鍵詞時留下改了沒記帳(正確性 F3、邊界 F2、接手 F1、回滾 F1);範本佔位字 `<卷證>` `<sha>` 沒擋(正確性 F2、邊界 F1、接手 F2);卷證目錄交集與無交集的處理(正確性 F1、外家否決 F1、邊界 F4);lands_in 漏 delguard(架構對齊 F1、正確性 F9、接手 F4、邊界 F13);接線點漏列(正確性 F7、接手 F3、邊界 F12、併發 F4);頭尾空白自驗打回(正確性 F6、併發 F2、接手 F8、邊界 F8)。以上多席一致或附了可執行證據,直接折,不開辯方。
- 正確性席與外家否決、邊界席在卷證目錄上方向相反(一邊要全列不濾、一邊要不列沒把握的):折成「全列標來源,範本只自動填兩者都有的」,兩邊的失敗情境都擋住。

## 處置

- 51 條全折(folded),accepted 空、refuted 空;折法見計劃〈審計修正紀錄〉r1 段與鏡像核對段(`r1-mirror.md`)。
