severity: minor

我做了實測,沒有發現會讓派工鏡頭超過 45 秒預算或吃光記憶體的問題。有一條 minor:新增的讀帳段沒有跟著鏡頭的剩餘預算走。

實測條件:

- **真實帳**:`review-converge` 的版控治理帳約 20MB、12 萬行,其中 residual-ask 為 0 列。呼叫 `_lens_residual_section` 一次約 0.25 秒。
- **壓力帳**:我在暫存 repo 造了 12 萬列 residual-ask、約 35MB 的帳,頂端再多 3 列判 untestable 的問答。`_residual_tier_hits` 約 0.84 秒,`_lens_residual_section` 約 1.64 秒,峰值記憶體約 360MB。
- **快取版本升到 4**:`_lens_cache_path` 的 key 帶 `schema` 版本,舊快取自然 miss,每個範圍只會多算一次。以上面的成本,這個重算可以接受。

severity: minor
blocking: 否 — 只有 git 異常慢時才會超預算,而且超時後鏡頭會在背景算完,下一席讀得到快取
引句:「st, raw = _residual_blob_at(repo_root, rev, GOV_LOG_REL)」
問題:`_lens_residual_section` 沒有接 `deadline`,也沒有扣掉 `_t0 + _LENS_INNER_BUDGET` 已用掉的時間。它內部的單次 git 讀取上限是固定值:治理帳 60 秒(`_residual_blob_at` 預設 `timeout=60`),索引 20 秒,`ls-tree` 20 秒。固定席、角色段、外部碼表補選都會夾進剩餘時間,只有這一段不會。這一段在每次鏡頭都會跑,不只在有新增殘留的範圍。
具體失敗情境:大帳加上慢磁碟或淺層 clone,讓 `git show` 卡住。單次讀取最久可到 60 秒,起點和頂端各一次,還要加上索引的兩次讀取(各 20 秒),合計遠超 45 秒。hook 會判超時,並把工作交給背景暖機;暖機算完後會寫快取,所以影響只是這一席拿不到鏡頭,不是資料壞掉。
佐證:``file: `scripts/lumos:50103` ``(`_res_part = _lens_residual_section(root, base_sha, head_sha, vault_rel)` 沒有傳入 deadline)

已讀,無 finding:

- 計數相減的 `Counter` 在 12 萬列、35MB 的帳上是線性成本。
- 超大單行或過深巢狀的 JSON 由 `RecursionError` 與 `ValueError` 的攔截擋住。
- 合約數(5 條)和每條的問答數(12 筆)有上限,輸出不會膨脹。
- 帳讀兩次:`_lens_residual_new_lines` 在有 want 時會對頂端帳再讀一次,多約 0.8 秒,屬於重複但量小,不另列。

最高等級 minor,blocking 0 條。
