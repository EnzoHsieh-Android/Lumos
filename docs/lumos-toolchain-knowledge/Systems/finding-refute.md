---
type: system
status: done
created: 2026-06-26
updated: 2026-08-29
self_audit: sonnet/2026-08-30
tags:
  - type/system
  - status/done
  - risk/守衛面
verified_by:
  - "[[Verification/2026-06-24_finding-refute]]"
  - "[[Verification/2026-08-27_辯方表態記帳]]"
summary: |-
  FLOW:auditor→findings→judge(caught/missed+severity,排掉canary後最嚴重真finding)→【辯方refute(新,step4.5)】對每條 judge 評 severity≥major 的 finding 各派 1 個獨立 opus 辯方(乾淨脈絡、不傳 auditor/judge 結論)→辯方回真(維持)/假(降級+file:line反證)→該輪 severity=存活 findings 機械取 max(判讀用)→record(★2026-08-26 [S1] 起帳面 severity 忠實記報告宣告最高、不得記辯方後較低值——照舊句記會 rc2;降級走 accepted-set+refute-verdict evidence★)→只折存活真 finding(被駁倒的不折、標「辯方反證:<file:line>」)
  KEY:防的失敗模式=auditor「認真讀了但判錯」的假陽性(誤抓);與 canary 防「沒讀/放水」的假陰性(漏抓)方向相反、對稱補位
  KEY:辯方派工本體=純 prompt 紀律;★2026-08-27 起表態記帳(--refute-verdict)已有 CLI 代碼與單元測(t_refute_verdict_ledger_and_stats),「無代碼」僅指派工本體★;只動 SKILL.md(手動版)+orchestrator-prompt.md(自動版),不碰 canary/judge/cross-family/lumos 原語/record
  KEY:辯方效力來源是「任務方向相反」(被逼構造推翻證據、查 auditor 跳過的反方向),非「更會看 code」;故 1 個辯方+強制 file:line 即可,不 N 個多數決
  KEY:只買 code 層假陽性——脈絡在 code 外(業務現實)或辯方自己也沒挖到那塊 code 時,拿不出反證則維持 finding(無功但無害);業務層留人(誠實天花板)
  KEY:辯方降級也須拿反證 file:line,拿不出則維持;對齊 judge「無查證行鎖 major」底線,空口『沒問題』不算
  DEP:skills/lumos-design-loop/SKILL.md 步驟4.5｜governance/autonomous_loop/orchestrator-prompt.md §2 步驟4.5｜judge-severity-gate(辯方接 judge 後)｜canary(對稱補位)
  TEST:派工本體無單元測(prompt 紀律);表態記帳有(t_refute_verdict_ledger_and_stats,含 blocker 輪讓步翻紅釘);spec 品質以 design-loop 自走驗:3 輪自動收斂、canary 3/3 全中;辯方降級效力(假 major 當輪被駁)本輪未觸發——首個出現假陽性的真實 loop 才可實測
  VERIFY:[[Verification/2026-06-24_finding-refute]]
decisions:
  - content: 辯方階段插在 judge 後、record 前——對 judge 評 severity≥major 的每條 finding 各派 1 個獨立 opus 辯方,預設 finding 假、強制附 file:line 反證才能降,該輪 severity 由編排者機械取存活 findings 的 max
    id: d1
    context: design-loop 全是檢察官(auditor 找洞)、缺辯方;canary 只驗審計員有沒有認真讀(防漏抓),抓不到「認真讀了但判錯」(誤抓)。2026-06-23 qwen 把已處理好的 __SCRATCH__(sed 替換 token)誤判 major,canary 對這型無能為力
    why_chosen: 把原「編排者克制剝誤判」(自填偏誤:利害關係人自評 severity)升級成獨立帶證據裁決,同 judge-severity-gate 精神(severity 交獨立評定者);辯方靠任務方向相反逼出反方向 grep,殺 code 層假陽性
    decided: 2026-06-24
    valid: true
  - content: 只對 severity≥major 派辯方、只派 1 個(非 N 個多數決)、不重派 judge 算 severity
    id: d2
    context: good()=caught 且 severity∈{clean,minor},minor/clean 不影響收斂;要選「1 辯方+file:line」還是「N 辯方投票」
    why_chosen: 強制 file:line=確定性查證(可被下輪 auditor/人複驗),比 N 個 AI 投票更貼「確定性>AI 判斷」主軸且省算力;minor/clean 派辯方是白費算力
    decided: 2026-06-24
    valid: true
  - content: 辯方效力來源是「任務方向相反」、不是「code 證據」本身——故不靠多派 auditor
    id: d3
    context: 質疑「缺脈絡時辯方憑什麼比 auditor 對」;auditor 提 major 時其實也 grep 過(強制查證)
    why_chosen: auditor 找洞(看到可疑就提、無動力深挖反證),辯方被逼構造推翻證據(專查 auditor 跳過的反方向);同樣 grep、目標命題相反→挖的角落不同。多派 auditor 只生更多起訴、同找洞方向
    decided: 2026-06-24
    valid: true
  - content: 辯方裁決升明確三選一(agree/evidence/concern)並記進帳(--refute-verdict);★純記帳、不改降級規則★——只有 evidence 態會降且照舊須 file:line,agree/concern 皆維持,去向仍由 folded/accepted 定
    id: d4
    context: 2026-08-22 [[Projects/收斂機制優化調研2026-08-14]] 裁「辯方三分類先不做」,理由:我們起點已有引句錨定+行號機驗+外家反證三層,論文(F1 0.457→0.533)的增益吃不吃得到估不出來;重啟條件=出現一次辯方被弱反駁說服、事後證明真的。但該裁定〈誠實界線〉自承帳裡無逐席對錯標註→重啟條件根本偵測不到。2026-08-27 治理日報又把同篇論文當新發現端上(未對決策帳),Enzo 裁走中間路
    why_chosen: 只補偵測儀器、不翻舊裁定:降級行為零改動(不碰散文層收斂差的部分),風險最低;開始記 evidence 降級樣本,日後抽驗『降錯、後來證明是真的』才有候選池,把 2026-08-22 那條原本看不見的重啟條件變成可用證據觸發。相對選項:①照做全套三分類(翻案,但增益仍估不出、且改判閘)②完全不動(維持看不見的重啟條件)——都比中間路差
    decided: 2026-08-27
    valid: true
  - content: 辯方表態的記帳一致性檢查在 blocker 輪讓步(2026-08-29 修回歸):同輪 severity=blocker 時,舊規則強制放行清單為空、而反證推翻的發現照規矩不折入——兩條一夾使 refuted 發現無處可去、整筆記帳被擋。處置=讓步的是本欄(它自稱純記帳),blocker 輪允許 evidence 落折入並提醒,反證 file:line 寫進 note;判閘一字未動
    id: d5
    context: 自主迴圈 2026-08-29 那輪四次撞上,只能把辯方判決留空、反證寫進 note,結構帳因此少了四輪的辯方資料(它自己的 notes 點名這條)。追查發現死結比 2026-08-27 的表態欄更早:舊規則『blocker 輪 accepted 必空』與『被駁倒的不折入』本來就互斥,表態欄只是讓它每次都撞、從偶發變必然
    why_chosen: 本欄 2026-08-27 立案時自己寫的定位就是『純記帳、不掛判閘』,那麼衝突時該讓的是本欄不是判閘;讓步範圍最小(只在 blocker 輪、且該 id 確實在折入清單才放行),非 blocker 輪的原檢查一字未動並有測試守住。★根因(blocker 輪該不該讓反證發現放行)是判閘語意問題,要動得走設計審,本次刻意不碰★——這條寫進註解,避免下次有人順手改判閘
    decided: 2026-08-29
    valid: true
aliases:
  - 辯方
---
# finding-refute

design-loop 審計 loop 的**辯方 refute 階段**(step 4.5)—— 檢察官(auditor)/辯方雙向對抗的「辯方」側,防 auditor「認真讀了但判錯」的假陽性(誤抓)。

> 源起:日報 2026-06-23 inspiration「借 REFLECT『評審最弱在核對證據』:能用死板比對(grep/diff)的就別交給 AI 判,只把 grep 查不到的(業務對錯)留給 LLM,把最不可靠的能力從收斂閘關鍵路徑挪開」+ 同日 gap「design-loop 最吃重的『地面事實查證』正是 AI 評審最不可靠(<55%)」。直接動機(設計稿)= 2026-06-23 cross-family 首次真審 nested-agent spec,qwen 誤判 `__SCRATCH__`(sed 替換 token)為 major,人手動 grep 駁回 = 辯方雛形。

## 解決什麼
- **canary 防假陰性、不防假陽性**:canary 驗審計員有沒有認真讀(漏抓=放水),抓不到「認真讀了但判錯」(誤抓)。qwen 引了行號、講得頭頭是道卻誤判,canary 對這型無能為力,甚至因 qwen「醒著」更信任其誤判。
- **原「編排者克制剝誤判」有自填偏誤**:由編排者自己判讀時剝,而編排者同時是「想收斂的人」(剝真 finding 求收斂 / 不剝假 finding 怕擔責)。同 judge-severity-gate 當初要解的「severity 別由利害關係人自填」。

## 關鍵機制
- **架構**:辯方接在 judge 後、record 前。對 judge 評 severity≥major 的每條 finding,派 1 個獨立 opus 辯方(乾淨脈絡、不餵 auditor/judge 結論),refute framing:「預設這條 finding 假/高估,構造反駁、必須附 file:line(實際 grep/Read);光說『沒問題』不算」。
- **無查證行底線**:若 finding 真的無任何查證行(judge 因此鎖 major),辯方也得拿反證 file:line 才能降,拿不出則維持。
- **該輪 severity = 存活 findings max**(編排者機械取,非自評)。被駁倒的 finding 降級、不折、審計紀錄標「辯方反證:<file:line>」;只折辯方存活的真 finding。
- **與四機制的關係**(各防一個失敗模式,互補):canary 防審計員放水/沒讀(測審計員狀態)；judge-severity-gate 防編排者自填 severity;cross-family 防同門盲點(另一檢察官 qwen,且其 disputed 走 self-grep——正是本 spec 要改進的自填偏誤);**辯方防 auditor 認真但判錯**。

## 兩個落點(動作對稱、step 號各異)
- `skills/lumos-design-loop/SKILL.md`(手動版,主對話用 Agent tool 派):步驟 4③辯方、4④存活 max、step5 record、step7 折。
- `governance/autonomous_loop/orchestrator-prompt.md` §2(自動版,claude -p):步驟 4.5 辯方、step6 record、step7 折。
- 注:勿照「對稱」字面去 SKILL 找 step6——SKILL step5=record、orchestrator step5=讀/決定,兩落點 step 號不同(這本身是 R1/R3 揪出的描述陷阱)。

## 已知限制(誠實天花板)
- **只買 code 層假陽性**:① 缺的脈絡在 code 外(業務現實/設計意圖)→ 辯方一樣 grep 不到、判錯,留人。② 辯方自己也沒挖到那塊 code → 拿不出反證 → 按規矩**維持** finding(假陽性沒殺,但「逼證據」讓它不空口誤殺真的——無功但無害)。故辯方只提高「脈絡在 code 裡、auditor 找洞時跳過」那類的糾正機率,**非保證**。
- **辯方也是 AI**:逼 file:line 降低瞎判,但可能查錯/引錯行;證據可複驗(下輪 auditor+人看得到)→ 降低、不消滅。
- **辯方太強會駁倒真 finding**(假陽性換假陰性):強制 file:line+只碰 major+ 限制;一個會偽造證據的辯方仍可能殺真 finding——摩擦地板非 oracle。
- **派工本體無單元測**(prompt 紀律);表態記帳層 2026-08-27 起有代碼有測試;驗證靠 design-loop 實戰觀察「假 major 有沒有被辯方當輪降級」。

## 辯方明確表態進帳(2026-08-27)
辯方裁決從二元(真/假)升成**明確三選一**,並把表態記進帳:
- **agree**:查證後同意這條 finding 是真的 → 維持、折入。
- **evidence**:拿反證降級(minor/clean)+ file:line → 放行、標「辯方反證」。
- **concern**:查了拿不出反證、只剩疑慮 → 維持、折入。**存疑不能單獨殺掉 finding。**

★**降級規則一字未動**★:三態裡只有 evidence 會降,而且照舊必附 file:line;agree 與 concern 都是維持,對應舊制的「真(維持)」——差別只在帳上把「我查證同意」和「我拿不出反證但存疑」分得開。折入/放行去向仍由處置帳的 folded/accepted 決定,**表態欄不掛任何判閘**。記帳:`canary record ... --refute-verdict <id>=agree|evidence|concern`(選填,鍵是辯方判過的子集;`gov --stats` 出三態分布)。

**記帳一致性契約**(2026-08-27 code-loop r1 折入):寫側核對表態與去向對得上——`evidence`(拿反證降級)的 id 必在放行(`accepted-set`)、`agree`/`concern`(維持)必在折入(`folded-set`),對不上 rc2。這是**記帳一致性**(同 accept-reason 鍵須==accepted-set),**不是判閘**,不碰 disposal/收斂——目的是別讓「抽驗降級樣本」抽到根本沒降的,不然這欄的用途會被亂標挖空。
★blocker 輪讓步(2026-08-29,d5)★:同輪 severity=blocker 時,舊規則強制放行清單必須是空的,而反證推翻的發現照規矩「不折入」——兩條一夾使 refuted 發現無處可去、整筆記帳被擋(自主迴圈 2026-08-29 那輪四次撞上,只能把辯方判決留空)。既然本欄自稱純記帳,讓步的就是本欄:**blocker 輪允許 evidence 落在折入,並印一句提醒,反證 file:line 寫進 `--note`**;非 blocker 輪的原檢查一字未動。**判閘沒動**——「blocker 輪該不該讓反證發現放行」是判閘語意問題,要改得走設計審。連帶:`--refute-verdict` 與 `--finding-kind` 都納入「缺 `--findings-set` 就 rc2」的守衛(防選配標註靜默丟失,兩姊妹欄同一 edge case 同一行為)。判閘不讀本欄這條不變式由 `t_refute_verdict_ledger_and_stats` 真跑 `loop status --disposal` 帶/不帶對照守住。

**為什麼加**:[[Projects/收斂機制優化調研2026-08-14]] 2026-08-22 裁「辯方三分類先不做」——它分析的正是這篇論文(F1 0.457→0.533),裁定不抄,理由是我們起點已有三層(引句錨定+行號機驗+外家反證),同樣增益吃不吃得到估不出來,且要改散文層。重啟條件寫的是「出現一次辯方被弱反駁說服、事後證明 finding 是真的」。但那條裁定自己在〈誠實界線〉點名:**帳裡只有 caught/severity/處置,沒有逐席對錯標註**——所以那個重啟條件根本偵測不到。這次**只補這個偵測儀器**:開始記辯方表態,evidence(降級)那批就是重啟條件的候選池,日後抽驗有沒有「降錯、後來證明是真的」。**不翻那條裁定(降級行為沒動),只讓它的重啟條件從此看得見。**

**回頭看的條件(承認風險配套)**:表態有記帳 ≠ 已偵測到重啟條件——still 要人事後標「這條 evidence 降級後來證明是真的」,這步是手動的、目前一筆都還沒做。重驗時機:帳裡 evidence 樣本累積到 ≥10 筆、或每季治理巡檢時,回頭抽驗降級樣本;抽出一例即滿足 2026-08-22 的重啟條件,屆時才走正式翻案上三分類判閘。在那之前,本欄是純觀測。

## 相關
- 設計稿:`docs/design/2026-06-24-finding-refute.md`(design-loop 3 輪自動收斂、canary 3/3 全中)。
- 實作計畫:`docs/superpowers/plans/2026-06-24-finding-refute.md`(3-task prompt 紀律改)。
- 實作落點:`skills/lumos-design-loop/SKILL.md` 步驟 4.5 + `governance/autonomous_loop/orchestrator-prompt.md` §2 步驟 4.5。
