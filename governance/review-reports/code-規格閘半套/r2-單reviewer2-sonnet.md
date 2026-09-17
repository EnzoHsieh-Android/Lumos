severity: major

**F1. 複合觸發判準只堵了「在」介詞這一種觸發,沒堵到「第二個觸發詞後沒逗號」的真複合觸發,會放行。**
`_CLAUSE_SEP_RE.search(rest)` 要求 rest 自己也要有逗號才判複合;但真實的複合觸發(如「當甲成立,若乙為真應回應」)第二個觸發詞後面常常直接接應句沒有逗號,實測 `_clause_grammar` 對這句回 `(True, 'trigger', '')`,放行成單條款,判準比原本(補丁前)還鬆,是「補丁堵了觸發沒堵範圍」的典型例子,而且 `_clause_check` 是規格閘與處置閘第五步共用的同一支,兩邊都會漏。
引句:「and _CLAUSE_SEP_RE.search(rest)):」
severity: major
blocking: 是

**F2. Setext 偵測用「下一個看得見的行」而非「實際下一行」,fence 之間會錯配,讓無關內容被算成回退節內容。**
實測 `text = "回退\n```python\nfoo = 1\n```\n---\n下一段文字這裡完全跟回退無關\n"`,`_rollback_section_chars` 回 14(found=True),因為 `_visible_lines` 跳過了整段 fence,`nxt` 抓到 fence 之後不相干的 `---`,把純文字裡出現的「回退」二字誤判成 Setext 標題起點;只要後面那段無關文字 ≥20 字,`_rollback_check_lines` 就會判「有回退節、內容夠」,讓沒有真正回退說明的計劃通過閘。
引句:「title = ln.strip() if ln.startswith("#") else "## " + ln.strip()   # Setext(回退\n---)當二級標題(代碼審 r1)」
severity: major
blocking: 是

**F3. Setext 沒分 H1(`===`)與 H2(`---`),一律當成「## 回退」接受,跟 ATX 版本行為不對等。**
實測 `"回退\n===\n…27字…\n"` 回 27(found=True,視同滿足),但語意對等的 ATX 版 `"# 回退\n…"` 回 None(正確被拒,因為 `title.startswith("# ")` 會關掉 inside)。Setext 對 H1/H2 不分,讓比設計寬鬆的層級也算數,且 `governance/review-reports/code-規格閘半套/r2-delta-snapshot.patch:32` 的同一次改動聲稱「Setext 不認」,實際碼是認的兩種都認。
引句:「setext = bool(re.fullmatch(r"[-=]{3,}\s*", nxt)) and not ln.startswith("#") and ln.strip() != ""」
severity: major
blocking: 是

**F4. 圖譜 KEY 行寫「Setext 不認」,跟同一個 patch 加入的程式碼與測試直接矛盾,會誤導下一個讀圖譜的人。**
`Systems/規格閘.md` 新增的 KEY 行明寫「回退節只認 ATX 二級標題(設計寫死,Setext 不認)」,但同一份 patch 的 `_rollback_section_chars` 明確新增了 Setext 支援,連測試 `t_spec_gate_code_review_r1_folds` 的第④步都在驗「Setext 寫法的回退標題也認」且要求 rc==0;下一個 session 查圖譜只會讀到假的結論。
引句:「回退節只認 ATX 二級標題(設計寫死,Setext 不認)」
severity: major
blocking: 是

**F5. `_lens_contract_rows` 沒收斂進 `_contract_key_matches`,跟這輪聲稱的「合約行掃描第三套收斂成一支」不符,是過度宣稱而非功能壞掉。**
file: `scripts/lumos:24766`(`_lens_contract_rows`)仍自己重複一份 `INVARIANT_RE.match(s)/CHECKPOINT_RE.match(s)/IRREVERSIBLE_RE.match(s)` 判斷,沒有呼叫 `_contract_key_matches`;輸出結果目前跟收斂前一致(功能沒壞),但 docstring「★全檔唯一的『合約行』掃描★」與 r1 折入紀錄的「收斂成一支」都不是事實,之後有人照著這句話去改共用邏輯會漏改這裡。
引句:「派工鏡頭(_lens_contract_lines)與規格閘的相依回歸(_contract_texts)都走這裡(代碼審 r1 架構席:別再各寫一份)。」
severity: minor
blocking: 否

**F6. `lands_in` 用專案自己的 `[[連結]]` 慣例寫成字串時,`_plan_system_links` 會靜默濾掉,跟這次修的目的相反。**
實測 `note.fields = {"lands_in": "[[Systems/Alpha]]"}` 時 `_plan_system_links` 回 `[]`——因為 `lands_in` 這條沒有像 `related` 那樣做 `re.sub(r"^\[\[|\]\]$", ...)` 去括號,`lk.startswith("Systems/")` 對 `"[[Systems/Alpha]]"` 判否。這個不對稱在 list 形式時就已存在,但這次補丁把它擴大到字串路徑,而字串正是 CLAUDE.md 自己規定的連結寫法(`[[連結]]`),很可能真的被用到,會讓相依回歸悄悄漏掉該節點。
引句:「字串/清單都收(代碼審 r1:別處都過 as_list,這裡漏了會靜默丟掉)」
severity: major
blocking: 是

---

已讀無 finding:X1(env.find/_node_not_found 的呼叫端 rc 處理,`_spec_gate_load` 回 `(None, "", None)` 時 `cmd_spec_gate` 用 `if text:` 擋掉二次印,只有 `_node_not_found` 自己印過一次,沒有重複印空字串);X2 中 S1/S2(「在」介詞開頭、rest 沒有逗號)的判準修正本身跟測試① ②一致;X6/X7(拿掉 noqa E731、拿掉 door 參數)確認全 repo 無其他呼叫端還在傳 `door=`,不會炸。

LUMOS-IMPACT(260f64b1..HEAD)逐節點判:
- design-loop★INVARIANT★:不影響它測過的那句(「處置閘第五步與規格閘共用同一支 `_clause_check`」這件事本身沒變),但 F1 那個複合觸發漏洞是兩邊共用的同一支函式,所以處置閘第五步也一併吃到這個判準漏洞,不是只有規格閘的問題。
- guard-kill★INVARIANT★:不影響——這次 delta 沒有碰 guard kill 的 rc 邏輯或 `--json` 輸出路徑。
- lumos-cli-lifecycle★INVARIANT★:不影響——沒有碰 re-inject/sentinel 相關程式碼。
- lumos-cli-read★INVARIANT★:不影響——`env.find` 是既有 resolver,`lumos search` 的 superseded/stale 排除邏輯在別的函式,未被這次 delta 觸及。
- 授權與歸屬★INVARIANT★:不影響——這次沒改 `scripts/lumos` 檔頭或 `_VENDORED_TOOLKIT` 白名單。
- pitfalls-code-loop / loop-convergence-recording★RISK★:不影響——改動集中在 `_clause_grammar`/`_rollback_section_chars`/`_plan_system_links`/`_contract_texts`/`_spec_gate_load`/`_contract_key_matches`,不在 pitfalls 或 convergence recording 的函式範圍內。
- 其餘「超出上限只列名」節點(check-t-sentinel、reversibility-governance-ledger、每支檔有家、check-r-guard、doctor-irreversible-hint、anchor-integrity、cochange-guard、lumos-refcheck、bound-tests-gate、canary-audit、slim-*、測試假綠形態、core-invariant-baseline、judge-severity-gate):⚠ 未逐條展開判——派工詞只列名沒附 KEY 內容給我核對,但這次 delta 的六個 hunk 全部落在規格閘/處置閘條款判定與派工鏡頭合約掃描這條窄路徑上,和上述節點各自的合約主題(帳本、簽名守衛、快取、refcheck 等)沒有函式交集,判「不影響」但信心較低。

---
最嚴重 severity: major;blocking 是的有 5 條(F1、F2、F3、F4、F6);blocking 否的有 1 條(F5)。
