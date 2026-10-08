severity: minor

## Finding BND8-01
severity: minor
blocking: 否
引句:「單檔 CLI,這裡不為一組常數載入整支,改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」
file: `governance/eval/ablation_lumos_first.py:385`
- 輸入:把報表的 `_SPECIAL_CATS` 改得跟主程式 `_PATH_SPECIAL_CATS` 不同。例如拿掉 Zl、Zp、Cs,或加上 Co。
- 走到哪一段:註解說「由測試核對兩邊寫法一致」,實際只有一個取樣字串 `"\u202e\ufeff\U000e0001\u3000\u00a0x"` 對 `_kill_esc` 的輸出。取樣裡只有 Cf、Zs 和一般字元,沒有 Zl、Zp、Cs,Cc 也沒涵蓋到。測試也沒有直接比兩個類別集合。
- 壞在哪:報表和主程式的類別集合一旦分岔,測試照綠。註解宣稱的漂移守衛不存在。這也違反「測試假綠形態」那條合約:還原後現場走不到被測分支。
- 重現(在 e5ce8675 取出的目錄逐一改 `_SPECIAL_CATS`,再跑 `python3.14 scripts/test_lumos.py -k probe_boundary_fourth_round_report`):
  - `("Cc","Cf","Zp","Cs")`:15 passed, 0 failed
  - `("Cc","Cf","Zl","Zp")`:15 passed, 0 failed
  - `("Cc","Cf")`:15 passed, 0 failed
  - `(…,"Cs","Co")`:15 passed, 0 failed
- 修前 67b1dea2 沒有這個常數,也沒有這句承諾,所以是這次新增的說明與守衛不符。
- 歸因:有證據的修復回歸。承諾的守衛是修補自己加的註解和測試,但缺口沒補上。

## Finding BND8-02
severity: minor
blocking: 否
引句:「raw = str(x).replace("\r", " ").replace("\n", " ")」
file: `governance/eval/ablation_lumos_first.py:398`
- 輸入:meta 欄位是 `"a\nb"`、`"a\rb"` 或 `"a b"`。
- 走到哪一段:`text()` 先把 CR、LF 換成空格,才呼叫 `visible()`。
- 壞在哪:`_kill_esc("a\nb")` 輸出 `a\u000ab`,報表輸出 `a b`,而且和真空格 `a b` 一樣。我對同一批輸入逐字比對:空字串、None、數字、各類控制字元、雙向覆寫、零寬、U+2028/2029、代理、非 BMP 格式字元、全形空白、NBSP、反斜線、Windows 路徑、時間、網址,只有 `\n` 和 `\r` 兩項不同。
- 修補把家筆記改成「跟 `_kill_esc` 同一套」,並用「換行與空白類仍會折成空白,一對一並不成立」當理由否決舊做法。現行做法對換行有一樣的缺點,筆記和程式註解都沒提。
- 重現:`git -C <repo> show 67b1dea2:governance/eval/ablation_lumos_first.py` 與 `e5ce8675` 版的第 398 行相同,而 `_kill_esc` 取自 `e5ce8675:scripts/lumos:16067`。
- 歸因:有證據的原有漏查。這一行修前就存在,第七輪把它說成同一套,但沒涵蓋換行。

## 行為表(macOS、非 root,實跑 `_output_target_problem`、`_atomic_write_text`、`_open_history`)

「開跑前」是 `_output_target_problem` 的結果,「實際」是實際寫入。

| 目標 | 取代:開跑前 / 實際 | 追加:開跑前 / 實際 |
|---|---|---|
| 不存在 | 過 / 成功 | 過 / 成功 |
| 自己的 0600、0640、0644 | 過 / 成功,權限不變 | 過 / 成功 |
| 0200 | 過 / 成功,權限不變 | 過 / 成功 |
| 0400、0000 | 擋(不可寫)/ PermissionError | 擋 / PermissionError |
| 多名字普通檔 | 過 / 成功 | 擋 / OSError |
| 目錄 | 擋 / 錯 | 擋 / 錯 |
| 符號連結(含懸空) | 過 / 換成普通檔,受害檔不變 | 擋 / ELOOP |
| FIFO 沒人讀 | 過 / 換成普通檔,不卡 | 擋 / ENXIO |
| socket | 過 / 換成普通檔 | 擋 / 錯 |
| /dev/null、/dev/zero | 過 / 成功 | 過 / 成功 |
| /dev/tty 無控制終端 | 擋(Device not configured)/ 同錯 | 擋 / 同錯 |
| 父目錄不存在、是普通檔、唯讀 | 擋 / 錯 | 擋 / 錯 |
| 檔名 255 bytes | 過 / 成功 | 過 / 成功 |
| 檔名 256 bytes | 擋 / 檔名過長 | 擋 / 檔名過長 |
| 空字串、`.`、`/` | 擋(是目錄)| 擋 / 錯 |

- 0200 和 0400:
  - 0400 的自有檔在開跑前就被 `os.access` 擋下,走不到暫存檔。
  - keep_mode 只會在 0200 這類可寫檔出現。
  - 暫存檔以 `os.open(...,mode)` 建立,回傳的 fd 本來就可寫,fchmod 前能寫入。
  - 我沒用 root 驗 keep_mode 為 0o000 或 0o400 的情況。
- 沒驗到的格子:
  - 有控制終端的 /dev/tty。
  - 有讀者的 FIFO 的實際追加。我用測試看到它報錯且不洩漏。
  - 沒寫入權的裝置。
  - Linux、root。
- 報表 `visible()` 對 `_kill_esc`:除了 BND8-02 的 CR、LF 之外逐字一致。Markdown 跳脫後 `\u001b` 變 `\\u001b`,Markdown 渲染成單一反斜線可讀,終端原文是雙反斜線。字面 `\u001b` 與真 ESC 呈現相同,筆記的 [代價:] 已寫明。

## 固定席逐條判定

我沒有跑 `lumos impact` 取原文,以下依 hook 摘要和審材判斷。

- codex-harness:新增的 PITFALL 與 WHY 與程式一致。`_open_char_device`、`_open_history`、100 次上限、先建後 fchmod 都有對應程式。未發現破壞合約。
- 測試假綠形態 ★INVARIANT★:這條要求「還原翻紅釘」必須配前置斷言證明現場成立。
  - 新的 0600 暫存檔測試有「現場成立:真的建了暫存檔」。
  - 字元裝置換位測試和 session 測試也都有現場成立的斷言。
  - 唯一違反的是 BND8-01:類別一致的守衛是空的。
- autonomous-iteration-loop:審材沒有改它的合約。
- lumos-cli-lifecycle:`t_confirm_tty_no_ctty_session_survives` 存在(`scripts/test_lumos.py:10255`),`_confirm_tty` 帶 `O_NOCTTY`(`scripts/lumos:23908`)。更新後的 PITFALL 與程式相符。
- lumos-cli-read、design-loop、bound-tests-gate、canary-audit:審材沒有碰它們的合約行為。

## 修補三問

- 原問題的修復效果:
  - `t_probe_boundary_char_device_session` 跑 4 passed。
  - `fifth_round_output_edges` 跑 37 passed。
  - `fourth_round_report` 跑 15 passed。
  - 這些是修後的結果。我沒有在修前版重跑,所以修前紅燈沒有自己的證據。
- 修補處的正常、錯誤與相鄰路徑:
  - 普通檔、/dev/null、FIFO 換普通檔、連結不跟隨、多名字歷史檔,以上都成立。
  - 100 次上限的 for-else 讀碼正確。
  - 唯一偏差是 BND8-01、BND8-02。
- 新發現案例修前、修後:
  - BND8-02:修前、修後都把 LF 折成空格,結果相同。
  - BND8-01:修前沒有這句承諾,修後承諾存在,但守衛不存在。

## 未驗範圍

- Windows 與 Linux。`os.O_NONBLOCK` 在 `_open_char_device` 和 `_open_history` 沒有用 `getattr` 保護,而 `_NOFOLLOW` 和 `_NOCTTY` 有。我沒驗,所以不列為 finding。
- root,以及真實序列埠、磁帶等會因開關而有副作用的裝置。開跑前試開會多一次 open 和 close,這個副作用我沒驗。
- 全套測試。
- 摘要寫的「424 passed」和 mutation log,我沒有核對。
- 實驗目錄已清除。

總結:最高嚴重度 minor
