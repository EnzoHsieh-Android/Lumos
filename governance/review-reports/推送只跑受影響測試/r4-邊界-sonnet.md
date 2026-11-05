severity: minor

我逐節讀了 spec,並對照 `push-subset` 的程式碼驗證。沒有實際跑實驗,沒建任何臨時目錄。

邊界題各自的結論:
- **空字串或奇怪形狀的 `--pushed-ref`**:不是 `refs/heads/` 底下的一律判 true,空字串不管被當成「沒給」還是「非 heads」,結果都是全套,方向安全。
- **`pf_json` 只有部分欄位**:不管是截斷還是缺欄位,spec 要求兩個欄位都讀得到才降級,缺一就全套。
- **grep 被其他欄位內容誤中**:不會。`pitfalls --json` 走 `_json_text_escaped(..., indent=None)`,輸出是單行,字串值裡的引號一律跳脫成 `\"`。所以 `"pushed_mainline": false` 這串字面不可能從檔名或程式碼片段偽造出來。字典裡以檔名當鍵的值是清單,不是布林,也湊不出 `true`/`false`。
- **分支名含 `/` 或特殊字元**:`feature/main` 不等於 `main`,不會被當主線。遠端名帶斜線時,`_note_reread_mainline_names` 取最長相符,也沒問題。

severity: minor
blocking: 否(措辭與文件精度,沒有照字面實作會放行壞東西的路徑)
段落:做法 1 `pushed_mainline` 的算法。
問題:spec 寫成 `_note_reread_mainline_names(root, tip)`,有兩處沒交代:
- `tip` 在 `pitfalls` 裡沒有定義。`pitfalls` 只收 `--diff` 範圍,而 `_lens_default_remote` 在 `tip=None` 時看的是目前簽出的分支,`tip` 給了就要完整提交編號。照字面實作的人得自己猜。
- 沒傳 `deadline`。`_git_timeout(None)` 的上限是每次 git 20 秒,沒有整體預算。一個 ref 最多約 15 次 git 呼叫(`remote`、`for-each-ref`、`config`、五個 `rev-parse`、至多五個 `symbolic-ref`)。一次推十幾個 ref 就是十幾輪,而 `pitfalls` 在掛鉤裡也沒有外層逾時。
- 只有在 git 卡住時才會拖到很久,平常大約零點幾秒。逾時時名稱集合退回 `main`/`master`,這個退路 spec 已經接受。
- 同一個 repo 的名稱集合每個 ref 都一樣,只有原本判全套的 ref 才用得到,spec 沒提快取或延後算。
引句:「分支短名在 `_note_reread_mainline_names(root, tip)` 回的集合裡」
佐證:`scripts/lumos:53734`(函式簽名有 `deadline=None`)、`scripts/lumos:65219`(`_git_timeout` 的 cap 與 None 的行為)、`scripts/lumos:65633`(`_lens_default_remote` 對 `tip` 的處理)。

severity: minor
blocking: 否(舊版 lumos 搭新掛鉤的退路只多了一些被吞掉的提醒,仍是全套,方向安全)
段落:實務隱患「算不出來的方向」。
問題:
- spec 說舊版 lumos 不認得旗標時只是「比現在慢」。實際上 argparse 拒絕之後整份 `pf_json` 都空了。純文件推送變全套 spec 有提,但下面幾樣沒被承認:
  - `_tier_high` 恆為 0,高風險提醒不印。
  - tag 路徑的 `stack_questions_applicable` 提醒不印。
  - `_ba=()`(因為 `pf_json` 空),`code-loop check` 少了 `--bound-tests-advisory`,行為變嚴。
- 掛鉤開頭已有「讀 lumos 原始碼找旗標字樣、不執行」的版本錯開慣例(`_CL_KG`、`--suite`、`--graph`),spec 沒沿用。探到旗標才帶 `--pushed-ref`,就能讓舊版 lumos 不丟掉整份 `pf_json`。
引句:「舊版沒欄位或不認得旗標(argparse 拒絕、`|| true` 吞掉 → `pf_json` 空)」
佐證:`scripts/hooks/pre-push:475-479`(探旗標慣例)、`scripts/hooks/pre-push:540-546`、`scripts/hooks/pre-push:591`。

severity: minor
blocking: 否(訊息精度)
段落:做法 3 訊息、做法 4 說明文字同步。
問題:掛鉤裡還有幾句會對功能分支說「CI 會跑全套當後盾」或「CI 會兜底」,但 spec 自己承認沒開 PR 的功能分支沒有任何全套。做法 4 的清單只列了 `_suite_word`,沒列這幾句。
- 降級後的訊息會跟這些舊句同時印出,互相矛盾。
- 做法 3 的「關鍵字空的就只有文件子集」跟現有的「抽不出函式或檔名當關鍵字」那句重複。
- 做法 4 清單與 S7 也都沒涵蓋這些句子。
引句:「掛鉤 `_suite_word` 的說明句」
佐證:`scripts/hooks/pre-push:894`、`scripts/hooks/pre-push:946`、`scripts/hooks/pre-push:963`、`scripts/hooks/pre-push:569`(註解)。

severity: minor
blocking: 否(測試可行性)
段落:驗收條款 S5 與做法 1 的 `suite_computed`。
問題:
- S5 要求「範圍算不出來」時 `pitfalls --json` 回 `suite_computed: false`。但 `_pitfall_diff_collect` 先跑一次 `git diff`,壞範圍會在那裡直接回 None、rc 2、沒有任何 JSON,根本走不到 `_test_suite_for_range`。
- `_test_suite_for_range` 自己的失敗分支(OSError 或第二次 `git diff` 回非零)只能靠 monkeypatch 觸發,沒有 CLI 上的壞範圍可以重現。
- 實際上「算不出」就等於 `pf_json` 空,同樣是全套,掛鉤端安全。但 S5 照字面寫不出紅綠測試,也沒提 `_test_suite_for_range` 有多個 return 點要統一補欄位。
- S4 也沒涵蓋空字串、`refs/heads/`(空短名)這類奇怪輸入。
引句:「當範圍算不出來時,`pitfalls --json` 應 回 `suite_computed: false`;算得出時 應 回 true」
佐證:`scripts/lumos:61787-61830`(`_pitfall_diff_collect` 的 git 失敗回 None)、`scripts/lumos:61705-61734`(`_test_suite_for_range` 的 return 點)。

其餘各節(範圍、回退、PRIOR-ART 與 RETIRE-IF、現況、審計修正紀錄):已讀,無 finding。

實務隱患:
- 併發與負載:無新增風險。
- 守衛面:降級刻意不受 `light_ok` 約束,spec 已列為代價。守衛檔變更時 `affected_keys` 為空,`autoloop_full` 走「抽不出關鍵字就整支跑」,方向正確。
- 主線查詢失敗:只在非 `main`/`master` 的預設分支名才會漏判,spec 已接受。

總結:最嚴重等級為 minor,共 4 條,會擋的問題 0 條。
