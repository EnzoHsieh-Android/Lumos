severity: major

我讀了完整改動與修補差異,在臨時 clone 跑了新測試與整組 `-k secev`(623 全綠),並對新碼做了 10 種改壞實驗。候選行為多數站得住,只有 F1 一個 major,F2 是文件措辭 minor。

F1 我重判後維持 major,blocking 改成「是」。理由是 S69 明文寫「沒有 outcome=not_applicable 的格子就不應要求蓋」,這是被保護的必要行為,而一個具體改壞(把算數的 risk_accepted 格子也算進來)讓兩支新測試與整組 secev 全綠。照 severity 判準,測試抓不住錯而被保護的是必要行為,就是 major。程式本身目前是對的,補一個反例斷言就能解除。

## F1 測試缺口:入口盤點改成「算數的 risk_accepted 格子也要蓋」,兩支新測試與整組 secev 都照綠
severity: major
blocking: 是
引句:「ctx.na_surfaces = {c["surface"] for c in cells.get("cells") or [] if c["id"] in pend}」

失敗場景:
- 我把 `c["id"] in pend` 改成 `c["state"] in ("not_applicable","risk_accepted")`,也就是入口上有一格算數的 `risk_accepted` 就要求蓋 `not_applicable_sound`。
- 實際跑出的結果:`t_secev_s68` 40 passed、`t_secev_s69` 7 passed。整組 `-k secev` 623 passed、0 failed。
- 這違反 S69「入口盤點沒有 outcome=not_applicable 的格子就不應要求蓋」。使用者會被多要求一項審查。
- 原因:S69 的反例只有四種情形:無任何格子、格子在別的入口、格子未經核可不算數、護欄自己標不適用。沒有「同一入口上有算數的 risk_accepted 格子」這一例。
- 補法:加一個 case,在 S1 放一列核可過的 `risk_accepted` consideration,斷言不出現 `missing:review_record_missing`。

file: `scripts/lumos:11259`(`_secev_stage_judge` 內填 `ctx.na_surfaces`)、`scripts/lumos:10568`(`_secev_na_judgments`)、`scripts/test_lumos.py`(`t_secev_s69_not_applicable_conditional`)

## F2 計劃〈核可鏈〉驗證步驟漏寫兩點,照寫會實作錯
severity: minor
blocking: 否
引句:「撤銷之後的筆用被撤金鑰簽的判 `approval_signer_revoked`）」

失敗場景:
- 計劃第 751 行(〈核可鏈〉逐筆驗證的步驟 3)只寫「撤銷之後的筆」判 revoked,以及「`expires_on` 減 `approved_on` 不超過上限」。
- 程式實際多了兩點。一是 `human_review` 的 `expires_on` 為 null 時略過上限檢查。二是撤銷之前簽的不設期限人審也會被補判 revoked(`scripts/lumos:9678`)。
- 這兩點只寫在 d21 的 trade_offs、S68 與 Systems 節點,〈核可鏈〉本文沒寫。
- 只照本文實作會漏掉回溯撤銷,金鑰外洩後舊的不設期限人審仍然有效。

file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:751`

## 核對結果(無 finding)

**repair:**
- 不設期限的人審,綁定的程式一改就判 `stale:binding_changed`。
- 其他每一種核可型別寫 null 都判 `approval_fields_missing`。
- 不帶 `--expires-on` 時,非 `human_review` 型別在 `payload` 一律 rc2 擋下。
- 撤銷金鑰讓它簽的不設期限人審失效,補判在 `scripts/lumos:9678`。拿掉這道補判,S68 ②' 會翻紅;去掉 `expires_on is None` 條件,「寫日期的照舊有效」那條對照也翻紅。
- 判不適用只認核可過的格子。「入口不符」與「只看護欄自標」兩種改壞,S69 都翻紅。

**preserve:**
- 寫日期的審查紀錄與核可,當天有效、隔天過期照舊。
- 把「核可超過上限」的檢查拿掉(`approval_too_long`),S68 與 S69 都不紅,但 `-k secev` 的 S23 與 S45 會抓到。這不是新測試的缺口。
- 核可鏈的主線前綴比對(`approvals_diverged`)不受影響:`approvers_init` 不在不設期限型別內,補判不會讓主線鏈變成「從沒有效過」。
- cells 計算前移後,cells 的輸出、候選護欄判定與全套 623 案例都沒變。我唯一看到的差異是提醒行順序,考量類提醒會先於護欄提醒出現,屬無害。

**None 與例外:**
- 所有讀 `expires_on` 的地方都已處理 null:`_secev_judge_review` 的三處、`_secapr_entry_dates`、`_secapr_verify` 的逾期判斷、`_secev_chain_reminders`、`_secapr_apply`(只讀金鑰型別)。
- `_secapr_add_check` 只看新加的最後一筆,所以撤銷補判不會擋住新增撤銷或其他筆。

**新舊互讀:**
- 舊版讀到 null 會整塊判不合格(只會多擋、不會漏放)。這點 Systems 節點的 PITFALL 已寫,與程式行為一致。

**冪等:**
- `payload` 是唯讀,重跑結果相同。

## 圖譜鏡頭(固定席節點)
| 節點 | 判定 |
|---|---|
| `Systems/bound-tests-gate` | 不影響。此改動沒動 code-loop check 對綁定測試逐支真跑的邏輯。 |
| `Systems/guard-kill` | 不影響。rc 優先序與 `--json` 純度合約沒動。 |
| `Systems/lumos-cli-read` | 不影響。`search` 的 superseded 濾網沒碰。 |
| `Systems/lumos-cli-lifecycle` | 不影響。re-inject 的 sentinel 行為沒碰。 |
| `Systems/design-loop` | 不影響。處置閘第五步沒碰。 |
| `Systems/測試假綠形態` | 與 F1 同類:改壞而測試照綠。F1 缺的就是這種「反例」斷言。 |
| `Systems/pitfalls-code-loop`、`loop-convergence-recording` | 沒有合約行被破壞。 |

其餘只列名的節點我沒逐篇展開。

我的臨時 clone 與紅燈現場(`gctl-run-*`)都已用字面絕對路徑刪除。

max severity 為 major(F1)。
