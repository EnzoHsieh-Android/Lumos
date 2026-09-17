severity: major

以下逐節讀完,交叉核對計劃筆記、`scripts/lumos`、`scripts/hooks/pre-push`、`scripts/test_lumos.py` 與現有卷證(`governance/review-reports/規格落成可驗收條件/r1-intake.md`)後的 finding。

## Finding 1 — 代碼審逃逸掛勾的「finding_kind=code」判準跟文字描述對不上,round 級 severity 配 any() 型 kind 檢查會誤記

file: `scripts/lumos:6181-6186`
```
_kinds = rec.get("finding_kinds") if isinstance(rec.get("finding_kinds"), dict) else None
_has_code = (_kinds is None) or any(str(v) == "code" for v in _kinds.values())
if loop and str(loop).startswith("code-") and severity in ("major", "blocker") and _has_code:
```
`severity` 是整輪 `canary record` 呼叫時給的單一值(round 級,見 `cmd_canary` 簽名 `scripts/lumos:5741` 及註解「rec["severity"]=severity」),`finding_kinds` 是每條發現各自標的字典(`scripts/lumos:5971-5985`)。`_has_code` 卻是「這輪任一條發現被標成 code」,不是「造成這個 major/blocker 的那條發現是 code 型」。實務上一輪代碼審常同時有多條不同 kind 的發現,只要其中一條(哪怕是 minor 的)被標 code,而輪的整體 severity 恰好是 major/blocker(由另一條 spec 型發現撐起來),就會誤記逃逸,且 --desc 文字仍寫「代碼審記到 major」暗示是程式缺陷。跟第五節表格寫的「該發現的 `finding_kind` 是 `code`」字面不符——那句話讀起來像是要對到具體那條發現,程式做的是輪級 any() 判斷。`t_escape_auto_scope_rules`(`scripts/test_lumos.py:31340`)裡的用例永遠只有單一 finding `f1`,沒有測過混合 kind 的多發現輪,測不出這個落差。
severity: major
blocking: 是(直接污染逃逸帳,而逃逸帳是第六節絕對門檻——整套安全網的判準來源)

## Finding 2 — pre-push 用字串包含比對分派逃逸來源,同一句阻擋訊息會被誤判成兩種來源、其中一種歸因錯誤

file: `scripts/hooks/pre-push:234-238`, `scripts/lumos:26722-26726`
```
if bound_advisory and tier == "high":
    ...
    if bt["status"] in ("red", "unfilterable"):
        return {"blocked": True, "reason": bt["reason"] + "(tier=high,--bound-tests-advisory 不適用)", ...}
```
`bt["reason"]` 本身就以「受波及合約的測試沒過:」開頭(`scripts/lumos:5974` 原文)。這條路徑回傳的整句同時含「受波及合約的測試沒過」與「tier=high」兩個子字串。pre-push 用兩個獨立 `grep -q` 判斷是否記逃逸(第 234、238 行),兩者都會命中——會同時記一筆 `push-gate`(合理)跟一筆 `push-gate:unreviewed`,而後者的 `--desc` 硬寫死「高風險缺審查留痕」,但實際擋下原因是測試沒過、與審查留痕無關。若該計劃剛好有雙向門留痕(`_door_for_loop` 回 `two-way`),`_auto_escape` 不會擋這筆記錄(§五表格②的條件只檢查 `door=="two-way"`,不驗證「真的是缺留痕」),於是這筆誤歸因的紀錄會直接計進第六節「`push-gate:unreviewed` 出現 ≥2 份 → 門判定規則重審」的門檻。`scripts/test_lumos.py` 沒有測到這個雙重命中場景(`t_escape_auto_scope_rules` 的 ④a/④b 是直接呼叫 `loop escape --auto --stage push-gate:unreviewed`,繞過了 pre-push 那段字串判斷邏輯本身)。
severity: major
blocking: 是(污染 RETIRE-IF ③ 的計數,而且這條計數規則本身就是為了防止門判定失控)

## Finding 3 — `pre-spec-gate` 回退錨沒有機械綁定,誰打、何時打、lumos 讀不讀得回都沒寫死

spec 第四節「落地前先打 git tag `pre-spec-gate` 當回退錨」與回退節「落地 S8 前先打這個 tag」。倉庫目前沒有這個 tag(`git tag -l "*pre-spec-gate*"` 空);S8 本來就還沒落地,這點不算違規。但 S1–S21 沒有任一條驗「這個 tag 有沒有被打」,回退節也只說「回滾到 tag」卻沒說 `lumos anchor` 或任何指令會不會自動讀它——純粹是給人看的一句話,沒有 `[test:]` 綁。本篇自己在「誠實界線」段已經點名「四層都有洞、靠量測補」,這條屬於同一類但沒被列進去:S8 真的落地那天,如果沒人記得手動打 tag,回退錨就是猜的,跟 r1 回滾席自己抓過的那類問題(「沒有錨的『原本那一版』會變成猜」)一模一樣,只是這次沒對自己再問一次。
severity: minor
blocking: 否(S8 尚未落地,現在不阻擋;但落地前應該補一條驗證,不然會重蹈 r1 已經點過的同一個坑)

## Finding 4 — fail-open 的「失敗要看得見」本身可能雙重失敗,無兜底

file: `scripts/lumos:7570-7577`
```python
def _escape_auto_failed(env, loop_id, stage, why):
    try:
        _append_governance_log(...)
    except Exception:
        pass
    print(..., file=sys.stderr)
```
第五節聲稱「fail-open 的失敗要看得見:每次自動記失敗,往治理帳寫一筆」,但如果治理帳寫入本身也失敗(例如 vault 唯讀、磁碟滿),就只剩 `stderr`——而 memory 裡「headless 探針配額上限」等記憶已經記過 stderr 在無人看顧環境等於消失。這是雙重失敗才會發生的邊角案例,但既然整篇的立場就是「承認風險要附條件」,這一條沒被寫成一行 REVISIT 或殘餘揭露。
severity: minor
blocking: 否

## Finding 5 — 第六節絕對門檻沒有對應的機械計算指令或測試,誰數、數哪本帳全靠人讀

spec 第六節寫「①任何一份雙向門計劃出現 blocker 級逃逸→立刻退回;②前 30 份雙向門計劃裡 major 以上逃逸 ≥3 份→退回;③push-gate:unreviewed ≥2 份→重審」,但 S1–S21 裡只有 S13(`t_doctor_escape_by_door`)驗「健檢按門與階段分開印出放行數與逃逸數」,是描述性輸出,沒有任何一條測試驗「達到門檻時系統會怎樣」——沒有自動判定、沒有擋什麼、甚至沒有明確定義誰去讀那段輸出並執行退回動作。這跟本專案 RETIRE-IF 的一般慣例(人讀 doctor 輸出、人裁定)一致,不算獨有缺陷,但既然第六節用「絕對門檻」這種聽起來像機械判準的措辭,又是整篇「靠量測補」的核心承重牆,值得在文件裡明寫「這是人讀 doctor 輸出後人工執行,不是自動擋」,避免下一個 session 誤以為有機械閘。
severity: minor
blocking: 否

## 已驗證屬實、無 finding 的項目

- **34/29/5/0/0 數字**:`find docs/lumos-toolchain-knowledge -name "*.md" | xargs grep -lE "^\s*-\s*risk/<類>\s*$"` 逐類機械數過,守衛面 29、不可逆 5、金流 0、對外送出 0,合計 34,跟 538 篇總數對得上。已讀,無 finding。
- **①寫側鎖範圍**:`_auto_escape`(`scripts/lumos:7497-7553`)讀 existing→判(含 `_door_for_loop`、`_plan_file_exists`)→append 整段都在 `with _vault_write_lock(env.vault):` 裡面,沒有一行在鎖外。已讀,無 finding。
- **④ 絕對門檻分母**:`_door_for_loop`(`scripts/lumos:7479-7494`)在沒有 `kind: spec-gate` 留痕時回 `"unknown"`,不會被誤算進「雙向門計劃」分母;S13 沒落地前 `.canary-log.jsonl` 裡本來就沒有 `spec-gate` 這個 kind,門檻現在確實算不出來,跟進度段「S13 沒落地前,規格閘一律當單向門處理」一致。已讀,無 finding。
- **⑥ 舊帳寬鬆口徑列**:`docs/.escape-log.jsonl` 現有 6 筆全是手動記(無 `"auto": true` 欄),ledger 裡完全沒有 `"auto": true` 的紀錄,也就沒有「r1 之前自動記進去、口徑寬鬆」的列存在,不會混進未來按 `door` 分母的計數。已讀,無 finding(但建議設計文件明寫這個排除是「因為現在沒有」而非「機制上保證不會有」,見上面 Finding 5 同類建議)。
- **S17 前提**:`.lumos/config.json` 的 `run_cmd` 已含 `{method}`,能鎖單支測試,S17 描述的前提在本 repo 成立。已讀,無 finding。
- **驗收條款自身文法**:抽查 S1、S6、S8、S12 對照第二節文法,觸發子句/分隔/主體/應/回應的結構都吻合(含 S8/S12 這種非「當/若」開頭或帶「在」型但不含「期間」二字的邊界情況)。已讀,無 finding。

## 兩層分開、進度、要動什麼、實務隱患、誠實界線、回退等節

已讀,無 finding——文字表述與程式現況(逃逸自動記三來源已落地、規格閘本體未落地)一致,「還沒做」清單如實反映 `scripts/lumos` 目前只有逃逸自動記掛勾、沒有 `cmd_spec_gate`。

## 固定席節點逐條判(這份設計會不會破壞該節點宣稱的行為/合約)

- **`Systems/design-loop` ★INVARIANT★(處置閘第五步)**:本案明確要改這條不可變合約行(改成呼叫同一支條款檢查器),但計劃裡已寫明「要綁測試加審計」且靠 `_CLAUSE_GATE_SINCE`/`_SPEC_GATE_SINCE` 做非回溯切分——這正是改不可變合約行該走的程序,現在(S8 未落地)尚未破壞。不影響現況;落地時會依既定程序改寫合約,屬預期。
- **`Systems/bound-tests-gate` ★INVARIANT★**:本案的 S17(run_cmd 需 `{method}`)沿用同一機制、不改變其 rc/懸空/弱證據判準。不影響。
- **`Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject sentinel)**:本案未觸碰 CLAUDE.md 注入邏輯。不影響。
- **`Systems/canary-audit` ★INVARIANT★(record 落盤可讀回、second 純 telemetry)**:逃逸自動記使用同一支 `_jsonl_append_verified`(`scripts/lumos:7547`),落盤自驗語意未變;未觸碰 `second`。不影響。
- **`Systems/guard-kill` ★INVARIANT★**:本案未觸碰 guard kill 的 rc 判定或 JSON 輸出。不影響。
- **`Systems/每支檔有家`**:本次改動的三支檔(`scripts/lumos`、`scripts/hooks/pre-push`、`scripts/test_lumos.py`)在圖譜裡皆已有家(牽連清單已列出),沒有引入孤兒檔。不影響。
- **`Issues/code-loop守衛main-direct盲區`**:本案不涉及 main 直推繞過的場景。不影響。
- **`Systems/anchor-integrity`(pre-push 的家)**:進度段已自陳「`lumos anchor verify` 現在會紅,推前要 `anchor approve`」,遵守既有程序,不是繞過。不影響。

---
最嚴重 severity:major;blocking 計 2 條(Finding 1、Finding 2)。
