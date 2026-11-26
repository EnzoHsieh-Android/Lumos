severity: minor

我對照了 S1–S8、S10(reach 部分)、S11、S21、S23 和範圍 1–4、6、7、12 的第一段部分。判定是縮水 1 條、未實作 1 條,都是 minor。另有 2 條標 ⚠ 交編排者。

## 已實作

- **範圍 1**:
  - `coverage` 鍵由 `_platform_cov_flag` 讀取,多平台與舊單平台 `test` 節兩條路徑都帶進 `load_platforms`,型別不對丟 `ValueError`。
  - `--no-cov` 旗標、`HELP_WHEN` 說明表、`06-代碼審與推送.md` 都已登記。
  - `--max-mutants` 預設改成 `None`,好偵測 `--reach-only` 同給;實際預設值不變。
- **範圍 2 ②**:
  - 經 `_kill_measure_singles` 加 `wrap`/`after`,與合併快篩共用,結果進 guard-kill 的基準快取。
  - 每支開跑前刪 AGP 固定位置的覆蓋資料檔,跑完沒有新檔記「覆蓋資料沒產出」。
  - 掛覆蓋紅的不掛再跑,綠就用不掛那次、覆蓋算不明(`red_rerun`),且不算進斷路器。
  - 收手時沒量到的記「時間不夠」。
- **範圍 2 ③**:`breaker` 看前 5 支 Robolectric(不足就全部,扣掉紅掉的),斷路後停止掛覆蓋,run 事件 `cov: tripped`。
- **範圍 2 ④**:
  - `_CHOICE_COV_ANALYZE` 一次 Gradle 呼叫、用 JaCoCo 分析 API,只挑壞法所在檔的套件資料夾、只留原始檔名相等的。
  - 輸出是 `hits`(測試序號對經過的壞法編號)加 `nolines`;逾時 `max(60, 支數×0.5)`,剩餘時間不夠記「時間不夠」。
- **範圍 2 ⑥ 與三條**:
  - `_KillPrep.run` 回傳依覆蓋選過的配方並呼叫 `on_prep`,`order` 改成子集,判定照子集判。
  - 續跑快取鍵是 `(平台, 測試名, 測試所在檔 blob, init 版本)`,存在 `choice-cov/<at_sha>/`,分析每次重做。
  - 工作目錄用 `_note_audit_safe_dir` 拒符號連結並自帶 `.gitignore`。
  - 中斷時不寫 reach。
- **範圍 3**:
  - `clause` 時合併快篩只帶子集(`_kill_merge_subset`),`_choice_merge_classify` 的 `names` 傳子集,合併基準仍是整組。
  - `none` 時記 `survived`、`via: cov`、`judged: cov`、`cov_sha`,`tests_sha` 寫 `"cov:"+tests_sha`。
- **範圍 4**:
  - `reach` 事件欄位、`reach_clauses` 排序與 4096 截斷旗標(`_gate_event_fit`)、`reach_n`、`reach_why` 字串表都在。
  - run 事件有 `cov`、`cov_secs`、`cov_skipped`、`cov_selected`、`cov_full`;`reach-run` 事件也有。
  - `LOOP_NOT_CLOSE_EVENTS`、`_GOV_FIELD_TYPES`、gov 的 `ck` 欄位白名單已登記。我只找到 `LOOP_NOT_CLOSE_EVENTS` 這一處 (gate, kind) 登記。
- **範圍 6**:
  - `_choice_ledger_aux` 只收 reach,型別不對略過;`_choice_ledger_index` 不動。
  - `_choice_kill_pick`:`via: cov` 要這次也開覆蓋且 `cov_sha` 相同才帶過去,否則重跑。
  - reach 有效判定正確,`unknown` 也算有效。
  - gov 另列「依覆蓋判存活」與「依覆蓋判存活後改跑」,第一次判定不變。
- **範圍 7**:
  - `--reach-only` 只補存活而沒有有效 reach 或暫時性 unknown 的行,走 `prep_only=True`,不寫壞法事件,記 `reach-run`。
  - 與 `--no-cov`、`--only`、`--max-mutants`、`--no-merge` 同給 rc2;工作目錄乾淨檢查沿用 `_choice_kill_base`。
- **範圍 12**:`guard-kill.md`(responsibility、prep 呼叫點、`_kill_measure_singles` 共用、子集 WHY、中斷 PITFALL)和 `規格閘.md` 已更新。
- **驗收條款**:S1–S8、S10、S11、S21、S23 各有對應測試(`t_choice_cov_reach_clause` 到 `t_choice_cov_subset_judge`,另有 `t_choice_cov_config_keys`);我沒有執行測試,只對照程式。

## 縮水與未實作

**[F1] 工作目錄清檔時機縮水(範圍 2「工作目錄」)**

severity: minor
blocking: 否
引句:「清檔在每次 choice-kill 與 choice-layer 開頭做」

清 `choice-cov/` 的動作只在 `_choice_cov_dir` 裡。它只由 `_choice_prep_attach` 呼叫,而 `_choice_prep_attach` 只在「有開覆蓋的平台且有壞法要跑」時才進來。`--no-cov`、沒開 coverage 的平台、沒有壞法要跑的 choice-kill,都不會清舊的 `at_sha` 資料夾。

**[F2] 範圍 12 的母計劃標記未做**

severity: minor
blocking: 否
引句:「[[Projects/選擇點變異覆蓋選測試_計劃]] 標成由這份做掉」

diff 的 5 個檔不含 `選擇點變異覆蓋選測試_計劃.md`,該檔 `status: todo` 沒變。這條屬範圍 12「跟這些有關的文件寫回」,若編排者認為它要等本計劃收尾才做,可降為不算。

## ⚠ 交編排者

- **中斷規則在 spec 內互相矛盾。**
  - 範圍 2「中斷」寫「量齊基準照 `_kill_measure_singles` 的現行規則(等手上那支跑完)」。
  - S7 與預期值表寫「當場收掉那次 Gradle 呼叫」。
  - diff 照 S7 做:`wrap` 回傳 `_KillPrep` 當當場收的標記,並在 PITFALL 說明。
  - 我判為符合驗收條款,不算縮水,請確認以 S7 為準。
- **`prep_only` 時零配方不回 rc2,diff 沒有顯式處理。** `cmd_guard_kill` 的零配方 rc2 判斷沒動。但 `_ChoiceKillRun.run` 只在 `self.recipes` 非空時才呼叫它,而且回傳值被忽略,所以實際行為不受影響。

縮水+未實作共 2 條
