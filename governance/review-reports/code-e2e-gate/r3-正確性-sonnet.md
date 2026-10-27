severity: major

整體判定的主幹(出口、放行、整套、按功能的銜接,兩端指紋與設定比較,時間先後比較)我走過一遍,找不到判錯的輸入。`python3.14 scripts/test_lumos.py -k android_e2e_gate` 為 100 passed。下面 6 條有 2 條是測試抓不住的改壞,1 條是 `waive --list`、`waive --ack` 對沒讀到的紀錄講錯話,另外 3 條是 minor。重現腳本都在 `/private/tmp/lumos-seat-work/code-e2e-gate/正確性-sonnet/`(s2、s3、s4、s5、s6、perf、s1,各附 b 或 mut 版對照)。

1. `waive --list` 與 `waive --ack` 把超過 500 份沒讀到的紀錄當成不存在,而且講錯話
severity: major
blocking: 是
file: `scripts/lumos:41856`(`_e2e_ack_targets`)、`scripts/lumos:41835`(`_e2e_waive_list`)
引句:「pend = dict(_e2e_ai_pending_all(root, budget=60)[0])   # 人明著要標:時間給寬」
- 失敗場景:`.lumos/e2e-records/` 有 501 份,最舊的一份帶一筆還沒人看過的 AI 放行。
  - 開場掛鉤印「另有 1 份沒讀…看:lumos android-e2e waive --list」。
  - 照做 `--list` 卻印「沒有任何放行。」,因為 `_e2e_record_files(root)[0]` 把沒取的份數丟掉了。
  - `--ack <最舊的指紋>` 回 rc 0 並說「沒有還沒人看過的 AI 放行。」,但其實有。
  - `--ack --all` 只標前 500 份,印「標好了 500 份」,沒提第 501 份。
  - 標過的檔 mtime 變新,第 501 份永遠擠不進前 500 份,所以這筆永遠標不掉。
- 合約:S41 寫明 `waive --ack` 要把沒讀到的份數講出來;S14 要三處列同一批。
- 重現:`python3.14 s2.py` 輸出「ack oldest explicit: 0 沒有還沒人看過的 AI 放行。」、「left unacked: 1」;`python3.14 s5.py` 輸出「list shows oldest waiver: False | 沒有任何放行。」。
- 歸因:有證據的原有漏查。修前版本(`ce46398a`,用 `before/scripts/test_lumos.py` 載入)跑 `s2b.py`,輸出相同。修補新增了 S41 條款,但 `--ack` 與 `--list` 沒有實作;`t_android_e2e_record_scan` 沒測這兩條路。

2. 測試抓不住:時間先後比較改成字串比對,測試照綠
severity: major
blocking: 是
file: `scripts/lumos:41530`(同樣影響 `scripts/lumos:41667` 的 `newer`)
引句:「elif rt is not None and rt >= _e2e_ts(v["ended"]):」
- 改壞:把 `_e2e_ts`(`scripts/lumos:41355`)的 `return t if ...` 改成 `return x if t.tzinfo is not None else None`,比較就退化成 ISO 字串字典序。
- 測試:`-k android_e2e_gate_newest`(5 passed)、`-k android_e2e_gate_by_feature`(15 passed)、`-k android_e2e_gate_bad_record`(11 passed)全綠,因為所有測試的時差都是 `+08:00`。
- 失敗輸入:整套 pass、`ended=2026-10-26T10:00:00+08:00`;按功能 fail、`ended=2026-10-26T05:00:00+00:00`(實際較晚)。
  - 原版:blocked「之後按功能跑 login.ok 沒過」。
  - 改壞版:pass「整套跑過且通過」。
- 重現:`python3.14 s3.py real` 與 `python3.14 s3.py mut`。
- 歸因:未判定。實作本身正確,缺的是跨時差的測試。兩版都沒有這種測試;這是 `_e2e_ts` 一開始就有的缺口,不是修補造成的。

3. 測試抓不住:被推送提交刪掉或改名的 flow 不算缺,拿掉這個豁免測試照綠
severity: major
blocking: 是
file: `scripts/lumos:41447`(`_e2e_runs_missing`)
引句:「miss = [f"flow {f}" for f in flows if f in have and f not in ran_flows]」
- 改壞:拿掉 `f in have`,畫面那行的 `... in have` 也一併拿掉。跑 `-k android_e2e_gate`,100 passed。
- 失敗輸入:分支把 `.maestro/other.yaml` 改名成 `other2.yaml`,設定跟著改,整套跑過涵蓋 login 與 other2。
  - 原版:pass。
  - 改壞版:blocked「整套結果沒涵蓋主線版要求的:flow .maestro/other.yaml」。這個擋下重跑也解不開。
- 同一條路還有一個設計上的洞:同時刪掉 flow 檔與設定項目,覆蓋檢查不會抓到。這是設計選擇,沒有對應測試。
- 重現:`python3.14 s4.py real` 輸出 `rename: 0 pass`,`python3.14 s4.py mut` 輸出 `rename: 1 blocked`。
- 歸因:未判定。`_e2e_present` 與這段都不在修補差異裡,屬原有缺口。S9 的測試刻意讓 flow 檔還在,從沒測過檔被刪或改名。

4. 主線在分岔後才開了記憶體檢查,擋下訊息叫人重跑整套,但重跑永遠解不開
severity: minor
blocking: 否
file: `scripts/lumos:41663`
引句:「miss = _e2e_runs_missing(root, sha, runs, ml[1], ml[0], sel_full, deadline)」
- 失敗場景:分支在主線開 `stability` 之前分出去,之後改了一支對不到功能的檔(需要整套)。
  - 分支自己的設定沒有記憶體,所以整套跑出來的紀錄不會有記憶體 check。
  - 訊息印「整套結果沒涵蓋主線版要求的:記憶體 exits…」,指令是 `android-e2e-run.sh # 整套跑`。照做後仍是同一個結果。
  - 只有 waive、`LUMOS_SKIP_ANDROID_E2E=1`,或合進主線(指紋會變)能解,訊息沒提合主線。
- 重現:`python3.14 s1.py`(輸出的接下來那段)。
- 歸因:有證據的原有漏查。修前版本跑 `s1b.py`,第 2 步結果相同。

5. S42 說 `--changed` 也在幾秒算完,但這條路逐檔重建索引
severity: minor
blocking: 否
file: `scripts/lumos:41003`
引句:「owners = _e2e_owners(f, feats)」
- 失敗場景:`_e2e_changed_features` 沒傳 `index`,每支檔都重建一次 `_e2e_owner_index`。
- 實量(`perf.py`):400 功能 × 30 路徑、300 支檔,修前 0.53 秒、修後 0.98 秒;每支檔約 3.3 ms,10 萬支檔約 330 秒。
- 測試 `t_android_e2e_owner_index` 只呼叫有預建索引的版本,抓不到這條路。
- 歸因:有證據的原有漏查(呼叫端兩版都沒傳 index)。每次呼叫的成本在修補後約變 1.8 倍。

6. 時間欄位讀不懂的紀錄:擋下訊息說「放行與重跑都不會覆蓋它」,實際上 `waive` 寫得進去,但判定照擋
severity: minor
blocking: 否
file: `scripts/lumos:40934`(`_e2e_record_update`)對照 `scripts/lumos:41647`
引句:「rerr = _e2e_record_err(rec, fp) or _e2e_gate_times_err(rec)」
- 失敗場景:提交裡的紀錄 `runs.ended="garbage"`。
  - 判定擋下,訊息叫人修好或刪掉,不印放行指令。
  - 手動 `waive` 回 rc 0、印「放行記在…」;提交後判定仍是「查證紀錄讀不懂」,多出一筆永遠待看的 AI 放行。
  - 原因:寫入端只驗 `_e2e_record_err`,讀取端另外驗 `_e2e_gate_times_err`。
- 重現:`python3.14 s6.py`(「waive rc 0」之後 `2 1 blocked 查證紀錄讀不懂`)。
- 歸因:有證據的原有漏查。「放行與重跑都不會覆蓋它」這句話是修補新增的,對這一類不成立。

## 三問

① 原問題的修復效果有何行為證據?
- 遞迴爆掉的紀錄、500 份上限與總時間上限、`ci` 出口記帳、`app_dirs` 一項包住另一項、舊分支兩端都沒有 e2e 段、拿掉 e2e 段不叫人合主線、`--commit` 驗證、`LUMOS_TTY_TIMEOUT` 上界:這些我都在 100 個測試通過的基礎上,用 `s1`、`s4`、`s6` 與讀碼走過,行為與修補意圖一致。
- 唯一沒做完的是第 1 條:`--ack` 與 `--list` 沒有「沒讀到的份數」。

② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?
- 正常與錯誤路徑成立。`_e2e_owners` 改成前綴查表,對 `--changed` 與推送前判定兩條路結果等價。
- 相鄰路徑有缺口:`_e2e_changed_features` 沒有受益於索引(第 5 條),`--list` 與 `--ack` 沒有套用新的名額語意(第 1 條)。

③ 新發現的同一案例在修前、修後各是什麼結果?
| 條 | 修前 | 修後 |
|---|---|---|
| 1 | 同樣的假話(`s2b.py` 與修後輸出相同) | 同修前 |
| 4 | `s1b.py` 同樣解不開 | 同修前 |
| 5 | 0.53 秒 / 300 檔 | 0.98 秒 / 300 檔 |
| 6 | 擋下時還印放行指令 | 改叫人修好或刪掉,`waive` 仍寫得進去 |
| 2、3 | 測試缺口,兩版相同 | 同修前 |

## 圖譜與本案鏡頭

- 這次沒附固定席節點,以下是我讀到的相關筆記。
  - `Projects/Android端到端驗收_計劃` 的 S41 被第 1 條破壞,S42 被第 5 條打折。
  - `Systems/android-e2e-acceptance`、`Systems/bound-tests-gate`、`Systems/codex-harness`、`Projects/推送前一次列出全部擋下原因_計劃`:這些筆記說的行為與程式一致,不影響。
- ⚠ 開場掛鉤 `_e2e_ai_line` 的 3 秒是固定值,沒走 `_inner_budget`。它接在 `_discipline_lag` 與 `_enforcement_line` 之後,理論上總和可能超過外層 10 秒。我沒能做出實際超時的情境,所以不列成 finding。
- 計劃條款 S8–S14、S17、S29–S42:除第 1、5 條對應的 S41、S42 外,判定與條款一致。
- 擋下訊息印的指令:缺主線版覆蓋、舊分支、拿掉 e2e 段、紀錄沒提交這幾種,照做都解得開。第 4 條那一種解不開(重跑整套結果相同),第 6 條那一種印的修法有效但「不會覆蓋」的說法不準。

最高等級 major,擋實作的有 3 條(第 1、2、3 條)。
