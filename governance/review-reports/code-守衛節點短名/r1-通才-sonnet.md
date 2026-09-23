severity: major

## F1 --name 的字元驗證比文件宣稱的寬很多,而且沒有做 NFC/NFD 正規化,同名擋不住的保護在非 macOS 檔案系統上會失效
severity: major
blocking: yes

`_guard_name_problem` 用來擋「檔名不能用的字」的正則,跟圖譜筆記與錯誤訊息裡寫的「只收中英數字底線連字號」對不上。我實際跑了字元分類:

引句:「_GUARD_NAME_OK_RE = re.compile(r"[\w\u4e00-\u9fff-]")   # 跟舊的自動檔名同一套字元規則」

Python 的 `\w` 在預設(Unicode)模式下不是只認「中英數字」,而是認所有 Unicode 字母/數字類別。我實測(`python3 -c` 逐字元跑 `_GUARD_NAME_OK_RE.match`):全形數字「５」(U+FF15)、全形字母「Ａ」(U+FF21)、韓文「한」(U+D55C)、俄文「Ж」(U+0416)、希臘文「Ω」(U+03A9)全部 `matched=True`——這些都不是「中英數字」,卻會被接受,跟這行明講的收窄範圍矛盾:

引句:「所以這是精確比對不是猜,零誤報。缺點:手取的長檔名不會被點到(使用者接受)。」

(這句在講另一件事,見 F3;這裡先講字元集合這件事的出處:同一份計劃筆記那段「只收中英數字底線連字號」的承諾,程式碼沒有真的做到。)

更嚴重的是 NFC/NFD:同一個視覺上一樣的短名,用組合字元正規化(NFD)寫出來的位元組序列跟用預組合(NFC)寫出來的不一樣。我用 `unicodedata.normalize` 實測「한글」的 NFC 是 2 個 codepoint,NFD 是 6 個(每個 jamo 都落在 `\w` 認得的 Lo 類別,所以兩種寫法都通過驗證),`len()` 算出來的長度也不同(2 vs 6),兩個字串在 Python 裡 `!=`。整支 `scripts/lumos` 檔案裡其實已經有專門處理這件事的工具:

file: `scripts/lumos:186-187`(`def nfc(s): return unicodedata.normalize("NFC", s)`)

而且這個 `nfc()` 在載入 vault 時就用來正規化筆記的 stem 與相對路徑:

file: `scripts/lumos:323`(`rel = nfc(p.relative_to(vault).as_posix())`)、`scripts/lumos:326`(`n.stem = nfc(p.stem)`)

但 `_guard_plan_check` 組檔名時直接用使用者輸入的 `name.strip()`,完全沒有呼叫 `nfc()`:

引句:「gname = f"{datetime.date.today().isoformat()}_{name.strip()}"」

同名保護(`gpath.exists()` 那段)靠的是作業系統的檔案系統語意,不是程式自己比對:一個字串經過 `nfc()` 正規化、一個沒有,兩邊完全脫鉤。我在這台 macOS 上直接用 Python 在檔案系統層寫兩個檔名(一個 NFC 一個 NFD、視覺上完全一樣),結果 `os.listdir` 只看到一個檔案——這台機器的 APFS volume 本身會把兩種正規化形式摺成同一個路徑,所以在這裡巧合地沒事。但這是這台機器的檔案系統設定,不是程式的保證:ext4(CI 多半用的 Linux runner)不會做這種摺疊,兩種正規化形式是兩個完全不同的路徑,`gpath.exists()` 在那種環境下不會擋下第二次寫入。一旦發生,會產生兩篇檔名視覺上一模一樣、但 `env.notes` 索引鍵(load 時又會被 `nfc()` 正規化)相同、實體檔案卻不同的守衛節點——這正好牴觸這個檢查存在的理由:

引句:「守衛節點 {gname} 已經存在,換一句話或改名再試」

(這行訊息的用意就是「不靜默覆蓋:兩個人同時建同名節點會把對方的蓋掉」,但 NFC/NFD 不一致時它連「已存在」都判斷不出來,保護形同虛設。)

我驗過的路徑:`_GUARD_NAME_OK_RE` 對六種字元類別的實測(全形數字/全形字母/韓文/俄文/希臘文/組合重音)、`unicodedata.normalize` 對「한글」NFC/NFD 的 codepoint 數與 `\w` 命中情形、`scripts/lumos:186-187`/`323`/`326` 的 `nfc()` 定義與用法、在臨時 vault 上直接寫入 NFC/NFD 兩種檔名觀察 `os.listdir` 結果。沒有驗證 Linux/ext4 上的實際行為(這台機器沒有),這部分是根據 ext4 不做路徑正規化這個廣為人知的檔案系統事實推論,不是我在這次審查裡實測到的。

## F2 截斷檔名提醒沒有排除已轉正/已棄置的守衛節點,做完的合約會被永遠提醒改名
severity: minor
blocking: no

原本逾期提醒那段會先篩 `status == "pending"`(這段不是這次 diff 改的,是既有邏輯),但這次新增的截斷檔名偵測完全沒有這道篩選:

引句:「if _gn.fields.get("type") != "verification" or not _gn.fields.get(GUARD_MARK_FIELD):」

我實際跑過一次完整流程驗證:用真的 CLI 建一篇合約原文超過 40 字、短名故意先給一個正常名字的守衛節點,再手動把檔名改成舊規則會產生的截斷樣子(模擬「舊帳」),`doctor` 正確點出它;接著 `lumos guard settle ... --test t_dummy` 把它轉正(`status: pass`),再跑一次 `doctor`,輸出一模一樣還是被點名。原因是 `guard settle`(`scripts/lumos:11090-11109`)只換功能節點裡的合約行、把守衛節點的 `status` 設成 `pass`,完全沒有動到守衛節點檔案裡「預告的合約:」那一行,而截斷偵測讀的正是那一行(`re.search(r"^預告的合約:(.+)$", ...)`),跟節點是不是已經做完無關。

這不會擋推送(`warn_soft` 不計入 `issues`,`scripts/lumos:1030-1034` 明寫「軟提醒:印出但不動 issues → 不影響 rc」),所以不是功能性錯誤,但代表本 repo 一旦有一批舊帳用截斷檔名做完並轉正,這條提醒會永久重複出現、沒有機制能讓它消失(唯一解法是真的去改檔名),跟這批 diff 在別處講的「每產一篇節點就生一條警告,用的人會被訓練成忽略」是同一類風險,只是這次是「做完了也甩不掉」的版本。測試 `t_doctor_flags_truncated_guard_names` 只驗了 pending 狀態,沒有涵蓋轉正/棄置後仍被點名這件事。

## F3 「零誤報」的判法在極端情況下可以被手造出誤報,但只有繞過 CLI 直接手寫節點檔才踩得到
severity: minor
blocking: no

引句:「所以這是精確比對不是猜,零誤報。缺點:手取的長檔名不會被點到(使用者接受)。」

判法是 `_gstem == _guard_plan_slug(_gc) and _gstem != _gfull`——如果有人手動建一篇守衛節點(不透過 `guard plan`,因為 CLI 的 `--name` 上限 24 字,而「舊規則會截斷」代表原文轉出來的 slug 一定接近 40 字、超過 24),把檔名(去日期後)剛好取成跟 `_guard_plan_slug(合約原文)` 算出來的字串一模一樣,這篇「手取的名字」就會被誤判成「舊規則截斷出來的」,牴觸上面那句「零誤報」。我算過一個真實例子(55 字的長合約文字),`_guard_plan_slug` 算出的舊規則 slug 是 40 字,遠超過 `--name` 上限 24 字,所以透過 `guard plan` 指令本身走不到這個誤判——必須是完全繞過 CLI、直接手寫 `.md` 檔且刻意重現舊規則的輸出才會發生。列進來是因為它跟文件寫的「零誤報」不符,不是因為容易踩到。

## F4 已驗過但沒發現問題的路徑
severity: clean

- ③ 順序/半套:`_guard_name_problem` 的檢查在 `_guard_plan_check`(`scripts/lumos:10775-10830`)裡排在「找不到節點/找不到計劃」之後、寫檔(`_guard_plan_write_node`)之前,短名不合格時函式直接 `return None`,`cmd_guard_plan` 收到 `None` 就整個 return 2,不會呼叫寫檔那段。測試 `t_guard_plan_requires_short_name` 也機械驗證了這點(擋下的四種情況都沒留下 `Verification/*.md`)。沒發現半套寫入。
- ④ 測試輔助 `_gp` 的雜湊短名:自動補的「測」+ sha1 前 10 碼組合最長 11 字,遠低於 24 字上限,雜湊字元全在 `[0-9a-f]` 內、不會被字元檢查擋下;我核對過全部呼叫點,沒有兩次在同一個 vault 用完全相同的合約原文呼叫 `_gp`(同一天雜湊會一樣,會撞成「已經存在」而非測試預期的成功)。另外確認 `t_guard_plan_requires_short_name`(驗「沒給 --name 要擋」的那支測試)是直接用 `run()`,沒有經過 `_gp`,所以 `_gp` 自動補名這件事沒有讓它悄悄失去意義;`t_guard_plan_requires_all_fields` 同樣沒用 `_gp`,而且它每次迭代本來就缺另一個必填欄位,會在 `_guard_plan_check` 裡比 --name 更早的那道檢查擋下,所以沒被 `_gp`(它根本沒用到)影響。
- Windows 保留字(CON/PRN/AUX/NUL/COM1…)與結尾句點:因為檔名強制帶「YYYY-MM-DD_」日期前綴,實際落地的 stem 永遠是「日期_短名」而不是單獨的保留字本身,Windows 判斷保留名是看「第一個點之前的完整 base name」,所以不會誤觸;`.` 和空白也不在允許字元集合裡,不會產生結尾句點/空白的問題。
