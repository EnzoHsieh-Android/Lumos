severity: clean

# 資安審查 r3fix 驗收(只看可被利用的洞)

## 1. 不可信輸入流到危險操作(綁定名稱進 git grep、正則)
已看,無。新 [test:] 名稱要先過單一識別字的正則,才會進判定;名稱進 git grep 時用參數陣列、`-F -w -e`,沒有 shell,也沒有正則注入。名稱開頭一定是字母或底線,不會被當成 git 選項。正則用 fullmatch,沒有會爆炸的巢狀量詞。
引句:「_NODEHOME_TAG_NAME_RE = re.compile(r"(?:[A-Za-z0-9_-]+:)?[A-Za-z_][A-Za-z0-9_]*")」
file: `scripts/lumos:44502`(`_test_in_tree` 以 `["git","grep","-w","-F","-q","-e",name,at_sha,"--",*_spec]` 呼叫,不經 shell)。
未定義的平台前綴會被 `resolve_test_refs` 丟 ValueError 而判 bad-name;單平台舊模式下含冒號的名稱過不了 `_KILL_METHOD_OK_RE`,判 dangling。這兩條路都擋得住。file: `scripts/lumos:5605`、`scripts/lumos:14567`。

## 2. 守衛繞過(只換綁定的判定放過說明、判定 yes 但被推版本沒那支測試)
已看,無可利用路徑。逐項推演如下。
- 新 [test:] 夾帶說明:名稱帶空白、點號、`::`、`#`、`[]` 都過不了識別字正則,回 False。反引號包住的值內層雖能放空白或 `]`,但名稱還是過不了識別字正則,所以夾不進去。
- [test-gone:] 夾帶說明:`@` 後只認 7 到 40 碼十六進位,多出的文字使整個值不被當綁定,原樣留在 sig_t,所以算說明。沒有 `@` 的項目,名稱必須在上一版 `[test:]` 的名單裡。這是舊資訊,不會多出新內容。
- 全形逗號與全形冒號:值的字元集只有 ASCII,含全形字元的值整個不拿。
- 判定 yes 但被推版本沒有該測試:推送時 `_nodehome_tag_judge` 走 `_ns_tr_guard`。簽出的提交不是終點,或測試檔、設定有未提交的改動,就回 None 而不豁免。`_NsTrJudge` 在終點樹內用 git grep 再核對一次。未追蹤的本機測試檔能通過第①道,但過不了第②道。
- judge 例外或判不了:一律回 False,也就是不豁免(fail-closed)。
引句:「if j is None or j(nm)[0] != "yes":」
引句:「# [test-gone:名稱@提交]:@ 後面只認提交編號」
殘留風險(inference,最多 minor,blocking: 否):推送時整批提交共用同一個終點判定。中途提交若綁定的測試要到後面的提交才加進來,仍判 yes。這只影響中間提交的歸屬,終點版本確實有那支測試,攻擊者拿不到「綁定指向不存在的測試」的結果。
〈天花板〉已列的「說明剛好寫成一個真測試名」不重報。

## 3. 密鑰與個資
已看,無。新增程式沒有讀寫憑證,也沒有記錄使用者資料。唯一的輸出是 `print(f"提醒:...{e.__class__.__name__}...")`,只印例外類別名,不印內容。
引句:「print(f"提醒:每支檔有家這次沒核對測試名({e.__class__.__name__})」

## 4. 加密與傳輸
已看,無。diff 沒有網路與加密相關程式。

## 5. 執行邊界
已看,無。只新增 git 唯讀呼叫(grep、ls-tree、diff、show),都是參數陣列,沒有 shell 與 eval。名稱走 `-e` 且開頭是識別字字元。`_nodehome_strip_test_tags` 是純字串處理,沒有檔案寫入。
引句:「r = _sp.run(["git", "grep", "-w", "-F", "-q", "-e", name, at_sha, "--", *_spec],」(既有碼,file: `scripts/lumos:44502`)

## 6. 行動端
已看,無。這份 diff 不涉及行動端。

## 新依賴
已看,無。只用標準函式庫的 re、sys、time 與既有的內部函式。

總結:全份最高等級 clean
