severity: major

## F1 prepare 與 record 之間沒有可驗證的來源錨點

severity: major

blocking: 是 —— 照字面實作後，record 無法可靠驗證 reviewer provider、模型及校準版本是否與 prepare 相符

引句:「報告開頭三行齊全、provider 跟 prepare 給的編排者同一家、申訴報告的席名跟被申訴那份不同」

1. Spec 段落：〈第二層：語意抽查〉的 prepare、record，以及〈判定者小實驗〉。
2. prepare 檔名只含「待審集合指紋」；record 只接收 `--diff`、`--report`、`--dispute`，沒有 prepare artifact ID、編排者、模型或校準批次參數。
3. 作者依流程刪除 CODE 行、修改 MIXED 行後，record 重算出的待審集合已不同於 prepare 時的集合，不能用目前指紋唯一找回原 prepare。舊檔又保留十四天，相同或重疊集合可同時存在。
4. 重現：以 Claude prepare；刪除一條 CODE 行；交給 Codex 或同 provider 的未校準模型出報告；執行 record。設計沒有可信資料可判斷這份報告是否屬於原 prepare，也沒有規則核對 line 73 所要求的模型校準版本。
5. 現有審查迴圈會把 orchestrator 直接帶入並驗證，不靠報告自述；Codex 席模型則是可變常數。第二層沒有等價錨點。

file: `scripts/lumos:10851`

file: `scripts/lumos:10865`

file: `scripts/lumos:17858`

## F2 逐實體行分類可由換行拆散語意

severity: major

blocking: 是 —— 程式碼可推得的單一敘述能被拆成數行，取得逐行 CONTEXT 覆蓋後靜默通過

引句:「檢查時,範圍裡每一行都要被某筆已提交的紀錄涵蓋」

1. Spec 段落：〈哪些行進第二層〉、〈一行一張通行證〉、條款 S6。
2. 借用的第一層函式把每個實體行 `strip()` 後放入集合；第二層內容編號也以單一實體行為單位。Spec 只處理「同一行有多個子句」，沒有處理「同一子句跨多行」。
3. 重現輸入：
   1. 第一行為 `目前只有`
   2. 第二行為 `兩個 handler。`
4. 合併後是可由程式碼驗證的數量宣稱；逐列分類時，兩列都不是完整命題。分類器可對兩列各自產生 CONTEXT，record 依逐行涵蓋寫入兩個 ID，check 隨後通過。
5. 第一層實作確實丟失行間語意與位置關係，因此第二層不能僅靠「直接借第一層」補回這個邊界。

file: `scripts/lumos:23633`

file: `scripts/lumos:23811`

## F3 done 清掃漏掉同篇既有摘要與 decisions

severity: major

blocking: 是 —— 計劃改成 done 時，已知高漂移區的舊摘要仍可留在筆記並通過

引句:「若範圍內某計劃被改成 done(含改名後才改的),prepare、record、check 三者算出的集合都應含它整篇正文」

1. Spec 段落：〈哪些行進第二層〉、條款 S5。
2. done 特例只擴大到「整篇正文」；未變動的 summary 與 decisions 仍不在集合。第一層的新增行集合也只會提供本次新增內容，不能補入既有摘要。
3. 重現：某 doing 計劃的 summary 已有 `FLOW: 目前只有兩條路由`；本次只把狀態改成 done。prepare、record、check 依 S5 清掃正文，但該 summary 沒有新增或修改，因此不受第二層審查。
4. 第一層設計的事故資料明載，漂移集中於摘要與完成計劃的現況段；本版補丁只封住後者，卻把同篇摘要留在閘外。

file: `scripts/lumos:23519`

file: `scripts/lumos:23633`

file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:80`

## F4 decision-amend 的遠端檢查沒有定義改名映射

severity: major

blocking: 是 —— 已發布決策在筆記改名後會被判成未發布，破壞只能 supersede 的合約

引句:「逐一讀遠端追蹤參照上的同一篇來判,跟分支拓撲無關;沒有任何遠端就都能改」

1. Spec 段落：〈第二層：語意抽查〉的處置規則、條款 S15。
2. 現行決策的全域識別是「筆記路徑 + `#dN`」；`d1` 本身只在單篇筆記內唯一。Spec 沒有定義如何把改名後的本地路徑對應到遠端舊路徑。
3. 重現：`origin/main` 有 `Projects/A.md#d1`；分支把筆記改名為 `Projects/B.md`，再執行 decision-amend。直接讀 `origin/main:Projects/B.md` 會得到不存在，於是判為可改；全庫搜尋 `d1` 又無法辨識是哪篇筆記。
4. 該路徑會直接改寫已發布決策，而非要求新增 superseding decision。必須先定義 rename-following 或穩定節點身分，S15 才可執行。

file: `scripts/lumos:14880`

file: `scripts/lumos:14887`

file: `scripts/lumos:14956`

## F5 證據路徑未限制在 repo 內

severity: major

blocking: 是 —— record 可遞迴讀取 repo 外路徑，造成安全邊界突破及無上限掃描

引句:「路徑是檔或資料夾都可、資料夾就遞迴掃、跳過 .git」

1. Spec 段落：〈第二層：語意抽查〉的 record 驗證。
2. file 證據只要求檔案與行號存在；search 證據允許檔案或資料夾遞迴掃描。未要求 repo-relative、拒絕絕對路徑與 `..`、限制 symlink 邊界或設定掃描預算。
3. 重現報告可填入 `file: /etc/passwd:1`，或 `search: impossible-token in / => 0`。照字面實作會讀取工作樹外檔案；後者還會遞迴掃描整個檔案系統，阻塞 record。
4. 現有 CLI 已有專門的 `_validate_repo_ref`，並明載若不拒絕絕對路徑與 traversal，`/etc/passwd` 這類 repo 外證據會被誤判為有效。本設計沒有借用這層既有防線。

file: `scripts/lumos:19819`

file: `scripts/lumos:19824`

file: `scripts/lumos:19831`

## F6 同一待審集合的 prepare 會跨 provider 互相覆寫

severity: major

blocking: 是 —— 兩個合法會談可在無錯誤訊號下覆蓋彼此的 provider-specific prompt

引句:「兩個會談同時 prepare → 清單檔以待審集合指紋命名、原子寫入」

1. Spec 段落：〈第二層：語意抽查〉、〈實務隱患〉。
2. 檔名只使用待審集合指紋，但 prompt 內容取決於 `--orchestrator claude|codex`。相同 diff 分別以兩個 orchestrator 執行 prepare，會命中同一路徑。
3. `_write_lf` 只保證單次 replace 不產生半檔；其註解明確指出未上鎖的 read-modify-write 仍是 last-write-wins。
4. 重現：會談 A 執行 `prepare --orchestrator claude`，會談 B 對同一範圍執行 `prepare --orchestrator codex`。兩者得到同一檔名，後寫者覆蓋前者；A 隨後會派出錯誤 provider 的 prompt，且 F1 所述 record 介面無法識別這次替換。
5. 因此「指紋命名、原子寫入」沒有化解 spec 自己列出的並行風險。

file: `scripts/lumos:14146`

file: `scripts/lumos:14150`

### 逐節覆核

1. 〈依據、拆分決定、PRIOR-ART、RETIRE-IF〉：已讀,無 finding。
2. 〈判定者小實驗〉：校準結果本身已讀,無額外 finding；模型切換與執行閘的銜接見 F1。
3. 〈哪些行進第二層〉：見 F2、F3。
4. 〈一行一張通行證〉：見 F2。
5. 〈第二層：語意抽查〉：見 F1、F4、F5、F6。
6. 〈跟第一層怎麼疊〉：已讀,無額外 finding。
7. 〈CLAUDE.md／skill／範本怎麼改〉：已讀,無 finding。
8. 〈驗收條款〉：S5 見 F3；S6 見 F2；S9、S12 見 F1；S15 見 F4；其餘已讀,無 finding。
9. 〈失敗回退〉：已讀,無 finding。
10. 〈實務隱患〉：並行處置見 F6；證據掃描邊界見 F5。
11. 〈誠實限制〉：已讀；未揭露的逐行切割限制見 F2。
12. 〈審查修正紀錄〉：已讀,無額外 finding。
13. 文件內部標題、wiki 節點、程式檔與 `judge_prompt.md` 交叉引用均已核對存在；無壞連結 finding。

### 實務隱患鏡頭

1. 守衛繞過：有。逐行切割、done 摘要漏掃與改名決策路徑分別見 F2、F3、F4。
2. 供應商與模型漂移：有。prepare provenance 與校準版本無可信錨點，見 F1。
3. 併發與資料競爭：有。同集合、不同 provider 共用輸出檔，原子替換仍會 last-write-wins，見 F6。
4. 檔案系統與秘密邊界：有。證據路徑可逃出 repo，見 F5。
5. 效能與可用性：有。未設根目錄及掃描預算的遞迴 search 可阻塞 record，見 F5。
6. 治理帳容量：有，但已列入限制並接上 2026-12-31 的 REVISIT；本輪無額外 finding。
7. 外部不可逆副作用：無；流程只寫本地筆記、暫存檔、提交與治理帳，未觸及金流、通知、部署或外部資料刪除。
8. 金流與計價：無；此功能沒有付款、額度或帳務路徑。

總結: 最嚴重 severity: major；blocking 6 條。