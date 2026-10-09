severity: minor

三問都沒有 major。有四條 minor,結構都對,只是命名、錯誤處理和跳脫做法有不一致。

## 1. 分層與依賴方向

方向與鄰居一致,沒有跨層直呼。
- `_lens_trusted_ref` 只用 `_mainline_ref` 和 `_lens_git`,都是鏡頭層既有的底層函式(file: `scripts/lumos:45117`、`scripts/lumos:45140`)。
- 推送前熱路徑 `_pitfall_diff_collect` 沒有載圖譜,只多了 git 查詢。規則原文還是由派工鏡頭附。
- `_arch_target_changed_files` 現在是 `_review_role_changed_files` 的薄包裝(file: `scripts/lumos:26688`)。原本另寫的 numstat 解析已刪,不再有平行實作。
- `_lens_emit_with_extra` 的行為與兩個舊呼叫點一致。
  - 人讀模式與 `rc==0` 才併進 text,和原本 `_cmd_dispatch_lens_impl` 相同。
  - 設計審包裝在 `rc==0` 才有 arch_text,所以併入條件與欄位名也沒變。
- `_dispatch_lens_graph` 把主線檢查改回原本的內嵌寫法,`_lens_base_on_mainline` 與 `_ARCH_TARGET_OFF_MAINLINE` 沒有殘留引用(grep 確認)。
- `_lumos_config_at_ref` 取代的是 `_review_roles` 與 `_arch_targets_at` 內嵌的「先讀、再 cat-file 分辨」。專案裡沒有第三處同樣寫法。`scripts/lumos:45507` 只做 `_json_at_ref(...) or {}`,用途不同。
- 角色段(`scripts/lumos:26731`)呼叫定義在目標架構區塊的 `_lens_trusted_ref`(`scripts/lumos:41151`)。這是往後的依賴,但 `_config_glob_error`(`scripts/lumos:41100`,角色段 `scripts/lumos:26654` 也用)已有同樣先例,所以不另列。

### ARC3-1 `_lens_trusted_ref` 是第四份「主線分叉點」寫法
引句:「r = _lens_git(root, "merge-base", base, ml[1])」
file: `scripts/lumos:44938`(`_push_range_start` 內嵌)
file: `scripts/lumos:47436`(受波及範圍起點內嵌)
file: `scripts/lumos:41521`(`_range_base`)
- 專案已有三份各自內嵌的「跟主線算 merge-base」寫法,失敗時的處置各異,例如有的回空樹、有的回「算不出來」。
- 新函式是第一個抽成函式的,但沒有回頭收斂舊的。
- 它們的失敗處置不同,所以不算重複同功能,只算又多一份。
severity: minor
blocking: 否

## 2. 命名與錯誤處理

### ARC3-2 狀態字串 `git-fail` 與專案慣用的 `git-failed` 不一致
引句:「return None, "git-fail"」
file: `scripts/lumos:38835`(`_DRIFT_M1_UNKNOWN` 用 "git-failed")
file: `scripts/lumos:33169`(`"git-failed" if err == "git"`)
- 專案裡表示 git 本身失敗的狀態字串一律是過去式 `git-failed`。
- 新函式的 `unreadable` 與 `timeout` 兩個詞跟專案一致,只有這個不同。
severity: minor
blocking: 否

### ARC3-3 可信版本算不出來時,四個呼叫端一律靜默當沒宣告,沒有照 r1 COR-7 的「git 失敗要附一句說明」
引句:「ref = _lens_trusted_ref(root, b)」
引句:「_at_rules, _at_warn = _arch_targets_at(repo_root, _at_ref) if _at_ref else ([], [])」
file: `scripts/lumos:41097`、`scripts/lumos:41162`(`_arch_targets_at` 遇 git 失敗會回 `_ARCH_TARGET_GIT_FAIL`)
- `_lens_trusted_ref` 的 None 同時代表「跟主線沒有共同祖先」和「git 失敗或逾時」。
- 四個呼叫端都直接當沒宣告:派工目標段回 `""`,推送前分級回 `([], [])`,`_arch_target_check_lines` 回 `([], [])`,角色段回 `(None, "missing")`。
- 同一功能的 `_arch_targets_at` 已有規矩:git 失敗一定附說明,不當成沒宣告。
- merge-base 逾時時,範圍內的新寫法會悄悄改回比鄰居,和 COR-7 要防的情況相同。
- 修法只需在 None 的 git 失敗路徑補一句警告,結構不用動。
severity: minor
blocking: 否

## 3. 第二種做法

### ARC3-4 同一個威脅在同一份修補裡用了兩種跳脫做法
引句:「res["targets"] = {n: [_kill_esc(f) for f in fs] for n, fs in targets.items()}」
引句:「print(_json_text_escaped(data, indent=None))」
file: `scripts/lumos:13562`(`_json_text_escaped` 的文件字串明寫「無損、結構層」,並說明為什麼不用 `_kill_esc`)
file: `scripts/lumos:16076`(`_kill_esc` 逐字替換成 `\uXXXX` 的文字)
- 兩種做法都是專案既有函式,各有用途,所以不是自創工具。
- 但 pitfalls 的 targets 檔名先被 `_kill_esc` 改成字面的 `\u2028`,再被 `_json_text_escaped` 包一層,等於跳脫兩次。
  - 其他欄位只經 JSON 層跳脫,例如 `files` 和 `tension_candidates` 的檔名。
  - 修補差異裡 `pitfalls-code-loop.md` 新加的段落寫「讀回來的值不變」,對 targets 並不成立,因為它已先被改寫。
- 派工鏡頭的 `_lens_emit_with_extra` 最後仍是 `print(_json.dumps(data, ensure_ascii=False))`。同一份修補不用 `_json_text_escaped`,而是靠事先替換內容來避開 U+2028。
  - 這樣圖譜段 `data["text"]` 如果含檔名,仍會原樣輸出行分隔字元。
  - 這個缺口早就存在,但新抽的唯一輸出點正好是統一修法的位置。
- 結構沒壞,只是 pitfalls 與鏡頭兩邊的做法分了兩套。
severity: minor
blocking: 否

## 其他觀察(不算 finding)

- 共用化對既有呼叫者的行為改變只有兩處,都是這次修補要的:`_review_roles` 改讀分叉點,`_arch_target_changed_files` 改走角色鏡頭那支。
  - 後者的語意有微調:只刪行的檔現在會算進去,簿記或文件檔不算。這一點新的 docstring 已寫明。
- `_lumos_config_at_ref` 裡 `strict` 的條件分支加了「不嚴格時照舊用三個位置參數」的註解,是為了遷就測試裡 `lambda *a: {}` 的替身(`scripts/test_lumos.py:24418`)。寫法略彆扭,但有理由,不列。
- 掛鉤把 `_role` 改名為 `_extra`,和 `_extra_text`(`scripts/hooks/claude/dispatch-lens-hook.py:267`)對齊。不過 `_debug` 字串裡仍寫「(說明/角色卡;0=放行)」,屬純文字。
- 推送前熱路徑現在對每個專案都會多跑 `_mainline_ref`(最多 4 次 rev-parse)加一次 merge-base,即使沒有宣告 arch_targets。沒載圖譜,不屬分層問題。
- `_json_text_escaped` 是逐字元走 `unicodedata`,輸出很大時成本會升高。這是效能問題,不是做法不一致,留給效能檢查。

不對齊共 4 條,其中 major 0 條

總結最嚴重 severity: minor
