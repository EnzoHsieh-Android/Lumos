severity: minor

## F1 report-normalize --items 另用一套方式找 repo 根,和帳本落路徑的根來源不同
severity: minor
blocking: 否
引句:「root = _cochange_repo_root(None)」
file: `scripts/lumos:11309`(`_ledger_rel_path`,落帳的根由呼叫端傳入)
file: `scripts/lumos:11630`(`--finding-source` 寫側用 `_vault_repo_root(env)` 當根)
file: `scripts/lumos:48982`(`cmd_refcheck`,同為不碰圖譜的指令,有 `--repo` 選項)
1. `_report_items` 的註解說「路徑用 canary record 落帳那一套」。路徑函式確實共用 `_ledger_rel_path`,但根的來源不同。
2. 寫側的根是從 vault 往上找 `.git`(`_vault_repo_root`)。`--items` 的根是從 cwd 往上找 `.git`(`_cochange_repo_root(None)`),而且沒有 `--repo` 可指定。
3. 兩個根在 vault 與 cwd 都在同一個 repo 時相同。cwd 在 repo 子目錄或另一個 repo 時,印出的範本路徑會和落帳路徑不同。
4. 結構上沒有自寫新函式,所以不判 major。`_cochange_repo_root` 是 cochange 功能的函式,被審查工具借用,是不同模組互叫。
5. ⚠ 這是否要對齊 `cmd_refcheck` 的 `--repo`,或改用 vault 找根,交編排者判。

## F2 範本列自己拼了一套「要不要加引號」的判斷
severity: minor
blocking: 否
引句:「t if _drift_sh(t.rpartition('#')[0]) == t.rpartition('#')[0] else _sh_quote(t)」
file: `scripts/lumos:42638`(`_drift_sh`,印給人貼的參數直接過它)
file: `scripts/lumos:40329`、`scripts/lumos:28362`(鄰居都是 `_drift_sh(x)` 一次包好)
1. 這裡拿 `_drift_sh` 的輸出和輸入比對,來判斷路徑部分要不要引號。要引號時再對整串呼叫 `_sh_quote`。
2. 原因是 `#` 不在 `_drift_sh` 的白名單裡,整串丟進去一定被包引號。
3. 底層仍是既有函式,但包法是這一處獨有。之後有人改 `_drift_sh` 的白名單,這個比對式可能悄悄失效。
4. 鄰居沒有這種「以是否等於自己判斷」的寫法。

## F3 cmd_report_normalize 的參數形狀和同層鄰居不同
severity: minor
blocking: 否
引句:「paths = [paths] if isinstance(paths, (str, Path)) else list(paths)」
file: `scripts/lumos:48982`(`cmd_refcheck(md_path, …)` 同層唯讀指令,只收單一路徑)
1. 同層的 vault-free 指令(`fold-check`、`prose-lint`、`quote-check`、`refcheck`)都只吃一個 `path`。
2. 這支改成可收單一值或清單,再加一道 `isinstance` 轉型。argparse 的 dest 仍叫 `path`,但實際值已是 list。
3. 多份報告的唯讀序號清單,同時掛在名為「normalize」的指令下,靠 `--items` 與 `--write` 互斥的兩條 rc 2 訊息撐住。
4. 錯誤處理是 rc 2 加 stderr「擋下:…」,和鄰居一致。

## F4 新增的代碼審判別不走 _roster_kind,和同層處置閘各步驟不同
severity: minor
blocking: 否
引句:「if not str(loop_id).startswith("code-"):」
引句:「if not str(loop or "").startswith("code-"):」
file: `scripts/lumos:27741`(`_disposal_security_step` 一族的 `_gated_seats_for`:`_roster_kind(loop_id or "")`)
file: `scripts/lumos:28068`、`scripts/lumos:28125`(`_disposal_clause_step`、`_disposal_landing_step`:`_roster_kind(loop_id or "") == "code"`)
file: `scripts/lumos:11847`(`cmd_canary` 的註解寫「判法走全檔唯一那支 _roster_kind」)
1. 處置閘獨立步驟判代碼審都走 `_roster_kind`。它把「code 開頭但沒連字號」判成 None,各步驟依此從嚴處理。
2. 新增的 `_mr_applicable` 和 `cmd_canary` 的 `--finding-source` 檢查都直接用 `startswith("code-")`。
3. 同一個 diff 裡 `_loop_status_disposal` 改的那條分支(原本就是 `startswith("code-")`)也是這個寫法。所以不是只有新碼不一致,但新增的 `_disposal_minor_release_step` 及其共用核對是鄰居步驟的同層。
4. 行為差異:`codeX` 這類編號在這一步一律算「不適用」。鄰居步驟遇到這種編號會從嚴處理。

## 三問逐問回答

1. 分層與依賴方向:基本一致。
   - 步驟函式 `_disposal_minor_release_step(rows, carrier, loop_id, prov_path)` 放在處置閘各步驟之間,簽章和 `_disposal_security_step(rounds, rid, loop_id, prov_path)`(`scripts/lumos:27790`)同形。它在 `_loop_status_disposal` 的第九步被呼叫(印 `[disposal] …`、回 "fail"/"ok"/"skip"、加進 `fails`、納入橫幅 `_extra`),與第五到第八步相同。
   - 讀留痕走既有 `_prov_read`(`scripts/lumos:27714`),路徑接根走既有 `_under_root`(`scripts/lumos:9405`)。寫側傳 `lambda v: _under_root(_vault_repo_root(env), v)`,與處置閘的 `_prov_path` 對稱,沒有跨層直呼。
   - 寫側和閘端呼叫同一支 `_minor_release_check`,讀報告也共用 `_report_reader`。這比鄰居更集中,沒有出現兩套。
   - 只有 F1 的 repo 根來源是借用 cochange 的函式。

2. 命名與錯誤處理:大致一致,不一致處見 F3、F4。
   - 寫側錯誤是 rc 2 加 stderr「擋下:…」,和 `--finding-severity`、`--refute-verdict` 一致。訊息帶現象與接下來怎麼做。
   - 閘端輸出用 `[disposal] 逐條放行: ✗ — …`,再接「在意的原因:」「接下來:」兩行,與資安席那一步同形。skip 的 `—(…)` 寫法也與條款綁定等步驟一致。
   - 新私有函式用 `_mr_*`、`_finding_sources_typed`、`_ledger_rel_path`,符合檔內底線前綴慣例。
   - 顯示路徑與使用者字串都走 `_esc_clean`,與逃逸帳的用法一致。

3. 第二種做法:沒有 major 等級的第二套。
   - 路徑正規化:原本散在 spec、report、snapshot、intake 四處的 `relative_to(_vault_repo_root(env))` 被收成 `_ledger_rel_path`,舊的四處也一併換掉,減少而非新增一套。
   - 讀檔與驗 sha:共用 `_prov_read`。severity 解析:`_report_severity_lines` 與 `_report_severities` 同源,沒有分叉。
   - 消毒與引號:用 `_esc_clean`、`_drift_sh`、`_sh_quote`,只有 F2 的組合式是這處獨有。
   - 測試端:新輔助 `_mr_project` 等(`scripts/test_lumos.py`)沿用 `_stats_fixture`、`run`、`check`、`_sha256_of`。造帳結構與 `_qfs_project`(`scripts/test_lumos.py:30355`)同形,沒有引入新的建帳方式。

## 圖譜鏡頭判定

- 本次沒有棧別檢核題的表態,沒查張力四欄。
- 圖譜固定席節點裡有 `Systems/design-loop.md` 的 `★INVARIANT★`:處置閘第五步,設計審必須是 .md 並做條款綁定。diff 沒有動第五步,只在第二步的「major 一律折」分支加了一個例外條件,也沒改判別函式。這一點沒有結構或做法上的不對齊。

不對齊共 4 條,其中 major 0 條。
