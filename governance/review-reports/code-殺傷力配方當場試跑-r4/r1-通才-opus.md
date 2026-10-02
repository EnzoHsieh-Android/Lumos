severity: major

# 殺傷力配方當場試跑 代碼審 r4 第 1 輪 通才-opus 席報告

臨時目錄:`trc-r4-work-通才-opus/`。`repo` 是 573d911e(被審版本),`repo-r3` 是 ed16a50f(這段修正之前,當對照組)。窮舉腳本是 `grid.py`(每一格自己一個 repo,照 `_mk_kill_env` 的形狀造,另外多放一支空檔 `empty.py` 和兩個連結 `plink.py`→`prod.py`、`elink.py`→`empty.py`),彙整用 `summ.py`,F1 的最小重現是 `repro_f1.py`。原始結果在 `out-all/grid.json`。

## 核對摘要(白話)

- **這次修正讓大部分怪配方不再當掉。** old 或 new 是數字、null、清單或缺欄位,不管 file 是正式寫法、`./` 開頭、連結還是只差大小寫,也不管帶不帶 `--id`、帶不帶合約片段、用 `--json` 還是人讀,一律判 error「配方欄位格式不對」並回 2。`--json` 時標準輸出恰好一行。修正前這些格子多半是回 1 加 Traceback(對照組實跑過)。
- **漏了一類(F1,major)。** 原地擋只檢查型別。判法認定「套壞法時會當掉」的另外兩種情形沒有擋:old 沒寫而且檔是空的,以及 new 帶替身字元。file 不是正式寫法時(判法停在 path),帶 `--id` 會照樣當掉、回 1。這跟第 3 輪 F1 是同一個形狀,只是換了欄位。
- **② 位置與順序:** old 型別放在數原文之前、new 型別放在原文恰好一次之後,跟 `_kill_judge_file` 一致(old=5 加正式路徑:判法 malformed ↔ guard kill error;new=5 加原文 0 次:兩邊都是 hits/drifted)。對照測試 `_krc_match` 把「配方欄位格式不對」算成 malformed 之後仍然是真的對照,可以在 `t_kill_recipe_check_matches_guard_kill` 92 格全綠的情況下逐格分清。不過對照表裡沒有「正式路徑加 old 不是字串」那一格,這次新加的 old 原地擋沒有被對照到。另外「old 沒寫加空檔」「new 帶替身」兩格只是靠「當掉也算 malformed」才對上,看不出 guard kill 跟判法其實判得不一樣(就是 F1)。
- **③ 不帶 `--id` 的回傳碼與 `--json` 純度:** 每一格回 0 或 1、沒有當掉時,標準輸出都恰好一行 JSON。回傳碼的變化都是「當掉回 1 → 擋下回 2」,只有一個例外:invariant 是清單或物件、又帶合約片段時,修正前會照跑,修正後判成沒有配方可跑,回 2(F4,minor)。
- 跑過的測試:`-k guard_kill_only_ids` 19 passed;`-k kill_recipe_check_matches_guard_kill` 92 passed;`-k guard_kill_json_purity` 6 passed;`-k guard_kill_rc_precedence` 4 passed。
- 固定席(`lumos impact --diff ed16a50f..573d911e`):跟這次有關的是 guard-kill 的兩條合約。「rc 優先序」這條:新的原地擋記成 error,回 2,符合合約;但每一個還會當掉的格子都回 1,跟 survived 同一個碼(F1–F3)。「--json 成功時恰一行」這條:沒當掉的格子全部守住。其餘固定席節點(bound-tests-gate、測試假綠形態、design-loop、slim 系列等)這段修正沒有碰到它們的程式路徑,答「不受影響」。

## F1 原地擋只檢查型別,判法認定會當掉的「old 沒寫」和「new 帶替身字元」沒擋到;file 不是正式寫法時,帶 --id 照樣當掉回 1
severity: major
blocking: 是
引句:「old/new 不是字串:記成 error、不當掉(順序照 _kill_judge_file」
file: `scripts/lumos:14193`(判法套壞法那一步判 malformed 的條件:`if "old" not in r or not isinstance(new, str) or any(unicodedata.category(c) == "Cs" for c in new):`)
file: `scripts/lumos:15183`(guard kill 原地擋只寫了 `if not isinstance(r.get("new"), str):`)
file: `scripts/lumos:15188`(`_tf.write(src.replace(r["old"], r["new"], 1))`:沒寫 old 時 KeyError;new 帶替身字元時寫回 UTF-8 出 UnicodeEncodeError)

1. 判法自己的註解寫明,套壞法那一步會當掉的情形有三種:「old 沒寫(數的時候當空字串,空檔剛好一次)、new 不是字串、new 含寫不成 UTF-8 的替身字元」。這段修正原地擋只放了「new 不是字串」,前一步也只擋「old 不是字串」。沒寫 old 時,`r.get("old", "")` 拿到空字串,不會被型別檢查擋下;空檔的 `"".count("") == 1`,於是走到 `r["old"]`。
2. file 是正式寫法時,`--id` 靠判法擋得住這兩種(判法回 malformed)。可是 file 是 `./empty.py`、連結或只差大小寫時,判法停在 path、不看 old/new,`--id` 放行,guard kill 就在第 15188 行當掉。這就是第 3 輪 F1 的形狀(「判法停在 path → --id 放行 → 碰到會當掉的那一步」),這輪換形狀只補了其中兩個條件。
3. 最小重現(`repro_f1.py`,每段一個新 repo;`empty.py` 是提交裡的空檔,Python 專案裡空的 `__init__.py` 很常見):
   ```
   == old 沒寫、file=./empty.py: guard kill Systems/Limit --id bd454d5a7e43 --json
   rc= 1 stdout= ''
   stderr 末兩行: [..., "KeyError: 'old'"]
   == new 帶替身字元、file=./prod.py: guard kill Systems/Limit --id 33a8166258b0 --json
   rc= 1 stdout= ''
   stderr 末兩行: [..., "UnicodeEncodeError: 'utf-8' codec can't encode character '\\ud800' in position 1: surrogates not allowed"]
   ```
   網格裡 `old=缺+空檔`、`new=替身` 在 `./`、連結、大小寫三種寫法下,帶 `--id` 的 4 個組合全部是 `1💥`。正式路徑帶 `--id` 會擋下並回 2。對照組 ed16a50f 結果一樣,所以這不是這段修正帶進來的回歸,而是它想收掉的那一類沒有收乾淨。
4. 跟條款不符:S1 寫「對到格式壞的配方時應回 2、印出 kill-rm 指令、不當掉」;計劃〈範圍〉寫「只保證 `--id` 不會把人帶進那個崩潰」。當掉時回 1,跟 survived 同一個碼(違反 guard-kill 的 rc 優先序合約精神),`--json` 的標準輸出是空的。
5. 建議用一條統一規則:把判法第 14193 行那個條件抽成一支小函式(例如 `_kill_new_unappliable(r)`),判法和 guard kill 第 15183 行共用,不要再逐條補。補完後在 `t_guard_kill_only_ids` ⑥d 加這兩種形狀(`./empty.py` 加沒寫 old、`./prod.py` 加 new 帶替身)。對照測試也加一格「正式路徑加 old 不是字串」,把這次新加的 old 原地擋納進對照。

## F2 Issue 的「還會崩的」清單跟實測對不上:漏列三種會崩的,而 --id 實際擋下的不只「前兩種」、帶 --id 仍會崩的也沒講
severity: minor
blocking: 否
引句:「還會崩的:元素不是物件、file 是數字、platform 是陣列、替身字元那幾種(guard kill --id 對到前兩種會先擋下)」
file: `scripts/lumos:15248`(`res["covers"] = [c for c in (res.get("covers") or []) if isinstance(c, str)]`)

1. 不帶 `--id` 會當掉、卻沒列進清單的(網格實測,對照組也一樣):`old 沒寫 + 空檔`(正式路徑也會崩,KeyError)、`file 含 NUL`(ValueError)、`covers` 是數字或布林(TypeError,見 F3)。下一個 session 讀這篇時,會以為只剩那四種。
2. 「--id 對到前兩種會先擋下」寫得比實際少:網格裡 `--id` 也會擋下 platform 是清單或物件、file 是 null、清單或含 NUL、test 帶替身字元(全部回 2)。反過來,帶 `--id` 仍然會崩的替身字元情形沒有寫出來:invariant、platform、file 帶替身字元時,人讀和 `--json` 都崩;old 帶替身字元時只有 `--json` 會崩。這些格子的例外全是 UnicodeEncodeError、回 1。
3. 建議照網格把這一行改寫成「不帶 `--id` 還會崩的」和「帶 `--id` 還會崩的」兩份清單,每份附一種形狀。

## F3 covers 不是清單(或配方多寫了數字型的 detail)時,帶不帶 --id 都會當掉;判法不把它算成格式壞,--id 照樣放行
severity: minor
blocking: 否
引句:「guard kill 碰到會當掉的兩步已原地擋」
file: `scripts/lumos:15248`(`res.get("covers") or []` 遇到 5 或 true 時迭代整數或布林)
file: `scripts/lumos:15239`(整套一起跑時 `res.get("detail", "") + note_ws`,配方帶 `"detail": 5` 時 int 加 str)

1. 網格中 `covers=5`、`covers=true`、`detail=5` 三種形狀,在正式、`./`、連結三種寫法下的 8 種組合全部是 `1💥`(TypeError,回 1;`--json` 時標準輸出是空的)。對照組 ed16a50f 一樣,屬於既有問題,不是這次造成的。
2. 跟這段修正的關係:註解寫「guard kill 碰到會當掉的兩步已原地擋」,意思是兜底放行沒有風險。但 covers 是 kill-add 會寫的正式欄位,手改成不是清單時,判法不判 malformed、P2 不列、`--id` 放行,guard kill 照樣當掉、回 1,跟 survived 同一個碼。前提是要有人手改筆記,出現機率低,所以標 minor。
3. 建議:蓋章那一行改成 `covers if isinstance(covers, list) else []`(或記成 error),detail 先轉成字串再相加;不然至少把這種情形列進 F2 那份清單。

## F4 合約片段過濾改成只比字串之後,invariant 是清單或物件的配方從「照跑」變成「沒有配方可跑」;不帶 --id 的回傳碼跟著變,註解寫的「原本會當掉」也不對
severity: minor
blocking: 否
引句:「invariant 不是字串的不算對到(原本會當掉;代碼審 r3 通才席)」
file: `scripts/lumos:15056`

1. 對照組 ed16a50f 實跑:`inv=["上限恆為5"]` 或 `{"上限恆為5": 1}` 加片段 `上限恆為5`、不帶 `--id`,結果是回 1、照跑(killed_unattributed),因為 `"x" in ["x"]` 和 `"x" in {"x": 1}` 都是 True,不會當掉。被審版本是回 2,印「沒有任何突變配方可跑」。數字和 null 在修正前確實會當掉(TypeError)。
2. S1 寫「不給 `--id` 時行為跟現在一樣」,這兩種形狀的回傳碼變了。結果比較嚴格,本身說得通,但註解把所有「不是字串」都講成「原本會當掉」,Issue 也只寫「不崩潰」,沒有記下「清單和物件原本會照跑,現在被濾掉」這個行為變化。
3. 建議:把註解改成實際的行為(清單和物件原本照跑、現在不算對到),在〈實作紀錄〉補一句;或者改成 `str(invariant)` 再比,保留原本的行為。

## 範圍外的觀察(不立 finding)

- macOS 上 file 寫成只差大小寫(`Prod.py`)時,不管配方長怎樣,guard kill 都判「revert 失敗——後續同組配方作廢防污染」、回 2。還原用的是 `os.path.relpath(realpath(...))`,而 macOS 的 realpath 不會把大小寫轉成 git 索引裡的寫法。這是既有行為,跟這段修正無關,P2 也已經把它判成 path 並請人改寫。

## 窮舉結果表

欄位:`無id`/`id` 表示帶不帶 `--id`;`+片段` 表示帶合約片段 `上限恆為5`;`/人`、`/J` 表示人讀或 `--json`。格內是回傳碼;`💥` 表示標準錯誤有 Traceback;`✗J` 表示 `--json` 時標準輸出不是恰好一行 JSON(只出現在當掉的格子)。測試環境的 run_cmd 不帶 `{method}`(整套一起跑),所以好配方是 killed_unattributed、回 1,這是既有的弱證據規則,不是錯。最後一欄是判定或例外類型,以及擋下訊息的開頭。

| 形狀 | file | 無id/人 | 無id/J | 無id+片段/人 | 無id+片段/J | id/人 | id/J | id+片段/人 | id+片段/J | 判定/例外 |
|---|---|---|---|---|---|---|---|---|---|---|
| good | 正式 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| good | ./ | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| good | 連結 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| good | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error, |
| elem=str | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | AttributeError; 擋:第 1 條配方欄位格式不對(不是物件,是 s |
| elem=int | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | AttributeError; 擋:第 1 條配方欄位格式不對(不是物件,是 i |
| elem=null | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | AttributeError; 擋:第 1 條配方欄位格式不對(不是物件,是 N |
| elem=list | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | AttributeError; 擋:第 1 條配方欄位格式不對(不是物件,是 l |
| inv=5 | 正式 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=5 | ./ | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=5 | 連結 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=null | 正式 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=null | ./ | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=null | 連結 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=null | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=list | 正式 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=list | ./ | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=list | 連結 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=list | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=dict | 正式 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=dict | ./ | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=dict | 連結 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=dict | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=缺 | 正式 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=缺 | ./ | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=缺 | 連結 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=缺 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error,; 擋:沒有任何突變配方可跑——先用 lumos k |
| inv=替身 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| inv=替身 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| inv=替身 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| inv=替身 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| file=5 | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(file 不是字 |
| file=null | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(file 不是字 |
| file=list | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(file 不是字 |
| file=缺 | — | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (file 路徑逃逸 worktree(圍欄擋下)); error, |
| file=NUL | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | ValueError; 擋:第 1 條配方欄位格式不對(file 不是字 |
| file=替身 | — | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| old=5 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 不是字串 |
| old=5 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=5 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=null | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 不是字串 |
| old=null | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=null | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=null | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=list | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 不是字串 |
| old=list | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=list | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=list | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(old 不是字串)); error, |
| old=缺 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | drifted (old 命中 48 次(需恰 1——配方漂移,重寫)); drifted, |
| old=缺 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | drifted (old 命中 48 次(需恰 1——配方漂移,重寫)); drifted, |
| old=缺 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | drifted (old 命中 48 次(需恰 1——配方漂移,重寫)); drifted, |
| old=缺 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | drifted (old 命中 48 次(需恰 1——配方漂移,重寫)); drifted, |
| old=缺+空檔 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | KeyError; 擋:第 1 條配方欄位格式不對(old 或 ne |
| old=缺+空檔 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | KeyError |
| old=缺+空檔 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | KeyError |
| old=缺+空檔 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | KeyError |
| old=空字串+空檔 | 正式 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | survived ( whole-suite); survived, |
| old=空字串+空檔 | ./ | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | survived ( whole-suite); survived, |
| old=空字串+空檔 | 連結 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | survived ( whole-suite); survived, |
| old=空字串+空檔 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error, |
| old=替身 | 正式 | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | UnicodeEncodeError; drifted, |
| old=替身 | ./ | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | UnicodeEncodeError; drifted, |
| old=替身 | 連結 | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | UnicodeEncodeError; drifted, |
| old=替身 | 大小寫 | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | 2 | 1💥✗J | UnicodeEncodeError; drifted, |
| new=5 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 或 ne |
| new=5 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=5 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=null | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 或 ne |
| new=null | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=null | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=null | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=list | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 或 ne |
| new=list | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=list | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=list | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=缺 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error,; 擋:第 1 條配方欄位格式不對(old 或 ne |
| new=缺 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=缺 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=缺 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (配方欄位格式不對(new 不是字串)); error, |
| new=替身 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | UnicodeEncodeError; 擋:第 1 條配方欄位格式不對(old 或 ne |
| new=替身 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| new=替身 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| new=替身 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| test=5 | 正式 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| test=5 | ./ | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| test=5 | 連結 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| test=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error, |
| test=null | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=null | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=null | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=null | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=list | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): "['TestLimitFi); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=list | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): "['TestLimitFi); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=list | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): "['TestLimitFi); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=list | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): "['TestLimitFi); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=缺 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=缺 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=缺 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=缺 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (test 名不合法(拒注入): ''); error,; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=替身 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | UnicodeEncodeError; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=替身 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | UnicodeEncodeError; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=替身 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | UnicodeEncodeError; 擋:第 1 條配方欄位格式不對(test 名 " |
| test=替身 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | UnicodeEncodeError; 擋:第 1 條配方欄位格式不對(test 名 " |
| plat=5 | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 '5' 不在 config); error, |
| plat=5 | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 '5' 不在 config); error, |
| plat=5 | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 '5' 不在 config); error, |
| plat=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 '5' 不在 config); error, |
| plat=list | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=list | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=list | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=list | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=dict | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=dict | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=dict | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=dict | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 2 | 2 | 2 | 2 | TypeError; 擋:第 1 條配方欄位格式不對(platform |
| plat=nope | 正式 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 'nope' 不在 config); error, |
| plat=nope | ./ | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 'nope' 不在 config); error, |
| plat=nope | 連結 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 'nope' 不在 config); error, |
| plat=nope | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (平台 'nope' 不在 config); error, |
| plat=替身 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| plat=替身 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| plat=替身 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| plat=替身 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | UnicodeEncodeError |
| covers=5 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=5 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=5 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=5 | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=true | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=true | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=true | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| covers=true | 大小寫 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| detail=5 | 正式 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| detail=5 | ./ | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| detail=5 | 連結 | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | 1💥 | 1💥✗J | TypeError |
| detail=5 | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error, |
| note=dict | 正式 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| note=dict | ./ | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| note=dict | 連結 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | killed_unattributed (弱證據:紅燈未歸因到綁定測試(建議 r; killed_unattributed, |
| note=dict | 大小寫 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | error (revert 失敗——後續同組配方作廢防污染); error, |

最高等級:major,blocking 共 1 條
