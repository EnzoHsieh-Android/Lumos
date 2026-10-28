preflight-4: ran

# r1 收貨紀錄(room資料庫測試守衛)

## 首輪前掃(sonnet,固定清單四項;2026-10-28)

①②③ 與存在類命中直接修真檔、不算 findings:
- ① 「測試路徑」「非測試路徑」未定義 → 做法 1 補定義(src/<名稱>/,名稱為 test 或以 Test 結尾)。
- ① 「結構目錄/結構檔」怎麼認未定義 → 做法 1 補定義(路徑形狀 + 內容帶 formatVersion 與 database.identityHash)。
- ② macrobench-lab 路徑查不到 → S28 補本機路徑 /Users/enzo/orca/workspaces/macrobench-lab(存在,git 工作樹 main 222b80a)。

④ 語意類命中(修真檔,前→後對照):
- 做法 1 範圍起點。前:「跟主線分岔點比被推的終點提交」。後:「比範圍起點與被推的終點提交(起點照筆記形狀擋用的 _lens_push_base 算;掛鉤傳 _brange:一般推送是遠端舊值..本地頂端,新分支首推是跟主線的分岔點)」。依據:scripts/hooks/pre-push 的 pp_block_range_for 只有新分支首推換成分岔點。
- 做法 6 舊版 lumos 回 2 時「講一句」。前:只寫「照其他非零放行講一句放行」(掛鉤的 home、note-shape 兩段其實靜默放行)。後:明寫印「Room 守衛這次沒檢查(rc=N),放行」,照存量漂移那段寫法;S26 加「回 2 時應印這次沒檢查並放行」。
- 做法 6 掛鉤位置。前:「接在筆記形狀擋之後」。後:「接在筆記形狀擋那個 if [[ -n "$_hrange" ]] 區塊之後、區塊外面」(該區塊在 _hrange 為空時整段不跑)。
- 做法 6 與 S26 擋下時機。前:「在全套測試前停下」。後:「所有閘跑完、全套測試之前統一擋」(pp_record_block 只記旗標,判斷點統一 exit 1)。
- 做法 5 淺層 clone。後:補「另記一筆 skipped-env,跟筆記形狀擋一樣」(cmd_note_shape 淺層 clone 時記 skipped-env)。

以上皆不動核心裁定(兩條 WHY、做法 2–5 的判斷規則),不升級為正式 finding。

## r1 收貨(四席到齊後一次寫入;報告從子代理逐字稿取原文,不用完成通知的跳脫版)

- report-normalize:正確性、邊界、通才已是正規化格式;架構對齊 `--write` 搬了 8 處(行內 `- severity:` 改獨立行)。
- 架構對齊 2(a) 原標 minor 又標 blocking 是,兩欄矛盾,退回該席重判,席位回覆改 major/blocking 是;回覆原文附在該席報告尾,檔級改 major。
- quote-check:邊界、架構全錨;正確性 #14、通才 #7 兩句因 <10 字(通才那句是引句內巢狀「」被截斷)判 miss,機械重現如下表,原句在快照裡,照採信。
- refcheck:四席 file:line 全部對得上(ok 6 / 4 / 9 / 34,missing 0)。
- seat-check:四席都報 unreported 快照路徑(報告引的是內容不是路徑,只觀測)。

### 重現表

| id | 判法 | 命令 | 結果 | 處置 |
|---|---|---|---|---|
| c12 | 引句 <10 字 | grep -c "檔是新的就全部算" r1-snapshot.md | 1(HIT) | 重現,採信 |
| g8 | 引句巢狀截斷 | grep -c "清單加一行、假 lumos 認得" r1-snapshot.md | 1(HIT) | 重現,採信 |
| c1/b1 | `_brange` 推 tag 退成空樹 | 讀 scripts/hooks/pre-push 的 pp_block_range_for:只有 refs/heads/* 且舊值全零才換起點 | HIT | 重現,採信 |
| c3 | 跑完全部升級不寫數字 | 官方 migrating-db-versions 的 migrateAll 範例只用 addMigrations(*ALL_MIGRATIONS) | HIT | 重現,採信 |
| g1 | `@TypeConverters(Converters::class)` 被當類別名 | 計劃原文「取註解後第一個 class 名稱」,`Converters::class` 含 class 字樣 | HIT | 重現,採信 |
| a2 | 閘名不在 _KNOWN_GATES 不寫帳 | 讀 scripts/lumos 的 _gate_event | HIT | 重現,採信 |

### id 對照與處置(根因分組)

id 規則:正確性席 Finding n → cn;邊界席 Fn → bn;通才席 Fn → gn;架構席依報告裡 severity 行的順序:第 1 問 a1、2(a) a2、2(b) a3、2(c) a4、3(a) a5、3(b) a6、3(c) a7、3(d) a8。

- 範圍起點:c1 b1 b15 a1 g9 → 折(改交 `_push_range_start`、空樹不判)。
- 升級觸發與版本來源:c4 c5 c10 b2 b3 b4 b9 g1 g7 c12 → 折(以結構檔目錄為準、路徑不倒退、只要求終點版本結構檔、改名對雜湊)。
- 升級邊辨識:c7 b10 → 折(具名與位置參數、非整數字面改提醒;沒 addMigrations 寫進誠實界線)。
- exportSchema 與清空:b5 g6 → 折。
- 結構檔改寫:c8 g12 → 折(改比主線分岔點)。
- 升級測試認定:c3 b11 g11 → 折。
- DAO 測試認定:c2 b8 g2 → 折。
- DAO 改到判法:c6 b7 → 折。
- 剝註解:b6 c11 a5(3a)→ 折(重用 _C_STRIP_PAT、保留換行;巢狀寫進誠實界線)。
- 測試路徑:g4 c9 → 折。
- 型別轉換:c13 → 折(改提醒)。
- 登記處與簽名:c14 a2(2a) a3(2b) g8 → 折。
- RETIRE-IF 可量:g3 → 折(加 passed 帳、改用帳上比例)。
- 規範內容:g5 g10 → 折(Room 2/3 對照、社群標註、條款加 mock 與故障)。
- 錯誤處理與重用:b12 b13 b14 a4(2c) a6(3b) a7(3c) a8(3d) → 折。
- 放行:b16(席位自述交叉引用全對得上,無缺陷)。
