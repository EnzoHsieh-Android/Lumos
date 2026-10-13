severity: minor

我沒找到會擋合併的問題。兩條 minor 都不擋合併。修法下的 `-k qfm`、`-k guard`、`-k kill` 三組子集在修後版本全綠(216、819、436 案例,0 失敗)。

做法:我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r5-通才回歸-sonnet/` 下用 `git clone --shared` 取出修前 `d6bb423f` 與修後 `48b327b0`。同一份臨時筆記庫(兩個 Systems 節點加一篇計劃節點、一個 git repo)各建一份,兩版逐支比 stdout、stderr、rc。

**guard 子指令**:parser 裡有 13 個,我全跑了正常與錯誤呼叫:list、scaffold、plan、settle、abandon、required、bind、audit、trace、kill-add、kill-rm、kill,另加未知子指令與沒給子指令。
- 修前修後輸出逐字相同,rc 也相同。唯一差異是 `head_sha` 與 `lumos-kill-*` 暫存目錄名,這兩個本來每次都不同。
- 搬進 `_guard_dispatch` 後沒有 NameError。函式裡只用到參數 `env`、`args` 和模組層的 `cmd_guard_*`。
- `guard kill` 讀到非 UTF-8 檔仍是 rc1。我用 `kill-add --file bad.py` 加一條指到非 UTF-8 檔的配方,修前修後都丟 `UnicodeDecodeError`、rc1。`UnicodeDecodeError` 是 ValueError,不會被新的 except 接走。
- 讀寫失敗的類型:`chmod 000` 筆記、唯讀的 Systems 資料夾、指到不存在檔案的符號連結,各自跑 bind、audit、plan。修前是裸追蹤加 rc1,修後是 `擋下:[Errno …]` 加 rc2。這是這輪設計的行為,見 finding 2。

**寫入路徑**(`lumos set`、`question-add`):

| 情境 | 修前 | 修後 |
|---|---|---|
| vault 本身是符號連結 | 寫得進 | 寫得進 |
| 相對路徑 vault、`--vault .`、尾端斜線 | 寫得進 | 寫得進 |
| 庫內資料夾是指到庫外的符號連結 | 寫得進 | 寫得進 |
| 筆記是指到庫內他處的符號連結 | 寫得進,但連結被換成一般檔 | 同修前 |
| 筆記是指到庫外的符號連結 | rc2 擋下 | rc0,連結被換成一般檔(finding 1) |

- 兄弟前綴目錄(`kg` 與 `kg2`)的情況由修後的 `t_qfm_r4_folds` ④ 覆蓋,我沒另外跑。
- 核心圖譜當 vault:原始碼裡 `CORE_KNOWLEDGE_ROOT` 只在讀取處出現,沒有獨立的寫入路徑,所以等同一般 `--vault`。

**圖譜鏡頭**:
- `Systems/lumos-cli-write.md` 的 WHY 行寫「守衛子指令在分派層統一接」,指的是拿鎖逾時,沒提 OSError 也一併轉成 rc2(finding 2)。
- 同一行寫「筆記本身是符號連結時只解析它所在的資料夾來判在不在庫裡」,沒說連結會被換成一般檔(finding 1)。
- `lumos-cli-read.md`、`規格閘.md`、`bound-tests-gate.md` 裡待決問題相關的行,與修後程式沒有矛盾。

severity: minor
blocking: 否
Finding 1:筆記是指到庫外的符號連結時,寫入「成功」但實際把連結換成一般檔,外部原檔不動。
- 輸入:`Projects/ol_計劃.md` 是指到庫外 `ext.md` 的符號連結,執行 `lumos set Projects/ol_計劃 status doing`。
- 走到哪:`_vault_lock_held_for` 改成只解析資料夾後放行,接著 `atomic_write_verify` 呼叫 `_write_lf`,最後 `os.replace` 換掉連結本身。
- 修前:rc2,訊息是「沒拿寫入鎖,這是工具本身的漏洞」,訊息誤導,但沒有寫入。
- 修後:rc0 並印「✓ status 已改成 doing」,`ls -l` 顯示變成 `-rw-r--r--`,`ext.md` 的 status 仍是 draft。
- 這個行為在庫內符號連結 `hl.md -> ../Systems/H.md` 的 `set` 上,修前修後都一樣,所以不是這次新增的。
- 修補的測試 `t_qfm_r4_folds` ③ 只檢查 rc0,沒檢查連結還在、內容寫到哪。
- 歸因:未判定,偏向有證據的原有漏查(`_write_lf` 沒被這次修補碰)。
引句:「只解析資料夾:筆記本身是符號連結時仍算在庫裡」
- file: `scripts/lumos:19999`
- 查證:兩版各跑 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r5-通才回歸-sonnet/wp.sh`(修前 case c 為擋下、修後為成功;case b 兩版皆換成一般檔)。

severity: minor
blocking: 否
Finding 2:所有 guard 子指令的 OSError 改成 rc2「擋下」,但圖譜只記了拿鎖逾時。
- 輸入:`chmod 000 Systems/G.md` 後執行 `lumos guard bind Systems/G 未綁 t_new`。
- 走到哪:`load_raw_for_edit` 的 `read_bytes` 丟 `PermissionError`,被 `main()` 的 `except (RuntimeError, OSError)` 接住。
- 修前:裸追蹤加 rc1。修後:`擋下:[Errno 13] …` 加 rc2。
- 這是設計內的行為,測試全綠,所以不擋合併。
- 缺口:圖譜只寫拿鎖逾時,沒寫讀寫失敗也轉 rc2。依 CLAUDE.md 鐵則一,這該補進 `Systems/lumos-cli-write.md`。
- 歸因:有證據的修復回歸(行為改變,屬刻意)。
引句:「守衛子指令多半會拿寫入鎖:拿鎖逾時(RuntimeError)與讀寫失敗(OSError)一律」
- file: `scripts/lumos:52905`
- 查證:兩版各跑 chmod 000、唯讀資料夾、壞符號連結三種情境,見 `chain.sh` 的輸出 `chain_before` 與 `chain_after`。

**三問**
1. 原問題的修復效果:`t_qfm_r4_folds` 在修後版本通過,涵蓋清單後接 decisions 等區塊、標籤字只在旗幟序列放行、符號連結筆記、鎖逾時回擋下、`--push-check=` 帶 `-` 開頭範圍不寫檔。守衛 plan、abandon 與 decision-amend 的鎖逾時回 rc2 也由同一支測試用模擬鎖驗過。我另外實跑了符號連結筆記(寫得進,但見 finding 1)。
2. 修補處的正常、錯誤與相鄰呼叫路徑:成立。13 個 guard 子指令的正常與錯誤呼叫兩版一致;rc1 的非 UTF-8 約定保留;唯一的行為差異是 OSError 由追蹤 rc1 改成 rc2 擋下。
3. 新發現案例的修前修後:
   - 庫外符號連結筆記的 `set`:修前 rc2,修後 rc0 且連結被換成一般檔。
   - 不可讀或唯讀的筆記上跑 bind、audit、plan:修前追蹤 rc1,修後擋下 rc2。

整體:修補沒有打壞既有 guard 與寫入功能,只剩上述兩條不擋合併的小問題。
