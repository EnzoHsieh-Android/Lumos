# r1 收貨(2026-11-08,高風險級七席 sonnet:正確性、資源、邊界、合約、通才、架構對齊、資安)

七席報告全數存檔、正規化;資安席判 clean、沒有引句(乾淨報告不需要);邊界席第一次交回 3 句引句錨不到(它自己標了「不是逐字」),退回刪掉那幾行後全錨定。全輪 23 條(major 1、minor 22)。id:co 正確性、rs 資源、bd 邊界、ct 合約、tc 通才、ar 架構對齊,加報告裡的 F 序號。

合約席回報查看時誤下了一次 `git checkout --detach`、已自己接回分支;編排者核對:分支仍是 EnzoHsieh-Android/rulepack-review-blind-judge、HEAD 仍是 f8c89efff、工作目錄沒被改,reflog 多一筆 checkout。

pitfalls 內建風險型樣「共享狀態有沒有鎖保護」命中 `rules-unwired/coroutines.yml` 第 11 行:五席(正確性、資源、邊界、合約、通才)都判誤報——那是搬過去的 `kt-mutex-reentrant` 規則文字 `$M.lock()`,不是會跑的程式;併發類在本 repo 本來就判範圍外。

## 先查世界

- PRIOR-ART: 探針要驗消費端真正讀的欄位——同一份 SARIF 要經過新增告警閘那支 `_lint_run_and_parse` 才算數,跟「測試要走真實路徑、不要只驗結構」同一個道理(本 repo `commands/03-寫回圖譜.md`〈實作測試品質〉);不另查外部,因為消費端就在本 repo。採用:探針改呼叫閘的解析函式。
- 其餘是本 repo 內部的文字與命名一致性,不涉外部做法。

## 逐條去向

| id | 一句 | 去向 | 重現 |
|---|---|---|---|
| tc1 | SARIF 探針只看 ruleId,閘要的位置與工具名沒驗 | 折:改用 `_lint_run_and_parse`,加「規則對但沒有檔案位置」改壞案例 | HIT:改回只看 ruleId 時新案例紅 |
| tc2 | 統計「會擋規則守到的列數」沒跟著降 | 折:重算 129→128 | HIT:程式重算 128 |
| tc3 | review_ids 擴到 unwired 沒測試 | 折:加不接閘規則 review-fp 樣本案例 | HIT:改回只認 rules-review 時新案例紅 |
| tc4 | sgconfig-unwired.yml 沒進 about_code | 折:lumos append | HIT:讀節點 about_code |
| tc5 | SARIF 掃描是第三份子程序樣板 | 折:改借閘的函式,不再自己開子程序 | HIT:讀碼 |
| co1 | review_ids 新分支沒測試 | 折:同 tc3 | HIT:同 tc3 |
| co2 | load_rules 說明寫三個目錄 | 折:改四個 | HIT:讀碼第 66 行 |
| rs1 | 新測試留規則包複本暫存 | 放行:假 ast-grep 目錄已用完即刪;`_ktpack(copy=True)` 的複本是既有測試的共同寫法,改它屬另一件事 | HIT:讀碼 |
| rs2 | 新設定檔沒進 about_code | 折:同 tc4 | HIT:同 tc4 |
| bd1 | 空的 rules-unwired/ 在 git 留不住 | 折:放 `.gitkeep` | HIT:邊界席暫存複本重現 |
| bd2 | 新設定檔沒進 about_code | 折:同 tc4 | HIT:同 tc4 |
| bd3 | RULE 的確認日期被順手改成今天 | 折:改回 2026-11-05,不冒用 | HIT:讀節點第 24 行 |
| bd4 | 探針寫死規則 id、改名時訊息誤導 | 折:先核對探針規則在指定目錄,不在就講清楚 | HIT:讀碼 |
| ct1 | 新設定檔沒有家 | 折:同 tc4 | HIT:同 tc4 |
| ct2 | 節點仍寫「靠盲判排除」 | 折:改成「改規則形狀時拿來對照」;前案計劃已作廢,留著當歷史 | HIT:讀節點第 62 行 |
| ct3 | [S2] 條款綁的測試沒驗放 rules-unwired | 放行:那條條款同時管訊息格式等多件事,綁的測試照舊有效且有斷言抓「非 hint 引用出處不全」;新行為另由 `t_kotlin_rulepack_unwired_dir` 守 | HIT:讀碼 |
| ct4 | WHY 換綁後前半句失去綁定 | 折:原 WHY 綁回型錄格式測試,新行為另寫一行 WHY 綁新測試 | HIT:讀節點 |
| ct5 | 「不改任何擋停」與提示級少擋 8 條不一致 | 折:改成「不收緊任何擋停」並寫明放寬那一點 | HIT:讀計劃 |
| ar1 | load_rules 說明 | 折:同 co2 | HIT:同 co2 |
| ar2 | r.get 與 r[...] 兩種取法 | 放行:刻意——既有測試的假規則沒有 dir 鍵,計劃寫明缺鍵照不在 unwired 算;message_problems 那邊的規則一定有 dir | HIT:讀碼 |
| ar3 | 新測試命名家族不同 | 折:改名 t_kotlin_rulepack_unwired_dir | HIT:讀碼 |
| ar4 | 新測試印頭尾、同族不印 | 折:拿掉 | HIT:讀碼 |
| ar5 | 第三份子程序樣板 | 折:同 tc5 | HIT:同 tc5 |

修補因果:首輪,無。
