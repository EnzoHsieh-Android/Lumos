severity: major

# spec對照-sonnet:r2 tests patch 對照計劃(spec-conformance 鏡頭)

做法:clone 到自己的臨時目錄(`/private/tmp/claude-501/seat-spec/w`),先跑 `-k m1` 基線 256 條全綠;再各自把修法改回去(或改壞)跑對應測試,共 16 種改法,結果見末節。

## F1 兜底(state error)只有直接呼叫 _drift_m1_guarded 才被測到,cmd_drift_check 那條接線沒有任何測試釘住
severity: major
blocking: 是
引句:「            rc_ = m._drift_m1_guarded(Path(root), mode, base, tip, vault_rel)」
file: `scripts/lumos:28545`
file: `scripts/lumos:29387`
1. r1 正確性-F1 的核心症狀是「例外一路丟到最外層,warn 也整支回 1」。修法有兩半:(a) `_drift_m1_guarded` 自己會兜底;(b) `cmd_drift_check` 改成呼叫它。測試 `t_drift_m1_review_r1_non_utf8_and_guard` ② 是把 `_drift_old_sentence_check` 換成丟例外的替身,然後直接呼叫 `m._drift_m1_guarded`,只釘到 (a)。
2. 重現:在 clone 裡把 `cmd_drift_check` 結尾 `return max(rc_core, _drift_m1_guarded(root, os_mode, base, tip, vault_rel))` 改成 `return max(rc_core, _drift_m1_report(root, os_mode, base, tip, vault_rel, _drift_old_sentence_check(root, base, tip, vault_rel, time.monotonic() + _DRIFT_M1_BUDGET_SEC)))`(即原本沒兜底的形狀),清 `__pycache__` 後 `python3 scripts/test_lumos.py -k drift_m1`:輸出 `207 passed, 0 failed`。
3. 也就是「只修了報上來的那個輸入」:兜底函式本身有測,但真實推送走的入口(`drift check`)遇到例外會不會回 0,沒有一條測試從入口端走過。要釘住得在 `cmd_drift_check` 層(或 `_run` 的 `drift check --range`)裝同一個丟例外替身、斷言 warn 回 0、block 回 1。
4. 計劃條款對得上:〈做法〉狀態節寫「warn 回 0、block 照判不了擋」,[S6] 涉及;但該條款目前沒有入口層的綁定測試。

## F2 計劃自相矛盾:治理帳欄位那段仍寫「state(五種之一)」,狀態節寫「六種」,且 error 專屬欄位沒寫進欄位清單
severity: minor
blocking: 否
引句:「check("②判定丟例外:warn 印判不了、rc 0、帳 state error」
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:106`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:140`
file: `scripts/lumos:29377`
1. 計劃第 106 行「狀態只有六種(代碼審 r1 加 `error`…)」,第 140 行帳欄位清單仍寫「`state`(五種之一)」。同一份計劃內部不一致(r1 折入時只改了一處)。
2. 程式在 `error` 狀態多寫一個帳欄位 `error`(`extra["error"] = _drift_m1_show(res["error"], 200)`),欄位清單沒有它;清單也只寫「timeout、git-failed、unreadable 時 handle/listed 是 null」,程式實際是 `judged = st not in _DRIFT_M1_UNKNOWN`,`error` 也是 null。REVISIT 用帳算「判不了比例」時會讀到這欄,計劃該寫。
3. 計劃是誰的錯:計劃(文字),程式與測試是對的;不影響行為。

## 其他觀察(不成 finding)
- `t_drift_m1_review_r1_shared_parsers` ① 是原始碼字串檢查(找 `_nodehome_name_status(`、不含 `split(b"\0")`),② 才是行為;把解析改回手刻但在註解留住字串,① 會綠。② 的行為對兩種實作都綠,所以這條測試釘不住「別另手刻」。屬風格層級,未實測,不標等級。
- 掃描預算測試(`scan_budget`)用的 3 萬個名稱全是 ASCII;沒有 ASCII 段的名稱走 `idx[1]` 線性掃描(`[n for n in idx[1] if n in ln]`),我量 3 萬個純中文名稱每行約 0.6 ms,受每行時間檢查保護,只會落成 timeout、不會掛住,所以不標。
- 「error 狀態、block 時帳記 blocked 帶 hard」有被 `hard` 那條既有測試間接釘住(見下表 block_not_hard 紅)。

## 逐項:計劃這輪新改的行為有沒有測試碰到,以及改回去會不會紅
| 改法(改 clone 裡的 scripts/lumos) | 測試 | 結果 |
|---|---|---|
| 沒副檔名檔只看終點版分類(修回 r1 前) | shebang_either_side | 紅 3 條(有前置斷言 code_files==3) |
| `_drift_m1_guarded` 的 `except Exception` 拿掉 | non_utf8_and_guard | 紅(EXCEPTION boom-x) |
| `_DRIFT_M1_UNKNOWN` 去掉 error | non_utf8_and_guard | 紅 2 條 |
| 名稱正規化不擋頭尾空白 | name_canon | 紅 4 條 |
| 名稱正規化不擋 Cf(方向覆寫)與 Cs | name_canon | 紅 2 條 |
| 沒起點記 skipped 不記 range-unavailable | ledger_kinds_and_umask | 紅 |
| gov 去重鍵不帶 check | ledger_kinds_and_umask | 紅 |
| `group_ok` 拿掉(既有 0775 ~/.cache) | ledger_kinds_and_umask | 紅(umask 002 那條在新建層 0700 下本來就過,只有 0775 條紅) |
| 單行上限拿掉 | scan_budget | 紅 1 條(計數斷言;時間斷言沒紅,因為逐行只拿可能命中的名稱) |
| 每 200 行才看時間 | whole_word ④ | 紅 |
| 帳的 head_sha 不傳終點 | events_and_budget ⑨ | 紅 |
| block 的帳不帶 hard | events_and_budget ① | 紅 |
| old_sentence 預設改 block | layers_and_mode ⑦ | 紅 |
| gate 預設(`_DRIFT_DEFAULT_GATE`)改 warn | layers_and_mode ⑦ | 紅 3 條 |
| doctor 那行不講 old_sentence 值 | spec_gaps ⑧ | 紅 |
| cmd_drift_check 不走 _drift_m1_guarded | 全部 `-k drift_m1` | **全綠(F1)** |

前置斷言:新加測試幾乎每組都有(①前置、⑧前置、⑨前置);shebang、canon、scan_budget、umask 各組的前置都在,沒看到缺前置而空綠的。

## 計劃條款與程式一致性
- error 狀態、單行上限 2 萬、兩邊判 Python、名稱正規化共用、range-unavailable、gov 去重含 check、兩個開關預設(gate block、old_sentence warn)、doctor 只在 gate 寫 warn/off 或設定寫壞時才多講 old_sentence:計劃文字與程式行為逐條對得上(除 F2)。
- 圖譜鏡頭固定席不在本席派工範圍。

最高等級:major
