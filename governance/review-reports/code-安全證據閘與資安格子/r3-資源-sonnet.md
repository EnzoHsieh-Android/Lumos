severity: minor

## 結論(白話)

這一輪補的是「別讓外部呼叫卡住、別讓迴圈沒有時限」。逐項核對下來,git 呼叫與 ssh-keygen 的時限都有接到整道預算。上限超過時也是擋下或記錯,不是默默截斷。只找到一條記憶體的小問題,而且只是舊做法的延伸,不是這次補壞的。

## 1. 收證快照讀取沒有總量上限
severity: minor
blocking: 否

引句:「got = ctx.tree.read_many(on_tree, _SECEV_FILE_MAX, deadline=ctx.deadline) if on_tree else {}」

失敗場景:
- `_secev_tq_source_problems` 把 baseline 收據快照裡列的所有路徑,一次批次讀進記憶體。
- 它只給了單檔上限 16MB(`_SECEV_FILE_MAX`),沒給 `max_total`。
- 整道判定的讀取總額度 `_SECEV_TOTAL_MAX`(256MB)也繞過了。額度預掃只涵蓋證據項的 `path`、`coverage_path`、`calibration_path`,不含快照路徑。讀進來的內容還全部留在 `_SecevTree._cache`。

實量:
- 我在臨時 repo 放了 40 個 15MB 的檔(共 600MB),直接呼叫 `_SecevTree.read_many`,deadline 設 60 秒。
- 指令是 `python3.14 /tmp/lumos-seat-work/code-安全證據閘與資安格子/資源-sonnet/m.py`,載入的是 474346765 版的 scripts/lumos。
- 結果:40 個檔全讀進來、共 600000000 位元組、0.66 秒、`ru_maxrss` 約 2.1GB。這是 macOS 回報的位元組值,上面程式把它除以 1e6,所以約等於 2118MB。
- 超過 256MB 額度後沒有任何擋下或標記。
- 我沒有從 `security evidence` 走完整條路徑重現,只量了這個讀取函式。

歸因:未判定。
- 同類的舊讀法本來就存在:`_secev_tq_phase` 的 `get()` 走 `ctx.read`,也讀快照檔本體,同樣不受額度預掃管。這條補丁等於多加了一份同類的讀取。
- 修前版(7655a12d)我沒另外跑,所以不能說這是補丁造成的回歸,也不能說它在修前不存在。
- 這是作者自己要推的證據,沒有敵對輸入,所以我只標 minor。
- 建議把 `max_total=ctx.budget_left` 傳進去,超過就記 `evidence_too_large`,跟其他證據檔一致。

## 已驗主張(附證據)

- **截止時間有傳到**,逐項看 474346765 版原始碼:
  - `_SecevTree.__init__` 在 `_nodehome_list` 之前就用 `_git_timeout(deadline, cap=60)` 算單次上限,沒時間丟 `_SecevTimeout`。
  - `_secev_snap_clash` 同樣處理,列不出來還會記 `enumeration_failed`,不當成沒碰撞。
  - `_secev_is_shallow` 把 `subprocess.TimeoutExpired` 轉成 `_SecevTimeout`。
  - `_secev_mainline_override` 的 sizes 與 blobs 兩趟共用同一個 deadline。
  - `bookkeeping_only` 在 deadline 用完時丟 `_SecevTimeout`。
  - `_secev_snap_md` 每 1000 項查一次截止時間。
  - ssh-keygen 在 `_secapr_verify_sig` 用 `_git_timeout(deadline)` 當逾時,並在逾時時丟 `_SecevTimeout`。`_secapr_verify` 每一筆驗章前都呼叫 `_secapr_tick(deadline)`。子行程由 `subprocess.run(timeout=)` 逾時時自動殺掉並收掉。
- **超過上限是擋,不是默默截斷**:
  - 核可鏈超過 2000 筆(`_SECAPR_MAX_ENTRIES`)丟 `_SecaprTooLong`,整道判 `read_incomplete`。
  - 設定檔或核可鏈超過單檔上限回 `too_large`,也判 `read_incomplete`。
  - 主線 tip 版的 config 超過上限判 `mainline_unknown`。這是新補的,不再當成「沒設」。
  - 檔數或項目超過上限會記 `too_many_files` 錯誤再截,不是無聲截斷。
- **預檢那條 50 個 ref 的上限**(`_secev_main_side_trace`)超過就回 None,走完整判定再由 `mainline_unknown` 擋,不是放行。每次 `git grep` 都帶 deadline。
- **舊的逐檔 `ls-tree` 已拿掉**(`_secev_tree_mode_link`)。連結檔判斷改用列樹時一併取得的模式(`tree.modes`),git 呼叫次數從 O(連結檔數) 降到 0。程式裡沒有再用到 `.special(`,所以它每次建 set 的 O(N) 成本沒有被迴圈放大。
- **小的時限超出(未量測、不構成 finding)**:
  - `bookkeeping_only` 內部最多跑 3 組 git,每組都用同一個「剩餘預算」當單次上限,最壞合計可超出預算約 2 倍剩餘秒數(單次還受 `cap=20` 限制)。
  - 之後仍會因 `unsure` 且預算 ≤ 0 而丟 `_SecevTimeout`,所以不是無限等待。

## 回答三問

1. 原問題的修復效果:時限傳遞與 git 失敗當成「讀取不完整」這兩項,我只做了原始碼層的核對,沒有跑修前、修後的對照實驗。連結檔判斷從逐檔呼叫 git 改成一次取得,這個設計上能消除 O(n) 的 git 呼叫,但我沒量出 3000 連結檔的前後秒數。那個「80 秒」是補丁註解寫的數字,不是我量的。所以這幾項的行為證據是未判定,只有原始碼證據。
2. 修補處相鄰路徑是否仍成立:`_nodehome_list` 與 `_nodehome_git` 新增的參數都有預設值(`timeout=20`、`modes=None`)。沒傳 deadline 的呼叫端(`_secapr_cmd_verify` 的 `_SecevTree(root, sha)`)行為不變。`_secev_mainline_override` 回傳形狀仍是「單一 None」或 3 元組,沒變。
3. 新發現的修前、修後:第 1 條沒有跑修前版,所以填「未判定」。

未驗範圍:
- 沒跑 `python3.14 scripts/test_lumos.py`。
- 沒量 JSON 深度。
- 沒量 `security approvals verify` 與 `security-approval-add` 在 `deadline=None` 下的總時間(2000 筆乘上每筆最多 20 秒的最壞情形)。這是舊行為,不在補丁內。
- 沒測多程序。

最嚴重 severity: minor,blocking 共 0 條。
