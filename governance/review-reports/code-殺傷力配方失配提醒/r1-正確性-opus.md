severity: major

# 代碼審第 1 輪 正確性席(正確性-opus)

審材:`governance/review-reports/code-殺傷力配方失配提醒/r1-snapshot-code.patch`(基底 51f83721..bd637de7)。
實驗都在自己的 clone(`kcc-r1-work-正確性-opus/repo`,`git clone --shared`)裡跑,用 python3.14.6(macOS,APFS,git 的 `core.precomposeunicode=true`、`core.ignorecase=true`)。對照測試 `t_kill_recipe_check_matches_guard_kill` 在這份 clone 裡是全綠(49 passed)。

## F1 檔名用 Unicode 分解形式(NFD)寫的配方:判斷函式說「不在提交裡」,真跑 guard kill 卻套得上壞法
severity: major
blocking: 是
引句:「why = "不在提交裡(guard kill 的工作樹沒有它)" if os.path.lexists(str(top / rel)) else "不存在"」
佐證:file: `scripts/lumos:13015`(`_kill_tree` 把 `git ls-tree` 的路徑原樣當字典鍵)
佐證:file: `scripts/lumos:13033`(`_kill_path_kind` 用 `modes.get(rel)` 逐字元比對)

1. 判斷函式判斷「這個路徑在不在 HEAD 裡」的做法,是拿配方的 `file` 字串去跟 `git ls-tree` 印出的路徑逐字元比對。真跑的 guard kill 不比對字串,而是對檔案系統做 `os.path.realpath` 加 `open`。macOS 的 APFS 不分 Unicode 正規化形式,所以 NFD 寫法的 `café.py` 也開得到 NFC 寫法存的檔;還原用的 `git checkout -- <file>` 在 `core.precomposeunicode=true`(macOS 預設)下,也會先把參數轉成 NFC,所以還原成功。結果兩邊判得不一樣:判斷函式判 `missing`,guard kill 照常套用壞法、跑測試、還原,拿得到判定。
2. 最小重現(腳本在 `kcc-r1-work-正確性-opus/repro_nfd.sh`):repo 裡提交一支 NFC 檔名的 `café.py`(內容 `LIMIT = 5`),`kill-add --file <NFD 寫法的 café.py>`,提交後跑 doctor,再真跑 guard kill:
   ```
   == kill-add --file <NFD 寫法的 café.py> ==
   ⚠ 提醒:café.py 讀不到(不在提交裡(guard kill 的工作樹沒有它));guard kill 跑到它會判 drifted 或讀檔出錯。修法:lumos guard kill-rm Systems/Limit --id 53710fb768ad,照現在的程式改寫後再 kill-add
   ✓ kill 配方寫入 Systems/Limit.md(…)
   == doctor --verbose 的 P2 段 ==
     ⚠ 有 1 條殺傷力配方的原文對不上程式(guard kill 跑到會判 drifted 或擋下;不擋):
         • Systems/Limit.md → csharp-xunit:café.py:讀不到(不在提交裡(guard kill 的工作樹沒有它))(…)
   == 真跑 guard kill ==
   ✗ survived  上限恆為5 [TestLimitFive]  whole-suite
   rc=1
   ```
   guard kill 判 survived,代表壞法已經套上、還原也成功(這格的測試是假的,所以沒翻紅);判斷函式卻說 guard kill 跑到會判 drifted。照判斷函式的 `_krc_match` 對應表,這就是「missing ↔ drifted」對不上(同一格丟進 `_krc_cell` 實跑,`match=False`)。
3. 後果:kill-add 印一行假提醒、doctor P2 每次都列一條假失配,而且照提醒修會繞回原點:提醒叫人 kill-rm,kill-rm 印出的 kill-add 範本會照抄原本 NFD 寫法的 `--file`(實跑 kill-rm 輸出 `--file 'café.py'`,位元組還是 NFD),照範本重新 kill-add,同樣的假提醒又會出現。畫面上 NFC 跟 NFD 長得一模一樣,使用者看不出差在哪,只看到「檔明明在、卻說不在提交裡」。
4. 同一個根因的變體:大小寫不同(`--file PROD.py`,實際檔是 `prod.py`)。判斷函式一樣判 `missing`「不在提交裡」;guard kill 開檔成功、套上壞法,接著 `git checkout -- PROD.py` 還原失敗,判 error「revert 失敗」。兩邊都判失敗,效果上還算對得上,只是說明寫錯原因(檔其實在提交裡,只是大小寫不同)。
5. 修法方向:在 darwin(或 `core.precomposeunicode` 為 true)時,`_kill_tree` 建字典與 `_kill_resolve` 查詢前,每一段路徑都先轉成 NFC 再比對。大小寫那個變體至少把說明改成「大小寫跟提交裡的 X 不同」。另外對照測試補一格 NFD 檔名,不然日後回歸看不出來。

## F2 還原必定失敗的幾種寫法(`prod.py/.`、`prod.py/x/..`、經過 repo 內資料夾連結):判斷函式判 ok、P2 說「都對得上」,guard kill 每次都判 error,還會讓同組後面的配方一起作廢
severity: minor
blocking: 否
引句:「# realpath 會把結尾斜線吃掉,guard kill 套得上壞法,但接著 `git checkout -- <file>/` 還原失敗、判 error(實跑)」
佐證:file: `scripts/lumos:13824`(guard kill 還原失敗後 `break`,同組剩下的配方都不跑)

1. 實作替「路徑以斜線結尾」開了特例,判 `missing`,理由是「配方永遠拿不到判定」:壞法套得上,但還原一定失敗、判 error。同一類「套得上、還原必敗」的寫法還有至少三種,特例都沒蓋到,判斷函式直接判 `ok`:
   - `prod.py/.` 與 `prod.py/x/..`:realpath 會把它們解析回 `prod.py`,但 `git checkout -- prod.py/.` 還原失敗;
   - 經過 repo 內資料夾連結(`lnk -> src`,`--file lnk/x.py`):git 拒絕還原穿過連結的路徑。實作紀錄把這格明寫成「算套用了」。
2. 重現(腳本在 `kcc-r1-work-正確性-opus/repro_dot.sh`):
   ```
   == kill-add --file prod.py/. ==        (沒有提醒)
   == kill-add --file lnk/x.py ==         (沒有提醒)
   == doctor P2 ==
     ✓ 殺傷力配方的原文都對得上
   == guard kill ==
   prod.py/. error revert 失敗——後續同組配方作廢防污染
   ```
   另外用 probe 對 `_krc_cell` 逐格實跑:`prod.py/.`、`prod.py/x/..` 兩格的判斷函式都是 `ok`,guard kill 都是 `error / revert 失敗`。
3. 照 S5 字面的對應表(ok ↔ 沒判 drifted、也沒判逃逸)這些不算對不上,所以我只標 minor。但結果是:P2 說全部對得上,guard kill 卻每次回傳碼 2;而且因為 `break`,同組排在後面的配方全部跑不到。重現裡第二條 `lnk/x.py` 根本沒被跑,P2 照樣說沒事。這跟實作自己替結尾斜線寫的理由互相矛盾。
4. 修法方向:把「還原一定失敗」當成一類判 `missing` 並寫明原因,例如原始 `file` 在 `os.path.normpath` 前後不同、或解析時經過了連結(guard kill 用原字串做 `git checkout --`)。如果刻意不做,至少在 Systems/guard-kill 的說明裡寫這類 P2 看不出來。

## 已查證、沒有問題的部分(不算 finding)

- **解析器跟 Python 3.14.6 的 `posixpath.realpath`(非 strict)對過原始碼**:`.` 與空段略過、`..` 照字面退一層、不存在的段照字面接上、`seen` 快取與迴圈停在連結本身、相對目標從連結所在的資料夾續走、絕對目標一律落在 wt 外,邏輯都對得上。自己另外試的格子也全部對得上:`./prod.py`、`a.py/../b.py`、經子模組空資料夾再 `..`、連到 `..` 的連結再接 `wt`/`wtfoo`。
- **跟 HEAD 比對**:用 `ls-tree -r --full-tree HEAD`,子模組(160000)當空資料夾、連結(120000)跟著走,這跟 guard kill 的工作樹一致。連結目標讀工作目錄,在工作目錄改了連結目標又還沒提交時兩邊會不一樣(probe `linkretarget` 實跑:判斷 hits、guard kill 套上了)。這點實作紀錄已經寫明,跟「內容讀工作目錄」是同一種取捨,不另外報。
- **kill-add 搬進上鎖函式**:逐行比對過新舊版本,參數檢查、判重、組配方、重寫開頭欄位、寫後自驗、輸出都一字不差。差別只有三處:只更新 covers 時多了 `recipe = r`、判重擋下那句改成指向 kill-rm、寫入前多一次 `_kill_add_warn`。設定讀取的警告被 `redirect_stderr` 接走,`load_platforms` 與 `load_test_profile` 只會印到標準錯誤,所以標準輸出不變。鎖可以重入,不會自己卡自己。
- **kill-rm**:doctor P2 印的短身分直接貼給 kill-rm,實跑移除成功(同一個節點字串、同一支身分函式)。短身分格式檢查、零條與多條擋下、同一身分的重複一起移除、壞配方的身分重新序列化後不變、寫後自驗比對每個身分的出現次數、移光時整欄拿掉、KEY 行標記只在被移除的配方對得到、剩下的都對不到時才拿掉,這些都對。
- **doctor P2**:沒有 `docs/` 時跳過、設定檔讀不了的字面跟整段兜底分得開、只印軟提醒不影響回傳碼、`check-p2` 已登記進 `_KNOWN_GATES`,都確認過。

最高等級:major
