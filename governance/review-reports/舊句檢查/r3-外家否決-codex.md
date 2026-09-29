severity: major

重現註記：嘗試依規則建立 `git clone --shared` 臨時副本，但唯讀沙盒以 `Operation not permitted` 拒絕建立目錄；以下各項均標「未能重現」，並附靜態程式路徑查證。

## F1 回訪重跑與正式工具使用不同的程式檔集合，量到的不是實際告警準度

severity: major
blocking: 是
引句:「rows 只是方便看,完整清單 REVISIT 用 revisit 子命令重跑拿(它對同一個範圍重算全部命中),所以截少不影響量準度。」
file: `scripts/lumos:23387`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:144`

1. 正式工具依 `_NODEHOME_CODE_EXTS` 判程式檔，其中包含 `.tsx`、`.jsx`、`.mjs`、`.kts`；參考實作的 `TEXT_EXTS` 沒有這些副檔名，反而包含正式工具不認的 `.json`、`.toml`、`.cfg` 等。
2. 具體失敗輸入：推送刪除 `src/OldPanel.tsx`，家筆記仍把該路徑當現況。正式工具會產生一筆要處理發現；P4r3 revisit 不會把這支檔視為程式檔，重跑後完整清單缺掉該筆。反向刪除 `config.json` 時，revisit 又可能產生正式工具從未告警的樣本。
3. 三組舊資料「剛好逐筆相同」只能驗當時資料，不能讓兩份不同分類器在未來兩週輸入上等價。準度分子、分母及單次最大筆數因此不是正式工具實際告警的母體，可能錯誤決定轉成 block。
4. 進實作前須讓 REVISIT 呼叫正式判定函式，或讓重跑完整套用八條刻意差異；並以 `.tsx`、`.json` 等每種差異各造一組未出現在舊資料的回歸案例。
5. 重現：未能重現；shared clone 被唯讀沙盒拒絕。上述分歧可由兩份副檔名清單直接確定。

## F2 回訪差集只看筆記與行號，同一行新增的漏報名稱會被吃掉

severity: major
blocking: 是
引句:「`clause_released` 與 `shape_released` 各自兩層合起來、照上面的鍵去重、照上面的抽判法判真假 → RETIRE-IF ④、⑤」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:1271`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:1279`

1. `cmd_revisit` 先把結果收成以 `(筆記, 行號)` 為鍵的 dict，再用「鍵不在 P4r3」算 released；名稱集合不在差集鍵裡。
2. 具體失敗輸入：同一行寫「現況先呼叫 `stale_alpha`；沒有參數時呼叫 `stale_beta`」，兩個名稱都在推送中消失。P4r3 會因「沒有」過濾 `stale_beta`，留下 `{stale_alpha}`；P4r3c 得到 `{stale_alpha, stale_beta}`。兩邊 `(筆記, 行號)` 相同，`clause_released` 仍是空，真正被字眼過濾漏掉的 `stale_beta` 不會進 RETIRE-IF ④。
3. 形狀過濾同樣會漏：一行同時提到會通過形狀過濾的 `old_alpha` 與被擋的 `resolve`，P4r3s 新增 `resolve` 後仍因行鍵已存在而不進 `shape_released`。
4. 這會系統性低估④、⑤的漏報，讓設計在不符合轉擋門檻時仍可能改成 block。
5. 差集至少要以 `(筆記, 行號, 名稱)` 計算，或對同一行做名稱集合相減；測試須覆蓋「主判法已有一個名稱、變體再增加另一個名稱」。
6. 重現：未能重現；shared clone 被唯讀沙盒拒絕。差集鍵與列表推導可由上述程式行直接確定。

## F3 帳寫失敗只出現在當次 stderr，兩週後無法判斷樣本是否不足

severity: major
blocking: 是
引句:「帳寫不進去的推送(`_gate_event` 回 False,stderr 會講)數不到,rtb 那份沒回報也算樣本不足。」
file: `scripts/lumos:1226`

1. `_gate_event_or_warn` 寫入失敗時只印 stderr 並回傳 False；沒有另一個持久來源記錄「曾漏掉一筆」。
2. 具體失敗輸入：治理帳暫時唯讀或磁碟滿，數次 m1 推送照常完成、事件只在當時終端印出。REVISIT 當天缺少的事件與「那段時間沒有程式推送」「old_sentence=off」完全不可區分。
3. 因此「只要有一筆帳寫失敗就算樣本不足」不是可重算判準。若剩餘帳恰有二十筆且準度達標，流程會在不知道曾漏帳的情況下轉成 block。
4. 進實作前須指定可持久觀測的失敗通道，例如 CI 必收集且回報失敗計數、獨立 fallback 帳，或把 telemetry 寫失敗轉成可機械累計的閘結果；不能只靠兩週前的一行 stderr。
5. 重現：未能重現；shared clone 被唯讀沙盒拒絕。現有函式只印 stderr、無持久後備的行為已由程式確認。

## F4 候選名稱無 200 字上限，但表態入口拒絕超過 200 字，會產生無法表態的擋項

severity: major
blocking: 是
引句:「`drift ack --kind m1` 要至少一個 `--name`(可重複);每個值去頭尾空白後 1 到 200 字、過 `_drift_one_line`;別的種類帶 `--name` 回 2」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:576`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:588`

1. 消失候選直接取 Python 定義名、舊路徑及檔名；參考實作與設計都沒有 200 字上限。含 `/` 的長路徑會直接通過形狀過濾。
2. 具體失敗輸入：刪除一條超過 200 字的受版控程式路徑，筆記仍提到完整路徑，且 `old_sentence=block`。工具會擋下並提示以該完整名稱執行 `drift ack`。
3. 同一份 spec 又要求 `--name` 超過 200 字回 2；使用者即使有合法保留理由，也無法建立涵蓋該發現的精準表態，只能改掉句子或略過整道 drift check。
4. 候選域與表態域必須一致：取消任意的 200 字限制，或在判定端對超長名稱定義另一個可穩定綁定的摘要鍵；並補 201 字 Python 名稱與長路徑測試。
5. 重現：未能重現；shared clone 被唯讀沙盒拒絕。候選生成無上限與表態入口上限的矛盾可由凍結 spec 與參考實作確認。

## 逐節核對

- 依據、PRIOR-ART、範圍：已讀,無 finding。
- 做法 1「抽消失名稱」：已讀；除 F4 外無 finding。
- 做法 2「找筆記舊句」：已讀；除 F2 外無 finding。
- 做法 3「接進 drift check」：已讀；除 F3、F4 外無 finding。
- 做法 4「兩週量準度」：已讀；F1–F3 會讓門檻母體錯誤或不可觀測。
- 與參考實作的刻意差異：已讀；F1 是差異已列出、但回訪流程沒有套用的接縫。
- 條款 S1–S17：已讀；缺少覆蓋 F1、F2、F4 的驗收案例。
- 回退、誠實界線、審計修正紀錄：已讀,無其他 finding。

## 合約核對

- `Systems/guard-kill` 的 rc 優先序與 JSON stdout 純度兩條 ★INVARIANT★：不影響；本設計不改 `cmd_guard_kill`、七態裁定或輸出串流。
- `Systems/lumos-cli-write` 的 frontmatter 原子寫入不變式：不影響；m1 表態追加 JSONL，不修改 `atomic_write_verify` 或圖譜 frontmatter。
- `Systems/存量漂移守衛` 沒有已登記的 ★INVARIANT★；其未帶 `[confirmed:]` 的預設轉 block RULE 也不直接約束獨立的 `old_sentence` 開關。
- impact 推出的 canary、design-loop、生命週期、search、slim install/uninstall、節點範圍 doctor 合約：均不改其命令路徑、rc 或輸出；未發現破壞。

## 實務隱患核對

- 不可逆：已排除；程式與帳在 git，快取可刪。
- 金流：已排除。
- 對外送出：已排除。
- 守衛面：有；F1–F3 使「先量準度再轉擋」的安全閘失真，F4 使精準表態入口不完整。
- 效能與記憶體：有；30 秒預算、快取與 4 MB 上限已有交代，未另發現本輪 blocking。
- 併發：有；快取採唯一暫存名與原子替換。治理帳仍沿既有無共用鎖設計，本輪沒有新增獨立 finding。
- 帳體積：有；rows 截斷本身有界，但 F1、F2 使其「可由 revisit 完整重建」的前提不成立。
- 資安：有；輸出消毒與 shell quoting 已交代，未發現新增 blocking。

最高等級:major;blocking 共 4 條