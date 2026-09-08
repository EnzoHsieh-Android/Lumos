preflight-4: ran

# r1 intake — 棧別提問表態閘(2026-09-08)

## 首輪前掃(sonnet,固定清單四項)
- ①未定義詞 6 處:Check T / GIGO / borrow-design / vault-free·Env / finding-refute / world-benchmark 裸名 → 全部當場改真檔(一句定義或補路徑),不算 findings。
- ②壞引用:0。frontmatter 全部節點與 DEP 列的函式/檔案/行號存在性驗訖。
- ③範圍矛盾 1 處(語意類,修真檔+留痕):「閘放哪裡」段 pass 一邊要「鍵對得上這個 diff 命中的問題」、一邊說「pass 不一定知道 diff」。
  - 修改前:pass 驗 JSON 形狀(三值、必附欄位、鍵對得上這個 diff 命中的問題)…沒帶旗標而 diff 命中棧 → 印提醒但不擋(pass 不一定知道 diff)
  - 修改後:pass 只驗形狀(status 三值、必附欄、question 非空),★不對照 diff★;鍵↔命中問題的對照移到 check(它本來就算 diff);S2/S3 條款同步。核心裁定「閘放在 check」沒動。
- ④機械宣稱驗語意:11 條全 OK(pass 原樣寫 note、check 走 _codeloop_guard_verdict 重算 diff/tier、diff_range 只在 check 用、pre-push:223 advisory 不影響 rc、_pitfall_diff_collect 產 stack_questions、_refcheck_scan 驗存在不驗內容、discover_test_methods 依 profile、pitfalls --check 只驗節存在、dispatch-lens 吃 base..head、gov --stats 按 gate 分組、reference.md:283 原文「建議」+「工具不驗」)。

## 機械排乾
- refcheck:0 條宣稱(計劃無 path:line 行內引用)。prose-lint:0。pitfalls --check:有節,命中 payment/external-send/prod-irreversible/self-governance 四類皆已逐類答。

## 收貨:外家否決席(codex)六條的機械重現(編排者,2026-09-08 夜)
- F1 skip 逃生路徑 → HIT:`_codeloop_guard_verdict`(scripts/lumos:20740 起,第 73 行註解「pass/skip 且 sha == marker_sha → 有效」)兩種留痕等價;pre-push 第 209-213 行把 `code-loop skip --note` 列為正式第二條路。spec 只寫 pass 帶表態=矛盾成立。
- F2 CI 讀不到 marker → HIT:`governance/.gitignore` 排除 `code-loop/`;`.github/workflows/ci.yml:48` 在乾淨 checkout 跑 `code-loop check --at-sha`;check 在 CI 只能退讀 tracked 的 `docs/.governance-log.jsonl`。spec 把表態寫進留痕檔與治理帳事件,但沒寫「表態必須在治理帳事件裡、且照既有『pass 後提交帳本再推』流程」。
- F3 --at-sha vs 工作樹 → HIT:pre-push 逐 ref 傳 `--at-sha "$_lsha"`(scripts/hooks/pre-push:165-203);`_validate_repo_ref`(scripts/lumos:14843)用 `repo_root / token` 讀工作樹;`discover_test_methods` 走訪工作樹。被推送 commit ≠ 工作樹時證據可造假。
- F4 多平台 → HIT:spec 指名單次 `discover_test_methods`(只吃 legacy profile);既有正確路徑是 `_platform_test_index(root)`(依 .lumos/config 逐平台 methods_for)。
- F5 鍵=序號、原文不對照 → HIT(設計缺口,spec 自己說跨版本靠原文卻沒釘住「存入原文==當前原文」)。
- F6 同 sha 並行 pass → HIT:`_codeloop_write` 用 `write_text` 直接覆寫、無 atomic replace;CI fallback 取該分支最後一筆事件。
- 效能/資源/回滾:席判無,同意(短命檔案+git 讀取)。
- Codex 報告引的行號是它讀取當下的舊行號(本工作樹 scripts/lumos 之後又被我改過),語意全部重現成立;refcheck 對報告跑會出 out_of_range,以本段重現為準。

## 收貨:正確性席(sonnet)五條的機械重現
- C1 CI 讀 ledger 重建無 dispositions → HIT:`_codeloop_read_from_ledger` 回傳固定四欄;`cmd_gov` 的 `load(name, mapper)` 欄位白名單(scripts/lumos:4678 附近)也不帶新欄。與外家 F2 同根:表態要進治理帳事件,且讀側(ledger 重建、gov mapper)要一起改,DEP 漏列。
- C2 多平台 → HIT(同外家 F4)。
- C3 派工鏡頭快取 → HIT:`_lens_cache_path(repo_root, base_sha, head_sha)`(scripts/lumos:19261)、`_lens_cache_read(path, ttl_sec=1200)`(19268);key 不含留痕狀態。
- C4 skip 路徑 → HIT(同外家 F1)。
- C5 「0 筆」→ HIT 但數字兩邊都不對:編排者重數 `grep -cE '"gate": *"code-loop"'` = 177 筆,其中含「檢核答|棧檢核」= 5 筆(席報 19,我原寫 0;我原來的 grep 帶了空白格式沒對上)。修真檔為「177 筆中 5 筆帶一句答案,其餘沒有」。

## 收貨:接手席(sonnet)九條的機械重現
- H1 CI → HIT(同 F2/C1)。
- H2 gov mapper 白名單 → HIT:`load(".governance-log.jsonl", lambda d: {"ts","commit","gate","kind","hard","nodes","detail"})`(scripts/lumos:4690 附近)只挑六鍵;`_gate_event` 的 `ev.update(extra)`(:899)寫進去的額外欄位讀側丟掉。
- H3 派工時表態不存在 → HIT(流程順序:派席在步驟 2、pass 在步驟 8)。★這條改變設計:表態必須獨立於 pass、在派席前就能寫入(新原語 `code-loop dispositions`),pass/skip 不再帶旗標,check 讀表態記錄★——同時解掉 F1/C4(skip 也有表態)。
- H4 S7 措辭會蓋掉 standard 分句 → HIT(reference.md:283 同句後半是 standard 的義務)。
- H5 效能檢核目錄 KEY 行漏列 → HIT。
- H6 多平台 → HIT(同 F4/C2)。
- H7 todo 錨點最弱 → 同意,加「todo 的 Issue 必須是本 sha 之後新建或正文含該問題關鍵字」成本高;改為 todo 必須指向 status open/doing 的 Issue 且理由 ≥10 字(同 na),鑑別力提一級。
- H8 簿記豁免 vs diff 範圍 → 讀 `_codeloop_guard_verdict` 前 140 行:豁免邏輯在留痕有效性判定(祖先 sha 之後只動簿記檔);表態改成獨立記錄綁 sha 後,用同一個「有效留痕座標」解析表態(找到的 sha 與 pass 相同),diff 範圍同一份代碼 diff(簿記檔本來就排除在 `_pitfall_diff_collect` 之外)→ 題目集合不變。判定:設計層已兜住,實作時加一條測試釘(簿記提交後 check 仍認得表態)。
- H9 旗標吃路徑還是內容 → HIT,裁定:吃檔案路徑,同 `--from-json` 慣例。

## 收貨:邊界席(sonnet)十二條的機械重現(節錄)
- B1 tier 與棧命中無關 → HIT:tier 來自 `_PITFALL_DIFF_PATTERNS`(Python 形狀 regex),棧命中另算;kt/swift/vue diff 幾乎永遠 standard,原設計的閘等於開不了門。★折法:閘條件改「有適用題就擋,不看 tier」,supersede 2026-07-20 裁定★。
- B2 CI → HIT(同 F2/C1/H1)。B3 docs/ 缺席 → HIT(既有 `_codeloop_gov_log` docs 不存在即 return),折為明確訊息。B4 多平台 → HIT(同)。B5 config 壞掉退 csharp → HIT,折為 BLOCKED 明講設定檔。B6 最後一次 pass 無人反駁 → HIT(同 H3),表態前移解掉。B7 path:line 切分 → HIT,定義切分規則。B8 理由門檻中英 → 折(非 ASCII ≥10/純 ASCII ≥25)。B9 status 大小寫 → 折(訊息)。B10 py 不在表 → 接受(另案)。B11 零命中輸出 → 折(`{}`)。B12 BLOCKED 長度 → 折(最多 10 問)。
- 引句錨定:正確性 3/5、邊界 1/11、接手 2/9、架構對齊 1/4 句對不回快照(標點抄寫差異:半形逗號 vs 全形、巢狀「」被截);外家 6/6 全錨→carrier。對不回的引句不採信,該條 finding 以 file:line 佐證通道成立(全部都有)。
