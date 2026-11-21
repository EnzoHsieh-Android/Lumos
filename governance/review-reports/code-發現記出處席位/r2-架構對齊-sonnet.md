severity: major

**1. 分層與依賴方向**

新碼的位置和呼叫方向跟鄰居一致,沒有跨層直呼。
- 寫側檢查仍放在 `cmd_canary` 讀帳之後,由 `_finding_seat_write_block` / `_finding_seat_required_block` 呼叫,依賴方向沒變。對照:`cmd_canary` 的 `--refuted-set` 檢查,`scripts/lumos:19851`。
- 統計側的 `_seat_noise_*` 仍掛在 `_render_gov_stats`,沒有往下呼叫寫側。
- 本輪新增的 `--loop` 前置檢查放在 `cmd_canary` 的處置集合區,跟 `--finding-kind` 的檢查同層。
- `_loop_next_hints` 多加的提示用 `kind != "design"` 判斷,跟同函式既有的 `kind` 判斷一致:`scripts/lumos:24909`。

這一問沒有發現。

**2. 命名與錯誤處理**

- 擋下訊息用「擋下:…」加 rc 2,跟鄰居一致。對照:`scripts/lumos:19860`。
- 擋下時留 canary blocked 事件、事件字串含 `loop=… auditor=… id=<uuid8>`,格式也跟鄰居一致。對照:`scripts/lumos:19851`、`scripts/lumos:20177`。
- 測試輔助 `_fs_since` 對照 `_ksp_since`(`scripts/test_lumos.py:133486`),結構一樣。
- 測試輔助 `_fs_blocked_n` 改成只讀 `docs/.governance-log.jsonl`,跟既有測試寫法一致。對照:`scripts/test_lumos.py:4585`、`scripts/test_lumos.py:5059`。
- 測試總檔預設值改成 `"9999-12-31"`(純日期),跟其他 `_SINCE` 的預設值寫法一致。

不一致的只有一處。環境變數覆寫收「純日期」,內部卻把日期接上 `T00:00:00+08:00` 再用 `_loop_ts_key` 比。
- 專案裡有兩種既有生效日做法,各自一致。
  - 第一種是日期常數加環境變數覆寫,日期字串直接比,不合 `_DAY_RE` 就退回常數。對照:`_expected_since`,`scripts/lumos:14516`;`_choice_since`,`scripts/lumos:77948`。
  - 第二種是帶時區時間常數、不給環境變數覆寫、用 `_loop_ts_key` 比。對照:`scripts/lumos:15770`、`scripts/lumos:13876`、`scripts/lumos:23832`。
- 這個專案的做法是把兩種接起來:時間常數加覆寫,覆寫收純日期並自己補 `+08:00`。這是第三種混合寫法,但結構上只是組合既有零件,所以只算 minor。
- 計劃與筆記寫「跟其他 `*_SINCE` 一樣」,只對了一半。
- 判不準是否該升成 major,標 ⚠ 交編排者。

severity: minor
blocking: 否
引句:「    v = os.environ.get("LUMOS_FINDING_SEAT_SINCE", "").strip()」
file: `scripts/lumos:19569`

**3. 第二種做法**

severity: major
blocking: 是
新增了 `_finding_seat_event`,把「擋下時寫治理帳事件」包成專屬函式。
- 鄰居全部是在擋下處直接呼叫 `_gate_event_or_warn(_vault_repo_root(env), "canary", "blocked", f"... loop={loop or ''} auditor={auditor or ''} id={uuid.uuid4().hex[:8]}", hard=True)`。這是派工詞點名的「新的事件包裝函式而鄰居直接呼叫」。
- 對照:`scripts/lumos:19851`(refuted-set-missing)、`scripts/lumos:20091`(report-not-normalized)、`scripts/lumos:20101`、`scripts/lumos:20186`。
- 鄰居要組複雜事件字串時,用的是只回傳字串的 `_quote_block_note`,呼叫仍在擋下處直接寫(`scripts/lumos:20126`)。新包裝連 `_gate_event_or_warn(... hard=True)` 本身都包進去,事件包裝專案原本沒有。

引句:「def _finding_seat_event(root, why, loop, auditor):」
file: `scripts/lumos:19576`

severity: major
blocking: 是
事件字串的清洗用了自己寫的 `_one`(`re.sub(r"\s+", " ", …)`),專案已有同功能的共用清洗,這是第二種做法。
- 對照:`_esc_clean`,`scripts/lumos:21616`,專門清 C0/DEL/C1、ESC 序列、雙向控制字元、孤立代理字元;`_out_clean`,`scripts/lumos:21632`,用於擋下訊息與外來文字。
- `\s+` 不含 ESC、C1、雙向覆寫,清得比既有函式少。計劃要擋的「迴圈名帶控制字元」,新寫法反而擋不全,所以不只是不一致,也不是「同一規則」。
- 鄰居事件(`scripts/lumos:19851`、`scripts/lumos:20091`)連清洗都沒做,新碼自己造了一條。要嘛跟鄰居一樣不清,要嘛改用 `_esc_clean`。

引句:「        return re.sub(r"\s+", " ", str(x or "")).strip()」
file: `scripts/lumos:19577`

其餘新增的做法在專案裡都有對應或沒有第二種:
- 席名去輪次記號的 `_seat_noise_name` 與 `_SEAT_SPLIT_RE`,專案裡沒有同功能函式(`scripts/lumos` 裡 seat/auditor 命名的函式都是別的用途)。
- 擋下訊息用 `repr` 印席名,是本模組內部的處理,沒有跟鄰居衝突。
- 覆寫時印「提醒:環境變數 …」到 stderr,專案裡沒有鄰居可對照,不算第二種做法。

不對齊共 3 條,其中 major 2 條
