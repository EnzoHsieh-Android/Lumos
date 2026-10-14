severity: clean

這個分支沒有引入第二種做法,也沒有跨層直呼。逐項對照如下。

**1. 入口強制設環境變數**
- 在 `main()` 開頭加了 `os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"`,只有這一處,跟既定裁定一致。
- 我 grep 整支 `scripts/lumos`,這個變數名只出現一次,沒有逐呼叫補設環境變數的另一套。

**2. 截止時間檢查**
- 新增的檢查全部走既有的 `_note_reread_fp_expired(dl)`,截止時間用 `base["dl"]` 往下傳。
- `_note_reread_hunk_nodes` 和 `_note_reread_hunk_tags` 的 `deadline=None` 預設,以及「到期回 None、呼叫端記原因逾時」,跟同區其他函式的寫法一致。
- 呼叫端 `_note_reread_fp_tags` 判到 `got is None` 就回 `(None, "逾時")`,對應該檔退回 v1 的既有慣例。
- 沒有另外自己呼叫 `time.monotonic()` 算一套。

**3. 祖先核對的 git 呼叫**
- `_note_reread_bp_vs_remote` 用 `_lens_git_dl(root, "merge-base", "--is-ancestor", bp, old, deadline=dl)`,不是直接 `subprocess`。
- 逾時判斷用 `_git_timeout(dl)`,取主線候選用 `_push_mainlines` 和 `_push_mainline_full`,取完整 sha 用 `_lens_full_sha`,範圍解析用 `_lens_range_ok`,預設遠端用 `_lens_default_remote`。這些都是既有的包裝函式。
- 對照:`scripts/lumos: 48229` 的 `_push_mainlines` 內部也是 `_lens_git_dl(... "merge-base", "--is-ancestor", ...)`;`scripts/lumos: 37193` 也一樣。
- 沒有重寫主線候選解析,只是複用。

**4. 單次跳過環境變數的訊息**
- 新訊息用既有的 `LUMOS_SKIP_REREAD_CHECK`,沒有新增環境變數。
- 措辭「可以用 LUMOS_SKIP_REREAD_CHECK=1 git push 單次跳過(跳過會留帳)」,跟其他閘的「LUMOS_SKIP_NOTE_SHAPE=1 單次跳過(會留帳)」(`scripts/lumos: 34041`)同屬一型。
- 只在 `hard` 時才印,這是這支檔的慣例。

**5. `_note_reread_fp_walk_keys` 的共用方式**
- 有兩個使用處:`_note_reread_fp_prefetch` 的 `blob_order`,以及 `_note_reread_contrast_fp_v2`。批次讀和算指紋因此走同一個順序,原本的排序分歧就是這樣消掉的。
- 沒有被收進去的 `_note_reread_contrast_fp`(`scripts/lumos: 36800`)還留著 `keys = sorted({k for k in (_nodehome_key(v) for v in about) if k})` 這個內聯寫法,`scripts/lumos: 31209` 也有類似的。
- 這不構成 finding:v1 是「口徑一字不改」的凍結函式,順序不影響批次讀,而且這些內聯寫法在這次改動前就有了。

最高等級 clean,blocking 0 條。
