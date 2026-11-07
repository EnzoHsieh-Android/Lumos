severity: minor

先核對 r1 的三條要求。F1(首次加入日只留一套算法)、F2(健檢截斷照統一慣例)、F3(是不是新計劃只留一份判法)都照方向修了,主體不再有第二種做法。剩下三條小的重複寫法。

- **F1 已修。** `_plan_first_day` 與 `_plan_effective_day` 現在都改查同一份 `_plan_first_days`(`scripts/lumos:14318`、`scripts/lumos:14324`)。批次那支 `_plan_first_days_batch` 已刪。新算法不限 pathspec,從 Projects 外搬進來的檔也接得上。表預期值那邊 `scripts/lumos:14373` 沒傳 `firsts`,自動走同一份快取。`_plan_first_commit`(`scripts/lumos:14241`)留著,它回的是提交編號,不是日期,用途不同。
- **F2 已修。** `warn_soft` 的 `cap` 參數拿掉,回到只用 `_SOFT_CAP = 3` 加 `--verbose`(`scripts/lumos:2082`、`scripts/lumos:2086`)。`_DOCTOR_PLAN_SOURCES_CAP` 也刪了。
- **F3 已修。** 規格閘、推送前、健檢都只走 `_plan_sources_is_new`(`scripts/lumos:14684`)。健檢那份手抄的新舊判斷已刪。

**① 模組邊界**
- 沒有跨層直呼。新程式碼都放在原來的函式群裡:首次加入日放在 `_plan_first_day` 旁,出處判法放在 `_plan_source_cell_ok` 旁,健檢只叫 `_plan_sources_is_new`。
- 出處存在判斷交給既有的 `_validate_repo_ref`(`scripts/lumos:37743`,帶 `at_sha="HEAD"`),沒有自寫第二套。
- 治理帳事件仍走 `_gate_event`(`scripts/lumos:1799`)。去重只在它前面加了一層,沒有繞過去。

引句:「_plan_first_day 與 _plan_effective_day 現在都改查同一份」不是 patch 內容,不採用。改引:
引句:「days = _plan_first_days(rr)」

**② 命名與錯誤處理**
- `_PLAN_FIRST_DAYS_CACHE` 加上 `_MAX` 滿了丟最早的,與 `_KT_BUILD_VERDICT_CACHE` 同寫法(`scripts/lumos:38517`、`scripts/lumos:38528`),記憶體有界。
- 生效日覆寫提示用「程序內只講一次」的集合,與 `_BT_PARALLEL_WARNED`(`scripts/lumos:70505`)同形。
- 健檢例外改成印軟提醒、不再印綠勾,錯誤處理一致。
- 命名沿用 `_plan_*` 前綴,沒有不一致。
- ⚠ 派工詞和 r1 收貨紀錄都引用 `_kt_sit_reminder_log` 當去重先例。我在 `scripts` 底下搜不到這個名字。patch 實際寫的先例是 `_ci_write`(`scripts/lumos:63923`)。請編排者確認收貨紀錄的先例名稱有沒有寫錯。

引句:「warn_soft([_esc_clean(f"{_e22.__class__.__name__}: {_e22}", _DOCTOR_LINE_MAX)],」

**③ 第二種做法**
- 收斂的部分:首次加入日只剩一套算法。「是不是新計劃」只剩一份判法。健檢截斷回到共用慣例。
- 還有三處是新增的重複寫法,結構上沒有跨層,但專案裡原本沒有。

F1
severity: minor
blocking: 否
`_plan_sources_uncomment`(`scripts/lumos:14599`)是專案裡第三種去 HTML 註解的寫法。
- 其一是建置檔的 `_XML_COMMENT_RE`(`scripts/lumos:38508`)。
- 其二是 `_fence_regions` 刻意不偵測註解(`scripts/lumos:5412`)。
- 新的一支要保留行數、避開圍欄與行內程式碼,理由成立,docstring 也寫明不動 `_visible_lines`。
- 問題在沒有留下「為何不共用」的回頭條件,日後兩套可能分岔。
引句:「def _plan_sources_uncomment(text):」

F2
severity: minor
blocking: 否
`_plan_sources_block_event`(`scripts/lumos:14706`)自己手寫一輪「讀整本治理帳、逐行 json 解析、比對指紋」。
- 形狀照抄 `_ci_write`(`scripts/lumos:63923`),但 `_ci_write` 的去重鍵交給 `_jsonl_append_verified` 一起處理。
- 這裡是掃帳之後再呼叫 `_gate_event`。專案現有的帳去重沒有統一成一支共用函式,所以不算引入第二種機制。
- 小問題:去重只掃 `GOV_LOG_NAME` 那本帳。`_gate_event` 會依 `_gov_routes_local` 改寫本機帳。目前 `sources-missing` 是 `hard=True`,應該不走本機帳,但沒有程式保證。
引句:「path = _docs_ledger_path(Path(rr) / "docs", GOV_LOG_NAME)」

F3
severity: minor
blocking: 否
首次加入日有兩層記憶。
- 第一層是程序級快取 `_PLAN_FIRST_DAYS_CACHE`,鍵含 HEAD。
- 第二層是 `_plan_first_days_once` 傳回的取值函式。它的用意是省掉每篇一次的 `git rev-parse`(快取鍵要先問 HEAD)。
- `_plan_effective_day` 因此多一個「可傳函式」的參數,形狀與專案其他快取呼叫端不同。
- 目的成立。但兩層都在管「只跑一次」,日後改快取鍵時容易只動一層。
引句:「def _plan_first_days_once(rr):」

不對齊共 3 條,其中會擋的 0 條
