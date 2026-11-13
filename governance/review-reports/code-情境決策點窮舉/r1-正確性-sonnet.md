severity: major

我審了整份 diff,也在 `/tmp` 下的乾淨 clone 上對 check.py 逐道做改壞實驗(實驗完已刪)。

真型錄現況沒問題:`check.py --catalog-only` 回 0 個問題,`check.py --sg` 完整模式回 0 個問題,五支測試加 S7 段全綠。

主要問題在測試:不少驗收條款字面寫了「應報」,但把對應程式改壞,測試照樣綠。另外有一個小的程式缺陷(`_bad_lines`)。

## Findings

### F1 範本改由整條路沒有任何測試走過
引句:「return [] if _parts_in_order(env["lumos"], snip, body) else [f"片段不在範本 {group} 的「### 壞寫法:{cid}」小節程式裡"]」

file: `configs/ast-grep/kotlin-android/check.py:1207`(`_template_route_problems`)

- 真型錄的範本改由是 0 筆(統計行「範本 0」)。
- `t_kt_catalog_bad_snippets_reach_rows` 只走到「單一識別字」那個分支,以及對 `_fence_body` 的單元斷言。
- 下面三種改壞,測試都是 22 passed, 0 failed:
  - 拿掉 `behavior_value(...) != f"範本 {group}"` 那道。
  - 拿掉 `if not body:` 那道。
  - 把 `_parts_in_order(...)` 判斷改成 `True`。
- 條款 S2 明寫「範本 T1 只有 API-10 沒有 API-1 應報」和「片段不在壞寫法小節程式圍欄裡 應報」。目前只有 `_fence_body` 這個小函式被驗,「報不報」那層沒驗。
- 重現(clone 內改檔後執行):`python3.14 scripts/test_lumos.py -k t_kt_catalog_bad_snippets_reach_rows`,輸出 `22 passed, 0 failed`。

severity: major
blocking: 是

### F2 `規則` 改由的起訖行上界沒有被測試守住
引句:「if isinstance(idx, dict) and not any(a <= no <= b for f, no in hits for a, b in idx.get((rule_id, f), ())):」

file: `configs/ast-grep/kotlin-android/check.py:1202`

- 測試的 `idx2` 只給了 `(5, 9)`,下界就沒涵蓋 BAD 行 2。
- 具體輸入:ast-grep 報的節點是 `[1,1]`,BAD 行是 2。
- 預期要報「起訖行沒有涵蓋」。
- 把 `<= b` 拿掉後 `a <= no` 為真,不報,測試仍是 22 passed。
- 這正是 S7 預期值表那一列的情境:`kt-nested-collect` 報了內層,片段在外層那一行。

severity: major
blocking: 是

### F3 完整模式(`--sg`)的 scan_index 接線沒有負向測試
引句:「scan_index = SCAN_FAILED if ranged is None else {}」

file: `configs/ast-grep/kotlin-android/check.py:1542`,以及 `scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples` S7 段。

- 條款 S7 要求「把片段在壞例樣本改成規則不報的寫法 應報問題」。
- S7 段只斷言真樣本沒有反查問題。
- 把 `check()` 裡傳給 `bad_snippet_reach_problems` 的 `scan_index=scan_index` 改成 `scan_index=None`(等於整個起訖行驗證關掉),`t_kotlin_rulepack_samples` 帶 `LUMOS_AST_GREP` 跑,結果 28 passed, 0 failed。
- 把 `scan_ranges` 的結束行改成起始行,結果也是 28 passed。
- 靜態函式有用合成的 `idx` 測過,但 `check()` 裡「建索引、正規化路徑 key、傳進去」這段膠水,沒有任何一個會翻紅的測試。

severity: major
blocking: 是

### F4 「同一名稱兩列應報」(S1)沒有測試
引句:「out.append((name, "〈API 決策點〉同一個名稱出現兩列"))」

file: `configs/ast-grep/kotlin-android/check.py:987`

- 把 `if name in seen:` 改成 `if False:`,`t_kt_catalog_api_decision_points` 仍是 28 passed。
- 測試裡有「多一個母體沒有的名稱」和「拿掉一列」,沒有複製一列的案例。
- 具體輸入:型錄把 `flatMapLatest` 寫兩列。

severity: major
blocking: 是

### F5 `…` 切段「依序」沒有負向測試
引句:「pos = m.end()」

file: `configs/ast-grep/kotlin-android/check.py:1098`(`_parts_in_order`)

- 條款字面是「兩段依序出現」。
- 改成 `pos = 0`(順序不計),或只比第一段,測試都照綠(28 和 22 passed)。
- 測試只有正向的 `OkHttpClient.Builder()…build()` 對 `OkHttpClient.Builder().build()`。
- 具體輸入:片段 `build()…OkHttpClient`,對壞例行 `OkHttpClient.Builder().build()`,應判不依序。
- 我在真 check.py 上直接呼叫,`_parts_in_order(lm, "a…b", "b a")` 正確回 False,所以程式本身是對的,缺的是測試。

severity: major
blocking: 是

### F6 `\|` 還原沒有測試
引句:「return [s.replace("\\|", "|") for s in re.findall(r"`([^`]+)`", cell)]」

file: `configs/ast-grep/kotlin-android/check.py:927`

- 條款 S2 寫「片段含表格跳脫的 `\|` 應還原後再比」。
- 把 `.replace("\\|", "|")` 拿掉,兩支測試都綠。
- 真型錄裡可能沒有含 `|` 的片段,所以真資料也抓不到。

severity: major
blocking: 是

### F7 `_bad_lines` 的「下一行」分支用 `split("//")` 截斷,字串裡的 URL 會被砍掉
引句:「out.append((str(f.resolve()), nxt + 1, _norm_code(lines[nxt].split("//")[0])))」

file: `configs/ast-grep/kotlin-android/check.py:1118`

- 輸入:壞例樣本是 `// BAD: note` 加下一行 `val u = "http://a/b".foo()`。
- 實測 `_bad_lines` 回的比對用文字是 `val u = "http:`。
- 字串沒閉合,`_norm_code` 清不掉,片段 `"http://a/b".foo()` 正規化成 `"".foo()` 後比不到。
- 結果是「片段不在 samples/bad/<id>/ 標了 // BAD 的行上」的誤報。
- 同行標法(`ln[:i]`)沒這問題。
- 這是大聲誤報,不會靜默放過,所以只算 minor。

severity: minor
blocking: 否

### F8 守衛分支缺紅測(合併一條)
引句:「if r is None or r.get("dir") != "rules" or not r["message"].startswith(f"[{cid}]"):」

file: `configs/ast-grep/kotlin-android/check.py:1194`

下面幾處改壞,測試都綠:
- `dir != "rules"` 拿掉。
- 訊息開頭 `[cid]` 那道拿掉。
- `_API_ITEM` 的「D-n 是停用列」(`check.py:972`)拿掉。
- `_norm_code` 的字串清空拿掉。
- `_parts_in_order` 的整字邊界改成子字串。

這些守的是設計規則,不是驗收條款字面,所以是覆蓋不夠完整,算 minor。

severity: minor
blocking: 否

## 其餘逐項判定
- 切段路徑篩選抽成 `_kt_sit_path_ok`(`scripts/lumos`):
  - 兩處呼叫的參數、語意和原內聯式一致,`skip` 傳法也一樣,沒有行為改變。
  - S6 測試是三個輸入對三個預期,加原始碼字串計數。
  - 計數偏脆,但判準獨立。
- 統計行(S8):`_KT_STATS_LINES` 的數字是手寫的獨立判準,不是從程式算出來的,這條合格。
- 新舊互讀:
  - 新程式讀沒有新兩節的舊型錄,會報「找不到〈…〉節」,這是預期行為。
  - 舊程式讀新型錄的情況,我沒驗。
- 資源與例外:
  - 沒有開子程序或檔案而沒釋放的路徑。
  - `scan_ranges` 的 `TimeoutExpired` 和 `OSError` 都接了,且回 None 時 `scan_index` 設成 `SCAN_FAILED`(測試有覆蓋)。
- 角色卡 be-api-compat、be-authz:這次沒有端點或對外 API 欄位,不適用。
- 固定席筆記:派工詞說鏡頭計算超時、沒附節點,所以沒有節點可逐條判。

## 總結
總結:最嚴重:major;阻擋共 6 條(F1 到 F6),minor 2 條(F7、F8)。

相關檔案:
- `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`
- `/Users/enzo/harness/lumos-d4-triggers/scripts/lumos`
- `/Users/enzo/harness/lumos-d4-triggers/scripts/test_lumos.py`
