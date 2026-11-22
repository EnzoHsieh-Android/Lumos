severity: major

鎖檔 `…c2e718ee….json.warming` 不存在,沒有要處理的鎖。臨時檔我放在 `/private/tmp/claude-501/` 底下,已用字面路徑刪掉。

## 問 1 分層與依賴方向:對齊

- **`_choice_err_start`**:放在 `scripts/lumos` 的 `_choice_anchor` 正後方(`_choice_err_start` 在 77439,`_choice_anchor` 在 77403,`_choice_line_index` 在 77445),跟「依錨點名稱分流的判斷收在 `_choice_anchor` 一帶」同處。
- 它是純函式,只讀 `row`、`hit`、`anchor` 和傳進來的 `line_of`,不呼叫其他 `_choice_*`。唯一呼叫端是 `_choice_file_points`(77784 起)。
- 它收 `line_of` 這個 callable,跟鄰居 `_choice_err_cover(err, line_of)`(77763)的傳法一樣,沒有跨層直呼。
- **「方法名」分支**改用既有的 `_CHOICE_CALL_NAME_RE`,跟「整個呼叫」分支(77409 起)共用一支,是收斂,沒有分叉。
- **`_cb_points`**:放在原 `_cb2_points` 的位置,仍呼叫 `_ktpack_sg`、`_load_lumos_inproc`、`m._choice_scan_parse`、`m._choice_file_points`,依賴方向跟原來相同。

## 問 2 命名與錯誤處理:大致對齊,有一處小落差(a1)

- **`_choice_err_start`**:跟 `_choice_err_cover` 同一套 `_choice_err_*` 命名。它回的是行號,沒有「產不出結果」的路徑。
- **沒裝 ast-grep**:函式裡有兩種處理,一種是 `skip` 沒給就回 `None`,一種是 `skip` 給了就 `raise _SrcOnly`。第二批呼叫端照舊印一行跳過,第三批照舊用 `_SrcOnly`。這個專案本來就有這兩套:第二批 `t_choice_points_batch2_api` 在 `_cb2_points` 回 `None` 之後自己 `raise _SrcOnly`(`scripts/test_lumos.py` 的 `t_choice_points_batch2_api`)。鄰居本身不一致,這輪只是把兩套收進同一個函式用旗標切換,沒有新增第三套。
- **暫存目錄**:改用 `with tempfile.TemporaryDirectory(...)`,這在 `scripts/test_lumos.py` 裡有 723 處,`mkdtemp` 有 813 處,新寫法在專案裡很常見。
- **S9 測試**:規則、樣本、跳過訊息、整段跳過的寫法都對齊;「某列撤了就 print 一行再 continue、三列都撤了才 `_SrcOnly`」跟第二批的半跳過一致。

## 問 3 第二種做法:不對齊(a2 是 major)

- 新規則寫法:`utils:` 放在 `rule:` 之前(C-48 的 `zero-int`),跟 C-34 一樣。C-38、C-39 的 `child-co` 內新加的 `not: inside:`,是既有的否定加關聯形狀。這兩項不算第二種做法。
- 樣本標記:新規則是「多行寫法的標記放在節點起始的第一行」,測試改成第一行或最後一行任一行有標記就算(a3)。
- 測試跳過:`_CB3_SKIP` 常數加 `skip=` 參數,沿用既有的 `_SrcOnly`,不是新的跳過方式。
- 工具:沒有自創工具而鄰居已有的情形,`_choice_err_start` 與 `_CHOICE_CALL_NAME_RE` 反而是收斂既有做法。
- **「整條外包雙重否定」記成第二種寫法**:跟專案處理「兩種寫法並存」的既有做法不一致(a2)。

## a1 `_cb_points` 用 `skip=` 旗標把兩套跳過慣例包在同一個函式,共用輔助函式前綴也不一致
severity: minor
blocking: 否
引句:「沒裝 ast-grep:skip 給了就 raise _SrcOnly(skip)(第三批),」
file: `scripts/test_lumos.py:146511`(`_cb2_util_block`,同層共用輔助函式仍用 `_cb2_` 前綴;批三測試也呼叫 `_cb2_row`、`_cb2_new`)
一個函式靠參數決定回 `None` 還是丟例外,呼叫端要知道傳不傳 `skip`。同樣被批三共用的 `_cb2_row`、`_cb2_new`、`_cb2_util_block` 沒跟著改名,只有 `_cb_points` 去掉了數字。
歸因:原有就有兩套跳過慣例,這輪把兩套併進同一函式,屬於未判定。⚠ 專案沒有單一既有做法可對,請編排者裁定要不要統一。

## a2 「整條外包 not: {not: …}」記成第二種寫法,但寫明的適用條件跟實際用法對不上,也沒有守衛
severity: major
blocking: 是
引句:「多層 has/inside/precedes 鏈(作用域往下配對、replay 往上三層再看外層呼叫)」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:199`(C-35,單層用 `not: {inside: {not: …}}`);`api.yml:215`(C-36,同樣是 call_suffix 加 annotated_lambda 再到呼叫的多層鏈,仍用第一種形狀)
對照:`api.yml:441`(C-40)起的 C-40~C-47 只有「方法名 inside navigation_expression inside call_expression」兩層,跟 C-35 同形,但寫成 `not: {not: {inside: …}}`;C-51、C-52(`BufferOverflow` 前綴)也是單層。
`docs/.../Systems/kotlin規則包.md` 的 WHY 說第一種形狀用於「父節點是 X」的單層判斷、第二種用於多層鏈。實際是兩邊都不符:
- C-36 是多層鏈,卻用第一種。
- C-40~C-47、C-51、C-52 是單層,卻用第二種,而且跟同批次的 C-35 同形。

這輪的處理是把兩種形狀寫成並存並記一條 WHY,沒有統一。專案對「第二種做法」的既有處理是拒絕並記 `[不選:…(第二種做法)]`,例如 `kotlin規則包.md` 裡統計判準那條 WHY;重複的 utils 則靠「兩份要一字不差」的比對測試守住。這條新 WHY 的 `[test:t_choice_scope_rule_output]` 只量 C-38/C-39、C-48、C-53 的輸出大小,不守「哪種情形該用哪種形狀」。
歸因:外包寫法在 r2 之前就存在(有證據的原有漏查);這輪的修補把它定案成並存,條件對不上實況,這份記法的問題是這輪造成的。

## a3 樣本標記的檢查改成「第一行或最後一行任一行有標記就算」,舊規則是只看最後一行
severity: minor
blocking: 否
引句:「# 標記看窗口的最後一行,或第一行(多行寫法時節點起始那一行)」
file: `scripts/test_lumos.py:146890`(`t_choice_samples_batch3` 內比對標記的那一行)
對照:原本的寫法是片段含換行時只看最後一行,對應 `f4b` 那種一行只能標一種的拆行寫法。兩種標記位置都是「錨點所在那一行」,原則一致,但測試用「任一端」判斷,比「錨點那一行」寬,標在不該標的另一端也會通過。
歸因:r1 修補(代碼審 g1)引入的新標記位置,這輪沿用;未判定。

不對齊共 3 條,其中 major 1 條
