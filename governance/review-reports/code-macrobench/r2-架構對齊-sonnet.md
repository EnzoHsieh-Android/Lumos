severity: major

## 問 1:分層與依賴方向

**一致,沒有跨層直呼。**
- 新碼放在 `_compose_metrics_mode` 後面、`_lint_watch_mode` 前面,同一個「vault-free 子指令」區段。對照:`scripts/lumos:39173`(compose)、`scripts/lumos:39606`(新的 `_macrobench_mode`)。
- 呼叫鏈跟鄰居一樣:`main()` 的分派行呼叫 `_xxx_mode(repo, as_json, update_baseline)`,再往下拆小函式。對照:`scripts/lumos:66417`(compose)、`scripts/lumos:66419`(macrobench)。
- 新碼只用既有底層:
  - 數值判斷用 `_secev_num`(`scripts/lumos:8554`)。
  - 寫基準檔用 `_write_lf`(`scripts/lumos:28446`,註解寫明是「vault 唯一寫入原語」)。這比鄰居 compose 直接 `open(..,"w")`+`json.dump`(約 `scripts/lumos:39279`)更貼專案原語,沒有另寫一套寫檔。
- 基準檔外層用 `{"version": 1, "entries": ...}`,專案裡有同樣包法(`scripts/lumos:26430`、`:31952`、`:36190`)。
- 註冊位置有對上:`HELP_WHEN`(`scripts/lumos:64988`,緊貼 compose-metrics 那行)、argparse(`scripts/lumos:66070`)。`--repo` 的 `dest` 命名(`macrobench_repo`)比照 `compose_metrics_repo`。
- 測試放在 `t_compose_metrics_audit` 後面(`scripts/test_lumos.py:17393` 起),跟鄰居相鄰。

## 問 2:命名與錯誤處理

**一致。**
- 設定檔壞掉一律印 `擋下:...` 到 stderr 並回 rc 2。對照:`scripts/lumos:39198/39202/39207`(compose)、`scripts/lumos:39386-39391`(macrobench 的 `_macrobench_config`,由 `_macrobench_mode` 印 `擋下:`)。
- 沒接(沒有設定檔)回 rc 0,有退步也回 rc 0(只提醒)。基準檔讀不了時「不比、也不蓋掉」,跟 compose 的 `baseline_unreadable` 行為同款(`scripts/lumos:39306-39322`)。
- `--json` 輸出走 `ensure_ascii=False`,函式內才 `import json`,都跟鄰居同。
- 檔名 `macrobench.json` / `macrobench-baseline.json` 對應 `compose-metrics.json` / `compose-baseline.json`。
- 測試沿用 `check(...)` 風格。用 `TemporaryDirectory` 而不是鄰居的 `mkdtemp`:專案內 322 處對 639 處都有,不算第二種做法。
- 文字輸出用中文,compose 是英文。鄰居內部本來就中英混雜,而且這屬措辭偏好,不列 finding。

## 問 3:第二種做法

**沒有。**
- 寫檔、數值判斷、設定驗證、`_load_lumos_inproc` 都用既有的。
- `_macrobench_mod()` 只是薄包裝。測試裡的 `_mb_run` 是把鄰居內嵌的 `sp.run([sys.executable,GRAPHCTL,...])` 抽成輔助函式,不是新做法。
- 真結果檔放 `governance/research/macrobench/`。專案測試本來就會讀 `governance/` 下的檔(`scripts/test_lumos.py:22876`、`:23076`),不算新做法。

## 不對齊的發現

### B1:新增頂層指令,沒有跟著鄰居更新「指令總數」與指令總目錄
- 既有做法:每加一個頂層指令,`ARCHITECTURE.md` 的命令數宣稱和 `skills/lumos-project-notes/reference.md` 的總覽要一起更新。compose-metrics 在 `reference.md:86` 有一整列說明,`:117` 的總覽也有列名。`ARCHITECTURE.md:131` 的圖也列了它。
- 隱患:`t_docs_command_count` 是有機械守衛的總數對照(`scripts/test_lumos.py:31907`)。這次沒同步,它就紅。
- 這次:新增 `macrobench`,但 diff 沒碰 `ARCHITECTURE.md` 與 `reference.md`。
- 我實測(`python3.14 scripts/test_lumos.py -k command_count`):`ARCHITECTURE.md` 與 `skills/lumos-project-notes/reference.md` 都是 `claim={'93'} actual=94`,`t_docs_command_count` FAILED(2 條斷言)。
- 不一致 N:2 檔。
- 另外 `reference.md` 沒有 macrobench 的用法列,而 compose-metrics 有。這是同一族問題。

severity: major
blocking: 是
引句:「"macrobench": "Android 專案跑完 Macrobenchmark 後:啟動時間、滑動每幀耗時有沒有比基準變慢(只提醒,不擋)。",」
佐證:file: `ARCHITECTURE.md:108`(「93 個頂層命令」,同檔 `:112`、`:142` 也有);file: `skills/lumos-project-notes/reference.md:117`(「93 個頂層命令」,compose-metrics 的詳列在 `:86`);file: `scripts/test_lumos.py:31907`

重判依據:這是文件不一致,而且會讓測試與推送被擋(上面實測紅),符合判準原句「會讓測試或推送擋下 → major」,所以改成「major ＋ 是」。檔級等級和末行的 major 計數跟著 B1 改,其餘內容沒動。

我跑測試時留下的暫存現場(`gctl-run-okexksqv`、`gctl-run-_4fcibrw`)已用字面路徑刪掉,別的會談的 `gctl-run-*` 沒碰。

不對齊共 1 條,其中 major 1 條
