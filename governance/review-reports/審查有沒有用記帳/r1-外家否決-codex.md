<!-- 外家否決席(Codex gpt-5.6-terra medium, --sandbox read-only;原始逐字稿 r1-codex-raw.txt;正規化:去重複印出的第二份、引句行全形括號改半形對回快照、一句含『』巢狀的截到巢狀前(內容未動) -->
severity: major

1.
severity: major
blocking: 是；舊帳同時缺 `reported`、集合與駁回欄時，S3 只規定「報 ?」，卻仍要求印存活／駁回／折／放行，會把未知值偽裝成數字。
引句:「`reported` 缺的印「報 ?(2026-09-09 前的帳沒數)」。」
file: `docs/.canary-log.jsonl:1` 既有列只有散文 note、無 `findings_set`；最小重現：該列進 `loop status --disposal`，預期必須印 `存活 ?／駁回 ?／折 ?／放行 ?`，否則任何 M/R/F/A 都無來源。

2.
severity: major
blocking: 是；S2 明稱 intake 對得上才算數，卻明定讀側不驗，故 R 可由任意 id 與一字理由灌大，不是可驗的「駁回」。
引句:「`--refuted-set` 的 id 要對得上 intake 才算數(讀側不驗,人抽查)。」
file: `scripts/lumos:5063` 現有集合帳的寫側範式會驗子集與全集，S2 卻只要求 refuted id 不重疊；最小重現：intake 僅有 `f1`、carrier 有 `findings-set=f1`，輸入 `refuted-set=虛構=x` 仍符合快照規則並印 `駁回 1`。

3.
severity: minor
blocking: 否；`severity: resolved` 不在既有嚴重度解析值域，若驗收報告只留下此宣告會被寫側判為沒有 severity 而 rc2。
引句:「嚴重度行寫 `severity: resolved`(不是留舊值)」
file: `scripts/lumos:4822` 解析器只收 clean/minor/major/blocker，且 `scripts/lumos:4849` 對空宣告回 noparse；最小重現：報告唯一嚴重度行為 `severity: resolved` → `canary record` 預期 rc2，規格須明定檔首仍必有 `severity: clean`。

S1 真實卷證計數：已讀,無 finding。
引句:「有 16 份跟手填的 `--findings` 一致」
file: `governance/review-reports/code-clause-bindings-b/r1-單reviewer-sonnet.md:1` 依快照規則扣首行後為 2，與帳一致；r1 外家 6、r2 單席 3、r2 外家 5、r2 架構 1、r3 單席 2、r3 外家 6、r3 架構 1 亦一致。

兩本帳與逃逸提醒：已讀,無 finding。
引句:「人記的帳(這段)跟機器擋的帳」
file: `scripts/lumos:4433` 現有 `gov --stats` 已把「閘的動作」獨立成段，S3 新段可物理分段；file: `scripts/lumos:6541` 逃逸帳本來就是 append-only 且不進閘。

總結：最高 major，blocking 2 條。
