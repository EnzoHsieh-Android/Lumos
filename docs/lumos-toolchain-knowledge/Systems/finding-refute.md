---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-24_finding-refute]]"
summary: |-
  FLOW:auditor→findings→judge(caught/missed+severity,排掉canary後最嚴重真finding)→【辯方refute(新,step4.5)】對每條 judge 評 severity≥major 的 finding 各派 1 個獨立 opus 辯方(乾淨脈絡、不傳 auditor/judge 結論)→辯方回真(維持)/假(降級+file:line反證)→該輪 severity=存活 findings 機械取 max→record(用重算 severity)→只折存活真 finding(被駁倒的不折、標「辯方反證:<file:line>」)
  KEY:防的失敗模式=auditor「認真讀了但判錯」的假陽性(誤抓);與 canary 防「沒讀/放水」的假陰性(漏抓)方向相反、對稱補位
  KEY:純 prompt 紀律疊加階段,無代碼、無單元測;只動 SKILL.md(手動版)+orchestrator-prompt.md(自動版),不碰 canary/judge/cross-family/lumos 原語/record
  KEY:辯方效力來源是「任務方向相反」(被逼構造推翻證據、查 auditor 跳過的反方向),非「更會看 code」;故 1 個辯方+強制 file:line 即可,不 N 個多數決
  KEY:只買 code 層假陽性——脈絡在 code 外(業務現實)或辯方自己也沒挖到那塊 code 時,拿不出反證則維持 finding(無功但無害);業務層留人(誠實天花板)
  KEY:辯方降級也須拿反證 file:line,拿不出則維持;對齊 judge「無查證行鎖 major」底線,空口『沒問題』不算
  DEP:skills/lumos-design-loop/SKILL.md 步驟4.5｜governance/autonomous_loop/orchestrator-prompt.md §2 步驟4.5｜judge-severity-gate(辯方接 judge 後)｜canary(對稱補位)
  TEST:無單元測(prompt 紀律);design-loop 實戰自驗,3 輪自動收斂、canary 3/3 全中
  VERIFY:[[Verification/2026-06-24_finding-refute]]
decisions:
  - content: 辯方階段插在 judge 後、record 前——對 judge 評 severity≥major 的每條 finding 各派 1 個獨立 opus 辯方,預設 finding 假、強制附 file:line 反證才能降,該輪 severity 由編排者機械取存活 findings 的 max
    context: design-loop 全是檢察官(auditor 找洞)、缺辯方;canary 只驗審計員有沒有認真讀(防漏抓),抓不到「認真讀了但判錯」(誤抓)。2026-06-23 qwen 把已處理好的 __SCRATCH__(sed 替換 token)誤判 major,canary 對這型無能為力
    why_chosen: 把原「編排者克制剝誤判」(自填偏誤:利害關係人自評 severity)升級成獨立帶證據裁決,同 judge-severity-gate 精神(severity 交獨立評定者);辯方靠任務方向相反逼出反方向 grep,殺 code 層假陽性
    decided: 2026-06-24
    valid: true
  - content: 只對 severity≥major 派辯方、只派 1 個(非 N 個多數決)、不重派 judge 算 severity
    context: good()=caught 且 severity∈{clean,minor},minor/clean 不影響收斂;要選「1 辯方+file:line」還是「N 辯方投票」
    why_chosen: 強制 file:line=確定性查證(可被下輪 auditor/人複驗),比 N 個 AI 投票更貼「確定性>AI 判斷」主軸且省算力;minor/clean 派辯方是白費算力
    decided: 2026-06-24
    valid: true
  - content: 辯方效力來源是「任務方向相反」、不是「code 證據」本身——故不靠多派 auditor
    context: 質疑「缺脈絡時辯方憑什麼比 auditor 對」;auditor 提 major 時其實也 grep 過(強制查證)
    why_chosen: auditor 找洞(看到可疑就提、無動力深挖反證),辯方被逼構造推翻證據(專查 auditor 跳過的反方向);同樣 grep、目標命題相反→挖的角落不同。多派 auditor 只生更多起訴、同找洞方向
    decided: 2026-06-24
    valid: true
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
- **無單元測**:prompt 紀律(同 cross-family/judge-severity-gate 的 prompt 改),無代碼可單元測;驗證靠 design-loop 實戰觀察「假 major 有沒有被辯方當輪降級」。

## 相關
- 設計稿:`docs/design/2026-06-24-finding-refute.md`(design-loop 3 輪自動收斂、canary 3/3 全中)。
- 實作計畫:`docs/superpowers/plans/2026-06-24-finding-refute.md`(3-task prompt 紀律改)。
- 實作落點:`skills/lumos-design-loop/SKILL.md` 步驟 4.5 + `governance/autonomous_loop/orchestrator-prompt.md` §2 步驟 4.5。
