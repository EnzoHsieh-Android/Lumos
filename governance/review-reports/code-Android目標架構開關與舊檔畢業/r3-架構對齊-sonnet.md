severity: clean

我沒有跑測試,只讀了 `r3-code.patch`,並拿固定提交 1bb9609b 的 `scripts/lumos`、`scripts/test_lumos.py` 對照。判定:新碼跟鄰居的做法一致,沒有第二種做法,也沒有跨層直呼。

## 1. 分層與依賴方向:對齊

- 新增的 `_arch_legacy_at`,讀版本的方式跟鄰居 `_e2e_config_at` 一樣,都走共用的 `_lumos_config_at_ref(root, ref, strict=True, rel=…)`,沒有另寫 git 讀取。
  - 引句:「data, state = _lumos_config_at_ref(root, ref, strict=True, rel=_ARCH_LEGACY_REL)」
  - 對照:`scripts/lumos:40726`(`_e2e_config_at`)、`scripts/lumos:57341`(`_lumos_config_at_ref` 本來就有 `rel` 參數)。回傳 `(資料, 狀態)`,狀態是 ok / missing / unreadable / git-failed,跟 `_arch_targets_at`(`scripts/lumos:57401`)的分岔寫法同一套。
- 畢業判定只有一份 `_arch_legacy_graduation`。它的使用者有四個:`_arch_legacy_apply`(推送前分級、兩條派工鏡頭共用)和 `_arch_legacy_check_lines`(代碼審判定說明行)。這跟 `_arch_target_split` 以及 `_arch_target_check_lines` 共用 `_arch_targets_at` 的分工一致。
- 呼叫方向沒有倒轉:
  - 推送前分級 `_pitfall_diff_collect` 先 `_arch_target_split`,再 `_arch_legacy_apply`,最後交給 `_arch_alignment_hints`。
  - 派工鏡頭 `_dispatch_lens_arch_text` 和設計審 `_dispatch_lens_spec_arch_text` 也是先 split,再 apply,最後交給 `_arch_target_text`。
  - 三處的接法完全一致。設計審傳 `head=None`,所以不畢業,跟「設計審讀 HEAD」的既有說法相符。
  - 引句:「targets = _arch_legacy_apply(root, "HEAD", None, targets, rules)」
- `_arch_legacy_check_lines` 優先重用分級算好的 `pf_data["arch_alignment"]["targets"]`,算不出才自己補算。鄰居 `_arch_target_check_lines` 也吃 `pf_data`,做法相同。
  - 對照:`scripts/lumos:57716` 附近。

## 2. 命名與錯誤處理:對齊

- 命名沿用 `_arch_*` 前綴、`_…_at(root, ref)`、`_…_doctor_lines`、`_…_check_lines`。常數 `_ARCH_LEGACY_REL` 對應 `_ARCH_TARGET_GIT_FAIL` 這類全大寫常數。
- 錯誤處理:
  - 讀不懂時回空集合加狀態,不丟例外;這是 `_arch_targets_at` 的「壞宣告整份不用」做法。
  - git 失敗另外分一種狀態,doctor 也分開說「讀不到」和「讀不懂」,對應 `_ARCH_TARGET_GIT_FAIL` 的寫法。
  - 元素檢查 `all(isinstance(x, str) …)` 把混入非字串的清單歸為 unreadable,新測試 H2 有守住。
- doctor 輸出:
  - 清單行用 `ok(...)`,提醒行用 `warn_soft(..., "…要看(不擋):")`,跟緊鄰的目標架構宣告段完全同形。
  - 對照:`scripts/lumos:2287`、`scripts/lumos:2289`。
  - 引句:「warn_soft(_alp, f"舊檔清單有 {len(_alp)} 處要看(不擋):")」
  - 外層的 try/except 兜底也沿用同一個,出錯時整組換成空清單,並多一句提醒。
- `_arch_target_doctor_lines` 回傳從 2 項擴成 4 項。我查過全 repo,沒有測試直接呼叫它,只有 `run_doctor` 一個呼叫點,而且已同步改好。
- 測試的寫法跟鄰居一樣:
  - 函式內 `from unittest.mock import patch`、`patch.object(m, "_lumos_config_at_ref", lambda *a, **k: (None, "git-failed"))`,逐字同於 `scripts/test_lumos.py:15887`、`scripts/test_lumos.py:15898`。
  - 夾具用既有的 `_arch_target_repo`、`_arch_pitfalls`、`_arch_lens`。
  - docstring 的「翻紅釘」寫法和 `t_arch_target_*` 命名也是延續既有慣例。

## 3. 第二種做法:對齊(沒有引入)

- 舊檔清單另放獨立檔 `.lumos/arch-legacy.json`,而不是在 `arch_targets` 加欄位。計劃與 `Systems/arch-alignment-lens` 都記了理由:宣告形狀只收兩欄,舊版 lumos 讀到多一欄會整份不用。獨立檔讀取走的仍是共用的 `_lumos_config_at_ref`,所以這是同一套讀法,不是第二種。
- 目標節點的規則仍沿用既有的 RULE 摘要行,沒有另立語法。
- ⚠ 一個觀察,我不判成不對齊。`_arch_legacy_doctor_lines` 的清單行用「(清單行, 提醒行)」兩元組,並塞進 `_arch_target_doctor_lines` 的 4 元組裡,讓兩段共用一次 `git ls-files`。這比鄰居的 2 元組多出一層,但回傳形狀跟鄰居同款,而且 docstring 寫明了共用 ls-files 的理由,不是新做法。

不對齊共 0 條,其中 major 0 條
