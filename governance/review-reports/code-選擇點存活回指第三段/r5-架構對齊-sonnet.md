severity: minor

**1. 分層與依賴方向**
修法把驗收條款、預期值表的判斷改成直接呼叫讀取器既有的 `_KT_SIT_ACCEPT_H2_RE`、`_EXPECTED_H2_RE`。這跟 `_h2_section_lines` 的家規一致(`scripts/lumos:13975`「找節邏輯不准長出第三套」),也沒有新的跨層呼叫。審計修正紀錄那一半仍是自己的判法(`_CHOICE_LAYER_AUDIT_WORD` 加交叉引用拿掉)。它不是 `_FOLD_AUDIT_RECORD_RE`(`scripts/lumos:69165`,錨在行首的 `## (§數字 )?審計修正紀錄`)。這是 r3 起的明文取捨,檔內註解也寫了差別,所以我不算新的不一致。

**2. 命名與錯誤處理**
讀取器對標題行的做法是 `h2_re.match(ln.strip())`(`scripts/lumos:13982`)。新的 `_choice_layer_not_body` 是先經 `_CHOICE_HEAD_RE` 取標題文字,再補回 `"## " + t` 去比對。`_CHOICE_HEAD_RE` 會把標題結尾的閉合 `#` 去掉,讀取器的 `\s*$` 不會。我實跑確認:標題行 `## 驗收條款 ##` 經 `_CHOICE_HEAD_RE` 得到「驗收條款」,`_KT_SIT_ACCEPT_H2_RE` 對重組後的字串比對成功,對原行比對失敗。結果是計劃正文把它當驗收條款排除,讀取器卻讀不到它,內容兩邊都看不到。這正是這次修補宣稱要消除的缺口,只是剩下這個窄形態。測試的 `fake` 表沒有涵蓋結尾 `#`。結構是對的,只是標題判讀的輸入跟讀取器不完全同口徑,所以列 minor。

severity: minor
blocking: 否
引句:「return bool(_KT_SIT_ACCEPT_H2_RE.match("## " + t) or _EXPECTED_H2_RE.match("## " + t))」

**3. 第二種做法**
自寫的 `_CHOICE_LAYER_NOT_BODY_RE` 和預期值表比對已拿掉,驗收條款、預期值表這兩類不再有第二套。`_CHOICE_LAYER_XREF_RE` 改成 `〈[^〈〉]*〉` 只是收窄正規式,沒有新做法。`t = str(title).strip()` 多了一層防禦轉型,但這是呼叫端傳進來的值,不算結構差異。測試改用 `_CKL_REAL_HEADS` 逐條歸類,跟 r3 的寫法一致。

不對齊共 1 條,其中 major 0 條。
