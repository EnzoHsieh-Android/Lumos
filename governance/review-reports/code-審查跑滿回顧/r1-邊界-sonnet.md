severity: major

席:邊界-sonnet。範圍:極端輸入(編號、--note、回顧檔、治理帳、審查帳)與圖譜鏡頭。重現都在臨時 repo 跑(沿用 test_lumos.py 的 `_cr_repo`/`_cr_loop`,環境變數 LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26),沒碰真帳。

### F1 審查帳一列含 U+2028/U+0085 就被 splitlines 劈成兩半,整列被靜默丟掉
severity: major
blocking: 是 — 新讀帳路徑(人裁輪數、新一輪判定、卷證資料夾判定)靠這支載入器,丟列會讓輪數少算,與既有讀側(逐行讀、只認換行)口徑不一致
- 輸入:審查帳某列的 `note`(或任何字串欄)含 U+2028、U+2029 或 U+0085。真寫入端 `json.dumps(rec, ensure_ascii=False)` 不會把這三個字元轉義(只轉義 U+0000–U+001F),所以它們原樣落帳。
- 走到:`_retro_canary_load` 先整本 decode,再 `text.splitlines()`。`str.splitlines` 在這三個字元也斷行,那一列變成兩段半截 JSON,`json.loads` 失敗被 `continue` 跳過,沒有任何訊息。既有讀側(`for line in f`)只在 `\n` 斷行,不會丟。
- 壞在哪:`cap-decision` 數輪數、`canary record` 判「輪次 id 在不在帳上」、`_retro_has_dossier` 判有沒有卷證,全部用這個載入器。規格〈名詞〉「帳上輪次」要與 `loop next` 同一套;這裡口徑分岔。
- 重現:帳上 crx 三輪(r1–r3,standard),把 r3 那列加 `"note": "x y"` 用 ensure_ascii=False 寫回,再 `loop cap-decision crx --decision extra-round --note 人裁決定破例再開一輪看最後修正` → rc=2,「帳上只跑了 2 輪,還沒到 standard 的上限 3 輪」(實際 3 輪)。真帳目前這三個字元零筆,所以還沒爆。
- 修法方向:改成 `text.split("\n")`(與 `_retro_gov_events` 的 `split(b"\n")` 一致)。

引句:「    for ln in text.splitlines():」
file: `scripts/lumos:12990`
file: `scripts/lumos:9681`(寫入端 ensure_ascii=False)

### F2 一份已記回顧含孤立代理字元(\ud800)就讓 retro-stats 整支炸掉
severity: major
blocking: 是 — 違反 S9「`retro-stats` 與 doctor 只標那一個迴圈、不中斷」,而且不是標一個,是全部統計都沒了
- 輸入:回顧檔 JSON 以 `\ud800` 轉義寫入 `changes[0].change`(例如 LLM 起草時把表情符號截斷成半個)。檔本身是合法 UTF-8/JSON,`--check` 與 `--record` 都過(印「已記回顧」)。
- 走到:`cmd_loop_retro_stats` 收集行動項,最後 `print(...c(a['change']))`;`_esc_clean` 不處理代理字元,stdout 編碼 utf-8 → `UnicodeEncodeError`。`--json` 路徑 `json.dumps(ensure_ascii=False)` 同樣炸。其他迴圈的統計一起消失。
- 重現(臨時 repo,crx 三輪+人裁,回顧檔用 ensure_ascii=True 寫入 change 含 `\ud800`):`loop retro crx --check` rc=0;`--record` rc=0;`loop retro-stats --repo <root>` rc=1,`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 64`(行 13587);`--json` 同樣 rc=1(行 13567)。要修只能改檔,改檔又讓回顧變「過期」。
- 修法方向:`--check` 對所有字串欄拒收代理字元,或輸出前以 `errors="replace"` 編碼。

引句:「+        print(f"  [{c(a['loop'])}] {c(a['target'])} {c(a['ref'])} — {c(a['change'])}")」
file: `scripts/lumos:13587`
file: `scripts/lumos:13567`

### F3 evidence 含 NUL 字元的絕對路徑讓 --check/--record 丟堆疊
severity: minor
blocking: 否 — 只有手寫怪檔才觸發,退出碼仍非 0、不寫帳;但違反 S9/S8 的「不丟錯誤堆疊」
- 輸入:回顧檔 `families[1].evidence = ["/abs\u0000x"]`(絕對路徑,含 NUL)。
- 走到:`_cap_retro_check` → `_retro_norm_path`:絕對路徑分支先建 tuple `(Path(os.path.normpath(s)), Path(s).resolve())`,`resolve()` 對含 NUL 的路徑丟 `ValueError: lstat: embedded null character in path`,沒有接。
- 重現:臨時 repo 記人裁後寫上述回顧檔,`loop retro crx --check` → 堆疊結尾 `ValueError: lstat: embedded null character in path`(`_retro_norm_path` 行 13060)。相對路徑含 NUL 不觸發(只走 normpath)。
- 修法方向:`_retro_norm_path` 的 resolve 包 `except (OSError, ValueError, RuntimeError)`,或 `--check` 先擋含控制字元的 evidence。

引句:「        for cand in (Path(os.path.normpath(s)), Path(s).resolve()):」
file: `scripts/lumos:13060`

### F4 「過期」「沒有」時印出的 --template 指令會把現有回顧檔清成空檔
severity: minor
blocking: 否 — 要使用者照抄那行才會發生,但這行是工具自己印在處置閘、doctor、canary 擋下訊息裡的建議
- 輸入:回顧已記後被改過(狀態「過期」),或寫好檔但還沒 `--record`(狀態「沒有」)。
- 走到:`_disposal_retro_step` 在 `none` 與 `stale` 兩種狀態都印 `lumos loop retro <編號> --template > governance/review-reports/<編號>/cap-retro.json`(`_cap_retro_template_cmd`,同樣出現在 doctor I2、canary 擋下、loop next 提示)。shell 的 `>` 在 lumos 啟動前就截斷檔案。
- 壞在哪:過期那條分支同時印「改好、--check 過了重新 --record」與這行 `>` 指令;照第二行做會抹掉剛寫好的內容。`--template` 即使回 2(沒人裁等)檔也已經被清空。規格只說「骨架印到標準輸出」,沒要求提示用覆寫導向。
- 重現:臨時 repo,記回顧後改檔使其過期,`loop status crx --disposal ...` 輸出含 `lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json`;在該目錄執行同一行 → 檔案變 0 位元組(或只剩骨架)。
- 修法方向:`stale` 狀態不印 `>` 指令;或 `none` 狀態印前先判斷檔案已存在就改提示 `--check`。

引句:「+    print(f"    {_cap_retro_template_cmd(root, loop_id)}")」
file: `scripts/lumos:13361`

## 逐條邊界輸入結論(沒問題的也列,方便對規格)
- 編號:空字串、全空白、`.`、含 `/`、`..`、控制字元都由 `_retro_id_bad` 擋回 2;超長編號在 Python 3.14 `Path.is_dir()` 不丟例外,走到「不在範圍/沒有卷證」回 2 或 0 正常。Unicode NFC/NFD 不同形的編號與帳上字串逐字比對不上,等同另一個迴圈(既有 canary/status 同樣不正規化),不構成新繞過。
- `--note`:全空白、9 字回 2、10 字過(`len(strip())>=10`),符合 S7/S10。
- 回顧檔:256KB 邊界用 `>`(剛好 256KB 收、257KB 擋);BOM 經 utf-8-sig 接受;非物件、deep 巢狀(900/990/3000 層)、`version` 是陣列、evidence 指到資料夾或帳外路徑,都判不合格不丟堆疊;`families` 空陣列、rounds 順序不同或重複、欄位型別錯都判不合格。
- 治理帳:`loop` 是數字或陣列、`rounds` 是字串、`recorded` 缺 `retro_sha256`、非 UTF-8 行、非物件列,都被跳過或判「過期」,doctor I2 與 retro-stats 正常出表(已實跑混入這些壞行)。
- 審查帳:非 UTF-8 與 `round` 非字串走 S17 的新接法;沒有人裁紀錄的迴圈不受影響。
- 效能:真帳(審查帳 3MB、治理帳 19MB)`_retro_canary_load` 0.04s、`_retro_gov_events` 0.07s。

## 圖譜鏡頭(LUMOS-IMPACT ce2a961..HEAD)
本次派工尾端沒有附固定席筆記,我自己跑了 `lumos impact --diff ce2a961fbd8706c627c2b25beeead6b7a4e2644c..HEAD`,逐條判前幾條:
- `Issues/canary-record未落盤事件`(事故):不影響。該事故的硬化是 `canary record` 寫後讀回(`_jsonl_append_verified`);新擋點在寫帳之前 `return 2`,沒有走成功路徑、不印 ✓,不會造成「回報成功而未落盤」。擋下事件用 `_gate_event_or_warn(..., hard=True)`,寫不進去只警告、仍回 2。
- `Systems/canary-audit` ★INVARIANT★「canary record 回報成功 ⟺ 該行已落盤且可讀回」:不影響,理由同上;擋下是非成功退出碼。第二條 second 純 telemetry 與本 diff 無涉。
- `Systems/design-loop` ★INVARIANT★(處置閘第五步等「七步合取」描述):處置閘多第八步。對沒有人裁紀錄的迴圈第八步印 — 回 skip,判定不變;對有人裁紀錄的迴圈是新增失敗原因,屬規格內行為。該節點與 docstring 寫「七步」,diff 已改 docstring,但節點本身不在這份 diff 裡,需確認同提交有補(我看不到)。凍結/回放四個 `_loop_status_disposal` 呼叫端中,三個帶 `retro_skip=True`,第四個(行 11581,`cmd_loop_status`)走即時問閘,與規格〈三〉2 一致。
- `Systems/loop-convergence-recording` ★RISK·守衛面★:`canary record` 多一個擋下條件;擋下路徑只在「帶 --loop 與 --round 且該迴圈有人裁紀錄」時啟動,既有迴圈行為不變。唯一例外是 F1:審查帳丟列會讓這個判定的輸入失真。
- `Systems/reversibility-governance-ledger`、`pitfalls-code-loop` 等:本 diff 不新增 ★IRREVERSIBLE★ 動作,治理帳只新增 `loop-retro` 事件(已登記 `_KNOWN_GATES`),不影響。

總結:最嚴重 major,blocking 2 條
