severity: major

我是照 spec 字面推演的。所有情境都跟 `scripts/hooks/pre-push`、`scripts/lumos`、`.github/workflows/ci.yml` 的現況比對過,但沒有實跑。

### Finding 1:`pushed_mainline` 只比遠端追蹤 ref,推網址、別名遠端、新遠端首推 main 會被判成功能分支
severity: major
blocking: 是(照字面實作,推主線時會漏掉本機全套,屬 fail-open,不是 fail-closed)
spec 段落:做法 2、做法 3、S4

引句:「每個 ref 叫 `pitfalls` 時帶上 `--push-remote "$1" --pushed-ref "$_rref"`。」
引句:「被推的 ref 對應的那條(`refs/remotes/<--push-remote>/<被推分支>`)等於其中任一 → true」

問題:判法的兩邊都依賴「本機有沒有那條遠端追蹤 ref」,有四種情境會漏。
- **推網址**:`git push <網址> main` 時,pre-push 的 `$1` 是網址,不是遠端名。目標變成 `refs/remotes/<網址>/main`,不可能等於任何候選,於是推 main 被判 false,降成 light。
- **別名遠端**:另一個遠端名指向同一個網址,而且沒 fetch 過。推 main 的結果同上。
- **新遠端或新 repo 首推 main**:`refs/remotes/<遠端>/main`、遠端 HEAD、`main@{upstream}` 都還不存在。`_push_mainlines` 對 `_push_rev` 找不到的候選一律 `continue`,候選清單是空的,沒有任何東西等於目標,判成 false。
- **spec 的失敗分支只涵蓋 git 查詢出錯**:「候選全都不存在」不算查詢失敗,仍落到「其他分支 → false」。

repo 內已有現成的對策沒被採用。`_note_reread_mainline_names` 是「固定名 main/master ∪ 候選指到的分支名」,而且註解寫明「不看 pre-push 給的遠端名」,理由正是換遠端名或直接推網址會整段不核對(代碼審 r4 資安 1)。spec 另寫一套只看追蹤 ref 的判法,等於重犯已修過的洞。

S4 的測試只列「主線、遠端 HEAD 指的分支、其他分支、標籤」。「推網址」「候選全不存在」「別名遠端」三種都沒有案例。

建議:被推分支名是 main/master,或候選清單為空且查詢未失敗時一律 true;或改用 `_note_reread_mainline_names` 那套。

佐證:
- `scripts/hooks/pre-push:166`(`_PP_REMOTE="${1:-}"`)
- `scripts/lumos:65263`(`_push_mainlines` 的 `if not sha: continue`)
- `scripts/lumos:53729`(`_note_reread_mainline_names`)

### Finding 2:`suite=full` 的原因被抹掉,「算不出範圍」也會被降成 light
severity: major
blocking: 是(spec 自己在實務隱患寫的方向是「算不出來照全套」,字面實作做不到)
spec 段落:做法 3、實務隱患「算不出來的方向」

引句:「這個 ref 判 `full`、`pf_json` 讀得到、而且 `pushed_mainline` 明確是 false 時,改判 `light`」
引句:「算不出來的方向:`pf_json` 空、舊版沒欄位一律照全套(做法 3),保住現行「算不出就多跑」。」

問題:`_test_suite_for_range` 在三種完全不同的情況都回 `suite: "full"`。
- 範圍算不出(`範圍 … 算不出來`、`算不出改動清單`)。
- 改到守衛檔(`code` 為空)。
- 真的改到非文件檔。

hook 只用 `grep '"suite": *"docs"'` 判斷,看不出是哪一種。第一種情況 `pf_json` 是讀得到的 JSON、`pushed_mainline` 是 false,於是降成 light,而且 `affected_keys` 是空的,本機只跑文件子集。spec 的「算不出來照全套」只覆蓋 `pf_json` 空與舊版沒欄位,不含「lumos 內部判不出」。

守衛檔那一種在「現況」段有明說,算已知取捨。範圍算不出來的那一種沒有被揭露,也沒有測試案例。

建議:降級條件多加「`suite_reason` 不是算不出」。更乾淨的做法是在 JSON 加 `suite_computed: true/false` 欄位,hook 只在 true 時降級。S2 補一個「範圍算不出」的案例。

佐證:`scripts/lumos:61705`(`_test_suite_for_range`)

### Finding 3:push concurrency 群組鍵只含 sha,同一個 sha 的「功能分支推送」與「推 main」會互相排隊
severity: minor
blocking: 否(延遲為主,取消需要第三個同 sha 事件)
spec 段落:做法 1、S6、實務隱患「併發」

引句:「push 事件以提交編號分組、不取消,之後再推的帳本提交不會取消功能提交那一次。」
引句:「併發:多個會談各自推分支,各自觸發 CI,互不取消(以提交編號分組)。」

問題:群組鍵是 `ci-push-<sha>`,分支與標籤都是 `push` 事件,所以同一個 sha 共用一組。這個 repo 的流程是功能分支推完後快轉合進 main(sha 不變)。
- 分支那次還在跑時推 main,main 那次變 pending,要等分支那次跑完才開始。
- 兩次各 15–20 分,序列起來可能超過 `ci-wait` 預設的 1800 秒,得到 timeout(rc0、不算綠)。
- pending 的 run 遇到同組第三個事件(同 sha 的 tag 或再推一個分支)會被取代。那時「合併後那一次」的 main CI 根本不會跑。
- `ci.yml` 現有註解特別提過「中間那個提交會一次 CI 都沒跑」,是同一類洞。
- spec 的併發分析只考慮「不同 sha 的帳本提交」,沒討論同 sha。

建議:群組鍵加上 `github.ref`,也就是 `ci-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}-${{ github.sha }}`。

佐證:`.github/workflows/ci.yml` concurrency 區塊

### Finding 4:`gates` 的 `if: github.event_name == 'push'` 後盾步驟會在每個分支推送上跑,spec 沒討論,現有註解也會變錯
severity: minor
blocking: 否
spec 段落:做法 1

引句:「prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)。」

問題:spec 只談 prep 與 shards。`gates` 裡的 code-loop gate、note-shape gate、drift check 都是 `if: github.event_name == 'push'`。這些步驟原本只在推 main 時跑,改成所有分支後,每次功能分支推送都會跑。
- note-shape 步驟註解寫「本 workflow 只在推 main 時跑這步」,會變成錯的。
- 這些閘在功能分支(尤其合過主線的分支)的範圍判法,正是 `Issues/推送前其他閘的範圍在合過主線時會多算` 那條已知問題。上線後功能分支的 CI 紅有一部分會來自這些閘,不是測試。
- RETIRE-IF 的「紅超過三成」門檻因此混進非測試原因。
- 新分支首推時 `BEFORE` 是全零,prep 一律 `suite=full`,連純文件首推也會跑全套。這是保守方向,但 spec 該講一句。

建議:spec 明寫這些步驟在功能分支要不要跑。要跑就補 note-shape 的註解,並在撤除條件裡把「測試紅」與「閘紅」分開數。

佐證:
- `.github/workflows/ci.yml`:`gates` 工作的 code-loop、note-shape、drift check 三步
- `.github/workflows/ci.yml`:prep 的「這次推送要跑哪個測試範圍」步驟

### Finding 5:`pitfalls` 新旗標「同名同義」跟既有同名旗標語意衝突,只給一個旗標的行為也沒定義
severity: minor
blocking: 否
spec 段落:做法 2

引句:「`pitfalls` 加旗標 `--push-remote <遠端名> --pushed-ref <遠端 ref>`(跟 `lumos push-range`、筆記內容閘同名同義)」

問題:`push-range`、`drift check`、`room-guard`、`reread-check` 的這兩個旗標都代表「`--diff` 的起點當成遠端舊值,改從主線分岔點重算」,而且要求一起給(只給一個回 2)。`pitfalls` 的 `--diff` 已經是 hook 算好的 `_brange`,新旗標只該產出 `pushed_mainline`,不能重算範圍。「同義」字面會讓實作者去重算範圍。spec 也沒講只給其中一個時是 rc2 還是靜默忽略。

建議:把「同義」改成「只用來判 `pushed_mainline`,不改 `--diff`」,並寫明單給一個的處理。

佐證:
- `scripts/lumos:73846`(既有旗標的 help 文字)
- `scripts/lumos:49221`(既有旗標的「要一起給」檢查)

### 其他各節
- 驗收條款 S1、S3、S5、S7:已讀,無 finding。
- 回退:已讀,無 finding。
- 舊否決對照、現況、PRIOR-ART:已讀,無 finding。
- 做法 4(訊息只印一次、`_suite_mode` 定案後才印):已讀,無 finding。

### 實務隱患逐類
- 併發:見 Finding 3。
- 資源:spec 已揭露,PR 事件加分支事件會重複跑。
- 版本錯開:新 hook 配舊 lumos 會因缺欄位走全套,舊 hook 配新 lumos 不帶旗標、照舊。已讀,無 finding。
- 混推(main 加功能分支):任一 ref 要全套就全套,字面可行。
- 標籤:`refs/tags/` 判 true,維持本機全套。CI 對標籤只跑 `security_tag`。已讀,無 finding。
- 刪除分支:hook 對 `_lsha` 全零直接 `continue`,不進判定。`push` 觸發也不會因刪除分支而起。已讀,無 finding。
- 不可逆、金流、對外送出:無,理由同 spec 所述。

總結:最嚴重等級為 major,共 5 條 finding,會擋的有 2 條(Finding 1、2),其餘 3 條不擋。
