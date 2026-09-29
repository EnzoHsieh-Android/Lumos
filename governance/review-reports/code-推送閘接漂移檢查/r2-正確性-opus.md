severity: major

# 推送閘接漂移檢查 代碼審 r2:正確性-opus

重現環境:`git clone --shared` 到 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/r2op`(HEAD dca86f7d),在那份的 `scripts/test_lumos.py` 插了兩支重現測試 `t_zz_r2op_repro`、`t_zz_r2op_repro2`(沿用 `_dr_repo`、`_dr_hook_fakes`、`_dr_hook_run`、`_dr_settle`,block 模式),用 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k t_zz_r2op_repro` 跑。repo 根沒動。

## F1 CI 起點補法只補了「before 空、全 0、找不到」,合過主線的推送在 CI 與消費專案 CI 範本照樣把主線上別人的轉正算進來
severity: major
blocking: 是
引句:「起點:before 在本機找得到就用它」
file: `scripts/lumos:28443`
file: `.github/workflows/ci.yml:151`
file: `/Users/enzo/rtb-mainwt/.github/workflows/ci.yml:4`

1. 掛鉤那邊這一輪改成自己算分岔點,理由正是「`git log 舊..新` 會把合進來的主線提交(別人的轉正)算成這次帶進來的」;CI 那步與 doctor 給消費專案的範本(`_DRIFT_CI_STEP`)只在 before 空、全 0、找不到時才換起點,before 找得到就原樣交 `before..sha`,lumos 的共用起點判法對找得到的起點不再算分岔點(`_lens_push_base` 找得到就原樣回)。同一個「合過主線」形狀,掛鉤判對、CI 判錯。
2. 工具鏈自己的 ci.yml 只在推 main 時跑(`branches: [main]`),碰不到這個形狀;但範本是貼給消費專案的,rtb 的 CI 是 `on: push`(所有分支都跑),照範本貼上就中。
3. 重現(`t_zz_r2op_repro` A 段):M0 推上主線 → feat 從 M0 開、推 F1 → 主線 M1 別人舊版 settle、預告句留著 → feat `git merge main` 得 F2。同一次推送:
   - 掛鉤:`A-hook rc 0`(範圍從 M1 起,正確)
   - 範本那步真的跑(`BEFORE=F1 SHA=F2`,python3 換成轉給真 lumos 的殼):`A-CI(before=f1 找得到,合過主線) rc 1`,印 `[c1 轉正了還寫預告] Verification/G.md…`、`✗ A CI 範本:合過主線再推,不該把主線上別人的轉正算進來  rc=1`
4. 補法本身還多出一個形狀:新分支首推(before 全 0)而頂端是「把 main 合進來」的合併提交時,`$SHA^1..$SHA` 是合併進來那一側的全部提交,不是註解說的「至少查這次推送的最後一個提交」。重現(A2 段,`BEFORE=全 0 SHA=F2`):`A2-CI(新分支首推,頂端是合主線的 merge) rc 1`、`✗ A2 CI 範本:新分支首推、頂端是合主線的提交,不該擋  rc=1`。
5. 影響:drift_check.gate=block 的消費專案,功能分支合一次主線就 CI 紅,而且被擋的人解不開(是主線上別人的句子);warn 模式是每次合主線 CI 都唸別人的筆記。判準同 r1 正確性 F1(那條已折入掛鉤),這裡是「只修了報上來的那個輸入」。

## F2 找主線先看本地 main 的 upstream、後看推送遠端的預設分支,整合分支不叫 main 或 main 追的是另一個遠端時,合過整合分支的推送照樣誤擋
severity: minor
blocking: 否
引句:「local _c _cands=("main@{upstream}" "master@{upstream}")」
file: `scripts/hooks/pre-push:59`

1. 候選順序是 main@{upstream} → master@{upstream} → `<遠端>/HEAD` → `<遠端>/main` → `<遠端>/master`。本地有 main 且設了 upstream 時,後面的遠端預設分支永遠輪不到。
2. git-flow(遠端 HEAD 指 develop、功能分支從 develop 開、合 develop):主線被認成 origin/main(舊),分岔點是 F1 的祖先,範圍退回 `F1..F2`,把 develop 上別人的轉正算進來。fork 流程(main 追 fork 自己沒同步的 main、功能分支合 upstream/main)同形。
3. 重現(`t_zz_r2op_repro` B 段):M0 推 main 與 develop,`origin/HEAD → origin/develop`;feat 從 develop 推 F1;develop 上 D1 別人 settle;feat 合 develop 得 F2;掛鉤帶 `origin <bare>` 推 feat:`B-hook rc 1`,drift 那行是 `--diff <F1>..<F2>`,`✗ B git-flow:功能分支合過 develop(遠端預設分支)再推,不該擋  rc=1`。
4. 工具鏈與 rtb 目前都是 main 單主線(rtb 的 upstream 都是 refs/heads/main),所以只標低;換到 git-flow 或 fork 的消費專案 block 模式就誤擋。

## F3 分岔點只取 `git merge-base` 的第一個,交叉合併(criss-cross)時可能挑到遠端舊值那一個,退回原樣範圍
severity: minor
blocking: 否
引句:「分岔點是遠端舊值的祖先(或同一個)→ 遠端舊值較新,用它」
file: `scripts/hooks/pre-push:77`

1. `_mb="$(git merge-base "$2" "$_ml" … | head -1)"` 在有多個合併基底時只看 git 挑的那一個。F1 推上去 → 主線 M1 別人轉正 → 本地 feat 先合 M1 得 F2 → 遠端主線把 PR(F1)合成 M2 → fetch 後推 F2:F2 與 M2 的合併基底是 {F1, M1} 兩個。git 挑 F1 時,「F1 是遠端舊值 F1 的祖先」成立,用 `F1..F2`,把 M1 算進來。
2. 重現(`t_zz_r2op_repro2` C 段,兩種先後各跑一次):
   - `M1先 bases: ['M1', 'F1'] picked: M1` → `hook rc 0 range from M1`
   - `F2先 bases: ['F1', 'M1'] picked: F1` → `hook rc 1 range from F1`、`✗ C criss-cross(F2先):feat 合了主線上別人的 M1 再推,不該擋  rc=1`
3. 結果取決於 git 挑哪個基底(跟提交先後有關),同一種推送時擋時不擋。要所有基底都是遠端舊值的祖先才用遠端舊值(`merge-base --all` 逐個 `--is-ancestor`),才不會挑錯。

## 查過、判不成立的分支(沒有 finding)

- 新分支(全 0):用分岔點;新分支開在主線頂端、零提交時範圍是 `L..L`,lumos 回 0。測試 ⑤ 釘著。
- 合過主線、重定基底、一般增量:與 `t_prepush_drift_range_ref_shapes` ②③④ 一致,且各有前置斷言證明原樣範圍會擋。
- 推主線本身(main-direct):main@{upstream} 就是遠端舊值,分岔點=遠端舊值,範圍是這次新加的提交,不會落進 [[Issues/code-loop守衛main-direct盲區]] 那種「範圍恆空」。推 main 到另一個落後的鏡像遠端:分岔點=本地頂端,範圍空;那些提交推 origin 時已查過,不算漏。
- tag:輕量 tag 有測試 ⑤;annotated tag(local_sha 是 tag 物件)我另跑了一次(`t_zz_r2op_repro2` D 段):`merge-base` 與 lumos 的 `^{commit}` 都會剝殼,`D annotated tag rc 1`,照擋,正確。
- 刪除 ref:迴圈在 drift 之前就 `[[ "$_lsha" == "$_ZERO" ]] && continue`,不會叫到。
- 遠端舊值本機找不到:`cat-file -e` 那道失敗 → 用分岔點;就算拿掉那道,`--is-ancestor` 對不存在的物件也回非 0,走同一條路。
- 主線找不到:原樣交並講一聲,測試 ③⑦ 都有斷言那句話。沒給遠端名(git 給的是網址)時 `refs/remotes/<網址>/HEAD` 解析失敗、跳過,不會出錯。
- 128 以上:lumos 沒有接 KeyboardInterrupt(`grep KeyboardInterrupt scripts/lumos` 無),Python 被 Ctrl-C 以訊號結束,bash 看到 130;掛鉤的 `trap … EXIT INT TERM` 先跑一次清理(不 exit),回到下一行 `dr_rc=130` → 印「被中斷」→ `exit 130` → EXIT trap 再清一次(`impact_done` 與 `rm -rf` 都可重入)。暫存目錄清得掉。測試 ⑨ 用 SIGTERM 真的走到這個分支。
- 其他非零:lumos 的 rc2 來源(範圍寫錯、終點找不到——git 逾時時 `_lens_full_sha` 回 None 也走這條)確實存在;舊版工具未知指令實測 `擋下:沒有「nosuchcmd」這個指令。` rc=2,與假 lumos 模擬的一致。判不了(git 失敗、預算用完)在 block 下是 rc1、會擋,不走「沒能跑完」那條——與 `cmd_drift_check` 的文件字串一致。
- CI 在淺層 checkout:`$SHA^1` 不存在 → 退空樹 → lumos 先偵測淺層、印「淺層 clone 算不出範圍」回 0。工具鏈 ci.yml 設 `fetch-depth: 0`,`SHA^1` 在;force push 的舊頂端沒被任何 ref 指到時不會被抓下來,走補法,正確。
- 範本與 ci.yml 的起點補法逐字相同:`t_doctor_drift_ci_template_start_fallback` ② 是把兩邊 `if … fi` 真的抽出來比、③ 在真 git 專案裡跑,不是空殼。錨定基準兩個雜湊我用 `git show HEAD:<檔> | shasum -a 256` 對過,與 patch 裡的新值相同。

## 圖譜鏡頭逐條判定

- Issues/code-loop守衛main-direct盲區(事故):不影響。這份 diff 沒動 code-loop 的範圍;漂移這道在 main-direct 推送時分岔點就是遠端舊值,範圍是這次新加的提交(見上一節),不重演「範圍恆空、守衛空轉」。
- Systems/存量漂移守衛(家):受 F1 影響。新 WHY 寫「doctor…給消費專案貼的 CI 步驟…用同一套 before 補法」屬實,但那套補法沒處理「合過主線」,跟同篇與 bound-tests-gate PITFALL 宣稱的「不把主線上別人的轉正算成這次的」在消費專案 CI 上對不上。
- Systems/每支檔有家、Systems/筆記內容閘(家):不影響。home check、note-shape 的範圍算法沒動;同形狀的疑慮已另開 Issue「推送前其他閘的範圍在合過主線時會多算」並帶 REVISIT。
- Systems/測試假綠形態(★INVARIANT★ 還原翻紅釘要有前置斷言):遵守。`t_prepush_drift_range_ref_shapes` ②③⑥ 每種先證明原樣範圍直接交 lumos 會擋;`t_doctor_drift_ci_template_start_fallback` ① 先證明 doctor 真的唸出步驟;⑨ 以「被中斷」字樣證明走到訊號分支。F1/F2/F3 這三種形狀沒有測試,是缺案例,不是假綠。
- Systems/anchor-integrity(★RISK★):不影響。基準的 pre-push 與 test_lumos.py 兩個雜湊對得上 HEAD。
- Systems/lumos-cli-lifecycle(★INVARIANT★ re-inject)、Systems/lumos-cli-read(★INVARIANT★ search 濾網):不影響。diff 沒碰 CLAUDE.md 注入與 search。
- Systems/bound-tests-gate:受 F1 影響,理由同存量漂移守衛;新 PITFALL ③「CI 裡前一步 fetch 過…整步跳過」的修法屬實。
- 只列名的其餘節點(canary-audit、design-loop、guard-kill、slim-get/slim-install/slim-uninstall、lumos-deinit、cochange-guard、節點範圍與索引守衛、check-r-guard、規格落成可驗收條件_計劃、雙向門放行_計劃、逃逸自動記_計劃):不影響。diff 只加漂移那段與它的測試,沒改這些節點管的指令、安裝器或掛鉤其他段(pre-push 其他閘的行沒動,只多了漂移範圍函式與回傳碼分支)。

最高等級:major
