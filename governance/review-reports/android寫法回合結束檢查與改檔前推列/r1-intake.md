preflight-4: ran

# r1 前掃收貨(2026-11-06)

被掃:`docs/lumos-toolchain-knowledge/Projects/Android寫法回合結束檢查與改檔前推列_計劃.md`(提交 cb9803ef2 那一版)。前掃計數:①未定義的詞 7、②壞引用 2、③範圍自相矛盾 6、④機械宣稱驗語意 6(另兩項缺口與 ③ 重複計列)。全部改進計劃本體;以下每條寫「修改前 → 後」。

## 最優先兩條(③,也列在 ④ 末)

- **`lint-new` 沒有 `--budget`**:前 → 範圍 1 旗標清單只有 `--worktree`、`--since`、`--json`、`--record-gate`,範圍 2 第 4 條卻帶 `--budget`;現行 parser 沒有這旗標,鉤子會被參數解析擋成 rc2,而鉤子只在 rc1 擋,等於永遠不擋且沒聲音。後 → 範圍 1 第 1 條新增 `--budget <秒>`(兩種模式都收、覆寫設定檔 `budget_sec`、從指令開始起算、非正數 rc2);範圍 2 第 5 條加「rc2 印一行重跑安裝、不擋」;新增 S13 與兩列預期值。
- **保底 1 秒與既有 30 秒沒對上**:前 → 範圍 1 第 6 條只寫「單條命令保底 1 秒」,沒說怎麼覆寫 `_LINT_NEW_DEFAULTS` 的 `per_cmd_floor_sec: 30`;鉤子給約 19 秒預算,照既有判法每條都不跑、永遠 rc3。後 → 工作樹模式改用程式常數 `_LINT_NEW_WORKTREE_FLOOR_SEC = 1`、不讀設定檔的 `per_cmd_floor_sec`(專案設定不能讓收工那道永遠不跑),`--diff` 照舊 30;S13 測「設定檔設 30 時工作樹模式照跑」。

## ① 未定義的詞(7)

1. 工具鏈根:前 → 「那支 lumos 腳本的上一層目錄(repo 根)」,字面上一層是 `scripts/`。後 → 改用主程式 `_kt_toolchain_root()`(盲判那條線建的):`scripts/lumos` 往上兩層、有 `skills/lumos-project-notes` 才算,否則退回 `_lumos_src()`;比對前再取真實路徑。也順帶擋掉「被複製進專案的 lumos 把專案當可信根」。
2. 規則包:前 → 沒定義。後 → 〈用詞〉新增一條指 `configs/ast-grep/kotlin-android/`。
3. 收工點名:前 → 沒定義。後 → 〈用詞〉新增,指 `check-graph-sync.py` 與 [[Systems/graph-sync-coverage]]。
4. 冷卻窗:前 → 沒定義。後 → 〈用詞〉新增,同會談同檔 20 分鐘內走 `--incidents-only` 快速路徑。
5. `no-files`、`not-checked`、rc3:前 → 當既有詞用。後 → 〈用詞〉新增「新增告警閘的狀態與退出碼」一條,列八種狀態與四種退出碼。
6. 席位代號:前 → 沒索引。後 → 〈用詞〉新增「席位代號」一條,指母計劃卷證的 `r2-<席>-sonnet.md` 與本篇卷證目錄。
7. 預期值表「第二輪設計審 S5 舊條款」:前 → 沒交代是哪份的 S5。後 → 改寫成「母計劃第二輪快照(卷證 r2-snapshot.md)的 S5『Edit 的舊字串裡 應 不推』」。

## ② 壞引用(2)

1. 跨案函式與測試歸屬:前 → 「誰先實作誰建」,S10 綁 `t_kt_decision_table_shared` 測讀表本身。後 → 查了 `android-situation-evidence` 工作樹的 `scripts/lumos`:`_kt_decision_table(path=None)`→(列, 問題)、`_kt_trigger_re(t)`、`_kt_toolchain_root()`、`_strip_c_comments(…, kotlin=True)` 都已建好,讀表借 `check.py` 新增的 `dt_table`(依表頭名稱),載入時存成 `_KT_DT_ROWS`、`_KT_DT_ERR`。計劃改成三支函式與 `dt_table` 及其測試**歸盲判那條線**,本案只呼叫;S10 改成測本案自己的消費行為(停用列、「(無)」列、讀表錯誤、列欄位),測試名換成 `t_impact_decision_rows_table_states`;〈實務隱患〉相依案寫明範圍 3 與白名單的工具鏈根要等那條線合進主線。
2. 「既有三處內嵌解析」與 `_porcelain_z_paths`:前 → 說三處、沒提 `_porcelain_z_paths`,也沒說為何不擴充。後 → 範圍 1 第 2 條寫明:`_porcelain_z_paths` 已吃舊路徑但只回路徑、丟狀態碼與舊路徑,本案三樣都要;切欄邏輯搬進新函式 `_porcelain_v1_entries`,`_porcelain_z_paths` 改成呼叫它再取路徑(兩個既有呼叫端行為不變);只有 `_handoff_files` 的內嵌解析不遷移(〈不做〉同步改)。

## ③ 範圍自相矛盾(6)

1. `--budget` 漏列:見最優先第一條。
2. 保底與預算沒對上:見最優先第二條。
3. 「沒被平台排除」對決策列無定義:前 → 沿用題目的平台排除字樣。後 → 範圍 3 第 2 條定成「`_stack_platform_excluded` 回的集合裡沒有 android_only 的題號」(即這支檔不是全判伺服端);S9 加「判成伺服端時不推」。
4. 「沿用 `_stack_applicability`」說法不精確:前 → 待解第 7 組說併進 `_stack_applicability` 通道。後 → 改成「放進 `cmd_impact` 算 `stack_questions_applicable` 的那一段、同一組啟用條件,不是呼叫 `_stack_applicability` 本身(那支用預編題目樣式)」;PRIOR-ART ⑥、〈決策〉第四條同步。
5. D-49 無處置:前 → 只改 D-33、D-34、D-39。後 → 範圍 3 第 5 條寫明門檻管字不管列,D-49 每個字都低於 8%(最高 `runTest` 6.8%)不改,列太常推交 RETIRE-IF。
6. `--harness codex` 沒交代:前 → 「不另加旗標」。後 → 範圍 2 寫明註冊由 `_hook_cmd` 產生,帶 `--budget 30`、Codex 目標另帶 `--harness codex`,鉤子只讀 `--budget`、其他參數一律忽略。

## ④ 機械宣稱驗語意(6)

1. `_inner_budget` 起算點與 `--budget` 來源:前 → 「30 × 0.7 − 已耗」,沒寫起算點。後 → 範圍 2 寫明 `main()` 第一行先呼叫一次載入來的 `_inner_budget()`(它的 `_BUDGET_START` 第一次呼叫才記),外層秒數由它從 `sys.argv` 的 `--budget` 讀、預設給 30;`HOOK_BUDGET` 新增一值就讓 `_hook_cmd` 帶上 `--budget 30`。
2. `_kill_proc_group` 直接 SIGKILL 沒寬限:前 → 依據表把它跟 E3「SIGTERM 後 1 到 2 秒」併列。後 → 寫明它直接 SIGKILL、刻意照用(檢查工具唯讀、結果檔由 lint-new 自己刪);寬限只放在上一層「鉤子對 lint-new 先 SIGTERM、1 秒後 SIGKILL」(lint-new 有快照要收);寫明主程式現在沒有訊號處理器、這是新裝的,並寫出程序登記點(`_lint_run_and_parse` 拿到 `_lint_spawn` 的程序後放進模組層清單、等完拿掉);依據表拆成「有寬限」「無寬限」兩列。
3. `_voice_once` 清理路徑:前 → 「標記跟著既有冷卻目錄 24 小時清」。後 → 寫明標記在 `<系統暫存目錄>/lumos-impact-<會談>/voice-row-D-n`,由既有 `_ttl_lazy_cleanup` 在每次改檔前鉤子跑時刪「目錄本身修改時間超過 24 小時」的 `lumos-impact-*` 目錄(已讀程式確認),所以是會談最後一次新增標記後 24 小時整個目錄一起清。
4. `cmd_impact` 啟用條件漏列:前 → 「完整模式、不是測試檔、棧是 kt、沒被平台排除」。後 → 範圍 3 第 2 條列全:`--json`、非 `--incidents-only`、非測試檔、棧 `kt`,再加 `delta_new` 是字串、不是全判伺服端、決策表讀得到;第 4 條寫明 S9「影響脈絡是空也照印列」要改的是鉤子的判空(`_ranked_ctx`),不是 lumos 那一段。
5. `check.py` 依欄序讀:前 → 「用 `check.py` 的 `_cells`、`dt_triggers` 依表頭名稱取欄」。後 → 寫明既有 `catalog_problems` 是固定 7 欄依欄序;依表頭名稱取欄的是盲判那條線在 `check.py` 新增的 `dt_table`,`_cells`、`dt_triggers` 是兩邊共用的切格與觸發字解析。
6. 「既有三處」解析數量:見 ② 第 2 條。

## 連帶改動(不是前掃點名的)

- 決策列剝字串從 `_stack_norm_line` 改成盲判那條線的 `_strip_c_comments(kotlin=True)`(整段剝,巢狀註解與字串樣板都對):E8 結論、天花板 5、待解第 7 組、〈不做〉、S9 與它的預期值同步;天花板 5 縮成「Edit 片段從字串或註解中間切起」。
- 回傳欄位 `not_applicable` 改名 `alt`,照盲判那條線列字典的欄名。

## 沒動的

- 決策 d1(同一批只擋一次、同會談最多三批)、d2(沒圖譜不推列):這次的修正沒碰到,範圍 2 第 6 條、〈不做〉、天花板 6、REVISIT 照舊。

## 收貨(r1 四席)

- 四席全 sonnet:通才、可行性(臨時 git repo 實跑 E4–E6、1 萬檔 500 改動量時間)、依據(WebFetch 官方鉤子頁)、架構對齊。外家預設不派,結論寫成「單家族視角下」。
- 通才、依據兩席初交時有 severity major 而 blocking 否的矛盾,退回原席自己重判,重交版改成 blocking 是;存檔的是重交版。席位沒改 repo;臨時目錄已清。

## 先查世界與裁決(編排者)

- 裁決:跨案相依(白名單的工具鏈根、決策表讀表、觸發字邊界都在第三批分支):實作在本機整合分支上進行——先把第三批分支(EnzoHsieh-Android/android-situation-evidence)合進來再開工,不另寫同名函式、不等主線(使用者 2026-11-06:主線不會再動、全部做完再一起推)。計劃〈範圍〉的「先做範圍 1 與 2」改寫成這個做法。
- PRIOR-ART: 擋停上限與去重綁回合(`prompt_id`)而不是整個會談——官方鉤子頁:`prompt_id` 是「UUID identifying the user prompt currently being processed」(https://code.claude.com/docs/en/hooks.md );去重鍵用(會談, 回合, 批次)。被背景工作或排程喚醒的回合,官方 Stop 段以 `background_tasks`、`session_crons` 區分,計劃要列實驗量測這類回合有沒有 UserPromptSubmit,沒有就明寫行為(不檢查並印一行、或以 Stop 帶的欄位判)。
- PRIOR-ART: 記帳只在真的擋下時寫(鉤子決定擋之後才記),照既有「判定函式只回傳、帳由呼叫層寫」。
- PRIOR-ART: 鉤子共用程式照既有 `_hookevent.py` 那種底線開頭共用模組加 `sys.path.insert` 匯入,不用 importlib 載另一支鉤子;新鉤子登記點全列(`_GLOBAL_CLAUDE_HOOKS`、`_VENDORED_TREE_FILES`、Claude 與 Codex 兩份存活事件清單、`_hookevent.guard` 包 main),各補條款。
- PRIOR-ART: 子程序收尾——檢查工具在自己的程序群組(`start_new_session=True`),收尾要打到工具的群組;先登記再開跑,寬限內由 lint-new 自己收,鉤子的強制終止要涵蓋工具群組。
- PRIOR-ART: 改名鏈——沿 porcelain 的舊路徑追回 HEAD 有的那一端,追不到才算基準為空並列出。

## 逐條去向

全部折入(通才 5、可行性 4、依據 7、架構對齊 3,共 19 條),細目由計劃〈審計修正紀錄〉逐條對照。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 可1 | 可行性 F1 | 臨時 repo 先 git mv 再 mv 再 git add -N,看 porcelain 輸出的舊路徑 | HIT(席位實跑):第二筆舊路徑是索引中間路徑、HEAD 沒有 |
| 通1 | 通才 F1 | 讀計劃:名額標記檔不分回合 | HIT(讀計劃字面) |

refuted: none
