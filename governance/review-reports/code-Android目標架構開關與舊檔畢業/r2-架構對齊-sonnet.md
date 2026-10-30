severity: minor

**1. 分層與依賴方向:對齊**
- 新增的 `_arch_legacy_at`、`_arch_legacy_graduation`、`_arch_legacy_apply`、`_arch_legacy_doctor_lines`、`_arch_legacy_check_lines` 都放在 `_arch_targets_at` 之後,和鄰居同一帶。它們的呼叫鏈和鄰居一樣:先讀設定,再切分,最後出文字。
- 讀版本走 `_lumos_config_at_ref(root, ref, strict=True, rel=…)`,對照 `scripts/lumos:57426`(patch 內 `_arch_legacy_at`)和既有的 `scripts/lumos:40726`(macrobench 同樣傳 `rel=`)。沒有另寫一套讀設定檔的做法。
- 畢業判定收斂成 `_arch_legacy_graduation` 一份。推送前分級(`_pitfall_diff_collect`)、兩條派工鏡頭(`_dispatch_lens_arch_text`、`_dispatch_lens_spec_arch_text`)和 `_arch_legacy_check_lines` 都呼叫它,沒有各算各的,也沒有跨層直呼。
- 改動檔清單沿用 `_arch_target_changed_files`、`_arch_target_split`(`scripts/lumos:57713` 一帶的 `_arch_target_check_lines` 同樣用法)。
- doctor 的 `ls-files` 只叫一次,兩段共用。`_arch_legacy_doctor_lines(root, rules, tracked)` 回 (清單行, 提醒行),和 `_arch_target_doctor_lines` 同形。

**2. 命名與錯誤處理:大致對齊,有一條不一致**
- 命名一致:模組常數 `_ARCH_LEGACY_REL`、`_arch_legacy_*` 前綴、狀態字串 `ok/missing/unreadable/git-failed`,都沿用 `_lumos_config_at_ref` 的詞彙。
- doctor 輸出:`ok(...)` 加 `warn_soft(..., "…處要看(不擋):")` 與目標架構宣告段同寫法。例外降級也沿用同一句式「檢查出錯(…),這次略過」。
- 派工鏡頭兩處的 `try/except` 外層沒動,新增的 `_arch_legacy_apply` 在 try 之內,與鄰居一致。
- 不一致的是測試裡覆寫內部函式的方式,見下方 finding。

**3. 第二種做法:發現 1 條(minor)**
- 修補後的 `t_arch_target_legacy_doctor_lines` 用 `m._lumos_config_at_ref = lambda …` 直接賦值覆寫內部函式,沒有 `with` 範圍,也沒有還原。
- 同一組 t_arch_target_* 測試和同檔其他地方的做法不同:
  - `with patch.object(m, "_lens_git", no_mb)` 在 `scripts/test_lumos.py:15987`。
  - `with patch.object(m, "_lens_git", flaky)` 在 `scripts/test_lumos.py:16134`。
  - `with patch.object(m, "_arch_target_split", boom)` 在 `scripts/test_lumos.py:16139`。
  - 同檔 `scripts/test_lumos.py:11315` 的註解明寫 patch.object 是本檔通篇的猴子補丁寫法,2026-09-07 r1 架構席也為此判過 minor。
- 同檔另有 `scripts/test_lumos.py:14962` 和 `:21612` 這類直接賦值,但它們都有 `orig`/`real` 還原。
- 結構沒錯:這裡的 `m` 是 `_load_lumos_module()` 新載入的模組,不會漏到別的測試。只是補丁寫法與鄰居不一致,所以是 minor。

severity: minor
blocking: 否
引句:「m._lumos_config_at_ref = lambda *a, **k: (None, "git-failed")」

**不在 finding 內、交編排者參考:**
- doctor 的舊檔清單檢查併進 `_arch_target_doctor_lines` 的 4 元組後,舊檔清單這段若出例外,會被外層 except 說成「目標架構宣告檢查出錯」,宣告段和清單段一起略過。這是形狀選擇(外層已有降級一行),不是第二套做法,所以不列為不對齊。
- 修補差異裡 `skills/lumos-design-loop/templates.md` 和計劃筆記只是補文字,沒有結構面的問題。

不對齊共 1 條,其中 major 0 條
