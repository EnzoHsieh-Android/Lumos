severity: major

## F1 形狀過濾的漏報不會進入兩週重跑樣本
severity: major
blocking: 是
引句:「有起點但沒有任何名稱消失 → 不印、不記」
file: `governance/review-reports/舊句檢查/r2-snapshot.md:118`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:95`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:131`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:282`

1. 判定先做形狀過濾；過濾後沒有候選即回 `no-candidates`，不寫治理帳。兩週重跑的 `<base_sha>..<head_sha>` 卻只從治理帳抽取。
2. 具體輸入：某次推送只刪除全小寫函式 `resolve`，筆記仍把 `resolve` 當現況。`_shape_ok("resolve")` 為假，因此整次推送不留事件。
3. REVISIT 的 P4r3s 雖會關掉形狀過濾，卻永遠拿不到這次推送的範圍；所以「兩週後再量形狀過濾放過多少真舊句」存在選樣偏差，最壞可量成零。
4. 這使 RETIRE-IF 無法量出已明知存在的漏報類型，不能據此決定轉擋。
5. 修正要求：在形狀過濾前，只要推送改到程式檔就記錄範圍；至少另存可供 revisit 使用的完整 range 帳。加入「只刪 `resolve`、筆記仍引用」且 P4r3s 必須抓到的驗收案例。
6. 重現:未能重現——唯讀沙盒禁止建立共同規則要求的隔離 clone，`mktemp` 回報 `Operation not permitted`；以上由凍結設計與參考實作控制流靜態查證。

## F2 轉擋門檻忽略大量判定失敗
severity: major
blocking: 是
引句:「state 是 done 的才進準度的分母;timeout 進完成率;git-failed、unreadable、no-base 各數一個數、另列」
file: `governance/review-reports/舊句檢查/r2-snapshot.md:30`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:109`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:120`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:126`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:130`

1. RETIRE-IF 只限制準度、單次筆數、timeout 比例與字眼過濾漏報；`git-failed`、`unreadable`、`no-base` 只有列數，沒有阻止轉擋的門檻，也沒有最低 `done` 樣本數。
2. 具體資料：100 筆有候選的帳中，95 筆為 `unreadable`，5 筆為 `done`；5 筆全判真且每次不超過 30 筆。依字面算法，準度 100%，timeout 比例為 `0÷5=0%`，其餘條件也可通過。
3. 轉成 block 後，同樣的 95% `unreadable` 會按設計作為「判不了」硬擋使用者；提醒期數據卻沒有把這種不可用率當成否決條件。
4. 灰色樣本同樣被排除分子與分母；即使只剩極少可判樣本，仍可能以表面高準度轉擋。
5. 修正要求：規定最少 `done` 數、可判定覆蓋率與灰色上限；`git-failed`、`unreadable`、`no-base`、帳寫入失敗均須進整體完成率或各自設否決門檻。資料不足時只能維持 warn。
6. 重現:未能重現——唯讀沙盒禁止建立隔離 clone；上述 95/5 資料依凍結規格公式可直接算出。

## F3 去重鍵丟掉名稱後真偽沒有唯一答案
severity: major
blocking: 是
引句:「要處理層的 rows 對 (路徑, 原文) 去重——同一句沒改、每次推送都會再列,只算一次」
file: `governance/review-reports/舊句檢查/r2-snapshot.md:120`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:127`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:128`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:129`

1. 帳中每列包含 `names`，而真假定義取決於「該事件消失的名稱」；但準度去重只保留 `(path, text)`，沒有名稱或事件版本。
2. 具體輸入：同一行一直是「舊版用 old_alpha，現在呼叫 old_beta」。第一次推送刪 `old_alpha` 時屬歷史說明，應判假；第二次刪 `old_beta` 時同一原文把消失名稱當現況，應判真。
3. 兩筆的 `(path, text)` 完全相同、`names` 不同。設計要求合併，卻沒定義保留哪組名稱、取聯集，或只要任一次為真便算真。
4. 因而相同帳本可因人工挑到不同事件而得到不同準度，並可能跨過 60% 轉擋線；兩週度量不可重現。
5. 修正要求：度量單位至少加入排序後的 `names`，最好再帶消失來源或事件 `head_sha`；若堅持合併，須明定名稱聯集及真偽聚合規則。加入同路徑、同原文、不同名稱且真假相反的測試。
6. 重現:未能重現——唯讀沙盒禁止建立隔離 clone；衝突由帳的既定欄位與去重鍵可靜態推出。

## F4 驗收參考實作與正式程式檔範圍不一致
severity: major
blocking: 是
引句:「凡是本計劃的字面跟 P4r3 不一樣,以 P4r3 為準、並回頭改計劃」
file: `governance/review-reports/舊句檢查/r2-snapshot.md:21`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:27`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:49`
file: `governance/review-reports/舊句檢查/r2-snapshot.md:131`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:116`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:138`
file: `scripts/lumos:23387`
file: `scripts/lumos:23603`

1. 正式設計指定非 Python 檔沿用 `_nodehome_code_kind`；它包含 `.tsx/.jsx/.mjs/.kts/.c/.cpp` 等，卻不包含 `.json/.toml/.yaml/.cfg/.ini/.txt/.dart`，而且副檔名大小寫敏感。
2. P4r3 的 `Code.kind` 使用另一份 `TEXT_EXTS`，包含後一組、缺少前一組，且先把副檔名轉小寫。
3. 具體差異：刪除 `src/OldPanel.tsx` 時正式工具會產生路徑候選，P4r3 完全忽略；刪除 `config.json` 時 P4r3 會計入，正式工具忽略；`legacy.PY` 也會因大小寫得到不同分類。
4. 因此 P4r3 的歷史數字不能驗收正式實作，REVISIT 也在量另一個檢查器。若照「P4r3 為準」實作，又會直接違反同份設計指定的既有 `_nodehome_code_kind` 範圍。
5. 修正要求：先抽出正式工具與實驗共同使用的程式檔分類器，再重跑 P4r3/P4r3s 基準；至少加入 `.tsx`、`.json`、`.PY` 的差異測試。數字重算前不應進實作。
6. 重現:未能重現——唯讀沙盒禁止建立隔離 clone；兩份副檔名集合與大小寫處理已由現碼逐字核對。

## 實務隱患逐類

- 不可逆：已讀,無 finding。功能只讀 Git 與筆記，新增的是版本控制內治理帳及可刪快取，設計有回退路徑。
- 金流：已讀,無 finding。沒有付款、額度或帳務動作。
- 對外送出：已讀,無 finding。沒有網路、郵件或外部 API 寫入；跨會談只要求回報既有 grep 結果。
- 守衛面：有 finding，見 F1–F4；主要風險是漏報樣本進不了度量，以及低可用率仍可能轉成硬擋。
- 效能：已讀,無額外 finding。30 秒期限、4 MB 剖析上限、快取與超時退路均有明文；失敗率門檻缺口已併入 F2。
- 記憶體：已讀,無 finding。AST 放大風險已有 4 MB 上限、例外處理及未剖提示。
- 併發：已讀,無 finding。快取採唯一暫存檔與原子替換；治理帳沿用既有寫法，未發現本設計新增的競態。
- 資安與輸入安全：已讀,無 finding。AST 不執行程式；路徑、原文及名稱經 `_esc_clean`，可貼 shell 參數另經 `_drift_sh`，快取兩端驗權限。

## 既有合約與行為核對

- `guard kill` 的 rc 優先序合約：已讀,無 finding。本設計沒有改 `guard kill` 的七態、rc 合成或錯誤優先序。
- `guard kill --json` 成功時 stdout 單行 JSON 合約：已讀,無 finding。本設計沒有改該命令或輸出通道。
- 圖譜寫入 T1 原子自驗：已讀,無 finding。新功能寫治理帳與快取，不修改 frontmatter 寫入原語。
- 既有 `_drift_check_core`、考試與歷史重放：已讀,無 finding。設計明定 m1 另開函式；未發現要求把 m1 塞回既有核心的句子。
- 做法 2 的撤除節、歷史區、字眼與家判定：已讀,無額外 finding。
- 回退、合約候選與審計修正紀錄：已讀,無額外 finding。

最高等級:major;blocking 共 4 條