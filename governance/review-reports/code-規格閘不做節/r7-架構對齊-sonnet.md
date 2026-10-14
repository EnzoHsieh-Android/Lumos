severity: minor

最高等級 minor,沒有引入第二種做法,也沒有跨層直呼。重點是這份 diff 把 r6 的架構意見(讀帳核心、「限 repo 內」路徑解析、快照讀取)併回了既有函式,方向對。我看到的是幾處旗標累積和收斂不完全。

我用 `git log` 確認過,對照用的 spec-gate-nondo 工作樹是 `48bf9109`,本次改動的 scripts/lumos 已在其中。

**finding 1:`_canary_ledger_scan` 加 `spec_gate=True` 與 `fields=`**
severity: minor
blocking: 否 — 這是把 r6 重複的讀帳函式併回既有核心,並沒有新增一套讀法;代價是一支函式帶兩種模式,現有三個呼叫端都不傳旗標,行為沒變。
引句:「spec_gate=True(規格閘這一族,代碼審 code-規格閘不做節 r6 架1):保留 kind=spec-gate 留痕、編號 NFC 後當鍵、跳過帶輪次的列」
對照:file: `scripts/lumos:13776`(`_loop_records` 一類的既有呼叫端,預設模式不傳旗標);file: `scripts/lumos:13727`(核心本身)
判定理由:
- 一個布林旗標同時切換五件事:是否保留 spec-gate 留痕、編號是否 NFC、是否跳過帶輪次的列、壞 UTF-8 是否替換後照讀、逐行解碼。
- 另一個 `fields=` 只在這個模式下被傳入。
- `spec_gate=True` 時第三個回傳值恆為 None,第二個(壞輪次說明)恆為空,因為帶輪次的列已先被跳過,簽名的語意在兩種模式下不一致。
- 合併比再寫第二份讀帳好,所以不列 major。
- 之後若再有第三種讀法,建議改成「核心只負責逐行解析並丟出列,模式差異放在呼叫端的過濾器」。

**finding 2:`_under_root` 說是共用,其實只收了三處**
severity: minor
blocking: 否 — 新 helper 的行為跟原本三份逐字相同,沒有新增做法;只是收斂不完整。
引句:「return q if q.is_absolute() or root is None else Path(root) / q」
對照:file: `scripts/lumos:49797`(`sp = Path(spec_path) if Path(spec_path).is_absolute() or root is None else root / spec_path`,同一個寫法還留著一份);file: `scripts/lumos:10930`(`_vault_repo_root`,根的來源,diff 照用)
判定理由:
- 名字叫「under_root」,但絕對路徑原樣放行,並不限制在 repo 內。
- 專案裡沒有現成的「限 repo 內」檢查可對照,`_repo_walk_lstat` 在此分支也不存在,所以沒有跨層或第二種限制做法。
- 剩下的 49797 那份可併入,或在 docstring 註明故意不限制。

**finding 3:`_NOGO_ROWS_V` 是第三套版本號,沒有守衛**
severity: minor
blocking: 否 — 目前只有一次演進(1 到 2),沒有漏升的實害;問題是之後改演算法時沒有機械提醒。
引句:「被略過那一行的雜湊算法版本(規格閘留痕的 nogo_rows_v)」
對照:file: `scripts/test_lumos.py:60395`(`_NOGO_SKIP_LOGIC_PIN` 把判斷邏輯的函式原始碼雜湊跟版本號一起釘住);file: `scripts/lumos:7910`(`_DOOR_RULE_VERSION` 加輸入指紋)
判定理由:
- 專案既有做法是「改了邏輯,測試釘值變紅,逼你升版」。
- `_nogo_line_key` 的算法不在 `_NOGO_SKIP_LOGIC_FUNCS` 裡,`_NOGO_ROWS_V` 也不進 `_door_rule_fingerprint`,日後有人再改正規化卻忘了升版,不會有測試變紅。
- 跟現有版本號分開本身合理,因為一個管門規則、一個管留痕雜湊算法。
- 建議把 `_nogo_line_key` 加進釘住清單,或加一支只釘它的測試。

**finding 4:`_prov_read` 自己算 sha256,沒用 `_sha256_file`**
severity: minor
blocking: 否 — 為了拿到位元組而多讀一次是合理理由;不是新做法,只是 hashing 又寫了一遍。
引句:「raw = Path(prov_path(pth)).read_bytes()」
對照:file: `scripts/lumos:10924`(`_sha256_file`:`hashlib.sha256(Path(path).read_bytes()).hexdigest()`)
判定理由:
- `_prov_check` 改成包 `_prov_read` 的拆法很乾淨,沒有第二份判斷邏輯。
- 小重複是 `hashlib.sha256(raw).hexdigest()` 這一行。
- 可讓 `_sha256_file` 接受已讀的位元組,或加一支 `_sha256_bytes`,不是必改。

**finding 5:`_light_gate_fails(..., ratchet=False)` 讓共用謂詞可以略過自己的 ratchet**
severity: minor
blocking: 否 — 只有一個呼叫端傳 False,而且該呼叫端接了 `verdict != "judged"` 的後備;`loop status --light` 預設 True,行為不變。
引句:「verdict, fails = _light_gate_fails(window, env.vault / prel, cur_sha_override=last.get("result_sha256"), ratchet=False)」
對照:file: `scripts/lumos:13480`(`loop status --light` 的既有呼叫,預設 ratchet)
判定理由:
- 這支謂詞的核心就是「曾經 major 就永久失效」,現在可以用旗標關掉。
- 替代做法是 `_nogo_light_window` 先把 major 列剔除再呼叫,謂詞就不必長出旗標。
- 目前用法有文件、有後備,主要是以後別的呼叫端誤傳的風險。

**已查、沒有問題的項目:**
- **`_nogo_line_key`**:專案裡沒有現成的「只留字母數字」正規化 helper,所以不是第二種做法。同檔 `scripts/lumos:16330` 的 `re.sub` 去空白是套套邏輯警告用的,語意不同。
- **門規則版本與指紋升級**:`_DOOR_RULE_VERSION` 從 4 升到 5,`scan_fenced` 換成 `scan_raw` 並進指紋,照既有「改了就 +1、`t_door_rule_version_pin` 釘住」的流程。附帶一個不算架構的小事:`_spec_gate_push_stale` 的「較舊版本」提示文字還只舉「版本 4 起程式碼圍欄」,沒提版本 5。
- **入口清 git 環境那段**:四個分支逐字同一段是既定裁定,不列。
- **跨層**:`_door_keyword_hits` 改成逐行讀原文,沒有繞過別的層。`_visible_lines` 和 `_strip_inline_markup` 仍是其他路徑(條款、已排除行、不做清單)的唯一實作。

最高等級 minor,blocking 0 條。
