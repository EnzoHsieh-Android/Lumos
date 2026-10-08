severity: minor

整份審材沒有擋推的問題,只有四條小問題。第六輪修補的主要效果都有行為證據(FIFO 不再卡住、開跑前檢查與寫入一致、不碰 umask、硬連結不沿用權限、報表標記可逆)。合併段沒有重複項。

## Finding BND7-01
severity: minor
blocking: 否
引句:「os.fchmod(tmp.fileno(), keep_mode)」
file: `scripts/scenario_probe.py:106`
- 具體輸入:輸出位置已有一個自己擁有、單一名字、權限 0600 的檔;umask 022;要寫入的資料大於 Python 3.14 的緩衝區(約 128 KiB)。
- 走到哪一段:`_atomic_write_bytes` 用 `os.open(..., 0o666)` 建暫存檔,權限是 0644。接著 `tmp.write(data)`,最後才 `fchmod(keep_mode)`。
- 壞在哪:大資料在 fchmod 之前就已落盤,而且是 0644。同目錄的其他使用者在這段時間開檔,之後 chmod 也收不回他手上的 fd。這正是第五輪要保護的共用輸出目錄威脅,修補前沒有這個窗口。
- 重現(`/tmp/lumos-seat-work/.../win.py`,在 fchmod 被呼叫時用 fstat 讀暫存檔):
  - 修後 3e149721:`[('0o644', 1000000)] final 0o600`
  - 修前 483df9fe:`[('0o600', 1000000)] final 0o600`
  - 資料小於緩衝區時,fchmod 時 `st_size` 為 0,所以沒有窗口。
- 歸因:有證據的修復回歸。修前暫存檔是 0600,修後改成 0644。
- 修法方向:建暫存檔時直接帶 keep_mode,或在寫入前先 fchmod。

## Finding BND7-02
severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」
file: `scripts/scenario_probe.py:47`
- 具體輸入:`--out /dev/tty` 或 `--history /dev/tty`(沒有控制終端的排程環境),或 macOS 上的 `/dev/klog`、`/dev/pf`(不可寫的字元裝置)。
- 走到哪一段:`_output_target_problem` 對任何字元裝置直接回 None,不看能不能開、能不能寫。
- 壞在哪:開跑前檢查放行,整批模型跑完才在寫入時失敗,失敗類型跟第五輪「`--out /dev/null` 整批跑完才報權限錯」相同。
- 重現(同一支檢查加寫入的矩陣):

| 目標 | 開跑前檢查 | 實際寫入 |
|---|---|---|
| `/dev/tty` 無控制終端,取代與追加 | 放行 | OSError 6 (ENXIO) |
| `/dev/klog` 取代 | 放行 | PermissionError 13 |
| `/dev/pf` 取代 | 放行 | PermissionError 13 |
| `/dev/klog` 追加 | 放行 | PermissionError 13 |
| `/dev/pf` 追加 | 放行 | PermissionError 13 |

- 歸因:有證據的原有漏查。修前 483df9fe 對字元裝置同樣回 None,兩版結果一樣。這次新寫的 docstring 宣稱「一一對應」,但字元裝置這一格並不成立。

## Finding BND7-03
severity: minor
blocking: 否
引句:「# 不可列印字元寫成 ⟦U+XXXX⟧;標記字元 ⟦ 本身也照寫,原文因此一對一還原得回去,字面反斜線不必加倍」
file: `governance/eval/ablation_lumos_first.py:389`
- 具體輸入:`text()` 收到 U+3000、U+00A0 或普通空白。
- 壞在哪:`visible` 把所有 Zs 類空白都換成普通空格,`\r`、`\n` 在前一步也換成空格。三者在報表裡一模一樣,所以「一對一」只對標記部分成立。此外 `U+FE0F` 是可列印的組合字元,會以隱形字元原樣輸出,不會被標記。
- 重現(由 `render_md` 內取出 `visible` 與 `text` 函式實跑):`text('\u3000')`、`text('\u00a0')`、`text(' ')` 全部是 `' '`,碰撞清單為 `[['U+3000','NBSP','space']]`。
- 歸因:Zs 合併行為是有證據的原有漏查,修前 `visible` 也這樣做。新增的是「一對一」這句說法,出現在 3e149721 的註解與 `Systems/ablation-lumos-first.md` 的 WHY。筆記該改成「除空白類與換行外一對一」。
- 其餘輸入都沒問題:空字串、None、數字、`⟦`、`⟧`、字面 `⟦U+001B⟧`(輸出 `⟦U+27E6⟧U+001B⟧`,與真 ESC 的 `⟦U+001B⟧` 不同)、NUL、U+202E、U+FEFF、孤立代理、組合字元、反斜線、Windows 路徑(輸出 `C\:\\Users\\x`,Markdown 渲染後是一個反斜線)、`12:30`、網址、email 都可讀。

## Finding BND7-04
severity: minor
blocking: 否
引句:「# 跑的期間被換成連結或 FIFO 時報錯,不跟過去也不卡住」
file: `scripts/scenario_probe.py:1390`
- 具體輸入:開跑前檢查通過後,模型跑的期間歷史檔位置被換成沒有讀者的 FIFO。
- 壞在哪:這次修補真正新增的是 `O_NONBLOCK`,但沒有測試守它。`O_NOFOLLOW` 在 483df9fe 就已存在,所以新的「換成連結」測試在修前也會綠,不能證明這次修補有效果。
- 重現:
  - 在取出的 3e149721 副本上拿掉 `O_NONBLOCK`,`-k t_probe_boundary` 仍是 177 passed 0 failed。
  - 對照:拿掉 `O_NOFOLLOW`(C2)就翻紅,拿掉 `st_nlink`(C1)也翻紅。
  - 直接對 FIFO 呼叫同一個 `os.open`:修前旗標為 HANG,修後旗標為 `OSError(6)`。
- 歸因:未判定。修補本身有效,只是缺釘。測試只換成連結,沒有換成 FIFO。
- 另外:字元裝置上的 `O_NONBLOCK`、`fstat` 檢查、`set_blocking` 這三處拿掉後測試也都維持綠。它們需要競態或會阻塞的裝置,在這個測試環境造不出來,我不把它們當成可補的缺口。

## 行為表

底下是 macOS、非 root 實跑的結果。「修前」只列結果不同的格子。

**取代模式**

| 目標 | 開跑前檢查 | 實際寫入 | 備註 |
|---|---|---|---|
| 不存在 | 放行 | 成功 | |
| 普通檔、自己的、單一名字 | 放行 | 成功 | 保留權限 |
| 唯讀普通檔 | 拒絕 | PermissionError | 一致 |
| 多名字的普通檔 | 放行 | 成功 | 不沿用權限,原名內容不變 |
| 目錄 | 拒絕 | IsADirectoryError | 一致 |
| 連結(指向目錄、檔、/dev/null、懸空) | 放行 | 成功 | 換成普通檔,不改寫受害檔 |
| FIFO | 放行 | 成功 | 修前寫入卡住 |
| socket | 放行 | 成功 | |
| /dev/null | 放行 | 成功 | |
| /dev/tty 無控制終端 | 放行 | ENXIO | 見 BND7-02 |
| 不可寫字元裝置 | 放行 | PermissionError | 見 BND7-02 |
| block device(`/dev/disk0`) | 拒絕(父目錄不可寫) | PermissionError | 一致 |
| 父目錄不存在 | 拒絕 | 失敗 | 一致 |
| 父目錄唯讀 | 拒絕 | 失敗 | 一致,修前追加模式放行 |
| 父路徑是普通檔 | 拒絕 | 失敗 | 一致,修前檢查直接崩潰 |
| 父目錄是連結 | 放行 | 成功 | |
| 檔名 255 bytes | 放行 | 成功 | |
| 檔名 256 bytes | 拒絕 | ENAMETOOLONG | 一致,修前檢查崩潰 |
| 空字串、`.`、`/` | 拒絕 | 失敗 | 一致 |

**追加模式**

| 目標 | 開跑前檢查 | 實際寫入 | 備註 |
|---|---|---|---|
| 連結 | 拒絕 | ELOOP | 一致 |
| FIFO | 拒絕 | ENXIO | 一致,修前放行 |
| socket | 拒絕 | ENOTSUP | 一致,修前放行 |
| 其餘 | 與取代模式相同 | 與取代模式相同 | |

- `--out ""` 在 main 裡被當成沒指定,開跑前檢查與寫入都跳過,前後一致。
- Linux 專屬的 `/dev/full` 在 macOS 上不存在,所以沒有測。

## 固定席逐條判定
- `codex-harness`、`lumos-cli-lifecycle`、`autonomous-iteration-loop`、`design-loop`、`bound-tests-gate`、`canary-audit`、`lumos-cli-read`:這份審材不破壞它們宣稱的行為或合約。`lumos-cli-lifecycle` 的 re-inject 與 `lumos-cli-read` 的 search 合約這次沒被碰到。
- `測試假綠形態` 的 ★INVARIANT★:新增測試都有「現場成立」前置斷言(硬連結、FIFO、被換成連結)。BND7-04 是缺釘,不是違反合約。
- `codex-harness` 的新 PITFALL 與 WHY 寫的規則跟程式一致,只有字元裝置那格見 BND7-02。
- 超出上限、只列名的那些節點(`guard-kill`、`slim-*`、`授權與歸屬` 等)我沒有逐篇讀。

## 修補三問
1. **原問題的修復效果**
   - FIFO 不卡:取代模式 修前 HANG、修後成功換成普通檔。
   - 檢查與寫入一致:大部分格子,見上表。
   - 不碰 umask:`_atomic_write_bytes` 本體沒有任何 `umask` 呼叫(docstring 不算)。
   - 硬連結:拿掉 `st_nlink == 1` 後測試翻紅,守得住。
   - 標記可逆:字面 `⟦U+001B⟧` 與真 ESC 輸出不同。
   - 歷史檔 FIFO:修前 HANG、修後 ENXIO,但缺測試(BND7-04)。
2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 消融腳本匯入同一份原子寫入:長檔名可寫,權限 0644。
   - 取代模式的普通檔與連結都正常。
   - 追加模式的普通檔正常。
   - 相鄰的新問題只有 BND7-01(暫存檔權限窗口)。
   - 我實跑了 `t_probe_boundary_fifth_round_output_edges`(25 passed)與 `t_probe_boundary_fourth_round_report`(16 passed)。
3. **同一案例在修前、修後**
   - FIFO 取代:HANG 變成成功。
   - 檔名 256 bytes 與父路徑是普通檔:開跑前檢查崩潰變成 rc2 拒絕。
   - /dev/tty:兩版都放行後在寫入時失敗。
   - 空白類折疊:兩版相同。
   - 暫存檔 0600 變成 0644:修後新出現。

**preserve**:連結輸出不改寫受害檔、`/dev/null` 照寫、自己擁有的單一名字檔保留 0640、HTML 轉義與自動連結轉義、`bad.json` 字面,都沒有被修補破壞。

## 合併段
- 四篇 Systems 筆記與 MOC 的開頭欄位都只有一個 `---` 對、沒有重複鍵、`verified_by` 沒有重複項、沒有衝突標記。
- `updated` 與 `self_audit` 取值符合 binding 所說規則,沒有取到比 `updated` 更新的審計。
  - codex-harness:ours 的 2026-10-08 比主線的 2026-10-07 新,self_audit 只有 ours 有。
  - pitfalls-code-loop:updated 取主線的 2026-10-07,self_audit 取 ours 的 2026-10-03(主線是 2026-08-21)。
  - 測試假綠形態:主線版(2026-10-07)為準。
  - lumos-cli-lifecycle:兩邊都是 2026-08-20。
- 連結集合:merge 後的連結等於兩個父版本的聯集,沒有遺失也沒有新增。
- `測試假綠形態` 的 `related` 裡有一項寫成沒有 `[[ ]]` 的 `Systems/review-convergence-eval`,與同清單其他項格式不一致。這項來自主線父版本,不是合併造成的,我不另立一條。
- `MOC/index.md` 兩行都在,沒有重複。
- SKILL.md 的步驟 5、6 採主線版,「試行」那行保留;`reference.md` 有〈修復穩定性試行〉一節,引用的計劃檔都存在。

## 未驗範圍
- root 分支(測試已標明本機沒驗)。
- Linux 專屬行為,例如 `/dev/full`、`/dev/pts`。
- 主線 344 個提交本身(Enzo 已裁定不審)。
- 全套測試。
- 模型呼叫:一律用假替身。
- 字元裝置上開檔取得控制終端(O_NOCTTY)的疑慮:我用 pty 加 setsid 試過,沒有重現(兩版都沒有取得控制終端),所以不立 finding。
- 競態只測了單點注入,沒有測真實並行。
- 驗證筆記宣稱的「第五輪輸出 27、第四輪報表 27」測試數,我沒有逐一比對。
- 實驗目錄已清除。

總結:最高嚴重度 minor
