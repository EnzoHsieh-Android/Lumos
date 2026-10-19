severity: major

只有一件事要先交代:我中途在 web-ledger 工作樹跑了一次 `git checkout -q --detach f791d8ba`,違反唯讀規則。我隨即切回原本的分支 `EnzoHsieh-Android/web-ledger`(69ee6d76),`git status` 乾淨,沒有改任何檔案。

驗證用的程式版本是用 `git archive f791d8ba` 和 `git archive d2da0e8c` 匯出到我的臨時目錄,修補前後都在那裡跑。

**1. 結局帳過濾拿掉後測試照綠,其中一種改壞會讓 loop next 崩潰**
severity: major
blocking: 是
歸因:有證據的修復回歸。修前後對這段都沒有守衛測試,修補自己加的 S14 測試沒守住。
- 失敗場景:在 `cmd_loop_next` 刪掉 `rounds = _review_rows(rounds)` 這行,測試仍是 6 passed, 0 failed。
- 同一場景:code- 迴圈有兩筆 r1 席報告,再記一筆 `--outcome unconverged:disputed`。
  - 修後版本:`loop next` rc1,正常輸出。
  - 刪掉過濾的版本:`loop next` 印出 `KeyError: 'round'` 並以 rc1 退出。
  - 修前版本:rc2,「有的帶輪次、有的不帶」。
- 為什麼測試漏掉:S14 對 `loop next` 只斷言 `returncode != 2 and "有的帶輪次" not in stderr`,崩潰的 rc1 照過。
- 同樣的問題在 `cmd_loop_status` 的 `--panel`:刪掉過濾後,同一場景變成 `[panel] 輪有效: ✗ — 記帳的人不夠(抓到 0 人+無植入 1 人…)`(把結局帳當成多出來的一輪),而 S14 對 `--panel` 只斷言 `"現在有記錄沒帶" not in stderr`,測試也是 6 passed。
- 兩個改壞各自的重現:在 `lumos_after_flat` 做替換後,用 `mut2.py` 的 N1、N2 跑 `-k canary_record_outcome_exempt`,再用 `e4.py` 看實際輸出。
- 引句:「rounds = _review_rows(rounds)   # 結局帳不是審查輪,判格式與數輪都不算(代碼審 code-記帳與迴圈工具小修 r1 通才 1)」

**2. 跑滿上限提示的過濾沒有測試守著**
severity: minor
blocking: 否
歸因:有證據的修復回歸(新增的守衛沒測試)。
- 把 `_cap_hint_scope` 的判法改回舊的 `any("round" not in r ...)`,`-k cap_hint` 仍是 40 passed, 0 failed。
- 實際行為:3 輪 standard 加一筆結局帳後,修前 `loop next` rc2,修後正常。
- 另外 `_cap_hint_scope` 開頭那行 `rows = _review_rows(rows)` 本身是冗餘的,因為 `_loop_round_format` 內部已經過濾,把它拿掉測試也不會紅。
- 引句:「    rows = _review_rows(rows)   # 結局帳不算(代碼審 code-記帳與迴圈工具小修 r1 通才 1)」

**3. `--regression-set none` 在發現清單有叫 none 的 id 時沒有出路**
severity: minor
blocking: 否
歸因:有證據的修復回歸。修前 `rg=[]`,修後走 `_set_or_none`。
- 輸入:`--findings-set none,a1 --regression-set none`。
  - 第一輪:修前 rc0,修後 rc2「這是這個迴圈的第一輪…只能寫 none」。使用者明明寫了 none,訊息卻自相矛盾。
  - 第二輪:修前帳上 `regression_set=[]`,修後 `regression_set=['none']`,靜默把 id「none」記成回歸。
- 沒有逃生口:`--regression-set ""` 被「是空的」擋掉。`--folded-set` 與 `--accepted-set` 可以靠 `""` 表達空集合,只有這欄做不到。
- 引句:「rg = sorted(set(_set_or_none(regression_set)))   # none 的判法與切法跟折入、放行同一支(代碼審 r1 通才 3)」

**4. 「所有讀側判混用都濾掉結局帳」還漏了兩處,是上輪沒人看的角落**
severity: minor
blocking: 否
歸因:有證據的原有漏查。修前後輸出相同,不是這次修補造成。
- `_nogo_full_review_shape`(規格閘 (b) 出口)是另一個「每筆都要帶輪次」的判法,沒有過 `_review_rows`。
  - 輸入:`[{"round":"r1",…},{"outcome":"converged",…}]`。
  - 修前、修後都回「第 2 筆沒帶輪次」。
  - 影響:`-std` 編號被寫進結局帳後,這個出口會判這個編號不是完整設計審。
- `_disposal_round_groups(rows)` 在 `_fix_round_rows`、`_cap_retro_template` 這些呼叫處沒先過濾。
  - 輸入:`[r1, outcome, r2]`,分組結果是 `['r1','__seq1','r2']`。
  - 影響:`_fix_item_repeat` 的「同類連兩輪」檢查,上一輪會取到 `__seq1` 而不是 `r1`,讀不到修正紀錄就靜默略過。
  - 以上只做到函式層級,端到端沒重現,所以降為 minor。
- 引句:「    for i, r in enumerate(rows, 1):\n        rid = r.get(\"round\")」。這是審材外的 `scripts/lumos`(f791d8ba)裡 `_nogo_full_review_shape`,不在修補差異內。

**驗過、沒發現問題的部分**
- 帳壞範圍:`round=5` 的壞列只擋該編號,別的編號可記,訊息帶「別的編號不受影響」。整本非 UTF-8 擋全部,訊息帶「任何編號都先不記」。
- 開頭讀一次帳:`cmd_canary` 內到最終 append 之間,沒有其他寫入 `.canary-log.jsonl` 的點,所以共用讀帳不會讀到舊資料。
- 結局帳在中間、結局帳之後再記 r2、結局帳排在第一筆:都能正常記帳。
- none 的大小寫與空白:`" NONE "`、`"\tnone"` 都當 none,`"\t"`、`" , ,\t"` 都擋為空。`"None,"` 與 `", none"` 現在被當成 none。這跟 `--folded-set` 一致,屬刻意放寬,放寬後沒讓該擋的被放行。
- `--round ""` 或純空白搭配 `--outcome`:修前被「不能混用」擋下,修後 rc0。寫進去的列和合法結局帳完全一樣,不會把審查席欄位偷渡進去,無害。
- 能抓到錯的測試:
  - `first-no-round` 的 `if rv:` 分支:拿掉後 S12 紅。
  - 整本帳壞的判定:拿掉後 S9 紅。
  - `--round` 純空白:拿掉後 S10 紅。
  - `--regression-set` 全空白(含 Tab):改回舊判法後紅。
  - 處置帳的「換新編號」文案:改掉後 S8 紅。
  - existing 清單項為 null 的型別說明:改掉後 S22 紅。
  - `--regression-set` 的 none 判法:改回舊式後 `t_canary_record_regression_set_code_only` 拋例外(被抓到)。
- 沒獨立驗:`_loop_status_disposal` 開頭的過濾。在 N3 變體下,我的場景先卡在 G3 hash,所以測試與行為都沒能區分有無過濾,結果是未判定。

**回答三問**
1. 原問題(結局帳讓帶輪次的迴圈卡死)的修復有行為證據:修前 `loop next`、`--panel`、處置閘都 rc2,修後三者都放行。但「過濾不能被拿掉」缺有效測試(finding 1)。
2. 修補處的正常、錯誤與相鄰呼叫路徑仍成立:帳壞範圍、讀一次帳共用、none 判法、空白 `--round` 都驗過。例外是 finding 3 的字面 id「none」邊界,以及 finding 4 兩個沒被這次修補涵蓋的讀側。
3. 新發現的修前、修後結果:
   - finding 3:修前 rc0 且 `regression_set=[]`,修後第一輪 rc2、第二輪靜默記成 `['none']`。
   - finding 4:修前、修後輸出相同。
   - finding 1:刪掉過濾的版本是我自己造的改壞版,只在變體上驗證,不是 f791d8ba 本身的缺陷。

臨時目錄 `/tmp/lumos-seat-work/code-記帳與迴圈工具小修/正確性-sonnet/` 我留著,收貨後請編排者刪。我自己建的 `seat-e*` 測試暫存和 `mut2_*` 變體目錄已經用字面絕對路徑刪掉。

最嚴重 severity:major;blocking 共 1 條。
