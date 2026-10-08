severity: minor

## Finding SEC8-01
severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK」
file: `scripts/scenario_probe.py:_open_history`(r8-snapshot.patch 中新增的 `_open_history` 與 `_output_target_problem` 的追加分支)
- 誰:對 `--history` 所在目錄有寫入權的另一個本機使用者。
- 從哪:該目錄是共用的,例如 /tmp,或別人可寫的 governance 目錄。
- 送什麼:他事先在歷史檔路徑建好一個自己擁有的普通檔,只有一個名字,權限 0666。
- 拿到什麼:`_open_history` 與開跑前檢查只看「普通檔、nlink==1、可寫」,不看檔案擁有者(不像 `_atomic_write_bytes` 的 `keep_mode` 有比 `st_uid == _euid()`)。受害者的探針會把 history_record 追加進攻擊者擁有的檔案。攻擊者可以讀到紀錄,也可以事後改寫來污染歷史。
- 重現:我在 `/tmp/lumos-seat-work/.../資安-sonnet/` 的實驗目錄裡預建 0666 檔,`_output_target_problem(h, replace=False)` 回 `None`,`_open_history` 成功追加。這個實驗用同一個使用者做,只能證明程式沒有檢查擁有者,證明不了跨使用者。
- 歸因:推論。
  - 紀錄內容是通過數、種子、耗時,不含密鑰,所以外洩價值低。
  - Linux 開了 `fs.protected_regular` 時,在 sticky 目錄用 O_CREAT 開別人擁有的檔會被核心擋下。macOS 沒有這個保護。
  - 這是修前就有的行為,r8 的修補沒有讓它更糟。
  - 建議在 `_open_history` 加 `st.st_uid == os.geteuid()`(或放寬到 root),追加模式的開跑前檢查也加。

## 逐類結論
1. 不可信輸入流到危險操作:除上面 SEC8-01 外已看,無。
   - 一般使用者不能 mknod 字元裝置,硬連結到 /dev/tty 也受 protected_hardlinks 和跨檔案系統限制。
   - 開跑前試開用 `O_NOFOLLOW`,檢查後被換成連結只會得到 ELOOP。
   - 被換成 FIFO 時,有人讀則 fstat 後關閉、讀的人拿不到資料;沒人讀則 ENXIO。
   - 歷史檔新建後到 fstat 之間,fd 指向的就是自己剛建的 inode,攻擊者無法插入。
   - 暫存檔以 `keep_mode`(再被 umask 收窄)建立,`fchmod` 在寫資料之前,內容不會先落在比原檔寬的檔裡。
   - 暫存檔名有隨機成分且用 O_EXCL 加 O_NOFOLLOW,無法預佔。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看,無。
   - 實測沿用 0600 的檔,寫完仍是 0600。
   - 新建檔照 umask,沒有比修前寬。
   - 歷史檔仍是 0o666 加 umask,與修前相同。
4. 加密與傳輸:已看,無。
5. 執行邊界:已看,無可利用的洞。
   - 控制、格式、行段分隔、代理字元都變成可見的 `\uXXXX`,之後 `\` 被加倍,`html.escape` 與 `[]()!:@~` 的跳脫維持不變,終端序列、Markdown 連結、圖片、HTML 都進不來。
   - 字面 `\u001b` 與真 ESC 渲染後同樣是 `\\u001b`,外部文字可以偽造「某題有控制字元」的外觀。這只影響報表可讀性,攻擊路徑寫不全,記為推論,不算獨立 finding。
   - 新測試只用固定字串的 `subprocess.run([sys.executable, "-c", code, probe])`,沒有 shell,也沒有外部輸入拼接。路徑來自 repo 自己的 `GRAPHCTL`。
6. 行動端:無。

新加依賴:無,只用標準函式庫(errno、stat、os、secrets)。

看過的檔:
- `governance/review-reports/code-probe-postreview-dispatch-ledger/r8-snapshot.patch` 全部七個檔區塊:
  - `scripts/scenario_probe.py`
  - `governance/eval/ablation_lumos_first.py`
  - `scripts/test_lumos.py`
  - `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md`
  - `docs/lumos-toolchain-knowledge/Systems/codex-harness.md`
  - `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md`
  - `docs/lumos-toolchain-knowledge/Verification/持久用量帳第七輪審查修補驗證.md`
- 實驗用的 `e5ce8675` 版 `scripts/scenario_probe.py`,實驗目錄已刪除。

總結:最高嚴重度 minor
