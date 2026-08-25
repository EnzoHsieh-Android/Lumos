# 架構對齊審查報告——loop-friction-v2 r1

被審:`/tmp/loop-friction-v2-r1.md`(62 行)。四項逐一判。

## 1. d3 回縮:三處現文對齊、[S3] 目標位置已修正

- file: `skills/lumos-design-loop/SKILL.md:43` 現文「暫用門檻 >1 條 blocking/300 字,本專案自定 heuristic、未實測校準,校準前只當攤人建議訊號」——與 v2 描述的「SKILL 現文...自定 heuristic、校準前只當攤人訊號」語意及關鍵數字一致,且該段本次確實**一字未動**(v2 只是引用現況,未提出修改)。
- file: `docs/lumos-toolchain-knowledge/Verification/2026-08-25_設計審收斂重定義落地.md:12` 校準 KEY 原文含「...建議上修至 2 條/300 字待下案再驗」——與 v2 稱「既有校準結論『上修 2 條/300 字待下案再驗』維持」一致,不是 v2 捏造。
- [S3] 目標位置:v1 曾誤指 Systems/design-loop.md(file: `governance/review-reports/loop-friction/r1-s1.md:56`「查『建議上修』該檔 0 命中...這句話實際只出現在 Projects/連鎖佇列軟提醒_計劃.md:67...[S3] 指的編輯目標寫錯檔案」;佐證重跑於 file: `governance/review-reports/loop-friction/r1-intake.md:20`)。v2 現行 [S3] 已改指 `docs/lumos-toolchain-knowledge/Projects/連鎖佇列軟提醒_計劃.md` 下一步段——實地讀取該檔(下一步節)確認含「重寫門檻建議上修」字樣;另一半目標指 `Verification/2026-08-25_設計審收斂重定義落地.md` 校準 KEY,也確認存在。**位置已修正,不是重蹈 v1 覆轍**。

**判定**:對齊。blocking: 否。

## 2. rN-intake.md 新慣例

- file: `governance/review-reports/loop-friction/r1-intake.md` 已存在,是本案自用首例(v2 審計修正紀錄自陳「r1-intake 慣例本案起用」屬實)。其「引句機械收貨」節確有重現指令+輸出(python 正規化比對區塊,三句皆標 HIT),形狀貼合 d1「重現命令+輸出摘錄」的要求。
- 但「佐證通道抽驗」節 5 條裡有 2 條(refcheck 正則實測、[S6] 校準已跑)只寫「file:line + 『屬實』判詞」,沒有附實際重現指令與輸出片段——形式上落回 d1 自己要排除的「編排者口頭說『我驗過』」,只是多掛了個 file:line 錨點,並非真正的可重現紀錄。
  **severity: minor,blocking: 否**,判準:v2 尚未把此慣例正式寫入 templates.md/SKILL.md([S1][S2] 待辦),現在的不一致屬前導樣本瑕疵,不構成本次「照既有做法走」的偏離;但落地時 [S1] 應把「佐證通道抽驗」也要求附實際指令+輸出,不只是「查過為真」的斷言,否則新慣例名存實亡。
- 與既有收貨三道(quote-check/refcheck/seat-check)的關係:核心裁定明確分工(quote-check 顧引句錨定、refcheck 顧 file:line 存在、rN-intake.md 顧「真偽」的機械重現留痕),[S2] 用「步驟 4 收貨加...一句」而非「加一道」的措辭,沒把「收貨三道」改成「四道」,不會被讀成取代既有機制。
  **severity: minor,blocking: 否**,判準:內容上不衝突、也沒有僭越既有三道的職能,但通篇沒有一句顯式聲明「新增於既有三道之外、非取代」,對不熟悉脈絡的讀者仍留一絲誤讀空間,建議 [S1] 落地時補一句顯式排除語。

## 3. rewrite 寫入端歸屬切割

- file: `scripts/lumos:434`(`cmd_loop_rewrite` docstring)原文:「人裁『整份重寫』的收尾記帳(設計審收斂重定義 d3 帳面件的寫入端;2026-08-25 第一次真實 rewrite 事件時補建)」——與 file: `docs/lumos-toolchain-knowledge/Verification/2026-08-25_設計審收斂重定義落地.md:11`「寫入端=第一次真實 rewrite 事件時才建(照 spec 收窄,不 gold-plate)」的承諾完全對得上。
- git 提交紀錄(commit `70fc8c2`,2026-08-25)與治理帳 file: `docs/.governance-log.jsonl:21555-21556` 證實:同一天先補測試(`t_loop_rewrite_mark`,file: `scripts/test_lumos.py:3790`)再記下首筆 `gate=design-loop kind=rewrite` 事件(note 帶 `prev=loop-friction;successor=loop-friction-v2`)——「裁甲當日先行落地並釘測試」屬實,且該子命令不在 v2 自己的落地件清單([S1]-[S4])裡,「不佔本案條款」的切割準確、無夾帶。

**判定**:對齊。blocking: 否。

## 4. 一事一处/正本指定

- [S1] 明文「正本歸屬循既有聲明(templates 權威、SKILL 摘要),不另立」——該既有聲明實際存在於 file: `skills/lumos-design-loop/templates.md:6`「SKILL.md 內嵌 framing 是摘要,漂移時以本檔為權威」,v2 沒有發明新規則,是援引已確立的慣例(且此慣例已有先例:blocking↔severity 綁定規則同樣兩邊都寫,見 file: `governance/review-reports/loop-friction/r1-s1.md:50`)。
- 卷證規則(引句限凍結審材)本就隱含在 SKILL.md 既有 quote-check 步驟描述中,不需另寫;佐證格式(`file: \`路徑:行號\`` 含反引號)只單寫入 templates.md、不重複進 SKILL.md;rN-intake.md 才是唯一真正雙寫的項目,且已由上述一句定調 templates.md 為正本、SKILL.md 只放一句指標。三件事沒有各說各話。

**判定**:對齊。blocking: 否。

## 總結

四項判讀共 **6 條**(4 項主檢查 + 2 條 minor 建議);**最嚴重 severity: minor**;**blocking 共 0 條**。核心的三處現文一致性、[S3] 目標位置修正、rewrite 寫入端歸屬、正本指定,均查證屬實、對齊既有做法,沒有引入第二種做法或與既有文件矛盾。唯一值得注意的是 rN-intake.md 這個新慣例的首例本身(r1-intake.md)在「佐證通道抽驗」節部分條目未完全貫徹自己訂的「非口頭斷言」標準——建議 [S1] 落地時把這條收緊,但不影響本次架構對齊放行。