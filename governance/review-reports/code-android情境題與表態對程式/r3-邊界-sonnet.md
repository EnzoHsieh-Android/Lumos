severity: minor

repo 沒被我改動。`docs/.canary-log.jsonl` 與 `docs/.governance-log.jsonl` 的未提交改動在我開始前就有。我的臨時目錄已刪。

**重現方式**:用 `check.load_lumos()` 載入真的 `scripts/lumos`。用 `lm._kt_sit_text_segments` 切段,再呼叫 `lm._kt_sit_row_verdict(段, 列, 答案, 列資料)`。回 `("block", …)` 是推送前擋下,回 `("evidence", …)` 是只提醒,回 `(None, None)` 是放行。

**鏡頭 1 結論**:r2 列的標準寫法在新判法下一條都不會被擋,全部變成「只提醒」。
- 實測 9 條:`awaitAll`、`Channel.BUFFERED`、`Unit` 回傳、`execute{copyTo}`、泛型逗號 `Map<String, String> =`、`LaunchedEffect(Unit)`、Modifier 中間夾 `background`、`MutableStateFlow<ViewState>`、`awaitAll` 搭 `coroutineScope`。這 9 條都回 `evidence`,沒有一條回 `block`。
- `ds.edit{}` 的 D-42 在我的輸入裡根本切不出段,所以不會被問。
- 提醒文字有指出段、檔案行範圍、列、寫法:「段 474df84f…(X.kt:1-4)的 D-1(main)證據樣式對不上:`\.await\(\)` 不在段材料…」。
- 照抄的段放行指令是 `lumos lint-waive kt-situation:<段> --rule kt-situation --file X.kt --note "<為什麼放行>"`。原樣貼上會被擋,因為去掉空白後 `<為什麼放行>` 不到 10 個字。把 note 換成實話後,在暫存 repo 實跑成功,記成 AI 放行並提示要 `--ack`。這符合設計,不算缺陷。

## F1 放行成功訊息還在講「整段不核」,跟新行為不符

severity: minor
blocking: 否

引句:「print(f"✓ lint-waive: 指紋 {key} 已放行{'(情境段:推送前表態那一道整段不核)' if _sit else ''},理由記下來了——{note.strip()}")」

這行在 `scripts/lumos` 的 `cmd_lint_waive`,本輪 diff 沒動它。r3 之後段放行只關掉那段的證據提醒,缺段與缺列照擋。

輸入:對暫存 repo 實跑 `lint-waive kt-situation:474df84f26f735ba --rule kt-situation --file X.kt --note "證據樣式誤報 awaitAll 是型錄標準寫法"`。
輸出:`已放行(情境段:推送前表態那一道整段不核)`。

用的人會以為放行後這段連缺列都免答。實際上「缺段」仍會擋,而 r3 把擋下訊息裡的放行出口拿掉了。

## F2 證據提醒逐筆落帳,數量一大就拖過 30 秒預算

severity: minor
blocking: 否

引句:「_gate_event_or_warn(repo_root, "code-loop", "warned", r["text"][:120], hard=False,」

`_kt_sit_reminder_lines` 對每一條提醒各呼叫一次 `_gate_event_or_warn`。印出只取前 6 條,落帳卻是全部。每次落帳在沒帶 `head_sha` 時會另開一個 `git rev-parse HEAD`,而且落帳不受 `deadline` 管。

輸入:在有 `docs/` 的暫存 repo,餵 2000 條 reminders。
輸出:耗時 44.7 秒,印 7 行;`docs/.governance-log.jsonl` 長到 1.17 MB。

證據提醒以前是擋下,每次最多印 6 條;現在每次推送都會把每一條重新寫進被追蹤的帳檔。大 diff 加上很多段時,推送前閘會比 `_KT_SIT_BUDGET` 的 30 秒預算慢得多。

我只實測了落帳這一段。作者答案真的產生 2000 條證據不符的提醒,是我構造的極端輸入。建議在 `_kt_sit_reminder_lines` 迴圈外取一次 `head_sha` 傳進去,並對落帳設上限或改成一筆彙總。

## F3 多行主建構子的 class 標頭行,段材料只剩 1 行

severity: minor
blocking: 否

引句:「# 屬於同一個宣告頭(Kotlin 主建構子文法),不能蓋掉前面的 class(代碼審 r2 通才 F1、正確性 F1);只剩它們(次建構子、init、getter)時是程式本體」

宣告頭判斷本身是對的:`class A @Inject constructor(...)`、`private constructor`、次建構子、`init`、companion、sealed interface 加巢狀 data class、帶 body 的 enum 都切對。原因是上面這條新規則把 `constructor`、`init`、`get`、`set` 從關鍵字清單排除,所以這些宣告頭和內文都不會被誤判。

沒修到的是 `_kt_sit_decl_end`。它把多行建構子裡 `private val …,` 的參數行當成「下一個同層宣告」,所以提早收尾。

輸入:
```
class A @Inject constructor(
    private val api: Api,
    private val db: Db,
) : ViewModel() {
    fun a() = 1
    fun load() = viewModelScope.launch {
        coroutineScope { x() }
    }
    fun b() = 2
}
```
輸出:`seg 1 4 mat [1, 1] rows ['D-39']`。class 本來有 10 行,標頭行命中的段材料卻只剩第 1 行。函式內的段正確,為 `mat [6, 8]`。

影響很小。目前 D-39 的證據樣式是 `(無)`,而證據對不上現在只提醒,所以不會擋也不會漏答。若之後某列的第二條樣式要在這種段材料裡找東西,會誤報提醒。這是 r1 就有的行為,r3 沒有新增。

**鏡頭 2 其他結論**
- 字元字面值 `'{'`、`'}'`、字串樣板 `"${items.map { it.name }.joinToString()} {"`、三引號字串內的 `{`、巢狀樣板 `"a${if (x) "}" else "{"}b"`、跳脫引號 `"\"{"`,宣告層級全部算對。
- 剩下會擋的只有答案形狀:缺段、缺列、evidence 不在段範圍內、換列的列選 alt。這些在真實寫法下不會誤擋,因為作者永遠可以選段範圍內的一行,或答 `applies:false`。
- 極端大小:4 MB 的 25 萬行建構子切段約 1.8 秒;10 萬個命中約 2.1 秒。拿掉 300 字上限沒有造成效能問題。

總結:最嚴重是 F2 的提醒落帳在大量提醒時超過 30 秒預算(minor),會擋 0 條;r2 的 11 條標準寫法變體在新判法下全不會擋,宣告頭新規則切對。
