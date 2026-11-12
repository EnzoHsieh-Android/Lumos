severity: minor

## Findings

### 1. 掛鉤腳本缺席時，`--append` 與 `--force-full` 直接崩 traceback（rc1，沒有友善訊息）
severity: minor
blocking: no
`governance/eval/build_goldset.py:151-162`（`_load_hook`）、`:208`（`edit_cases` 的 `_hook_would_fire`）
引句:「spec = importlib.util.spec_from_file_location("lumos_impact_hook_for_goldset", HOOK)」

- **重現輸入**：把 `build_goldset.py` 和 `scripts/lumos` 複製到暫存 git repo，旁邊不放掛鉤檔。repo 裡要有一個提交過的 `a.py`，這樣 `edit_cases` 才會走到掛鉤判斷。
- **`--append 2`**：走到 `edit_cases` → `_hook_would_fire` → `_load_hook` 時丟出 `FileNotFoundError`，沒有任何友善訊息。
- **`--force-full`**：同樣崩潰，search 題的建池已經跑完才崩。
- **資料面**：兩條路徑都在寫檔之前崩，題庫檔仍是 `{"edit":[],"labels":{},"search":[]}`，沒有損壞。
- **裸跑防護不受影響**：延後載入的設計達到了目的。我另外用 `t_goldset_force_full_guard` 的情境確認，裸跑仍是 rc2 並指路 `--force-full`。
- **意義**：筆記與程式註解只承諾「裸跑防護」在無掛鉤時能走到。`--append` 和 `--force-full` 在腳本被單獨搬走時無法使用，這點沒有被明講。
- **歸因：有證據的原有漏查，不是修補造成。**
  - 修前 `d613ce4f5` 已是同樣的延後載入（`_HOOK_MOD` list，在 `_hook_would_fire` 內載入），同樣會崩。
  - 兩版差別只在快取容器從 list 改成 dict，崩潰行為相同。
  - 我只跑了修後版，修前版是讀 `git show d613ce4f5:governance/eval/build_goldset.py` 的原始碼，沒有實際執行，所以歸因是由原始碼比對得出。

## 三問回答

**① 原問題的修復效果有何行為證據？**
- **G1（抽題端與追加端的去重）**
  - **claim**：抽題端同檔同改動片段只出一題；追加流程的預先過濾不替名額已滿、同提交、同片段的候選建池。
  - **case_source**：`t_goldset_file_quota_cap`（r1-behavior-cases.json 的 G1 repair 案例）。
  - **input**：`src/dup.py` 先加、再刪、再加回同一行；追加端用假 `edit_cases`／`edit_pool`，餵入同提交、同片段、名額已滿三種候選。
  - **after**：`python3.14 scripts/test_lumos.py -k goldset` 為 44 passed、0 failed。包含「抽題端：同檔同改動片段只出一題」（dup 共 2 題）與「預先過濾：只替該出的題建池」（建池呼叫恰為 `a.py d2、d3`、`b.py e1`）。
  - **before**：這兩個案例在修前不存在，修前沒有可比對的結果，歸因未判定。
  - **comparison**：我讀程式後確認這兩個斷言會因為拿掉抽題端 `deltas` 去重或 `_run_append` 預先過濾而失敗。我沒有實際跑拿掉後的變異，所以只是推演，實際翻紅未驗。
- **G2（掛鉤改字典快取、延後載入）**
  - **claim**：行為不變，只換容器。
  - **after**：`t_goldset_edit_cases_hook_eligible` 通過。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**
- **正常路徑**
  - 我在暫存 repo 把 `HOOK` 指向真掛鉤檔，用 `edit_cases(10, per_file=3, root=…)` 跑含中文與空白的路徑 `src dir/中文 檔.py`：兩個提交各出一題，片段不同，題目正確。
  - 該檔被刪除後不再出題，因為 `(root/f).exists()` 為 False。
- **提交碼長度**：題庫既有題的 commit 欄一律以 `[:8]` 比對，而 `edit_cases` 與 `_run_append` 取到的 commit 本來就是 8 碼，兩端一致。
- **指定題庫路徑**（`gpath`）：寫後自驗是拿記憶體裡的 `before_edit`／`before_labels` 比對，與路徑無關，指定路徑後仍成立。這條只靠讀程式確認，測試只跑了 rc0 與 a.py 剛好 3 題，沒有案例對指定路徑故意改壞既有區塊去觸發 rc2。
- **參數檢查**：`--per-file 0` 回 rc2 並印出「要是正整數」。
- **錯誤路徑**：掛鉤缺席見 finding 1。

**③ 新發現的同一案例在修前、修後各是什麼結果？**
- **Finding 1**：修前與修後都是 `FileNotFoundError`（修前只讀原始碼，未實跑），所以不是回歸。

## 圖譜鏡頭

- 派工詞說這次沒附固定席節點，我沒有可逐條判的合約。
- 筆記對照：
  - 計劃檔與 `Systems/retrieval-ranking.md` 裡「不帶上限選項時每支檔仍只出一題、出題母體換成掛鉤會觸發的檔」，與程式一致（`per_file` 預設 1，`edit_cases` 永遠過 `_hook_would_fire`）。
  - 回退方式「要回舊母體得把掛鉤判斷與範例資料夾過濾一起拿掉」與程式一致。
  - `docs/lumos-toolchain-knowledge/Verification/2026-11-13_改檔題庫擴充與新基線.md` 的變異翻紅宣稱我沒有重跑，未驗。

## 角色鏡頭
- 本檔是離線出題腳本，沒有對外 API，也沒有端點授權問題，所以 be-api-compat 與 be-authz 不適用。
- 題庫 JSON 的格式只多了讀端容忍的欄位，既有題格式未改，新舊互讀沒有問題。

## 未驗範圍
- 修前版沒有實際執行。
- 沒有對修補做變異驗證（拿掉判斷看測試翻紅）。
- 沒有跑不帶 `-k` 的全套測試（派工禁止）。
- 非原子的 `gpath.write_text` 屬於修前就有的寫法，這次沒動它。

總結 max severity: minor

(暫存目錄 `/tmp/lumos-seat-work/code-改檔題庫擴充/單reviewer-r2-sonnet` 已刪除。)
