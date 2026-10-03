severity: blocker
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md

## 開場與既有案例銜接、PRIOR-ART／RETIRE-IF

已讀，無 finding。

## 根因與取捨

### F1：一次性的有效設定驗收擋不住分支條件式 include

severity: blocker
blocking: 是
引句:「設定 hook 後讀有效 `git remote` 與 `core.hooksPath`，只有 remote 空且 hook 等於本次副本專用目錄才准啟動模型。」
具體輸入→壞結果：來源在目前分支 main 設定 `includeIf.onbranch:escape.path=/tmp/escape.config`，該外部設定在 escape 分支才加入 remote 並把 core.hooksPath 改成空目錄。建立副本時位於 main，一次性驗收會看到 remote 空、hook 正確而放行；runner 執行普通 `git checkout escape` 後，繼承設定才生效，remote 與弱 hook 同時出現，`git push --dry-run escape HEAD:refs/heads/probe` 實測 rc0。這仍屬設計自稱涵蓋的「繼承 Git 設定及意外 git push」，不是模型主動指定 URL 或停用 hook。file: `scripts/scenario_probe.py:538`、file: `scripts/scenario_probe.py:643`、file: `scripts/scenario_probe.py:716`。
最小翻紅重現：臨時 repo 建 main、escape 兩分支；以 `includeIf.onbranch:escape` 指向含 remote 與弱 hooksPath 的外部 config；於 main 完成一次性驗收後切到 escape。預期 remote 仍空且 pre-push 阻擋，實際 remote=escape、hook 被覆蓋、dry-run push rc0。規格需處理所有可隨 repo 狀態轉換生效的繼承設定，或在 runner 執行期間提供不依賴 repo config 的外層阻斷。

### F2：一般工作樹的絕對符號連結仍可把 runner 寫入導回來源

severity: blocker
blocking: 是
引句:「所有題目及重試改用各自副本，跑完在 `finally` 刪除」
具體輸入→壞結果：來源追蹤 `target.txt`，另有 `escape-link` 絕對連到來源自己的 `target.txt`。`rsync -a` 保留絕對符號連結；規格只拒絕巢狀 Git，現行檢查也只掃 Git 資料內的符號連結。Claude runner 執行 `printf poison > escape-link` 時會直接改寫來源 `target.txt`。本機臨時 repo 實測 source_after=poison；下一次副本也會複製到污染內容，因此「各次乾淨副本」與來源不變同時失效。file: `scripts/scenario_probe.py:510`、file: `scripts/scenario_probe.py:538`、file: `scripts/scenario_probe.py:716`。
最小翻紅重現：臨時來源內建立並提交 target.txt 與指向其絕對路徑的 escape-link；呼叫 `make_sandbox`，再從副本寫入 escape-link。預期來源 byte 相同，實際來源內容改變。規格需在 runner 啟動前拒絕解析到副本外的工作樹符號連結，或提供等價檔案系統隔離。

### F3：`--keep` 對初始化失敗副本同時要求刪除與保留

severity: major
blocking: 是
引句:「導致結果不符，刪除本次副本並報儀器錯誤」／「`--keep` 明確保留每次副本並印其路徑」
具體輸入→壞結果：以 `--keep` 執行含 worktree hook override 的來源，S2 要刪除失敗副本，S3 要保留並列路徑；結果互斥。現碼初始化失敗無條件清理，而 `--keep` 只控制 main 結尾，不能替新設計裁決。file: `scripts/scenario_probe.py:503`、file: `scripts/scenario_probe.py:846`、file: `scripts/scenario_probe.py:988`。

## S1–S5、先紅後綠、隱患、回退、審計修正

各節已讀。S1 巢狀 Git、S2 現有有效設定好例、S3 逐次副本、S4 一般模式清理失敗、S5 空 ID 基本方向無額外 finding；F1、F2 需補翻紅測試，F3 需先裁定三種 `--keep` 情境。

總結：最嚴重 severity=blocker，blocking 3 條。
