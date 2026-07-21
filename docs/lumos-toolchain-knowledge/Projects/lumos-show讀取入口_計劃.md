---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/全盤外審2026-07_調研]]"
  - "[[Systems/lumos-cli-read]]"
summary: |-
  FLAG:DECISION
  KEY:問題=規範禁直接 Read/Grep 圖譜(lumos-project-notes skill),但 lumos 無全文讀取指令——context 只給 summary 壓縮索引不含 body(scripts/lumos:3717 docstring 自述),agent 要讀完整決策理由只能違章(外審 blocker,見[[Projects/全盤外審2026-07_調研]] finding 2)
  KEY:解=新增唯讀 `lumos show <node> [--body-only]`——輸出節點檔完整內容(frontmatter+body);--body-only 略過 frontmatter 只印 body。分工:context=低 token 導航,show=完整真相讀取。stdlib 薄介面,非新治理層
  KEY:實作錨=掛既有名稱解析派發組(scripts/lumos:9656 的 links/backlinks/context/map 組,env.find 解析、找不到 stderr ERROR+rc2)——不造新解析路徑;show 同時寫 _usage_log(env,rel,"show")(三位置參數,對齊 scripts/lumos:3704 簽章與 :3721 呼叫慣例;r1 折入:原引用抄丟 env)
  KEY:★實作陷阱三條(r1 審計折入)★——①派發組尾行是**無條件** `return cmd_decisions(env,rel)`(scripts/lumos:9670),只把 "show" 加進 tuple 忘插 if 分支=靜默印出 decisions;必須在該行前插 `if args.cmd=="show": return cmd_show(...)` ②argparse 位置引數**必須命名 note 非 node**(:9658 getattr(args,"note")、:9660 裸 args.note 無保護,命名 node 會 AttributeError crash;codebase 有 note/node 兩套並存慣例,本組用 note) ③--body-only 開檔須 **utf-8-sig**(loader :195 慣例;show 是首個原樣吐全文的指令,一般 utf-8 會把 BOM 印進輸出)
  KEY:範圍刀=不做 --at <git-sha>(git show 已覆蓋歷史版本)/不做 --json/不做多節點批次;lumos-project-notes skill 補一行「讀 body 用 show」(解禁章的成文出口)
  KEY:圖譜同步義務(r1 折入,F8)——同一 commit 須帶:[[Systems/lumos-cli-read]] 讀指令數 12→13+show 條目、Verification 節點(plan_refs 回指本計劃)——pre-commit Gate 3 對 test_lumos.py(.py 命中 code regex)要求同 commit 有圖譜檔,此二者天然滿足;spec 原版漏列=落地首 commit 必被自家 gate 擋
  KEY:light 檔資格自核(M0 honor-system)——硬否決三訊號:①風險類:唯讀指令,四類風險面皆不涉 ②硬合約:不動任何 invariant 級合約(純新增讀取口) ③體積:預估 ~40 行 code+測試,50 行先驗內、孤立 → light 放行。⚠自核時 pitfalls --check 對本段「引用風險類名稱」關鍵字誤報全四類——honor-system 下人工判掉;此發現餵 [[Projects/design-loop輕量檔_計劃]] M1(機械化硬否決須剝自核段,同 risk-tiered assess_spec 黑名單剝除前例)
  DECISION:[2026-07-21]走 light 路徑(M0 首戰):pre-flight+1 通才席+canary 護+legacy --need 1+人裁實質收斂;存活 ≥major 即 ratchet 升 standard
  TEST:t_show 計畫覆蓋(六項,與 body 測試策略同單,r1 折入 F5 對齊):找到(rc0 全文含 frontmatter)/找不到(stderr+rc2)/--body-only(無 frontmatter 有 body)/模糊名解析(沿 env.find 既有行為)/show 不改檔(唯讀)/派發組迴歸(context/links 不受影響)
  DEP:[[Projects/全盤外審2026-07_調研]]｜scripts/lumos env.find/派發組
  PRIOR-ART:①最小解=既有派發組掛一個子指令+檔案讀取,無新機制 ②世界解=外審調研本體已裁(Spec Kit 單一 persistence model 警告) ③裁定=borrow-design(cat 級功能原生實作)
---
# lumos-show讀取入口_計劃

> **狀態**：spec 完成，light 路徑審計中（M0 首戰）。緣起：外審 finding 2（blocker）——規範禁直接 Read 圖譜，但 lumos 沒有全文讀取入口，結構性逼 agent 違章。
>
> **light 資格與審計路徑（frontmatter KEY 的 body 鏡像，r1 折入 F6）**：硬否決三訊號自核（風險類不涉／不動 invariant 級合約／~40 行孤立）→ 走 light：pre-flight＋1 通才席＋canary 護＋`--need 1`＋人裁實質收斂；**存活 ≥major 即 ratchet 升 standard 完整 panel**。自核時 `pitfalls --check` 對「引用風險類名稱」的段落誤報全四類（關鍵字迴聲）——honor-system 人工判掉，發現已餵 M1。

## 問題

`lumos-project-notes` skill 禁止直接 Grep/Read vault、指定以 `context` 進場；但 `cmd_context` 是「summary 壓縮索引」（scripts/lumos:3717 docstring 自述），只輸出 metadata/summary/合約/鄰居，**不輸出 body**。agent 要讀完整決策理由（decisions 全文、章節內文）就只能違反規範。今天實際發生：本會話讀 `design-loop提效_計劃` body 時 `lumos show` 不存在、只能退回 Read——當場踩坑。

## 規格

- **指令**：`lumos show <node> [--body-only]`（CLI 顯示名 `<node>`；**argparse 位置引數內部必須命名 `note`**，見下方陷阱②）
- **行為**：解析節點名（沿用既有 `env.find`，掛 scripts/lumos:9656 的 `links/backlinks/context/map` 派發組）→ 印該節點檔完整內容（frontmatter + body）到 stdout。
  - `--body-only`：略過 frontmatter 區塊（**只認檔案開頭**首個 `---` 對到第二個 `---`），只印 body；開檔用 `utf-8-sig`（陷阱③）。
  - 找不到節點：沿組內慣例 `ERROR: 找不到筆記: <名>` 到 stderr、rc 2。
  - 模糊名：`env.find` 既有解析行為（多筆命中 stderr 警告取第一筆，scripts/lumos:287-299），不另造。
  - 唯讀：不寫任何檔；同 `context` 寫一筆 `_usage_log(env, rel, "show")` 用量記帳（簽章 scripts/lumos:3704、呼叫慣例 :3721）。
- **實作陷阱三條（r1 審計折入，照抄會炸）**：
  1. 派發組尾行是**無條件** `return cmd_decisions(env, rel)`（scripts/lumos:9670）——把 `"show"` 加進 tuple 後**必須**在該行前插 `if args.cmd == "show": return cmd_show(...)` 分支，否則 `lumos show` 靜默印出 decisions（rc0 無錯誤）。
  2. 位置引數命名 **`note`**（非 `node`）：:9658 `getattr(args, "note", ...)`、:9660 **裸** `args.note` 無保護——命名 `node` 會讓所有 show 呼叫 AttributeError crash。codebase 有 note/node 兩套並存慣例（gov/spec-trace 用 node），本派發組是 note 套。
  3. `utf-8-sig` 開檔：loader 慣例（scripts/lumos:195，BOM 容錯）；show 是首個「原樣吐出全文」的指令，一般 `utf-8` 會把歷史 BOM 檔的 `﻿` 印進輸出。
- **skill 同步**：`lumos-project-notes` SKILL「禁直接 Read」段補一行成文出口——「需讀節點完整 body（決策全文/章節內文）→ `lumos show <node>`；context 仍是進場導航首選」。
- **圖譜同步（r1 折入 F8，同一 commit 必帶）**：`Systems/lumos-cli-read` 讀指令數 12→13＋show 條目；Verification 節點（`plan_refs` 回指本計劃）。pre-commit Gate 3 對 `test_lumos.py` 變更要求同 commit 有圖譜檔——此二者天然滿足；原版 spec 漏列，落地首 commit 會被自家 gate 硬擋。
- **CLI help**：`sub.add_parser("show", help="節點完整內容(frontmatter+body;--body-only 略 frontmatter)")`。

## 明確不做（範圍刀）

- `--at <git-sha>` 歷史版本：`git show <sha>:<path>` 已覆蓋，不重造。
- `--json` 結構化輸出：context 已有 as_json 導航用；show 是給人/agent 讀全文的，YAGNI。
- 多節點批次 show：逐個呼叫即可。

## 測試策略（t_show，六項，與 frontmatter TEST 行同單）

1. 找到節點 → rc0、輸出含 frontmatter `---` 與 body 標題行。
2. 找不到 → stderr 含「找不到筆記」、rc2。
3. `--body-only` → 輸出不含 frontmatter 鍵行（如 `type:`）、含 body 內容。
4. 模糊名 → 沿 `env.find` 既有行為（多筆命中 stderr 警告、取第一筆）。
5. 唯讀驗證 → show 前後節點檔 mtime/內容不變。
6. 派發組迴歸 → context/links 既有行為不受影響（既有測試不紅）。

## 實務隱患

- **frontmatter 邊界剝離**：`--body-only` 對「無 frontmatter 的檔」「body 內含 `---` 分隔線」要正確——剝離只認檔案開頭第一組 `--- ... ---`，不掃全文。
- **usage_log 副作用**：show 寫用量記帳（append jsonl）不算「改圖譜」——與 context 同慣例，測試 4 的「唯讀」指節點檔本身。
- **編碼（r1 修正 F7）**：show 是首個「重新開檔、原樣吐全文」的指令——**不是**其他 cmd 已處理的同路徑（它們只印已解析的 fields）。開檔必須 `utf-8-sig`（loader :195 同慣例），否則歷史 BOM 檔會在輸出頭多印不可見 `﻿`。

## 審計修正紀錄

**r1（2026-07-21，light 通才席首戰，sonnet×1）**：canary=summary↔body rc 矛盾型（TEST 行 rc1 vs 規格 rc2；probe 紀律偏離記錄：同窗重植×2 皆被 haiku 抓 → 改植入拓撲跨 frontmatter/body，r4 probe pass——**小 spec 的 ±20 行 probe 窗≈半份 spec，協議失準，發現已餵輕量檔計劃 M0 數據**）→ **caught**（審計員精準點出性質＋全庫 rc2 慣例佐證）。真 findings 7 條全折入 v2：
- **F2 派發組無條件 fallback（major，機械證實免辯方）**：:9670 `return cmd_decisions` 無守衛——必須插 if 分支，否則 show 靜默印 decisions。
- **F3 note/node 命名陷阱（major，機械證實）**：:9660 裸 `args.note`——引數必須命名 note。
- **F4 `_usage_log` 簽章抄錯（major，機械證實）**：spec 原文丟了 `env`，照抄必炸 TypeError。
- **F8 圖譜同步義務漏列（major）**：test_lumos.py 命中 pre-commit code regex，Gate 3 要求同 commit 圖譜檔；spec 原版只列 skill 同步（不在 knowledge 路徑下）＝首 commit 被自家 gate 擋。折入：同 commit 帶 lumos-cli-read 12→13＋Verification 節點。
- **F6 自核內容無 body 鏡像（審計員評 major→編排者按 severity 錨降 minor，理由：文件鏡像精度、非錯行為；照折）**：body 補 light 資格鏡像段。
- **F5 測試單 frontmatter/body 不一致（minor）**：統一六項。
- **F7 BOM 新風險面（minor）**：「無新風險」宣稱被駁——show 是新路徑，須 utf-8-sig。
- **輪判定**：canary caught；存活 max=major（F2/F3/F4/F8）→ **按 M0 ratchet 規則升 standard，r2 起走完整 panel（W=3）**。
