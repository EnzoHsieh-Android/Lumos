# 架構對齊審查報告——code-probe-retire r1

範圍:`r1-docs.patch`(481 行,兩家 skill+五篇圖譜)、`r1-code.patch`(262 行,scripts/lumos + test_lumos.py)。核對方式:兩份 patch 逐檔 add/del 行與當前 repo(HEAD=03842ce)比對,確認 patch 內容等於已落地版本(僅個別行因 hunk 上下文移位造成誤判,已逐一排除),行為斷言直接對落地後檔案實跑 grep。

## 1. 落地件對 [S1]-[S3] 與 c1-c4/d2/d3 裁定

- **[S1] SKILL.md 步驟2/7 消歧義+刪義務句+護欄補註**:對齊。步驟2「只在 high 的多席編制(記帳與問閘見步驟 6-7」、步驟7「單席循序與多席(2026-08-25 甲裁後)一律 lumos loop status」、護欄句補「(含 high;2026-08-25 甲裁後多席亦處置閘)」均逐字落地,「再開一輪 probe」句已刪(grep=0)。severity:無;blocking:否。
- **[S2]① 4019/4122 印行整句改寫**:對齊。`_panel_probe_verdict` 呼叫處兩處(scripts/lumos:4035、4138)已改為「本輪落在應抽樣——2026-08-25 起 panel 僅回放、不再加開 probe 輪」,「才算做完」「要——加開一輪」全部 0 命中。severity:無;blocking:否。
- **[S2]② cutoff 拒判**:對齊。`_panel_retired_for`(scripts/lumos:3843)cutoff 預設 `2026-08-26`、env `LUMOS_PANEL_RETIRE_CUTOFF` 覆寫,命名與行為對齊既有 `LUMOS_PANEL_K2_CUTOFF` 慣例;`_loop_status_panel`(3926)與 disposal 撞牆訊息(10090)兩處都掛了這條守衛,cluster 變體因是同函式內部呼叫故一併受covered,無漏防。severity:無;blocking:否。
- **[S2]③ code-* 嚴格輪級(d2)**:對齊。`_loop_status_disposal` 內 `AC and str(loop_id).startswith("code-") and any(...major/blocker...)` 只加嚴 code-\* 前綴、且散文不受影響,符合「以 loop 編號 code- 前綴判;散文迴圈維持 blocker 門檻」。severity:無;blocking:否。
- **t_panel_probe_retired 三釘 + 既有測試凍結手法**:對齊,且是本輪較漂亮的一手——`test_lumos.py` 頂部 `_os_mod.environ.setdefault("LUMOS_PANEL_RETIRE_CUTOFF", "9999-12-31")` 把既有 panel 測試整批凍結在退役前語意,`t_loop_status_disposal_panel_routing`、`t_panel_k2_and_probe` 因此不需逐條改斷言就自然維持正確,比計劃原文字面「期待值同步」更省事但語意等價。severity:無;blocking:否。
- **[S3] ⛔ 告示、被翻紀錄二、reference.md 三處(180/332/374)、06 指令檔**:對齊,詳見第 3、4 節。
- **[S3] Issue 結案橫幅**——`docs/lumos-toolchain-knowledge/Issues/probe輪三參數只在散文.md` body 加了「✅ 已結案」橫幅,但 frontmatter `status: open` 與 tag `status/open` 未同步改(patch 只加了 body 一行,未動 frontmatter)。severity:minor;blocking:否——判準:落地件字面只承諾「橫幅」,橫幅確實加了,但欄位未跟著改會讓 `status/open` 查詢繼續把這篇當未結案,建議補一次 `lumos set`。
- **[S4] 迴圈摩擦三修_計劃.md 兩輪數據回寫**——初判疑似漏做(計劃檔本體 `## 落地件`/`## 下一步` 仍寫「[S4] 掛下案」),深入查證後確認**對齊**:真正的回寫落在 `Verification/2026-08-25_迴圈摩擦兩修落地.md`(patch 內),新增 KEY「★[S4] 實測已跑(probe-retire 兩版三輪為載體)★」並把「誠實邊界」段從「[S4](下案實測)未跑」改成「[S4] 已跑(見 KEY)」,計劃檔 `status: doing→done` 正是該筆記自己寫的退場條件「計劃 status 維持 doing 至 [S4] 驗畢」兌現後的自然結果。唯一殘留:計劃檔本體的「下一步」一行(「...[S4] 掛下案」)沒跟著更新,是同一節點內文正本(Verification)與副本(計劃檔散文)新舊打架的典型情況。severity:minor;blocking:否。

## 2. 行為斷言例1-5 實跑驗收

```
例1: grep -c "再開一輪 probe" skills/lumos-code-loop/SKILL.md            → 0  (目標0) 過
     grep -cE "僅供.*舊迴圈回放" skills/lumos-code-loop/SKILL.md         → 1  (目標≥1) 過
例2: grep -c "不再加開 probe 輪" scripts/lumos                           → 2  (目標2) 過
     grep -c "要——加開一輪" scripts/lumos                                → 0  (目標0) 過
例3: t_panel_probe_retired 三釘(a)(b)(c) 讀碼逐一核對邏輯與訊息字串,均對應到實作 過
例4: reference.md:180/:374 均含「回放」字樣                               過
     grep -c "判準凍結" convergence-evidence-gate.md                     → 2  (目標「維持1」) 不符
例5: grep -c '"round": "probe-' docs/.canary-log.jsonl                   → 0  (目標0) 過
```

- **例4 後半不符**:severity:minor;blocking:否——判準:c3 實質要求(判準凍結句原文保留、未被改寫)確實達成(convergence-evidence-gate.md:23 原句一字未動),count 從 1 變 2 純粹是因為新增的 ⛔ 告示自己也引用了這個詞(file: `docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md:68`,回放條件段落提及「判準凍結」一詞),計劃作者寫斷言時沒預料到新告示會自我引用,屬斷言目標值過時而非落地錯誤。

## 3. ⛔ 告示結構 / 被翻紀錄二 / 殘留 panel-現行 文件

- **⛔ 告示四段結構**:對齊。convergence-evidence-gate.md:65-69 新增告示逐段對應 canary-audit 範本——標題(帶裁定日期+decisions d3)/理由/落地實證/回放條件,末句「以下 KEY 中 panel/K=2/抽查相關行=退役前機制紀錄」呼應 canary-audit 的「不是現行協議」收尾,唯一差異是把 canary 的「重啟條件」換成「回放條件」——這是刻意調整(panel 是進入永久回放模式,不是等待技術突破後重啟),語意上更準確。severity:無;blocking:否。
- **被翻紀錄二 vs 08-08 段**:對齊。`panel收斂判準改革_計劃.md:34-40` 明確寫「上段(08-08)翻的是閘切換...本段翻的是多席路由+抽查機制」,兩段區分清楚未混寫。severity:無;blocking:否。
- **殘留掃描(兩家 skill + commands + 根目錄)**:在嚴格範圍內(`skills/lumos-code-loop/*`、`skills/lumos-design-loop/*`、`skills/lumos-project-notes/commands/*`、repo 根目錄)乾淨——`lumos-design-loop/SKILL.md`、`templates.md`、`commands/05-設計審查迴圈.md` 雖未被本輪 patch 觸碰,但都是被更早的「設計審收斂重定義」批次已修正過,現文已正確寫「僅已定錨 panel 帳的舊迴圈用」。
- **但擴大到相鄰檔案發現一處真殘留**:`skills/lumos-project-notes/reference.md:1261`「⛔ **協議已於 2026-08-14 全面停用**...現行:輪記帳...收斂閘=design-loop `--disposal`/code-loop `--gate --panel`(none 制輪有效=記帳席≥2)。」——同一份文件在 `:692`(76379ca 已訂正)與 `:1273`(gate 契約補注,已訂正)都寫對了,但 `:1261` 這第三個「現行收斂閘」重複段落沒被那次「三處清掉」的修正掃到,現在同時牴觸 2026-08-08 舊裁定與今天的 d1。severity:major;blocking:否——判準:內容本身確實與裁定矛盾(把已作廢的「code-loop 現行走 panel」講成現行事實),但這份檔案不在 r1-docs.patch/r1-code.patch 觸碰範圍內、也不是本輪落地件承諾要修的檔案,故不擋這兩份 patch,但因議題與今天裁定完全同源,建議立刻補一個小 patch(同批或緊接著的下一輪)清掉,不要留到下次才被抓到。

## 4. 十二處「已定錨」訂正文字抽查(3 處)

- **skills/lumos-code-loop/SKILL.md 步驟7**(其中一處訂正處,亦被本輪 patch 直接改寫):對齊——甲裁落地後語意完全一致(見第1節)。
- **Systems/design-loop.md「d5 落地」KEY 行**(未被本輪動,內含 2026-08-25 早先的「code-loop 自 08-08 亦處置閘」訂正字句):對齊——單獨看這行對「多席」未講清楚(08-08 字面其實只落到單席,今天 d1 才真正涵蓋多席,計劃本身也承認這點),但本輪 patch 在同節點頭部另外插入一行新 KEY「多席 code-loop 統一處置閘([[Projects/probe輪退場_計劃]])」把缺口補上——多條 KEY 並存、後出覆蓋前出是本專案既有寫法慣例,不算矛盾。severity:無;blocking:否。
- **skills/lumos-project-notes/reference.md:1261**:如第3節,**不一致**——這正是十二處訂正裡被漏掉的一處(該批次自陳「訂正的訂正」只補了「現行收斂閘行+gate 契約補注×2」共三處,`:1261` 是第四個同型重複段落,從未被那次或這次修正碰到)。severity:major;blocking:否(理由同第3節)。

## 總結

- 最嚴重 severity:**major**(1 條,即 `skills/lumos-project-notes/reference.md:1261` 殘留「code-loop 現行走 panel」的過期教學,牴觸 2026-08-08 舊裁定與今日 d1)。
- blocking 共 **0 條**——該 major 項不在這兩份 patch 的觸碰範圍內,不擋這一輪落地,但建議緊接著開一個小 patch 清掉,避免和 08-08、08-25 兩次「先裁後動」具名翻案的紀律精神打臉自己。
- 其餘 4 條 minor(判準凍結 grep 目標值過時、Issue 節點 frontmatter status 未隨橫幅同步、迴圈摩擦三修計劃檔本體「下一步」文字落後於其 Verification 正本、免抽分支「(觀測)」以共用前綴而非逐分支複寫實現)均為對齊落地內的措辭/欄位級小瑕疵,均非 blocking。
- [S1]-[S3] 落地件逐條核對 c1-c4/d2/d3,無條款漏做、無條款做超過裁定範圍;行為斷言 5 條除例4 後半(斷言目標值過時,非落地錯誤)外全數過。