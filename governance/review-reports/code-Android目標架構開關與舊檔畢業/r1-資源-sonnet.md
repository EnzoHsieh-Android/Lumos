severity: minor

我沒找到 major 或 blocker。四個鏡頭問題裡,逾時、孤兒子程序、二次方工作都沒有具體失敗場景,只有兩條 minor。

## Findings

### 1. 新增四支測試約加 90 秒,佔全套約 8 分鐘的近兩成
severity: minor
blocking: 否
file: `scripts/test_lumos.py`(`t_arch_target_graduate_same_branch` 與 `t_arch_target_graduate_check_note`)
引句:「d, arch = run_case(both, lambda d, g, w: w(".lumos/arch-legacy.json", _arch_legacy(_ARCH_HELPER)))」

- **走到哪一行**:`t_arch_target_graduate_same_branch` 的 A、B、C、D、E、F、H 共 7 次 `run_case`,每次都建一個臨時 git repo、提交兩次,再各起一個 `lumos pitfalls` 子程序。加上 G 又多建一個 repo,A、B 還各多起一個 `dispatch-lens` 子程序。
- **量測**:`python3.14 scripts/test_lumos.py -k <名>` 實測,用 `-k` 子字串比對,各支分開跑。

| 測試 | 實測秒數 | 備註 |
|---|---|---|
| `t_arch_target_graduate_same_branch` | 53.3 | sys 27 秒 |
| `t_arch_target_graduate_check_note` | 25.2 | |
| `t_arch_target_legacy_doctor_lines` | 8.6 | |
| `t_arch_target_spec_lens_reads_legacy` | 3.6 | |
| 合計 | 約 90 | |

- **對照**:既有的 `t_arch_target_lens_trusts_mainline_base_only` 是 15 秒。
- **影響**:不會翻紅,只是推送前閘拉長。
- **未能重現**:它不構成錯誤,只是量測數字。

### 2. doctor 的 `ls-files` 逾時時,摘要會把整份清單報成「已不存在」
severity: minor
blocking: 否
file: `scripts/lumos`,diff 內 `_arch_legacy_doctor_line`;`_lens_git` 預設逾時 20 秒,見 `scripts/lumos:62331`
引句:「tracked = {nfc(x) for x in (r.stdout.split("\0") if r is not None and r.returncode == 0 else []) if x}」

- **走到哪一行**:`_lens_git(root, "ls-files", "-z")` 逾時時回 `None`,`tracked` 變空集合。下一行 `gone = sum(1 for f in legacy if f not in tracked)` 就等於 `len(legacy)`。
- **結果**:例如清單 5000 行、巨型 repo 或慢機器上 `ls-files` 超過 20 秒,doctor 會印「已不存在 5000」,全是假的。
- **影響範圍**:只影響提醒文字,doctor 本來就只提醒、不擋。既有的 `_arch_target_doctor_lines` 也有同樣寫法(命中 0 支)。
- **未能重現**:要把 git 拖過 20 秒才看得到,我沒有造出來。

## 其他鏡頭逐項判定(都不構成 finding)

- **派工鏡頭 5 秒預算**:新加的 `_arch_legacy_apply` 在 `_arch_target_lens_split` 之後呼叫,不受預算約束。
  - 它多出的成本是固定幾次 git。有清單時最多約 6 次:讀 ref 版清單 2 次,head 版宣告與 head 版清單各 2 次。沒清單時 2 次就短路。
  - 每次 git 在 `_json_at_ref` 內有 10 秒上限,其餘 `cat-file` 走 `_lens_git` 預設 20 秒。正常是毫秒級。
  - 清單比對本身是集合查詢,和檔數成線性。
- **清單沒有條數上限**:實測 200 萬行(70MB)的 JSON,載入加 NFC 正規化 0.5 秒,峰值記憶體約 470MB。
  - 讀到 head 版清單時沒有大小檢查。作者可在分支上提交超大清單,但 `_arch_targets_at(head)` 對 `config.json` 本來就是同一種暴露,不是新增的面。
  - 超深巢狀由 `_json_at_ref` 內建的 `RecursionError` 處理接住,形狀不對則被判 unreadable。
- **doctor 的比對成本**:清單 5000 支、規則 500 條、全部不命中,fnmatch 約 1 秒。`fnmatch` 內部有快取,不會每次重編正規式。每個 doctor 另外多一次 `ls-files`,既有宣告檢查也在做同樣的事。
- **code-loop check 多叫的 git**:`_arch_legacy_check_lines` 多 2 次清單讀取。
  - 清單少了行且宣告沒改時,另多 1 次 `_arch_target_changed_files` 的 git diff 與一次不帶期限的比對,結果和 pitfalls 已算的重複。
  - 這是重複工作,但沒有放大到會出錯的輸入。
- **子程序殘留**:全部走 `_lens_git`。它用 `subprocess.run` 加 `timeout`,逾時由 `subprocess.run` 收掉子程序,例外被接住。沒有新增孤兒來源。

## 固定席逐條

- `Issues/code-loop守衛main-direct盲區`:不影響。diff 沒碰 main-direct 守衛,只在已算好的 base、head 上多讀清單。
- `Systems/lumos-cli-read`(★INVARIANT★ search 排除 superseded):不影響。diff 不碰 `search`。
- `Systems/pitfalls-code-loop`(★RISK★):不影響。分級仍由 `_arch_target_split` 先算,再由 `_arch_legacy_apply` 扣掉清單上的檔。清單讀不到時是「全照目標」,審得更多而不是更少。
- `Systems/arch-alignment-lens`:不影響。它的筆記沒寫預算或「只讀起點版」的條文,diff 本身有改它。
- `Systems/design-loop`(處置閘第五步):不影響,設計審路徑只改了鏡頭文字的產生。
- `Systems/guard-kill`(rc 優先序、`--json` 純度):不影響,diff 不碰 guard kill。
- `Systems/測試假綠形態`(還原翻紅釘須配前置斷言):部分相關。新測試的 A、D、E 有前置斷言證明現場成立,沒發現假綠形態。
- `Systems/reversibility-governance-ledger`(★RISK★):不影響。

最嚴重等級為 minor
