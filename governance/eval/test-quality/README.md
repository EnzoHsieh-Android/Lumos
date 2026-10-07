# 測試品質固定考卷

這批資料驗證「工具是否能找到指定形態」，不證明測試的業務正確性或 Agent 讀手冊後一定改善。

- `corpus-v1.json`：七種來源語言、各四個人工分類樣本。自比／重抄、獨立字面值、合理穩定性測試刻意並列；合理穩定性測試也會命中自比，所以命中不是不當測試的裁決。
- `report.schema.json`：靜態、固定故障及考卷報告的共用格式。`complete` 是執行／範圍完整性，`verdict` 固定 `not_assessed`，不代表品質放行。
- Python CLI 考卷在 `scripts/test_test_quality_scan.py`，由既有 `t_test_quality_scan_cli` 接入全套測試。

在工具鏈來源 repo 執行：

```sh
python3 scripts/test_lumos.py -k test_quality_scan_cli
python3 governance/eval/test_quality_pilot.py > /tmp/fault-report.json
python3 governance/eval/test_quality_corpus.py --semgrep /path/to/semgrep > /tmp/corpus-report.json
```

Python 使用內建 AST；其他語言選配 Semgrep CE 1.179.0，先只含特定斷言介面的自比規則；Swift 僅 XCTest，Swift Testing #expect 尚未支援。跨語言的重抄算式案例在規則未接入時必須顯示 `unanalysed`，不能算通過；backend 缺失／未掃到快照／有解析錯顯示 `unavailable`。因此目前完整跨語言考卷可以回傳 2，應同時查看 `supported_checks_match` 和每個案例的範圍。

固定故障只停用兩個掃描器辨識分支，各選一條已有獨立預期值的 CLI 行為考卷；保存基準綠、目標斷言紅、還原綠及來源 hash。它不接受任意測試命令或生產環境操作。

後續手冊效果實驗須固定開發題、模型、起始程式與故障評分器，兩臂只有是否讀新規範不同；保留輸出與重複次數。這個固定語法考卷不是該實驗，也不提供跨真實專案的誤報率。

## 手冊效果試行

`handbook-baseline.md`、`handbook-candidate.md` 與 `handbook-manifest.json` 是凍結實驗材料；政策仍以共用手冊為單一來源，候選文字依證據決定是否採用。

離線驗評分器：`python3 -m unittest discover -s governance/eval -p test_test_quality_handbook.py -v`。

執行固定模型兩臂（會使用 Claude 配額）：`python3 governance/eval/test_quality_handbook.py --run --out /tmp/handbook-new-run`。`--lane behavior` 只跑行為題，`--lane trigger` 只跑入口模擬；輸出目錄必須為新目錄，保存原始事件、材料摘要、測試與故障結果。

入口模擬用明示技能目錄與 Read，非原生 Skill 調用；行為題強制載入規範。生成測試僅允許固定 unittest 語法子集，超出者列無效；此 runner 不是通用程式沙盒。人工敘述核對是探索性觀察；機械評分不讀 arm 或文字說明，只看固定斷言紅綠。首批不完整場次按 instrument-disposal 排除，不能直接累加所有 results.json 的 valid 數。

### 人工推導澄清與原生路由重驗

`handbook-holdout.json` 固定 shipping/calendar 兩個新業務題與故障，`handbook-clarified.md` 是澄清候選快照。行為 baseline 此次是前批 candidate，與原規範不同；澄清版只補人工從規格推導答案與固定字面值。

- 行為：`python3 governance/eval/test_quality_handbook.py --run --suite holdout --lane behavior --out /tmp/handbook-holdout-behavior`。首個 verify.py 回饋前最後完整 Write 為 first_draft_score，最終交付為 score，分開報。
- 原生路由：`python3 governance/eval/test_quality_handbook.py --run --suite holdout --lane native-trigger --out /tmp/handbook-holdout-native`。用隔離 project skill、唯讀 Read/Skill；init 只准有待測技能，Skill invocation 與實際 handbook Read 分開核對。

原生路由两臂是原 description／擴充 description，body與手冊相同；兩個lane的baseline含义不同。評估不更動全域技能；模型呼叫沿固定模型、一次每題每臂，不把未載入、拒絕或逾時當作路由失敗。只有Claude Code隔離native路由被量測，其他宿主與技能共存環境另驗。

有限迴圈僅支援固定字面值 tuple/list、字面值容器變數及 dict.items、字面值 range；可用 self.subTest。未知迭代器拒絕，逾時亦列無效。生成源碼保存於 .first-draft.json／.tests.json 的 code 與 SHA256。若事後補齊考卷語法，凍結原始事件與分數並對全部兩臂一致重算，生成 runner SHA 與重算 runner SHA 分開留存。


## 真實歷史弱測試重播

`python3 governance/eval/historical_test_quality.py --out /tmp/lumos-historical-new-output` 重播一個固定歷史案例，輸出目錄須全新；只需要本地完整 git 歷史與 Python 標準庫，支援 POSIX symlink/SIGALRM。它在暫存 HOME 與筆記庫執行歷史錯版／修復版、原弱測試／修正強測試四組，保存 code hash 及原始結果。強測試原8秒鬧鐘改2秒；程序超時、匯入錯、零／缺少預期斷言、情境前置不成立都不能算檢出。這是考卷預檢，不執行模型輸出，也不證手冊效果。
