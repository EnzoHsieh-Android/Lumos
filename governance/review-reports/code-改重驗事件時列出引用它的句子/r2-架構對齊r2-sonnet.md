severity: clean

我看到的:LUMOS-IMPACT 範圍 c163f941..a040f829 只有 `scripts/lumos`、`scripts/test_lumos.py` 和兩篇筆記。本輪修補三件(同一行每句一筆、最多列 20 句、掃描包 try)都落在 `_print_revalidate_backrefs` 和 `_revalidate_backref_lines`。以下行號都對 a040f829 的 `scripts/lumos` 與 `scripts/test_lumos.py`。

**1. 分層與依賴方向:對齊。**
- 本案的函式只讀不寫,在 main 的 `set` 成功後呼叫(`scripts/lumos:50508`),放在 status 區塊之前。這跟 `_drift_print_followups`、`_closing_revisits`、`_closing_pending_decisions`、`_drift_print_backrefs`(`scripts/lumos:50510-50516`)是同一個位置、同一個形狀:`rc == 0` 才多印、不改回傳碼。
- 鄰居 `_drift_print_backrefs`(`scripts/lumos:35017`)自己重建 Env,本案收呼叫端的 `env`。`_closing_revisits`(`scripts/lumos:35385`)和 `_closing_pending_decisions`(`scripts/lumos:35409`)也是收呼叫端的 env,而且 docstring 已寫明「env 是改之前載入的、別篇沒變」。這不算第二種依賴方向。
- 沒有跨層直呼。掃描函式與 S21 共用 `_in_spans`、`_search_visible_lines`、`_SENT_END_RE`、`env.resolve(link_target(...))`。

**2. 命名與錯誤處理:對齊。**
- 例外清單完全相同:`(OSError, ValueError, RuntimeError, UnicodeDecodeError)`,本案在 `scripts/lumos:4178`,對照 `scripts/lumos:35023`。
- stderr 句型同一個骨架:`(列出…失敗,剛才的寫入照樣完成了:{e})`,對照 `scripts/lumos:35024`。
- 上限寫法相同:`rows[:20]` 加 `if len(rows) > 20`,對照 `scripts/lumos:35034-35039`。「…還有 N 句」只是單位從「行」改「句」,因為本案一行可有多筆。
- 鄰居那句尾有「(lumos drift scan 看全部)」。本案沒有對應的「看全部」指令,不能照抄,所以不列為不一致。
- 清單讀回那段只接 `(OSError, UnicodeDecodeError)` 且靜默 return,跟 `_closing_revisits` 的讀檔做法一致(`scripts/lumos:35396-35399`)。
- 測試格 ⑧ 用 `unittest.mock.patch.object` 加區域別名 `_patch2`、`_io2`,例外用 `# noqa: BLE001` 標註。全檔已有同樣寫法:`scripts/test_lumos.py:40963` 的 `_io2`、`:64219` 同型的 `noqa: BLE001`(如 `:58756`、`:74783`)。⑥、⑦ 沿用同函式既有的 `_rvb_vault` 加 `run` 寫法。

**3. 第二種做法:沒有。**
修補三件全部是把既有的 `_drift_print_backrefs` 做法搬過來,沒有新增 helper、旗標或另一套上限或安全網。「同一行每句各一筆」只是拿掉 `break`,不是新機制。

不對齊共 0 條,其中重大 0 條
總結:這次修補的上限、出錯處理、提示文字和測試寫法都照著專案裡現成的列句函式做,沒有另立一套,我沒找到不一致的地方。
