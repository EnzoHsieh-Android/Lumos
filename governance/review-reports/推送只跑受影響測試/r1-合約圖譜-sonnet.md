severity: major

我只讀了 spec、筆記和程式碼,沒動 repo。我沒跑 `spec-gate`,因為它會寫留痕,所以條款句式(S1、S3 有複合觸發)我沒驗。

## 固定席逐條

- **bound-tests-gate 的 ★INVARIANT★**:這份設計沒破壞它。高風險推送在 `code-loop check` 裡真跑合約測試、紅了擋,spec 明說不動。CI 的 `LUMOS_SKIP_BOUND_TESTS` 只在 gates 的 push 事件步驟,PR 事件不跑那步,所以 PR 改跑子集也沒拿掉後盾。同一篇有幾行日期 KEY 會變成假話,見 F3。
- **guard-kill 兩條、lumos-cli-read 一條**:無關,已讀,無 finding。
- **design-loop 處置閘第五步**:S1–S6 有 `[test:]`,S7 是 `[manual:…]`(字數夠),形式上過得了。句式文法沒驗。
- **lumos-cli-lifecycle、slim-install、slim-uninstall(sentinel 以外 byte-equal)**:spec 第 8 點若改範本 `scripts/templates/graph-discipline.md`,`CLAUDE.md` 的紀律區塊要靠重新注入同步,不能手改。spec 沒講這點,見 F3。

## findings

### F1 強制全套的環境變數會讓自己的新測試在逃生推送時變紅
severity: major
blocking: 是(照字面實作,用逃生寫法推送就會被測試擋下)
spec 段落:做法 6、驗收 S1–S3。
引句:「`LUMOS_PREPUSH_FULL=1 git push` 這次推送前跑全套(不留帳,它是多跑不是少跑)」

問題:`LUMOS_PREPUSH_FULL=1 git push` 會讓掛鉤跑全套,全套測試繼承這個變數。S1(`t_suite_affected_for_feature_branch`)期望回 `affected`、S3 在子程序裡跑掛鉤。這兩支一讀到變數就改回 full,於是逃生推送被「測試有紅」擋下。

佐證:`測試假綠形態` 已記過同族事故:照逃生段 `LUMOS_SKIP_REREAD_CHECK=1 git push` 推,全套反而紅。當時的修法是在 `_isolate_environment` 用前綴清掉 `LUMOS_SKIP_*`,但新變數叫 `LUMOS_PREPUSH_FULL`,不在這個前綴裡。spec 沒要求清它,也沒有對應測試。

file: `scripts/test_lumos.py:48724`(`startswith("LUMOS_SKIP_")` 只清這個前綴)
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:23`

建議:在 `_isolate_environment` 加清這個變數,並加一支「帶著該變數跑測試,S1 仍綠」的測試。

### F2 掛鉤對 `affected` 的狀態與自主迴圈處理沒定義,自主迴圈會被靜默少跑
severity: major
blocking: 是(照字面實作會漏測)
spec 段落:做法 3。
引句:「`suite=affected` 時跑「文件子集 + 關鍵字子集」(同現行 light 的跑法,同樣分片同時跑)」

問題:現行掛鉤用 `_SUITE_FULL`、`_SUITE_LIGHT` 兩個旗標加 `_AUTOLOOP_FULL` 做決定,且 `_AUTOLOOP_FULL` 只在 light 分支裡設。spec 沒說這些:
- **新旗標與多 ref 混合**:一次推多個 ref,結果混著 affected、docs、light、full 時怎麼合併,關鍵字怎麼聯集。
- **自主迴圈測試**:掛鉤現在對「不是全套」的情況一律只跑 `-k real_claude_md`,只有 light 且 `autoloop_full` 才整支跑。affected 不是 light,沒人設 `_AUTOLOOP_FULL`,改到自主迴圈模組的功能分支推送會被靜默少跑那 144 支。spec 第 4 點只處理了 CI 的 gates,沒處理本機掛鉤。
- **舊掛鉤配新 lumos**:`pitfalls --json` 多了 `suite: affected`,舊掛鉤只認 `"suite": "docs"`,其餘當 full。這個方向是安全的,但 spec 沒寫,也沒測試守。

佐證:
file: `scripts/hooks/pre-push:543`(per-ref 判 `_suite_this`)
file: `scripts/hooks/pre-push:818`(自主迴圈只在 light 且 `autoloop_full` 才整支跑)
file: `scripts/hooks/pre-push:871`(`_suite_mode` 只有 docs、light、full)

### F3 共用函式 `_mainline_ref` 改動的波及面沒盤點,也沒接住既有的 REVISIT
severity: major
blocking: 是(多個閘的範圍會變,只有表態閘有測試)
spec 段落:做法 7、驗收 S6。
引句:「`_mainline_ref` 認不到 `main@{upstream}`(追蹤設定指向不存在的遠端,本 repo 就是)時,先找各遠端的 `main`/`master` 追蹤分支」

問題:
- 範圍只寫「表態閘」,但 `_mainline_ref` 有 7 個呼叫端:筆記形狀擋與筆記內容閘(`remote_only=True`)、新分支首推的合約測試範圍(`bound-tests-gate`「新分支首推」那條)、派工鏡頭等。
- 它的 docstring 明說 `remote_only=True` 就是「只認 upstream」,語意是故意的。S6 只測表態閘,其他呼叫端沒有紅燈守。
- spec 說「同 `_push_mainlines` 的候選」,但 `_push_mainlines` 需要遠端名和被推的 ref,`_mainline_ref(repo_root, remote_only)` 兩者都沒有。遠端名要從哪來沒說。
- 這件事已有立案:`pitfalls-code-loop` 的 REVISIT 2026-11-13 寫了「改成共用 `_lens_default_base`」的做法,附帶 `-k reread_fp` 要一起綠。`Issues/推送前其他閘的範圍在合過主線時會多算` 也寫「收斂時兩邊一起改」。spec 開了第三條路,沒提這兩處,也沒說做完要關掉它們。

佐證:
file: `scripts/lumos:65710`(`_mainline_ref`)
file: `scripts/lumos:65263`(`_push_mainlines`)
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:247`
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:22`

### F4 說明文字同步漏列幾處會變成假話的句子
severity: minor
blocking: 否(文件精度,不改行為)
spec 段落:做法 8。
引句:「專案 CLAUDE.md〈本 repo 的測試子集怎麼跑〉一段、`Systems/bound-tests-gate` 的現況說明、推送前掛鉤印的提示改成新規則」

問題:同一句「全套留給推送前的閘」還在三處:`CLAUDE.md:61`、`AGENTS.md:62`、`scripts/templates/graph-discipline.md:59`。改了推送前的行為後它就不實了。`CLAUDE.md` 的紀律區塊是範本注入的,要改範本再重新注入(sentinel 之外 byte-equal,手改會被覆蓋或造成漂移)。

另外:
- `bound-tests-gate` 有一行 2026-09-18 的 KEY 寫「CI 只認 docs…pull_request 一律全套」「CI 對 light 照跑全套當後盾」,上線後就錯了。spec 只籠統寫「現況說明」。
- 全域 CLAUDE.md 的 Q1 只問一句。〈推送前〉另一條「要等 CI 結果出來才回報完成」,在 PR 的 CI 只跑子集後,意思也會變。
- 記憶裡的 `dont-rerun-verified-work`、`run-full-gate-locally-before-push` 也寫「全套交給推送前閘」,應排進記憶過期清掃。

佐證:
file: `CLAUDE.md:61`
file: `AGENTS.md:62`
file: `scripts/templates/graph-discipline.md:59`

### F5 改 `ci.yml` 的自主迴圈步驟會踩到逐字指紋守衛,spec 沒提
severity: minor
blocking: 否(實作時測試就會紅,不會漏過)
spec 段落:做法 4、驗收 S4。
引句:「PR 事件 affected 時,gates 工作的自主迴圈測試照推送前掛鉤同一條規則(`_autoloop_full_for`:關鍵字碰到自主迴圈就整支跑),不再只認 docs。」

問題:`t_ci_yml_matrix_and_gates_shape` 用指紋 `70b4cb1b0437f13e` 釘死「自主迴圈測試」步驟逐字不變,對應 `CI加速_計劃` 的合約「後盾步驟逐字照搬」。改這一步會讓那支現有測試變紅。spec 的 S4 只列新測試 `t_ci_yml_affected_shape`,沒說要改指紋,也沒說這是刻意推翻「逐字不改」。

佐證:
file: `scripts/test_lumos.py:87127`

### F6 基準線單獨被改時是否仍全套,spec 沒有明確測試
severity: minor
blocking: 否(S2 的「抽不出關鍵字」規則大致涵蓋)
spec 段落:做法 1、S1。
引句:「守衛檔裡的測試檔簽名基準 `governance/anchor-baseline.json` 在這裡不強制全套」

問題:`_DOCS_ONLY_NEVER` 的註解寫明,只推基準線會被當純文件,是兩段式竄改的第一步(代碼審 r3 資安席)。spec 的豁免若實作成「從 `guard` 清單拿掉」,基準線單獨改就變回 docs。只要把豁免限定在 affected 分支內就沒事。S1 只測「多改了基準線仍是 affected」,沒有「只改基準線仍全套」的案例。

佐證:
file: `scripts/lumos:61672`
file: `scripts/lumos:61675`

### F7 撤除條件的第二條沒有量測來源
severity: minor
blocking: 否
spec 段落:RETIRE-IF。
引句:「或八週內功能分支推送前的測試時間中位數沒有比上線前少一半以上」

問題:推送前掛鉤沒有記測試耗時的治理帳(只有擋下時的 `prepush-summary`)。「上線前」基準只有 2026-11-05 的一次實測。這一臂到期時算不出來。專案規則要求撤除條件可機械量,要嘛這份計劃加記帳,要嘛改寫這一臂。

佐證:
file: `scripts/lumos:65388`(`prepush-summary` 只在擋下時記)

### F8 落點與要收尾的舊記錄
severity: minor
blocking: 否
spec 段落:前言 `lands_in`、做法 8。

- `lands_in` 只有 `Systems/bound-tests-gate`,該篇現況是「掛 0 份計劃、沒寫負責範圍」,已經有 18 行 KEY。
- 表態閘範圍(做法 7)應落在 `Systems/pitfalls-code-loop`(或表態閘那篇),並關掉上述 REVISIT 2026-11-13。
- 父計劃 `推送與CI提速_計劃` 有 `REVISIT:2026-11-14 …開第二階段`,這份就是第二階段,spec 沒說要更新或結掉它。
- 新增的 `notify` 工作和 `main-red` Issue 流程是新機制,值得有自己的家。

### F9 notify 工作的權限與 schedule 的存活
severity: minor
blocking: 否(已超出圖譜一致性範圍,順手記)
spec 段落:做法 4。
引句:「這個工作要 `issues: write` 權限,只給它,不給其他工作。」

問題:job 層級的 `permissions` 會取代頂層的 `contents: read`。notify 要 checkout 並重算選測清單,所以得同時宣告 `contents: read` 和 `issues: write`。另外 GitHub 對一段時間沒活動的 repo 會停用 schedule(印象中約 60 天,我沒查證),單人 repo 可能停擺,實務隱患節沒提。

## 其他段落
〈舊否決對照〉〈現況〉〈範圍〉〈回退〉:已讀,無 finding。
對程式碼的 5 條現況宣稱(`light_ok` 的條件、`_DOCS_ONLY_NEVER` 內容、`run_group` 空片回 3 與沒用到的 `_krc_all3`、`ci.yml` 的 prep 只問 push 事件、`main@{upstream}` 因遠端叫 `Lumos` 而認不到)我都對過,全部成立。

## 實務隱患
spec 自己列的風險類我沒有補到新的。

總結:最嚴重等級為 major,共 3 條會擋的問題(F1、F2、F3),其餘 6 條為 minor、不擋。
