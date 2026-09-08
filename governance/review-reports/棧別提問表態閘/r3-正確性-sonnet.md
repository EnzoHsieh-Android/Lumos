severity: blocker
# r3 正確性席(sonnet)——棧別提問表態閘(末輪)

### C1 題目 id 穩定性零機械守衛
severity: major
blocking: 是——改語意留舊 id 會讓統計桶混雜,且無測試能攔;同型態的「人工紀律、工具不驗」。
引句:「改措辭不改 id、改語意才換 id；表態與統計都以 id 為鍵」

### C2 「delta 掃描上限 2 MB」與「母體即 extract_delta_query」矛盾
severity: major
blocking: 是——既有函式 cap_chars=8000/512 詞、以空白重組丟換行,2 MB 門檻永遠碰不到。
引句:「改檔前的 delta 掃描上限 2 MB（超過只掃前 2 MB 並註記）」
file: `scripts/hooks/claude/impact-hook.py:412`、`scripts/hooks/claude/impact-hook.py:434-435`。

### C3 pre-push 把 check 輸出丟進 /dev/null 並自印死狀文案
severity: major
blocking: 是——只拆外層條件不動重導向,缺表態仍被講成「跑一輪代碼審查」。
引句:「pre-push 對每個分支 ref **無條件**呼叫 check（拆掉 tier=high 才呼叫的 if／elif），rc1 的原因由 check 印」
file: `scripts/hooks/pre-push:202-203`、`scripts/hooks/pre-push:206`。

### C4 跨 repo 平台 root 的 `git grep` 會 fatal(rc=128),不是找不到
severity: blocker
blocking: 是——多平台旗艦場景(root=../另一個 repo)第②道錨點永遠失敗;實測 `fatal: ... is outside repository`。
引句:「在被推送的樹命中（限該 profile 的測試副檔名）。未追蹤、未提交的測試檔自然過不了②」
file: `docs/lumos-toolchain-knowledge/Projects/多平台合約測試綁定_計劃.md:45`、`scripts/lumos:3391-3392`。

### C5 `--carry` 帶入舊 satisfied 證據不重驗內容(minor)
severity: minor
blocking: 否——天花板段已承認 GIGO;實作後用真樣本觀察。
引句:「有效性規則跟 pass 留痕**同一套**——目標 sha 等於表態 sha」

前輪:C1 已解(文字;實作面見 C3)、C2 已解、C3 已解、C4 已解、C5 部分解(新迴歸 C4)、C6 已解(殘留 C5)、C7 已解(殘留 C2)、C8 已解、C9 已解。
最嚴重 blocker(C4);blocking 共 4 條。
