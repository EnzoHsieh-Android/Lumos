severity: major

三問都有對照，全文如下。

## ① 模組邊界（盲判記帳、核對、統計、讀表各落在哪）

大方向落對地方：
- 記帳走 `_codeloop_gov_append` 和 `_codeloop_write_marker`，兩支都是從表態那組抽出來共用的。
- 核對放在 `_kt_sit_verdict_one`，跟既有的 `_kt_sit_check` 同一層。
- 統計放在 `_render_gov_stats` 裡，用 `rows` 逐筆掃，跟同檔表態閘那段的作法一致。
- 讀表借 `_kt_pack_check()` 去載 check.py，沒有在 scripts/lumos 另開一套。

引句:「ok, why = _codeloop_gov_append(repo_root, ev)」
對照:`scripts/lumos:71574`（`_codeloop_gov_append`）。`scripts/lumos:73660` 附近的 `_cmd_codeloop_dispositions` 也是先寫治理帳、再寫標記檔，順序一致。

**F1**
severity: major
blocking: 是
引句:「def _kt_bj_range(repo_root, diff_range, at_sha, branch):」
- 這支把 `code-loop check` 算「表態適用題範圍」的那段內嵌邏輯整段抄了一份：`_mainline_ref`、`git merge-base`、`merge-base..版本`。原版在 `scripts/lumos:73025-73040`，是 `_codeloop_guard_verdict` 裡的內嵌段，沒有抽成函式。
- 兩邊的退路不同：check 在推主線或算不出來時退回「推送範圍」，盲判退到 `_codeloop_default_base`（`scripts/lumos:72805`）。
- 段身分綁的是範圍切出來的 hunk 內容。兩邊範圍一旦對不上，盲判寫進去的段身分在 check 端就核不到，會報「缺第一盲判」。
- 這是同一條規則兩份實作。應該先把那段內嵌邏輯抽成共用函式，check 和盲判一起呼叫。

**F2** ⚠ 判不準，交編排者
severity: minor
blocking: 否
引句:「bj, notes = _kt_bj_check(segs, ent, _kt_bj_read(repo_root, branch), waived=waived, branch=branch)」
- 表態紀錄是走 `_disp_record_for`（`scripts/lumos:72036`），目標分支沒有時會認「合進來那一側」（`merge_side`）。
- 盲判紀錄只讀 `marker_branch` 名下的標記檔或治理帳，沒走這條。
- 合併提交若靠 merge_side 取得表態，盲判那邊可能整批算「缺第一盲判」。
- 我只看了程式路徑，沒實跑合併提交，所以標 ⚠。

**F3**
severity: minor
blocking: 否
引句:「repo_root = Path(repo) if repo else next((c for c in (Path.cwd(), *Path.cwd().parents) if (c / ".git").exists()), None)」
- 其他 code-loop 子指令都走 `cmd_code_loop`（`scripts/lumos:73623`）統一解析 repo 根、分支、版本，`security_only` 則用 `_secinv_repo_root`（`scripts/lumos:73290`）。
- 新入口 `cmd_codeloop_blind_judge` 自己手寫找 repo 根的迴圈。`--at-sha` 的 `rev-parse` 也抄了一份 `scripts/lumos:73660` 附近 dispositions 那段。
- 結構是對的，只是又多一份重複。

## ② 命名與錯誤處理

大致一致：
- 事件 kind `blind-judge` 搭配欄位 `blind_judge`，跟 `recall-miss` 搭配 `recall_miss` 同形。
- 擋下訊息都以「擋下:」開頭、回 rc 2，成功訊息以「✅ code-loop …」開頭。
- 標記檔沒寫成時，只提醒、不當失敗，跟 `_cmd_codeloop_dispositions` 一致。
- `("code-loop", "blind-judge")` 登進 `LOOP_NOT_CLOSE_EVENTS`，`HELP_WHEN` 也補了。
- `--branch`、`--at-sha`、`--diff` 的旗標和 dest 都沿用既有名稱。

引句:「print(f"擋下:盲判結果檔讀不了或不是合法 JSON({e.__class__.__name__}:{str(e)[:120]})", file=sys.stderr)」
對照:`scripts/lumos:73535`（dispositions 的「擋下:要給表態檔路徑…」）。

**F4**
severity: minor
blocking: 否
引句:「"sit_waive": (d.get("origin") or "human") if (d.get("kind"), d.get("scope")) == ("waived", "kt-situation") else None,」
- `scripts/lumos:17473-17475` 的註解規定「新增 mapper 用到的欄位時一起補進來」。
- 這次只補了 `blind_judge`，`_gov_row` 新讀的 `role`、`seg`、`row`、`keys` 都沒進 `_GOV_FIELD_TYPES`。
- 帳上若有型別錯的 `seg`（例如清單），`_gov_situation_collect` 裡的 `list(dict.fromkeys(warns))` 會因為不可雜湊而炸掉整個 gov。這正是那張表要擋的事。

## ③ 第二種做法（標記檔、治理帳重建、去重、統計、讀表）

標記檔和從治理帳重建這兩項有重用既有函式：
- 標記檔寫入用 `_codeloop_write_marker`。
- 治理帳重建用 `_codeloop_ledger_events`（`scripts/lumos:69937`），每格取第一筆。
- 去重 token 把 `blind-judge` 併進既有的 `written_at` 那一支，沒有另開。

引句:「for ev in _codeloop_ledger_events(text, (_KT_BJ_KIND,)):」

統計、去重、讀表有重複：

**F5**
severity: minor
blocking: 否
引句:「p3 = str(k).split("|")」
- 「段|列|種類」這個 keys 編碼，現在寫入端 1 處、讀取端 2 處：`_kt_sit_reminder_log` 的去重（`scripts/lumos:72140` 起）和 `_gov_situation_collect`。兩處讀取是逐字相同的拆解，沒有共用 helper。
- `_gov_situation_collect` 的「每格取最早一筆」（`tgt.setdefault((seg, rid), …)`）也是 `_kt_bj_cells_add` 規則的第二份寫法。
- 同檔其他統計段本來就各自掃 `rows`，這點不算違規，所以只列 minor。

**F6** ⚠ 判不準，交編排者
severity: minor
blocking: 否
引句:「def dt_sources(text):」
- check.py 的 `dt_table`（`configs/ast-grep/kotlin-android/check.py:197`）docstring 寫著「原本兩邊各寫一套、必有欄數已經分歧」，宗旨是讀表只有一套。
- `dt_sources` 有重用 `_cells`、`_dt_header`、`_MAIN_ROW_RE`，但另外走了一輪決策表列、另解析一次〈來源縮寫〉表。`catalog_problems`（`check.py:315-322`）已經解析過一次，縮寫比對的正規式現在重複了三處。
- 其實只要讓 `dt_row` 多帶「來源」欄，就不用另走一輪。
- scripts/lumos 側的 `_KT_DT_SOURCES = []` 用模組級清單當快取，跟 `_KT_DT_ROWS, _KT_DT_ERR = _kt_decision_table()` 的載入慣例不同。`_kt_pack_check` 的 `required` 也沒補 `dt_sources`，改用 `getattr` 退路。
- 結構上有重用 helper，所以給 minor。

不對齊共 6 條，其中會擋的 1 條。
