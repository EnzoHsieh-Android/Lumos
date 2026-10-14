severity: major

## 逐項結論

**`_disposal_judge`**:見 finding 2。
**讀帳函式的分工**:已讀,無 finding。
**`_nogo_seat_ok`**:見 finding 4。
**`_under_root`**:見 finding 3。
**`_INVISIBLE_EXTRA` 與 lens-repo**:lens-repo 沒有這個常數,不會變兩份。lens-repo 只有舊版的 `_strip_zero_width`(`/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:5016`)。但同一支檔案裡已有另一張隱形字元表,見 finding 1。

以下 finding 的行號都是 `spec-gate-nondo/scripts/lumos` 的現況。

severity: major
blocking: 是 — 這次新增第二份隱形字元定義,實測漏掉 6 個碼位;同一族(危險詞夾隱形字元)已被連續換字元打穿三輪,第四次還有空隙
引句:「_INVISIBLE_EXTRA = frozenset([*range(0xFE00, 0xFE10), *range(0xE0100, 0xE01F0), 0x034F, 0x115F, 0x1160, 0x3164, 0xFFA0])」
對照:``scripts/lumos: `scripts/lumos:6978-6987` `` 的 `_PQ_DICP_RANGES` 加 `scripts/lumos:7030` 的 `_pq_is_default_ignorable`。這是專案已有的 Unicode 預設可忽略碼位全表,有版本釘和官方來源。另有 `scripts/lumos:37443` 的 `_PATH_SPECIAL_CATS`(Cc、Cf、Zl、Zp、Cs)。
判定理由:
- `_strip_zero_width` 現在是「Cf 類別」加手抄的 `_INVISIBLE_EXTRA`,成了第三種「什麼算看不見」的寫法。
- 我拿 `_PQ_DICP_RANGES` 對照,既不是 Cf 也不在 `_INVISIBLE_EXTRA` 的碼位有 U+17B4、U+17B5、U+180B、U+180C、U+180D、U+180F 六個。
- 例如夾蒙古文變體選擇符 U+180B 的「退款」,在 `_strip_zero_width` 不會被拿掉,在 `_pq_is_default_ignorable` 卻算看不見。同一個檔案裡兩張表給出不同答案。
- 改成 `category == "Cf" or _pq_is_default_ignorable(ch)`,就能刪掉 `_INVISIBLE_EXTRA`。

severity: minor
blocking: 否 — 說法過頭,沒有改變行為;凍結與回放走的是另一組參數
引句:「處置閘判定的唯一入口,吃已經讀好的這個編號的帳列」
對照:``scripts/lumos: `scripts/lumos:1126` ``、`scripts/lumos:1140`、`scripts/lumos:1268` 三處凍結與回放仍直接呼叫 `_loop_status_disposal`。`scripts/lumos:1077-1095` 的 `_load_rows` 是同一個篩法(編號相符且不是規格閘留痕)的第四份。
判定理由:
- 三處直呼帶 `spec_sha_override`、`result_out`、`retro_skip`,而且不經過 `_disposal_judge` 內「輪次不是字串」的跑滿回顧檢查。
- (b) 出口呼叫 `_disposal_judge` 時沒傳 `bad_linenos`,讀不懂的行被靜默跳過,訊息只補一句「已跳過」。
- 同一本帳在 `loop status --disposal` 是 rc2 擋下(fail-closed),在推送前 (b) 卻照過。這是刻意的設計(r8 合2),但「唯一入口」的說法不準。
- 建議把 docstring 改成「即時判定的唯一入口,凍結與回放另走」,並說清楚 (b) 為什麼不 fail-closed。

severity: minor
blocking: 否 — 漏的是原本就有的一處,不是這次新增;但守衛測試有盲點,「只剩一份」的說法不成立
引句:「r8 合5 再收六處另一種拼法的:席報告路徑(_severity_check_row)、loop next 印的在審材料(reviewed_spec)」
對照:``scripts/lumos: `scripts/lumos:15405` `` 還有 `Path(nx) if os.path.isabs(nx) else Path(root) / nx`,同樣是「絕對路徑照用、否則接根目錄」。
判定理由:
- 測試 `_abs_join_sites`(`scripts/test_lumos.py:64718`)只認 `.is_absolute()` 方法呼叫,認不出 `os.path.isabs`,所以這一處漏網。
- 該處的 `_retro_norm_path` 說明了不共用 `_prov_path` 的理由是方向相反,但 15405 這行本身只是接路徑,可以用 `_under_root`。
- 建議改成 `_under_root(root, nx)`,並讓守衛一併認 `os.path.isabs`。
- `scripts/lumos:1157` 與 `scripts/lumos:22322` 是拒絕絕對路徑,`scripts/lumos:28073` 是 `relpath`,都不是同形寫法。

severity: minor
blocking: 否 — 只是同一個席位條件寫了兩份,分岔風險小
引句:「只有架構對齊席、或沒寫席名,就沒有人逐行看。(a) 另要那一席判 clean/minor」
對照:``scripts/lumos: `scripts/lumos:9402-9408` `` 的 `_nogo_seat_ok` 與 `scripts/lumos:9451` 的 `seats = [...]`。
判定理由:
- `_nogo_full_review_gate` 在失敗訊息分支又手寫一次「有席名且不是架構對齊席」。
- `_nogo_seat_ok` 的前兩個子句因此在兩處各存一份,日後改席位規則容易只改到一處。
- 可以抽成 `_nogo_has_named_seat(r)`,兩處都叫它。
- 既有的 `loop status --light` 用另一種席位計法(`scripts/lumos:15356` 數 auditor 去重),這次沒動,不算新增第二種做法。

最高等級 major,blocking 1 條。
