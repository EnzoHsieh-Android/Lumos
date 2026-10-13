severity: major

審查範圍:scripts/lumos、scenario_probe.py 與技能、圖譜筆記。我跑了 `t_backend_qo_*` 與 `t_stack_questions_kotlin_spring_triggers`,26 項全綠。`lumos lint` 對計劃與五篇 Systems 筆記都是 0 錯誤,`lumos doctor` 沒有 ✗。計劃的 d1–d9 作廢鏈是自洽的:d2 到 d7、d3 與 d4 到 d6,開發工作流總覽的 d1 指到本計劃 d1。〈待決問題〉一節本身通過新 lint,Q1–Q7 都合文法。

severity: major
blocking: 是
解析器對不合文法的題目行靜默略過,lint 和規格閘都不會報,阻塞題可繞過 S1 與 S2。`1. [Q1] … [阻塞]`、`- Q2 …` 這類行直接被丟掉,`parse_pending_questions` 回 `[]`,`_nl_rule_pending_questions` 因此 `if not qs: return []`。標題寫成 `## 待決問題(2026)` 或 `### 待決問題` 時回 `None`,整節不檢查。
最小重現:python3.14 載入 scripts/lumos,把 `"## 待決問題\n1. [Q1] 真 [類:需求][階段:需求][狀態:待人][阻塞]\n- Q2 真 [類:需求][階段:需求][狀態:待人][阻塞]\n"` 傳給 `parse_pending_questions` 與 `pending_questions_blocking_gate`。結果是 `[]` 與 `[]`,規格閘放行。
引句:「_PQ_LINE_RE = re.compile(r"^\s*[-*]\s+\[Q(\d+)\]\s*(.*)$")」

severity: minor
blocking: 否
節標題會取第一個符合的行,不看 code fence,所以計劃裡先貼一段含 `## 待決問題` 的 fenced 範例時,範例被當成真節,後面真正的節被忽略。重現:輸入 "```\n## 待決問題\n- [Q1] 例 [類:a][階段:需求][狀態:已決]\n```\n## 待決問題\n- [Q2] 真 …[狀態:待人][阻塞]",只解出 Q1,`blocking_gate` 為 `[]`。這個 repo 常寫「寫法說明」型計劃,所以不算純理論。
引句:「start = next((i for i, ln in enumerate(lines) if _PQ_HEAD_RE.match(ln)), None)」

severity: minor
blocking: 否
S3 的「不帶 --stage 輸出逐位元不變」,測試⑤只比同一版程式的兩次輸出(`plain_before` 與 `plain_after` 都在改動後跑),再加「沒有 [Q3]」。它驗不到「跟現行相同」。S1 的「沒有〈待決問題〉的計劃輸出與現行相同」也只驗不含「待決問題」字樣與 rc0。計劃把這兩句列為合約候選,綁定的測試卻只驗到「不新增待決問題輸出」。⚠ 這兩條合約候選尚未蓋章,風險有限。
引句:「check("⑤ 不帶 --stage 時輸出不變(不出現待決問題清單)", plain_before.stdout == plain_after.stdout」

severity: minor
blocking: 否
圖譜內部不一致:計劃 A 塊寫「決策存在且有效、測試名在本篇條款裡」這類檢查「只放規格閘與 lint」,Systems/情境出題 寫「只放 lint(規格閘只看狀態)」。實作是後者,規格閘不查決策。三個月後的接手者讀計劃會以為已決指到不存在決策的題在規格閘也會被擋,實際不會。
引句:「這類要讀圖譜的檢查只放規格閘與 lint」

severity: minor
blocking: 否
reference.md 新寫的刪除線註記引用了不存在的機制:「交付前證據檢查」。計劃 d6 已把交付檢查整塊拆出,現況沒有這個檢查。這句屬未定義詞,接手者會去找一個不存在的檢查。
引句:「規格閘與交付前證據檢查會讀它」

severity: minor
blocking: 否
Verification/2026-10-12_情境出題對照實驗結果 的開頭白話段仍寫「接線與否等使用者裁」,但同篇後段與計劃 d9 已裁定接線。這篇狀態是 `pass`,開頭那句已過時,會誤導只讀白話段的人。
引句:「接線與否等使用者裁」

severity: minor
blocking: 否
命令說明沒跟著改。SKILL.md 已教 `lumos pitfalls <計劃> --stage`,但 `skills/lumos-project-notes/commands/02-動手前算波及.md` 的 pitfalls 列只寫 `<spec.md>` 與 `--diff`;同目錄 05 與 INDEX 的 spec-gate 列沒提「待決問題阻塞回 1」這個新擋因。這幾個檔是「指令全集」,SKILL.md 與它們現在對不上。
引句:「會列出那一階段的)找缺口」
佐證:file: `skills/lumos-project-notes/commands/02-動手前算波及.md:6`;`scripts/lumos:50753` 的子命令一句話表也沒有 --stage。

severity: minor
blocking: 否
Systems/情境出題 的風險面表漏列一個觸發詞:req-duplicate 表上寫「API、送出、下單…建立、寫入」,程式的 `when` 多了「提交」。
引句:「提到 API、送出、下單、兌換、預約、付款、扣、建立、寫入」

固定席逐條判定(每條都以程式為準,筆記是線索):
- codex-harness:不影響。scenario_probe 的改動維持舊行為:expect 非空時 `min()` 照舊,預設 ANSWER_MAX 是 1500,缺 expect 的題仍被擋,只有明寫 `collect_only: true` 才放行。新增段落與程式相符,綁定測試存在。
- lumos-cli-read(★INVARIANT★ search 預設排除 superseded):不影響。search 與 `--include-superseded` 的路徑都沒碰,改的是 lint、spec-gate、pitfalls、題庫。
- bound-tests-gate(★INVARIANT★):不影響。`code-loop check` 與綁定測試真跑沒被動,S1–S4 的四支測試都存在於 test_lumos.py。
- design-loop(★INVARIANT★ 處置閘第五步):不影響。處置閘判定沒改,新增的 `_spec_gate_front` 擋法在前段、只對有〈待決問題〉的計劃生效。design-loop 技能新增那行與實作一致:風險高低都擋、需求或架構階段。
- guard-kill:不影響,未碰。
- lumos-cli-lifecycle(re-inject 的 sentinel):不影響,未碰。
- 授權與歸屬(★INVARIANT★ SPDX/MIT):不影響。scripts/lumos 檔頭未動;新增檔 qo_ablation.py 在 governance/eval,不在 `_vendor_toolchain` 範圍,scripts/ 內沒有新增檔。
- 測試假綠形態(★INVARIANT★ 翻紅釘要有前置斷言):大致符合。S4 測試有 `kt-coroutines in big` 當前置;S1 的⑥與 S3 的⑤前置斷言偏弱,見上面第三條。

總結:最嚴重 major;blocking 共 1 條
