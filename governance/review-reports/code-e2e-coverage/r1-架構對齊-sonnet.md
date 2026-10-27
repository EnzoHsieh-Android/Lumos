severity: major

## F1 歸屬判定自己另寫一套,沒呼叫既有的 `_e2e_gate_owners`
severity: major
blocking: 是
引句:「if not any(_e2e_under(f, d) for d in shared) and not _e2e_owners(f, feats, index):」
file: `scripts/lumos:41584`
1. `_e2e_gate_owners(files, e2e, feats, deadline)` 已經在判「落在 shared_paths 底下,或對不到任何功能,就算沒歸屬(推送時要整套)」。它自己建 `shared`、`_e2e_owner_index`,再逐檔判 `_e2e_under` 加 `_e2e_owners`。
2. 新的 `_e2e_coverage_report` 把同樣的三步(shared 正規化、建 index、逐檔判)在內部又寫了一遍,只是把結果分到資料夾桶裡。
3. 之後有人改歸屬規則,例如 shared 的語意或 owners 的來源,就得同時改 `_e2e_gate_owners` 和 `_e2e_coverage_report`。兩邊不同步時,coverage 報的「沒歸屬」和推送時真的被擋的檔會對不上。這正是本命令存在的目的。
4. 新程式的 docstring 和筆記 WHY 都寫「歸屬照推送前判定那兩支(`_e2e_scope_hit`、`_e2e_owners`)」。這與實況不符:推送前判定用的是 `_e2e_gate_owners` 這個包裝,`_e2e_scope_hit` 與 `_e2e_owners` 只是它底下的零件。
5. 鄰居 `_e2e_changed_features`(`scripts/lumos:41067`)和 `_e2e_gate_need`(`scripts/lumos:41554`)都經 `_e2e_scope_hit` 過濾後再走單一歸屬函式。coverage 是第一個把「shared 加 owners」內聯展開的呼叫端。
6. 要對齊,可以把逐檔判定抽成回傳「每檔是否有歸屬」的共用函式,讓 `_e2e_gate_owners` 與 coverage 都呼叫它。

## F2 外來檔名不經源頭檢查、直接 print
severity: minor
blocking: 否
引句:「for f in u["files"] if files_mode else []:」
file: `scripts/lumos:41073`
1. 鄰居 `_e2e_changed_features`(`scripts/lumos:41073`)和 `_e2e_gate_need`(`scripts/lumos:41567`)在用檔名之前,都先做 `_path_special_chars` 源頭檢查,有控制字元就擋下、不印那種檔名。
2. 筆記 `android-e2e-acceptance.md` 的 WHY(patch 第 352 行)寫明:e2e 區的外來文字有兩層看門,源頭擋加出口清理。
3. coverage 的 `_e2e_coverage_input` 從 `ls-tree` 或 `_e2e_changed_files` 取檔名,沒做源頭檢查。
4. `_e2e_coverage_cmd` 的輸出也沒清理:資料夾名、`    {f}`、`、`.join(功能名、流程檔名、畫面名)都是原樣 `print` 到 stdout。
5. 鄰居 `_e2e_waive_list`(`scripts/lumos:41958` 起)輸出外來字串時一律包 `_esc_clean`。
6. `--json` 路徑用 `json.dumps`,這條不受影響。

## F3 讀 HEAD 設定並驗證的 4 步序列又複製一份
severity: minor
blocking: 否
引句:「full, err = _e2e_config_at(root, head) if head else (None, "讀不到 HEAD")」
file: `scripts/lumos:41877`
1. `_e2e_head_fp` 已有「`rev-parse HEAD`、`_e2e_config_at`、檢查 e2e 段存在、`_e2e_cfg_err`」這一整段。`_e2e_coverage_input` 逐步複製,只多一個 features 檢查。
2. 呼叫的是同一批底層函式,所以不算第二種讀法,結構沒歪。但現在有兩份同形序列,錯誤訊息也已經分歧:`_e2e_head_fp` 的合格錯誤前綴是「HEAD 的 e2e 段不合格:」,coverage 沒有這個前綴。
3. 要對齊,可以抽出共用的「讀 HEAD 的 e2e 設定並驗證」函式。

## 三問

1. 分層與依賴方向:部分不對齊。
   - 對齊:新碼放在 `_e2e_check_cmd` 前面的 android-e2e 子命令群。命令函式 `_e2e_coverage_cmd` 呼叫 `_e2e_coverage_input` 與 `_e2e_coverage_report`,再由 `_android_e2e_dispatch` 分派。doctor 呼叫 `_e2e_coverage_line`。這和 `_e2e_check_cmd`、`_e2e_select_cmd` 的層次一致,沒有跨層直呼 macrobench 或 vault 的內部。
   - 不對齊:見 F1。歸屬判定繞過 `_e2e_gate_owners`,自己另算一套(`scripts/lumos:41584`)。F3 是同類的小規模重複(`scripts/lumos:41877`)。

2. 命名與錯誤處理:大致對齊,有一處不對齊。
   - 對齊:函式名是 `_e2e_coverage_*`;錯誤走 `_say_block(err)` 加 `return 2`,與 `_e2e_check_cmd` 一致(`scripts/lumos:42221` 起,同為 `_say_block` 加 rc 2)。子命令參數沿用 `--repo`/`e2e_repo`、`e2e_changed` 的 dest 慣例,並補了 `HELP_WHEN`。
   - 不對齊:見 F2。檔名輸出沒有源頭檢查,也沒有 `_esc_clean`(`scripts/lumos:41073`、`scripts/lumos:41958`)。

3. 第二種做法:有,即 F1。
   - 沒有引入新的讀設定或跑 git 的方式:設定走 `_e2e_config_at`,git 走 `_nodehome_git`,檔案清單走 `_e2e_changed_files`,斷行走 `_nodehome_split_z`,都是既有的。
   - 測試用的 `_e2ecov_run` 與 `select` 測試輔助(`scripts/test_lumos.py:19213`)同形,沒有自創另一套。
   - SVG、`generate.py`、README 沒有新做法:標題仍只在 `ANDROID_ACCEPTANCE_TITLES` 一處,場景與 validate 共用。

⚠ 交編排者:設定來源在鄰居之間本身就不一致。
- `_e2e_select_cmd --changed` 讀工作目錄的設定(`_e2e_worktree_e2e`,`scripts/lumos:41147`)。
- `_e2e_check_cmd`、`_e2e_head_fp`、推送前判定讀 HEAD 提交的樹。
- coverage 讀 HEAD 的設定,卻配工作目錄的改動清單。使用者補了對照表但還沒提交時,`coverage --changed` 仍會報舊缺口。
- 新增的 SKILL 步驟 3 正好叫人在這個時點跑它。
- 沒有單一既有做法可對照,所以我不判這個不對齊,只標出來。這比較像行為問題,留給正確性席判。

不對齊共 3 條,其中 major 1 條
