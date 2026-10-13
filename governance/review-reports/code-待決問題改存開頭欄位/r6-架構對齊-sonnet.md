severity: minor

**1. 分層與依賴方向:大致一致,有兩處小不齊**

符號連結檢查放在 `atomic_write_verify` 這個共用寫入原語裡,層次是對的。所有走這支原語的開頭欄位寫入共用同一道守衛,跟同函式下一行的拿鎖檢查同層、同樣丟 `RuntimeError`。

`cmd_summary_line` 自己接錯誤,不算跨層。同檔 `cmd_*` 函式自己接 `(ValueError, RuntimeError)` 的有二十多處,例如 `scripts/lumos:15573`、`16095`、`17229`、`20161`、`20260`。但緊鄰的分派段做法不同。`updated-sync`、`set/append/remove`、`new`、`loop escape` 都是在 `main()` 裡接,見 `scripts/lumos:52981`、`52996`、`53008`、`52910`。同一段分派裡,`summary-line` 就在 `updated-sync` 正上方,卻是唯一不在分派段接的。程式碼註解「接在這裡不加 main() 的分支」說明了理由,所以結構可接受。

`_guard_dispatch` 的新 docstring 另有一句「其他子指令群…照舊留在 main() 裡內聯」。這句跟同一個 patch 把 summary-line 的接法放進指令函式,說法不一致。

severity: minor
blocking: 否
引句:「    try:   # 拿鎖逾時、寫入原語丟的錯轉成擋下訊息、rc2,不印堆疊(代碼審 待決問題改存開頭欄位 r5 合約席);接在這裡不加 main() 的分支」
對照處 file: `scripts/lumos:52981`(`updated-sync` 在分派段接)、`scripts/lumos:52996`(`set/append/remove` 在分派段接)。⚠ 這個函式內外兩種做法並存,所以我判得不準。

severity: minor
blocking: 否
引句:「    if os.path.islink(path):」
對照處 file: `scripts/lumos:9831`(`log.is_symlink()`)、`scripts/lumos:26396`(`p.is_symlink()`)、`scripts/lumos:23677`(`dst.is_symlink()`)。全檔判符號連結都用 `Path.is_symlink()`,`os.path.islink` 只有這一處。`atomic_write_verify` 的 `path` 本來就是 `Path`,所以這是命名上的小不齊,功能沒差。

**2. 命名與錯誤處理:大致一致**

- `_PQ_INVISIBLE` 的命名跟同區 `_PQ_CF_OK`、`_PQ_KEYS` 一致。位置在 `_PQ_SUB_RE` 後面、所有函式之前,符合「常數放函式前」。
- `_pq_is_vs` 命名同 `_pq_is_tag`,放的位置也同它。它定義在使用它的 `_pq_bad_char` 之後,跟 `_pq_is_tag` 一樣,這是這區既有的排法。
- 符號連結擋下丟的 `RuntimeError`,跟旁邊拿鎖失敗的 `RuntimeError` 同型。`_esc_clean(os.readlink(path), 160)` 的第二個位置參數用法,跟 `scripts/lumos:1893` 的 `_esc_clean(raw, 120)` 一致。
- 推送前提醒新增 `shown = _esc_clean(rel)`,跟全檔印路徑一律過 `_esc_clean` 的做法一致。

severity: minor
blocking: 否
引句:「_PQ_FLAG_TAG_RE = re.compile("[\U000E0061-\U000E007A]{2}[\U000E0061-\U000E007A\U000E0030-\U000E0039]{1,3}\U000E007F")」
對照處 file: `scripts/lumos:6916`(`_PQ_CF_OK` 與 `_PQ_INVISIBLE` 放在常數區)、`scripts/lumos:6953`(這條常數夾在 `_pq_is_vs` 與 `_pq_flag_run_ok` 兩個函式之間)。上一輪被點名的「常數放在函式後」,這輪只搬了 `_PQ_CF_OK`。新加的 `_PQ_FLAG_TAG_RE` 又放在函式之間,是同一個毛病的重現。

**3. 第二種做法:沒有,上輪點名的三項已收掉兩項,第三項沒收乾淨**

- 專案裡「看不見字元」的現成共用判斷只有兩個。一個是 `_PATH_SPECIAL_CATS`,`_pq_bad_char` 本來就在用。另一個是 `_strip_zero_width`(`scripts/lumos:4994`),它是搜尋正規化用的剝除,範圍 U+200B–200F 與 FEFF。
- 全檔找不到點字空白 U+2800、韓文填充字 U+3164/115F/1160/FFA0、U+034F、異體選擇符 U+FE00–FE0F 與 E0100–E01EF 的既有判斷,所以 `_PQ_INVISIBLE` 與 `_pq_is_vs` 沒有重造輪子。
- `_PQ_INVISIBLE` 加上 `_pq_blank` 的 `isspace` 判斷是這個欄位專用的「空值」定義,沒別處可共用。
- 上輪三項的狀況如下:
  - 守衛分派搬出沒寫理由:已補理由,見 `_guard_dispatch` docstring。
  - docstring 舊名:已收,全檔搜不到 `_pq_cf_ok`。
  - 常數放在函式後:`_PQ_CF_OK` 已搬到常數區,但新增的 `_PQ_FLAG_TAG_RE` 又犯,見第 2 問。

不對齊共 3 條,其中 major 0 條
