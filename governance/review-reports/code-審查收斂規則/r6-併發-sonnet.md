severity: major

實驗目錄已刪。

## Finding 1:舊索引加改到圖譜檔時,「未知決策位置」的殘留一律排最前,把真正新增的殘留擠出派工鏡頭

severity: major
blocking: 是 — 新增殘留是這輪鏡頭存在的理由,審查席必答題正是針對它。在升級後第一次推送,新增的那條可能整條不出現在鏡頭裡,審查席不知道要答。
引句:「keyed.setdefault(k, ("起點索引沒記這筆殘留的決策在哪篇,這次改了圖譜的檔", None))」

問題:`_lens_residual_new_lines` 對 `_residual_note_hits` 回的每一筆 `notes_unknown`、`notes_moved` 和 `notes` 都放進 `keyed`。`_lens_residual_wanted` 再把 `keyed` 的全部鍵一律設為排序級 0,也就是跟「這次新增」同一級。排序鍵是 `(want[ck], ck)`,同級就照節點名字串排。只取前 `_LENS_RESIDUAL_MAX`=5 條。

舊索引(沒有 `notes` 欄)的起點,每筆殘留的 `notes` 值都是 None。只要這次推送碰到任何圖譜檔,`graph` 就為真,所有舊殘留都進 `notes_unknown`。`guard residual --add` 本身會改圖譜筆記,所以「新增殘留的那一次推送」必然碰到。結果是新增的那條跟全部舊殘留同級,再被字串排序擠掉。這跟 r5 G3 修過的是同一類擠占。r5 的修法是分級,這輪新增的來源沒有跟著分級。

失敗情境:
- 實測 5000 筆舊格式殘留、新增 1 筆 `Systems/n5000`、改一個 `docs/x-knowledge/` 檔。
- `_residual_tier_hits` 回 `notes_unknown: 5000`。
- 派工鏡頭只列 `n0`、`n1`、`n10`、`n100`、`n1000` 這五條,最後一行是「另有 4996 條合約未列」。
- `n5000` 的出現次數是 0。
- 上線後所有尚未重跑 `--reindex` 的專案都是這個狀態。
- 即使不是舊索引,改到一篇存著大量殘留決策的筆記(例如 1000 筆),結果相同。

建議:把排序級拆開,「這次新增」與「合約改字」排 0,「改到筆記、換位置、位置未知」排 1。或者把位置未知彙總成一行,不逐條展開。

佐證:
- file: `scripts/lumos:48993`(`keyed.setdefault` 三處)
- file: `scripts/lumos:48863`(`_lens_residual_wanted` 以 `{... for k in keyed}` 一律設 0)
- file: `scripts/lumos:49009`(`order = sorted(want, key=lambda ck: (want[ck], ck))`)

## 已讀,無 finding

- **deadline 夾住每次 git 呼叫:**
  - 用在 PATH 放一支每次睡 8 秒的 git 假殼實測,deadline 設 12 秒,整段在 12.02 秒結束。
  - 索引讀起點版、讀頂端版、治理帳讀兩版、ls-tree、`diff --name-only`、決策筆記讀取都經過 `_residual_blob_at` 或 `t>=1` 判斷。
  - 剩餘不足 1 秒的路徑會印「算不出來」那句和必答題,不會靜默放空。
  - 呼叫次序:索引 2、diff 1、治理帳 3(含頂端多讀一次,上一輪就有)、決策筆記每條殘留 1。次數有界,但一條合約若掛很多殘留指標,同一篇筆記會重複 `git show`。因為有 deadline,只是浪費,不會超時。
- **大索引乘大改動清單的比對成本:**
  - 實測 `_residual_note_hits` 在 5 萬筆索引乘 20 萬個檔名下約 0.2 秒,`_residual_index_notes` 兩版共約 0.1 秒。
  - 整條 `_residual_tier_hits` 在 5000 筆索引、10 萬列治理帳(16MB,真實帳是 20MB、12 萬行)下是 1.75 秒、峰值約 67MB。
  - 整條派工鏡頭殘留段是 3.3 秒、峰值約 78MB。
  - 離掛鉤 45 秒很遠。
- **鏡頭餘裕:**
  - 殘留段的 deadline 是 `_t0 + 45 - 5`,跟外部碼表補選段同一個絕對時刻。
  - 前面的段若已用完時間,殘留段會直接印「算不出來」。後面只剩 `_lens_visible` 與輸出,餘裕足夠。
  - 純 CPU 的解析(治理帳逐行、JSON)沒有夾 deadline,但在真實規模下不構成問題。
- **`--add` 寫索引算 notes:**
  - `note_path` 每個不重複的殘留指標算一次。
  - `_vault_repo_root` 在迴圈外只算一次,`_pq_decision_target` 共用 cache。
  - 成本是線性的。
- **`main()` 開頭設環境變數:**
  - `GIT_GRAFT_FILE=/dev/null/lumos-no-grafts` 實測 git log 與 show 正常、不報錯。
- **pitfalls 分級路徑(`_residual_tier_hits`):**
  - 這條路的 git 呼叫沒有 deadline,最壞是各逾時上限相加。這在上一輪就是如此,不是這輪新增,所以不列 finding。

最高等級 major,blocking 1 條。
