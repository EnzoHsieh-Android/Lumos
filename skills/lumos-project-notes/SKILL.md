---
name: lumos-project-notes
description: 專案知識圖譜(docs/{project}-knowledge/)的進場與讀寫——任何任務開始要搞懂「這個模組/欄位/流程為什麼這樣、邊界在哪、哪些不能改、會波及什麼」時先用 lumos 查,不要直接 grep/Read;改完 code 要寫回決策/驗證/合約;收工體檢。觸發:正要 grep 或讀 code 去理解既有系統、排查、對外支援、查 DB、改名/刪除東西、開工掌握現況、收工寫回、問「圖譜有沒有記」。指令全集按情境分類在 commands/INDEX.md。
---
# lumos 專案知識圖譜——一頁手冊

圖譜記「為什麼、邊界、不能改的、驗過沒」;code 只記「現在長怎樣」。圖譜跟行為事實(測試、實際執行、生產觀測)對不上時,不自動信圖譜——查清哪邊錯,立一篇事故筆記。主工具 `lumos`(python3 零依賴,自動找 `docs/*-knowledge/`)。**別用 Grep/Read/Edit/Write 直接碰圖譜的 .md 開頭欄位**——會繞過自驗和防護;正文段落用 Edit 可以。

**指令怎麼找**:`commands/INDEX.md`(本目錄,4k)——先看「grep 衝動對照表」,再按你正在做的事開九個子檔之一。下面只列每個階段最常用的。

## 1. 進場(每個子任務都重來,不是 session 開頭一次)

| 你在想… | 敲 |
|---|---|
| 這件事為什麼這樣 / 圖譜記了嗎 | `lumos search <詞>` → `lumos context <節點>`;0 命中先換同義詞;**中文概念之間加空白**(`作廢 收回 點數`,別黏成一句) |
| 動這段有什麼不能碰 | `lumos contracts <節點>` |
| 要讀全文再下結論 | `lumos show <節點>`(search 只給索引行;拿摘要判「沒記」以前真的錯過——值在筆記第 64 行,靠摘要判成沒有) |
| 篩條件(金流 / 未收案 / 連到 X) | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
| 開工掌握現況 | `lumos query --tag status/doing`;`lumos recent --days 7` |
| 圖譜空或稀疏(接手 brownfield) | 走節點還原 SOP:`commands/09-節點還原.md`(七步;需要才產節點、有就照慣例用) |

看到筆記有 `core_refs:` 或 `CORE:` → 權威在跨專案核心圖譜,改那邊(`lumos-core-knowledge` skill)。
**查得到才算先行**(Landmark 實測):0 筆看「逐詞覆蓋」標 ★ 的詞換同義詞,換三次再問人,別轉 grep;大節點先 `--brief`;單篇內部新舊打架時摘要有日期的 KEY 行 > 正文,衝突影響決策去 code 裁再回頭修。
**分清你在哪種 session**:本機 Claude Code(含手機/網頁遙控本機)有本機 git 憑證、能 push;網頁版 claude.ai/code 是雲端沙盒,對主分支沒 push 權、只能推 feature branch——「遙控」不等於「遠端版」,曾騙到 AI 一次。
被催「直接改、不用解釋」也一樣:不解釋可以,不查不行——改 code 前至少 `lumos impact --file <檔>` 一行。

## 2. 動手前

- `lumos impact --file <檔>` / `--diff <範圍>`:哪些筆記、驗證、決策會受影響(Edit 前 hook 也會塞一份,但只推你碰到的檔)。
- `lumos pitfalls --diff <範圍>`:風險分級;`tier: high` 要過代碼審(`lumos-code-loop`)。
- 要刪 / 改名東西:`lumos search <舊名> --code` 逐句判哪些筆記還在講它。
- 改了環境 / 流程 / 設定(版本、金鑰、hook、排程):`lumos stale --candidate --match <關鍵字>` 列出寫了「改到這個就該重驗」的驗證紀錄。
- 設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記(`type: project`),不寫到別的路徑;動筆前一行 `PRIOR-ART:`(最小解在哪層 / 世界解過沒 / 借用‧自建‧採用)。

## 3. 寫回(同一次工作內;pre-commit 擋「改 code 沒動圖譜」)

| 要做 | 敲 |
|---|---|
| 新筆記 | `lumos new <system\|issue\|verification\|project> <名>`;驗證紀錄加 `--plan <計劃> --systems <節點>` 自動雙向連 |
| 改狀態 / 日期 | `lumos set <節點> <欄位> <值>`(日期不加引號) |
| 加 / 刪清單項 | `lumos append <節點> <欄位> "[[x]]"` / `lumos remove …` |
| 記決策 / 翻案 | `lumos decision-add <節點> "<內容>" --decided <日期>` / `lumos decision-supersede` |
| 正文段落 | Edit;寫完 `lumos lint <節點>` |

**四條血換的開頭欄位鐵則**:① 多個連結一行一項,擠成一串會長假筆記 ② `summary: |` 區塊裡的 `[[連結]]` 不算連結,要關聯另放 list 欄位 ③ 值含「冒號+空格」要引號或區塊 ④ 同層不能重複鍵。用指令寫天生避開;手改才會踩。

**合約標記(動筆前掃一眼;不確定就不標,嚴禁看 code 反推)**:
```
KEY:★INVARIANT★ <業務合約,改=破壞性> [test:測試名] [audit:模型/日期] [kill:recipes]
KEY:★DEBT★ <偶然行為,可改>
KEY:★IRREVERSIBLE★ <做了回不去> [rollback:decisions]     KEY:★CHECKPOINT★ <改了難救>(建議補 [rollback:])
```
- 綁測試 / 留審計走指令:`lumos guard bind <節點> "<KEY 片段>" <測試名>`、`lumos guard audit …`;裸合約 doctor 擋,未審計 pre-push 擋。綁之前對照 [[Systems/測試假綠形態]](最隱蔽的一型:現場根本走不到被測分支;修 bug 的翻紅測試要配一條「現場成立」的前置斷言)。
- 外部不可逆(信已寄、下游已吃)用 `[guard:decisions]` 寫怎麼防重複。`[test:]` 只證程式對,「規則還符不符合業務」要人確認:`lumos signoff`。
- 從 code 重建的筆記先 `lumos set <節點> regen from-scratch/<日期>`,每條主張標 `[src:]`/`[git:]`/`推測:`/`佚失:`;佚失就寫佚失,嚴禁編。

**摘要區塊**(Systems/Issues 必有):`FLOW:`流程 `KEY:`關鍵概念 `DEP:`依賴 `TEST:`測試;Issues 用 `FLAG:`(只收 TECHNICAL/DECISION/ORIGIN) `DECISION:` `KEY:`。已結案的 Issue 正文第一段要有結案橫幅(status 在開頭欄位,`show --body-only` 看不到,讀者會把修好的當現況)。
**標籤**:`type/` `status/`(值域 lint 硬擋)、`priority/` P0–P3、`scope/`(feature/ area/ 已停用)、`risk/` 金流‧對外送出‧不可逆‧守衛面、`flag/`。

**決策與驗證**:重大決策填四欄(context / alternatives≥2 / why_chosen / trade_offs),缺資訊問人不編。驗證紀錄填 `valid_under`(前提)與 `revalidate_when`(何時重驗),用 `plan_refs` 指回計劃;漏掛 `lumos sync-verified-by --apply`。計劃結案前 `lumos spec-trace <計劃>` 看哪些條款沒人認領。

**承認風險的鐵則**(Enzo 2026-08-22 裁):筆記或訊息裡寫「沒機械守衛 / 只提醒不擋 / 單次量測 / 這數字是拍的」這類承認句,**旁邊必須有「什麼時候回頭看」**(週報、重驗條件、revalidate_when、到期日);寫不出重驗條件的,就是該處理不該承認。**回頭條件要接電**(2026-08-31 回訪案):帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD 一句要做什麼`(緊鄰原句,doctor 到期會唸、逾 14 天沒人動升級週報);綁事件的明寫事件入口——純散文=52 件盤點實證的死文。

## 4. 收工

1. `lumos lint <每篇動過的>` → `lumos doctor`(紅的段先修;`--verbose` 看全部提醒)。
2. code 有「拿掉 / 反轉」的改動:把那些名字逐個 `lumos search <名> --code`,逐句判筆記還成不成立,不成立當場改或標作廢。動到畫面 → 補可重放的 UI flow 並 `[test:<平台>:<flow>]` 綁回(沒裝置要明寫「未驗+原因」)。
3. 圖譜實質更新後:派乾淨 agent 只讀圖譜還原脈絡,對不上就補到一致,留痕 `lumos self-audit <節點>`。
4. push 後(專案有宣告 ci 區塊才有):`lumos ci-wait`,紅就當輪修,修不完要在收尾明講。
5. 跨 session 傳訊只傳「指標+觸發」(我動了哪篇、你去讀哪篇),不傳內容本身;規則權威在圖譜不在誰的記憶。

## 再深一層(按需開,別一次全讀)

| 要做 | 開 |
|---|---|
| 某個指令的旗標與用法 | `commands/0N-*.md`(INDEX 指到)或 `lumos <cmd> --help` |
| 合約鏈深規、[audit:] 五問、guard 工作流、防帶風向 | `reference.md`〈★INVARIANT★ → `[audit:]` 獨立合法性審計〉〈★INVARIANT★ → `[test:]` 綁定〉〈`lumos guard`〉 |
| 決策四欄完整版、驗證紀錄完整規格、同步規則 | `reference.md`〈Properties〉〈同步規則〉 |
| 開頭欄位鐵則、標籤家族、摘要區塊、結案橫幅、退場自問、跨 session 傳訊、CI 細則全文 | `reference.md`〈寫入規範與紀律全文〉 |
| 自足性審計 prompt、交叉審計變體 | `reference.md`〈圖譜更新後：Sonnet agent 自足性審計〉〈變體 B：圖譜×程式碼交叉審計〉 |
| maestro UI flow 派工要求 | `reference.md`〈產 maestro UI flow 的派工要求〉 |
| 資料夾位置 | `docs/{slug}-knowledge/{Projects,Systems,Issues,Verification,MOC}`;某主題 >5 篇建 MOC |
