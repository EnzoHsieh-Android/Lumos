severity: clean

我審的是 `r5-repair-code.patch` 這 119 行,對照 `configs/ast-grep/kotlin-android/check.py` 裡既有的列號撤號判斷和 `choice-batch2.kt` 樣本。三問都判一致,零 finding。

## 三問

**1. 分層與依賴方向:一致。**
- 新增的列號檢查放在 `choice_tables` 的逐列迴圈裡,位置在「列號重複」檢查之前。它只用 `re.fullmatch`,沒有另讀帳、也沒有另開讀表路徑。
- `scripts/lumos` 照舊透過 `choice_tables` 讀表,讀表還是只有這一套(見 `check.py:1384` 的註解)。
- 樣本改動只加 `.kt` 行,用的是既有的 `// HIT|MISS C-n` 標記格式。我跑了 `-k choice_table_batch2`,測試通過(修後 20 條,修前 16 條),所以 `_CHOICE_SAMPLE_MARK` 解析樣本沒有問題。
- 我沒有重跑 `-k choice_samples_batch2`,也沒有重跑 ast-grep 規則本身,樣本核對的結果引用編排者提供的全綠紀錄。

**2. 命名與錯誤處理:一致。**
- 新增的 `probs.append((rid, f"列號要寫成 …"))` 後接 `continue`,和同一迴圈裡 `check.py:1510` 附近「列號重複」那一支的寫法相同:`(列號, 原因)` 元組,跳過該列,不另開 rc 或另一套訊息路徑。
- 文字沿用鄰居的用詞:「半形數字、不帶前導零」,和 `已撤列號` 那段說明相同。
- 這個函式是 `scripts/lumos` 的上游,它讀到任何問題就整張表不用,所以沒有另外的 rc 或帳本事件要對齊。
- 測試裡用 `tempfile.mkdtemp(prefix="gctl-cb2rules-")` 開暫存目錄,沿用既有做法。

**3. 第二種做法:沒有引入。**
- 判斷列號的正則 `[CA]-[1-9][0-9]*`,在 `check.py:1544` 的撤號檢查已經有同形的 `C-[1-9][0-9]*`,不是新寫法。
- 我考慮過是否該改嚴 `_CHOICE_ROW_RE` 這個 `\d+` 常數。改嚴會讓 `C-040` 這種列被 `section_table` 靜默丟掉,變成沒報錯,反而更糟。所以保留 `\d+`、改成事後 `fullmatch` 並報錯是對的,不算第二種做法。
- 同一個正則字面值在檔裡出現不止一處,專案其他地方也有這種形狀:具名常數有 `_FINDING_SOURCE_NO_RE`、`_KT_SIT_CID_RE`,行內寫法有 1544 行。鄰居本身兩種都有,不判不一致,不列 finding。

## 圖譜鏡頭

LUMOS-LENS 這次沒附固定席節點(鏡頭計算超時)。派工詞說備份在 `/tmp/lumos-seat-work/code-選擇點第二批/lens-r5.txt`,我沒有去讀,所以圖譜鏡頭的固定席沒有逐條判。我另外看了:改動只在 `check.py` 的 `choice_tables` 與 `choice-batch2.kt` 樣本,碰到的是既有的選擇點表與乾節點規則,沒有新增檔案,也沒有改到介面。

## 已驗主張的證據

| 主張 | 輸入 | 預期 | 修前 | 修後 | 比較 |
|---|---|---|---|---|---|
| 表裡列號寫成 `C-040`、`C-４０`、`C-4０` 或 `A-01`,不能因規則 id 跟著寫成同樣子而繞過撤號 | 測試 `t_choice_table_batch2`(第 146020 行起,在 `/tmp/lumos-seat-work/code-選擇點第二批/架構對齊-sonnet/repo`) | 報「列號要寫成…」 | `-k choice_table_batch2` 16 條通過,沒有這幾條斷言 | 同指令 20 條通過,含這幾條 | 修後多出的 4 條就是新守衛,修前根本沒有 |
| 正常列號照認 | 既有列號 `C-1`、`C-40`、`A-1` | 不新增問題 | 通過 | 通過 | 正常路徑不變 |

## 未驗範圍

- 規則 yml 本身(`api.yml` 的 C-34 到 C-37)這輪是否有改,我沒有逐行比對。
- 樣本 HIT/MISS 是否真的對應規則行為,我沒有拿 ast-grep 重跑。
- 全套測試依規定沒跑。
- 修前行為上,我只確認了修前版沒有新斷言,沒有另外造「`C-040` 列通過」的失敗重現。

我造的臨時 clone 和 worktree 還在 `/tmp/lumos-seat-work/code-選擇點第二批/架構對齊-sonnet/` 底下(`repo`、`before`、`probe.py`),沒有刪,請編排者收貨後清理。

最嚴重:clean;blocking 共 0 條;不對齊共 0 條,其中 major 0 條
