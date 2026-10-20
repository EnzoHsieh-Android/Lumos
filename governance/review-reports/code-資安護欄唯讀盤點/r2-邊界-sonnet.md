severity: minor
## 邊界鏡頭報告(邊界-sonnet,第 2 輪)

**先說結論:這個鏡頭下沒有 major 或 blocker,有 3 條 minor、都不擋。** 我從固定版本實跑,沒有讀上輪席報告。

**未讀到共用派工詞。** `/private/tmp/claude-501/.../scratchpad/code-seat-common.md` 不存在(用 find 全找過也沒有),所以我只依邊界.txt 本身和 `seclist-r2/codex.txt` 裡的輸出格式(每條 finding 的 severity 與 blocking 各獨立一行、引句至少 10 字)做事。共用詞裡若有額外規則,我沒套到。

**做法:**
- 臨時資料夾:兩個工作樹 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-邊界-before`(20293afe)和 `r2-邊界-after`(aadf6b07)。
- 對照:同一個臨時圖譜、同一條指令跑兩版,比 rc、JSON 可否解析、`errors`。
- 臨時資料已清:工作樹已 remove,`邊界-sonnet` 目錄已用字面絕對路徑刪除。

### Findings

**邊1**
引句:「print(f"擋下:{select_error}", file=sys.stderr)」
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後輸出相同)

選圖譜失敗的訊息走 stderr 時原樣印出路徑,沒有跳脫控制字元。
- 重現:`p4/docs/` 底下放兩個知識圖譜,其中一個目錄名含 `\x1b[31m`,在 `p4` 執行 `lumos security list`。
- 預期:跟 stdout 一樣把 ESC 變成可見的 `\u001b`(計劃寫「文字輸出把控制字元可視化」,不過那句只明講 stdout)。
- 實際:stderr 帶出原始 ESC 位元組。`--json` 的 stdout 有跳脫,stderr 沒有。
- 影響:目錄名可被第三方控制時,有終端注入的口子。
- 兩版:修前 stderr 含 `x\x1b[31mred-knowledge`,修後相同。

**邊2**
引句:「if "flag/security-relevant" in as_list(n.fields.get("tags")) and rel not in registered」
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後一樣漏)

標了 `flag/security-relevant` 的節點,寫法一換就不會被列進 `unregistered_nodes`,而且 rc 0、`registration_complete` 為 true。
- 實測寫法:
  - 會列出:`tags:` 後接區塊清單、純量、單引號、雙引號。
  - 不會列出:行內清單 `tags: [flag/security-relevant]`、逗號分隔 `tags: other, flag/security-relevant`、大小寫不同、`#` 開頭、行尾註解。
- `lumos lint` 對行內清單沒有警告,作者不會被提醒。
- 這是缺口被藏的形狀。程式內建的限制文字只說「沒標籤的散文規則找不到」,沒說標了籤卻漏列也有可能。
- 兩版:`t_flow` 圖譜修前、修後的 `unregistered_nodes` 都是 `[]`;區塊清單那份都列出 `Systems/Tagged.md`。

**邊3(測試缺口)**
引句:「if len(out) >= entries_left:」
severity: minor
blocking: 否
歸因:未判定(修前沒有這道上限,無從比較)

總項目數上限(50000)的剛好邊界沒有被測試釘死。
- 我把 `>=` 改成 `>`(這會讓 50001 個項目放行),`t_seclist_g7` 仍然全綠(5 passed)。
- 原因:該測試放了 50001 個檔,靠別的目錄剩餘額度為負才間接觸發。
- 實際行為目前是對的:剛好 50000 個項目 rc 0,50001 個項目 rc 2 並列 `enumeration_failed`。
- 對比:檔數(10000 / 10001)、單檔(2MiB / +1)、總量(64MiB / +1)都有精確邊界測試,把 `>=` 改成 `>` 會翻紅。只有項目數這條漏了。

**附帶觀察(不算 finding):** 圖譜根目錄權限 000 時,`--vault` 的 JSON 錯誤寫成「不像知識圖譜(底下沒有 Projects、Systems…)」,實際原因是讀不了。rc 2 沒錯,訊息會誤導人。

### 三問

**① 原問題的修復效果有何行為證據**

| 案例 | 修前 | 修後 |
|---|---|---|
| `source.kind` 是 list 或 dict | rc 1,TypeError traceback | rc 2,單一 JSON,`invalid_record` |
| `inventory.assets[].id` 是 list;`surfaces[].asset_ids` 含 list | rc 1,TypeError | rc 2,`inventory_error` |
| `scope` 含孤立代理字元 `\ud800`(文字、`evidence_refs.node`、`decision_ref` 欄位同樣) | `--json` UnicodeEncodeError、rc 1(文字模式 `scope` 那例 rc 0) | rc 2,`invalid_record` |
| JSON 模式輸出含 `\u202e`、`\u2066`、`\u2028`、`\u0085`、`\ufeff`、`\u200b` | stdout 原樣出現,讀回值相同 | stdout 全跳脫,讀回值相同(含 U+1F600) |
| `--vault` 指向不存在路徑、檔案、非圖譜空目錄、捷徑 | 不存在與檔案:rc 2 但 `--json` 沒有 JSON。空目錄與捷徑:rc 0 | 全部 rc 2,且 `--json` 輸出 `vault_selection_failed` |
| 自動找圖譜時圖譜目錄本身是捷徑 | rc 0(跟隨) | rc 2,「是捷徑,不跟隨」 |
| 目錄含 50001 個項目(非 .md) | rc 0 | rc 2,`enumeration_failed` |

這些都是同一組命令、兩版各跑一次的結果。
- 側面印證:把後版測試檔拿去對修前程式跑,`g1`、`g2`、`g3`、`g7` 都翻紅(例如 g1 列出 20 個 TypeError、30 個 rc 錯)。
- `g4`、`g8`、`s03`、`s08`、`s11` 在修前因缺少 `_vault_safe_read_rel` 等符號直接 EXCEPTION,只是「還沒有」,不算行為證據。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立**

仍成立,兩版 rc 與 JSON 形狀一致的案例如下:
- 正常登記:rc 0,`registration_complete` 為 true。
- 中文與空白路徑,自動找圖譜與 `--vault` 皆然。
- NFD 檔名配 NFC 引用。
- BOM、CRLF 的登記檔。
- 空檔,非 UTF-8 檔(rc 2,`not_utf8`)。
- 捷徑檔與捷徑目錄,指向圖譜內外皆拒(`symlink_rejected`,外部哨兵沒被讀)。
- FIFO 的 `.md`(`special_file`)。
- 單檔 2MiB-1、2MiB 照讀,2MiB+1 拒。
- 總量剛好 64MiB 照讀,加 1 位元組拒。
- 檔數剛好 10000 照讀,10001 拒。
- 50000 個項目照讀。
- 目錄深度 400 照讀;1000 與 2000 層回 `enumeration_failed` 並退出 2。
- 無權限讀的檔與目錄(`read_error`、`enumeration_failed`)。
- 同層多個圖譜(報錯不猜)。
- 登記值為 null、陣列、數字、空字串、純空白、NaN、重複鍵、5000 位整數、10 萬層巢狀陣列,共約 50 種。除上表修前會崩潰的幾例外,兩版行為相同,且都是單一 JSON。
- 圍欄變體(縮排、引用、清單前綴、四個反引號、波浪線、結尾多空白、未閉合、兩塊、放在 Projects、放在 frontmatter、大小寫不同)。有的回 `malformed_block`、`unclosed_block` 或 `multiple_blocks`,有的靜默忽略(例如放在更外層圍欄或 frontmatter 裡、標記大小寫不同或寫成 v2),修前修後一致。
- 在行程內注入快照:NFC/NFD 兩份原始路徑撞名列 `normalized_path_collision`。孤立代理字元的檔名與錯誤節點,JSON 與文字都不崩、不洩漏原始代理字元。
- 後版 `-k t_seclist` 全部 280 條斷言通過(最後一輪 195 passed、0 failed)。

**未能驗證:** macOS 的 APFS 對 NFC/NFD 與大小寫不敏感。我無法在磁碟上造出「只差大小寫」或「同字不同正規化」的兩個檔名,只能用行程內注入快照驗證撞名邏輯。非 UTF-8 的檔名也一樣造不出來。

**③ 新發現在修前、修後各是什麼結果:** 邊1 與邊2 在修前修後輸出相同,屬原有漏查,不是修補造成。邊3 是修補新增的上限在測試裡沒被釘死,修前沒有這道上限,所以不適用。

### 已驗正向主張的證據

| claim | input / expected / 出處 | case_source | 命令與結果(before / after) | comparison / attribution |
|---|---|---|---|---|
| 壞型別欄位不再讓指令崩潰 | `source.kind=["invariant"]`、`inventory.assets[0].id=["x"]`,預期 rc 2 單一 JSON(`t_seclist_g1_field_type_fuzz`) | 本席自補(r2-intake.md G1 表只列守護測試名稱,沒給具體輸入) | 兩版各跑 `lumos --vault <圖譜> security list --json`:修前 rc 1 且 stderr 有 TypeError traceback,修後 rc 2 且 JSON 可解析 | 修復成立(有修前紅/修後綠的同一案例) |
| 選圖譜失敗時 `--json` 仍輸出單一 JSON | `--vault` 指向不存在路徑,預期 rc 2 加 `vault_selection_failed` | 本席自補 | 修前 rc 2 但 stdout 空,修後 rc 2 且 stdout 是 JSON | 修復成立 |
| JSON 對雙向控制符與行段分隔符跳脫,讀回值不變 | `scope="x\u202eevil\u2066y\u0007\u001b[31m\u2028\u0085z\ufeff\u200b\U0001F600"`,預期 stdout 無原始特殊字元且讀回相等 | 本席自補 | 修前 raw specials 有 6 種,修後為空,兩版讀回相等 | 修復成立 |
| 容量邊界不變(2MiB、64MiB、10000 檔、50000 項目) | 各取邊界值與邊界加 1,預期恰在加 1 處退出 2 | 本席自補 | 兩版 rc 與錯誤種類逐項相同(50000 項目那條,修前沒有這個上限) | preserve 成立。修前上限不存在的那條只能說「修後新增」,不能算 preserve |
| 正常路徑(中文與空白路徑、BOM、CRLF、NFD 檔名、無權限、捷徑拒讀)不受影響 | 見上表 | 本席自補 | 兩版相同 | preserve 成立;更廣的範圍未判定 |

**未驗範圍:**
- 讀取期間檔案被改動的併發情境(s11),我沒獨立重做,只看到後版測試全綠。
- 非 macOS 平台,以及真正區分大小寫的檔案系統。
- 超過 10 萬層的 JSON 巢狀記憶體用量。
- 3.14 以外的 Python 版本。

**整體無回歸保證:** 我不提供。

改動集中在 `/Users/enzo/orca/workspaces/lumos-toolchain/security-list/scripts/lumos`,相關測試在同目錄的 `test_lumos.py`。

最嚴重 severity:minor,blocking 共 0 條。
