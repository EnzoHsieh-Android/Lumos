severity: major

說明:鎖檔 `…2127b4fa.json.warming` 不存在(`cat` 回 No such file),沒有鎖要處理。固定席筆記沒有附上(LUMOS-LENS 寫「沒附固定席節點」)。我沒有執行 `lumos impact`。

驗證方式:在臨時目錄各 `git clone --shared` 一份,修前 `4b056532664f7d6d8c2ad000ee0f925159057c21`、修後 `7988107c0c903087fda5af18d5efd6a34d4e96c1`,檢出後用 `git log -1` 確認版本。再用 `importlib` 載入各自的 `scripts/lumos`,直接呼叫函式。臨時目錄已刪。

## F1 路徑規則合併後,功能的 paths 寫 `./.` 或 `././` 又收得進來了
severity: major
blocking: 是
file: `scripts/lumos`(修後版)的 `_e2e_relpath_err`,由 `_e2e_feature_head_err` 呼叫。

失敗場景:
- 修前,`_e2e_feature_head_err` 自己檢查 `_e2e_norm(x) in ("", ".")`,所以 `./.` 會被擋。
- 修後這段改成呼叫 `_e2e_relpath_err`。它的「專案根本身」檢查用的是 `q = p.strip().rstrip("/")`,沒有先經過 `_e2e_norm` 去掉開頭的 `./`。
- `./.` 的 `q` 還是 `./.`,不在 `("", ".")` 裡。`_e2e_norm("./.")` 變成 `.`,`normpath(".")` 也是 `.`,正規寫法檢查通過。
- 結果是 paths 寫 `./.` 的功能設定檢查回 0。`--changed` 用 `_e2e_under(f, ".")` 比對,而 `_e2e_under` 要求 `startswith(".")` 加 `/`,任何改動檔都對不到。這個功能永遠不會被挑中,也沒有任何提示。
- `app_dirs`、`exclude`、`flows` 與 `apk` 也走這支函式,`./.` 照樣收下。這些欄位修前就收,屬原有漏查。
- 現有測試只涵蓋 `"."`(測試改成要求出現「根本身」),沒有 `./.`。

重現(兩版同一命令):
```
m._e2e_feature_head_err("f", {"paths":["./."], "cases":{"a":{}}}, re.compile(r"[A-Za-z0-9_-]+"))
```
- 修前:回「features.f.paths 的 './.' 要寫成正規的相對路徑…」,被擋。
- 修後:回 `None`,收下。
- `_e2e_relpath_err("./.","w")` 與 `("././","w")` 兩版都回 `None`。

歸因:有證據的修復回歸。僅限 features.paths(修前會擋、修後不擋)。`app_dirs`、`flows` 等欄位是有證據的原有漏查。

引句:「    if posixpath.normpath(_e2e_norm(p)) != _e2e_norm(p) or any(c in q for c in "*?["):」

建議修法:根本身檢查改用 `_e2e_norm(p)` 判斷,例如 `_e2e_norm(p) in ("", ".")`。

## F2 `run-id` 擋 `history.jsonl` 只比對完整小寫,在 macOS 預設的不分大小寫檔案系統上擋不住 `History.jsonl`
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `preflight`。

失敗場景:
- 在這台 macOS 上驗證過:先 `mkdir History.jsonl`,再對 `history.jsonl` 做 `touch`,只是更新了目錄的時間。
- 用修後版 `_local_ledger_append(Path("cs/history.jsonl"), …)` 回 `False`,目錄 `History.jsonl` 仍在。
- 所以 `run-id` 傳 `History.jsonl` 會通過檢查(`rid == "history.jsonl"` 為 False,也符合後面的字元規則),run 目錄佔住總表檔名,這次的檢測總表紀錄寫不進去。
- 後果只是總表少一行並印出提醒,判定本身不受影響,所以降為 minor。
- 新測試只試了小寫 `history.jsonl`。

歸因:有證據的原有漏查。修前完全沒檢查;修後只擋了完全相同的小寫寫法,沒補大小寫。
- 修前:`run-id` 傳 `history.jsonl` 或 `History.jsonl` 都通過。
- 修後:`history.jsonl` 被擋,`History.jsonl` 仍通過。

引句:「    if run_id == "history.jsonl":   # 本機總表 .lumos/artifacts/android/history.jsonl 跟 run 目錄在同一層」

## 三問
1. **原問題的修復效果:**
   - 路徑規則合併:`app/./`、`./app/.`、`app/.`、`a[1]` 在修前回 `None`、修後被擋,同一函式同一輸入前後對照過。
   - 反斜線、萬用字元兩類我只在修後看到被擋,修前版的這支函式沒有這兩條檢查,所以前後有差,但我沒另外跑命令。
   - 以下幾項我只讀了程式,沒跑修前版,都標未判定:
     - 逾時 `break`:`run()` 在逾時或啟動失敗時回 `None`,`step` 原樣回傳。我讀了 `_e2e_stab_by_name` 與 `_e2e_judge_stability`:沒跑到的情境因缺 `stability_judge` 步驟而判「沒判完」,`macrobench` 逾時只寫提醒,邏輯一致。
     - `collector_override` 後移:僅在 `stab_to_run` 非空且有替身時設定,沒有讀到會讓它漏掉的路徑。
     - 紀錄檔捷徑檢查:`_local_ledger_append` 對總表另有檢查,但紀錄目錄那條是新加的,我沒造捷徑重跑。
     - `mode` 預設改成 `partial`。
2. **修補處的正常、錯誤與相鄰呼叫路徑:**
   - 「`mode` 預設 `partial`」只改了 `steps.json` 讀不懂的那一支。
   - 新增的「沒帶 `--no-record` 被拒也記總表」只在 `serr is None and "selection" in steps` 時走到。
   - 新增 `open(` 的 diff 行沒有;`run()` 裡原有的 `fo`/`fe` 兩個 `open` 不在這次 diff,不評。
   - F1 是相鄰路徑出狀況的例子:`_e2e_feature_head_err` 改叫共用函式後,原先只在 features 上的 `.` 檢查沒搬過去。
3. **新發現的同一案例修前修後:** F1 與 F2 都已列在各自條目。F1 修前被擋、修後放行;F2 修前後都有缺口,只是修後多擋了一個寫法。

## 其餘角度的逐行結果
- **被刪除的行為:** 只有 F1 對應的 features 專屬檢查被刪。`_e2e_now` 不用了的 `collector_override` 搬位置後仍有等價守衛。
- **跨檔追蹤:** `judge` 的 `--no-record` 與 `--history`,以及 `steps.json` 的 `selection` 和 `dirty`,範本腳本與 `lumos` 兩邊欄位對得上。
- **重用:** 紀錄寫入的 `OSError` 回傳形狀沿用 `(None, 錯誤訊息)`,呼叫端已會處理。
- **其他角度(簡化、效率、修的深度、慣例):** 沒有能講出具體失敗情境的候選。

## pitfalls manifest 判定
唯一內建題(`open(` handle)判為誤報。這次 diff 新增的行裡沒有裸 `open(`,範本腳本的 `Steps.save` 用 `with open`。`run()` 裡原有的 `fo = open(...)` 後接 `fe = open(...)`,第二個失敗時第一個會洩漏,但那行不在這次改動內,也不是修補造成。

## 圖譜鏡頭
這次沒附固定席筆記,我也沒另外查圖譜,所以不逐條判。可確認的一點:新增的 `_e2e_relpath_err` 說明裡寫「app_dirs、exclude、flows、apk 與功能對照表的 paths 共用這一支」,而 F1 正好顯示合併時漏了 `.` 的檢查,圖譜若有路徑規則的紀錄,應在補洞後一併更新。

**總結:** 修補大致守住了原問題,但路徑規則合併讓功能 paths 寫 `./.` 變成能通過檢查,卻永遠挑不到功能(F1,修前會擋);run-id 的 `history.jsonl` 檢查在不分大小寫的檔案系統上仍有縫(F2)。
