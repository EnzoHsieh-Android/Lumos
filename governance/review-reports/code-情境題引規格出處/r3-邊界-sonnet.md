severity: minor

## b1 等寫入鎖的最多 60 秒內,Ctrl-C 與 SIGTERM 全被吞掉
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前寫入階段沒有裝處理器,訊號走預設立刻結束;修後 defer=True 把整段包住,含等鎖)

引句:「整段(拿鎖之前到記完帳)在 _situation_rule_signals(defer=True) 裡,SIGTERM、SIGHUP、Ctrl-C 只記下、在檢查點判」

file: `/tmp/lumos-seat-work/code-情境題引規格出處/邊界-sonnet/lumos_after.py:30684`(`_vault_write_lock` 搶不到鎖就每 0.05 秒重試、最多 60 秒)

失敗場景:
1. 另一個程序握著筆記庫寫入鎖,使用者跑 `situation-rule` 通過殺傷力與終端確認,走到 `_situation_rule_locked_write` 的 `with _vault_write_lock(...)`。
2. 這時按 Ctrl-C,或對話工具逾時送 SIGTERM。handler 只把訊號號碼 append 進 `sigs`,不丟例外,所以 `_t.sleep(0.05)` 迴圈繼續轉,最多等 60 秒才回應。
3. 搶到鎖後 `if sigs` 才擋寫入,回 rc 2;60 秒逾時則回「拿不到鎖」。
4. 修前這一段沒有處理器,Ctrl-C 與 SIGTERM 立刻結束,等鎖階段什麼都還沒寫。
5. 這是「收不到訊號」,不會損壞資料,只是對終止訊號變遲鈍。

這一條只讀程式碼推得,沒有實際跑兩個程序爭鎖重現,屬 ⚠ 未重現。要修的話,把等鎖放在 `defer=True` 區塊之外,或等鎖時用 defer=False。

## b2 --keep-worktree 建樹失敗時,印出的「現場保留」路徑已經被刪掉
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前訊息同樣指向不存在的路徑);修後因為連暫存資料夾都收掉,訊息與現實的落差更明顯

引句:「建樹失敗的平台照舊印一行(guard kill 每個平台一行,t_isolated_worktree_shared ⑤);那個路徑本來就沒建出來」

file: `/tmp/lumos-seat-work/code-情境題引規格出處/邊界-sonnet/lumos_after.py:27864`(on_keep 印的是「(--keep-worktree) 現場保留: {p}」)

失敗場景:
1. `guard kill --keep-worktree` 的某個平台 `git worktree add` 失敗。
2. 修後 `finally` 走 else 分支,`rmtree(parent)` 把暫存資料夾刪掉,接著 `on_keep(wt.path)` 印出「現場保留: <路徑>」。
3. 使用者照著去看,路徑不存在,輸出是在說謊。
4. 修前這個路徑也不存在,因為 add 失敗,只是 parent 資料夾與標記還在。
5. 建議建樹失敗時印「建樹失敗,沒有現場可留」。

## 附:三問、圖譜鏡頭

**邊界與合法輸入核對**(載入 `f04090128:scripts/lumos` 以 SourceFileLoader 實跑):
- 命令:`python3.14 t1.py`。
  - `Projects/子/深`(子資料夾)、`Projects/中文_計劃`、`Projects/が`、`Projects/が2`:結果 None,通過。
  - 磁碟上檔名是 NFD、`--plan` 打 NFC 或 NFD:都通過。
  - `Projects/abc` 對實際的 `Abc.md`:拒絕,訊息指出實際檔名。
  - `Projects/子/../中文_計劃`:拒絕。
  - 同一次輸出的磁碟列表顯示,`が.md` 與 `が2.md` 在這個檔系統上以 NFC/NFD 分開存。
- 命令:`python3.14 t2.py`。圖譜根經過符號連結(`vlink` 與 `v/../vlink`)時,`_situation_rule_plan_path_problem` 回 None,沒有誤擋。
- 同一支腳本跑 `_situation_rule_read`:
  - BOM 只在第二行以後:放行。BOM 不在檔頭本來就是合法字元,與 `load_raw_for_edit` 只查檔頭一致。
  - 反引號裡的單獨 CR:拒絕。這是預期,因為 `_note_lines` 會把它當換行,寫回會改成 LF。
  - 空檔、沒有欄位區塊、欄位區塊沒收尾、CRLF:都拒絕。
  - 小問題:沒有欄位區塊時訊息是「沒辦法改欄位」,對人裁寫回略顯誤導,但不影響行為。
- `.MD` 大寫副檔名:`removesuffix(".md")` 只吃小寫,`Projects/X.MD` 會變成 `X.MD.md`,走「找不到計劃」,沒有誤寫。這一條只讀程式碼推,沒實跑。
- consent 原話含換行、CR、ESC 序列、U+202E、U+2028、U+0085、零寬字元、BOM、300 個全形字:命令 `python3.14 t3.py`。
  - 控制字元與不可見字元全部轉成 `\uXXXX` 跳脫輸出,截 200 字,沒有注入行。
  - 空 consent 印空引號,不崩。
  - 編號 S1、S2、S10 依數字排序。
- 尾端換行:`load_raw_for_edit` 用 `split("\n")` 再 `"\n".join`,尾端 `\n` 保留,插條款不會吞掉檔尾換行。
- refs 重複:`set(refs) == {test}` 與規格閘的 `got[1] == {test_name}` 是同一個集合語意,兩邊口徑一致。
- 現有測試:命令 `python3.14 scripts/test_lumos.py -k situation_rule_plan`,結果 5 passed, 0 failed,含 `t_situation_rule_plan_symlink_and_case` 與 `t_situation_rule_plan_path_contained`。其餘測試沒跑。

**三問**
- ①原問題修復的行為證據:路徑、大小寫、BOM、CR、consent 跳脫與符號連結,都有上列實跑結果。雙訊號、記帳訊號、規格閘提醒只讀程式碼確認有檢查點,沒有實際送訊號驗證,判定為未判定。
- ②修補處的相鄰路徑:正常與錯誤路徑都成立。唯一退化是 b1。
- ③同一案例兩版結果:b1 的修前/修後行為只讀程式碼比對,沒有實際重現,標 ⚠ 並已自降為 minor。修補與降複雜度拆函式混在同一個提交,歸因拆不開的部分按 binding 的限制算未判定。

**圖譜鏡頭**:這次沒附固定席筆記(鏡頭計算超時),我也沒自己補算。diff 裡動到的 `Systems/guard-kill.md` 與計劃筆記,只看了 patch 的相關 hunk。`_isolated_worktree` 和 `_situation_rule_signals` 的行為變更,該筆記有寫理由,與程式一致。

最嚴重:minor;blocking 共 0 條
