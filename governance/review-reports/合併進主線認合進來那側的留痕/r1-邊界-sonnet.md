severity: blocker

# 外部審稿:合併進主線認合進來那側的留痕(邊界席)

## F1 只驗第二個母,第一個母帶進來的未審改動整包放行(主線合進分支再推、本機 pull 合併)
severity: blocker
blocking: 是 — 守衛放寬後可被正常操作(非惡意)繞過高風險審查,屬放行錯誤
引句:「合併提交恰好兩個母、它的樹等於兩個母自動合併的結果(合併時沒手改任何東西),而合進來那一側的頂端有有效的 pass/skip」
輸入:本機 main 有未審的高風險提交 X(母1),`git pull`(非 rebase)把 origin/main 合進來,合併提交的母2=origin/main 頂端,該處本來就有有效 pass;再推 main。反向同理:分支上有未審提交,把 main 合進分支再推分支,母2=main 頂端。
照 spec:merge-tree 重算樹相等(我在臨時 repo 實跑,反向合併 rc=0、樹相等);母2 有有效紀錄;放行。母1 側的 X 從沒被任何人審過。
應該:放行條件必須同時限定「母1 是被推送目標的既有遠端頂端/主線祖先」(即合進來的是母2 的『新增部分』),或要求母1..合併提交的範圍(不含母2 已審部分)也被留痕涵蓋;spec 完全沒定義哪個母算「目標那側」。另外「任何分支」查帳讓母2=主線頂端時,任一舊主線 pass 都可能成立。
file: `scripts/lumos:46927`(_codeloop_guard_verdict 以 diff_range 算 tier,放行只看 rec 對 marker_sha 的有效性)

## F2 「任何分支」查帳沒寫清楚過濾條件,50 筆上限在大帳本下會誤擋或誤放
severity: major
blocking: 是 — 判準不明確導致實作者可能把 blocked/fail-open 當留痕,或在 12 萬行帳上誤擋有效紀錄
引句:「依帳本行序由新到舊、最多看最近 50 筆;找到就放行」
輸入:`docs/.governance-log.jsonl` 實測 120201 行(`docs/.governance-log.jsonl`)。(a)「50 筆」是 50 行、50 筆 code-loop 事件、還是 50 筆 pass/skip?spec 沒說;(b) 同一 head_sha 先 pass 後來又 blocked/skipped-env/fail-open:既有讀函式靠預篩與 kind 白名單排除這些,新函式「新寫」若漏掉就會把 blocked 當留痕;(c) 母2 的有效 pass 若被其他分支 50 筆以上的 pass/skip 擠到後面(繁忙 repo、多分支並行)→ 第 51 筆有效卻照舊擋,正是使用者要修的症狀重現。
照 spec:行為取決於實作解讀。應該:改成「先找 head_sha==母2 的紀錄(不設筆數上限,或以 head_sha 預篩再驗),再對少數候選做 `_codeloop_record_valid`」;明寫只收 kind∈{passed,skipped}、gate==code-loop、有 head_sha;讀帳整檔 read_text(12 萬行)每次都要付,應只掃一次。
file: `scripts/lumos:45517`(_codeloop_read_from_ledger 的 kind 白名單與預篩)

## F3 表態那關:讀取函式不同、「任何分支」會混到別的題集,且 spec 一句「同一條規則」過粗
severity: major
blocking: 是 — 表態紀錄含題目答案,跨分支取用沒有定義比對口徑
引句:「目標分支的表態紀錄沒有或過期時,同樣去找對第二個母有效的表態紀錄。」
輸入:表態讀取是 `_codeloop_read_dispositions`(另一種 kind,帶 dispositions dict),不是 pass/skip 那支;「任何分支」下可能撈到同一 head_sha 但那條分支當時的適用題範圍(merge-base 範圍)不同,答案集合與合併提交上現在要答的題不一致。
照 spec:只驗 head_sha 有效就採用;之後 `_dispositions_verdict` 仍會拿該紀錄的 dispositions 逐題比對(缺題才擋),但「過期」判斷改採第二個母後,錨點驗證用的是 marker_sha(合併提交)還是母2?spec 未說。應該:寫明表態驗證的 at_sha 與 marker_sha 各用哪個、取不同分支紀錄時題集不全如何處理;實作時同樣有「只認有 dispositions 且 kind 正確」的過濾。
file: `scripts/lumos:46756`(_dispositions_verdict 先讀 marker_branch 紀錄再驗有效性)

## F4 淺 clone 與 git 失敗被講成「有衝突」,且總預算與單次逾時語意不清
severity: minor
blocking: 否 — 只影響擋下原因的訊息品質,方向仍是照舊擋(保守)
引句:「回傳碼 1(有衝突)、其他回傳碼(git 太舊不認得 --write-tree、用法錯)」
輸入:淺 clone(我實跑 `--depth 1` clone,merge-tree 回 rc=1 且訊息是「HEAD^1 - not something we can merge」而非衝突);git<2.38 回 rc=129(實跑確認未知選項是 129)。CI 三處 checkout 都是 fetch-depth: 0(file: `.github/workflows/ci.yml:24`),CI 不受影響,但開發者本機淺 clone 會得到「有衝突」這種誤導訊息。
照 spec:rc1 一律歸衝突;應該:rc1 時要檢查第一行是否為 40/64 位十六進位樹、並先 `_git_is_shallow` 判斷,訊息分「淺 clone 缺母」「衝突」。另外 spec 說的「總預算照表態閘既有的時間預算」是 `_DISP_BUDGET=20` 秒(file: `scripts/lumos:46314`),但 `_codeloop_record_valid_ex` 單次逾時是 8 秒且不看 deadline,50 筆×最多約 3 次 git 理論上界遠超 20 秒;spec 要寫明 deadline 如何傳進有效性判斷(該函式有 timeout 參數可傳剩餘預算)。
file: `scripts/lumos:46538`(_codeloop_record_valid_ex 的 timeout 參數)

## F5 merge-tree 與 GitHub 實際合併結果不一致的邊界未涵蓋
severity: minor
blocking: 否 — 不一致時方向多為保守擋下;另一個方向(誤認)需配合 F1 才成立
引句:「第一行的樹等於合併提交的樹 → 回第二個母(合進來那一側的頂端)」
輸入:二進位檔(我實跑,二進位未改動時兩邊一致)、改名偵測差異(merge-tree 用本機 git 版本/設定的 rename 偵測,GitHub 用自己的實作)、本機 `.gitattributes` merge driver/`merge.renormalize`/`merge.conflictStyle` 設定會改變 merge-tree 結果、criss-cross(多個 merge-base)的虛擬基底不同。
照 spec:不一致=樹不等=照舊擋,屬保守但會讓部分合法 PR 在主線仍紅(天花板第 1 點只提解過衝突)。應該:天花板補一句「改名/合併驅動造成的差異也會照舊擋」;並要求 merge-tree 呼叫固定乾淨環境(忽略使用者設定),避免開發者本機與 CI 判定不同。空合併(兩邊相同變更,我實跑 rc=0 樹相等)會放行且母1 與合併樹相同的特例也落入 F1 的母1 未驗問題。

## F6 合併提交第二個母本身是合併提交、母2 紀錄記在已刪分支名
severity: minor
blocking: 否 — 保守方向(找不到就擋),且 spec 的「任何分支」查帳已涵蓋刪分支名
引句:「改在治理帳裡找「任何分支」的 pass/skip 紀錄」
輸入:(a)母2 是合併提交(分支把主線合進來才合回):spec 只驗母2 的紀錄,合法;但母2 內部的合併是否手改沒被驗,實質上信任母2 的審查,可接受,但應在 spec 明說。(b) pass 記在已刪除的分支名:因為不以分支名過濾而成立,這點是優點;但帳本裡 branch 欄位是 push 當時自述、非受信輸入,任一人能寫 `--branch` 任意名。與「現在信任目標分支紀錄的程度一樣」(實務隱患第一條)不完全等同:原本要偽造需知道目標分支名,現在「任何分支」不需要,範圍擴大。
照 spec:放行。應該:在「信任誰的紀錄」一節改寫成「信任面擴大為整本帳」並說明為何可接受。

## 範圍(已讀)
已讀,無 finding(除上述各條對其定義的批評)。

## 實務隱患
逐類:
- 信任/權限:見 F6(信任面擴大,非「一樣」)。
- git 版本:2.38 門檻正確,Apple Git 2.39.2 本機實測 `--write-tree` 可用;舊版 rc=129 會被正確歸入「其他回傳碼」。無額外 finding。
- 效能:見 F2、F4(帳本 12 萬行、50 筆上限、預算與逾時)。
- 金流/對外送出/不可逆:已排除,同意,理由是只改判定、不寫資料、不連網;唯 F1 是放行正確性而非這三類。
- 守衛面:spec 說兩個條件各有一格測試;缺第三個必要條件(母1 是已驗/主線側,見 F1),應補測試格。
- 併發/競態:無+為什麼:只讀帳與 git 物件,不寫狀態;帳本在 pass 與讀取間追加只會使結果多一筆可認紀錄。

## 驗收條款
引句:「合進來那側沒有紀錄、或紀錄之後又改過程式 應 照舊擋;舊合併請求的紀錄(之後動過程式)應 不被認」
S1/S2 缺:反向合併(F1)、帳本 >50 筆、同 head_sha 先 pass 後 blocked、git 不支援 --write-tree、淺 clone、逾時的測試格。建議補入。

## 回退
已讀,無 finding。

## 天花板
已讀,無 finding(F5 建議補一句)。

## 圖譜鏡頭
LUMOS-SPEC 對應的 [[Issues/code-loop-pass自失效追尾]]:本案沿用其「祖先且之後只動簿記檔」豁免,不影響其語意;但 F1 的母1 缺口讓同一份豁免被延伸到「合進來側」,與該 Issue「pass 不得蓋到新代碼」的原意衝突,故判影響(見 F1)。[[Systems/bound-tests-gate]]:合約測試在 2.5 步先於留痕判定執行,本案只動留痕那步,不影響。

總結:最嚴重 blocker;blocking 條數 3(F1、F2、F3)。
