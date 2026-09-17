severity: major
# 外部審稿意見 — 規格落成可驗收條件_計劃 r3

severity: major

## 逐節閱讀與交叉引用

已讀全篇(frontmatter/decisions/為什麼/兩層要分開/設計一~六/進度/要動什麼/實務隱患/驗收條款/回退/誠實界線/審計修正紀錄)。r1、r2 卷證(`governance/review-reports/規格落成可驗收條件/`)交叉讀過,folding 記錄(A1–A15、B1–B30)與本篇 decisions/正文逐一核對,未發現「席位說折了但正文沒改」的落差。

## 帳面數字查證(現況 vs 凍結稿)

- 風險標籤:`grep -rl -- "- risk/守衛面" docs/lumos-toolchain-knowledge` → 29;不可逆 5;金流 0;對外送出 0;總篇數 538。與凍結稿「538 篇裡 34 篇掛了——守衛面 29、不可逆 5、金流 0、對外送出 0」逐字一致。已讀,無 finding。
- `_classify_one`(scripts/lumos:8924)docstring 明寫「單條 ★INVARIANT★ 的綁定狀態」,`_clause_bindings_for`(scripts/lumos:4698)才是給 `[SN]` 用——與 d(第三節)「初版寫 `_classify_one` 是錯的」的自我訂正相符。已讀,無 finding。
- `_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE`(scripts/lumos:4599/15805)、`IRREVERSIBLE_RE`/`CHECKPOINT_RE`(scripts/lumos:3859-3860)、`_vault_write_lock`(scripts/lumos:11391)、`.lumos/config.json` 的 `run_cmd` 帶 `{method}`——都存在且與正文描述一致。已讀,無 finding。
- S9/S10/S11/S18/S19/S20/S22 對應的七支測試(`t_escape_auto_*`)確實存在,`python3 scripts/test_lumos.py -k escape_auto` 實跑 28 passed / 0 failed,與「現在 7 條有真測試」相符。已讀,無 finding。
- `_round_valid_m2`(scripts/lumos:6356)現況對未知 kind 一律判整輪無效,若把 `spec-gate` 硬塞進 `("caught","missed","none")` 而不特殊處理,會讓帶 spec-gate 記錄的輪次被判無效或被算進分子——本篇 S28/第四節末段的描述(「不計入分子、也不讓那一輪判無效」)與這支函式現況的風險描述相符,不是無的放矢。已讀,無 finding。

## Findings

1. **引句:「看測試工具說「跑了幾支」,恰好跑到 1 支且失敗才算紅」**
severity: major
   blocking: 是
   spec 第四節(「紅」的判準)聲稱借用 bound-tests-gate 的做法能鎖「恰好 1 支」,但 bound-tests-gate 自己的 `_ran_evidence_check`(scripts/lumos:25718)docstring 明寫「★它證的是『有東西跑過』,不是『跑的是你要的那一支』★」,python profile 的正則是 `r"[1-9]\d*\s+passed"`(scripts/lumos:25707),只判斷「有沒有出現 1 以上的數字+passed」,不解析實際支數,無法區分「1 支」跟「2 支」。本 repo 的 `run_cmd`(`python3 scripts/test_lumos.py -k {method}`)用子字串比對(scripts/lumos:29331 `if _args.keyword in t.__name__`),而現有 967 支測試名裡已存在 158 組子字串碰撞(如 `t_anchor` 是 `t_anchor_covers_all_auto_running_hooks` 的子字串),`_bound_tests_filter_probe` 的docstring 也自承「逐支精準度靠 `_RAN_EVIDENCE` 那條路,這條備援路上沒有解」(scripts/lumos:25753-25755)。這代表 S17/S27/S6 要求的「恰好跑到 1 支」目前沒有現成機制能兌現,借用的參照本身就明寫做不到——這是一個真殘餘,但沒被列進第四節「殘餘(寫明,不假裝解掉)」段落(那段只寫了「綁一支永遠失敗的樁測試」)。落地前至少要把這個殘餘寫進去,或者把 `_RAN_EVIDENCE` 擴成解析實際計數並比對 `==1`。

2. **引句:「剛寫的樁測試標不了 keeps」**
severity: minor
   blocking: 否
   第三節「keeps 測試必須在 git 歷史裡早於本計劃建立」用 `git log -S` 的首次出現日期擋新樁測試,但沒有擋「作者在寫計劃前先另開一個不相干的提交,預先埋一支之後要拿來標 keeps 的樁測試」——這是刻意遊戲化而非誤用,發生成本高、機率低,且第六節逃逸帳事後量能捕捉,不阻塞落地,但值得在誠實界線裡補一句。

3. **引句:「門判定規則版本 `door_rule`」**
severity: minor
   blocking: 否
   第四節與第六節都要求留痕帶 `door_rule` 版本、「門判定規則改版 → 從零重數 30 份」,但沒定義：這欄位的初始值是什麼、什麼動作算「改版」(程式碼 diff?人工宣告?)、誰負責 bump。零份雙向門上線前這不影響落地,但實作時若不先定義,第一批留痕可能全部缺這欄或塞錯值,回填成本比三個「拍的」門檻更高(門檻是全域常數,`door_rule` 是逐筆欄位,寫錯了要逐筆回填)。

4. **對 persona 問題①(d11 新理由是否只是換個說法)**
severity: minor
   blocking: 否
   **引句:「句式是格式不是提醒——不擋就沒有機械可辨識的條款」**
   判:站得住。舊理由(d3)是行為統計論證(「沒人照做」),新理由(d11)是機制必要性論證(下游綁定/跑紅/留痕都要「這行是條款」可被機器辨識)——兩者邏輯獨立,舊理由的數字被推翻不影響新理由成立,不是同一結論換句話說。

5. **對 persona 問題②(keeps 三層防線有沒有一層就夠)**
severity: minor
   blocking: 否
   **引句:「★全標 keeps 的後門(r2 正確性/邊界席 blocker)★」**
   判:三層各防不同攻擊面,不是同層防線的重複——「每條紅」防的是無新行為驗證就放行;「至少一條未標 keeps」防「每條紅」對空集合 `all()` 恆真被繞過;「keeps 早於計劃建立」防「至少一條未標 keeps」被滿足後,其餘條款仍能把新測試謊報成 keeps。三層是遞進補洞(這正是 r1→r2 folding 記錄裡反覆出現的模式:B1/B3 都是「堵了觸發沒堵範圍」),拿掉任一層都會重開一個已知洞,不建議合併。

6. **對 persona 問題③(27 條款有幾條在驗機制自身)**
severity: minor
(資訊性)
   blocking: 否
   **引句:「規格閘應放行並經 cmd_canary 留一筆 spec-gate 紀錄」**
   判:S1–S28(扣併入的 S14)共 27 條,逐條讀完,全部是在驗規格閘/逃逸帳/處置閘第五步這套機制自己的行為,沒有一條驗「使用者要的產品行為」。這不是缺陷——本案的「產品」就是治理工具本身,沒有外部終端使用者,所以 100% 自指是結構性的,不是審查員該挑的洞。但這代表本篇沒辦法用自己提倡的「spec 94%/code 4%」框架來分辨自己的折入是「文件寫不好」還是「工具真的錯」,因為它沒有下游使用者行為可以拿來對照——第六節的逃逸帳事後量測到頭來是唯一能回答這問題的機制,這點在誠實界線裡已經寫了(「靠量測補的設計,不是靠規則封死的設計」),屬已自陳,不重複扣分。

7. **對 persona 問題④(door_rule 是否過早抽象)**
severity: minor
   blocking: 否
   **引句:「此刻零份雙向門上線,不可能有經驗分布」**
   判:`door_rule` 本身只是留痕多一個欄位,成本低,不像三個門檻數字那樣需要「未來重跑」的機制;真正的過早抽象風險是「改版從零重數」這條規則本身缺乏觸發判準(見 finding 3),不是欄位存在與否的問題。作為單一欄位的抽象,可接受;作為「改版流程」的抽象,還沒想清楚。

8. **對 persona 問題⑤(本篇是否也是散文收斂)**
severity: minor
(資訊性)
   blocking: 否
   **引句:「全折 23 條、放行 0、重現不到 0」**與**「全折 30 條、放行 0、重現不到 0」**
   判:去重後的折入數 r1→r2 從 23 條升到 30 條,不是遞減,字面上確實像「多輪散文收斂」在本案自己身上重演;但差別在於 r2 的 30 條裡多數(B1/B3/B5/B6 等)是「r1 的補丁堵了觸發沒堵範圍」的同族漏洞延伸,不是全新獨立問題類別,且每輪都有機械重現(編排者用 grep/sed 對照)佐證,不是純散文互折——跟本篇自己批評的「模型自我批評到第二輪反而變差、除非有外部工具回饋」的說法相容(這裡的外部回饋是編排者的機械重現)。本篇在第「為什麼」節第 105-106 行已自陳這個張力,屬已自陳,不重複扣分,但建議 r3 定案前明確寫一句「r2 折入數字上升的原因是同族漏洞延伸,不是新問題類別增加」以示不是在迴避這個矛盾。

## 固定席節點逐條判(這份設計會不會破壞該節點宣稱的行為/合約)

- **Systems/design-loop ★INVARIANT★**(處置閘第五步合約):會動。本篇第四節已寫出新文字草稿並規劃綁 `t_disposal_clause_gate` + `t_disposal_step5_shares_checker`(S8),屬計劃內、有審計配套的變更,不算破壞。
severity: minor
  blocking: 否
- **Systems/bound-tests-gate ★INVARIANT★**:不修改其程式路徑,只是仿照其「跑了幾支」判準的精神——但見 finding 1,仿照的精神在借用點上比原節點自己承認的能力更強,這是本篇對它的**誤用**而非破壞它的合約本身。
severity: major
  blocking: 是(同 finding 1)
- **Issues/code-loop守衛main-direct盲區**(status: done):本篇 S21/S24 推送閘檢查透過 `_plans_in_range(repo_root, git_range, vault)`(scripts/lumos:7468)接收呼叫端傳入的 range,若沿用既有已修正的 push-range 計算(而非重新用 merge-base 自己算),不會重開此盲區;但正文沒有明寫「range 從哪裡拿」,實作時若圖方便另開一條 merge-base 算法就會重蹈覆轍。建議在第四節「推送前」段落明寫「range 沿用 pre-push 現有的 push-range 計算,不得自算 merge-base」。
severity: minor
  blocking: 否
- **Systems/anchor-integrity ★RISK★**:進度節已明確記錄「`lumos anchor verify` 現在會紅…推之前要 `lumos anchor approve`」,顯示已經走過這道閘,不是破壞它是正常使用它。
severity: minor
  blocking: 否
- **Systems/每支檔有家**:`lands_in` 新開 `Systems/規格閘` 作為 `cmd_spec_gate`/`_clause_check`/`_excluded_line` 的家,符合鐵則五;`scripts/hooks/pre-push` 已有家(不在本案新增責任範圍外)。
severity: minor
  blocking: 否
- **Systems/canary-audit ★INVARIANT★**(record/second 落盤與 second 不影響 rc):本篇留痕明寫「走既有審查帳寫入口 `cmd_canary`」,不繞道另開寫路徑,理論上會自動繼承既有的 readback 驗證與 fail-open 行為;但目前 `spec-gate` 這個 kind 完全未實作(`grep -n "spec-gate" scripts/lumos` 只在讀側一處命中,寫側尚未加),無法實跑驗證繼承是否完整,屬設計期合理假設。
severity: minor
  blocking: 否(留 REVISIT:落地時補一支 `t_canary_record_persist` 對 `kind=spec-gate` 的翻紅釘)
- **Systems/guard-kill ★INVARIANT★**:不同指令、不共用程式路徑,無關聯。
severity: minor
  blocking: 否
- **Systems/lumos-cli-lifecycle ★INVARIANT★**(sentinel 外內容 byte-equal):本篇改 `scripts/templates/graph-discipline.md` 第 60 行再透過 `lumos update` 重新灌注,若 `lumos update` 本身遵守既有 sentinel-only 覆寫邏輯,不會破壞此合約;正文已明寫這一步驟(「模板改了要在本 repo 跑一次 `lumos update`」)。
severity: minor
  blocking: 否

## 實務隱患(四類)

已讀,本篇自己的四行「已排除」在第二輪已被指出過(B1/B2),本輪重驗 `_excluded_line` 目前尚未實作(`grep -n "_excluded_line" scripts/lumos scripts/test_lumos.py` 零命中),屬於設計期正常狀態,不重複扣分。無新 finding。

---

**最嚴重 severity:major(finding 1,以及對應的 Systems/bound-tests-gate 固定席判)。blocking 共 2 條(finding 1、Systems/bound-tests-gate 固定席判——兩者同一個根因)。**
