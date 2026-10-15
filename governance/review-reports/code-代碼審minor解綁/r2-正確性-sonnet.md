severity: minor

## F1 共用核對 `_minor_release_check` 對手改帳的集合欄型別沒有防線(閘的第二步先丟例外,不可達)
severity: minor
blocking: 否

引句:「FO, AC = set(car.get("folded_set") or []), set(car.get("accepted_set") or [])」
file: `scripts/lumos:27913`

1. 這條不是上輪已知的清單型 severity 或超長序號,是上輪修補沒碰到的相鄰角落。
2. 修補只處理了 `severity` 與 `finding_severities` 的清單值。但同一支函式對 `findings_set`、`folded_set`、`accepted_set`、`report_path` 也直接做 `set()` 或拿去當字典鍵。
3. 我直接呼叫 `_minor_release_check`,餵手改帳型態。結果都丟例外:
   - `findings_set=5`、`folded_set=5`、`accepted_set=5`:TypeError。
   - 這三個欄位的元素是清單:TypeError unhashable。
   - `report_path=["x"]`:TypeError unhashable。
4. 實際路徑上它們不可達,所以降為 minor:
   - 寫側的 `_ids()` 只產出字串清單。
   - 處置閘第二步在 `scripts/lumos:28245` 附近先做 `set(carrier.get("findings_set") or [])`,同樣型別會先丟例外,到不了第九步。
5. 也就是說,第九步在函式層面沒有真正達到「型別壞掉判不過、不噴例外」。目前只靠上游先崩。這是原有漏查,不是修補回歸。
6. 歸因:有證據的原有漏查。修前修後我的直接呼叫都丟例外,修補沒改這幾行。查證用在 repo 載入 `scripts/lumos` 後直接呼叫共用核對,兩版同結果。
7. 原有的上游崩潰是否算範圍外(單人、AI 依序操作的威脅模型),我未判定。

## 三問與逐案結果

- ① 原問題的修復效果:
  - 序號超長數字:`len(no) > 9` 先比長度,`"9"*5000` 現在判 fail。
  - 序號剛好多一條:`#3`(報告只有 2 條)判 fail。
  - 逐條等級是清單:判 ok,不噴例外。
  - 席位等級是清單:判 ok,不噴例外。
  - 修前我沒有逐案跑,這些修前結果未判定(沒切回舊提交重跑),只憑程式差異判斷舊版會丟例外。
  - 修後行為證據:三個相關測試 `t_disposal_code_minor_release`、`t_canary_record_finding_source`、`t_report_normalize_items` 在修後全綠(86、34、9 項)。
  - 抓錯力:新測試涵蓋 `isinstance(mine, str)` 拿掉(清單進 `in _SEV_ORDER` 會 TypeError)、`len(no) > 9` 拿掉(`int()` 超長會 ValueError)、`#3` 的 off-by-one,這三種改壞都會翻紅。我只靠讀程式與測試輸入推得,沒有逐一實測翻紅。
- ② 修補處的相鄰路徑:
  - `_mr_applicable` 改成清單後,`"blocker" in sevs`、`"major" not in sevs` 與處置閘第二步的 `r.get("severity") in ("major","blocker")` 判法一致,沒有寫側與閘不一致。
  - 範本輸出改成 `_drift_sh(path_)` 加 `#序號`。我實跑 `report-normalize --items` 驗過路徑含空白、`#`、`$` 時輸出 `'a b/r#1.md'#1`,殼層會合併成單一參數,`rpartition("#")` 讀回正確。
  - 拿掉 `cmd_report_normalize` 開頭的 `paths = [paths] if isinstance(...)`:argparse 是 `nargs="+"`,永遠是清單。程式與測試裡沒有其他呼叫者傳字串,安全。
  - 測試裡把 `hash(tag)` 改成 `enumerate` 序號當 loop id:去掉了 `PYTHONHASHSEED` 造成的不穩定,更好。
- ③ F1 同一案例的修前修後:兩版都丟例外。修補沒改到那幾行,未造成回歸。
- repair 逐案:超長序號、剛好多一條、逐條等級是清單、席位等級是清單,修後都符合預期(見①)。修前結果未判定。
- preserve 逐案:合法流程(S1 折入與放行各指其原報)、序號邊界 `#1`、`#2`,以及 `+1`、`01`、全形數字、`0` 仍被擋,修後三個測試全綠,行為保持。
- 繞過檢查:我沒找到讓原報 major 被放行或不被交代的新路徑。`"major" in sevs` 改用清單比對後,不會因為席位等級型別怪異而少算 major 席。若怪異型別使它被誤判成非 major 席,寫側與閘兩邊判定一致,都落回「major 一律折」的舊判斷。
- 新舊互讀:沒有 `finding_sources` 的舊帳仍在 `_mr_applicable` 回 skip,與修補無關。
- 圖譜鏡頭:
  - 新增的 PITFALL 行格式齊全(出處、根因、修法、test),所綁測試存在。
  - `loop-convergence-recording`:修補不改它宣稱的合約,不影響。
  - `design-loop` 的 INVARIANT(第五步 .md 計劃與條款綁測試):修補只動 `_mr_*` 與範本輸出,不影響。
  - `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle` 的 INVARIANT:改動不碰 search、guard kill、re-inject,不影響。
- 未驗範圍:沒有切回舊提交逐案重跑;沒有實測各項測試守衛的翻紅;沒有端到端用手改帳打過閘。

最高 severity: minor,blocking 條數 0。
