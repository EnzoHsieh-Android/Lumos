# 收貨紀錄(code-ci文件子集裝工具)

- 分級:pitfalls 判 light(ci.yml 不算程式檔);改的是 CI 這道後盾,照上一批做法派一位審查員加一席架構對齊。
- 審查席原交第一行寫 clean、內文一條 minor,退回該席只改檔級那一行與縮排重交;架構對齊席有一句跨兩行的引句(在「沒有不對齊」段)對不回快照,不是發現。

| id | 席 | 原報 | 一句 | 處置 |
|---|---|---|---|---|
| s1 | 審查 | minor | 沒有測試守 prep 在文件子集時裝工具,刪掉也全綠,同一事故會重演 | 折:新增 t_ci_yml_test_tools_in_sync |
| x1 | 架構對齊 | minor | 註解用 PR 編號當出處,鄰居用日期或計劃節點 | 折:改成日期加 Systems/bound-tests-gate |
| x2 | 架構對齊 | major | 複合動作是專案沒有的第二種重用寫法,既有做法是每個工作各自抄、註解寫「照這步抄」 | 折:拿掉複合動作,prep 照 shards 抄那三步只多一行 if,兩處同步由新測試守 |
| x3 | 架構對齊 | minor | 「照這步抄」指引搬家後跟現況不一致 | 折(同 x2,指引留在 shards 原處、繼續成立) |

## 修補後驗證(這輪修補沒有再派席,編排者機械驗)

- 新測試 t_ci_yml_test_tools_in_sync 10 條斷言過;改壞 6 種各自翻紅:刪掉 prep 的 ast-grep、拿掉 if、if 改錯、只改 prep 的 detekt 版本、只改 shards 的 compose-rules 雜湊、把 ast-grep 那步搬到文件子集之後。
- -k ci_yml 43、-k ci_ 391、-k workflow 2、-k docs_suite 13 全綠。
- CI 上真的裝得上、文件子集轉綠,要推上去由主線 CI 驗。

## 先查世界

- PRIOR-ART:x2——GitHub 官方的重用做法有複合動作與可重用工作流程(https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action);專案既有做法是每個工作各自抄(ci.yml「工作之間不共用機器,每個工作都要自己補」)。不採複合動作:只為這三步引入第二種寫法,其他重複步驟不一起改就是兩種並存;改用抄一份加逐字同步測試,同步風險由測試擋。
