severity: clean

沒有能構成攻擊路徑的發現。我讀了完整快照與修補差異,沒有另外跑測試,也沒有做變異實驗。因此下面每條只是依程式碼推論,沒有附跑過的重現。

**③ 這輪特別要看的:推 main 或會直接上主線的 ref 會不會被判成功能分支**

已看,無。

- 判斷在 `_pitfalls_pushed_mainline`。被推的 ref 不是 `refs/heads/` 開頭(標籤、空字串),或剛好等於 `refs/heads/`,一律回 true,照全套。
- 分支短名在主線名集合裡也回 true。集合是固定的 main、master,再加主線候選指到的分支名,不看遠端名。
- 照常操作下,推到 main 的形式都會落到 `refs/heads/main`:
  - `git push origin HEAD:main` 與 `git push origin feat:main` 都會是這個 ref。
  - `git push origin main:feature` 的目的地是 feature,判成功能分支,屬於刻意放寬。
  - 本機名與遠端名不同時,判斷只看遠端 ref(掛鉤傳入 `$_rref`),所以不會被本機名騙過。
- 查主線候選失敗或逾時,集合退回固定的 main、master。main、master 仍然判成主線,只有非標準主線名(如 develop)會被當成功能分支。這個方向不影響推 main。
- 照常操作下,pitfalls 出錯、被 Ctrl-C 中斷、或舊版不認得 `--pushed-ref`,`pf_json` 都是空的或不帶 `pushed_mainline`。掛鉤那段需要 `"pushed_mainline": *false` 與 `"suite_computed": *true` 兩條同時成立才降級,所以這幾種情形都照全套。
- 檔名等可控字串進 JSON 時引號會被跳脫成 `\"`,掛鉤的 grep 比對不到 `"pushed_mainline": false` 這串字,不能靠檔名偽造降級。
- 混推 main 與功能分支時,main 那個 ref 維持 full,`_SUITE_FULL` 因此為 1,整次推送照全套。
- CI 端:push 事件只限 main(`.github/workflows/ci.yml` 第 5-6 行),`pull_request` 事件一律全套。推 main 的路徑沒有被放寬。

**① 提示注入**

已看,無。

- 新增的輸出是固定的中文說明句與 `$_SUITE_KEYS` 的回顯。
- `$_SUITE_KEYS` 來自 `affected_keys`,是既有路徑,這次沒有新增注入面。
- 說明句沒有把分支名、檔名或筆記內容帶進給 AI 的派工詞。

**② 讀寫與執行越界**

已看,無。

- `--pushed-ref` 的值只用於字串比對與前綴判斷,不寫檔、不進 shell。
- 掛鉤的 `_pf_extra` 用陣列傳參並加引號,沒有 shell 插值。
- 掛鉤用 grep 探測 `dest="pf_pushed_ref"`,是讀檔找字樣,不執行對方。
- 快照裡沒有新增下載網址、環境變數覆蓋點、密鑰或信箱。我用 grep 掃 `@…com`、`key`、`secret`、`http` 等,命中的只有帳本裡的 `token` 欄位(SPEC-、CANARY- 編號)與專案既有的 GitHub 網址。

**範圍外,順手一提**

- 功能分支的主線名集合信任本機的主線候選 ref。刻意改 ref 讓主線名消失屬於刻意多步偽造,系統天花板,不加機制(minor,blocking: 否,只有推論,沒有攻擊路徑)。

**我看過的檔(完整快照改到的 20 個檔)**

- 程式與掛鉤,逐行讀過:`scripts/hooks/pre-push`、`scripts/lumos`。
- 為了確認集合與邏輯,另外讀了 repo 的 `scripts/lumos` 裡的 `_note_reread_mainline_names`、`_diff_range_ends`、`_NOTE_REREAD_MAINLINE_NAMES`。
- 為了確認 CI 事件範圍,另外讀了 `.github/workflows/ci.yml`。
- 其餘只確認在快照裡出現,沒有細讀逐行內容:
  - 文件與筆記:`ARCHITECTURE.md`、`CLAUDE.md`、`README.md`、`README.en.md`、`skills/lumos-project-notes/commands/08-自動跑的.md`。
  - 圖譜筆記:`Projects/依實測覆蓋挑測試_計劃.md`、`Projects/推送只跑受影響測試_計劃.md`、`Projects/推送與CI提速_計劃.md`、`Systems/bound-tests-gate.md`、`Systems/pitfalls-code-loop.md`。
  - 帳本、基準與放行設定:`docs/.canary-log.jsonl`、`docs/.escape-log.jsonl`、`docs/.kill-log.jsonl`、`governance/anchor-baseline.json`、`.lumos/lint-waivers.json`。我只對這幾個檔和快照整體用 grep 掃過密鑰與信箱,沒細讀內容。
- `scripts/test_lumos.py`:新增的 t_prepush_feature_branch_* 等六支測試案例我沒有逐行讀,上面關於「本機與遠端不同名」的結論是依掛鉤與 `_pitfalls_pushed_mainline` 的程式碼推論,不是看測試輸出。

臨時目錄:我沒有建立任何臨時目錄,不需要刪。
