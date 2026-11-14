severity: major

## k1 守的測試雜湊拿到的是計劃筆記的物件編號,不是測試檔的,補強測試後存活的行不會重跑
severity: major
blocking: 是——計劃、SKILL 與推送閘提示都說「補強既有測試後重跑 choice-kill 會自動重跑」,照做卻不重跑,被保護的是條款必要行為(G3 的修復目標)。

- 輸入:計劃條款 `[test:alphaCase]` 寫在 `docs/…/Projects/*.md`,測試檔放 `src/test/VmTest.kt`。
- 路徑:`cmd_choice_kill` → `_choice_test_blobs` → `_choice_tests_sha`。
- 壞在哪:`_choice_test_blobs` 用 `git grep -l -F -e <測試名> <sha> --` 取「第一支含測試名的檔」。git grep 照路徑排序,`docs/` 排在 `src/`、`test/` 前面。第一個命中的是引用測試名的計劃筆記,不是測試檔。
- 預期:補強測試內容後 `tests_sha` 改變,survived 的行重跑。
- 實際:`tests_sha` 不變,行不重跑。反過來,計劃筆記一被改(例如 situation-rule 寫回條款),所有行的 `tests_sha` 都變,造成無謂重跑,並讓推送前印「另一組守的測試」提醒。

引句:「原地補強測試(名字不變)也會重跑存活的行」

file: `scripts/lumos:77652`(`_choice_test_blobs` 的 `git grep -l -F`)

最小重現(在 `g1` 這個 repo 裡):

```
docs/p/plan.md        含 "[test:alphaCase]"
src/test/VmTest.kt    含 "fun alphaCase"
python3.14 -I probe.py
→ [['alphaCase','df28193e…']]
git rev-parse HEAD:docs/p/plan.md HEAD:src/test/VmTest.kt
→ df28193e…(計劃筆記)  6b881f7e…(測試檔)
```

probe 檔在 `/tmp/lumos-seat-work/code-改動選擇點/合約-sonnet/probe.py`、`probe2.py`。

兩版對照:`probe2.py` 提交一次對 VmTest.kt 的補強,再算 `tests_sha`。

| 版本 | 補強測試檔後 `tests_sha` 是否改變 |
|---|---|
| 修前 7826895c1 | False |
| 修後 4dd1ed800 | False |

歸因:有證據的原有漏查。修前 `tests_sha` 只雜湊名字,本來就不會重跑。修補加了物件編號卻取錯檔,沒有達到宣稱的效果。

綠測試為何沒抓到:`t_choice_kill_rerun_rules` 的夾具測試檔在 `app/src/test/…`。`app/` 排在 `docs/` 前面,所以剛好命中測試檔。只要把測試檔放到排在 `docs/` 之後的路徑,測試就抓不到這個錯。

## k2 部分檔掃不出來時的新結束碼,計劃〈範圍〉1、2 沒寫
severity: minor
blocking: 否——只是文字落後,不會讓操作出錯。

- `choice-points`:有幾支檔掃不出來時,程式回 rc 3。計劃〈範圍〉1 只寫「ast-grep 不在 → rc 3」。
- `choice-kill`:有幾支檔掃不出來時,程式回 rc 2,並印「這支檔這次不跑」。計劃〈範圍〉2 的 rc 規則只寫「有 no_result、不唯一、沒跑完或中斷 → 2」。
- 接手的人照計劃會以為 rc 3 只代表沒裝工具。

引句:「return 2 if (nores or nu or unrun or kr.interrupted or kr.wrote_fail or res.get("unverified")) else (1 if surv else 0)」

file: `scripts/lumos:78130`、`scripts/lumos:77564`(`_choice_points_unverified`)

歸因:有證據的修復造成的文件落後。修前沒有 `unverified` 這條路徑(修前 `_choice_compute` 掃不出來時整批 raise)。

## 三問
1. **原問題的修復效果**(兩版證據)
   - G1(放行抽中的行後重抽):`probe3.py` 兩版跑「20 行曾存活、上限 14、放行抽中的 1 行」。
     - 修前:放行後仍擋 14 行,沒抽中 5 行。
     - 修後:擋 13 行,沒抽中 6 行,提醒印的曾存活數是 20。已修復。
   - C-18 規則改寫為雙重否定:修前與修後兩份 `kotlin-choice` 規則掃同一份語料(repo 樣本加手寫的 if、when、lambda、init、註解案例),命中 173 筆對 173 筆,逐筆相同。等價成立。語料只有 repo 樣本加我手寫的一支檔,真實專案沒驗,未判定。
   - G3 的「補強測試重跑」:k1,未達成。
   - G3 的「no_result 一律重跑」:程式與計劃文字一致。`_choice_kill_pick` 裡 `disp == "survived"` 才帶過去。
   - G2、G4、G5、G7、G8、G9、G11、G12:只跑修後測試子集,全綠。修前沒另外跑,這幾項歸因未判定。
     - 子集:`choice_points_sbr`、`choice_scan_per_file`、`choice_kill_weak_evidence`、`choice_kill_same_name`、`choice_push_cap_waive_stable`、`choice_unique_overlapping`、`choice_ledger_write_semantics`、`gov_stats_choice_dedup`。
2. **修補處的正常、錯誤與相鄰路徑**
   - `cmd_guard_kill` 不傳新參數時行為不變。
     - 兩條 ★INVARIANT★ 的綁定測試修後全綠:`t_guard_kill_rc_precedence` 與 `t_guard_kill_json_purity` 各 4 與 6 案例,另 `t_choice_guard_kill_new_params` 2 案例。
     - `killed_weak` 只是 `_KillHooks.flush` 的區域鍵,只影響 `stop_on`。`on_row` 列的 `verdict` 仍是 `killed`,不外洩到 rc 或 JSON。
     - `_count_overlapping` 把重疊兩次的 old 從「恰好一次」改判 drifted,走合約允許的 rc 2。
   - SKILL.md 與計劃寫「放行檔不在帳本檔清單,通過後提交會讓留痕失效」:屬實。`.lumos/lint-waivers.json` 不在 `_BOOKKEEPING_FILES`(`scripts/lumos:40649`)。
   - doctor 放行計數的新函式 `_lint_waivers_doctor_bits`:順序與修前一致(新增告警、情境段、選擇點),選擇點另列。
   - 計劃 S11 條款與預期值表一(S11 三列)沒有被新行為打破:沒變的 survived 不重跑、補一支綁條款的測試後重跑。新行為(no_result 重跑、內容雜湊)沒有對應列,屬增補缺口,未列為 finding。
3. **新發現的同一案例修前修後**:只有 k1。修前與修後結果相同(補強後 `tests_sha` 不變),所以不是修補回歸,是修補未解決原問題。

## 圖譜鏡頭
這次沒附固定席節點。我自己查了被改到的合約節點 `Systems/guard-kill`:
- 兩條 ★INVARIANT★ 的綁定測試在修後都綠。
- 新增的 PITFALL 與 WHY 行引用的 `[test:…]` 測試名全部存在。
- `lumos lint Systems/guard-kill` 回 0 問題。
- 判定不影響。

臨時目錄 `/tmp/lumos-seat-work/code-改動選擇點/合約-sonnet/` 留給編排者收貨後刪,我沒有刪。

最嚴重:major;blocking 共 1 條
