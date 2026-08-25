# 架構對齊審查報告——probe輪退場_計劃 v2(r1)

被審:`/tmp/probe-retire-v2-r1.md`(69 行)。逐項判對照 repo 既有做法。

---

## 1. canary 停用三件套(告示形狀+測試三向釘)補齊到位嗎

**severity: minor,blocking: 否**。判準:兩件都「有補」,但都只補了形狀的骨架、沒補到精度,不算「與既有文件矛盾」,只算「不到位」。

- 告示形狀:v2 對 [S3] 只寫「convergence-evidence-gate KEY 補裁定事實句+頁頂 ⛔ 告示(canary 同款,含『回放仍可用』)」。
  引句(審材): 補裁定事實句+頁頂
  對照 file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:94-100` 的實際告示有固定四段結構(標題行帶裁定日期/決策 id → 理由三腳 → **落地實證**段落 → **重啟條件**段落 → 尾句「以下正文是停用前…不是現行協議」)。v2 只點名「同款」和「回放仍可用」一句話,沒把四段結構列進落地件——實作時容易漏段(尤其「重啟條件」)。

- 專屬測試:v2 對 t_panel_probe_retired 的斷言描述(引句:新印行字樣斷言+disposal PASS 輸出不含,見審材第 43/51 行)是三則**印行字串比對**(含新觀測句/不含「才算做完」/不含「抽查」)。對照 file: `scripts/test_lumos.py:10748`(`t_loop_panel_none_kind`)——canary 先例的「三向釘」測的是**三種情境下的閘邏輯行為**(none 輪有效 rc0/嚴重度合取讀 none 列 rc1/單席仍無效 rc1),且其中一釘專門記錄了「只斷 rc 分不出、要加斷 stdout 的 ✗ 行才真的釘住」這種防止假綠的教訓(canary-audit.md KEY 行同款描述)。v2 的三則斷言只是「文字有沒有變」,不是「行為有沒有變」,借了「三」這個數字但沒借到「行為級可翻紈」這個實質——退場本身確實只是印行文字改動(d1 沒動 gate 邏輯),所以嚴格意義上沒有新行為可測,但寫成「補三向釘缺口」這個定性比對稍微誇大了對齊程度,建議措辭改成「三則印行斷言」而非套用「三向釘」這個已有特定含義的詞。

## 2. d1 路由統一與今天已推送的「已定錨」訂正文字一致嗎

**對齊,無 severity(不構成發現)**。全檔 grep「已定錨」在 design-loop 相關文件命中 13 處(`Projects/設計審收斂重定義_計劃.md:29/57/84`、`Verification/2026-08-25_設計審收斂重定義落地.md:26`、`Systems/design-loop.md:29`、`skills/lumos-project-notes/reference.md:692/693/1273`、`skills/lumos-design-loop/SKILL.md:7/36`、`skills/lumos-project-notes/commands/05-設計審查迴圈.md:3/10`、`skills/lumos-design-loop/reference.md:252`),逐處判讀:全部一致主張「panel/K=2 僅供已定錨舊迴圈回放,code-loop 自 2026-08-08 起亦走處置閘」。

甲裁之後,這批文字**變成說對了**,不是需要再改——d1(引句: 多席 code-loop(含 high)一律 d5 型記帳)正是把這批文字「已經走處置閘」的斷言從「文件先講、機制未必跟上」補成事實的那個決定。而且 v2 自己的症狀段①已經誠實承認這批文字在寫下當下(08-25 稍早)其實**還沒有機制支撑**——file: `skills/lumos-code-loop/SKILL.md:19,24,30` 現在仍寫「多席不同鏡頭…只在 high 的 panel」「多席 panel → --gate --panel…K=2 連續兩輪」,跟已推送的 12 處「已定錨」文字互相矛盾,而這正是 v2 [S1] 要修的對象——即 v2 準確診斷了這個落差並排進落地件,不是漏判。唯一沒被 v2 點名的細節:那 12 處文字寫的「code-loop 自 2026-08-08 起」沒分單席/多席,對高分級 panel 而言這個日期不準(真正讓多席可走 disposal 的是今天的 d1,不是 08-08);但這只是措辭精度問題,不影響「已補齊還是待補」的判斷方向,不另立一條。

## 3. [S1] 有沒有處理 code-loop SKILL 步驟 2「只在 high 的 panel」這句

**severity: minor,blocking: 否**。判準:[S1] 明列的改動範圍逐字只到步驟 7 與護欄段,沒把步驟 2 排進去,退場後留下一個局部可能誤導但很快被下文澄清的殘留詞。

引句(審材): code-loop SKILL.md:步驟 7 改寫

v2 [S1] 的落地件只提步驟 7(記帳行 rewrite)和「舊制 panel…K=2」護欄句(補註記),完全沒提到 file: `skills/lumos-code-loop/SKILL.md:19` 這句「多席不同鏡頭(正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致)只在 high 的 panel」。這裡「panel」原意是「一組審查員」(編制,d1 明說「編制不變」),但退場後同一份 SKILL 幾行之後(步驟 7)把「panel」重新定義成「已停用、只供舊迴圈回放的閘」——同一個詞在同一份文件裡從「編制」切到「已退役指令」語意,讀者若只看步驟 2 容易誤以為 high 分級仍在問 `--gate --panel`。因為步驟 7 就在附近會把疑惑接住,危害有限,故評 minor 非 blocking,但建議 [S1] 補一句(例如步驟 2 後綴「編制仍為 panel,記帳與問閘見步驟 6-7」)一併排入落地件,避免遺漏。

## 4. t_panel_probe_retired 命名與擺放慣例

**對齊,無 severity**。判準:比對現有 `t_panel_*` 家族(`t_panel_near_perfect_and_gov_ledger`、`t_panel_k2_and_probe`,以及 `t_loop_panel_*`/`t_disposal_gate_rN_panel_hardening` 兩個旁系),`t_panel_probe_retired` 落在 `t_panel_*` 這支且直接呼應它要動到的 `t_panel_k2_and_probe`(審材第 59 行已自陳這支既有測試會被印行改寫波及)——前綴選對了家族。file: `scripts/test_lumos.py:21840` 顯示測試是 `sorted(globals().items())` 依函式名字母序探索並執行,不是依檔案物理位置,所以「擺放在哪」不影響執行語意,v2 沒指定插入位置不構成缺陷。唯一可議的是命名風格:掃過全檔沒有任何既有測試用「_retired」這種「以被砍掉的舊功能命名」的方式(對照 `t_loop_panel_none_kind`、`t_panel_k2_and_probe`、`t_loop_next_legacy_emits_a_command_that_actually_runs` 都是以「現在測的行為/新機制」命名),`t_panel_probe_retired` 是唯一一個以「退場事件」命名而非「新行為」命名的案例——風格上是新樣式但不构成不一致,未達發現門檻,僅供參考不列 severity。

---

## 總結

四項判讀:第 2、4 項對齊;第 1、3 項各一條 **minor**,**blocking: 否**。全份最嚴重 severity = **minor**,blocking 合計 **0 條**——不構成擋下 v2 的理由,但建議在進入實作前把①告示四段結構列進 [S3] 落地件、②步驟 2 的「panel」補一句排入 [S1],兩處都是幾秒鐘的補丁,不需要重開一輪審查。