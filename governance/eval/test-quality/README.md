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
