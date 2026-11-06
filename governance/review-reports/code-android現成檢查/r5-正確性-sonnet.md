severity: minor

第 5 輪驗收:r4 三個重現(欄位值、資料夾連結、repo 內檔案連結)都修好了,沒有會擋的問題。下面三條是一般小問題。

驗了什麼:
- 我跑了 `python3.14 scripts/test_lumos.py -k lint_android_ci`,160 過 0 敗。
- 我用 `worktree add` 取 cd36e5e04 舊版,拿同一組輸入前後各跑一次。
- 我在臨時副本做了 8 種改壞(只動副本,沒碰 repo)。

符號連結(修補問題二):
- 連結鏈(`chain.yml` → `hop2.yml` → `hop1.yml` → `real.yml`,在 repo 內)新版照讀,舊版略過。
- 連結迴圈和懸空連結略過,不拋例外。
- 指到 repo 外的連結,不論檔案本身或資料夾那層是連結,都略過。
- 把 `_path_resolves_in_root` 改成永遠回 True,7 條斷言轉紅。

F1 `command:` 欄位把一般 run 指令也當 gradle 任務列
severity: minor
blocking: 否
引句:「# CircleCI gradle orb 的 command、Bitrise gradle-runner 的 gradle_task(出處見計劃〈依據來源〉;代碼審 r4 四席)。」
- `_CI_GRADLE_TASK_FIELD` 認欄位名,不認它屬於哪個 orb 或哪個 step。
- CircleCI 一般 `run:` 底下的 `command: npm run build`、`command: |` 區塊裡的 `make build`,都被當成 gradle 任務列,A1 提醒因此被壓掉。
- 最小重現:對 `_android_ci_lint_evidence` 餵 `- run:\n    command: |\n      make build\n      ./gradlew assembleDebug\n`,新版回 True,舊版回 False。
- 同樣的情況還有:Ansible 的 `tasks:\n  - name: build`、`empty_field_then_deeper_map`(`tasks:` 底下縮排更深的子表 `foo: build`)。
- 後果只是少印提醒,屬於這個設計刻意偏向的方向(寧可少印)。但計劃寫的「其他欄位照舊不算」在這裡不成立。
- 計劃或註解該明說這個天花板,或把 `command:` 限縮到同層有 `gradle/` 前綴的 job 名。

F2 欄位值「結束偵測」缺同欄位的別欄負例
severity: minor
blocking: 否
引句:「if not ln.strip() or ind > field_col or (ind == field_col and ln.lstrip().startswith("-")):」
- 把 `ind > field_col` 改成 `ind >= field_col`(區塊純量後面同縮排的別欄,例如 `name: build`,會被吞進任務列)。
- 160 條測試全綠,沒有一條抓到。
- 負例只涵蓋縮排比欄位淺的 `next:`,沒有涵蓋同欄的兄弟鍵。
- 真實 YAML 裡 `with:\n  arguments: |\n    …\n  name: build` 是常見形狀。
- 補一條負例即可:`with:\n  arguments: |\n    assembleDebug\n  name: build` 應回 False。

F3 區塊純量標記 `>`、`>-`、`|-` 沒有測試
severity: minor
blocking: 否
引句:「if not val or re.fullmatch(r"[|>][-+0-9]*", val):」
- 把 regex 縮成只認 `|`,測試全綠。
- 實測現行對 `arguments: >-\n assembleDebug\n build` 回 True(正確),但沒有測試守住。
- 同類缺口:連結迴圈(`except (OSError, RuntimeError)` 分支)沒有專屬測試。我手動驗過行為正確,只是拿掉那個分支測試也不會紅。

測試獨立判準:
- 「其他欄位不算」、`tasks`/`command`/`gradle_task` 三個欄位名、`field_col` 重設、Jenkinsfile 註解,這幾處各自改壞都會轉紅:
  - 拿掉重設,轉紅 1 條。
  - 刪 `gradle_task`,轉紅 1 條。
  - 刪 `command`,轉紅 1 條。
  - 擴大欄位清單加 `name|needs`,轉紅多條。
  - 拿掉 Jenkinsfile 的 Groovy 註解剝除,轉紅 3 條。
  - 拿掉清單項同欄判定,轉紅 1 條。
- 語料測試 `t_lint_android_ci_corpus` 抓得到 A1 全印或全不印這類大改壞。
- 欄位偵測的細節邊界只靠 `t_lint_android_ci_advice`,語料測試沒覆蓋。

角色鏡頭 be-api-compat、be-authz:這次改動是 lint 工具內部的靜態字面判定,沒有對外 API,也沒有端點授權,不適用。

臨時目錄與 worktree 已清。

總結:最嚴重是 minor(`command:` 欄位誤吞一般 run 指令、結束偵測測試缺同欄負例),會擋 0 條
