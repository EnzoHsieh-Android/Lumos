severity: minor

我在固定版本 22f6e132 的複本上實際造了輸入跑,沒有 blocker 或 major。找到 2 條 minor,都不擋推。

## Findings

severity: minor
blocking: 否

**1. `--shard 1/<超大數字>` 會依片數配置記憶體,片數打錯(例如多打幾個 0)就可能耗盡記憶體 ⚠**

引句:「loads, counts, buckets = [0.0] * live, [0] * live, [[] for _ in range(n)]」

- 輸入:有耗時表,`python3.14 scripts/test_lumos.py --shard 1/20000000 --list`。
- 走到的行:`_shard_by_duration` 裡 `buckets` 仍依 n 配置空串列。r1 只把比較次數限在 `live`,沒限配置。
- 實測結果:

| 片數 | 時間 | 最大記憶體 |
|---|---|---|
| 1,000,000 | 1.84 秒 | 約 540MB |
| 20,000,000 | 5.35 秒 | 約 1.9GB |

- 耗用隨片數線性成長,所以 1e9 約 95GB。這是推算,我沒真的跑 1e9,怕拖垮本機。
- 沒有耗時表時走 `k % _n`,幾乎不耗資源。這是「有表才會爆」的新耗用。
- 應該:`buckets` 只配 `live` 份,其餘以空串列處理(回傳時才補,或呼叫端用索引取)。也可以在 `_n` 超過測試數時直接擋。
- 歸因:有證據的原有漏查。修前 0cdfc7cc 就有同一行,而且 `loads`、`counts` 也依 n 配置;修後只收掉了比較次數那一項。
- 查證命令:`git show 0cdfc7cc:scripts/test_lumos.py | grep -n "def _shard_by_duration" -A14`。修後用 `/usr/bin/time -l` 跑上面的 `--shard`。

severity: minor
blocking: 否

**2. 耗時表路徑是目錄(或懸空符號連結)時,執行器靜默退回輪流分,刷新卻同一狀態擋 rc2**

引句:「if not p.is_file():」

- 輸入:`governance/test-durations.json` 是一個目錄。
- 執行器:`--shard 1/3 --list` 印「沒有耗時表,照名字輪流分」,rc 0。
- 刷新:`lumos test-durations refresh` 回 rc2,訊息是 `[Errno 21] Is a directory`。
- 各片看到的狀態相同,所以聯集仍等於全部,不會漏測。問題只在不一致:壞掉的表被當成沒有表。
- 設計意圖是「表格式不對每一份都擋」,這個狀態應該也擋(改成 `p.exists()` 後再判型別)。
- 補充:跑到一半把表換成目錄,結尾比對會抓到(開頭有雜湊、結尾沒有表)。但從頭就是目錄的情況不會被抓。
- 歸因:未判定。我沒有在修前 0cdfc7cc 上跑這個案例。

## 已驗、行為正確的輸入

這些我都在 22f6e132 上實際跑過。

**耗時表形狀(執行器,`--shard 1/3`、`--shard 3/3`)**
- 空檔、結尾多餘垃圾、巢狀 100 萬層(陣列與物件兩種):兩片都擋下,說「不是合法的 JSON」。
- 沒有 `tests` 或沒有 `version`:正常分片。`version` 填 99 也照收,欄位根本沒被檢查,但目前沒有造成實際問題。
- BOM、重複鍵、`-0.0`、整數與浮點混用、三個 1e308 並存:都正常分片,聯集等於全部。
- 不可讀(chmod 000):擋 rc2,訊息帶 `Permission denied`。
- NaN、Infinity、超大整數:由作者的測試涵蓋,我沒重造。

**`--shard` 參數**
- `0/3`、`-1/3`、`1/-3`、`1/0`、`1/3/4`:擋下。
- 全形數字 `１/3`:`int()` 接受,照常分片,無害。
- `3/3` 搭 `--suite docs`:分法照表,docs 子集 89 支,分到 30 支。
- `--suite keys` 搭單一名字、`2/2`:子集比片數少,第 2 片分到 0 支,「這片算過」,rc 0。
- `-k` 搭 `--shard`:先對全部測試分片、再套 `-k`,所以 `-k` 只選到少數支時,部分片會選中 0 個而判紅。這是修前就有的語意,不是這次新增。
- 片數等於或大於測試數:作者的測試涵蓋空片 rc1。

**每片跑完重讀表**(在臨時複本裡加一支睡 3 秒的測試,跑到一半動手腳,`--shard 1/1`)

| 跑到一半的動作 | 結果 |
|---|---|
| 刪表 | rc2,訊息「開頭 19a95d9d、結尾 沒有表」 |
| 改壞 | rc2,訊息「結尾 讀不懂」 |
| 改成別的內容 | rc2 |
| 換成目錄 | rc2 |
| 從無到有 | rc2 |
| 用相同內容重寫 | rc0 |

不帶 `--shard` 時表壞了不影響,rc 0。

**refresh(臨時 git 專案)**
- `.lumos/` 不存在、或 `.lumos` 是檔案:rc2,訊息要求先跑一次測試。
- 舊表是目錄:rc2,不覆蓋。
- 舊表不可讀(chmod 000):rc2。
- 舊表唯讀(chmod 444):rc0,靠原子替換寫入,沒有跟檔案權限衝突。
- 舊表帶 BOM:讀得進、保留舊值,寫出來的檔案沒有 BOM。
- run 檔帶 BOM:收進來。
- run 檔是 `[1]`、字串、`tests` 為字串或陣列:略過並印出名稱,不崩潰,run 檔仍被刪除。
- 秒數 `1e308` 收進表;`1e999`、NaN、負數、字串、布林不收。
- 只有一份 run 檔、與舊表完全不重疊:正常合併。
- run 檔是符號連結:只刪連結,指向的檔案不動。
- `governance` 是檔案:rc1,訊息以「擋下:寫不進耗時表」開頭。
- 不是 git 專案、不帶 `--repo`:rc2。
- 不是 git 專案、帶 `--repo .`:rc0,在非 git 目錄建出 `governance/`。docstring 說得通,但這個行為值得知道。
- `--repo` 指向不存在的路徑:rc2,訊息會走到「沒有 run 檔」。
- git 專案的子目錄、不帶 `--repo`:用 toplevel,rc0。

## 三問

1. **原問題的修復效果**:表在跑的期間被改動,現在每種情況都擋成 rc2,上面表格就是同一案例的修後結果。巢狀 100 萬層、超大整數、舊表帶 BOM 的行為也符合作者宣稱。我只在修後版本驗證,修前沒有逐案跑,只讀了 `git show 0cdfc7cc` 的 `_shard_by_duration` 原文。
2. **修補處的相鄰呼叫路徑**:正常、錯誤、`--suite`、`-k`、空片路徑都成立。唯一的相鄰缺口是 finding 1(片數配置)和 finding 2(目錄型壞表)。
3. **新發現在修前修後的結果**:
   - finding 1:修前修後都有 `[[] for _ in range(n)]`。r1 沒有收掉配置,只收了比較次數。
   - finding 2:未判定,沒在修前版本跑。

## 固定席節點逐條判

- **pitfalls-code-loop、reversibility-governance-ledger、loop-convergence-recording**(`scripts/lumos`):`_BOOKKEEPING_FILES` 加入耗時表只是多一條路徑常數。refresh 只寫耗時表和刪 `.lumos` 下的 run 檔,不碰治理帳。不影響。
- **測試假綠形態**(★INVARIANT★ 還原翻紅釘要配前置斷言):新測試都有「★前置★ 現場成立」斷言。邊界上沒發現讓釘子失效的情況。不影響。
- **lumos-cli-read、guard-kill、lumos-cli-lifecycle、design-loop**:這幾條合約的行為(search、guard kill、re-inject、處置閘)都沒被改動碰到。不影響。
- 超出上限只列名的節點(bound-tests-gate、雙向門放行等):耗時表被判成文件改動(`--suite docs`)這條,我只確認了 `--shard 3/3 --suite docs` 在表正常時可用。耗時表本身的簿記判定,我沒有獨立驗。

## 未驗範圍

- 沒跑 `--shard 1/1000000000`(怕耗盡本機記憶體)。
- 沒在 CI 環境和 Windows 驗證。
- 沒比對修前的 `--suite keys` 行為。

最嚴重等級 minor,blocking 共 0 條。

驗證用的複本在 `/tmp/lumos-seat-work/code-推送與CI提速-r2/邊界輸入-sonnet/`,按派工詞由編排者刪。
