severity: clean

我讀完 r4-repair.patch 的全部 hunk,對照 repo 既有寫法。三問都對齊,沒有不對齊的項目,所以沒有 finding。

**已驗主張**

1. 分層與依賴方向:對齊。新測試 `t_choice_kill_merge_cap_wiring` 從 `_load_lumos_inproc()` 取得載入的模組 `m`,攔截 `m._kill_run`,再經 `_ckm_repo`、`_ckm_inproc`、`cmd_guard_kill` 走公開入口驅動。這跟被刪掉的舊端到端案例,以及同檔相鄰的 `t_choice_kill_merge_budget_edge` 是同一條路徑,沒有跨層直呼。
   引句:「    orig = m._kill_run」
   file: `scripts/test_lumos.py:147219`(budget_edge 在同一函式內用 `m._kill_run = ...` 換掉再 `finally` 還原)

2. 攔截寫法:對齊。「包一層、記下參數、照樣呼叫原函式」在 test_lumos.py 早就是慣例。
   - 例子有 `def spy(path): ... return real(path)`(21908 行)、`def spy(path, *a, **kw): ... return orig(path, *a, **kw)`(85270 行)、`def spy(repo_root, *args, **kw): ... return real(repo_root, *args, **kw)`(71877 行、83021 行)。
   - 還原也都用 `finally: m._kill_run = orig`,跟這份修補一樣。
   - 所以這不是第二種做法。
   引句:「        return orig(cmd, cwd, timeout, *a, **kw)」
   file: `scripts/test_lumos.py:85270`、`scripts/test_lumos.py:71877`

3. 計劃條款與預期值表:對齊。
   - S22、S23、S24 沿用既有格式:`[Sn] 當…時,choice-kill 應…[test:…]`。
   - 預期值表 S22 到 S24 的欄位也是「條款 | 輸入 | 預期 | 來源」。
   - 來源欄用「代碼審 rN …」,跟 S1 到 S21 欄位用「第二輪 a1」「第三輪 rs1」的做法同族,沒有引入新欄位或新標記。
   - 多個測試綁定用連續的 `[test:a][test:b]`,跟 S4 原本的寫法一致。
   - 順帶看了綁定搬移:S4、S6、S20 拿掉的 `[test:…]` 都轉到 S22 到 S24 去了。`t_choice_kill_merge_screen_cap` 在 S22,`budget_edge` 和 `reestimate` 在 S23,`no_lane_chunk` 在 S24。S6、S19、S20 保留的綁定也都還在,沒有孤立的條款。
   引句:「- [S22] 當總時限只剩 R 秒、而且 R 小於下限時,choice-kill 送給合併基準與合併快篩的逾時上限 應 都不超過 max(R, 1) 秒 [test:t_choice_kill_merge_cap_wiring][test:t_choice_kill_merge_screen_cap]」

4. guard-kill 摘要行:對齊。
   - 新增的兩條 PITFALL(配方不在合併道、judged 重複記)用 `PITFALL:症狀 [出處:…] [根因:…] [修法:…] [test:…]`,跟同檔既有 PITFALL 一致。
   - 改寫的快篩逾時那條也沿用同一格式:`[出處:]` 往後累加輪次、`[修法:]` 寫明測試做法、`[test:]` 換成新測試名。
   - 縮排沿用該節既有的兩格縮排。
   引句:「  PITFALL:壞法的配方一支都不在合併道(那幾支單支基準全紅)時照開一次快篩,還把它記成合併判 [出處:代碼審 code-選擇點變異加速 r1 通才 #2] [根因:開快篩前沒看配方跟合併道有沒有交集] [修法:_kill_merge_in_lane 先看,沒有交集就不套壞法、直接交逐支] [test:t_choice_kill_merge_no_lane_chunk]」

5. 同族補測:`t_choice_kill_merge_budget_edge` 新增的耗時不等案例,沿用同函式內既有的 `types.SimpleNamespace` 與 `mg.remaining = lambda rem=rem: rem` 構造,`check(f"r3 …")` 的命名也跟同函式其他案例一致。
   引句:「        took = {"run aCase": 1.0, "run bCase": 3.0, "run cCase": 1.0}」

6. 錨點與帳務:`governance/anchor-baseline.json` 的 note 沿用「使用者在對話中核可,原話「簽」…」的既有格式(記憶 `anchor-approve-chat-consent` 規定的做法)。

**未驗範圍**:沒有跑測試,本席只判寫法是否一致,行為正確性由其他席負責。我也沒建 worktree,所以沒有需要移除的 worktree。暫存只有一個從 HEAD 匯出的 test_lumos.py 副本,已用字面絕對路徑刪除。

**不對齊共 0 條,其中 major 0 條**

總結:最高嚴重度 clean
