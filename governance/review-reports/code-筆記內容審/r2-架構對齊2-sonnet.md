severity: major

## F1 範圍終點的全零判斷另刻一套 regex,沒有沿用專案既有的共用零 SHA 常數

severity: major
blocking: 是 — 同一個概念(「這是不是全零 SHA」)在同一支檔案裡出現兩套定義,其中一套是這次修正新刻的,屬於「引入第二種做法」。

引句:「if re.fullmatch(r"0{40}|0{64}", b):」

這是 `_note_audit_resolve` 這次新增的判斷(範圍終點是全 0 就當作刪除分支跳過)。但專案裡已經有一個共用常數在做同一件事:`_ZERO_SHA_RE = re.compile(r"0{40}")`(file: `scripts/lumos:29082`),被 `_lens_push_base` 拿來判斷範圍**起點**是不是全零(file: `scripts/lumos:29098`、`scripts/lumos:29102`),而 `_lens_push_base` 正是筆記形狀擋、每支檔有家、筆記內容審三層「共用一支判法」的那支函式(`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md` 的 PITFALL 行也這樣講)。這次修正沒有把終點的全零判斷交給 `_ZERO_SHA_RE`(或反過來把 `_ZERO_SHA_RE` 擴充成兩者共用),而是就地寫了一個支援 40 或 64 個 0 的新 regex，只給這一處用。

具體失敗場景:兩套「零 SHA」定義從此不同步。用最小重現可以直接看到分歧:

```
python3 -c "
import re
ZERO_SHA_RE = re.compile(r'0{40}')
new_re = re.compile(r'0{40}|0{64}')
z64 = '0'*64
print('既有 _ZERO_SHA_RE 對 64 個 0:', bool(ZERO_SHA_RE.fullmatch(z64)))
print('這次新刻的 regex 對 64 個 0:', bool(new_re.fullmatch(z64)))
"
```
輸出:
```
既有 _ZERO_SHA_RE 對 64 個 0: False
這次新刻的 regex 對 64 個 0: True
```
也就是說,如果哪天起點也給了 64 個 0(例如 SHA-256 repo,或單純上游格式改變),`_lens_push_base`(進而 note-shape、home-check、note-audit 三層共用的起點判法)完全不認得那是「新分支首推」,會被當成「起點在本機找不到」走到不同分支;但 `_note_audit_resolve` 對終點卻認得。同一份程式碼裡,「零 SHA 長什麼樣」有兩個彼此不知道對方存在的答案。

## F2 「範圍終點在本機找不到」這件事,note-audit 改成擋下,但同層的 note-shape、home check 仍然放行——三個共用同一套範圍判法的手足出現不一致行為

severity: major
blocking: 是 — 同一種輸入(範圍終點本機找不到),同家族三個守門在這次修正後給出不同 rc(擋 vs 放行),屬於「引入第二種做法」而非單純風格差異。

引句:「print(f"擋下:範圍 {diff_range} 的終點在本機找不到——範圍寫錯了?", file=sys.stderr)」

這次修正把 `_note_audit_resolve` 對「終點在本機找不到」的處理,從舊有的 fail-open(rc0、印「跳過(fail-open)」)改成 fail-closed(rc2、印「擋下」)。修正的理由(實作紀錄裡也寫了:「放行等於整道檢查沒跑」)講得通,但完全相同的「終點在本機找不到,放行等於整道檢查沒跑」的道理,對筆記形狀擋(note-shape)、每支檔有家(home check)理論上同樣成立——而這兩支到現在還是 fail-open、rc0。也就是說,這次修正只把三層共用的其中一層改成更嚴格的行為,另外兩層沒有跟著動,也沒有在筆記或程式裡講清楚「為什麼終點找不到這件事,三層可以有不同答案」(現有筆記只講清楚範圍**起點**的三層一致判法,和淺層 clone 的三層一致跳過,唯獨終點找不到這件事沒有被列進「兩層一致」的範圍)。

最小重現(三個指令、同一顆 repo、同一個找不到的終點,rc 不一致):

```
python3 scripts/lumos note-shape --diff "HEAD..definitely-missing-tip" --repo <repo>
# rc=0,印「筆記形狀擋:範圍 …的終點在本機找不到,跳過(fail-open)」

python3 scripts/lumos home check --diff "HEAD..definitely-missing-tip" --repo <repo>
# rc=0,印「每支檔有家:範圍 …的終點在本機找不到,跳過(fail-open)」

python3 scripts/lumos note-audit check --diff "HEAD..definitely-missing-tip" --repo <repo>
# rc=2,印「擋下:範圍 …的終點在本機找不到——範圍寫錯了?」
```
（file: `scripts/lumos:24412-24417` 是這次改的地方;對照 `scripts/lumos:23389-23391`〔home check〕、`scripts/lumos:24111-24113`〔note-shape〕仍是舊行為,三者可實測互相對照。）

## F3 decision-amend 判斷「欄位值是不是清單/巢狀欄」,用的是自己土砲的啟發式,沒有沿用專案裡既有的 block-scalar 標記判法

severity: minor
blocking: 否 — 沒能具體舉出這個啟發式跟既有判法(`parse_decisions`)會給出不同答案的輸入,只確定是另起一套邏輯做同一件事;判準上屬於「跟鄰居不一致但結構仍對」,所以自降一級不算 major。

引句:「if k1 > k0 and not head_val:」

`cmd_decision_amend` 判斷某個文字欄位的值是不是「清單或巢狀欄」(該擋)還是「多行文字塊」(該准),用的是「值那一行冒號後面是不是空字串」這個啟發式。但專案裡早就有一支處理同一個問題、更精確的既有判法:`parse_decisions`(file: `scripts/lumos:12959-12977`)明確檢查值是不是 `|`、`|-`、`>`、`>-` 這幾個 YAML block-scalar 記號才當多行文字塊,否則值是空字串才當清單去掃 `- ` 開頭的行。`cmd_decision_amend` 這次修正(file: `scripts/lumos:24920-24939`)沒有呼叫或比照這支既有判法,而是另外寫了一個不看記號、只看「後面是否接了縮排更深的行,以及首行冒號後是否有字」的通用掃描器(`_ind`、k0/k1 迴圈),外加這條新加的 `head_val` 空字串檢查來兜底判斷清單/巢狀欄。兩套邏輯目前測出來的行為一致(r1 regression 測試 ⑥/⑥b 都綠),但這是同一個專案裡「同一個問題(YAML 欄位值形狀判定)有兩套彼此獨立、判準不同的實作」,屬於這輪審查題目本身點名的例子(decision-amend 判多行值/清單欄有沒有既有判法可用)。往後 `parse_decisions` 那套改了判準(例如支援 flow-style `[a, b]` 清單),`cmd_decision_amend` 這套不會跟著變,兩邊會慢慢漂移。

---
不對齊共 3 條,其中 major 2 條
最高等級是 major:兩處「同一件事該怎麼判」在專案裡各自多長出一套獨立邏輯——一套是零 SHA 的判斷式跟既有共用常數不同源,另一套是三個共用同一套範圍判法的守門在終點找不到時給出不一致的放行/擋下結果,其中一項在同一顆 repo 上可以直接用三個指令重現出不同的 rc。
