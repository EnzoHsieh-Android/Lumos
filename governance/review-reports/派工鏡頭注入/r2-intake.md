# r2 前置留痕(派工鏡頭注入)

日期:2026-09-03(晚)。r2=末輪驗收紀律:火力只掃 blocking 級與 r1 修復驗收;新 minor 照寫照記,可附理由 accepted。
機械排乾:refcheck ok 5/missing 0;prose-lint 0;pitfalls --check 有節。r2-delta.diff=r1 快照→r2 快照全部差異。

## 收貨三道(五席)

| 席 | 條數 | 最高 | blocking | quote-check | refcheck |
|---|---|---|---|---|---|
| s1 通才 | 5 | blocker | 2 | 全錨 | 19 ok / 1 missing(`scripts/hooks/{pre-commit,pre-push,post-commit}` 是大括號展開式,非真路徑) |
| s2 載荷安全 | 4 | blocker | 3 | 全錨 | 9 ok / 1 missing(同型) |
| s3 極端輸入 | 5 | major | 5 | 全錨 | 11 ok / 2 missing(`scripts/lumos impact --diff` 是指令串、`docs/測試-knowledge/中文節點.md` 是它臨時 repo 的路徑,皆非本 repo 檔案宣稱) |
| arch 架構對齊 | 2 | major | 1 | 全錨 | 25/25 |
| ext Codex | 5 | major | 5 | 1 句錨不到(f4「base=標記左側;節點在 base 不存在」跨了括號,非逐字)→ f4 不採信;內容(base 未驗證)照折 | 6/6 |

合計 21 條(5+4+5+2+5)、blocking 16(2+3+5+1+5)、blocker 4(s1-f1 圖譜路徑前綴、s1-f2 §7.6 共用格、s2-f1 contract 自由文字、s2-f2 matched_by 自由文字)——逐檔 grep 數的。

## 佐證通道機械重現(編排者)

- s1-f1 / cx-f2「node 是圖譜相對路徑」:`impact --diff c3b4f3f~1..c3b4f3f --json` 首筆 `"node": "Systems/lumos-cli-lifecycle.md"`,repo 內真路徑 `docs/lumos-toolchain-knowledge/Systems/…` → HIT。
- s2-f1「contract 帶 risk/ 標籤原文」:`scripts/lumos:15601` `_impact_contract` 直接串 tag 值 → 開檔核 HIT。
- s2-f2「matched_by=pitfall_when 原文」:`scripts/lumos:15872-15896` → HIT。
- s3-f5「ls-tree 不帶 quotePath 中文轉義」:s3 用臨時 repo 實跑重現;`scripts/lumos:16354` impact 自己對 `git diff` 加了 `core.quotePath=false` 並註明「r2 panel major」→ HIT。
- arch-f5「鄰居 repo 解析先 CLAUDE_PROJECT_DIR」:`scripts/hooks/claude/impact-hook.py:436` → HIT。
- cx-f1 / s1-f2「§7.6 共用」:`templates.md:236` 標題「code-loop 與 design-loop 皆派」→ HIT。

## 處置摘要

20 條採信全折(blocker 輪 accepted 必空);不採信 1 條(cx-f4)內容照折。
折入=消毒原則(自由文字零輸出)、base 主線可達驗證、圖譜路徑前綴、§7.6 兩支、標記正規式、quotePath、快取鍵 sha 檢查、錨點交叉測試+anchor-integrity 同步、兩個退役常數、砍一句話層、CLAUDE_PROJECT_DIR 優先。
