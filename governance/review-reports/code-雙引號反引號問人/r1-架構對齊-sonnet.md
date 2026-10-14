severity: major

**第 1 問：分層與依賴方向**

這份 diff 在分層上是對齊的，沒有跨層直呼。

新方法 `_double_tick` 在 `scripts/hooks/claude/bypass-ask-hook.py` 的 `_Normalizer` 裡，由 `_in_double` 呼叫。呼叫鏈跟鄰居一樣：`step` 到 `_in_double`（`bypass-ask-hook.py:323`、`:354`），對照 `step` 到 `_paren` 的鏈（`:323`、`:421`）。

它往下只用了同層的 `_mask` 和 `_Normalizer` 本身，沒有碰切段、走訪或 git 那幾層。它產出的 `` `…` `` 交給下游 `_split_cmdsubs`（`:464`）抽出來判。這跟引號外反引號的既有分工一致，那一種本來就是 `_Normalizer` 原樣放過、由 `_cmdsub_at` 認（`:498`、`:505`）。

**第 2 問：命名與錯誤處理**

結構對，只有一處小不一致。

- **命名**：同檔處理特殊結構的方法是 `_in_single`、`_in_double`、`_bare`、`_bare_special`、`_paren`、`_heredoc_op`、`_drop_bodies`、`_ansi_decode`（`:345`、`:354`、`:378`、`:389`、`:421`、`:431`、`:440`、`:267`）。`_double_tick` 是同一種底線加描述式，我不列。
- **錯誤處理**：找不到結尾反引號時，它不丟例外，改成遮掉反引號、往前走一格，行為還是「寧可多問」。這跟鄰居一致，鄰居（`_ansi_decode` 的 `:267`–`:285`、`_drop_bodies` 的 `:440`–`:451`）也都不丟例外、靠旗標或回傳位置收尾。此處跟 `_ansi_decode` 的差別是未結尾時「吃到指令尾」對「遮一個字就走」，各有理由，不算不對齊。

下面這條是結構相同、規則不同的小處：

引句:「while k < len(cmd) and cmd[k] != 」
severity: minor
blocking: 否
對照 `bypass-ask-hook.py:498`–`:507`：既有的 `_cmdsub_at` 認引號外反引號結尾時用 `text.find("`", i + 1)`，不管反斜線跳脫。新碼自己寫一個認跳脫的掃描（`k += 2 if cmd[k] == "\\" else 1`）。
- 同一個「反引號找結尾」現在有兩條規則：引號外的不認 `\``，雙引號裡的認。
- 這不算兩種做法，因為跳脫規則本來就隨引號環境不同。
- 但 `_split_cmdsubs` 對重整後的內容，仍會用 `find` 的規則再切一次。這裡靠 `_backslash` 把跳脫的反引號遮成私用區字元才不出事（`:338`–`:343`）。這個耦合沒有註解說明。
- 建議在 docstring 補一句「內部的跳脫反引號已被遮罩，所以 `_cmdsub_at` 的 `find` 不會誤切」。

**第 3 問：第二種做法**

算，我判 major。

引句:「新指令重整一趟,原樣包回反引號交給 _split_cmdsubs 抽出另外判;找不到結尾就照普通字遮掉」
severity: major
blocking: 是
對照 `bypass-ask-hook.py:305`–`:336` 的類別說明與 `step`。

- **既有做法**：同檔處理巢狀結構只有一種，就是在同一個 `_Normalizer` 實例上，用 `self.ctx` 堆疊重開一層狀態。
  - `step`（`:323`–`:336`）遇到 `$(` 就 `self.ctx.append([False, False, 0])`。
  - `_paren`（`:421`–`:429`）用 `cur[2]` 計深度，歸零時 `self.ctx.pop()`。
  - 巢狀期間共用同一個實例的 `self.out`、`self.pending`、`self.heredoc_ok`。類別說明明寫「`$(` 裡重開一層」。
- **新做法**：`_double_tick` 在方法裡直接 `_Normalizer(cmd[i + 1:k]).run()`，另建一個有自己 `ctx`、`pending`、`heredoc_ok` 的實例，遞迴跑一整趟，再把結果包回反引號。
  - 整個檔案裡，除了入口（`:170` 的預篩、`:1116` 的 `bypass_reasons`）之外，`_Normalizer` 從未被自己呼叫過，這是第一次在類別內部遞迴。
  - 連帶改變了狀態語意：反引號內的 heredoc 待剝清單、`heredoc_ok` 旗標跟外層隔離。`$(` 內則共用。同一個檔裡兩種巢狀的狀態邊界不一樣。
  - 類別說明寫的「整趟是線性的」，現在要靠 docstring 另外保證（「每段只重整一次」），不再是結構自然成立的。
- **替代寫法的可行性**：這是我不確定的點，⚠ 交編排者裁。
  - 反引號沒有括號深度可數，結尾是靠掃字找的，所以直接套 `ctx` 計深度不通。
  - 但可以讓 `ctx` 多一格「反引號層」，或在 `step` 遇到雙引號裡的反引號時 `self.ctx.append([False, False, 0])`，再讓 `_in_double` 或 `step` 在遇到結尾反引號時彈出。這樣是沿用同一個實例與同一個堆疊。
  - 若編排者認為遞迴建新實例的隔離性（不共用 heredoc 狀態）是刻意需求，就應該改成「接受第二種做法」，並在類別說明與家筆記補上兩種巢狀的狀態邊界差異。
  - 目前圖譜（`Systems/代理繞閘問人.md`、計劃筆記）只更正了「雙引號裡的反引號要抽出來判」，沒有交代為什麼這裡不用 `ctx`。

不對齊共 2 條，其中 major 1 條
