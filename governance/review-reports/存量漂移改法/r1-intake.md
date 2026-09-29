preflight-4: ran

# r1 收貨紀錄(存量漂移改法)

## 前置掃描(首輪,派一席 Sonnet 5.5 唯讀掃四類;報告原樣存 r1-preflight.md)

- 結果:①未定義詞 0(輕微 1:結案狀態兩個集合沒分);②壞引用 2(函式名 _drift_acks_load、_drift_findings 不存在;舉例的計劃其實還沒收尾);③範圍矛盾 5;④機械宣稱 29 條,不屬實 1、部分屬實 12。沒有一條動到核心裁定(Enzo 2026-09-29「現在開始」做五項改法,方向由 rtb 回報決定),全部由編排者直接修進計劃;修改前的整份另存編排者暫存區(plan-fix-before-preflight.md),〈做法〉到〈條款〉前後差 35 行。

| 前掃項 | 類 | 修改前(摘) | 修改後(摘) |
|---|---|---|---|
| ④#10 印舊理由 | 語意不屬實 | 「並印舊理由供參考(`_drift_old_reason`)」 | 不能借它(原路徑還在就跳過),要新寫「同路徑、清單變了」的查找 |
| ② 函式名 | 存在 | `_drift_findings`、`_drift_acks_load` | `_drift_state_findings`(c1 在 `_drift_guard_findings`)、`_drift_load_acks` |
| ②③ 舉例 | 語意 | 最低Python版本改3.14_計劃 的 lumos.cmd 那條(該計劃還在 doing) | 兩席相反時端出張力_計劃(已收尾、留著之後才到期的 REVISIT) |
| ③-1 E5 範圍 | 語意 | 只談 Issue | 標記對所有類型都做,QUERY_CLOSED_STATUSES 值列出 |
| ③-2 範圍漏 c3 | 語意 | 〈範圍〉⑥ 只寫 c2 | c2、c3 |
| ③-3 --kind | 語意 | --kind c1\|c3\|c4 | 接受全部種類,由函式回 2 指路(argparse 那層擋印不出該走的指令) |
| ③-5 --test 必填 | 語意 | 沒交代 | --test 改選填:pending 沒給擋下、pass 補改用不到 |
| ④#7 補完 | 語意部分 | 「照既有做法」 | 寫明是新行為,不是既有的「pending 補完」 |
| ④#11 相容理由 | 語意部分 | 「只取需要的鍵」 | 整行原樣回傳、只驗 path 與 kind,下游只取四個鍵 |
| ④#14 set 列出位置 | 語意部分 | 「同計劃收尾的做法」 | 接在 main 分派處 cmd_set 成功後,新加 Issue 分支;不經 cmd_set 的寫入不列 |
| ④#16 正文自驗 | 語意部分 | 「改完重讀自驗」 | atomic_write_verify 只驗開頭欄位,另外重讀並跑同一支判定確認發現已不在 |
| ④#19 valid_under 形狀 | 語意部分 | 清單、純量兩種 | 單行、清單、多行區塊三種;清單好幾項都含就擋;只換一項要新寫 |
| ④#21 git log -S | 語意部分 | 取最早一筆 | 會連預告行命中,逐筆用 _guard_formal_line 判正式行才算;shallow 擋 |
| ④#26 收尾集合 | 語意部分 | 沒分 | c2/c3 用 _DRIFT_CLOSED,E5/S7 用 QUERY_CLOSED_STATUSES |
| ④#29 回退找得回來 | 語意部分 | 靠 fixed.txt | 新增修復帳 governance/drift-fixes.jsonl 逐筆記改前改後 |
| 編排者查到 | 語意 | c3 --status pass\|fail | 驗證紀錄合法狀態沒有 fail:改 pass\|stale\|superseded\|abandoned(lint 類型狀態表) |

- 屬實、不用改的:④#1–6、#8、#12、#13、#15、#17、#20、#23–25、#28。

## 席位收貨

- 凍結材料:r1-snapshot.md(115 行,前置掃描修正後的版本);7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet(Sonnet 5.5);外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。
- 7 席全交,等完成通知、ls 確認後才讀。席報告暫存目錄裡另有一支 codex-prompt.txt,時間是同日 13:24,是更早那輪(最低 Python 3.14 設計審)留下的,跟這輪無關;這輪 7 份報告的時間都在派工之後。clone-ns 的 reflog 只有編排者自己的提交;工作目錄裡 canary 帳多的兩列是編排者跑 spec-gate 時工具寫的。
- report-normalize 7 份都已是正規化格式;quote-check 6 份全錨定,邊界席 1 句「c4 的證據是「猜」」不到 10 字不採信,那條(F12)另有別的引句。
- 發現 61 條(邊界 12、正確性 11、架構對齊 10、接手 9、外家 7、併發 6、回滾 6;機器數各報告的 F 標題與 severity 行),major 25(外家 6、架構對齊 4、邊界 4、接手 4、正確性 3、併發 3、回滾 3)。
- 多席獨立報到的同一件:git log -S 找不到原地轉正(正確性、邊界、併發、外家);修復帳沒進簿記名單(接手、回滾、架構對齊、外家);c4 整欄換與指定方式(正確性、邊界、外家、架構對齊);先判定再上鎖(接手、併發);表態多筆與 related 來源(邊界、併發、接手、架構對齊);提示還教手改(正確性、接手、邊界);fixed.txt 殘留(回滾、架構對齊、外家、正確性、邊界)。
- 有 major,accepted 為空,全折。

## 機械重現(編排者在臨時 repo 與 clone-ns 跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1 / 邊界 F1 / 併發 F1 / 外家 F1(git log -S 找不到原地轉正) | 臨時 repo:一行「預告:X 會成立」提交 plan,原地換成「KEY:★INVARIANT★ X 會成立 [test:a]」提交 settle;`git log -S "X 會成立"` 與 `git log -G "★INVARIANT★ X 會成立"` | HIT:-S 只找到 plan、-G 才找到 settle |
| 接手 F1 / 回滾 F1 / 架構對齊 F1 / 外家 F6(修復帳沒進簿記名單) | 讀 scripts/lumos 的 _BOOKKEEPING_FILES | HIT:表態檔在、修復帳不在 |
| 架構對齊 F2(既有 _set_conditions_locked 已處理三種寫法) | 讀 _set_conditions_locked 說明 | HIT:四種寫法(單行、清單、空的、多行區塊)一律整段重寫,擋空值與換行 |
| 架構對齊 F3(git log -S 有先例) | `grep -n '"-S' scripts/lumos` | HIT:每支檔有家的上線點用 `_nodehome_git(... "-S…")` |
| 併發 F3(鎖 30 秒) | 讀 `_VAULT_LOCK_STALE_SEC` | HIT:30 秒 |
| 正確性 F9 / 接手 F2(提示教手改) | `grep -n "手改成歷史說法" scripts/lumos` | HIT:drift check 擋下時那段 |
| 其餘 | 讀碼核對各席引的 file:line | 採信;席位附的其他實測沒有逐條重跑 |

## 處置

- 全部折入,細節寫在計劃〈審計修正紀錄〉r1 段。另外編排者自己查到:計劃裡當範例寫的 `[[<節點>]]` 與存量漂移防線計劃裡的 `[[後續紀錄]]` 被 doctor 當成斷掉的連結、擋了推送,包進反引號。
- refuted 無;accepted 無。
