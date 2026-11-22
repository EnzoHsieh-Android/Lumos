severity: major

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/80159e55…json.warming` 不存在,我沒有動任何鎖。我的臨時目錄已刪。

## 1. 分層與依賴方向

大致對齊,沒有跨層直呼。
- `check.py` 的 `CHOICE_ANCHORS` 在尾端加「整個呼叫」,沿用第二批「加在尾端、不動順序」的做法(`configs/ast-grep/kotlin-android/check.py` 的 `CHOICE_ANCHORS`)。
- 錨點分支放在 `_choice_anchor` 和 `_choice_anchor_edits`,走 `_choice_edits` 交接,呼叫方向跟安全呼叫符、引數一樣。
- 補 import 照舊走 `_choice_also` 加 `_situation_rule_header_scan`。
- 有一處小偏離,見 a3:`_choice_file_points` 是一般流程,卻第一次寫死錨點名稱。

## 2. 命名與錯誤處理

對齊。
- 產不出壞法時,`_choice_anchor` 回 `(None, None)`,`_choice_anchor_edits` 回 `None`。對照 `scripts/lumos:77603-77616` 的安全呼叫符、引數分支,以及它們在 `_choice_anchor` 的回法,一樣。
- 沒有新增日誌。
- 命名沿用 `_choice_*`、`_cb3_*`(對應 `_cb2_*`)、`_CB3_IDS`(對應 `_CB2_IDS`)。
- 規則訊息前綴改成「業務情境」,是批次的分類標籤,我不當作不一致。

## 3. 第二種做法

有兩處。分別是 a1(測試工具函式整份複製)和 a2(雙重否定的形狀不同)。另有 a3、a4 兩條 minor。

## a1 `_cb3_points` 整份複製 `_cb2_points`
severity: major
blocking: 是
引句:「d = Path(tempfile.mkdtemp(prefix="gctl-cb3-"))」
file: `scripts/test_lumos.py:146259`(`_cb2_points`)

`_cb3_points` 的做法跟 `_cb2_points` 幾乎一樣:建暫存目錄、寫規則檔與 sgconfig、跑 `sg scan --json=stream`、`_choice_scan_parse` 之後 `_choice_file_points`、同一組 `tables` 結構。只有三處不同:
- 暫存目錄前綴。
- 規則字典(`_CB3_RULES`)。
- 沒裝 ast-grep 時,`_cb2_points` 回 `None`,`_cb3_points` 改 raise `_SrcOnly`。

`_cb2_points` 已經是第二批留下的同功能測試工具,卻再複製一份,沒有改成帶規則字典參數的共用版。順帶一提,第二批自己對「沒裝 ast-grep」也不一致:`_cb2_points` 回 `None`,而 `scripts/test_lumos.py:146362` 用 `raise _SrcOnly`。所以 raise 的做法是專案既有的,真正的第二種做法是複製的函式本身。

## a2 規則的雙重否定換了形狀,註解卻寫「同 C-18、C-34~C-37」
severity: major
blocking: 是
引句:「一律外包雙重否定 not: {not: …}(同 C-18、C-34~C-37」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:240-248`(C-36 的 `not: inside: not: …`)

既有規則的雙重否定,是把 `not` 塞進關聯規則裡面,寫成 `not: {inside: {not: <目標>}}`。可以對照:
- C-34、C-35:`api.yml:196-211` 一帶。
- C-36、C-37:`api.yml:240-248` 與 `api.yml:290-300` 一帶。
- C-18:`sbr.yml` 的 `inside: {not: {kind: statements}}`。

新規則 C-38 到 C-55 改成整條規則外包 `not: {not: {inside: …}}`,也就是外層兩層 `not` 夾住關聯規則。兩者是不同的寫法,而註解卻聲稱「同」既有規則。

計劃筆記有寫這是刻意選擇,並附 r2 資源席的實測。但專案裡原本只有一種形狀,現在有兩種。編排者要定:統一成既有形狀,或把這個形狀明記成第二種慣例,並更正註解的「同」字。

## a3 `_choice_file_points` 第一次在一般流程裡寫死錨點名稱
severity: minor
blocking: 否
引句:「if err_hit(line_of(anchor) if row["anchor"] == "整個呼叫" else h["line"], h["end_line"]):」
file: `scripts/lumos:77725`(`_choice_pick` 排序用到的 anchor 是已算好的位移,不是名稱)

鄰居的做法是:依錨點分支的邏輯都收在 `_choice_anchor`、`_choice_anchor_edits`、`_choice_also`,每個都在自己內部判 `row["anchor"]`。`_choice_file_points` 本來不看錨點名稱,這次直接在迴圈裡判。結構還在同一層,所以只算 minor。

## a4 `_CHOICE_CALL_NAME_RE` 與同函式「方法名」分支的行內正規式重複
severity: minor
blocking: 否
引句:「_CHOICE_CALL_NAME_RE = re.compile(rb"(\?\.|\.)\s*([A-Za-z_]\w*)")」
file: `scripts/lumos:77419`(`_choice_anchor` 方法名分支的 `re.match(rb"(\?\.|\.)\s*([A-Za-z_]\w*)", …)`)

兩者的正規式字面完全相同,新增成常數卻沒有回頭改舊分支去用。結構沒問題,是重複。

## ⚠ 交編排者,我不硬判
- C-54、C-55 用了 `pattern:` 加 `constraints: {A: {not: {regex: …}}}`。kotlin-choice 以往沒有人用過 `constraints:`:既有規則用 `pattern:`(`ror.yml`、`nul.yml` 的 `'$A ?: $B'`)或 `regex:`,排除接收者靠 `not: regex` 寫在節點上(C-35)。但這一列需要後設變數 `$A`,既有寫法做不到,專案沒有對應的做法可比,所以標 ⚠。

不對齊共 4 條,其中 major 2 條
