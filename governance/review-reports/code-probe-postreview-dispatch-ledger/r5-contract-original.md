severity: major

審查範圍:修前 05e87b54 → 修後 4d765d5c。兩版用 `git archive` 取到 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/合約圖譜5-sonnet/{before,after,r1..r7}`,只在副本裡還原和變異。

## Finding CTR5-01
severity: major
blocking: 是
引句:「`t_confirm_tty_unit` 在修補前穩定走到第 2 階 pty 成功路徑後收到 SIGHUP，測試 runner 以 129 結束」
file: `scripts/test_lumos.py`(測試 `t_confirm_tty_unit`,diff 沒動它);`scripts/lumos:18879`(`os.open(tty_path, os.O_RDWR | getattr(os, "O_NOCTTY", 0))`)
- 輸入:把 `O_NOCTTY` 拿掉(`r4` 副本),在一般 shell 裡跑 `python3.14 scripts/test_lumos.py -k t_confirm_tty_unit`。
- 結果:6 passed, 0 failed。這顆釘子對修補沒有殺傷力。
- 只有 runner 是「無控制終端的 session leader」時才翻紅。我用 `os.setsid()` 再 exec 重現:
  - `r4` 副本(拿掉 O_NOCTTY):`rc=129`,沒有任何輸出。
  - `after` 副本:`rc=0`。
- 壞在哪:Systems/測試假綠形態的 ★INVARIANT★ 要求修 bug 的還原翻紅釘必須配「現場成立」前置斷言。這支測試沒有,也沒有自己 setsid 或 fork 出 leader 環境。
  - 修補只有在碰巧由 session leader 啟動時才被守住。
  - 新增的 `Verification/TTY確認不取得控制終端驗證` 寫「修補前穩定走到…SIGHUP」,但 `valid_under` 沒寫「必須由無控制終端的 session leader 啟動」。
  - `lumos-cli-lifecycle` 的 `[防回歸:t_confirm_tty_unit]` 因此是條件式宣稱。
- 歸因:有證據的原有漏查。修補本身正確,修前(沒有 O_NOCTTY)在 setsid 下同樣 rc129,修後 rc0。缺的是測試現場。

## Finding CTR5-02
severity: minor
blocking: 否
引句:「mode = stat.S_IMODE(old.st_mode) & 0o666」
file: `scripts/scenario_probe.py:27`
- 輸入:`--out` 指向不存在的新檔,umask 022。
  - 修前 `Path.write_text` 建出 0644。
  - 修後 `NamedTemporaryFile` 建暫存檔,新檔 `mode is None` 沒有 fchmod,結果是 0600。實測 `_atomic_write_text("new.json","x")` 得 `0o600`,而 `Path.write_text` 得 `0o644`。
- 既有普通檔的權限位元有保留(實測 0664 保留),所以只有新建路徑退化。這是對 CLI 輸出權限的無聲改動。
- 控制缺口:把 `os.fchmod` 那段拿掉(`r6`),`t_probe_boundary_fifth_round_output_contracts` 仍 2 passed。`r5-behavior-cases.json` 自己承認權限保留「目前沒有案例」,修後仍沒補。
- 附帶:同樣邏輯與 `governance/eval/ablation_lumos_first.py:25` 的 `_atomic_write_bytes` 幾乎逐行複製。兩份實作之後可能漂移,新檔 0600 在 ablation 側是既有行為。
- 歸因:新退化的新建檔模式是有證據的修復回歸(修前 0644、修後 0600,有兩版命令);權限未被測試守住是有證據的原有漏查。

## Finding CTR5-03
severity: minor
blocking: 否
引句:「delay = min(300, a.wait_on_limit - waited)」
file: `scripts/scenario_probe.py:1255`
- 輸入:把 `min(300, …)` 換成 `a.wait_on_limit - waited`(`r7`,等於一次睡滿預算)。
- 結果:`t_probe_boundary_persistent_ledger_stop_contracts` 仍 5 passed。
- 原因:唯一的等待案例用 `--wait-on-limit 1`,「預算大於 300 時仍每次只睡 300 秒」沒有任何案例。`r5-behavior-cases.json` 的 preserve 欄已自承。
- 守衛條件 `waited < a.wait_on_limit` 保證 `delay > 0`,所以不會有 `sleep(負數)`。
- 歸因:有證據的原有漏查。修前 `time.sleep(300)` 對這個案例同樣無測試。

## Finding CTR5-04
severity: minor
blocking: 否
引句:「`--out` 指向既有符號連結時,不得改寫連結指向的檔」
(這行逐字出自 `r5-behavior-cases.json`;patch 內相近原文為「候選輸出經真 main 寫入時只能替換連結本身，不得改到連結指向的檔」。)
file: `scripts/scenario_probe.py:1322`(`with open(a.history, "a", encoding="utf-8") as hf:`)
- 同族漏掃:`--history` 仍用 `open(...,"a")` 跟隨符號連結。可寫目錄裡的相鄰程序把 `history.jsonl` 換成指向別檔的連結,探針會把 JSON 行追加到那個檔。
- `--out` 的修補沒有涵蓋這條。這是推論,沒有現場重現,所以降為 minor。
- 歸因:未判定。修前修後兩版同一行,都存在。

## Finding CTR5-05
severity: minor
blocking: 否
引句:「本輪是第三輪上限後由使用者裁決開出的唯一額外輪。依代碼審迴圈規則，到頂且處置閘未過須再次由人裁決；未取得裁決前只允許保存卷證與圖譜，不開第五輪、不宣告 code-loop pass、不推送此分支。」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳第四輪代碼審停點.md`(審材新增檔,「下一個入口」節)
- 內部不一致:同一份審材另有 `持久用量帳第五輪修補驗證`(status: pass),Projects 與 Systems 筆記也寫「第五輪採…」。
- 停點筆記的 `revalidate_when`(使用者裁決再開修補輪後)已經發生,筆記仍是 pending,仍告訴接手者不要開第五輪。三個月後接手的人讀到兩個互斥入口,筆記裡沒有「使用者已裁決」的出處。
- 第五輪 Verification 的 `self_audit: pending-fifth-round-review` 是佔位值,且 status 已是 pass。
- 歸因:有證據的修復回歸(兩篇筆記都是本次 diff 新增,互相矛盾)。

## 固定席逐條判定
| 節點 | 判定 |
|---|---|
| codex-harness | 新 PITFALL 與程式相符:同目錄暫存加 `os.replace`、等待取剩餘預算。WHY 說 `verified_by` 是 pending 的停點,不等於分支通過,成立。PITFALL 缺 `[出處:][根因:]` 鍵,但同檔既有 PITFALL 也這樣寫,`lumos lint` 0 error,不新增違規。 |
| lumos-cli-lifecycle ★INVARIANT★ re-inject | 不影響:diff 只動 `_confirm_tty` 的一個 open 旗標,不碰 sentinel 與注入邏輯。`[防回歸:t_confirm_tty_unit]` 見 CTR5-01。 |
| lumos-cli-read ★INVARIANT★ | 不影響:`search` 過濾邏輯沒動。 |
| design-loop ★INVARIANT★ | 不影響:處置閘規則沒動。 |
| 測試假綠形態 ★INVARIANT★ | 受影響,見 CTR5-01。其餘新測試都有現場成立斷言:符號連結先 `symlink_to`、claim 前先斷言真 claim 最後一格、`len(calls)==2`。 |
| bound-tests-gate | 不影響:沒動閘邏輯。 |
| guard-kill | 不影響:沒動 guard kill 流程;rc 優先序與 JSON 純度不在這份 diff。 |
| 授權與歸屬 | 不影響:沒新增程式檔,`scripts/lumos` 檔頭與 SPDX 區塊沒動。 |

## 還原翻紅結果表
| # | 還原 | 測試 | 結果 |
|---|---|---|---|
| ① | `_atomic_write_text` 換回 `write_text`(`r1`) | `t_probe_boundary_fifth_round_output_contracts` | 0 passed, 2 failed(「輸出位置改成工具自己的普通 JSON 檔」✗,另一條也紅) |
| ② | `delay` 換回 300(`r2`) | `t_probe_boundary_persistent_ledger_stop_contracts` | 4 passed, 1 failed:`✗ 等待總量不超過 --wait-on-limit (0, 2, [call(300)])` |
| ③ | `text()` 換回舊版(`r3`) | `t_probe_boundary_fourth_round_report_and_provenance` | 8 passed, 2 failed(Markdown 字面與控制字元兩條皆紅) |
| ④ | 拿掉 `O_NOCTTY`(`r4`) | `t_confirm_tty_unit` | 一般 shell 下 6 passed,不翻紅;`setsid` 下 `rc=129`;修後同環境 `rc=0` |
| ⑤(補) | 重加結果檔硬限(`r5`):`runs_in_window` 達上限就令 `remaining=0` | `test_runs_in_window_counts_recent_only` | FAILED:`('with','zz','skip 持久窗口已達 3 場上限…')`,修後版本 OK,測試有殺傷力 |

測試沒有重抄實作,走真的 `main` 與 `run_job`;但 ③ 的檢查只比對字串是否出現,不驗 Markdown 實際渲染。

## 修補三問
1. 原問題的修復效果:符號連結覆寫、`sleep(300)` 放大、Markdown 與控制字元三項,在修後有行為證據,還原後會翻紅(表 ①②③)。TTY 的 SIGHUP 只在 setsid 環境有證據,見 CTR5-01。
2. 修補處的正常、錯誤、相鄰路徑:
   - `--out` 既有普通檔的權限保留(實測 0664);符號連結被取代;不存在的新檔改成 0600,見 CTR5-02。
   - `wait_on_limit - waited` 在守衛下恆正。
   - `text()` 把全形空白 U+3000 與 ZWJ 轉成 `\uXXXX`。這是我從 `str.isprintable` 的行為推論,沒有重現,也沒有現行題號含這些字元,所以不標 finding。
   - `--history` 相鄰路徑仍跟隨連結,見 CTR5-04。
3. 新發現案例在修前、修後的結果:
   - CTR5-02:修前 0644,修後 0600。
   - CTR5-03:兩版同樣沒有 ≥300 的案例。
   - CTR5-04:兩版相同。
   - CTR5-01:兩版 rc 差異只在 setsid 下。

## 未驗範圍
- 沒跑全套測試、沒跑真模型。
- 沒驗 Windows 與沒有 `O_NOCTTY` 的平台。
- `Verification/持久用量帳第五輪修補驗證` 裡的「143 passed / 1 failed」等歷史數字沒有逐項重跑。
- 沒讀 r1–r4 檔,也沒驗 `review-reports` 內被筆記引用的檔案是否存在。
- 圖譜 lint:新增與修改的 Projects/Verification 筆記 0 問題;Systems 三篇 0 error,about_code 警告來自我取出的副本,不當 finding。

max severity: major
