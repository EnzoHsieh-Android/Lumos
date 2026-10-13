severity: major

1. 頂格的 `status`、`source`、`reason` 等題目鍵掉到清單中間時,後面所有題目被靜默丟掉,沒有任何錯誤。這會漏掉後面的阻塞題。
severity: major
   - blocking: 是
   - 最小重現:在 Q1 與 Q2 之間放一行頂格的 `reason: 等人回覆`(Q1 的 `reason` 縮排滑掉),Q2 是 `stage: 架構`、`blocking: true`、`status: 待查`。
   - 修前(`c0265db`):`pq_parse` 回傳 `(12, 'reason 是題目的鍵,卻寫在頂格…')`,`_pq_blocking_open` 回 `['Q2']`,規格閘會擋。
   - 修後(`646dc3a`):`pq_parse` 回傳 `['Q1']`、錯誤清單是 `[]`,`_pq_blocking_open` 回 `[]`,規格閘放行。`lumos lint` 只報 Q1「狀態是延後卻沒有 reason」,Q2 完全不見。
   - 原因:`_pq_scan` 對非旗標的頂格鍵一律 `break` 結束範圍,之後的縮排行不再讀。
   - 修法方向:`break` 之後若還有 `  - id:` 的行,就報讀不懂。
   - 引句:「if name in _PQ_BOOL_KEYS:   # 只擋旗標:掉到頂格就少擋一題;status、source 這類名字筆記本身的頂格欄位也會用(代碼審 r2 邊界席)」
   - file: `scripts/lumos:6999`
   - 同族輸入修前修後都沒擋,第 2 條單獨列。
   - 歸因:有證據的修復回歸。
   - 查證命令(用 `h.py` 載入兩版 `scripts/lumos`):`python3.14 t1.py ./lumos_before` 與 `./lumos_after`,以及 lint 的 `lumos_{before,after} --vault v lint Projects/p_計劃`。結果如上。

2. `Blocking: true`、`BLOCKING: true`、`blocking`+U+200B 加冒號,這幾種寫法一樣會靜默丟掉後面的題。
severity: minor
   - blocking: 否
   - 重現:`Blocking: true` 放在 Q1 與 Q2(blocking)之間。修前與修後輸出相同,都是 `[('Q1', False)] []`。
   - 原因:只有小寫且完全相符的 `blocking`、`irreversible` 才擋,其他名字都算合法頂格鍵而結束範圍。
   - 與第 1 條同根因,第 1 條修好就一併解決。
   - 引句:「name = s.partition(\":\")[0].strip().strip(\"\\\"'\")」
   - file: `scripts/lumos:6958`
   - 歸因:有證據的原有漏查(兩版輸出相同)。
   - 已確認的相鄰寫法:`"blocking": true`、`blocking :true`、`blocking:true`、`irreversible:`(空值)掉到頂格,修後都擋得住,行號正確。
   - 合法筆記本來就有頂格 `blocking:` 欄位的情況:仍整份讀不懂。這是文法表寫明的取捨,repo 內沒有這樣的筆記(`grep` 結果為空),不列問題。

3. `_PATH_SPECIAL_CATS` 含 Cf,合法的 emoji 組合序列與軟連字號會被拒。
severity: minor
   - blocking: 否
   - 重現:`question-add Projects/p_計劃.md "家庭👨‍👩‍👧要不要" --class c --stage 需求`。
     - 修前:寫入成功。
     - 修後:`擋下:題目文字不能換行、含 tab 或控制字元(U+200D),檔案沒動`。
   - 同樣被拒:蘇格蘭旗 `🏴󠁧󠁢󠁳󠁣󠁴󠁿`(U+E0067 標籤字元)、軟連字號 U+00AD。
   - 逐一確認的結果:
     - U+200D、U+200B、U+200C、U+00AD、U+E0067、U+FEFF、U+2060 是 Cf,會被擋。
     - U+FE0F 是 Mn,`心❤️` 放行。
     - 膚色 U+1F3FB 是 Sk,`👍🏽` 放行。
     - 區域指示符旗(`🇹🇼`)是 So,放行。
   - 讀取端也一樣:含 U+200D 的 text 會讓整份清單「無法判定」(`pq_parse` 回 `(4, 'Q1 的 text:值裡有控制字元或換行類字元(U+200D)…')`)。
   - 訊息把 Cf 說成「控制字元」,文字會誤導。
   - 這是 r2 刻意選的取捨(兩端共用規則)。
   - 引句:「return next((c for c in v if unicodedata.category(c) in _PATH_SPECIAL_CATS), None)」
   - file: `scripts/lumos:6928`
   - 歸因:有證據的修復回歸。

4. 推送前的重新命名偵測是對 `git diff` 傳入未清洗的 base,範圍字串以 `-` 開頭會被當成 git 選項。
severity: minor
   - blocking: 否
   - 重現:範圍 `--output=<路徑>..main` 傳給 `_pq_push_remind`。修前不產生檔案,修後在 `<路徑>` 寫出檔案(`ls pwn.txt` 修前 No such file,修後存在)。
   - 影響有限:範圍來自本機 CLI,不是跨信任邊界的輸入。
   - 引句:「r = subprocess.run([\"git\", \"-C\", str(rr), \"-c\", \"core.quotePath=false\", \"diff\", \"-M\", \"--name-status\", \"--diff-filter=R\", base, head, \"--\"],」
   - file: `scripts/lumos:7035`(`_pq_renames`)
   - 修法方向:加 `--end-of-options`,或拒絕以 `-` 開頭的 base/head。
   - 歸因:有證據的修復回歸(`_pq_renames` 是這次新增的 git 呼叫)。

5. 規格閘筆記「管到的檔」仍列已刪除的函式 `_pq_git_read_many`。
severity: minor
   - blocking: 否
   - 這個修補把 `_pq_git_read_many` 整支刪掉。
   - 查證:`git grep -n _pq_git_read_many 646dc3a8 -- docs scripts` 只剩 `規格閘.md:81`。`lumos lint Systems/規格閘` 回報「0 問題」,lint 沒抓到。
   - 其餘三篇的待決問題段落與修補相符(`lumos-cli-write` 的「所有入口都拿鎖」,我用 AST 列出 `atomic_write_verify` 的呼叫者,沒鎖的都在有鎖的外層)。
   - `pitfalls-code-loop.md` 沒有需要更新的內容。
   - 引句:「這篇管 `scripts/lumos` 裡的 `cmd_spec_gate`、`_spec_gate_pending`、`_pq_push_remind`、`_pq_git_read_many`、`_clause_check`」
   - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:81`
   - 歸因:有證據的修復回歸。

6. 決策連結的兩篇只差大小寫(`Projects/A.md` 與 `projects/a.md` 並存)時,連完全相符的路徑也判成 bad。
severity: minor
   - blocking: 否
   - 重現:用 `Env.from_texts` 造兩篇同名只差大小寫,`Projects/A#d1` 得到 `bad`。修前是 `ok`。
   - 這是 fail-closed,只影響區分大小寫的檔案系統;macOS 不會並存。
   - 引句:「hits = list(cache[\"\\0paths\"].get(lit.lower(), []))」
   - file: `scripts/lumos:7111`
   - 歸因:有證據的修復回歸。
   - 其他決策連結輸入都正常:
     - NFD 與 NFC 的 `café` 都解到同一篇。
     - `Other/A` 與 `Projects/A` 只寫短名 `A` 是 bad,帶路徑的各自是 ok。
     - `./`、`//`、前導 `/`、`.md#d1`、`/#d1` 都是 missing 或 bad,沒有例外。
     - `"\0paths"` 鍵與筆記路徑不衝突,沒有人迭代這個 cache。
   - 效能:5000 題、5000 篇只寫短名,修前 39.12 秒,修後 0.01 秒。

7. 範圍字串在推送前被靜默跳過。
severity: minor
   - blocking: 否
   - 重現:`side..nonexist`、`side ..main`、` side..main`、`side.. main`、`side..main..x`,修前修後都完全沒輸出。
   - 原因:head 解不出時被當成「整份計劃被刪」而 `continue`,不印跳過訊息。
   - `..b`、`...b` 修後正確,左端補成 `HEAD`;`main` 這種沒有 `..` 的範圍會印跳過。
   - 引句:「if new is None:   # 整份被刪或改名走:不是刪題」
   - file: `scripts/lumos:7051`
   - 歸因:有證據的原有漏查。
   - 重新命名的兩個情況:
     - 改名到別的資料夾,以及改名加中度改內容,修後都正確報出 Q2 不見了。
     - 改名後相似度低於 50% 的小檔,git 判成「刪除加新增」。我造的例子(`git diff -M --name-status`)輸出是 A 與 D,所以 `_pq_renames` 沒資料,Q2 被刪不會被報。這屬於 git 的限制,舊版本來就沒處理。

   測試名中括號規則已確認:`t_a::b`、`py:t_a`、`TestX.test_y`、`a b`、`t-a/b#c` 修前修後都放行;`t_a[1]`、`[t_a` 修後被拒,符合設計。

**三問**

1. **原問題的修復效果**:有行為證據。
   - `blocking`、`irreversible` 掉到頂格(含引號、冒號前空白、空值)修後報讀不懂,行號正確。
   - 5000 題乘 5000 篇的短名索引從 39 秒降到 0.01 秒。
   - `..b` 與 `...b` 範圍可用,rename 加中度改內容、改名到別的資料夾都能比對題號。
   - 測試名含括號被擋,含 `::`、`:`、`.` 的名字放行。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:大致成立,但頂格鍵的處理有缺口。
   - 正常路徑(`status:` 接在清單最後)讀得懂,這是修補的目的。
   - 錯誤路徑中,旗標掉到頂格仍擋。
   - 相鄰路徑(`status`、`source`、`reason` 等掉到清單中間)從報錯變成靜默丟題,這是第 1 條。
   - 寫入鎖檢查沒有發現呼叫路徑被誤擋。
3. **新發現的同一案例修前修後**:
   - 第 1 條:修前報錯(規格閘擋),修後靜默放行。
   - 第 2 條:修前修後都靜默丟題。
   - 第 3 條:修前可寫,修後被拒。
   - 第 4 條:修前不寫檔,修後會寫。
   - 第 5 條:修前沒有這個過期參照,修後有。
   - 第 6 條:修前 ok,修後 bad。
   - 第 7 條:修前修後相同,都靜默跳過。

總結:第 1 條會擋合併。頂格的非旗標鍵掉到清單中間,會讓後面的阻塞題靜默消失,規格閘放行,這比修前更糟;其餘都是 minor。

(臨時檔放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r3-邊界輸入-sonnet/`,可由編排者刪除。)
