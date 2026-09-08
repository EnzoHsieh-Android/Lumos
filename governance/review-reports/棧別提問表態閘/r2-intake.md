# r2 intake — 棧別提問表態閘(2026-09-09 凌晨;修訂稿驗收輪)

## 收貨:外家否決席(codex)九條的機械重現(編排者)
- F1 CI 重建兩種獨立留痕 → HIT:`_codeloop_read_from_ledger` 只認含 `"passed"`/`"skipped"` 字面的行,`kind=dispositions` 事件會被跳過;pass/skip 事件不帶表態。折法:讀側分別重建「該分支最後一筆 pass/skip」與「該分支最後一筆 dispositions」,各自用同一套 sha/祖先規則驗;不靠 pass/skip 複製表態(閘不看 tier,standard 沒有 pass/skip 事件)。
- F2 治理帳寫失敗被吞 → HIT:`_codeloop_gov_log` 對 OSError `pass`,呼叫端照印成功。折法:新原語先寫治理帳(失敗 rc2、不寫 marker、明講),再寫 marker;順序寫進 spec。
- F3 `git diff --quiet` 看不到 untracked → HIT(語意):未追蹤測試檔可當證據。折法:丟掉 diff --quiet 那條;`test:` 證據=工作樹 discovery(profile 語意)∧ `git grep -F <名> <at_sha> -- <root>` 在該樹命中(sha 準確、便宜),未追蹤/未提交的測試自然不在樹裡。
- F4 hook 全文 vs check added 行兩種母體 → HIT(設計未講清)。折法:明文分兩層——hook=提醒母體(檔案全文命中,寬),閘=判定母體(diff 變動行命中);提醒 ⊇ 判定,spec 不再宣稱「同一組 when 同一結果」。
- F5 added-line 看不到「移除型」風險 → HIT(deletion-only diff 零適用=自動放行)。折法:`when` 對 diff 的 added 與 removed 行都比對(移除 CancellationToken/timeout/key 也觸發);recall-miss 帳照舊;大改動全問門檻改為「added+removed 行數」。
- F6 `stack_questions` 語意變更 → HIT。折法:`stack_questions` 保持舊語意(命中棧整組),新增 `stack_questions_applicable`(適用題)與 `stack_questions_meta`;hook 有 applicable 就只印 applicable;既有數量守衛測試不動。
- F7 tag 推送出口 → HIT:pre-push 對非 `refs/heads/*` 只 advisory。折法:總則縮為「分支推送」;tag 沿既有 advisory(CI 後盾對 tag 的 check 照舊);寫進實務隱患。
- F8 ledger 競爭與順序 → HIT。折法:明定「最後一筆=檔案行序最後一筆(非 ts)」;同 sha 重複事件後者覆蓋;不加鎖(同 pass 留痕既有限制),加一條兩程序交錯寫入的測試釘行為。
- F9 效能預算 → HIT(spec 沒寫)。折法:check 的表態核對加預算(同鏡頭 `_LENS_SPEC_BUDGET` 慣例,超時=fail-open 進治理帳)、每題 regex 在 import 時編譯(壞 regex=啟動即錯,測試釘)、hook 全文掃描限 2 MB。
- 效能/資源/回滾:席判同 F9/F8;回滾無新增。

## 前掃
- 修訂稿沒另派前掃 agent(r1 已做 preflight-4;r2 新增段落由五席直接審)。編排者自跑:lint 0 問題、prose-lint 0、pitfalls --check 有節、fold-check 只剩 reverse-omission 軟提醒(summary 未提旗標名,非矛盾)。

## 收貨:正確性/邊界/接手/架構對齊四席重現(節錄)
- C1/B8 pre-push if/elif 互斥 → HIT(pre-push:187/223)。折:表態核對進 check 當獨立判定;pre-push 對分支 ref 無條件呼叫 check。
- C2 ci.yml 訊息硬寫 tier=high → HIT。折:改訊息、ci.yml 進 DEP。
- C3/H2/B3 事件與 marker 缺 branch/head_sha → HIT(`ev.get("branch")==branch`)。折:形狀補齊。
- C4 `git cat-file` glob 不展開 → HIT(編排者用乾淨 repo 實測 `fatal: path ... does not exist`)。折:`git ls-tree` 先解析 slug。
- C5/B2 root 乾淨要求=整 repo 乾淨 → HIT(legacy root=repo_root)。折:丟掉,改 `git grep -F` 對 at_sha 樹。
- C6/B3 表態 sha vs pass sha → 折:同一套有效性規則,改碼即過期,`--carry` 重表態。
- C7/A1/H3/B1 hook 主詞與母體 → HIT(hook 只格式化;PreToolUse 在落地前)。折:lumos `impact --file` 依 stdin 編輯內容算 applicable。
- C8/H5 測試樣本 → 折:`stack_questions` 語意不變,舊測試不動;新測試用觸發樣本。
- C9/F5 刪除行 → 折:增刪行都比對。
- H1 LOOP_NOT_CLOSE_EVENTS → HIT(scripts/lumos:6321-6331、test:32283)。折:登記兩個新 kind。
- H4 decision-supersede 不可執行 → HIT(節點無 decisions 欄)。折:先 decision-add。
- H6/F5 原文當鍵 → 折:穩定 id。H7 四處文件 → 折:S10 補列八份。
- A2/F6 stack_questions 形狀 → 折:語意不變另加 applicable/meta。A3 傳入形狀 → 裁裸位置參數。A4 config 讀法 → 裁直讀 repo_root。A5/B15 剝字串跳註解 → 折。A6/B11 resolve_test_refs → 折。
- B4 前端 .ts → 折歸 vue 棧。B5 門檻範圍 → 折該棧增刪加總。B6 門檻值域 → 折。B7 gate=off → 折。B9/F1 kind 各取最後一筆 → 折。B10 理由門檻 → 折 CJK 計數。B12 全量指令 → 折。B13 空 when → 折測試釘。B14 撞名 → 接受(刻意不做,既有風險)。F7 tag → 接受寫進不做(advisory 既有)。F8 順序 → 折(檔案行序)。F9 預算 → 折。
- 帳面處置:blocker 輪 accepted 必須為空——B14/F7 以「刻意不做」段落明文承接,算折入(文件已改)。
