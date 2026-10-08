severity: minor

我逐項還原後,七個指定改壞版本裡有六個讓對應測試翻紅。字元裝置分支拿掉 fstat 沒有翻紅。另外三處相關的改壞(拿掉 `set_blocking`、歷史追加拿掉 `O_NONBLOCK`、umask 檢查改用不含 "umask" 字樣的輔助函式)也都沒翻紅。以下是 4 條 minor,沒有會擋推送的問題。

## Finding CTR7-01
severity: minor
blocking: 否
引句:「if not stat.S_ISCHR(os.fstat(fd).st_mode):」
file: `scripts/scenario_probe.py:84`
- 具體輸入:取代模式下的輸出目標是字元裝置,例如 pty slave 或 `/dev/ttysNNN`;或檢查後、開檔前被換成別的東西。
- 走到哪一段:`_atomic_write_bytes` 的字元裝置分支(第 82–87 行),有三個動作。
  - 非阻塞開檔(`O_NONBLOCK`)。
  - `fstat` 確認開到的真的是字元裝置。
  - `set_blocking(fd, True)` 把阻塞模式改回來。
- 壞在哪:三個動作都沒有測試守著。測試只寫 `/dev/null`,而 `/dev/null` 不受這三個動作影響。
- 重現 ① 拿掉 `fstat` 檢查:`t_probe_boundary_fifth_round_output` 27 passed、`fourth_round` 27 passed、`postreview` 18 passed,0 failed,沒有翻紅。`r6-mutation-checks.log` 的 11 種改壞也沒有這一項。
- 重現 ② 拿掉 `os.set_blocking(fd, True)`:同樣三組全綠。
- 這一步不是只有形式上的風險。我開一個 pty,另一邊的執行緒慢慢讀走資料,對 slave 路徑寫 300KB:
  - 現行版本:`OK`,讀端收到 303004 位元組(含 pty 換行轉換多出的 4 位元組)。
  - 拿掉 `set_blocking`:`BlockingIOError: [Errno 35] write could not complete without blocking`,讀端只收到 2048 位元組。
- 所以 `--out` 指向非 `/dev/null` 的終端裝置、輸出又超過緩衝時會寫不完,而且整批模型跑完後才爆。
- 歸因:未判定。483df9fe 沒有這個分支(普通阻塞開檔),所以不是修補造成的行為回歸,而是 3e149721 新增的分支自帶測試缺口。兩版查證用上面的 pty 腳本:修前 483df9fe 用 `O_WRONLY|O_NOFOLLOW` 阻塞開檔,不會 EAGAIN;3e149721 與 67b1dea2 的現行版本寫完整。

## Finding CTR7-02
severity: minor
blocking: 否
引句:「在有控制終端的開發機上走不到這條路」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:156`
- 具體輸入:合併後這篇筆記同時留著兩條講同一件事的 PITFALL。
  - 第 140 行(主線側):用 `python3 scripts/test_lumos.py -k confirm_tty_unit` 當 O_NOCTTY 的重現與重驗,說「修前停在 prompt 有寫進 tty,修後 6 passed」,並叫人「重跑此單例」。
  - 第 156 行(第六輪分支側):說 `t_confirm_tty_unit` 在開發機上走不到這條路,拿掉 `O_NOCTTY` 照樣全綠,不能當防回歸。
- 壞在哪:第 140 行的重跑指令對 O_NOCTTY 沒有鑑別力。我在副本把 `scripts/lumos` 的 `O_NOCTTY` 拿掉:
  - `t_confirm_tty_unit` 仍是 6 passed、0 failed。
  - `t_confirm_tty_no_ctty_session_survives` 翻紅,輸出是 `✗ 開 pty 確認後關掉,程序沒收到掛斷 (-1, 'SCENE leader=True ctty=False\n', '')`。
- 接手的人照第 140 行重驗會得到假的安心。第 140 行也沒有說只有在「執行器是 session leader」時才成立。
- 歸因:合併手解時兩邊都保留造成。第 140 行在 6467401a 有、在 483df9fe 與 3e149721 沒有;第 156 行相反。兩個父版本各自沒有矛盾,合併後才有。查證命令:`git show <sha>:docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md | grep -c 重跑此單例與全套分片`,結果 6467401a=1、483df9fe=0、3e149721=0。

## Finding CTR7-03
severity: minor
blocking: 否
引句:「check("原子寫入不碰整個程序的 umask"」
file: `scripts/test_lumos.py:43383`
- 具體輸入:有人把「讀 umask」搬進輔助函式,例如 `_cur_mask(): m = os.umask(0); os.umask(m); return m`,再由 `_atomic_write_bytes` 呼叫。
- 壞在哪:這條斷言只檢查 `_atomic_write_bytes` 自己的原始碼(去掉 docstring)裡有沒有 "umask" 這個字。
- 重現 ④ 原子寫入改回 `NamedTemporaryFile` 加 umask 設 0 再設回的寫法:`✗ 原子寫入不碰整個程序的 umask` 翻紅,`26 passed, 1 failed`。
- 重現 ④ 變體(同樣改回 `NamedTemporaryFile`,讀 umask 搬進 `_cur_mask()`):三組測試全綠,`27 passed, 0 failed`,而全程序 umask 的瞬間改動又回來了。
- 這是字面檢查,不是行為檢查。函式本體只要多一行含 "umask" 的註解,它也會誤紅。
- 歸因:未判定。這條斷言與 `_atomic_write_bytes` 重寫都在 3e149721,沒有修前對照。

## Finding CTR7-04
severity: minor
blocking: 否
引句:「跑的期間被換成連結或 FIFO 時報錯,不跟過去也不卡住」
file: `scripts/scenario_probe.py:1390`
- 具體輸入:模型跑的期間 `--history` 路徑被換成 FIFO,而且已有讀端。
- 壞在哪:註解說換成 FIFO 時會報錯。實測有讀端時,`O_WRONLY|O_APPEND|O_NONBLOCK` 開得起來,寫入成功。我開了 FIFO 加讀端,讀端收到 `b'{"x":1}\n'`,沒有報錯。只有沒讀端時才會 ENXIO。
- 另外歷史檔換成 FIFO 的情況沒有任何測試,只測了換成連結。
- 重現 ⑥ 歷史追加拿掉 `O_NOFOLLOW`:`✗ 跑的期間被換成連結時追加不跟過去`,翻紅。
- 重現 ⑥ 變體,拿掉 `O_NONBLOCK`:三組全綠,沒有翻紅。
- 影響很小:這個換 FIFO 的攻擊者自己就是讀端,拿到的只是自己能讀的歷史紀錄。
- 歸因:未判定。這行是 3e149721 新增。

## 固定席逐條判定
- **codex-harness**:第六輪新增的 PITFALL 與 WHY 對得上 67b1dea2 的程式碼。
  - 必要鍵都齊,`lumos lint` 0 error;2 條 warning 是舊的 FACT 行,不在 diff 內。
  - 「lumos 原語註明否決 umask 設 0 再設回」成立,見 `scripts/lumos` 的 `_write_lf` docstring(第 19321 行起)。
  - 取代模式與追加模式規則的前後對照腳本顯示 483df9fe → 3e149721 → 67b1dea2 一致。
  - 合併段:兩個 `verified_by` 清單、10-05 段落沒有互相矛盾,也沒有重複。
- **測試假綠形態(★INVARIANT★)**:
  - 綁定測試 `t_slim_uninstall_manifest_parent_cleanup_is_best_effort`、`t_deinit_vendored_unlink_failure_does_not_abort` 存在。
  - 新測試多數有「現場成立」前置斷言(硬連結、換成連結),但 CTR7-01、CTR7-03 的缺口沒有,見上。
  - `t_confirm_tty_no_ctty_session_survives` 在拿掉 `O_NOCTTY` 時翻紅,前置斷言 `SCENE leader=True ctty=False` 成立。
- **lumos-cli-lifecycle(★INVARIANT★ re-inject)**:不受影響,綁定測試 `t_reinject_preserves_outside` 存在。只有 CTR7-02 的矛盾。
- **bound-tests-gate / canary-audit / design-loop / lumos-cli-read / autonomous-iteration-loop 等**:這份審材沒有改這些節點宣稱的行為。`ablation_lumos_first.py` 只改原子寫入的匯入來源與 `render_md` 的 `visible/text`。
  - 消融單元測試 `TestScenarioProbeAblation` 在副本跑出 32 個、31 過、1 個 error。error 的原因是我的部分解壓沒有 `CLAUDE.md`。
- **MOC、SKILL.md、reference.md**:
  - `reference.md:123` 確實有「### 修復穩定性試行」一節。
  - `skills/lumos-design-loop/templates.md:190` 有「§3.1」,第 0 步與第 6 步都在。
  - MOC 兩行都保留,連結目標都存在。
  - `pitfalls-code-loop` 合併後的 `updated` 與 `self_audit` 沒有矛盾。

## 還原翻紅結果表

| 項 | 改壞方式 | 結果 |
|---|---|---|
| ① | 字元裝置分支拿掉 fstat | 沒翻紅(三組全綠,CTR7-01) |
| ②a | FIFO 改回直接寫,連 `O_NONBLOCK` 一起拿掉 | `fifth_round_output_edges` 翻紅,`✗ 沒人讀的 FIFO 不會卡住,換成普通檔`,26 passed 1 failed |
| ②b | FIFO 改回直接寫,保留 `O_NONBLOCK` | 翻紅,`Errno 6 Device not configured` |
| ③ | `_output_target_problem` 追加模式收連結 | 翻紅,`Errno 62 Too many levels of symbolic links`,20 passed 1 failed |
| ④ | `NamedTemporaryFile` 加 umask 設 0 再設回 | 翻紅,`✗ 原子寫入不碰整個程序的 umask` |
| ④變體 | 同上,讀 umask 搬進輔助函式 | 沒翻紅(CTR7-03) |
| ⑤ | 拿掉 `st_nlink == 1` | 翻紅,`✗ 有多個名字的檔不沿用權限... 0o100666` |
| ⑥ | 歷史追加拿掉 `O_NOFOLLOW` | 翻紅,`✗ 跑的期間被換成連結時追加不跟過去` |
| ⑥變體 | 歷史追加拿掉 `O_NONBLOCK` | 沒翻紅(CTR7-04) |
| ⑦ | `⟦` 標記字元不自轉 | `fourth_round` 翻紅,`✗ 字面寫成標記樣子的文字也跟真控制字元不同`,26 passed 1 failed |
| 附 | 拿掉 `os.set_blocking` | 沒翻紅(CTR7-01) |
| 附 | 永不沿用權限 | 翻紅,`fifth_round_output_edges` 加 `postreview` 各 1 條 |
| 附 | 拿掉 uid 判斷 | 翻紅 |
| 附 | 拿掉父目錄可寫檢查 | 翻紅,`Errno 13` |
| 附 | 拿掉 lstat 的 OSError 處理 | 翻紅,`Errno 63` |

## 修補三問
- 原問題的修復效果:修前 483df9fe 與修後 3e149721、67b1dea2 三版用同一組案例對照,結果如下。
  - FIFO:修前 HANG,修後換成普通檔。
  - 硬連結:修前沿用 0666,修後 0644,另一個名字的內容不變。
  - 歷史檔是 FIFO、連結、在唯讀目錄:修前放行,修後 rc2,模型呼叫數為 0。
  - 輸出檔名過長、父路徑是普通檔:修前拋出 `OSError`/`NotADirectoryError`,修後轉成訊息。
  - 標記字元 `⟦` 與字面反斜線:對應測試通過。
- 保留行為:
  - 自己擁有且單一名字的 0640 既有檔,三版都維持 0640。
  - `/dev/null` 三版都維持字元裝置、寫入成功。
  - 既有唯讀普通檔照舊拒絕寫入。
  - 3e149721 到 67b1dea2 這兩個程式檔的行為一致:`scripts/scenario_probe.py` 與 `ablation_lumos_first.py` 的對照腳本輸出相同。
- 新發現的同一案例:CTR7-01 到 CTR7-04 在修前 483df9fe 都沒有對應程式碼,因為這些分支和斷言都是 3e149721 新增的。CTR7-02 兩版都沒有,是合併造成的。

## 未驗範圍
- 探針大子集的 409 數字沒能重現。我只解壓了允許的三個目錄,`-k probe` 在副本跑出 385 passed、9 failed。9 個失敗都來自副本缺 `governance/scenarios` 與 `CLAUDE.md`,例如 `commands.jsonl` 找不到,不是這次變更。另外 `fifth_round_output` 27、`fourth_round` 27、等待 2、終端確認 8、消融子集 4 都重現,第 8 項消融單元測試除缺檔那 1 條外也重現。
- 「兩支產品檔的規則告警與修前相同」(ruff 與專案規則)沒驗,副本沒有專案設定。
- 沒驗 root 身分的分支。
- 主線 344 個提交本身依規定不審。
- 快照檔 `r7-snapshot.patch` 在第 59830 位元組附近有不合法的 UTF-8,是 git 把 `--cc` 的 hunk 標題函式名截在 80 位元組、剛好切斷一個中文字造成的。這對審材內容沒影響,但直接用 UTF-8 讀會報錯。
- 兩篇舊驗證紀錄 `Verification/持久用量帳第五輪修補驗證.md:21` 與 `持久用量帳第五輪審查修補驗證.md:23` 仍寫 `\xNN`、字面反斜線加倍。它們有 `revalidate_when`,ablation 的 PITFALL 也已交代第六輪改了寫法,所以我沒單獨列成 finding。
- 實驗目錄 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/合約圖譜7-sonnet/` 已刪除。

總結:最高嚴重度 minor
