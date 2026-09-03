# v2 r1 外家否決席報告(Codex, gpt-5.6-sol, sandbox=read-only, 前景執行)

---

1. 核心配對器不存在：`_quote_rows` 只回傳 `quote`、`ok` 與格式旗標，沒有快照中的起訖 offset；而正規化還會刪除 Markdown、反引號與空白，事後也不能直接拿原字串位置充當區間。v2 沒規格化「正規化字串到原快照位置」的映射、多重命中如何選、重複句如何處理，因此 M1/M2 的位置重疊判準目前無法照 spec 實作。
severity: blocker
blocking: 是；主指標的唯一 matching oracle 缺少必要輸出與替代演算法，實驗算不出數字。
引句:「兩條引句在 `r(N-1)` 快照裡的錨定位置區間重疊即算同一條;完全不重疊即算不同條。」
file: `scripts/lumos:11445` `_quote_rows` 宣告。
file: `scripts/lumos:11461`–`scripts/lumos:11475` 只做正規化後的存在性判斷並回傳 `{"quote","ok"}`，沒有任何位置欄位。

2. 「純新增」篩選仍需要 finding→修訂 hunk 的對應，spec 的免映射推論不成立。歷史 finding 的引句錨在舊版中已存在的問題敘述；真正補上的條款通常位於另一處，甚至一條 finding 可能導致多個 hunk。只知道某份 diff 內有純新增 hunk，不能判定哪個新增是在修哪條 finding；若看引句附近 hunk，又會錯漏非局部修正。這正是 v1 遺失的「finding→折入改哪裡」鏈，v2 只是把 id 換成位置措辭。
severity: blocker
blocking: 是；無此映射就不能建立「漏項型 finding」分母，M1 樣本標籤不可重算。
引句:「這個判定是機械的(diff hunk 的型態),不需要知道哪個 hunk 對應哪個 id。」
file: `governance/review-reports/entry-latch/r1-external.md:2` finding 指向事故歸因與外部證據，不是待新增條款所在位置。
file: `governance/review-reports/entry-latch/r1-external.md:4` 同一 finding 同時要求文字／JSON 合約及多 phase 測試，天然跨多個修訂位置。

3. 「答案卷各席都有逐字引句且必然錨回快照」被真實母體反例推翻。`entry-latch` r1 的 carrier 有七條 findings，但報告完全沒有 `引句:` 格式；因此 `_quote_rows` 會直接回 `None`。這不是孤兒檔：帳本正把它列為 r1 的 carrier、帶完整 `findings_set`。依 v2 退場規則會整個剔除迴圈，但 spec 未先盤點有多少母體因此消失，四個樣本可能根本湊不出。
severity: blocker
blocking: 是；標準答案的宣稱資料前提已被帳內正式樣本直接反證。
引句:「那些報告逐條寫著:當時抓到什麼、`severity` 多少、以及★逐字引句★——而引句必然錨得回 `r(N-1)` 快照」
file: `docs/.canary-log.jsonl:792` `entry-latch` r1 carrier 記有七個 `findings_set`，報告指向 `r1-external.md`。
file: `governance/review-reports/entry-latch/r1-external.md:1`–`governance/review-reports/entry-latch/r1-external.md:9` 是七條編號敘述，無任何 `引句:` 欄。
file: `scripts/lumos:11459`–`scripts/lumos:11460` 無引句時明確回傳 `None`。

4. 同一輪不一定有單一 `r(N-1)` 快照，材料定義仍有歧義。`Android側UI測試綁圖譜工作流` r1 三席各自綁定不同 `snapshot_path` 與不同 SHA；v2 一面說「各席報告本身」，一面把 deficient 寫成單數的 `r(N-1)` 快照，去重也只說比較「該 snapshot_sha256」，沒有規定逐 finding 使用自己的席位快照、如何組成一個迴圈樣本及如何去重。
severity: blocker
blocking: 是；材料、引句座標系與去重鍵均不唯一，選不同帳列會得到不同答案卷。
引句:「一律以帳上 `snapshot_path` 欄為準,不用檔名慣例猜」
file: `docs/.canary-log.jsonl:400`–`docs/.canary-log.jsonl:402` 同一 loop/r1 分別指向 `r1-snapshot-s1.md`、`s2.md`、`s3.md`，三個 SHA 皆不同。

5. fixed 組不是乾淨的偽陽對照：後輪快照常已寫入上一輪「審計修正紀錄」，直接列出上一輪發現與折入內容。新席位在 fixed 組重述答案卷項目，可能只是正確引用文件內的歷史紀錄，不能一律判成「無中生有」。這會把 M2 系統性灌高，再依讀法 4 降級 M1。
severity: blocker
blocking: 是；對照組洩漏標籤，M2 不再測 hallucination，且會直接污染主結論。
引句:「那些條款已經補進去了;在這一組報「缺這條」就是無中生有」
file: `governance/review-reports/entry-latch/r2-snapshot.md:78` 起的「審計修正紀錄」逐項列出 EL-1 至 EL-10，明載 r1 findings 與處置。
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:126` 已把 eval-awareness／知道被測後配合演出列為真實失效模式。

6. M1、M2 與第一批場次的聚合單位沒有定義。答案卷是「各席 findings」，新跑是每組三席；spec 未說 M1 是任一新席命中即算、逐席配對、三席聯集，還是 3×finding 微平均；M2 卻改用「有幾成的席位報出答案卷上那條」。門檻取整所稱的 `n` 也沒有說是迴圈數、finding 數或席位×finding 數。
severity: major
blocking: 是；同一批原始報告可依合理聚合法得到不同 M1、不同可達刻度與相反裁決。
引句:「deficient 組裡,答案卷上的漏項型 finding 有幾成被重新抓到」
file: `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:150` M1 未定席位聚合。
file: `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:151` M2 使用席位比例，與 M1 分母語意不同。
file: `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:166` 門檻取整使用未定義的 `n`。

7. 隔離宣稱三道，但機械防呆只斷言兩個路徑條件，沒有驗證最承重的安全條件：remote 確實為空、`core.hooksPath` 指向沙盒且 pre-push 可執行並回非零、帳本與原卷證在執行前後未變。尤其 runner 若誤在真 repo 呼叫其他寫入命令，只靠「不呼叫 canary record」的散文約束擋不住。
severity: major
blocking: 是；已有真實誤推事故，安全控制卻未對其三個失敗點逐一 fail-closed。
引句:「runner 開跑前先斷言「輸出根目錄不在 `governance/review-reports/` 底下、且沙盒路徑不等於 repo 根」」
file: `scripts/scenario_probe.py:168`–`scripts/scenario_probe.py:177` 真正沙盒會移除 remote、建立 blocking hook 並設定 `core.hooksPath`；v2 的預定斷言沒有核驗這三件事。
file: `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:171` 不寫帳本僅以流程宣稱表達，沒有 before/after hash 守衛。

8. canary d5 的核心邊界未處理完整：v2 承認同樣量「有沒有抓到」，卻沒有規定盲化實驗提示、移除快照內審計修正紀錄或防止席位知道 deficient/fixed 身分。d5 的重啟條件要求先能區分「真醒／演醒」；本案雖改稱不評價席位，仍用相同行為訊號作修法／關案決策，不能靠改名消除 eval-awareness。
severity: major
blocking: 是；若席位看得到組別或歷史答案，測得的是應試重現率，不能支撐「閘對漏失有感」的因果結論。
引句:「差別在本案不拿它評價席位可靠度,只拿它回答一個是非題:「這道閘對內容漏失有沒有感覺」」
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:78` d5 明載 caught/missed 翻譯不出結論。
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:98` 重啟條件是能區分「真醒／演醒」的探針出現。
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:126` 行為層 caught/missed 無法排除 eval-awareness。

9. 母體分類數重算可復現，但「868 筆」不是可重放的凍結輸入。按 spec 規則重算仍為 80 個迴圈、代碼 27／設計 53、設計多輪 25／單輪 28；然而當前帳檔已有 873 行且處於修改狀態。spec 只寫日期，沒有帳本 commit、SHA 或截至哪一列，未來無法重建當時的 868 筆母體。
severity: minor
blocking: 否；分類結果目前仍一致，不阻止實驗，但削弱預註冊與日後重算性。
引句:「來源=`docs/.canary-log.jsonl`(2026-09-03 當日 868 筆)」
file: `docs/.canary-log.jsonl:873` 當前檔案共 873 行；依 `findings_set`、`_roster_kind` 與 unique round 重算仍得到 80／27／53／25／28。
file: `docs/.canary-log.jsonl:868` 日期不足以界定後續追加前的輸入邊界。

最嚴重 severity: blocker；blocking 共 8 條。
tokens used
99,842