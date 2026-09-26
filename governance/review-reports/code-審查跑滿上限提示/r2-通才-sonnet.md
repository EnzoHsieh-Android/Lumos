severity: blocker

## F1 patch 對照現在的 main 是舊底稿,套上去會在 scripts/lumos 灌進一整段(約264行)重複的既有函式
severity: blocker
blocking: yes
引句:「_SEV_ORDER = {"clean": 0, "minor": 1, "major": 2, "blocker": 3}」

用乾淨的 `git clone /Users/enzo/harness/lumos-toolchain`(HEAD=7cc2b9da,跟 repo 現況一致)套這份 r2-snapshot.patch(`git apply`,不需要 --3way、也沒有衝突),套完之後 `grep -n "^def _review_yield_round\|^def _report_severities\|^def cmd_report_normalize\|^def _intake_declared\|^def normalize_report_text\|^def _report_findings_missing_severity\|^def _report_reported_count" scripts/lumos`,這七支函式全部變成兩份定義(例如 `_review_yield_round` 在 7366 跟 7630 各一份,`_report_severities` 在 7177 跟 7441 各一份),`_SEV_ORDER`/`_SEV_WRITESIDE_CUTOFF`/`_REPLAY_ENGINE_REV` 這三個常數甚至出現三次(7126、7390、7676)。

逐行比對兩份函式本體(`sed -n '7137,7400p'` vs `sed -n '7401,7653p'`),內容逐字相同(只差多印出一次的那三個常數)。原因是:main 目前已經有 `審查有沒有用記帳`(commit fee29590/9d89d085)這支功能,`_intake_declared`/`_report_severities`/`normalize_report_text`/`cmd_report_normalize`/`_report_reported_count`/`_review_yield_round` 這些函式早就在 repo 裡;但這份凍結 patch 的 diff hunk(`@@ -7387,6 +7387,270 @@`)是拿一份「還沒有審查有沒有用記帳」的舊底稿去對比出來的,套到現在的 main 上,context 行(`_review_yield_round` 結尾那行 `return {...}`)還是能唯一匹配到,於是把整段舊底稿當「新增」再貼一次。

Python 允許同名函式重複定義(後面那份蓋掉前面那份),所以現在測試都還會綠——這也是這份審查的測試子集(`python3 scripts/test_lumos.py -k cap_hint`,34 條全過)照樣過關、不會自己翻紅的原因;但這不代表這份 patch 可以直接拿去用。如果照這份 patch 去 commit,scripts/lumos 會多出一大段死掉的重複程式碼(264+ 行),往後有人改 `_report_severities` 之類的函式,很可能只改到前面那份沒作用的舊拷貝,改了等於沒改——這是真的會咬人的坑,不是無害的多餘字。

要處理:重新對現在的 main(或這輪真正要合併進去的那個 commit)重新產生這份 delta patch,不要用舊底稿去 diff;套上去之後要用上面那條 grep 指令確認每支函式只剩一份再放行。

## F2 test_lumos.py 裡新測試的裝飾器被複製貼上了兩次(功能上無害,但是抄寫留下的破綻)
severity: minor
blocking: no
引句:「@_cap_real_cutoff」

同一份 patch 裡,`t_disposal_cap_hint_fail_open` 前面疊了兩層 `@_cap_real_cutoff`(patch 第 363–365 行:第 363 行是既有的裝飾器、364 行又加了一個一模一樣的、365 行才是 `def t_disposal_cap_hint_fail_open():`)。套用後在 scripts/test_lumos.py 可以看到:

```
@_cap_real_cutoff
@_cap_real_cutoff
def t_disposal_cap_hint_fail_open():
```

`_cap_real_cutoff` 這支裝飾器只是把環境變數設成同一個值再還原,疊兩層在邏輯上互不衝突(外層存、內層存同一個值、內層還原、外層還原,結果一致),實測跑這支測試沒有任何異常,所以不算功能 bug,但明顯是複製貼上留下的贅字,跟 F1 同一個病灶(這份 patch 的內容有被重複貼過的痕跡),一併清掉。

## 已驗過、沒問題的部分

- **`_cap_hint_print` 的吞例外範圍夠不夠**:實際突變測試——把 `_cap_hint_print` 改回沒有 try/except 的版本,`t_disposal_cap_hint_fail_open` 立刻真的翻紅(丟出 `TypeError: object of type 'int' has no len()`,來自 `_review_yield_round` 裡 `len(carrier["refuted_set"])`),證明這條防呆真的在擋這個洞,不是心理安慰。範圍上,`_cap_hint_print` 把 `_cap_hint(...)` 的計算跟 `_cap_hint_lines(...)` 的組字串、連同 `print` 都包進同一個 try,夠。

- **loop next 那邊會不會崩**:loop next(`scripts/lumos` 10951–10954 行附近,這段不在本輪 patch 的改動範圍內,是既有程式)已經自己把 `_cap_hint(rows)` 包在 try/except 裡、失敗就把 `_ch` 設成 `None`;後面 `_cap_hint_lines(_ch)` 沒有另外包 try,但因為 `_cap_hint_lines(None)` 開頭就 `if not h: return []`,而 `_cap_hint` 只有在成功組出合法 dict 時才會走到 `_cap_hint_lines`,所以這條路徑本來就不會拿到「算一半壞掉」的 h,不會崩。這個既有防呆跟本輪處置閘那邊新加的 `_cap_hint_print` 是兩套獨立防呆,職責分開,沒有互相依賴造成的破洞。

- **段首標籤改法(只在第一行印 `[cap-hint] `、其餘行縮排兩格)有沒有外部依賴**:全 repo 只找到兩處會檢查 `[cap-hint]` 字樣的地方,都是 `"[cap-hint]" in stdout` 這種存在性檢查(scripts/test_lumos.py 33179/33184/33206/33223 行),沒有任何地方要求「每一行都要以 `[cap-hint]` 開頭」。突變測試把 `P` 改回 `"[cap-hint] "`(所有行都帶標籤)重跑 `t_loop_next_cap_hint_appended_without_changing_phase`,真的翻紅,證明新加的「段首一行帶標籤、之後都是縮排」這條斷言是有效釘住這個格式的,不是擺著好看。順帶一提:設計筆記 `審查跑滿上限提示_計劃` 第三節「文字」那句「段落每行開頭 `[cap-hint]`」還是舊寫法沒跟著更新——但那是代碼審輪次(跟設計迴圈的 r1/r2/r3 編號不同層)產生的格式修正,不影響這次程式對不對,只是設計筆記本身現在跟實作的印字格式對不上,算文件債,不升等成 blocker。

- **提示行一律印之後會不會在沒到上限、沒熔斷時也印出來**:不會。`_cap_hint()` 本體在 `at_cap` 跟 `breaker` 都不成立時直接 `return None`(7717–7718 行),`_cap_hint_lines(None)` 一開頭就短路回空清單,根本不會走到組「提示:」那一行的邏輯。也就是說「一律印」只在 `_cap_hint_lines` 拿到非 None 的 h 才生效,而拿到非 None 的前提本來就是已經到上限或已經熔斷——沒到門檻的情況這段輸出完全不會出現。突變測試把這行改回 `if h["at_cap"] or h["hint"] != "unknown": lines.append(...)` 的舊條件,`t_cap_hint_breaker_total_folded` 裡「只有一輪的熔斷」那條斷言(要求文字同時有「判不了」跟「拆小」)真的翻紅,證明這條修正是有效的,對應的是 r1 抓到的「熔斷觸發但判不了時提示行被吞」。

- **`_disposal_round_groups` 有沒有被搬動時順便改到內容**:對照 patch,這支函式在 diff 裡整段是「未變更的上下文行」(沒有 +/- 前綴),表示這份 delta 裡它其實沒有真的被搬過位置或改過內容(它本來就已經緊接在新插入的大段程式碼後面)。跟本輪審查任務描述裡「分輪函式 `_disposal_round_groups` 搬到處置閘步驟函式家族旁」這句對不上——但這不影響程式對錯,只是這份 patch 沒有反映那個折入項目(有可能那項在更早的提交就做掉了),不另開新 finding。

- **測試子集本身**:`python3 scripts/test_lumos.py -k cap_hint` 在套上這份 patch 的 clone 裡跑,34 條全過(含新加的 S2 fail-open 測試跟 S1 標籤格式測試);另外跑了 `-k disposal_round_groups`(0 命中,函式沒有獨立命名測試)跟 `-k loop_status_disposal`(13 條全過),確認處置閘既有的行為沒被這輪改動波及。

共 2 條(F1 blocker、F2 minor)。
