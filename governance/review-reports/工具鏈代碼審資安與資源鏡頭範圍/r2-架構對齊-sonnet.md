severity: minor

整體判斷:這版跟專案既有做法一致,沒有引入第二種做法、跨層直呼或自造已有工具函式。只有兩條位置上的小差異,列在下面。

### Finding 1
severity: minor
blocking: 否 — 沒有第二種做法,只是新說明放的位置跟既有放法不同
引句:「圍欄之後的說明加一條:「工具鏈本 repo(`loop next` 印了『鏡頭範圍: 工具鏈本 repo』)派工時」
對照:
- §3 圍欄結束後緊接 `### §3.1`,沒有「圍欄後的說明」這個位置,`file: \`skills/lumos-design-loop/templates.md:206\``。spec 把它寫成「圍欄之後的說明加一條」,等於新開一個位置。
- 既有的編排者備註放在圍欄前的 `### §3 編排者派工前須知(不貼進派工詞)`,`file: \`skills/lumos-design-loop/templates.md:110\``。
- 對 §3 第 1 點做每席調整,既有寫在 §7 的 ★ 行,`file: \`skills/lumos-design-loop/templates.md:478\``。
- 「圍欄外寫換掉哪一段」也有先例,§7.9 寫「只把…換成下面這段」,`file: \`skills/lumos-design-loop/templates.md:452\``。

判定理由:
- 「由編排者在圍欄外替換」這個做法本身有先例,不算新做法。
- 只有落點偏離。建議放進 `### §3 編排者派工前須知`,或併進 §7 那兩條 ★ 行旁邊,讓同一個 §3 第 1 點的調整集中在既有位置。
- 測試 `t_templates_toolchain_idempotency_scope` 的「圍欄之後」切法,也要跟著新落點改。

### Finding 2
severity: minor
blocking: 否 — try 包法與取根算式都一致,只有輸出位置和 JSON 欄位的常駐方式不同
引句:「位置:文字輸出緊接在「應派」那一段的 if/elif 兩支之後、不放進任何一支(編制表算不出來、印「目前算不出該派誰」時也照印),在「在審材料」那行之前。」
對照:
- 同一函式既有的附加提示(修正關卡、跑滿上限)都在 `emit()` 裡先算、放進 `out`,算的時候包在 `try: … except Exception: = None`,`file: \`scripts/lumos:16413\`` 到 `scripts/lumos:16421`。
- 文字輸出時,它們排在最後,在「圖譜」段之後,`file: \`scripts/lumos:16483\`` 與 `scripts/lumos:16487`。
- 它們的 JSON 欄位只在有值時才寫入,`if _fc: out["fix_check"] = _fc`。
- spec 的 `lens_scope` 則是常駐(`toolchain` 或 `default`),文字行插在「應派」與「在審材料」之間。

判定理由:
- try 失敗就不印、取預設,跟既有寫法一致。
- 取根算式 `Path(repo).resolve() if repo else _vault_repo_root(env)` 是同一支檔裡反覆出現的內嵌寫法(`file: \`scripts/lumos:1074\``、`scripts/lumos:16399`),獨立再算一次不算自造。
- 插在「應派」旁邊的理由站得住,因為它跟派席有關。這是風格偏好,可以接受,不構成 major。
- 另一個值得知道的小事:判斷「是代碼審編號」既有 `_roster_kind(loop_id) == "code"`,`file: \`scripts/lumos:14035\``。spec 沿用同函式內的內嵌 `startswith("code-")`,行為相同,也有同一函式內的先例,不列 finding。

### 已讀,無 finding

- **§7.8 填空 `{…}`**:範本裡本來就有帶說明文字的填空,`file: \`skills/lumos-design-loop/templates.md:422\``;有條件才加的填空也有,`file: \`skills/lumos-design-loop/templates.md:98\``、`file: \`skills/lumos-design-loop/templates.md:145\``。
- **§7.8 圍欄外的 `###` 小節**:同一個 `##` 底下圍欄後接 `###`,`file: \`skills/lumos-design-loop/templates.md:206\``(§3 的 §3.1)已有先例。既有測試切 §7.8 用 `"\n## "` 當界線,`###` 不會截斷它,`file: \`scripts/test_lumos.py:57856\``。
- **每份圍欄第二行寫刪檔規則**:跟「每份圍欄重複寫 git -C 那句」一致。§1、§3、§7.6、§7.8 的第二行都已重複寫那句,`file: \`skills/lumos-design-loop/templates.md:30\``、`templates.md:142`、`templates.md:343`、`templates.md:418`。§2 與 §7.5 本來就沒有那一行,spec 寫「補在 `LUMOS-SEAT:` 下一行」正好涵蓋。
- **`t_seat_templates_carry_marker` 的相容性**:它只驗第一行,`file: \`scripts/test_lumos.py:96273\``。補第二行不會讓它誤判。
- **決策取代、RULE 行、question-set**:`superseded_by: "#d3"` 加 `ended` 的寫法有同類先例,`file: \`docs/lumos-toolchain-knowledge/Projects/Android側UI測試綁圖譜工作流_計劃.md:60\``。RULE 行帶 `[依據:人] [since] [retire:人裁] [until] [confirmed]`,跟既有一致,`file: \`docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:46\``。`pending_questions` 的 `decision: "#dN"` 格式符合 `scripts/lumos:7810` 的檢查規則。
- **判別工具鏈本 repo**:用既有的 `_is_toolchain_repo`,`file: \`scripts/lumos:25437\``,沒有另寫一套。

最高等級 minor,blocking 0 條。
