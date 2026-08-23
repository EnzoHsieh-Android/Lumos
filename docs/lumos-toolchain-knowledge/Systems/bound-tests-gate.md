---
type: system
status: doing
created: 2026-08-22
updated: 2026-08-22
about_code_stamp: batch-2026-08-23/2026-08-23
aliases:
  - 受波及合約測試真跑閘
  - bound tests
  - 合約測試閘
tags:
  - type/system
  - status/doing
summary: |-
  FLOW:pre-push→code-loop check→impact --diff 固定席→合約行 [test:] 解平台→classify 存在性→逐支 _kill_run→紅/懸空/不合法=BLOCKED
  KEY:★INVARIANT★ code-loop check 對 impact 固定席上合約綁的測試逐支真跑,任一紅/懸空(dangling/fake)/方法名不合法 → blocked=True rc1;沒 run_cmd/diff 算不出/無固定席/沒綁 → 不擋但寫 gate=bound-tests 帳 [test:t_bound_tests_gate] [audit:sonnet/2026-08-22]
  KEY:掛在 check(擋的路徑)不掛 pass——design-loop bound-tests-gate-c r1 架構席抓到的;去重鍵=解析後完整指令(同 kill);超時用 runner 同名 LUMOS_TEST_TIMEOUT,whole-suite 600s(同 kill)
  KEY:逃生門 --skip-bound-tests --note(留痕 kind=skipped);CI 設 LUMOS_SKIP_BOUND_TESTS=1(CI 已跑全套)
  DEP:[[Systems/pitfalls-code-loop]]
  DEP:[[Systems/guard-kill]]
  TEST:t_bound_tests_gate(綠/紅/懸空/逃生門/env/no-config 十斷言);本 repo 實跑 42 支 29s
verified_by:
  - "[[Verification/2026-08-22_受波及合約測試真跑閘落地]]"
about_code:
  - .github/workflows/ci.yml
  - scripts/hooks/pre-push
  - scripts/lumos
---
# bound-tests-gate

# bound-tests-gate

> 白話:改到相依功能,以前工具只會「點名」那些功能綁的測試,跑不跑靠自律。現在 pre-push 每次呼叫的 `code-loop check` 會把被點名的測試當場跑完:紅的、綁了不存在測試的、名字不合法的,一律擋推送。

## 怎麼跑
1. `impact --diff <range>` 取固定席(合約/事故/直接相依)裡帶合約的節點。
2. 每個節點的 ★INVARIANT★ 行 `[test:…]` 用 `resolve_test_refs` 解平台前綴,再用 Check T 同一套平台真測試索引判存在(real/dangling/fake)。
3. real 的逐支用 `.lumos/config.json` 的 run_cmd 真跑(`_kill_run`,同 kill);去重鍵=完整指令。超時:單支 `LUMOS_TEST_TIMEOUT`(預設 180s,同測試 runner),整套(run_cmd 無 {method})600s。
4. 任一紅 → check 回 BLOCKED(rc1),訊息列合約、測試、尾段輸出,並給 `--skip-bound-tests --note` 範本。

## fail-open 四情境(不擋,但都寫帳讓零觸發看得見)
沒 run_cmd(kind=no-config)/ diff 算不出(diff-unavailable)/ 沒固定席(no-pins)/ 固定席沒綁測試(no-bound)。`gov --stats` 看 bound-tests 那列就知道這道閘在這個專案有沒有真的開。

## 設計迴圈紀錄
`bound-tests-gate-c` r1 四席(通才/正確性邊界/可執行性成本/架構對齊)20 條:19 折 1 放行(hermetic:run_cmd 是專案自宣告指令,與 CI 同信任邊界)。我自己記帳走歪兩次(處置帳一輪只能一筆;每席都要留痕)才過閘,編號 -b/-c 是這樣來的。

## 回頭看條件
- 30 天後 `gov --stats` 若 bound-tests 只有 no-config/no-pins、零 green/red → 入口 hook 加「本專案沒設 run_cmd,合約測試閘沒開」提醒;再 30 天仍零 → 列入只退場不痛的機制檢討。
- 三次 check 超過 3 分鐘 → 加只跑 direct 相依的縮圈選項。
- gov --stats 出現 red 且原因是外部資源 → 加單支白名單跳過。
