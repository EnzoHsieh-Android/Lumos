severity: major

審查範圍:修補差異(`scripts/lumos`)。我讀了全部修補,並用 `_note_reread_hunk_tags` 和 git 2.39.2 實測了函式名怎麼算、裸庫模式讀不讀屬性檔。臨時目錄已刪。

## Finding 1

severity: major
blocking: 是 — 上一輪資安席判 major 的「同一段改動搬到同檔另一個前後三行相同的函式、指紋不變」,在 TS/JS、Kotlin、Java、C 系列仍然重現,修補只補到有 def/class/function/func/fn 關鍵字的語言。
引句:「名字取 def/class/function/func/fn 後面那個(前面可帶 async/export/pub 這類修飾字,Go 的方法接收者跳過),都沒有就取第一個識別字」
問題:`_NOTE_REREAD_DEF_RE` 沒匹配到時,函式名退成頂格行的第一個識別字,而那通常是修飾字或型別,不是函式名。縮排的方法行也只認同一組關鍵字,所以沒有 `def`/`function` 的方法拿不到內層名字。實測各語言算出的名字如下:
- TS/JS:`export const pub = (u) => {` 和 `export const adm = ...` 都得到 `export`。
- Kotlin:頂層 `fun a()`、`fun b()` 都得到 `fun`。類別裡的 `    fun one()` 沒有內層名,只剩類別名。
- C:`int one(...) {` 和 `int two(...) {` 都得到 `int`。
- Java:`    public void one()` 沒有內層名,兩個方法都只得到類別名 `A`。
- 還有 `public interface/enum/record`(得到 `public`)、`struct`(得到 `struct`)和 Python 同名 property 的 getter/setter(得到 `A/x`)。

具體失敗情境:
- 輸入:作者把 `-check(user)` / `+allow(user)` 這段改動,從公開函式搬到管理員函式。兩個函式前後三行相同,都是 `export const ...` 或 Java 類別 `A` 裡的方法。
- 結果:兩份 diff 的 hunk 內容相同,標籤都是 `export`(或 `A`、`int`、`fun`),`_patch_file_changes(headers=False, lf_only=True, hunk_tag=…)` 算出同一個指紋。改動變了、指紋沒變,「已對照」被當成成立,不會提醒重讀。
- 我用 `_patch_file_changes` 驗過:兩邊標籤相同、hunk 內容相同,指紋相同。

建議:標籤不要靠關鍵字猜。可以把頂格行去掉參數列之後的整段「簽名前綴」當名字(例如括號之前的全部),或在名字退回修飾字時,改取括號、`=`、`:` 之前最後一個識別字。再為 TS/Kotlin/Java/C 各補一條「搬到另一個相同上下文函式時指紋要變」的先紅測試。

佐證:`scripts/lumos:36580`(`_note_reread_hunk_tags`,對應修補差異的 `_NOTE_REREAD_DEF_RE`/`_NOTE_REREAD_IDENT_RE` 兩個正規式)

## 已讀,無 finding

- **函式名的穩定性(Python)**:主線改了上方函式的簽名或參數,名字只取識別字,指紋不變。裝飾器行(`@` 不是頂格字母)不影響。巢狀函式名字確定,但不一定是最內層,這只可能讓指紋多變,方向安全。hunk 起點正好是函式定義行時,名字取前一個函式,同樣只會多失效、不會漏。
- **行號邊界**:新側行數為 0(純刪除)取 c 行之後,新側行數大於 0 取 c-1 行之前,`+0,0`、檔頭新增、沒有行數的 `@@ -1 +1 @@` 都沒越界。
- **hunk 對應**:`_NOTE_REREAD_HUNK_RE` 只比對行首的 `@@`,內容行都有前綴所以不會誤配;同一檔的 hunk 以 `(c,d)` 為鍵不會重複。
- **截斷判斷兩邊一致**:`_note_reread_v2_cut` 與 `_note_reread_diff` 走同一支 `_note_reread_diff_once`,同基準、同路徑清單、同 -U0 與上限;v2 成立時 files 一定非空,不會變成整個範圍的 diff。唯一差別是 check 有預算而 prepare 沒有,已明文處理成「逾時」並改用舊版,方向安全。
- **裸庫模式**:git 2.39.2 實測,`--git-dir <gd> --bare` 加上工作目錄設在 gd,工作樹裡有 `.gitattributes`(`-diff`)時,原本會變成 `Binary files differ`,現在照常出文字 diff。已提交的屬性檔、linked worktree 的 gitdir、中文與 NFD 路徑加 literal-pathspecs 都正常。
- **給判定者的 diff 與指紋所讀的 diff**:現在都走 `_note_reread_git`,同一組全域選項與 hunk 切法。
- **退回舊版的各條路**:查大小逾時或失敗、個別物件查不到、blob 讀失敗、型別變更、太大、diff 空、被截斷,都回 `(None, why)` 整篇退回舊版。`sizes` 失敗不再讓 32MB 上限靜默失效。
- **資料狀態五問**:沒有逾時或預算被吃光的洞。已擋下的路徑是:`rev-parse` 失敗被快取成「在工作樹跑」,方向是多列。預取小檔沒有總量上限,最壞約等於(改到的檔數 × 1MB),屬效能面,不影響正確性。

最高等級 major,blocking 共 1 條。
