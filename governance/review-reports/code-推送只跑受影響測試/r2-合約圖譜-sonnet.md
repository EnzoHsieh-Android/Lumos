severity: minor

我沒有找到會擋的問題。兩條 finding 都是 minor。

**Finding 1:[S6] 後半句綁的測試守不住它**

severity: minor
blocking: 否

[S6] 的驗收條款有兩半:「功能分支改到測試檔或守衛檔照樣降成子集」,以及「原本就判 light 的功能分支推送不印降級那行」。條款只綁了 `t_prepush_feature_branch_light_ok_false`。後半句實際由 `t_prepush_feature_branch_already_light` 守,這支沒綁在任何條款上。

引句:「- [S6] 當功能分支改到測試檔或守衛檔(`light_ok` 為 false)時,掛鉤 應 照樣降成文件子集加關鍵字子集;原本就判 light 的功能分支推送 應 不印降級那行 [test:t_prepush_feature_branch_light_ok_false]」

file: `scripts/test_lumos.py`(`t_prepush_feature_branch_already_light`)、`scripts/hooks/pre-push`(`_down="light"` 那行)

- **具體改壞**:把 `_down="light"` 改成 `_down="light"; _SUITE_BRANCH_DOWN=1`,原本就判 light 的推送會多印「推功能分支:」。
- **改壞後的結果**:
  - 條款綁的 `t_prepush_feature_branch_light_ok_false` 是 2 passed、0 failed,照綠。
  - 沒綁的 `t_prepush_feature_branch_already_light` 是 2 passed、1 failed,翻紅。
  - 改壞前 20 條斷言全綠。
- **為什麼只算 minor**:全套測試仍會抓到,而且推 main 時掛鉤跑的就是全套。但 `spec-gate` 只驗綁定的測試,條款自己宣稱的守衛沒對上。
- **修法**:在 [S6] 補一個 `[test:t_prepush_feature_branch_already_light]`。
- **歸因**:未判定。修補差異把這支測試加進來了,但沒補綁定;兩版掛鉤的行為相同。
- **同案例**:
  - input 是原本就判 light 的功能分支推送,expected 是不印降級那行。
  - 修前版本我沒取出來比對。
  - 修後版本的改壞前後結果見上。
  - 同一支測試、同一個輸入,兩次結果可比。

**Finding 2:ARCHITECTURE.md 的流程圖還說「push 後是 CI 全套測試」**

severity: minor
blocking: 否

引句:「功能分支的全套由 PR 的 CI 跑(PR 事件一律全套)」

file: `ARCHITECTURE.md:182-183`。圖上寫 `PASS --> CI["CI (GitHub Actions): 全套測試…"]`,接著 `WAIT{"lumos ci-wait (push 後同輪等結論)"}`。

- **失敗場景**:接手的人照圖,推功能分支後就 `ci-wait`。但 `.github/workflows/ci.yml` 的 push 觸發只有 main 與 tag,沒開 PR 的功能分支沒有 CI,`ci-wait` 回 rc0(no-run,不是綠)。
- **跟掛鉤新訊息的關係**:掛鉤的新訊息講的是對的版本,圖沒同步。
- **歸因**:有證據的原有漏查。CI 觸發條件這次沒改,圖本來就不準,這輪改動讓它變得會誤導。
- **同案例**:ARCHITECTURE.md 和 ci.yml 兩邊在修前修後都沒變。

## 逐句對照結果

**中英文 README**
- 兩邊意思一致,都是推 main 在本機跑、功能分支由 PR 的 CI 跑、合併前要等它綠。

**CLAUDE.md 紀律區塊外那段**
- 它說功能分支降成 `--suite keys`,推 main 才在本機跑全套。這跟掛鉤的實際行為一致。
- `ci-wait --sha` 旗標存在(`cw_sha`)。
- 「PR 事件一律全套」在 ci.yml 看得到(第 83 行註解、第 47 行 `pull_request` 條件)。

**`_test_suite_for_range` 的 docstring**
- 跟程式一致。

**其他殘留的舊句**
- 我 grep 了「CI 會跑全套」「CI 會兜底」「CI 後盾」「推送前一律跑全套」這幾種說法,改動範圍裡沒有殘留。
- 其餘命中的是歷史計劃與卷證,不用改。
- `bound-tests-gate.md:40` 與 `ci.yml:217` 說「CI 的全套在 shards 工作當後盾」,對 main 與 PR 的 CI 仍然成立。
- `scripts/templates/graph-discipline.md` 說「全套留給推送前的閘」。這句對消費專案仍成立,因為消費專案沒有這次的降級,刻意不改是對的。

**固定席合約**
- `bound-tests-gate`:code-loop 對綁定測試逐支真跑,這次沒碰,不影響。
- `lumos-cli-read`:search 的 superseded 排除,不影響。
- `design-loop`:處置閘條款綁定,不影響。
- `guard-kill`:rc 優先序與 JSON 純度,不影響。
- `lumos-cli-lifecycle`:re-inject 保留 sentinel 之外的內容。CLAUDE.md 這次改的是 sentinel 之外,不影響。
- `測試假綠形態`:新測試都有現場成立的前置斷言。`failclosed` 的「算不出」案例是把 `"computed": True` 全換成 `False`,換不到就會翻紅;`old_lumos` 先斷言舊版字樣不在。
- `Systems/pitfalls-code-loop` 沒有登記合約。
- `Issues/code-loop守衛main-direct盲區`:這是事故節點,我沒有逐條對它判斷。

**設計對照 [S1]–[S8]**
- 條款綁的 8 個測試名都存在。
- `-k prepush_feature_branch` 實跑,20 條斷言全綠。
- [S6] 後半句現在由 `t_prepush_feature_branch_already_light` 守(見 Finding 1)。

**修補三問**
- **原問題修復效果**:基準 20 條斷言全綠。這只證明修後版本現在通過,沒有修前版本的對照,不能證明問題解決。
- **修補處的正常、錯誤與相鄰路徑**:
  - 推 main、混推、舊版 lumos、算不出範圍、純文件這幾條路,各有對應測試走到。
  - 相鄰路徑裡只有 [S6] 後半句有守衛缺口,見 Finding 1。
- **新發現同案例的修前修後**:Finding 1 的改壞實驗只在修後版本做,修前版本沒有取出。

**沒驗的範圍**
- 沒跑全套。
- 沒對 `Issues/code-loop守衛main-direct盲區` 逐條判斷。
- `_pitfalls_pushed_mainline` 裡 `pushed_ref == "refs/heads/"` 那個子條件沒有單獨的測試。去掉它會讓 `refs/heads/` 空分支名變成 false。這個形狀不在 [S4] 條款範圍,我沒做改壞實驗。

臨時目錄與我那次測試留下的 `gctl-run-*` 現場已用字面絕對路徑刪除,`lsof` 確認刪前沒有程序開著。
