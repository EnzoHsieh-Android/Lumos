severity: blocker
# r3 接手席(sonnet)——棧別提問表態閘(末輪)

### H1 gov --stats 去重鍵把同 commit 兩筆表態折成一筆
severity: major
blocking: 是——去重鍵 (commit,nodes,gate,kind,token),code-loop 事件 nodes 恆空、token 只有 canary/rejected 給;牴觸「治理帳兩筆」,S9 分母失真。
引句:「同 sha 兩次 `dispositions` 寫入＝治理帳兩筆、marker 原子覆寫」
file: `scripts/lumos:4746`、`scripts/lumos:4699-4704`。

### H2 內容源(效能檢核目錄)沒有 id 欄,「改語意才換 id」無從執行
severity: major
blocking: 是——三個月後改目錄語意不知該不該換 id。
引句:「改措辭不改 id、改語意才換 id；表態與統計都以 id 為鍵」
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:26`。

### H3 S10 八份之外至少漏三份
severity: major
blocking: 是——commands/08 寫「低風險只提醒不擋」、docs/command-reference.md:95 與 docs/指令參考.md:95 寫 code-loop 是高風險專屬。
引句:「[manual:讀改後的八份文字對照本節]」
file: `skills/lumos-project-notes/commands/08-自動跑的.md:7-8`、`docs/command-reference.md:95`、`docs/指令參考.md:95`。

### H4 decision-supersede 會自動開 rel-cascade 連鎖帳
severity: major
blocking: 是——實測該節點有一個 plan_refs 入邊鄰居(Verification/2026-07-20_棧別效能追問),supersede 一跑就開一張待人跟的單;spec 沒提。
引句:「該節點沒有 `decisions:` 欄，先 `decision-add` 把當年裁定補成一條、再 `decision-supersede` 指向本案」
file: `scripts/lumos:22785-22805`、`scripts/lumos:11116`、`scripts/lumos:11664`。

### H5 「母體＝extract_delta_query」與 2 MB 預算矛盾,逐行正規化會被截斷邏輯破壞
severity: blocker
blocking: 是——cap_chars=8000、超 512 詞攤平成無換行詞列表;Write 全文情境逐行/跳註解失效。
引句:「改檔前的母體＝hook 手上的編輯內容（Write 全文、Edit 的 old_string＋new_string，即既有 `extract_delta_query` 那份」
引句:「改檔前的 delta 掃描上限 2 MB（超過只掃前 2 MB 並註記）」
file: `scripts/hooks/claude/impact-hook.py:434-446`、`scripts/hooks/claude/impact-hook.py:412`。

### H6 治理帳體積問題被加速(minor)
severity: minor
blocking: 否——已有 ledger-growth 顧問級檢查;REVISIT 該加一維。
引句:「看留痕帳裡 satisfied/na/todo/auto-na 的分布」
file: `governance/review-reports/repo-audit-2026-09-06/findings.md:1376`、`scripts/lumos:1640-1653`。

前輪:H1 已解、H2 已解、H3 方向已解(衍生 H5)、H4 原範圍已解(衍生 H4 新)、H5 已解、H6 原範圍已解(衍生 H2 新)、H7 未解(H3 新)。
最嚴重 blocker(H5);blocking 共 5 條。
