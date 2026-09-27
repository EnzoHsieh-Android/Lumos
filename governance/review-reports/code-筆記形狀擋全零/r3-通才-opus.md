severity: major

# r3 通才席(opus)——正確性鏡頭

範圍:r3-delta.patch(`_lens_push_base` 加「頂端＝主線頂端→空樹」、ci.yml code-loop 步驟改原樣交前一版、doctor 步驟 `||` 補空值、t_push_base_zero_or_missing 改寫)。
跑過:`python3 scripts/test_lumos.py -k push_base_zero` → 11 passed。實驗都在 scratchpad/r3exp 的臨時 clone(`git clone --shared`),沒動 repo。

先把題目問的幾條路徑走完(沒問題的不列成 finding):

- **CI 推 main 時 code-loop 那步有沒有主線**:有。模擬 actions/checkout 的 `git checkout --progress --force -B main refs/remotes/origin/main`,git 印出 `branch 'main' set up to track 'origin/main'.`,`main@{upstream}` = origin/main = 這次的 SHA。所以 code-loop 那步雖然排在「建本地 main」之前,照樣找得到主線。
- **正常推 main(before 是真的提交)**:走不到新加的分支。`_lens_full_sha(before)` 先成立就直接回。fetch-depth: 0 讓 before 在本機找得到。
- **本機 pre-push 會不會傳 40 個 0 進這三道**:不會。code-loop 拿到的是 `pp_range_for` 換過的空樹..頂端,一進 `_lens_push_base` 就從 `a == _EMPTY_TREE_SHA` 那行直接回。home check 與 note-shape 拿到的是 `_hrange`,用 `--not --remotes` 算出真提交,全在遠端就整個不叫。所以新分支這條只有 CI 會走。
- **`||` 在 GitHub 表達式遇到空字串**:空字串是假值,會回 `'0000…'`。push 事件的 before 永遠有值,這個補值只在照抄時漏了 `if:`、被 pull_request 觸發的情況下才用得到。沒問題。
- **主分支叫 master**:`_mainline_ref` 依序試 `main@{upstream}`、`master@{upstream}`,可以找到。但 doctor 給的那步寫死 `git branch --track main origin/main`,master 專案沒照說明改掉的話,主線找不到,就退回「空樹、截到上線點」。這是既有行為,不是這一輪引進的。

## F1 新規則回傳的空樹,代碼審那道不截上線點——主線頂端開的零提交新分支被整個 repo 當新增擋下
severity: major
blocking: 是 —— 這一輪新引進、可穩定重現的誤擋。三個呼叫端共用的函式回了一個值,違反它自己文件寫的呼叫端約定;測試 ⑦ 還被改寫成剛好繞開這個情況。

引句:「用空樹時呼叫端照樣截到上線點。」

三個呼叫端只有兩個真的會截。home check(file: `scripts/lumos:23385`)與 note-shape(file: `scripts/lumos:23990`)有接 `_nodehome_clamp_base`。`_codeloop_guard_verdict` 沒接(file: `scripts/lumos:30726`),拿到空樹就直接把 `空樹..頂端` 交給合約測試、pitfalls 分級、表態、新增告警閘(file: `scripts/lumos:30823`)。結果是整個 repo 的每一行都算「這次新增」。

r2 時,頂端等於主線頂端會落在「已在主線上→None」,代碼審那道說「沒有新東西」放行。這一輪改回空樹之後,同一個輸入變成整庫掃描。

最小重現(臨時 clone 的本地 main 追蹤 origin/main,開一個零提交的新分支,用 CI 的形狀呼叫):

```
git clone -q --shared <repo> c1 && git -C c1 checkout -q -b release-1
python3 probe.py c1 0000000000000000000000000000000000000000..065be851… release-1
→ push_base: ('4b825dc6…', '新分支首推,頂端就是主線(main@{upstream})頂端——…從上線點起全查')
→ range fed to gates: ['4b825dc642cb…..065be851…']        ← 沒截上線點
→ verdict: blocked=True tier=high reason='754 條新增告警' reason_kind=lint_new
LUMOS_SKIP_LINT_NEW=1 再跑一次:
→ verdict: blocked=True tier=high reason='tier=high 且無留痕(尚未跑 code-loop pass/skip)'
對照:同一個 clone 用 main~1 當頂端 → (None, '…頂端落後主線…——沒有新東西')
```

probe.py 的做法:把 `scripts/lumos` 當模組載入,包住 `_bound_tests_check` 記下收到的範圍,再叫 `_codeloop_guard_verdict(repo, diff_range=…, at_sha=頂端, branch=…)`。

「差一個提交放行、剛好在頂端就整庫 754 條擋下」,說明這不是「寧可多查新提交」,而是把整段歷史當新增。

同一個缺口還有兩處:

- 測試 ⑦ 原本斷言「頂端已在主線上時說沒有新東西」,是對 main 頂端呼叫;這一輪改成對 `old-tag`(落後主線)呼叫。代碼審那道在「頂端＝主線頂端」時的新行為因此完全沒有測試。
- ci.yml code-loop 那步的新註解寫「跟 note-shape 那步同一支判法」,會讓人以為兩邊行為一致。實際上 note-shape 會截上線點,code-loop 是整庫。

本 repo 自己的 CI 只在推 main 時跑,只有 force-push 主線會走到這裡,而改前的 ci.yml 本來就把它換成空樹,所以本 repo 沒有退步。退步出現在兩種情況:照 skill 說的「CI 對每個分支 ref 都叫 code-loop check」、而且 CI 裡有本地 main 追蹤 origin/main 的專案(開零提交分支或打標籤就紅);以及手動 `lumos code-loop check --diff 000…..HEAD`。

改法方向:代碼審那道在 `_lens_push_base` 回空樹時要有自己的截法,或對「頂端＝主線頂端」照 r2 回 None。最少也要把 docstring 那句改成只對兩個呼叫端成立,並補一條 ⑦ 在主線頂端的斷言。

## F2 「分不出推主線還是新分支」這個前提不成立;為了它重新引進 r2 已經否決的誤擋,而且測試 ④ 變成假綠
severity: major
blocking: 否 —— 這是作者明說的取捨(寧可多查),不是寫錯;但取捨的前提有反例,又連帶讓一條測試的名字與行為對不上。屬於要記下、另排修正的設計債,不擋這一輪。

引句:「★頂端正好等於主線頂端時用空樹★(推主線本身與剛開在主線頂端的新分支分不出來,寧可多查——」

同一段 docstring 下面還寫著「★也不能一律當空樹★:新分支開在主線頂端時會把主線上線後的舊帳當新增誤擋」。這一輪正好在「新分支開在主線頂端」這個情況改回空樹,等於自己推翻了這句。

**分得出來。** 前面已經驗過本機 pre-push 永遠不會把 40 個 0 傳進來,所以只有 CI 會走到這條。GitHub push 事件的內容本來就帶 `created`(新 ref)與 `forced`(force-push)兩個布林值,在 CI 用 `${{ github.event.forced }}` / `${{ github.event.created }}` 就能把兩種情況分開,不必一律整段重查。

假綠的測試:④ 標題是「每支檔有家:新分支沒有新提交時不查」,斷言只有 `rc == 0`。這一輪之後它其實**有查**(從上線點起全查),會綠只是因為測試專案的主線乾淨。重現:同一套骨架在主線上多一個 `--no-verify` 進去的沒家檔,再從頂端開 `feat`:

```
_nh_check(h, "--diff", "0"*40 + ".." + head)
→ (1, '每支檔有家:新分支首推,頂端就是主線(main@{upstream})頂端——…從上線點起全查
      擋下:這次推送有 1 條「每支檔有家」的新違規。… src/:debt.py …')
```

所以 ④ 的名字與斷言已經說不出它在驗什麼,而且跟 ①b 互相矛盾:①b 斷言同一個情況會查、會擋。

實際會擋掉的東西:一個專案先用 note_shape.gate=warn / node_home.gate=warn 跑一段時間(每次推 main 只看增量,舊的違規留在主線上),之後切成 block。從此在主線頂端開的零提交分支、標籤推送,CI 都會被 warn 時期的舊帳整批擋下。正常推 main 的增量範圍則不會報這些。這就是 docstring 自己列為不能做的「把主線上線後的舊帳當新增誤擋」。

## F3 force-push 主線後十分鐘內再推一次,被改寫的內容照樣整批放過(這一輪要補的洞,修法沒補完)
severity: major
blocking: 否 —— 要三個條件同時成立才會漏:`--no-verify` 繞過、force-push 主線、在 CI 跑到 note-shape 那步之前又推一次主線。這道閘是後盾,不是唯一的閘。但這一輪的目的就是「force-push 改寫主線不整批放過」,修法本身在常見時序下仍然會漏,應該記一筆回頭看的條件。

引句:「頂端落後主線就不查,」

ci.yml note-shape 那步第一件事是 `git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'`(file: `.github/workflows/ci.yml:131`),把 origin/main 更新到**執行當下**的遠端主線,而不是這次推送的 SHA。這一步排在全套測試(約 10 分鐘)之後。

force-push 主線後,只要在這個 run 跑到 note-shape 之前又推了一個提交,這個 run 看到的就是「頂端落後主線」,回 None 不查。下一個 run 的 before 是被改寫的頂端(本機找得到),只查新推的那一個提交。被改寫的內容兩個 run 都沒查到。

最小重現(沿用測試 ⑧ 的骨架,多推一個後續提交):

```
f=_ns_repo(); _ns_note(f,"乾淨"); commit c1; _pb_remote(f)
_ns_note(f,"force-push 塞進來的 `src/a.py:6`"); commit --amend; push --force origin HEAD:main   # bad=這個頂端
README 改一行; commit; push origin HEAD:main; fetch                                           # 後續推送
_ns(f,"--diff","2"*40+".."+bad)  → (0, '筆記形狀擋:起點在本機找不到,而且頂端落後主線(main@{upstream})——沒有新東西')
_ns(f,"--diff",bad+"..HEAD")     → (0, '')
```

測試 ⑧ 綠,是因為 force-push 之後沒有後續推送。

改法方向:跟 F2 同一把鑰匙。CI 在 `github.event.forced == true` 時直接當「頂端＝主線頂端」處理(從上線點起查),不看執行當下的主線。或者 note-shape 那步只在缺本地 main 時建立、不重抓已經在的 origin/main。

最嚴重等級 major,需要擋的 1 條(F1),另 2 條記下不擋(F2、F3)。
