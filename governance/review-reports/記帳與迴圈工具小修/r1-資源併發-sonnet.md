severity: major

**資源併發鏡頭審查報告(記帳與迴圈工具小修 r1)**

先說結論。這份設計在大輸入、記憶體、子程序、時間預算上沒有問題,我實測過。真正的洞在 §1 對「讀帳」的描述跟程式結構不符,照字面實作會漏擋最主要的情境。

**實測(工作樹 web-ledger,2026-10-15)**
- 審查帳 `docs/.canary-log.jsonl` 有 4787 列、4.9 MB。`_canary_ledger_scan` 整本掃一次要 0.056 秒,行程峰值記憶體約 52 MB。
- `canary record` 現在就至少讀三次帳:載體最後記、定錨檢查,以及 T6 段的整檔 `read_text`。再多一次也在雜訊內。
- 派工單最大的一份是 56 KB。§7 只在 `scope_oversize` 時才讀它,大小不是問題。
- `pitfalls --json` 不動,pre-push 熱路徑(0.23 秒)不受影響。pre-push 裡人可讀的 pitfalls 輸出只經 `sed` 顯示,多印一行不會被解析。
- 本案沒有新增子程序、迴圈或遞迴。新判法 `_loop_round_format` 是對單一編號列表掃一次,O(該編號列數)。
- `loop next --json` 多一個 `hints` 鍵:`scripts/hooks`、`scripts/templates`、`.github` 都沒有解析它的消費者,測試裡也沒有釘住鍵集合。

---

**F1**
severity: major
blocking: 是(照字面實作會讓 [S5]、[S7]、[S9] 要擋的主情境根本不進檢查)

- **§1「`canary record` 寫側」**:spec 說新檢查「放在載體最後記那段讀帳之後,跟它共用同一次 `_loop_records_checked` 讀帳,不多讀一次」。
- **程式現況**:`file: `scripts/lumos:11847`` 那段的條件是 `if loop and round_id and outcome is None:`。也就是說,「沒帶 `--round`」的那筆根本不會進這段,也不會做那次讀帳。
- **具體例**:
  1. 輸入:迴圈 `code-x` 既有列都帶 `--round`,這筆 `canary record --loop code-x --tier standard`(沒帶 `--round`)。
  2. 預期([S5]):rc2。
  3. 照 spec 把新檢查塞在該段裡面:`round_id` 是 None,整段跳過,不擋,寫進一筆混用的帳。
  4. 第一筆零帳的情況([S7]、[S9])同理,`round_id` 也是 None。
- **要補的規格**:新檢查必須自己的條件(`loop and outcome is None`)獨立成段。「共用同一次讀帳」得改成「讀帳提到兩段共用的位置,條件放寬為 `loop and outcome is None`」,否則實作者會照字面把它塞進 `round_id` 的條件裡。
- **帳壞的行為沒寫**:`_loop_records_checked` 在帳壞時回 `_lerr`(讀不到、不是 UTF-8、該編號有一列輪次不是字串)。載體最後記對 `_lerr` 的處理是只在帶 `--finding-source` 時才擋。新規則在 `_lerr` 時要放行還是擋,spec 沒說。放行就是 fail-open,而且這份設計明說沒有跳過旗標,所以要寫死。
- **成本結論**:效能上沒差,見上面實測。
- 引句:「帳上零筆(這是第一筆)時」

**F2**
severity: minor
blocking: 否(只會讓 §7 的核對在真實帳上漏擋或偶爾誤擋,不會做出壞系統)

- **§7 派工單位置與材料比對**:spec 只讀固定名稱的 `<輪>-dispatch.json`。
- **真實帳的形狀**(`governance/review-reports` 下全數掃過):
  - 829 份是 `rN-dispatch.json`,但另有約 70 份每席各一檔,例如 `rN-dispatch-s1.json`。既有讀法 `_fix_dispatch_base` 和 `_roster_dispatch_entries` 都 glob `rN-dispatch*.json`。拆包審用每席一檔時,本節的核對全部跳過,F28 的坑原樣還在。
  - 有一份 `seats` 是字典、不是清單(`code-test-quality-native-push/r3-dispatch.json`)。spec 只說「讀不懂就跳過」,沒說 `seats` 非清單的處理。
  - 材料路徑的基準不統一。465 筆超標帳列中,245 筆「有同名席、有材料、snapshot 不在材料裡」,其中 242 筆確實是整份對分包,擋得對。但有 3 筆材料寫成相對派工單所在目錄的裸檔名(例如 `r1-slice-code.patch`,而 snapshot 是 `governance/review-reports/code-java補棧/r1-slice-code.patch`),照「正規化後路徑」比對會誤擋。
- **誤擋怎麼出來**:設計沒有跳過旗標,誤擋沒有出路,只能 cd 到 repo 根或改派工單。
- **要補的規格**:
  - glob `<輪>-dispatch*.json`。
  - 材料路徑先試 repo 根、再試派工單所在目錄。
  - 比不上路徑才算 sha256,且只在材料檔存在時算,避免對每筆材料都全檔雜湊。
- 引句:「照手冊的固定位置;沒帶輪次或檔不在就跳過」

**F3**
severity: minor
blocking: 否(影響很窄,而且訊息只是不準)

- **§1 `_loop_round_format` 與結局帳**:spec 說判法的排除條件跟 `loop next` 現行 `n_round` 一樣。現行 `n_round` 數的是 `"round" in r`,結局帳列(沒有 `round` 鍵,真帳 13 筆)也被算進去。
- **具體例**:
  1. 某迴圈每筆都帶輪次,另外記過一筆結局帳。
  2. 之後再記一筆帶 `--round` 的帳,既有列加上這筆,`_loop_round_format` 回 `mixed`。
  3. 寫側 rc2,訊息卻講「既有都帶輪次」,實際是被結局帳那一列害的。
- **不算矛盾但要明寫**:§〈不做〉承認 `loop next` 會把這種帳判混用,但沒講寫側遇到「既有列已含結局帳」時的行為。要嘛判法排除 `outcome` 列,要嘛寫明這種情況維持擋並說明原因。
- 引句:「結局帳寫進帶輪次的迴圈後」

**F4**
severity: minor
blocking: 否(會在 pre-push 全套才發現,可回頭修)

- **〈實作時要跑的子集〉最後一段**:「既有測試裡用 `canary record` 寫 code- 標準級、沒 `--round` 的第一筆,會被新規則擋;實作時逐支看」。但 `-k` 只比對測試函式名,而且全套約 8 分鐘,不能在對話裡跑。
- **規模**:`test_lumos.py` 有 2363 個測試,提到 `tier.*standard` 的地方有 155 處。會被新規則打到的測試散在 `loop_next`、`disposal`、`cap_hint`、`retro`、`fix_check` 等各種函式名底下。
- **要補的規格**:加一條可機械列舉的做法,例如 grep 出所有呼叫 `canary record` 且帶 `--tier standard` 或 `high` 卻沒 `--round` 的測試,否則實作者只能等全套紅。
- 引句:「實作時逐支看:測的是循序舊帳的改用直接寫帳的測試輔助函式」

---

**已讀,無 finding**
- §2 `none` 當空集合:`_ids` 逐筆處理,無效能面。
- §3、§4、§5、§6:只是一次判斷、一行輸出或一次 `_TIER_ROSTER` 讀取。§5 的 stderr 提醒發生在已寫帳之後,不改回傳碼,也不增加 I/O。
- §8、§9:`hints` 是純字串組裝。
- 〈實務隱患〉的「效能」一條:「寫側只多用既有那一次讀帳」這句要連同 F1 修正,其餘成立。拆包核對只在超標時讀派工單,已用真帳驗證(最大 56 KB)。
- 威脅模型:單人、依序操作,併發寫帳不報。

最嚴重 severity:major;blocking 共 1 條(F1)。
