severity: major

整體判斷:這一輪修補多半往專案既有做法收斂。有一處把既有的時間預算慣例改壞了,另有兩處輕微的重複。

severity: major
blocking: 是 — `_dispositions_verdict` 的 `deadline` 簽名預設是 None,拿掉 None 判斷後,沒傳 deadline 的呼叫會在 `_time.monotonic() > None` 丟 TypeError。
引句:「if _time.monotonic() > deadline:」
對照:lumos: `scripts/lumos:51464`(`deadline=None` 預設,docstring「超過 deadline 時停下來」)、`scripts/lumos:51458`(`_disp_record_for` 明確保留 `None if deadline is None`)、`scripts/test_lumos.py:76848`(測試呼叫沒傳 deadline,且有一題適用,會走進迴圈)
判定理由:這段改動不在派工鏡頭範圍,是為了「全檔統一用 deadline」順手改的。專案對這個預設值的慣例是「None 表示不設上限」。`_lens_extcode_section` 那邊的 deadline 是必傳參數,所以不用判 None;表態閘的 deadline 是選填。把兩種慣例混成一種,等於在原本安全的路徑上加了新的崩潰點。我是從程式推導,沒有實際跑出 TypeError(測試在逾時前沒跑完,已中止)。要統一就得連簽名一起改,或把 `is not None` 判斷放回去。

severity: minor
blocking: 否 — 只多一份手抄的範圍類代碼,有守衛測試比對,漂移會被抓到。
引句:「_RANGE_ONLY_FAIL_CODES = frozenset({"commit_missing", "base_not_mainline", "no_mainline", "sha_unresolved", "empty_range"})」
對照:lumos: `scripts/lumos:48958`(`_LENS_RANGE_FAIL_CODES`)、`scripts/test_lumos.py:42934`
判定理由:掛鉤的計劃類代碼改成由 `LENS_FAIL_REASONS` 推導,方向正確,但推導時還要手抄一份「只屬範圍」的清單。這份清單跟 lumos 的 `_LENS_RANGE_FAIL_CODES` 只差一個 `not_git`。這不算第二套做法,因為 S11 守衛會一起比。另外 `_spec_fail_note` 裡 `code not in LENS_FAIL_REASONS` 的判斷現在多餘。

severity: minor
blocking: 否 — `--out` 的專用檢查範圍小,而且是 spec-freeze 自己的領域。
引句:「k = next((i for i in range(1, len(parts) + 1) if os.path.realpath(os.sep.join(parts[:i]) or os.sep) == real_root), None)」
對照:lumos: `scripts/lumos:49706`(`_spec_freeze_lstat` 對計劃路徑逐段 lstat)、`scripts/lumos:27268`(`_events_path_safe` 逐層檢查符號連結)
判定理由:同一個子命令裡,計劃路徑和 `--out` 各用一套逐段走訪的寫法。`--out` 因為要允許絕對路徑和 `..`,形狀確實不同,不是明顯重複。`_events_path_safe` 與 `_spec_freeze_lstat` 本來就各自獨立,所以這不是新增的第二種做法。

沒有問題的項目:
- `_vault_node_path`:只管路徑是否逃出圖譜,不重做 `_LANDS_IN_ITEM_RE` 的語法判斷。落點與連結兩條路共用它,是把原本落點那條單獨的檢查收成一支,不算第二套。
- 批次 `ls-tree`:`_spec_commit_index` 沿用 `_lens_git` 和 `--literal-pathspecs`。原本逐筆跑 git 的 `_spec_commit_has` 已刪除,沒有殘留舊路徑。
- `_write_bytes_atomic`:從 `_write_lf` 拆出位元組核心,取代手寫的 `_spec_freeze_write`,淨減少一套原子寫入。
- `_load_hook_file`:handoff 與 spec-freeze 共用同一個載入函式,關 bytecode 的做法也一致。
- `_SPEC_FREEZE_FAIL_CODES`:登記先於印出的做法與 `_LENS_FAIL_CODES` 一致。「不認得的代碼」的處理不同(spec-freeze 丟 ValueError,`_dispatch_lens_fail` 另有處理),屬各自的子命令,不構成衝突。
- 入口清 git 環境:只在 `main()` 設一次。lumos 與掛鉤全檔 grep `GIT_NO_REPLACE_OBJECTS`、`GIT_GRAFT_FILE`、`GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF`,沒有殘留逐呼叫的另一套。
- `_lens_spec_*` 的 deadline:沿用 `_lens_extcode_section` 的「絕對 deadline 加剩餘不足 1 秒就停、回 truncated」寫法,一致。

最高等級 major,blocking 1 條。
