severity: minor

我有看到「lumos 自動附加」段,列了 9 篇有詳細內容的固定席節點,另有 12 篇只列名。表態記錄(py-eventloop na)與本題無關,沒有採用。

**1. 分層與依賴方向:對齊。**
- `_SENT_END_RE` 放在 `scripts/lumos` 前段正規式常數區,緊接 `DATE_PREFIX_RE`(`scripts/lumos:417-418`)。
- 漂移檢查在後段引用它(`scripts/lumos:38370`),S21 在中段引用它(`scripts/lumos:4087`、`4107`)。
- 依賴方向是前段往後段,沒有後段回頭呼叫前段以外的東西,跟鄰居一致。

**2. 命名與錯誤處理:大致對齊,有一處不一致(A1)。**
- 同區的共用常數(`WIKILINK_RE`、`DATE_PREFIX_RE`、`TOP_KEY_RE`、`LIST_ITEM_RE`,`scripts/lumos:415-421`)全部沒有底線前綴。新常數 `_SENT_END_RE` 有底線。
- 全檔 `^_X_RE = re.compile` 有 126 條、無底線的有 172 條,兩種都有。檔案前段那一區的慣例是無底線。
- 別名寫法 `_DRIFT_M1_CUT_RE = _SENT_END_RE` 整檔只有這一處,沒有「共用一份、在地另取別名」的先例可對照。它做法單純,屬無害,但是新做法。

**3. 第二種做法:有一處(A2)。**
- 用 `.pattern[1:-1]` 剝掉字元類別外括號,再拼出否定字元類別,全檔找不到先例。
- 先例只有:
  - `_RREF_AFTER_DATE_RE` 嵌入 `_RREF_DATE_RE.pattern`(`scripts/lumos:4072`),這是 S21 自己的。
  - `scripts/lumos:7033-7034` 把 `.pattern` 當雜湊輸入。
  - 這兩種都是整條嵌入或取值,沒有「剝殼重組字元類別」。
- 「句尾定義全檔只剩一份」:精確的 `[。;；!?！？]` 確實只剩一份(`scripts/lumos:418`)。
- 但還有兩個句尾字元的近親(都是舊的、用途不同):
  - `_NS_NEG_SEG_CUT_RE`(`scripts/lumos:31055`)重抄了同樣七個字,再加逗號、冒號、括號。
  - `_DRIFT_CLAUSE_SPLIT_RE`(`scripts/lumos:34591`)只有 `[。;；]`。
  - 兩個都不是這次改動造成的,我標 ⚠:沒證據說它們該併入。

## A1 新共用常數命名帶底線,與同區慣例不同
severity: minor
blocking: 否
引句:「_SENT_END_RE = re.compile(r"[。;；!?！？]")」
佐證:file: `scripts/lumos:415`(WIKILINK_RE)、`scripts/lumos:416`(DATE_PREFIX_RE)、`scripts/lumos:419`(TOP_KEY_RE)
失敗場景:前段共用常數區都不帶底線,下一個人照鄰居找名字(例如搜 `SENT_END_RE`)會搜不到,也看不出這是跨段共用的公開常數。
歸因:有證據的修復回歸(r2 的修補才新增這個名字)。查證命令:`git -C /Users/enzo/harness/lumos-a3 show 8ff89d22:scripts/lumos | sed -n 415,421p`,結果是前段一區沒有底線前綴,只有新加的這一條有。

## A2 用 `.pattern[1:-1]` 剝殼拼否定字元類別,是專案裡沒有的導出法
severity: minor
blocking: 否
引句:「_RREF_NOT_END = r"[^\n\[" + _SENT_END_RE.pattern[1:-1] + "]"」
佐證:file: `scripts/lumos:4072`(整條嵌入 `.pattern`)、file: `scripts/lumos:7033`(`.pattern` 當雜湊輸入)
失敗場景:`[1:-1]` 暗中假設 `_SENT_END_RE` 永遠是單一字元類別。以後有人把它改成含 `——` 的交替式,或加 `(?:…)`,剝殼結果會悄悄變成錯的類別,而且不會報錯。專案別處由一條導出另一條時,是整條嵌入(如 `scripts/lumos:4072`),或由資料常數生成(`SYMBOL_RE` 由 `SYMBOL_NAMES` 生成)。這裡沒有採用這兩種做法。
歸因:有證據的修復回歸。查證命令:`grep -nE '\.pattern\[|\[1:-1\]' scripts/lumos` 在修後版本只命中 `scripts/lumos:4068` 一處正規式導出,其餘是字串去引號。
這條判 minor,不判 major:導出的方向(單源導出)本身跟專案「由資料生成」的精神一致,只是手法是新的。

不對齊共 2 條,其中重大 0 條
總結:這次修補把句尾定義收成一份,結構上跟鄰居一致;只剩新常數名稱的底線寫法,和拼字元類別的剝殼手法,是專案裡沒見過的小差異。
