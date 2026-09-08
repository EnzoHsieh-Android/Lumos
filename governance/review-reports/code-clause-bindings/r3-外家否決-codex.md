<!-- 外家否決席 r3(Codex gpt-5.6-sol, xhigh, --sandbox read-only);原始逐字稿 r3-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

前輪 1 — 修好：`code-` 才跳過；`codefake` 等名稱現在視為設計審，未標條款會 fail。
引句:「code 開頭但不是 code- 的一律當設計審,fail-closed」

前輪 2 — 修好：半形／全形標點與純 emoji 都是 `untagged`；全形數字及 `a!!!` 會通過，符合本輪明訂的「至少一個英數實字」，不另列 finding。
引句:「if len(x.strip()) >= _MANUAL_MIN_CHARS and re.search(r"[^\W_]", x)」

前輪 3 — 修了但引入 Markdown 遮蔽缺口：成對同行反引號已修好，但 fenced code、整行 inline code 與奇數反引號仍誤判，見 finding 1。
引句:「line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw)」

前輪 4 — 修了但引入誤擋：`- [ ] [S1]`、`- [x] [S1]` 已算定義，但零定義硬擋會誤殺純引用及其他合法前綴，見 finding 2。
引句:「有 [SN] 卻沒有一條在行首定義:多半是這裡不認得的寫法」

前輪 5 — 修了但引入 JSON 缺口：人讀輸出不再謊報零條，`--json` 仍在索引錯誤時輸出 `total: 0`，見 finding 5。
引句:「驗收條款:測試索引建不起來」

1.
severity: major
blocking: 是 — 合法 Markdown 程式碼範例會被當成條款或觸發零定義硬擋，使正常設計審錯誤失敗。
引句:「line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw)」
file: `scripts/lumos:4112` 遮蔽只處理同一行成對反引號；函式級已實跑：fence 內 `[S1] example` 得 `untagged/fail`、整行 `` `[S1] example` `` 得空列但仍 `fail`、奇數反引號同行則製造 `S9=untagged/fail`。

2.
severity: major
blocking: 是 — 「原文有 `[SN]`、解析後零定義」無法區分格式錯誤與普通引用，會誤擋未啟用條款制的正常計劃。
引句:「if not SPEC_CLAUSE_RE.search(text):」
file: `scripts/lumos:13475` 函式級已實跑：`## 規格 [S1] 詳解`、`<!-- [S1] -->`、`1) [S1]`、`+ [S1]`、`• [S1]`、`— [S1]` 全部 `fail`；全形空白前綴則正常 `ok`。

3.
severity: major
blocking: 是 — 真條款同行的普通引用會被製造成第二條條款，破壞「行內引用不算定義」合約並錯誤卡閘。
引句:「定義行:這一行所有 [SN] 都算定義,各認到下一個 [SN] 之前」
file: `scripts/lumos:4120` 最小重現已實跑：`- [S1] 甲 [manual:人看一次]，詳見 [S2]` 得 `S1=manual、S2=untagged`，處置閘回 `fail`。

4.
severity: major
blocking: 是 — 重複條款編號只保留第一筆，可讓後續同編號的未標條款漏過。
引句:「defined.setdefault(cid, (no, seg))」
file: `scripts/lumos:4121` 最小重現已實跑：第一行 `[S1]` 帶有效 manual、第二行同為 `[S1]` 但未標，只產生一筆 `manual` 並使處置閘 `ok`。

5.
severity: minor
blocking: 否 — 只誤導 `handoff --json` 的機器消費者，不改處置閘結果。
引句:「c["total"] = len(rows)」
file: `scripts/lumos:20925` `_clause_bindings_for` 回索引錯誤時 rows 已是空列，函式級重現仍得到 `{"total":0,"index_error":"ValueError: bad config"}`。

最嚴重 severity: major；blocking 4 條。
