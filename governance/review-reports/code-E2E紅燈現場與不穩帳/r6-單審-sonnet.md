severity: clean

本輪沒有 finding。這次修補只有一個重構(把逐行讀與篩選抽成 `_e2e_history_rows`)加一行筆記。我在修前後兩版各跑同一批 history 指令,輸出與回傳碼逐字相同。

## 查證方式

我把修前 9b52b445 和修後 65f76c66 的 `scripts/lumos` 各複製一份。兩版用同一份總表,帶下表的參數組合各跑一次,逐字比對輸出與回傳碼。

總表內容:
- 同一個 run_id "A" 在非相鄰位置出現兩次。
- run_id 為數字 0、空字串、字串 "0"、None 的行。
- 沒有 run_id 的舊行、`cases` 不是清單的行、項目為空的重判行。
- 一行壞 JSON。

## 同一案例證據

| claim | input | expected | before | after | comparison |
|---|---|---|---|---|---|
| 重構不改輸出與回傳碼 | 不帶 `--flaky`;`--flaky`;`--case`;`--feature`;兩者並用;`--last 1`、`--last 2`、`--last 3`;`--last 1000000000000000`;`--last -1`;`--case nonexist --flaky` | 兩版相同 | 見右 | 見右 | 全部逐字相同,`diff` 輸出 SAME |
| 讀不了總表的訊息與回傳碼不變 | 總表 `chmod 000`,帶 `--flaky` 與不帶 | 擋下並回 rc=2 | `檢測總表讀不了:[Errno 13]…` rc=2 | 同左 | 相同 |
| 總表目錄不存在時照舊 | 總表路徑是目錄(`is_file()` 為 false) | 「還沒有檢測紀錄」 | 同 | 同 | 相同 |
| `--last` 淘汰順序不變 | `--last 1 --flaky`(留 ev10)、`--last 2 --flaky --case x.a`(ev7) | 兩版相同 | 同 | 同 | 相同 |
| 測試能抓到重構出錯 | 在修後版本分別改壞三處,跑 `-k android_e2e_flaky`:①`return rows` 恆定、②歸併鍵改成 `("row", n)`、③`popitem(last=True)` | 測試翻紅 | — | ①11 條紅、②1 條紅、③1 條紅 | 三處都被抓到;`-k android_e2e_history` 在這三處下維持 15 條全綠 |

修後原版直接跑,`-k android_e2e_flaky` 是 29 passed,`-k android_e2e_history` 是 15 passed。

## 本輪首要鏡頭(0):回傳型別

- **回傳型別**:`_e2e_history_rows` 在 flaky 時回 OrderedDict、否則回 deque,呼叫端與之對應。
  - flaky 分支用 `got.values()` 與 `len(got)`,這是 OrderedDict 的用法。
  - 非 flaky 分支用 `for r in got` 與 `if not got`,deque 與 OrderedDict 都能用,但這個分支只會拿到 deque。
  - 兩個分支沒有用錯型別的路徑。
- **OSError**:`_e2e_history_rows` 是普通函式,不是產生器,OSError 在函式內部呼叫時就丟出,仍被 `_e2e_history_cmd` 的 `try` 接住。
- **`n` 的編號**:`enumerate` 仍然包含被篩掉的行,所以沒有 run_id 的行用 `("row", n)` 當鍵,與舊版一致。
- **`import collections`**:搬進新函式,舊函式已移除這行,沒有遺漏。

## 其餘鏡頭

- **(b) 只提醒的保證**:這次修補沒碰判定、回傳碼、`feature_runs`,`_e2e_history_cmd` 的 flaky 路徑固定 `return 0`,與修前相同。
- **(c) 歸併與淘汰順序(非本次引入,不算 finding)**:同一個 run_id 非相鄰重現時,它的位置固定在第一次出現處。
  - 例:`--last 2` 下 A(第 1 行)、B、A(重判)、C 會淘汰 A,即使 A 的重判比 B 新。
  - 這是修前就有的行為,兩版相同;需要連續重判跨過其他執行才會碰到。我給不出合理的實際操作會觸發,所以不標 finding。
- **(d) 印出口**:`_e2e_history_line` 在修補內沒有變動,仍經 `_out_clean`。這次修補沒有新增印出點。
- **(e) 效能**:非 flaky 路徑仍是逐行讀的 deque(maxlen=last)。flaky 路徑的 OrderedDict 仍以不同執行數為上限。重構沒有改變這兩個資料結構。

## 圖譜鏡頭

- 固定席節點 guard-kill、lumos-cli-read、design-loop、測試假綠形態、lumos-cli-lifecycle 等的合約,對象分別是 guard kill、search、處置閘、還原翻紅釘、re-inject。diff 只動 android-e2e history 的內部函式,不涉及這些合約,判不影響。
- loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger 是 RISK 節點,同理不受影響。
- 沒有帶殘留徽章的合約行,也沒有「新增殘留」段,殘留問答換編號的問題不適用。
- 新加的一行 WHY 筆記有寫 `[出處:]`、`[因:]` 和 `[test:t_android_e2e_flaky_history]`;該測試確實存在,而且如上所示能在改壞時翻紅。

## 修補鏡頭三問

1. **原問題的修復效果**:原問題是 `_e2e_history_cmd` 複雜度 12 超過上限 10。我只確認了行為不變(見上表)。我沒有跑 ruff 或新增告警閘,所以複雜度是否降到 10 以下我未驗,未判定。
2. **修補處的正常、錯誤與相鄰路徑**:正常路徑、讀不了的錯誤路徑、不帶 `--flaky` 的相鄰路徑,以及 `--case`、`--feature`、兩者並用,在兩版輸出一致。
3. **新發現的同一案例**:沒有新發現,所以沒有修前修後的差異案例。

未驗範圍:ruff 與複雜度數值;十萬行總表的實測時間與記憶體(只從資料結構判斷沒有變化);其他 diff 區塊(判定、flow 範本腳本等)在本輪沒有重審,按任務指示只就修補差異與歸併路徑查證。

總結:整份最高嚴重度為 clean
