severity: minor

## Finding SEC7-01
severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK」
file: `governance/review-reports/code-probe-postreview-dispatch-ledger/r7-snapshot.patch:339`(對應 scripts/scenario_probe.py 的 `--history` 追加段)
- 誰:對 `--history` 所在目錄有寫入權的另一個本機使用者。
- 從哪:開跑前檢查(`_output_target_problem`)之後、模型跑完的追加之前,這段時間窗。
- 送什麼:兩種做法。(a) 把歷史檔換成 FIFO,自己持有讀端。(b) 放一個指向受害者可寫檔的硬連結,例如與該目錄同一檔案系統的 `~/.zshrc`。
- 拿到什麼:
  - (a) 歷史追加只加了 O_NONBLOCK 和 O_NOFOLLOW,開檔後沒有 fstat 確認是普通檔。有讀端時 FIFO 開得成功,那一行歷史 JSON(題數、通過率、秒數、arm、seed)會寫給攻擊者。沒有讀端時報 ENXIO,不卡住。洩漏內容是統計摘要,不含密鑰。
  - (b) 追加不像取代路徑那樣檢查 `st_nlink`,會把一行 JSON 追加進硬連結的另一個名字。建立硬連結要先有對目標檔的權限(Linux 預設 protected_hardlinks 會擋非擁有者),所以實際可利用性低。追加的內容是固定格式 JSON,也無法控制。
- 重現命令與輸出(複製開檔旗標在暫存目錄實測,已清除):
  - 命令:對 FIFO 先以 O_RDONLY|O_NONBLOCK 持讀端,再用同樣旗標開檔寫入。
  - 輸出:`attacker read: b'{"record":1}\n'`
  - 命令:對一個硬連結名字開檔追加。
  - 輸出:原檔 `victim` 內容變成 `keep\n{"x":1}`
- 歸因:修補自己的說明寫「跑的期間被換成連結或 FIFO 時報錯」,但實際只擋了連結,沒擋 FIFO 和硬連結。這是縱深防禦缺口,不是直接可利用的洞。修法是開檔後 `fstat` 要求 `S_ISREG` 或 `S_ISCHR`,並檢查 `st_nlink`。
- 標「推論」的部分:硬連結那條缺少跨使用者的實際環境驗證。

## 六類逐類
1. 不可信輸入流到危險操作:
   - 取代路徑:暫存檔用 `O_EXCL|O_NOFOLLOW` 建立,預測 `.probe-out-<pid>-<8hex>.tmp` 這個名字沒用,撞名只會重試,指向該名字的連結也會被 O_EXCL 拒絕。`os.replace` 是替換目錄項,不跟隨連結、不寫進 FIFO 或硬連結的 inode。
   - 目錄寫入權本來就能刪或換目標檔,這不是新增能力。
   - 字元裝置分支:一般使用者不能 mknod,而且檢查後被換成連結、FIFO 或普通檔時,開檔用 `O_NONBLOCK|O_NOFOLLOW`,`fstat` 不是字元裝置就拒寫(寫入前已確認,未實跑)。所以裝置節點接 pty slave 的攻擊走不通。
   - `st_uid==_euid()` 且 `st_nlink==1` 的判斷與 `lstat` 之間有時序窗,但可繞過的結果只是新檔權限變成 `mode` 沿用舊值,而這個值來自我方原本的 `lstat`,不會變寬。
   - 追加路徑見 SEC7-01。
2. 登入與權限:已看,無。
3. 密鑰與個資:結果檔和歷史檔新建時用 `0o666` 加 umask,與修前相同。沿用權限只限自己擁有且單名字的檔,比修前更嚴,沒有變寬。
4. 加密與傳輸:已看,無。
5. 執行邊界:
   - 報表:不可列印字元(含 ESC、BEL、C1、U+202E 等 Cf/Zl)一律轉成 `⟦U+XXXX⟧`。標記字元 `⟦` 本身也轉寫,偽造標記不會與真標記混淆。之後還過 `html.escape` 和 Markdown 跳脫(`\ ` * _ [ ] ( ) ! | : @ ~ ` 加 `www.`)。換行已先去掉,沒找到可注入終端序列、Markdown 連結、圖片或 HTML 的路徑。
   - 合併進來的 `skills/lumos-code-loop/SKILL.md` 與筆記:只有記帳步驟說明和連結,沒有新的執行指令、網址抓取或 shell 片段。
   - 新測試:只用暫存目錄、`mkfifo`、`os.link`、`patch`、`signal.alarm` 和 `importlib` 載入本 repo 的檔案,沒有命令拼接,也沒有外部輸入。
6. 行動端:無。
新依賴:無(只新增標準庫 `errno` 的匯入)。

看過的檔:
- `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md`
- `docs/lumos-toolchain-knowledge/Systems/codex-harness.md`
- `docs/lumos-toolchain-knowledge/Verification/持久用量帳第六輪審查修補驗證.md`
- `governance/eval/ablation_lumos_first.py`
- `scripts/scenario_probe.py`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/MOC/index.md`
- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md`
- 合併段中的其餘 Systems 筆記(含 `Systems/review-convergence-eval` 的連結)
- `skills/lumos-code-loop/SKILL.md`

說明:合併段的「其餘 Systems 筆記」部分,檔名只在材料中截斷顯示,我沒有逐檔讀完整內容,只確認它們不含可執行指令。

總結:最高嚴重度 minor
