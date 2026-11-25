severity: minor
圖譜鏡頭(知識同步)審查報告。範圍是 r2-repair.patch 改到的筆記、手冊、計劃、程式與測試。我只讀 patch、查 repo 現況,沒有改檔也沒有跑測試。

severity: minor

**F1:`Systems/guard-kill.md` 的 WHY 行還說 `n_mutants` 保留。**
severity: minor
blocking: 否。這是措辭過期,不會讓測試或推送被擋,也不會讓人做錯操作。
- 引句:「_KillMerge 的 n_mutants 只剩建構簽名相容」
- file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:65`(patch 新行 190)。這行是修補時才改寫的:「一個壞法也合併」那條 WHY,同一行已改成 `_KillMerge.plats[平台] = (False, 原因)`,卻留了這句舊話。
- file: `scripts/lumos` 的 `class _KillMerge`:`__init__(self, deadline, breaker=…, t0=None)` 已沒有 `n_mutants`。
- 計劃第二段〈做法〉2 也寫「`_KillMerge` 拿掉 `n_mutants` 參數」。三個月後的人會去找一個不存在的參數。
- 歸因:有證據的修復回歸。修補只改了同一行的 `off` 那段,漏了這句。
- 查證:`git grep n_mutants` 在 scripts/ 沒有命中,在 docs 只剩計劃的「拿掉」敘述和這行 guard-kill。

**F2:計劃 WHY 寫「不論原因都印一行」,跟「中斷只記不印」衝突。**
severity: minor
blocking: 否。只是措辭精度。
- 引句:「一個平台組這次不合併時,不論原因都印一行並把固定種類的原因記進 run 事件」
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:33`(patch 未改這行)。
- 修補把 `中斷` 改成 `quiet=True`(`scripts/lumos` 的 `_kill_merge_off`),計劃〈做法〉3 也寫「`中斷` 只記不印」。
- 合併基準不乾淨那案走既有字樣的另一行,不是「這次不合併(原因)」格式。這句 WHY 沒跟著改。
- 歸因:有證據的原有漏查,是第一輪就有的句子;修補讓例外變明確,但沒回頭改這行。

**F3:`_kill_merge_iter` 的 docstring 還說「off 記『中斷』」。**
severity: minor
blocking: 否。程式行為正確,只是 docstring 過期。
- 引句:「量基準途中停下(_KillHalt)→ off 記「中斷」再往外丟。」
- file: `scripts/lumos:29160`。`off` 字典已拿掉,現在是 `mg.plats[平台] = (False, "中斷")`。
- 歸因:有證據的修復回歸。改名時漏了這句 docstring。

**F4:計劃的 S7、S10 條款與預期值表沒有收進測試新增的案例。**
severity: minor
blocking: 否。測試比條款多,守衛沒變弱。
- 引句:「[S7] 當守 169 支、`--max-seconds` 是 1800、走到時限門前已花 40 秒時」
- file: `scripts/test_lumos.py` 的 `t_choice_kill_merge_budget_hint` 新增「基準量不齊提示照全部 3 支、約需 9 秒、--max-seconds 200」和「_ChoiceKillRun 傳自己的 t0」兩案。
- file: `scripts/test_lumos.py` 的 `t_choice_kill_merge_off_reasons` 新增指令形狀不支援、平台不穩、筆記未提交、讀結果檔模組不在、結果資料夾不在工作樹、只守 1 支共 6 案。
- 這些只寫在測試 docstring 裡。計劃條款與預期值表只有〈做法〉3 的文字交代,條款本身沒有。
- 條款是驗收單一來源,三個月後的人看條款會以為這些路徑沒驗收。
- 歸因:有證據的修復回歸,是修補補的測試。

**問題 1:[S1]–[S10] 與預期值表逐字對照測試斷言。結果:對得上,只有 F4 的覆蓋差。**
- claim:S1、S2、S3、S4、S8、S9 的斷言與表格列一致。
- input:`t_choice_kill_merge_failed_first` 五案順序與判定、S2 三案、`t_choice_kill_merge_failed_names`、`t_choice_kill_merge_event_fields`、`t_choice_kill_merge_unclean_reasons`。
- expected:表格列。
- case_source:我自己開測試讀斷言。
- before / after:修補把 S2 表格從「a、b、c、d」改成「a、b、c」。我讀到 S2 的測試斷言是 `[one, a, b, c]`,表格現在對得上。修補前表格是錯的。
- S9 舊帳改寫成「merge_kind 讀成空字典、single_runs 讀成 0」。測試的舊帳那案拿掉兩欄、看 gov 的 ck,兩邊一致。
- S10:對不到名字那案沿用既有字樣、不另印,條款和表格都已改,斷言以 `err.getvalue()` 比對。
- 未驗:我沒有跑這些測試,只讀斷言。
- 備註:S1 和 S2 同綁 `t_choice_kill_merge_failed_first`,該測試兩段都有斷言,合理。

**問題 2:全 repo 搜尋被改名或拿掉的東西,結果:除 F1、F3 外沒有殘留。**
- `mg.off`、`_KillMerge.off`、`n_mutants`:`scripts/lumos` 與 `scripts/test_lumos.py` 都沒有。
- 計劃只剩「拿掉」的敘述。前一份計劃第 117 行已改成「參數已拿掉」。
- 舊 `_single` 欄與 on_row 的 `single` 鍵:程式、測試、筆記都已改成 `_ran_solo` / `ran_solo`。剩下的 `single` 都是判法 `judged: single` 的合法用法。
- 「條件不合」「基準」兩個舊原因字串:程式裡沒有。前一份計劃第 124 行的「條件不合」已標〔已被第二段計劃取代〕。
- 測試裡殘留的 `_KillMerge(x, 2)` 帶位置參數建構:全部已改。

**問題 3:`06-代碼審與推送.md` 改後那句跟程式行為一致。**
- 手冊寫的行為:一個壞法與 `--only` 單點也合併;有失敗時先跑合併結果裡紅的;不乾淨照原順序;量不齊就不合併;不合併時印一行原因,時限不夠會講 `--max-seconds`。
- 程式:`_kill_merge_ready` 已拿掉 `n_mutants < 2`;`_kill_merge_off` 在時限不夠時印提示;`_kill_merge_failed_first` 做先紅排序;`_kill_merge_singles` 量不齊回 False。
- 手冊沒提「合併道不足 2 支」和「中斷不印」,屬精度,沒有誤導,不列 finding。

**問題 4:新改筆記行的格式。**
- 計劃的 WHY 四條都有 `[出處:]` 與 `[因:]`,各自指到存在的 `[test:]`。
- guard-kill 和規格閘新改的 WHY 行,`[test:]` 指到的測試函式都存在於 `scripts/test_lumos.py`,逐名各一個定義。
- 我沒跑 `lumos lint`,格式只是人工對照。

**圖譜固定席**:派工詞說這次沒附固定席節點(鏡頭計算超時)。我沒有逐節點判,只對照 patch 內改到的筆記與計劃。上述範圍內沒有發現合約破壞。

**本輪 patch 改到的合約相關敘述**
- guard-kill 兩條 ★INVARIANT★(rc 優先序、`--json` 純度):`--json` 的過濾清單 `"_single"` 改成 `"_ran_solo"`,內部標記不外漏,純度仍成立。
- rc 優先序:修補沒動到它。

最高嚴重度 minor,blocking 0 條。
