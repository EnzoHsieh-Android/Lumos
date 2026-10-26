severity: minor

我先看了鎖檔 `…c4f8…732a.json.warming`。它不存在,所以我沒碰任何鎖,照派工詞審查。這次是逐條對照 README 中英、skill、計劃條款 S8–S14、S17、S29–S37、Systems 筆記和真程式。重現都在 `/tmp/lumos-seat-work/code-e2e-gate/合約-sonnet/` 的臨時複本裡做,沒有改被審的 repo。

先講已確認成立的部分:
- 對照表、`_PPC_KIND_SENTENCES` 和計劃正本三處逐字一致。
- 從複本裡把 `pre-push` 的 `android_e2e` 行拿掉,兩支守衛測試都翻紅;把那一句改掉也紅。
- 摘要行 `[test:]` 指到的測試函式都存在,`lumos lint Systems/android-e2e-acceptance` 為 0 問題。
- waive 的 y、n、Ctrl-C、沒有終端三種回應,以及鎖在確認之後才拿,程式都照條款做。
- S34 說的 `_vault_write_lock` 與「不自動接手殘留鎖」,程式也是這樣。

## Findings

1.
severity: minor
blocking: 否
引句:「兩邊都用 lstat 只讀一般檔,份數與單份大小同一組上限,一份讀不懂只跳過那一份」
file: `docs/lumos-toolchain-knowledge/Systems/android-e2e-acceptance.md:73`(PITFALL 行)、`scripts/lumos:41788`、`scripts/hooks/claude/lumos-entry-hook.py:300`
- 失敗場景:太大的紀錄在 lumos 這邊先占一個 500 份的名額,在開場掛鉤那邊先被濾掉、不占名額。
- 結果:兩邊算出的待看筆數不一樣,和 `_e2e_ai_pending_one` 註解說的「兩邊算出一樣」相反。
- 重現(修後):500 份各有 1 筆 AI 放行的小紀錄,再加 1 份最新的 2MB+10 位元組紀錄。lumos 算 499,掛鉤印「有 500 筆」。
- 重現(修前,501 份小紀錄,沒有太大的檔):lumos 算 501,掛鉤算 500。
- 測試缺口:`t_android_e2e_ai_count_copies_agree` 只放了 7 份檔,沒到 500 的邊界,抓不到這個差。
- 歸因:有證據的原有漏查。修前兩邊的上限本來就不一致(lumos 沒上限,掛鉤按檔名排序取前 500)。修補把兩邊對齊了,只剩太大檔的名額算法不同。

2.
severity: minor
blocking: 否
引句:「人用 `lumos android-e2e waive --ack <指紋>…`(可一次給多個)或 `--ack --all` 標成看過」
file: `scripts/lumos:41852`(`_e2e_ack_targets` 與 `_e2e_waive_ack`)、`scripts/lumos:41819`(`_e2e_ai_pending_all`)
- 失敗場景:一份紀錄帶有未看的 AI 放行,但 `runs.result` 不是認得的值,或 schema 比這版新。
- 結果:doctor、開場提示、推送三處都用寬鬆規則,照樣列出「1 筆待看」。`waive --list` 用嚴格規則,只印「讀不懂」。`--ack --all` 回 2:「讀不懂…這次不寫」。
- 後果:S14 說「確認後三處都不再列」,這份清不掉,只能手改檔。多份一起標時,前面的已經標了,後面的才失敗,會停在一半。
- 重現(修後):`probe_b.py`,結果 `pending_all` 有 1 筆、`_e2e_records_all` 為 None、`_e2e_waive_ack` 回 2。
- 重現(修前):同一份紀錄,`_e2e_ai_pending_all` 回 `[]`。
- 歸因:有證據的修復回歸,限 doctor 這條路。修前 doctor 用嚴格規則,和 `--ack` 一致;修補把它改成寬鬆。開場掛鉤修前本來就是寬鬆,那邊是原有漏查。

3.
severity: minor
blocking: 否
引句:「這個提交拿掉了 e2e 段(分岔點還有):刻意關掉驗收的那一次推送用 LUMOS_SKIP_ANDROID_E2E=1 關掉」
file: `scripts/lumos:41624`(`_e2e_gate_fps`)、`scripts/lumos:66756`(`_cl_say_e2e_block`)
- 失敗場景:這個提交刻意刪掉了 `e2e` 段,而分岔點還有。
- 結果:程式回的 dict 帶 `merge_main=True`,「接下來」印出 `git merge <主線> # …合進來之後這一版才有 e2e 段`。
- 後果:合併主線不會把被刪的段補回來。S36 說的「先把主線合進來」只適用於「舊分支沒有 e2e 段」,對「拿掉」這條路是錯指令,訊息本文講對了,指令行講錯。
- 歸因:有證據的修復回歸。「拿掉」這條路是修補新增的(修前這種提交直接放行),沿用了舊分支那條路的 `merge_main`。修前只有舊分支那一個 `merge_main` 呼叫點(`0aecbf90:scripts/lumos:41589`)。

4.
severity: minor
blocking: 否
引句:「判定應擋下(回 1);`waivers` 裡有一筆 `by` 是 human 或 ai、`note` 非空的放行時應放行」
file: 條款 S10 與〈資料怎麼流〉第 4 步「訊息改成「提交這支紀錄」」;`scripts/lumos:41640`
- 失敗場景:紀錄只存在工作目錄、還沒提交。
- 結果:程式印「這一版的查證紀錄還沒提交:<路徑>」,再印 `git add … && git commit -m "chore: 記錄 Android 端到端驗收"`。「提交這支紀錄」這句字面在程式和測試裡都沒有,測試只斷言「還沒提交」。
- 歸因:有證據的原有漏查。這是措辭差,功能對。

5.
severity: minor
blocking: 否
引句:「對照表句子跟計劃正本一致、兩支守衛測試認得含數字的種類名;放行時「提醒:」開頭的 AI 放行待看行與按功能放行行,經過真的 pre-push 也印得出來 [test:t_android_e2e_gate_wiring]」
file: `scripts/test_lumos.py:19790`(`t_android_e2e_gate_wiring`)、`scripts/hooks/pre-push`(逃生路那段)
- 缺口一:S12 說「擋下時 pre-push 的逃生路都要印出 android_e2e 的說明」,但沒有任何斷言守這段文字。
  - 重現:在複本裡把 `;Android 端到端驗收 → 照上面…` 到 `。緊急硬推` 之間整段刪掉,`-k android_e2e_gate_wiring` 仍是 5 passed, 0 failed。
- 缺口二:wiring 測試經過 pre-push 過濾的斷言只對「按功能放行」那一行。AI 放行待看行改成「注意:」開頭,wiring 仍 5 passed。那一行只由 S14 的測試(直接看 `code-loop check` 輸出,沒經過 pre-push)抓到,會紅 1 條。
- 降級說明:擋下訊息自己已經印了放行指令和 `LUMOS_SKIP_ANDROID_E2E=1`,所以逃生路缺的那段只是重複資訊,我定為 minor。
- 歸因:有證據的原有漏查。修前測試沒有這兩條斷言,修前 `pre-push` 也有同一句逃生路文字。

6.
severity: minor
blocking: 否
引句:「各道判定(合約測試、表態、新增告警、代碼審留痕;2026-10-20 起有資安登記時另有安全證據,排最前,共五道)」
file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:58`、`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:154`、`scripts/test_lumos.py:80016`、`scripts/test_lumos.py:80793`
- 這四處都還寫「五道」或「五句」,但本 diff 把對照表加成六種。
- `test_lumos.py:80016` 的註解還指向已改名的標記字「對照表五句的正本在這裡」,照它去找會找不到。
- 歸因:有證據的原有漏查。這是漏改的文字,測試不受影響。

## 圖譜鏡頭
- `lumos impact --diff 0701350…..ce46398…` 列出 `Issues/code-loop守衛main-direct盲區`(事故)等一批固定席節點,命中的是 `pre-push`。
- 我對照了 main 直推的情形:`_e2e_check_cmd` 與 `_secev_mainline` 都用推送前的主線位置,沒有掉進盲區。
- 這次輸出裡沒有「這次新增的殘留」這一段,所以沒有逐條可答的項目。

## 三問
1. 原問題的修復效果,行為證據如下。
   - 只改設定的推送會要求驗收,程式的比對邏輯在 `_e2e_gate_fps`、`_e2e_gate_need`。
   - 兩個出口(`LUMOS_SKIP_ANDROID_E2E=1`、CI)排在讀設定之後也生效,見 `_e2e_gate_evaluate` 最後一行。
   - 捷徑指到 `/dev/zero`:兩邊都改用 lstat。
   - 殘留鎖改用 `_vault_write_lock`。
   - 以上我跑 `-k android_e2e_gate_wiring`、`android_e2e_waive`、`android_e2e_ai_waiver_notice`、`prepush_cl_reason` 共 34 條,全綠。
2. 修補處的正常、錯誤與相鄰路徑,大致仍成立,但有兩處走偏。
   - doctor 的寬鬆計數和 `--ack` 的嚴格讀取不一致(Finding 2)。
   - 「拿掉 e2e 段」那條新路徑沿用了舊分支的指令(Finding 3)。
3. 新發現在修前、修後的結果:
   - Finding 1:修前兩邊不一致(501 對 500),修後只在太大檔時不一致(499 對 500)。
   - Finding 2:修前 doctor 不列(`[]`),修後會列。
   - Finding 3:修前直接放行,修後是擋下但帶錯指令。
   - Finding 4、5、6:兩版都存在。

最高等級 minor,擋實作 0 條。

臨時檔(探針腳本與修前版程式的副本)還在 `/tmp/lumos-seat-work/code-e2e-gate/合約-sonnet/`,臨時 clone 已刪,其餘請編排者收貨後清。
