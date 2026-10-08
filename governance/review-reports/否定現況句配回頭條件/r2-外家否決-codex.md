severity: major

重現狀態：未能重現 shared-clone 實驗；唯讀沙盒禁止 `mktemp` 與 `git clone`，均回 `Operation not permitted`。以下 findings 由凍結 spec、現行程式與既有量測資料核對。

## F1 新增的上線門檻量的是逐行準度，擋不住已量到的提醒洗版

severity: major  
blocking: 是  
引句:「量測裡大約三成多改到圖譜的提交會看到提醒,通常 1 行、最多 10 行;準度 40%,六成的提醒是看一眼就可以略過的。」  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:183`  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:48`  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:54`

1. 第 1 輪 F3 要求補上線門檻，是因為多數提醒為誤報、會訓練作者忽略同一段 stderr。新版門檻只檢查「逐行準度點估計 ≥40%」，沒有檢查有提醒的提交比例或固定教學文字的長度。
2. 現有量測已顯示工具鏈 36%、rtb 32% 的圖譜提交會出聲，而且 60% 提醒可忽略；12/30 又只是剛好壓線，95% 區間下緣約 25%。照字面仍直接上線。
3. RETIRE-IF 同樣沒有噪音或提交命中率條件。具體地，準度維持 40%、照做率 25%、綁錯率 20%、提交命中率 36% 時，三條撤除條件全部不成立，這個預設開啟的高噪音提醒會永久存活。
4. 真違規和提醒會在同一次輸出同時印；每三次圖譜提交約一次的長篇、多數可忽略訊息，正會遮掉 note-shape 的硬擋內容。新增門檻沒有修掉第 1 輪指出的失敗場景。

## F2 綁錯事件的量法只看頂端仍存在的條件，且混入所有非本提醒產生的條件

severity: major  
blocking: 是  
引句:「上線後新寫的條件式回頭條件行(重放時新增行裡 `_revisit_split` 回 `cond` 的行),到量測那天用 `lumos drift scan --at <主線頂端>` 列出條件已成立的」  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:141`  
file: `scripts/lumos:27459`  
file: `scripts/lumos:29572`

1. `drift scan --at` 只建立主線頂端那一棵圖譜，逐篇掃當下仍存在的 REVISIT 行。事件成立後已被刪除或改寫的條件不在頂端，scan 無法列出。
2. 這會形成存活者偏差：正確條件在事情完成後通常被刪除；綁錯但被 `ack` 保留的條件反而較容易留下。量到的比例不是「上線後成立條件的綁錯率」。
3. 母體又是上線後所有條件式回頭條件，不是被本提醒引來的條件；spec 自己承認沒有「這條是不是提醒引來的」欄。大量由其他流程寫出的正確條件，可以把本提醒產生的錯誤條件稀釋到 10% 以下。
4. 具體地，本提醒產生 10 條、其中 6 條綁錯並在被擋後改掉；另有 90 條其他流程產生的正確條件。第 8 週掃描看不到已改掉的 6 條，且會混入後 90 條，可能宣告低於 10% 而提議升級成擋；本提醒本身其實是 60% 綁錯。
5. 這使 RETIRE-IF ③與升級門檻第 4 條都不能回答它們宣稱要量的問題；第 1 輪 F4 的分母缺口只是換成有偏分母，尚未真正處置。

## F3 照做率排除改名筆記，最小樣本卻在排除前計算，能用極小分母誤放行

severity: major  
blocking: 是  
引句:「那一篇被刪或改名找不到,不計入分母。最小樣本:判成真的行 ≥ 10(不到就判樣本不足)。」  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:140`  
file: `governance/eval/negation-revisit/neg_revisit_measure.py:263`  
file: `governance/eval/negation-revisit/neg_revisit_measure.py:357`

1. 最小樣本只要求抽樣中有至少 10 行真句，沒有要求排除刪除／改名後的實際分母仍有 10 行。
2. 具體反例：10 行真句中，9 篇筆記改名但原句照留，只有剩下 1 行真的處理。照 spec，9 行不計入分母、最小樣本仍因原始 10 行而達標，照做率變成 1/1=100%；實際只有 1/10=10%。
3. 量測程式的 `--renames` 只在逐提交取新增行時使用 `-M`；樣本 ID 固定為當時的提交、路徑與行號，設計沒有把該路徑沿後續改名追到頂端。
4. 因此照做率可能在實際遠低於 50% 時通過，錯誤推動「升級成擋」的人工裁決。

## F4 「when- 開頭任何鍵」與指定的參考實作不一致

severity: minor  
blocking: 否  
引句:「鍵是 since、retire、until、confirmed、status、applies、test、audit、kill、rollback、guard、src、git、manual、by、來源、`when-` 開頭的任何鍵(量測程式 `FIELD_RX`)」  
file: `governance/review-reports/否定現況句配回頭條件/r2-snapshot.md:71`  
file: `governance/eval/negation-revisit/neg_revisit_measure.py:153`  
file: `scripts/lumos:26674`

1. 參考實作的 `FIELD_RX` 實際只認 `when-[a-z]+`，不認帶第二個連字號、底線、數字或大寫字母的鍵；既有探針 token 文法則接受 `[A-Za-z0-9_-]*`。
2. 正式實作若照散文遮掉任何 `when-` 鍵，會與要求逐句相同的 `classify_v3` 不一致；若照參考實作，又違反本節與 S9 宣稱的鍵清單。
3. 應先把散文收窄為 `when-[a-z]+`，或修改參考實作並重新量測，否則 S8／S9 沒有單一可實作答案。

## 逐節讀取紀錄

- 白話、依據：已讀；對應 F1。
- PRIOR-ART：已讀，無 finding。
- RETIRE-IF、上線門檻：已讀；對應 F1、F2。
- 範圍：已讀，無 finding。
- 做法 1：已讀；對應 F4。
- 做法 2：已讀，無 finding。
- 做法 3：已讀；對應 F1。
- 做法 4：已讀，無 finding。
- 做法 5：已讀，無 finding。
- 做法 6：已讀，無 finding。
- 做法 7：已讀；對應 F2、F3。
- 做法 8：已讀，無新增 finding。
- 與參考實作的刻意差異：已讀；對應 F4。
- 條款 S1–S9：已讀；S8、S9 對應 F4，其餘無 finding。
- 回退：已讀，無 finding。
- 實務隱患：已讀；對應 F1。
- 誠實界線：已讀；對應 F1、F2。
- 下一步：已讀，無 finding。

最高等級:major;blocking 共 3 條