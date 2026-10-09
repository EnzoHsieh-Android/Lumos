severity: major

審查對象是 `/tmp/歷史弱測試手冊評估-r1.md`。我對照了實作 `/tmp/lumos-readme-oct-audit/governance/eval/` 下的三支腳本(`historical_test_quality.py`、`historical_handbook_trial.py`、`historical_case_corpus.py`),也讀了 `test_quality_handbook.py`、`test_quality_pilot.py`、`test_quality_corpus.py`、`test_quality_evidence.py`、`k1_stop_replay.py`、`home_audit.py`。

## 1. 分層與依賴方向:對齊,沒有跨層直呼

- `historical_case_corpus.py:9` 引用同層的 `historical_test_quality`。
- `historical_handbook_trial.py:18-19` 引用同層的 `historical_test_quality` 與 `test_quality_handbook.run_model`。
- `test_quality_handbook.py:20-24` 的註解「模型程序與 CLI 收證共用同一個程序群清理實作,不另抄一份」,同樣是重用既有函式。
- 載入歷史版 `scripts/lumos`(`historical_test_quality.py:44-60`)的方式,和 `k1_stop_replay.py:10-16`、`home_audit.py:load_lumos` 同類:都是 importlib 載入主程式,從腳本往 `scripts/` 單向讀。
- 把模型產生的測試放進子程序執行,也沿用 `test_quality_handbook.py:158-170` 的 `--child` 加 stdin JSON 加 15 秒逾時加最小 env。
- 這一問沒有 finding。唯一要提的是 `sha()` 在各腳本各抄一份(`historical_test_quality.py:22`、`test_quality_handbook.py:48`、`test_quality_pilot.py:digest`),這是既有慣例,不列。

## 2. 命名與錯誤處理:結構對,三處不一致(皆 minor)

ID: ARC-2
severity: minor
blocking: 否
引句:「保存每場原始事件、最終測試code及SHA、來源／手冊／執行器快照manifest和各版細項。」
file: `governance/eval/historical_handbook_trial.py:280`
敘述:既有做法會把「執行器依賴的檔」也記下指紋。`test_quality_handbook.py:347-348` 記了 `runner_sha256` 加 `process_runner_sha256`,`historical_case_corpus.py:76` 記了 `replay_dependency_sha256`。trial 的 manifest 只記 `runner_sha256`(trial 自己),評分實際依賴的 `historical_test_quality.py` 與 `test_quality_handbook.py::run_model` 都沒指紋。`MODEL` 寫死在程式碼裡(`historical_handbook_trial.py:21`),handbook 則放在 manifest JSON 的 `model` 欄(`test_quality_handbook.py:343-346`)。結構相同,欄位漏了。

ID: ARC-3
severity: minor
blocking: 否
引句:「[manual:核對輸出 report.json 的來源與 instrument 欄]」
file: `governance/eval/historical_test_quality.py:104-111`
敘述:這支是考卷預檢,和 `test_quality_pilot.py:34-36` 與 `test_quality_corpus.py:22-25` 同類。後兩支用 `report.schema.json` 的形狀(`schema_version`、`kind`、`tool.source_sha256`、`complete`、`verdict:'not_assessed'`),過關旗標叫 `complete`。這支輸出 `preflight_passed`、`runner_sha256`、`instrument`,corpus 用 `controls_passed`,trial 的 controls 也用 `controls_passed`。逾時在 pilot 與 handbook 是 `{'status':'timeout'}`(`test_quality_pilot.py:30-31`、`test_quality_handbook.py:167`),這裡併進 `invalid` 加 `reason:'child-timeout'`(`historical_test_quality.py:64-65`)。計劃本身寫的是「逾時列無效」,所以語意一致,只是標記名稱不同。`--out` 目錄內的檔名也各異:`report.json` 加 `test-materials.json`、corpus 的 `manifest.json` 加 `results.json` 加 `summary.json`、`test_quality_handbook.py:351,401` 的 `manifest.json` 加 `results.json`。

ID: ARC-4
severity: minor
blocking: 否
引句:「保留原產物，按根因處置，不調分母迎合成績。」
file: `governance/eval/historical_test_quality.py:26-29,87`
敘述:既有固定考卷遇到前提不成立時,把狀態記進報告並回傳 2,例如 `test_quality_pilot.py:51-52` 的 `invalid-mutant`。這三支的前提檢查是 `git show` 的 `check=True`、`historical_case_corpus.py:34,49` 的 `raise ValueError`、`assert ... == 1`。它們會直接炸出 traceback(退出碼 1),而且 `historical_case_corpus.py:72` 先 `mkdir` 再 `load_materials()`,失敗會留下空的輸出目錄、沒有任何卷證。這與計劃自己的 RETIRE-IF「保留原產物」不一致。另外 `assert` 在 `-O` 下會被拿掉。

## 3. 第二種做法:有 1 條 major

ID: ARC-1
severity: major
blocking: 是
引句:「control 無規範，handbook 強制提供正式共用手冊〈實作測試品質〉全文；不是技能路由評估。」
file: `governance/eval/historical_handbook_trial.py:266-268`
敘述:專案既有的手冊實驗不直接讀正式手冊。`test_quality_handbook.py:349-350` 讀 `governance/eval/test-quality/handbook-*.md` 這些凍結副本,並記 `handbook_sha256`。`governance/eval/test-quality/README.md` 與副本開頭都寫「凍結實驗材料(政策來源仍為共用手冊)」。trial 改成每次執行時即時讀 `skills/lumos-project-notes/commands/03-寫回圖譜.md`,用 `split('**測試必須有獨立的判準')` 和 `split('## ')[0]` 切字串取出,而且 manifest 沒有手冊的 SHA。這是兩種不同的凍結方式:這份技能文件日後被改,同一個 runner 的 handbook 臂內容會悄悄變掉,事後也無法用指紋驗證。標題一改還會在切字串時 IndexError。manifest 有存全文,所以事後仍可人工對照,但機械上沒有凍結。

其餘項目都屬既有做法的延伸,不算第二種:
- `historical_handbook_trial.py` 的 AST 白名單、受限 builtins、`--child` 模式,和 `test_quality_handbook.py` 的 `validate_test`、`execute_tests`、`child_main` 同一套骨架。因為 fixture API 不同(`total`、`route` 對 `fixture`、`s.*`),分開實作可以接受。
- 證據放 `governance/review-reports/test-quality-historical-*`,與既有 `test-quality-handbook-*`、`test-quality-three-evidence` 同位置。
- 用 `r1-snapshot.patch` 加 base 重建 Java 錯版(`historical_case_corpus.py:31-50`),是重用既有審查快照,不是新做法。
- `--out` 要求全新目錄(`exist_ok=False`)、每列寫完就落檔並 `flush`,也和 handbook 一致。

## 4. 落點:合理,沒有 finding

- 計劃的 `lands_in` 只列 `Systems/historical-test-quality`。該節點 `about_code` 已涵蓋三支腳本,職責「歷史弱強測試重播與受限 unittest 模型對照」包得住 corpus 與 trial。
- 它的 `related` 已連到 `Systems/test-quality-handbook`,用 `run_model` 這個依賴關係也有交代。
- 不需要改寫進 `test-quality-handbook`(`run_model` 本身沒改)、`test-quality-multilang`(擁有的是 `test_quality_corpus.py`,不是 `historical_case_corpus.py`)。
- 另開新節點沒有必要。
- 順帶一提:`governance/eval/test-quality/README.md` 有新增段落,它不是圖譜節點,不需列入 `lands_in`。

不對齊共 4 條,其中 major 1 條
總結最嚴重 severity: major；blocking 共 1 條
