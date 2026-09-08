<!-- 外家否決席(Codex gpt-5.6-terra, xhigh, --sandbox read-only);原始逐字稿 r1-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

1.
severity: major
blocking: 是 — `.patch` 跳過只看副檔名、不驗 loop 類型，設計審可藉此令未標條款不進第五步。
引句:「skip 三種:審材不是 .md 計劃(code 迴圈的 patch)/ 迴圈首筆帳早於 _CLAUSE_GATE_SINCE(不回溯,週跑回放會重跑閘)/ 計劃無 [SN](opt-in 未啟用)。」
file: `scripts/lumos:13422` 函式沒有 loop id，`scripts/lumos:13434` 只驗尾碼，`scripts/test_lumos.py:4596` 也以非 `code*` 的 `cg-d` 驗證 PASS。
最小重現（已實跑）: `_disposal_clause_step(..., "design.patch", ...)` 輸出 `patch_skip skip`。

2.
severity: major
blocking: 是 — `[manual: ]` 被解析成空字串但仍視為「靠人」，使第五步 PASS，違反條款必須寫出怎麼驗。
引句:「要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗];設計審處置閘會擋。」
file: `scripts/lumos:4085` 容許空白捕獲，`scripts/lumos:4119` 保留空字串，`scripts/lumos:4122` 以非空 list 判定 manual，`scripts/lumos:13449` 僅擋 untagged。
最小重現（已實跑）: 真實 parser 加 gate 以 `- [S1] 甲 [manual: ]` 回 `blank_manual_gate= ok`；現測只覆蓋有內容的 manual PASS，見 `scripts/test_lumos.py:4592`。

3.
severity: minor
blocking: 否 — `spec-trace` 的 rc 已改成未標條款，CLI help、主要指引與雙語 command reference 仍說 rc1／用途是「驗證紀錄未認領」。
引句:「spec-trace ★裁決改綁定★:舊制全認領但條款沒標仍 rc1」
file: `scripts/lumos:4243` 實際依 `untagged` 回 rc；`scripts/lumos:21030`、`scripts/lumos:21439`、`skills/lumos-project-notes/commands/03-寫回圖譜.md:18`、`commands/INDEX.md:19`、`docs/command-reference.md:64`、`docs/指令參考.md:64` 均保留舊說法。
已實跑：本計劃輸出 `unclaimed=["S1","S2","S3","S4"]`、`untagged=[]` 且 rc0，但 `spec-trace --help` 仍說「沒有驗證紀錄認領」。

4.
severity: minor
blocking: 否 — 唯一出現在反引號或表格列的 `[SN]` 會作 fallback 條款，`defined=False` 卻仍能讓閘 PASS，與「反引號範例不算定義」的說法不一致。
引句:「clause: S10 定義行是 ### 那行(反引號範例不算)」
file: `scripts/lumos:4114` 收集非行首 fallback，`scripts/lumos:4117` 採用它，`scripts/lumos:13449` 不檢查 `defined`。
最小重現（已實跑）: `` `[S1] 範例 [test:t_ok]` `` 回 `backtick_gate= ok`；表格列同樣產生 `defined=False, state=manual`。

已讀,無 finding（凍結／回放）: 凍結後拔掉標記，週跑會持續 PASS；這是計劃明示的歷史判定模型，不是作者漏看。
引句:「凍結/回放模式帶 [SN] 沒標的活檔也跳過、理由句講明」
file: `scripts/lumos:596` 至 `scripts/lumos:615` 先用活檔取輪次、再以凍結 sha 重算；`Projects/條款綁測試算進度_計劃.md:184` 明定不重讀活檔。

已讀,無 finding（明示跳過）: 整份無 `[SN]`、首筆帳早於 cutoff 都是設計明示的 opt-in／不回溯；timestamp 由寫側自動產生，直接改帳本屬既有 append-only 信任邊界。
引句:「首筆帳早於 2026-09-08 的舊迴圈不回溯」
file: `scripts/lumos:4901` 自動寫 ts，`scripts/lumos:13430` 至 `scripts/lumos:13433` 套用 cutoff。

已讀,無 finding（七態）: 真測試加「只被提到」的 ref 會得 `mentioned`，同列 `[test:]` 加 `[manual:]` 以 test 為準；引用塊與編號列為定義，重複行首 id 取首次。
引句:「同一行同時有 [test:] 與 [manual:] → 以 [test:] 為準」
file: `scripts/lumos:4112`、`scripts/lumos:4126`、`scripts/lumos:4137` 至 `scripts/lumos:4148`；已以載入中的函式驗得上述狀態。

已讀,無 finding（程式化 rc／JSON 消費者）: hooks、governance shell、autonomous replay 沒有讀 `spec-trace` rc 或 JSON；既有 `unclaimed` key 亦保留。
引句:「舊制欄仍在(四條都無回指)」
file: `scripts/test_lumos.py:4530` 至 `scripts/test_lumos.py:4535` 為唯一 JSON 消費測試。

`python3 scripts/test_lumos.py -k clause` 未能實跑：唯讀沙盒沒有可用暫存目錄。

最嚴重 severity: major；blocking 2 條。
