severity: blocker

## F1 更新機制沒有把推送前審查裝進使用端 CI
severity: blocker
blocking: 是 —— 不改，使用端以 no-verify 推送時兩層守衛都會被繞過，直接放進壞筆記。
引句:「不是 git 或找不到 lumos 就照既有 hook 慣例放行並說一句(推送前與 CI 會再跑一次)」
file: `scripts/lumos:16888` — `lumos update` 的固定白名單只包含 CLI、測試、hooks 與紀律範本，不含 `.github/workflows/ci.yml`。
file: `scripts/lumos:17158` — 更新流程只複製上述白名單。
file: `.github/workflows/ci.yml:98` — 現有代碼審 CI 閘只存在這個來源 repo 的 workflow。

1. 具體輸入是在使用端專案執行 `lumos update`，再提交一行 `FACT: 重試上限固定為 3`。
2. 執行 `git push --no-verify` 會略過 pre-commit 與 pre-push；使用端 CI 也沒有 spec 所稱的 `note-shape` 或 `note-audit` 步驟。
3. 兩層守衛皆未執行，與 spec 用來容許本機 hook 放行的「推送前與 CI 會再跑」保證直接矛盾。
4. 回退段承認來源 repo 的 CI 需手動移除，卻沒有定義如何把新增 CI 閘分發到使用端；照字面實作只會保護這個 repo。

## F2 ADR 欄位名稱寫錯，正式替代方案欄會完全漏審
severity: major
blocking: 是 —— 不改，實作者會依錯誤欄名取值，讓合法 ADR 欄位成為穩定繞過路徑。
引句:「每條的文字欄(content / context / why_chosen / alternatives / trade_offs)」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:91` — 現行決策資料使用的欄位是 `alternatives_considered`。
file: `scripts/lumos:4999` — CLI 寫出的決策結構同樣使用 `alternatives_considered`。
file: `scripts/lumos:12904` — 現行決策解析器依正式 schema 解析決策欄位。

1. 具體輸入是在 frontmatter 新增決策，於 `alternatives_considered` 寫入「目前 scripts/lumos 只有三種模式」。
2. 共同取行範圍只抽 spec 列出的五個文字欄；正式的 `alternatives_considered` 不在其中。
3. 該行位於 frontmatter，亦不會落入正文逐行審查。
4. `note-shape` 看不到一般現況句型，`note-audit` 也沒有收到該行，結果是兩層都放行。

## F3 引句前綴可讓任意內容退出兩層守衛
severity: major
blocking: 是 —— 不改，任何投稿者只需加固定前綴，就能主動隱藏程式碼現況。
引句:「別人的原話,改了就是竄改」
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:24` — 決策要求筆記不得保存可從程式碼推出的內容，沒有給引句豁免。
file: `scripts/lumos:7205` — 現有 `引句:` 特判服務的是審查材料格式，並未建立知識筆記內的來源驗證機制。

1. 具體輸入是新增正文行 `引句:目前系統只有三種付款方式`。
2. 共同取行範圍先排除所有以 `引句:` 開頭的行；兩個閘因此都收不到它。
3. 設計沒有要求來源、被引文件、逐字比對或引用邊界，也沒有驗證這真是第三方原話。
4. 即使確為原話，句中仍可夾帶會漂移的系統現況；d1 禁止的是內容本身，而不是作者身分。

## F4 完成計劃的整篇收斂只出現在 prepare，check 沒有同一套集合規則
severity: major
blocking: 是 —— 不改，狀態切成 done 的提交可以在沒有審查紀錄時通過，且無法強制收成一句。
引句:「那篇計劃整篇正文都進清單,不只新增行——照 d4 要把現況收成一句」
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:45` — d4 要求完成計劃只留下開案問題與原因的一句話，細節必須刪除。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:9` — 判定規則把計劃與需執行才能知道的結果歸為 `CONTEXT`，不是一律拒絕的 `CODE`。

1. 具體輸入只把計劃 frontmatter 的 `status: doing` 改成 `status: done`，正文保留原有二十行實作現況。
2. `status` 行被共同範圍排除，普通新增行集合為空；spec 只在 `prepare` 段宣告整篇擴張。
3. `record` 與 `check` 段仍寫成重算「新增筆記行集合」，沒有要求沿用完成計劃的整篇擴張；照字面實作時 `check` 得到空集合並放行。
4. 即使實作者自行把擴張補到三個子命令，AI 規則也只拒絕 `CODE/MIXED`；二十行純動機、計劃或實驗結果可全判 `CONTEXT`，沒有任何規則檢查「只剩一句」。

## F5 審查指紋不綁程式碼快照，既有通過紀錄會在語義改變後繼續有效
severity: major
blocking: 是 —— 不改，原本合法的脈絡行可在後續程式變更後變成可推導現況，卻不會重新審查。
引句:「指紋只看內容:rebase、壓提交、只改程式碼都不影響;筆記行內容一變就要重審」
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:8` — `CODE` 的判準明確依目前程式碼、測試及設定是否可查得。

1. 先新增 `RULE: 生產重試上限為 3`；當下此值只來自程式庫外的部署平台，因此審查判為 `CONTEXT` 並留下通過紀錄。
2. 留痕後再提交 `config/prod.json`，把重試上限設為 3；同一句筆記此時已可由 repo 設定直接推出。
3. spec 明定只改程式碼不改指紋，`check` 會沿用舊通過紀錄，不觸發重新分類。
4. 同一漏洞也適用 skip：模型故障時留下的 skip 可跨任意程式碼變更重用，導致其統計不再代表當次推送的判定缺口。

## F6 判定模型契約與 Codex 路徑互相矛盾
severity: major
blocking: 是 —— 不改，Codex 使用者無法同時滿足預設模型、同提供者及已校準模型三項要求。
引句:「預設 opus;★判定者跟編排會談用同一家模型提供者,不派外家席★」
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:6` — 此工具鏈正式支援 Claude Code 與 OpenAI Codex 兩種 harness。
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:59` — Codex 審查席使用 GPT 系列模型，不是 Opus。

1. 具體輸入是在 Codex 會談中執行 `lumos note-audit prepare`。
2. 若照「預設 opus」派工，判定者落到另一家提供者，違反同一句的同提供者與不派外家席條款。
3. 若改派 GPT，則違反明載的預設模型；上線校準數據也只驗證 Opus，沒有 GPT 的 30 行零錯誤證據。
4. S14 只規定 prompt 或取行範圍改變時重跑，未把模型或提供者變更列入失效條件，無法補上這個分支。

## F7 留痕寫入追蹤檔後沒有提交步驟，本機通過而 CI 必然失敗
severity: major
blocking: 是 —— 不改，正常 record 流程產生的通過只存在工作樹，乾淨 CI 看不到。
引句:「治理帳有對得上的通過或 skip 就放行,否則 rc1 並印 prepare 那行指令」
file: `scripts/lumos:28749` — 既有 code-loop 專門檢查留痕後的 dirty bookkeeping。
file: `scripts/lumos:28774` — 既有流程明示治理帳檔必須提交。
file: `scripts/lumos:20532` — lint waiver 同樣明示豁免檔必須提交。
file: `.github/workflows/ci.yml:14` — CI 從乾淨 checkout 開始，不會取得本機未提交內容。

1. 開發者先提交程式與筆記，再執行 `note-audit record`；新紀錄被 append 到已追蹤的 `docs/.governance-log.jsonl`。
2. 本機 pre-push 從工作樹讀到該紀錄，因此通過。
3. push 傳送的仍只有既有 commits；CI checkout 不含剛 append 的紀錄，重新執行 `check` 時找不到對應指紋並回傳 rc1。
4. spec 沒有仿照既有機制提示或阻擋未提交治理帳，也沒有要求重新提交後再檢查，形成必現的本機綠、CI 紅迴圈。

## F8 新鎖只包住 note-audit，沒有排他於其他治理帳寫入者
severity: major
blocking: 是 —— 不改，spec 宣稱要消除的同檔競寫仍可由既有命令觸發。
引句:「那種無鎖直接 append 兩個會談同時寫會壞行,讀端會靜默跳過」
file: `scripts/lumos:928` — `_gate_event` 直接 append `docs/.governance-log.jsonl`，不取得 vault lock。
file: `scripts/lumos:28816` — `_codeloop_gov_log` 也直接 append 同一檔案，沒有取得該鎖。
file: `scripts/lumos:28712` — code-loop 讀端遇到無法解析的 JSONL 行會直接略過。

1. 會談 A 執行 `note-audit record` 並取得 spec 指定的 vault lock。
2. 同時，會談 B 執行現有 `code-loop pass` 或其他 `_gate_event` 寫入路徑；既有 writer 不認這把鎖，仍直接寫入同一檔案。
3. 鎖只約束新 writer，沒有形成共同排他區，spec 自己指出的壞行與靜默跳過結果仍然成立。
4. S13 只測兩個 note-audit 寫入者，無法揭露新舊 writer 交錯的實際路徑。

## F9 prepare 產物宣稱不進版控，但路徑沒有被忽略
severity: major
blocking: 是 —— 不改，正常整批加入會把審查清單與完整派工詞提交進 repo。
引句:「不進版控);集合指紋=所有(路徑, 行文字)排序後的雜湊」
file: `.gitignore:1` — 現有 `.lumos` 規則只涵蓋指定測試快取及 lint baseline，沒有 `.lumos/note-audit/`。
file: `scripts/lumos:17333` — 初始化流程只設定既有治理檔案的追蹤或忽略規則，沒有新增 note-audit 路徑。

1. 執行 `note-audit prepare` 會建立 `.lumos/note-audit/<fp>.md`，其中含所有待審行及完整模型派工詞。
2. 現行忽略規則不匹配該檔；`git add -A` 會將它納入下一次提交。
3. 該路徑不在知識圖譜範圍內，兩層新守衛也不會攔截這個工具產物。
4. 結果違反「不進版控」的明示契約，並永久保存原本只應作為本機暫存的審查內容。

## F10 decision-amend 沒有定義遠端範圍，無法可靠判斷決策是否已推送
severity: major
blocking: 是 —— 不改，合法修訂會被卡死，或已公開決策會被錯誤允許改寫。
引句:「只准改還沒推上遠端的決策——範圍起點不存在那個編號」
file: `scripts/lumos:30308` — 既有 code-loop 對非當前 checkout 及多 ref 情境要求明確 `--branch`。
file: `scripts/lumos:30313` — 既有檢查另以 `--at-sha` 綁定實際推送版本，避免用錯 ref。

1. 具體情境是在本機 `feature-a` 推送 `HEAD:refs/heads/review-a`，或在尚未設定 upstream 的新分支執行 `decision-amend`。
2. 新命令介面沒有 remote、push destination、base ref、`--branch` 或 `--at-sha`，卻要求判定「範圍起點」是否已有決策編號。
3. 若實作者取 `main` 或其 merge-base，已推到 `review-a`、尚未合入 main 的決策會被誤認為未推送，允許覆寫歷史。
4. 若找不到 upstream 就拒絕，第一次推送前的合法修訂會被卡死；S12 只測內容變更，沒有任何 ref 拓撲案例替這個判斷定義答案。

〈判定者能不能用:小實驗〉已讀,無 finding

〈規範文字跟著改〉已讀,無 finding

〈審計修正紀錄〉已讀,無 finding

實務隱患逐類核對:

- 守衛覆蓋與繞過:有，見 F1–F5、F10。
- CI、分發與留痕一致性:有，見 F1、F7。
- 併發與資料完整性:有，見 F8。
- 模型提供者與資料外送邊界:有，見 F6。
- 工作樹污染與意外入版控:有，見 F9。
- 可用性與推送卡死:有，見 F7、F10。
- 效能與模型成本:無 finding；設計採單批判定、列出耗時與配額界線，沒有逐行模型呼叫。
- 新依賴與供應鏈:無 finding；方案沿用現有零依賴 CLI 與既有 harness，未引入套件。
- 不可逆資料刪除:無 finding；新命令以讀取及 append 留痕為主，回退順序不要求刪除使用者筆記。
- 金流、權限提升與秘密處理:無 finding；功能不觸及金流或權限提升，且 spec 明定 prompt 不送 gitignored 檔、秘密及憑證。

總結:最嚴重 severity 是 blocker、blocking 共 10 條。