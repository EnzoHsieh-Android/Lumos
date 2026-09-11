---
type: system
status: done
created: 2026-08-22
updated: 2026-08-22
about_code_stamp: batch-2026-08-23/2026-08-23/5461ed371d06
self_audit: sonnet/2026-08-30
aliases:
  - 受波及合約測試真跑閘
  - bound tests
  - 合約測試閘
tags:
  - type/system
  - status/done
  - scope/guards-gates
summary: |-
  FLOW:pre-push→code-loop check→impact --diff 固定席→合約行 [test:] 解平台→classify 存在性→逐支 _kill_run→紅/懸空/不合法=BLOCKED
  KEY:★INVARIANT★ code-loop check 對 impact 固定席上合約綁的測試逐支真跑,任一紅/懸空(dangling/fake)/方法名不合法/★證不出跑過(unfilterable)★ → blocked=True rc1;沒 run_cmd/diff 算不出/無固定席/沒綁 → 不擋但寫 gate=bound-tests 帳 [test:t_bound_tests_gate] [audit:sonnet/2026-08-22]
  KEY:★閘不得把「指令回成功」當「測試跑過」★(2026-09-09 消費專案接入靜默失效 [F];r1 代碼審把判準整條換掉):主力證據是★逐支看測試工具自己的輸出有沒有說「執行了 N 支(N≥1)」★(_RAN_EVIDENCE,只填實測過「跑 1 支」與「跑 0 支」兩種輸出的 profile:swift-xctest/csharp-xunit/node-jest/python);沒有樣式可比的 profile 才退回過濾能力冒煙測試(拿不存在的測試名跑一次看回不回 0)。任一支證不出來 → 狀態 unfilterable、不報綠,擋的路徑上跟紅一樣擋 [test:t_bound_tests_unproven_blocks_push]
  KEY:為什麼不是只用冒煙測試(同上,r1 實測推翻第一版):★大多數測試工具都分不出「測試不存在」與「測試通過」★——xcodebuild 三段 -only-testing 但方法名打錯回 0、dotnet test --filter 對不到回 0、jest -t 對不到回 0;只有 pytest(回 5)分得出來。只靠冒煙測試等於把最常見的幾種棧全判成不可信,不是擋錯人就是等於沒擋 [test:t_bound_tests_rejects_unfilterable_cmd]
  KEY:★xcodebuild 帶 -quiet 時跑 1 支跟跑 0 支的輸出一模一樣★(2026-09-09 在 calc-ios 實測,逐字比對過兩份輸出):所以 swift 骨架指令刻意不帶 -quiet,unfilterable 的訊息也直接點名這件事;dotnet 的解法是尾巴加 `-- RunConfiguration.TreatNoTestsAsError=true`(實測對不到回 1、對到回 0),已寫進骨架
  KEY:★「擋」跟「講」是兩個地方★(2026-09-09 代碼審 r2 blocker):判定在 _codeloop_guard_verdict、但印給人看的在 cmd_code_loop,後者原本只認 green/red——低風險推送因此在假綠上一個字都不印就放行,高風險擋下時也看不到逃生指令。動判定一定要回頭看列印分流 [test:t_code_loop_check_speaks_about_unproven]
  KEY:證據行不得被輸出截斷砍掉(同上 r2):輸出超過 256KB 取頭尾各半時,符合證據樣式的行要從中段撈回來(_kill_cap 的 keep_re);★審查席舉的 jest 實例實測不成立(jest 29 摘要仍在最後一行),這是防禦性修法★——沒有它等於押注「所有測試工具都把摘要印在最後」
  KEY:整套跑(run_cmd 沒有 {method})那條路也驗證據(同上 r2):整套跑但一支都沒執行、退出碼仍為 0 的情況不得報綠;★天花板:整套跑只證得出「有測試跑過」,證不出「你綁的那一支跑過」★
  KEY:★這一層不驗「跑的是不是正確那一支」★(同上 r2 訂正):它只數輸出裡有沒有「N passed」,不比對測試名。「合約綁的名字對到別支測試」是更早的存在性靜態檢查(resolve_test_refs 判 real/dangling/fake)擋下的,別把既有防線的功勞算到新機制頭上
  KEY:零覆蓋不再靜默(同上 [E]):四種來源各自出聲(找不到知識庫/沒節點引用/沒綁測試/算不出範圍),訊息帶「受波及合約測試」關鍵字以通過 pre-push 對 check 輸出的 grep 過濾 [test:t_bound_tests_explains_no_pins]
  KEY:(2026-09-09 表態閘起)pre-push 對每個分支 ref 都叫 check,低風險那一路帶 `--bound-tests-advisory`:紅了只印、寫帳、不擋(2026-09-07 人裁「低風險只提醒」搬進 check 內部執行,不再另呼叫 bound-tests --advisory);高風險不帶旗標,上面那條合約照擋;tag 推送仍走獨立的 bound-tests --advisory [test:t_prepush_computes_impact_once]
  KEY:掛在 check(擋的路徑)不掛 pass——design-loop bound-tests-gate-c r1 架構席抓到的;去重鍵=解析後完整指令(同 kill);超時用 runner 同名 LUMOS_TEST_TIMEOUT,whole-suite 600s(同 kill)
  KEY:逃生門 `code-loop check --skip-bound-tests --note` 或 `bound-tests --skip --note`(留痕 kind=skipped);CI 設 LUMOS_SKIP_BOUND_TESTS=1(CI 已跑全套)
  DEP:[[Systems/pitfalls-code-loop]]
  DEP:[[Systems/guard-kill]]
  KEY:[2026-09-11 多平台缺指令,Issues/多平台設定下測試指令被默默略過]沒設 run_cmd 改成★逐平台★——有指令的平台照跑,沒指令的平台那幾支列成 not_run(平台點名);全部沒指令才 no-config;原本碰到第一支沒指令就整批 no-config,連前面已判的懸空紅都被吞掉(違反上一行合約「任一懸空 → 擋」的原意)。訊息改由 _no_run_cmd_reason 給:多平台點名平台,最上層還留著 test.run_cmd 就照 2026-07-10 並存優先序講明它不生效、要搬;code-loop check 與 bound-tests 兩條路共用 [test:t_bound_tests_multiplatform_missing_cmd]
  TEST:t_bound_tests_gate(綠/紅/懸空/逃生門/env/no-config/壞設定檔/新分支首推 12 斷言(2026-08-30 機械重數訂正,原記十));本 repo 實跑 42 支 29s
verified_by:
  - "[[Verification/2026-09-09_接入靜默失效七項落地]]"
  - "[[Verification/2026-09-11_多平台缺指令逐平台處理]]"
about_code:
  - .github/workflows/ci.yml
  - scripts/hooks/pre-push
  - scripts/lumos
---
# bound-tests-gate

# bound-tests-gate

> 白話:改到相依功能,以前工具只會「點名」那些功能綁的測試,跑不跑靠自律。現在 pre-push 每次呼叫的 `code-loop check` 會把被點名的測試當場跑完:紅的、綁了不存在測試的、名字不合法的,一律擋推送。

## 怎麼跑

★2026-09-07 起有兩條路★([[Projects/合約測試閘什麼時候跑_計劃]],人裁):
- **高風險推送**:照舊藏在 `code-loop check` 裡,紅了**擋**。
- **低風險推送**:pre-push 同一次 `code-loop check` 帶 `--bound-tests-advisory`(2026-09-09 表態閘起;之前是另外呼叫 `lumos bound-tests --advisory`,現在只有 tag 推送還走那條),紅了**印出來、記帳,但不擋**。
  不選「低風險也擋」的理由:擋下去最可能的結果不是人去修測試,是人改走 `--no-verify`
  ——而 pre-push 自己在別的地方就把那條當第三選項在教,那條零留痕。

★而且波及計算一次推送只算一次★:pre-push 算一份寫進暫存檔給這道閘(`bound-tests --from-json`)讀。
以前同步點名(`impact --sync-only --from-json`)也讀這一份;2026-09-11 起推送前的點名改由 [[Systems/每支檔有家]] 照家算,不再讀它。
算不出來時這道閘記 `range-unavailable` 放行,不拖垮別的檢查。

1. `impact --diff <range>` 取固定席(合約/事故/直接相依)裡帶合約的節點。
   ★新分支首推★:起點是空樹時改用主線 tip(`_mainline_ref`),不是放棄計算、也不是跑滿全部;
   連主線都問不到才記 `range-unavailable`。
2. 每個節點的 ★INVARIANT★ 行 `[test:…]` 用 `resolve_test_refs` 解平台前綴,再用 Check T 同一套平台真測試索引判存在(real/dangling/fake)。
3. real 的逐支用 `.lumos/config.json` 的 run_cmd 真跑(`_kill_run`,同 kill);去重鍵=完整指令。超時:單支 `LUMOS_TEST_TIMEOUT`(預設 180s,同測試 runner),整套(run_cmd 無 {method})600s。
4. 任一紅 → check 回 BLOCKED(rc1),訊息列合約、測試、尾段輸出,並給 `--skip-bound-tests --note` 範本。

## 帳的類別(2026-09-07 拆細,不擋的都寫帳讓零觸發看得見)

`green` / `red-advisory`(低風險,只提醒) / `red-blocked`(高風險,擋) /
`skipped-flag`(人給了理由) / `skipped-env`(CI 環境變數) /
`no-config`(沒 run_cmd) / `no-pins`(沒固定席) / `no-bound`(固定席沒綁測試) /
`range-unavailable`(範圍算不出,含首推連主線都問不到) /
`whole-suite-deferred`(測試指令不可過濾、而且這次是低風險 → 不跑)。

★為什麼要拆這麼細★:紅了擋跟紅了只提醒,後果完全不同;人給理由跳過跟 CI 常態跳過,
意義也完全不同。混成同一個 kind 就回答不了人裁時掛的那條回頭條件(「只提醒到底夠不夠」)。
★耗時也拆成兩個獨立欄位★(`secs` 跑測試、`calc_secs` 算波及):
以前塞在自由文字的備註裡,回頭條件量不到。

`gov --stats` 看 bound-tests 那列就知道這道閘在這個專案有沒有真的開。

## 設計迴圈紀錄
`bound-tests-gate-c` r1 四席(通才/正確性邊界/可執行性成本/架構對齊)20 條:19 折 1 放行(hermetic:run_cmd 是專案自宣告指令,與 CI 同信任邊界)。我自己記帳走歪兩次(處置帳一輪只能一筆;每席都要留痕)才過閘,編號 -b/-c 是這樣來的。

## 回頭看條件
- 30 天後 `gov --stats` 若 bound-tests 只有 no-config/no-pins、零 green/red → 入口 hook 加「本專案沒設 run_cmd,合約測試閘沒開」提醒;再 30 天仍零 → 列入只退場不痛的機制檢討。
- 三次 check 超過 3 分鐘 → 加只跑 direct 相依的縮圈選項。
- gov --stats 出現 red 且原因是外部資源 → 加單支白名單跳過。

## 鏡頭側呈現(2026-09-03 v1.1)

`lumos dispatch-lens` 對每條 ★INVARIANT★ 合約行用同一個 `_classify_one` 標「綁定測試:有/懸空/偽證據」或「★裸合約★」,並在段尾固定寫「有=方法存在,不代表跑過或有殺傷力(閘只看 rc)」。鏡頭是參考、本閘是判決:鏡頭讀 base 版合約行、閘讀工作樹版節點,分支改了合約行時兩邊可能不同。單源 [[Projects/派工鏡頭注入_計劃]] v1.1 節。
