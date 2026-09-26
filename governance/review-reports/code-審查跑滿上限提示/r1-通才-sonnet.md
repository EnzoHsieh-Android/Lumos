severity: blocker

## F1 處置閘呼叫 `_cap_hint` 沒包 try/except,實測會把整支指令炸掉(loop next 有包,處置閘沒有)
severity: blocker
blocking: yes

設計條款 S2 要求「輪數已達上限,處置閘應在判定之後印同一段,不論過關與否,且過關判定與退出碼不變」——這隱含「印這段不能讓指令壞掉」。`cmd_loop_next` 那邊確實把 `_cap_hint(rounds)` 包了 `try/except Exception`(patch 第 168–172 行);但 `_loop_status_disposal` 的兩個呼叫點(FAIL 分支與 PASS 分支)完全沒有 try/except 保護,直接呼叫 `_cap_hint(rounds, gate=...)`。

引句:「for _ln in _cap_hint_lines(_cap_hint(rounds, gate={"passed": False, "fails": list(fails)})):」

`_cap_hint` 內部呼叫既有的 `_review_yield_round`(這支函式是 patch 明講「機制層沿用」、不改動的既有函式),其中一行是:
```python
R = len(carrier["refuted_set"]) if carrier and carrier.get("refuted_set") is not None else None
```
只要帳上某一輪的彙總帳列(carrier)有 `refuted_set` 這個欄位、值不是 list(例如手改帳或舊版工具寫壞的 int),`len()` 就會丟 `TypeError`。**關鍵是:`_cap_hint` 會對「這個編號的每一輪」都跑一次 `_review_yield_round`,不是只驗判定輪(latest)**;而處置閘自己既有的防禦(findings 欄整數檢查、findings_set/folded_set/accepted_set 的 set 運算、單一 carrier 檢查……)全部只驗 `latest`(判定輪)那一組,從不碰更早輪次的 `refuted_set`。所以:一支在此 patch 之前完全能正常跑完(印出 PASS/FAIL 判定)的帳本,只要「非判定輪」裡混進一筆壞掉的 `refuted_set`,套上這個 patch 之後,`lumos loop status --disposal` 就會在印完判定橫幅後,直接對著使用者噴出未捕捉的 Python traceback,而不是「只印不擋」。

重現步驟(在唯讀 repo 上不能改,已在 `/private/tmp/.../scratchpad/caphint/exp/repo` 這份複製體上驗證):
1. 手寫一支帳本(`.canary-log.jsonl`),`loop=caphintcrash`:
   - r1:一筆彙總帳列(carrier),`findings_set/folded_set` 是正常 list,但額外帶 `"refuted_set": 999`(整數而非 list)——模擬舊版工具或手改帳留下的壞值。
   - r2(判定輪):0 發現的空輪,report/snapshot 都齊全、sha256 對得上。
2. 跑 `lumos loop status caphintcrash --disposal --spec <spec.md> --repo <root>`。
3. **套用此 patch 後**:stdout 正常印出所有 disposal 檢查行、印出 `⛔ DISPOSAL GATE FAIL (... G3)`,但緊接著 stderr 噴出完整 traceback,終點在 `_loop_status_disposal` 第 18688 行(`_cap_hint_lines(_cap_hint(rounds, gate=...))`)呼叫進 `_review_yield_round` 的 `len(carrier["refuted_set"])` 那一行,`TypeError: object of type 'int' has no len()`。
4. **回到 patch 前一個 commit(452e9780)、同一份帳本重跑**:乾淨結束,rc=1,stderr 完全乾淨,沒有 traceback——證實這是這份 patch 新引進的迴歸,不是既有問題的延伸。

我用 in-process 呼叫也單獨證實 `_cap_hint` 本身(不透過完整 disposal 流程)對同樣壞值會直接丟 `TypeError`,不是我在拼湊 disposal 前置檢查時湊出的巧合。

影響:這不是「少印一段提示」而已——PASS 分支的呼叫點在 `_loop_gov_mark(env, loop_id, "converged", "disposal gate PASS")` **之後**才呼叫 `_cap_hint`,代表如果同一種壞值出現在 PASS 情境,治理帳已經寫下「converged」,但整支指令卻以未捕捉例外(非 0、非設計預期的乾淨 rc)收尾——判定內容與退出行為不一致,直接違反 S2「過關判定與退出碼不變」的精神。

建議修法:比照 loop next,在處置閘的兩個呼叫點外包 `try/except Exception`(或在 `_cap_hint`/`_review_yield_round` 內部對 `refuted_set`/`findings_set`/`folded_set`/`accepted_set` 做型別防禦),兩者擇一,但不能維持現狀。

## F2 「熔斷觸發但還沒到上限、且算不出走勢」時,提示行(「判不了,自己看」)被靜默吃掉,沒有任何測試守住
severity: major
blocking: no

設計第三節「二、印什麼」把「4. 提示」列成這段輸出固定要印的五項之一,而且 4 的第一條規則明寫:「有任何一輪『沒記處置』、或只有一輪 → 『判不了,自己看』」,沒有註明這條規則只在到上限時才適用;熔斷本身在第一節就被列為獨立的印出觸發條件(「不論輪數」),第 5 點也強調「熔斷跟第 4 點各自獨立,兩者都成立兩段都印」。

引句:「if h["at_cap"] or h["hint"] != "unknown":」

但 `_cap_hint_lines` 實作是:
```python
if h["at_cap"] or h["hint"] != "unknown":
    lines.append(P + "提示:" + msg)
```
也就是說:只要「還沒到上限」而且「提示規則算出來是 unknown(判不了)」,這一行就整條不印——即使熔斷已經觸發、整段仍然會印出來(閘一行+熔斷一行)。這正好是「只有一輪但累計折入超過 20」這種最典型的熔斷情境(此時輪數必然 < cap,規則第一條「只有一輪」必然成立、hint 必為 "unknown"),而這正是設計裡明講要印「判不了,自己看」的那一種情況——現在完全不印。

我用 mutation 驗證過這是測試沒守住的洞、不是我誤讀規則:把上面這行的判斷條件整個拿掉(一律印),讓 `python3 scripts/test_lumos.py -k cap_hint` 重跑,**32 支測試全部照樣通過(32 passed, 0 failed)**——代表現有測試完全沒有斷言過「只有一輪+熔斷」情境下,`_cap_hint_lines` 的輸出裡到底有沒有那行「提示:判不了,自己看」;`t_cap_hint_breaker_total_folded` 這支測試名稱上寫著要驗這個情境,但實際斷言只檢查 `_cap_hint(...)` 回傳 dict 裡的 `h["hint"] == "unknown"` 欄位,從沒呼叫 `_cap_hint_lines` 去看文字輸出真正印了什麼。

重現步驟:
```python
h = m._cap_hint(_cap_rows([(21, "major", [21])]))   # 只有一輪,累計折入 21(熔斷)
print("\n".join(m._cap_hint_lines(h)))
```
實際輸出只有「還沒到上限…」「r1:折 21 條…」「閘:過了沒要帶 --spec…」「熔斷:各輪累計折入已經 21 條…」四行,沒有「提示:判不了,自己看」那一行,即使 `h["hint"]` 內部確實算成 `"unknown"`。

影響:使用者在熔斷觸發但還沒滿輪次的當下,少了設計原本要給的最保守提醒(「資料不足,自己看」),只看到閘狀態跟折入數字,容易誤判成「數字已經很在意但沒人喊停,那就繼續跑」。

## 已看,無:
- `_disposal_round_groups` 抽出的邏輯逐字比對舊版 `_loop_status_disposal` 內聯程式碼(擋壞行、`__` 前綴、非連續重現三個分支),語意完全一致,只是包成函式回傳 `(groups, err)` 而非直接印+return 2;呼叫端 `if _gerr: print(_gerr, file=sys.stderr); return 2` 正確還原原本行為。
- `loop next` 側 `_ch = _cap_hint(rounds)` 是在 `emit()` 函式本體內計算,JSON 輸出與文字輸出共用同一次計算結果,不會有「JSON 印一種、文字印另一種」的分裂風險;「少了 --spec」「cap-reached」「converged」等所有會呼叫 `emit()` 的分支都會一致地附加這段,符合 S1「只要正常印出結果就附加」與 M1 包既有裁定(少了 --spec 排在跑滿之前)。
- 已用 mutation 驗證測試真的會對修法翻紅:拿掉 `try/except`(直接把 `_ch` 設 `None`)會讓 `t_loop_next_cap_hint_appended_without_changing_phase` 與兩支 `t_loop_next_cap_hint_json_fields` 斷言翻紅;拿掉處置閘 FAIL 分支的 cap-hint 呼叫,`t_disposal_cap_hint_without_changing_verdict` 與 `t_cap_hint_not_declining_reshape`(該次執行順序下連帶翻紅,detail 見上)確實翻紅——S1/S2/S10 這幾條確實有測試守住。
- `--json` 欄位只包 `rounds`/`hint`/`breaker` 三個,不含 `gate_status`/`cap`/`tier`/`at_cap`,跟第三節條款字面一致;S11(帳本行數不變)也跑過 `loop next` 與 `loop status --disposal` 兩次呼叫比對 `.canary-log.jsonl`/`.governance-log.jsonl` 行數,實測沒有變化。
- 空輪判定(S7/S15)、輪次跳號排序(S14)、沒有分級退回 standard(S13)、累計熔斷不論輪數觸發(S8)、可以停必帶閘狀態(S12)——都用 32 支既有測試各自實跑通過,且都做過至少一次針對性的邊界檢查(找不到明顯偏離字面條款的地方)。
