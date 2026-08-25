# 架構對齊審查報告——probe輪退場_計劃 r1（`/tmp/probe-retire-r1.md`）

## 1. 退場形狀 vs canary d5 先例

先例（file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md` decisions d5 + 頁頂 banner）實際做了四件，不是三件：①義務全停 ②`record` 加 `kind=none` 當觀測載體、**五處閘謂詞同步改**、外加**專屬新測試 `t_loop_panel_none_kind` 三向釘**（機械驗證退場後行為真的正確） ③工具封存不拆 ④**頁頂顯眼橫幅**（`⛔` blockquote，緊接 frontmatter 之後，非埋在一堆 KEY 行裡）。

本案（引句：`裁定=**借用** canary 停用模式:義務退場+碼保留+告示`）只做到「義務退場＋碼保留」，另外兩件都比先例弱：
- 沒有新增專屬機械測試——[S2] 只講「`t_panel_k2_and_probe` 若釘了印行字面則同步」（沿用舊測試，非新增三向釘），行為斷言例2 也只是「既有 panel 測試全綠」，驗證的是「沒改壞」，不是「退場行為本身對」。
- 沒有先例那種頁頂顯眼告示——見下第 2、4 點，落點分別是 SKILL.md 步驟句與 KEY 行尾巴，形式比先例弱得多。

**severity: minor｜blocking: 否｜判準**：三件套的「形」借對了，但「量」比先例縮水（少測試三向釘、少顯眼告示），屬完整度落差非矛盾或另立做法，不擋，建議 r1 補一條專屬測試斷言。

## 2. [S1] 落點——現文存在？改法合行文慣例嗎？

- **code-loop SKILL.md 步驟 7**：確實存在，`file: skills/lumos-code-loop/SKILL.md:24`，原句「要再開一輪 probe-* **抽查**(材料全量、不計上限、抽出 major 自動撤銷收斂)才算做完」。本案引句（引句：`要再開一輪 probe-*(材料全量、不計上限、抽出 major 自動撤銷收斂)才算做完`）漏了「抽查」二字——小瑕疵，不影響定位。該檔是無歷史包袱的「一頁手冊」，直接改句不加告示符合它的行文慣例。
- **design-loop reference 舊制章節**：對整份 `skills/lumos-design-loop/reference.md`（含 SKILL.md、templates.md）逐字搜尋 `probe-`／`應抽`／`抽查`，**零命中**。§四「panel 兩種帳與收斂判準」（`file: skills/lumos-design-loop/reference.md:228-229`）確實是「舊制章節」，但裡面從未提過 probe 輪或抽查判定；抽查判定只活在 `Systems/convergence-evidence-gate.md` 的 KEY 行與 `scripts/lumos` 印行。本案引句（引句：`design-loop reference 舊制章節同步一行告示`）用「同步」二字暗示那裡已有對應內容可比對更新，但現文不存在，這個動作項落地時等於「無中生有」而非「同步」，措辭要修——且該檔既有的退場標記慣例是刪除線＋`**⛔ 已停用**`／`> ⚠` blockquote（`reference.md:162,176,229`），本案只講「一行告示」沒承諾跟這個既有格式對齊。

**severity: major｜blocking: 是｜判準**：SKILL.md 步驟 7 落點對，design-loop reference 的「同步」對象不存在，執行者會找不到東西可同步，須先修正動作描述再落地。

## 3. [S2] 一行字串改 vs tool-output-plain-style

現況兩處（`file: scripts/lumos:4019` 與 `:4122`）：`"[panel] 要不要額外抽查(任何人都能重算出同樣結果): " + ("要——加開一輪 probe-* 抽查(不算進輪數上限;抽出 major 以上就自動撤銷收斂)" if probe else "免抽")`。

本案引句（引句：`scripts/lumos:panel PASS 抽查印行追加`）＋要加的字串「(觀測;2026-08-25 起不再加開輪,詳 Issues/probe輪三參數只在散文)」，若照字面「追加」在既有句尾，「要」分支印出來會變成：
「要——加開一輪 probe-* 抽查(...)才算做完**(觀測;2026-08-25 起不再加開輪...)**」——前半句命令「要開一輪才算做完」，後半句立刻說「不再加開輪」，同一行自我矛盾。這直接撞上已升格為長期標準的家規自檢句（file: `docs/lumos-toolchain-knowledge/Verification/2026-08-21_工具鏈體檢修復批.md:81`）：「讀的人看完第一句就知道發生什麼、不用查代號、知道下一步敲什麼——三者缺一就重寫」。本案「行為斷言」例2 只驗證新片段字面出現，**沒有驗證舊的「才算做完」命令句被移除**，等於驗收標準本身接不住這個矛盾，會帶病落地。

**severity: major｜blocking: 是｜判準**：字串改法本身會製造自相矛盾訊息，違反 tool-output-plain-style 家規，且本案自帶的驗收例不足以攔下，須明講「連同刪掉/改寫『要——…才算做完』那句」才算對齊。

## 4. [S3] 四處寫回——各自存在、是正確權威位置嗎？

- **Issue 結案橫幅**（`docs/lumos-toolchain-knowledge/Issues/probe輪三參數只在散文.md`）：對齊，該檔正是立案來源，結案橫幅落這裡是正確權威位置。
- **`Systems/convergence-evidence-gate` KEY 補退場事實句**：對齊，`file: docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md` 的 KEY 行本就記著「應抽→加開 probe-* 輪…防浮動條款:判準凍結,唯一翻案通道=攢滿 20 筆抽查帳」，是這件事唯一的權威源頭，補句落這裡對。
- **`Projects/panel收斂判準改革_計劃` 補「被翻」段**：**不對齊**。該檔已有一段「被翻紀錄(2026-08-08)」（`file: docs/lumos-toolchain-knowledge/Projects/panel收斂判準改革_計劃.md:34`）——內容是「A 案收斂制與防浮動條款…已由 Enzo 具名推翻…code-loop 收斂改走 --disposal」，講的是 2026-08-08 的**閘切換**那件事。本案引句（引句：`該案無 decisions 陣列,循驗證層去模型化 r1 折入的合法路徑`）描述的動作跟 08-08 那次一模一樣的操作手法，卻完全沒提及、沒區分「已有的被翻段講閘切換」跟「本案要補的是 probe 義務退場」是兩件不同的事——照字面執行容易寫成重複段落或跟既有段落打架，讀者分不清這是同一件事的補充還是另一件事。
- **Enzo 具名認可項**：先例真實存在且精準（`file: docs/lumos-toolchain-knowledge/Verification/2026-08-08_驗證層去模型化落地.md`：「★經 Enzo signoff 具名推翻 panel收斂判準改革 防浮動條款★」「翻案先例已立…後續翻案須同等具名」），本案援引這條先例要求新一輪具名認可，方法論上對齊。但本案的因果敘事（引句：`隨 probe 義務退場而失去 feeder,成為死信`）有精度問題——本案自己「症狀」段已承認 panel 閘自 08-08 起僅供舊帳回放，代表 20 筆抽查帳的餵料早在 08-08 閘切換時就已經停了，不是被本案退場才「新造成」死信；因果講早了約兩週，不影響要不要找 Enzo 簽字，但敘事不精確。

**severity: major｜blocking: 是｜判準**：四處裡三處落點正確，`panel收斂判準改革_計劃` 那一處因為不理會既有「被翻紀錄」段而有重複/混淆風險，須先讀那段、講清楚兩件事的區別再動筆。

---

## 總結

四條判準結果：對齊 0 條（1 條 minor 不擋，3 條 major 且 blocking）。**最嚴重 severity：major。blocking 共 3 條**——[S1] design-loop reference 同步對象不存在（判準2）、[S2] 字串改法會製造自我矛盾訊息（判準3）、[S3] 對 `panel收斂判準改革_計劃` 既有「被翻紀錄」段視而不見（判準4）。第 1 條（三件套完整度落先例）為 minor 不擋，建議一併順手補。