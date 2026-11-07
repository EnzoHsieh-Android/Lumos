severity: major

**第二輪 F1–F4 核對**:四條都修好了。
- F1:`Systems/規格閘.md` 舊修法已改。
- F2:首次加入日改成只留計劃和改名鏈上的舊路徑。
- F3:符號連結改在樹清單裡解析,最多跟 8 跳。
- F4:去重指紋改算 `[計劃, 出處格, 問題清單]`。

F2 的修法帶出了新問題,見下面 F1。我另外讀過 `_plan_tree_resolve`、`_plan_blob` 的行數算法、`<!-->` 與 `<!--->`、塊與行內註解的分流,沒有找到會判錯的路徑。

F1 首次加入日只留 `_計劃.md`,預期值表那條路跟著失去 git 日期
引句:「return path.endswith("_計劃.md") and "/Projects/" in "/" + path」
severity: major
blocking: 是
- 呼叫端:`scripts/lumos:14402` 的 `_expected_requirement` 也用 `_plan_effective_day`。
  - 它的輸入不限 `_計劃.md`。規格閘對任何節點跑,推送前則涵蓋 `Projects/` 底下所有 `.md`(`_spec_gate_touched_plans`、`_spec_gate_push_candidates`)。
  - 但 `_plan_first_days` 現在只留 `_計劃.md`。
- 實跑:臨時 repo 提交 `Projects/a_調研.md`、`Systems/s.md`、`Projects/b_計劃.md`,各呼叫 `_plan_first_day`。
  - 輸入→實際:`a_調研.md` 回 None、`s.md` 回 None、`b_計劃.md` 回 2026-11-07。
  - 預期:前兩個也該回 git 首次加入日,和修改前一樣。
- 後果有兩個:
  - 沒有 `created` 的舊「風險高、有新行為條款」節點,日期變 None,被當成新計劃,現在會被要求補預期值表並簽核,修改前是放行。
  - `created` 寫舊日期、但檔案是剛複製進 git 的非 `_計劃.md` 節點,以前靠 git 日期判新,現在只剩 `created`,會被判舊而放行。
- 修法:`_plan_first_days` 的過濾別寫死「計劃」。
  - 過濾放寬到 `Projects/` 底下的 `.md`。
  - 或讓 `_expected_requirement` 只處理 `_plan_sources_applies` 同範圍的檔。
  - 兩邊至少要用同一個範圍定義。
  - 目前沒有測試覆蓋非 `_計劃.md` 的首次加入日。

F2 去註解的「找閉合」會變二次方
引句:「hit = None if no_close else close_after(i)」
severity: minor
blocking: 否
- 失敗情境:同一段(中間沒有空白行、標題或圍欄)每行都有沒閉合的 `<!--`。每行的 `close_after` 都掃到段尾。
- 實跑(單一段落,每行 `x <!-- y`):2000 行 0.50 秒,6000 行 4.2 秒,約為行數的平方。
- 代價:規格閘、推送前和健檢都會呼叫它。惡意或貼壞的長計劃會讓三道閘各卡數秒。
- 更簡單的做法:每一段只算一次「段內第一個 `-->` 的位置」,所有沒閉合的 `<!--` 共用,不要每行重掃。

F3 行內註解跨過表格列,被吃掉的列不再被驗
引句:「for z in range(i + 1, q):」
severity: minor
blocking: 否
- 失敗情境:出處格寫了 `| a | b | 一般 <!-- x |`,幾列之後另一列有 `-->`。GFM 的表格列是逐行拆的,行內 HTML 不能跨列。
- 實跑:輸入 `| a | b | 一般 <!-- x |`、`| c | d | `scripts/lumos` |`、`| e | f | y --> |`,輸出中間那一列整行變空,最後一列只剩 `|`。
- 代價:被吃掉的列從檢查裡消失,爛列因此放行,好列也會被少算。機率低,所以是 minor。
- 更簡單的做法:`close_after` 遇到以 `|` 開頭的表格列就停,不跨列。

F4 行號用 `int()` 轉換,超長數字會讓閘當掉
引句:「lo, hi = int(lo), int(hi or lo)」
severity: minor
blocking: 否
- 實跑:`_plan_src_path_ok(rr, "scripts/lumos:" + "9"*5000)` 丟出 `ValueError: Exceeds the limit (4300 digits)`。
- 舊的 `_validate_repo_ref` 路徑同樣會丟,這是既有問題。
- 但這次重寫了這段,沒有順手收掉。一格出處就能讓規格閘、推送前、健檢整個崩。
- 做法:行號字串超過約 9 位就當超界回 False,或包 `except ValueError`。

F5 樹清單快取存整個 repo 所有檔案
引句:「tree[nfc(name.decode("utf-8", "replace"))] = tuple(x.decode("ascii", "replace") for x in f)」
severity: minor
blocking: 否
- 失敗情境:這是上一輪資源席 F2「快取隨歷史線性長」的同類問題,只修了首次加入日,沒修樹清單。
- 每個檔存一個字串鍵加一個三字串 tuple,快取最多 8 份。
- 我沒有量大 repo 的實際數字,是依結構推估,會隨檔案數線性增長。單人單程序影響小。
- 做法:模式和類型不必存字串,可只存 `(是否符號連結, 是否 blob, oid)`。

總結:最嚴重是 major(F1:首次加入日只留 `_計劃.md`,弄壞預期值表的新舊判斷),會擋 1 條。

臨時目錄 `/private/tmp/lumos-seat-work/code-計劃依據來源必填/通才-sonnet/t` 已刪;我沒有修改 repo。
