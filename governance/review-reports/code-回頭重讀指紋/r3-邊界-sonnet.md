severity: minor

縮排鏈本身沒有崩潰類的邊界問題,測試也抓得到把判斷改壞的變異。有兩個非阻擋的 finding。

**已讀,無 finding 的部分**
- **CRLF**:行尾的 `\r` 被 `strip()` 去掉,純 `\r` 的行當空行。實測鏈原文是 `CONFIG = {`,不帶 `\r`。
- **只有 tab 或空白的行**:當空行跳過。
- **非 UTF-8**:全程用 bytes,`surrogateescape` 只用在給人看的鏈。實測 `\xff` 能正常算出來。
- **檔案第一行就是改動、純刪除、新增檔、檔尾之後的範圍**:沒有崩潰或錯位。刪檔的新側行數是 0,沒有鏈,符合文件說的。
- **二進位**:沒有 hunk,不讀內容。
- **效能**:對 `scripts/lumos`(5.5 萬行)每行各一段改動共 5.5 萬段,算完鏈約 0.12 秒。
- **測試有效**:我在複本上改了六種判斷再跑相關測試,每種都紅,清掉 `__pycache__` 後跑。
  - 彈堆疊 `>=` 改 `>`:`t_reread_fp_hunk_chain_rule` 紅(7 條斷言)。
  - 標籤不套用:`t_reread_fp_hunk_moved_between_functions` 紅(9 條),`t_reread_fp_chain_stable_on_other_edits` 也紅。
  - 逾時不擋的判斷拿掉:`t_reread_fp_timeout_not_blocking` 紅。
  - 起點不跳過空白行:`t_reread_fp_hunk_chain_rule` 紅(3 條)。
  - 範圍全是空白時的無限深起點拿掉:`t_reread_fp_hunk_chain_rule` 紅(2 條)。
- 複本與 `gctl-run-*` 暫存現場已刪;`reread_fp` 子集在原工作樹 104 全綠。

severity: minor
blocking: 否 — 只是讓搬移偵測在少見形狀下失靈,函式本體裡頂格的行在 `scripts/lumos` 裡約占 3% 以下
引句:「    那段改動的縮排鏈原文的雜湊(_note_reread_hunk_tags;代碼審 r1 資安席 major:整個拿掉時,同一段改動搬到同檔另一個前後三行」
問題:計劃〈實務隱患〉承認的盲區,我實際量了影響。函式本體裡頂格的行(`#endif`、多行字串內容、heredoc 結尾)會把縮排堆疊清空,之後的行以那一行當最外層,函式名就不在鏈裡了。
具體失敗情境:兩個函式本體逐字相同,且各在中間有一行頂格的 `#endif`。實測兩邊的鏈都是 `['#endif']`,標籤相同。同一段 `check(u)` 的改動從公開端點搬到管理員端點,只要前後三行相同,指紋不變。這就是 r1 資安席 major 的情境,只是被限縮在這種形狀。
影響大小:對 `scripts/lumos` 每個縮排行算鏈,最外層不是 def、class 或裝飾器的占約 2.9%,而且多數是頂層語句(`_START_TEMPLATE = (` 這類),不是函式本體裡的頂格行。實際落入盲區的比例更低。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:36745` ``(`while stack and stack[-1][0] >= ind`)

severity: minor
blocking: 否 — 只是誤擋方向:主線改了外層那一行,整個函式的指紋會變,要人重讀一次
引句:「那段改動的縮排鏈原文的雜湊(_note_reread_hunk_tags;」
問題:標籤是「整行原文」的雜湊,所以外層函式或 class 那一行的參數、簽名只要被主線改動,函式內每一段改動的指紋都變。上一版(只取函式名)和計劃動機 headers=False 都是為了讓「主線改了封閉函式的簽名」不使指紋失效,這輪的做法又把這個失效帶回來了。
另一點:起點取的是範圍內第一個非空白行,也就是上下文的第一行,不是被改的那一行。上下文跨到前一個兄弟函式的尾巴時,鏈會掛在前一個函式上,而不是被改動的函式。
具體失敗情境:rebase 後主線給封閉函式加了一個參數,該函式內全部 hunk 的指紋都變,對照紀錄對不上,要重新派判定者。方向是誤擋,可接受;`t_reread_fp_chain_stable_on_other_edits` 只測了其他位置的編輯,沒測封閉行本身被改。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:36698` ``

另外,「逾時沒算出新版指紋的篇不擋」讓大改動(依註解約要改到上千支被候選 about_code 列到的檔)可以整批不擋,帳上有記(`late` 欄)。這是設計明講的取捨,我當成已知、不另列 finding。

最高等級 minor,blocking 0 條。
