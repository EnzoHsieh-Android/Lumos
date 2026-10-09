severity: minor

## Finding ARCH8-01
severity: minor
blocking: 否
引句:「_SPECIAL_CATS = frozenset(("Cc", "Cf", "Zl", "Zp", "Cs"))」
file: `scripts/lumos:34338`(另見 `scripts/test_lumos.py:65307-65320`)
- 既有:`_PATH_SPECIAL_CATS` 在 `scripts/lumos:34331-34338` 的註解明寫「只有這一份」。`t_note_audit_reread_drift_share_special_char_cats`(`scripts/test_lumos.py:65307`)就是為了擋「各處自己抄一組」而寫的。`_kill_esc`(`scripts/lumos:16067-16070`)也是直接引用這個常數。
- 隱患:這次在消融腳本又寫了一份同樣的五類,還重寫了 `_kill_esc` 的一行函式本體。我沒找到「複製常數再用測試核對」的先例。同目錄的消融腳本取用共用物的做法是匯入,例如從探針匯入判準和原子寫入(`governance/eval/ablation_lumos_first.py:29`)。
- 這次:測試核對得很弱。取樣字串 `"\u202e\ufeff\U000e0001\u3000\u00a0x"`(patch 第 669 行)只涵蓋 Cf 和 Zs,沒有 Cc、Zl、Zp、Cs。主程式日後增減類別,這支測試不會翻紅。專案自己的做法是直接斷言集合相等(`test_lumos.py:65320` 的 `set(cats) == {...}`)。
- 判斷:這是第二份常數,我歸為不一致的命名與結構,不算第二種做法,但判得不很準,標 ⚠ 交編排者。
- 不一致 1 檔(消融腳本),外加測試核對力道不足。

## Finding ARCH8-02
severity: minor
blocking: 否
引句:「暫時借 SIGALRM 抓卡住的呼叫;結束時把測試執行器原本的逾時鬧鐘還回去」
file: `scripts/test_lumos.py:35292`
- 既有:`run_with_timeout`(`test_lumos.py:35292-35306`)是執行器的逾時工具。測試內部自己抓卡住的寫法是就地內嵌 `signal.signal` 加 `alarm`,用區域 `_Hung` 例外,例如 `test_lumos.py:13076-13092` 和 `69765-69779`。
- 這次:新增 `_guard_hang` 這個 context manager(`test_lumos.py:43319`),`_Hung` 也改成模組層級,只替換了一處內嵌寫法。現在有三種形狀:執行器的 `run_with_timeout`、其餘內嵌處、`_guard_hang`。
- 行為差異有理由:`run_with_timeout` 結束時 `alarm(0)`,不還原外層鬧鐘,所以不能巢狀。內嵌處也都是 `alarm(0)`。`_guard_hang` 會還原,這是它的新價值。
- 判斷:不管走哪條路都是第二套逾時工具,可能算引入第二種做法。我不硬判,標 ⚠ 交編排者。
- 建議的對齊方向:讓 `run_with_timeout` 或其他內嵌處也共用它,或把還原邏輯併進 `run_with_timeout`。
- 不一致 1 檔。

## Finding ARCH8-03
severity: minor
blocking: 否
引句:「raise FileExistsError(errno.EEXIST, "連續 100 次都撞到既有的暫存檔名", str(path.parent))」
file: `scripts/lumos:20438`
- 既有:`scripts/lumos:20438-20453` 是專案裡唯一帶上限的 O_EXCL 迴圈,上限 99(`range(1, 100)`),用尾端 `raise RuntimeError("連續 99 次都撞到同名…")` 收尾。
- 這次:用 100 次、`for…else`、`FileExistsError(errno.EEXIST…)`。
- 註解「跟專案其他 O_EXCL 迴圈一樣」與事實不符。主程式的 `_write_lf`(`scripts/lumos:19334`)、`9331`、`22966` 都是單發,沒有迴圈。有上限的只有那一處,它的數字和例外型別都不同。
- 隱患:註解過度宣稱,數字與例外型別不統一。
- 不一致 1 檔,屬錯誤處理與日誌層級的小差異。

## Finding ARCH8-04
severity: minor
blocking: 否
引句:「_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)」
file: `scripts/lumos:1385`
- 既有:`scripts/lumos` 一律就地寫 `getattr(os, "O_NOFOLLOW", 0)`(`1385`、`9331`、`14099`、`20420`),`O_NOCTTY` 在 `23908` 也是就地寫。`scripts/scenario_probe.py` 修前同樣就地寫。
- 這次:改成模組常數 `_NOFOLLOW` / `_NOCTTY`。
- 這是小命名差異。常數化本身站得住腳,因為同檔內用了三處以上。
- 不一致 1 檔。

## 三問

**1. 分層與依賴方向:結構對齊,常數處理不對齊。**
- `scenario_probe` 不匯入 `lumos`,消融腳本匯入 `scenario_probe`(`ablation_lumos_first.py:29`),測試用 `_load_lumos_inproc()`(`test_lumos.py:225`)載入主程式。方向都跟既有的一致,沒有跨層直呼。
- 唯一例外是 `_SPECIAL_CATS` 的複製加測試核對。我沒找到先例,專案現行做法是單一出處再用測試斷言集合相等(`test_lumos.py:65307-65320`)。見 ARCH8-01。

**2. 命名與錯誤處理:大致對齊。**
- `_open_char_device`、`_open_history` 的 `_` 前綴和動詞開頭,與同檔 `_atomic_write_bytes`、`_output_target_problem` 一致。
- 錯誤用 `OSError(errno.EINVAL, 訊息, str(path))`,與同檔既有的 `PermissionError(errno.EACCES, …, str(path))`(`scenario_probe.py:128`)同形。
- 主程式的 `_regular_own_fd`(`scripts/lumos:1378`)是失敗回 None 的風格,但那是另一個執行檔,不拿來比。
- 主要差異:模組常數(ARCH8-04)和 O_EXCL 迴圈上限與例外型別(ARCH8-03)。`_guard_hang` 是小寫開頭的類別,與其他 context manager 的命名比,我沒查到直接對照,不列。

**3. 第二種做法:**
- `_guard_hang` 與 `run_with_timeout`、內嵌 alarm 並存,見 ARCH8-02(⚠)。
- O_EXCL 迴圈上限的寫法不一致,註解過度宣稱,見 ARCH8-03。
- `visible()` 與 `_kill_esc` 的比對:
  - 類別集合一致。
  - 格式一致,都是 `\u{ord:04x}`,非 BMP 同樣寫成 5 位 hex(`scripts/lumos:16070`)。
  - 唯一差異是 `text()` 先把 `\r` 和 `\n` 換成空白,再進 `visible`;`_kill_esc` 會把換行寫成 `\u000a`。這是報表排版的刻意處理,不是不一致。
  - 測試取樣沒涵蓋 Cc、Zl、Zp、Cs,見 ARCH8-01。

總結:不對齊共 4 條,其中重大 0 條
