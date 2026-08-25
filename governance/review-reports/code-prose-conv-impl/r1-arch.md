# 架構對齊審查報告——code-prose-conv-impl (r1-docs.patch / r1-code.patch)

## 1. 跨檔一致性

**Finding 1-A(severity: major,blocking: 是)** 判準:本批的核心裁定之一(d2,見計劃筆記)是訂正「panel/K=2 留給 code-loop」這句舊說法為錯,但同一份訂正聲稱「九處行文同批訂正」全掃過,實際 `skills/` 全文 grep 仍命中兩處活文件(非歷史快照)未同步,構成跨檔矛盾。

file: `skills/lumos-project-notes/reference.md:693`(第二份重複段落在 `:1273`,兩處逐字相同)
引句:「舊 `--gate --panel` 留給 code-loop」
file: `skills/lumos-project-notes/reference.md:690`(同段上文)
引句:「收斂閘=design-loop `loop status --disposal` / code-loop `--gate --panel`」

反證(patch 已改過、內容互斥):
file: `skills/lumos-code-loop/reference.md:311`
引句:「本 skill 收斂改走處置閘,loop status --disposal」
file: `governance/review-reports/code-prose-conv-impl/r1-docs.patch:224`
引句:「九處行文同批訂正(spec/SKILL/reference/05/INDEX 波及處+Systems KEY+驗證筆記+記憶檔)」

這兩處把「design-loop 用 disposal、code-loop 用 panel」寫成現行事實,正是這批修訂認定為錯誤並訂正掉的舊說法本身,而且不是歷史帳(不在 `docs/lumos-toolchain-knowledge/` 的計劃/決策節點裡,是 `lumos-project-notes` skill 的常駐 reference,下一個讀者/agent 會直接照做),下一次有人查 code-loop 該問哪個閘就會被這兩句帶錯路——正是這次訂正想根除的漂移類型。

**Finding 1-B(severity: minor,blocking: 否)** 其餘我核對過的位置(SKILL.md 描述行/步驟 7-8、reference.md〈D · panel 收斂的兩種帳〉新增路由句、templates.md 判讀規則、commands/05、commands/INDEX、Systems/design-loop.md KEY、新建 Verification 筆記)彼此說法一致,且都正確把「code-loop 自 2026-08-08 亦走處置閘、panel/K=2 僅剩已定錨舊迴圈在用」講清楚——對齊。根目錄文件(README/README.en/AGENTS/ARCHITECTURE/CLAUDE.md)未殘留舊說法——對齊。`docs/lumos-toolchain-knowledge/Projects/design-loop重設計.md` 等歷史決策節點仍寫著舊版「留給 code-loop」,但這些是決策當下的既成歷史紀錄(2026-08-04,早於 08-08 撤銷),不在本次「skills/ 與根目錄文件」的訂正範圍內,不算殘留。

## 2. 子命令慣例

四件套(HELP_WHEN 字典 `scripts/lumos:15336`、`add_parser` 註冊 `scripts/lumos:15744`、`main()` 分派 `scripts/lumos:15925`、測試 `scripts/test_lumos.py:6197`)都比照 `fold-check` 的既有位置緊鄰擺放,rc 語意(恆 0、僅用法錯誤才 rc2)與 `test-layers`(`scripts/lumos:12651` docstring「軟提醒(vault-free,恆 rc 0)」)同款;模糊詞表 `_PROSE_WEAK_WORDS`(`scripts/lumos:13658`)的模組層常數+版本註解寫法,與既有 `_PITFALL_BLACKLIST`/`_PITFALL_QUESTIONS`(`scripts/lumos:10799` 附近)同一慣例——對齊。

**Finding 2-A(severity: minor,blocking: 否)** 判準:同一個新子命令在四個登記點裡的相對順序前後不一致,雖不影響功能但跟既有寫法有落差。
file: `scripts/lumos:15336`(HELP_WHEN:fold-check 排在 prose-lint 之前)
引句:「"fold-check": "一份文件前後寫的數字」」→ 下一行才是 prose-lint
file: `scripts/lumos:15744`(add_parser:prose-lint 卻插隊排在 fold-check 之前)
引句:「sub.add_parser("prose-lint", help="spec 白話健檢」

**Finding 2-B(severity: minor,blocking: 否)** 判準:家規「軟提醒開頭『提醒:』…一眼分輕重」(見 `tool-output-plain-style` 記憶筆記)在既有碼裡有 20+ 處字面遵守,prose-lint 掃到弱詞時的訊息未採同一開頭字樣,雖然仍在第一句內交代了「不擋」,但不是一眼就能分辨輕重。
file: `scripts/lumos:13706`
引句:「掃到 N 處模糊措辭。這不擋任何事」
對照既有寫法(如 `scripts/lumos:3111`):「提醒:這輪要審的東西有」——同類 advisory 訊息慣例是把「提醒:」放最前面;prose-lint 把非阻塞聲明挪到句中,三段式(發生什麼→為何在意→指令獨立一行)三要素都在、指令也確實獨立成行(`scripts/lumos:13712` `print(f"    lumos prose-lint {path}")`),僅開頭視覺分輕重這點跟既有寫法不同,不影響判讀。

## 3. 豁免清單語意

**對齊。** 判準:既有豁免哲學是「凍結的歷史證據不得為了過守衛回改」(`golden/`/`l4-audit/`/`external-reviews/` 皆同一句式),新增的 `governance/review-reports/`+`governance/audits/` 用同一套理由,且比既有幾條寫得更具體——附上機械綁定證據而非只講「精神上不該改」。

file: `scripts/test_lumos.py:298-300`(patch 新增註解)
引句:「回改=打斷留痕驗證,實錘:2026-08-25」

我逐筆查證了這句話:`docs/.canary-log.jsonl` 裡 `node-restore-sop/r1-ext.md` 與 `prose-convergence-v2/r1-s2.md` 兩筆記錄確實各帶 `report_sha256`/`snapshot_sha256`(`--report`/`--snapshot` 旗標本就「存 path+sha256」,見 `scripts/lumos:15475`),回改這兩份文件裡的舊命令數會讓 hash 對不上、觸發 disposal/panel 閘的重驗——豁免理由不是編造的。另外這不是本專案第一次對 `governance/review-reports/` 開豁免:`scripts/test_lumos.py:13914` 的 `t_pitfalls_diff_skips_review_report_artifacts`(2026-08-05)早就用同一句「證物是文字紀錄,不是要合入的碼」豁免過 `pitfalls --diff` 掃描——這次只是把同一條哲學延伸到第二個守衛,不是新發明的例外邏輯。豁免顆粒度(整個目錄,不分檔案)也跟既有三條(golden/l4-audit/external-reviews)一致。

---

## 總結

最嚴重 severity:**major**(1 條,1-A)。blocking 共 **1 條**。其餘 3 條(1-B 為對齊敘述、2-A、2-B、第 3 節)均為 minor 或對齊,非阻塞。

**建議動作**:1-A 應在合入前一併修掉——把 `skills/lumos-project-notes/reference.md:693` 與 `:1273` 的「design-loop 新制(2026-08-04)…舊 `--gate --panel` 留給 code-loop」改成與 `skills/lumos-code-loop/reference.md:311`、`Systems/design-loop.md` KEY 一致的「code-loop 自 2026-08-08 亦走處置閘,panel/K=2 僅供已定錨舊迴圈」,否則這批修訂自己宣稱掃乾淨的漂移面仍留了一個活的破口。