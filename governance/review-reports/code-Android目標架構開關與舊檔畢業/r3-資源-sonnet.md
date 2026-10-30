severity: clean

## 資源席第 3 輪

本輪沒有 finding。下面是已驗主張的證據、固定席判定,以及三問的回答。

### 逐 hunk 走過的大輸入

**1. 說明行改用 pf_data 的目標檔(`_arch_legacy_check_lines`),確實少叫一次列改動檔**
- 引句:「pf_targets = ((pf_data or {}).get("arch_alignment") or {}).get("targets")」
- 實驗:3000 支舊檔、3000 支改動、畢業 1500 支。單支實驗腳本直接呼叫 `_arch_target_check_lines`,並計算 `_lens_git` 的呼叫次數。
- 結果:

  | 路徑 | 耗時 | `_lens_git` 呼叫數 | 說明行 |
  |---|---|---|---|
  | 帶 pf_data | 0.32 秒 | 10 | 「少了 1500 行,其中 1500 支這次有改動」 |
  | 不帶 pf_data(退路) | 2.43 秒 | 75 | 同上 |

  兩條路徑的輸出一致,代碼審 r2 說的「多 1 秒」已經消掉。
- 退路本身仍會多叫 65 次 git。這條只在 pf_data 沒有 `arch_alignment.targets` 時才走。
- 該情況的條件:分級結果沒有任何目標檔。此時 `keep` 也會是空的,`if keep:` 根本進不去。退路實際走到的機率很低,不構成問題。

**2. `_arch_legacy_doctor_lines` 在函式內轉 NFC**
- 引句:「present = None if tracked is None else {nfc(x) for x in tracked}」
- 成本是一次對 `git ls-files` 結果的線性 set 建立。呼叫端原本就已經在整份走一遍,沒有新增二次方工作,也沒有新的子程序。
- 另一條使用 `files` 的路徑(`hits` 迴圈)沒有受影響。

**3. 拿掉 `not h_warns` 條件(`_arch_legacy_graduation`)**
- 引句:「return legacy, h_legacy, (legacy - h_legacy if h_rules == rules else set())」
- 我讀了 `_arch_targets_config` 的每個 return:有任何警告時 rules 一律回 `[]`。
- git 失敗時回 `[]` 加上 `_ARCH_TARGET_GIT_FAIL`,所以 `h_rules == rules` 只在起點 rules 也是 `[]` 時成立。這種情況下 targets 本來就是空的,`_arch_legacy_apply` 在 `if not targets` 就已經提前返回。
- 結論:拿掉警告條件在行為上等價,沒有放行的新路徑。

### 新測試跑時(`python3.14 scripts/test_lumos.py -k`)
| 測試 | 結果 | 耗時 |
|---|---|---|
| t_arch_target_graduate_same_branch | 18 passed | 54.2 秒(含子程序) |
| t_arch_target_graduate_check_note | 8 passed | 42.1 秒 |
| t_arch_target_legacy_doctor_lines | 9 passed | 10.5 秒 |
| t_arch_target_spec_lens_reads_legacy | 2 passed | 3.5 秒 |

- `-k` 是子字串比對,所以 same_branch 的 18 passed 可能含同前綴的其他測試。這個 54 秒是上界。
- check_note 新增的 L 情境多開一個 repo 加一次 `code-loop check` 子程序。
- 計劃筆記寫的「約 42 秒」對應的是 check_note 那一支。

### 固定席逐條判定
- **`Issues/code-loop守衛main-direct盲區`**:這份 diff 沒有碰 main-direct 守衛的路徑,不破壞。
- **`Systems/lumos-cli-read` ★INVARIANT★(search 排除 superseded)**:diff 不碰 search,不破壞。
- **`Systems/pitfalls-code-loop`(★RISK★)、`reversibility-governance-ledger`(★RISK★)**:說明行仍然只印不擋,`code-loop check` 的 try/except 外殼沒動。不破壞。
- **`Systems/arch-alignment-lens`**:行為方向沒變(畢業判定仍是一支共用函式),不破壞。
- **`Systems/design-loop`(★INVARIANT★ 處置閘第五步)**:diff 沒碰處置閘,不破壞。
- **`Systems/測試假綠形態`(★INVARIANT★ 還原翻紅釘要前置斷言)**:本輪新增測試 H2、L、NFD 各自帶了前置條件。
  - H2:先確認 `_arch_legacy_at` 回 `(set(), "unreadable")`。
  - L:先確認起點沒有清單。
  - NFD:直接傳 `[_ARCH_CAFE_NFD]`,現場成立。
  - 未做還原翻紅。
- **`Systems/guard-kill`(★INVARIANT★)**:不涉及。
- 超出上限只列名的節點:未逐條判。

### 三問
**① 原問題的修復效果有何行為證據?**
- 資源面(少叫一次列改動檔):已量到,10 次對 75 次、0.32 秒對 2.43 秒。
- doctor 的 NFC 問題:測試帶 NFD 輸入通過(「已不存在 0」)。
- H2(清單混非字串元素):測試通過。
- 修前的行為我沒有另跑。作者也標「修前證據沒另存」,所以修前結果記未判定。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 相鄰路徑已走過,仍成立:
  - 少行、多行、宣告有改、沒宣告四種說明照舊,對應 A、E、B、K 都通過。
  - `tracked=None` 仍輸出「算不出」。
  - git 失敗仍輸出「讀不到」。
  - `patch.object` 取代了原本直接賦值 `m._lumos_config_at_ref`,不再污染後續案例。
- `_arch_target_check_lines` 的簽章把 `at_head` 換成 `pf_data`,唯一呼叫端已同步。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- 沒有新發現。

### 未驗範圍
- 修前版本沒有逐案重跑(沒有開 44b0044 的 worktree)。
- 非 NFC 之外的 Unicode 正規化差異(例如 NFKC)。
- 超過 3000 支的規模:耗時隨檔數線性成長。
- `docs/.escape-log.jsonl` 與 `docs/.kill-log.jsonl` 在審查期間出現改動,跑完我的實驗後 `git status` 仍顯示它們。我沒有碰,也不確定是不是測試跑出來的。
- 我的實驗目錄 `/private/tmp/lumos-seat-work/code-Android目標架構開關與舊檔畢業/資源-sonnet` 已刪。

最嚴重等級為 clean
