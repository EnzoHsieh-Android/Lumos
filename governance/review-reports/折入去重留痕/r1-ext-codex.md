# r1 外家否決席報告(Codex,前景)

---

1. `fold.json` 沒有寫入入口，也沒掛進現行第 6–8 步；所謂「寫入驗證」實際上只可能在選配的 `--from-fold` 讀取時執行。編排者可完全不產檔、產檔後不跑 `capture-counts`，或直接手填 `--capture-counts`，處置閘仍照常通過。因此「fail-closed」與「有驗證」均不成立；REVISIT 只能事後統計失敗，不能保證單檔有效。現行流程是折入、記帳、問 disposal 閘，三處都沒有 fold 驗證掛點。  
severity: blocker  
blocking: 是；判準：核心留痕可被正常流程完整繞過，且無任何命令對「寫入成功」負責。  
引句:「寫入驗證(fail-closed,rc2):每條 `quote` 必須錨得回該輪凍結快照」  
file: `~/.claude/skills/lumos-design-loop/SKILL.md:27`  
file: `scripts/lumos:17197`

2. `carrier_findings_set` 被複製進 fold.json 後，再用同一檔中的集合驗同一檔中的 id，是自證循環；它沒有對到治理帳真正的 carrier `findings_set`。操作者可同時漏寫或改寫兩者而通過驗證。Spec 又明確排除 disposal 閘讀 fold，因此「id → carrier findings_set」這條鏈沒有權威錨點。  
severity: blocker  
blocking: 是；判準：核心一致性驗證只比較同一份人工輸入，無法偵測它與正式處置帳分歧。  
引句:「每個 `id` 必須 ∈ `carrier_findings_set`;同一席同一 quote 不得重複」  
file: `~/.claude/skills/lumos-design-loop/SKILL.md:28`  
file: `scripts/lumos:17128`

3. 「記已在做的判斷」不符合現行流程。第 5 步先判真假，第 6 步只折入「存活的真問題」，第 7 步才由一席 carrier 建立處置全集；被丟棄、降級或判為重複但未存活的原始 finding，現行並沒有逐席逐條分配 canonical id。若 fold 要覆蓋所有席報告，它新增的是一次完整 coding 工作；若只記存活項，算出的則是「存活缺陷席間重疊」，不是所有原始抓取的覆蓋率。Spec 沒有裁定母體。  
severity: blocker  
blocking: 是；判準：輸入母體未定義，兩種合理實作會產生不同指標，且其中一種推翻「沒有新增判斷／工作」的立案理由。  
引句:「把那個已經在做的判斷寫進一個檔,讓「被幾席抓到」從人手數變成機器數」  
file: `~/.claude/skills/lumos-design-loop/SKILL.md:26`  
file: `~/.claude/skills/lumos-design-loop/SKILL.md:27`

4. 把 JSON quote 包成 `引句:「…」` 餵 `_quote_rows` 對同型巢狀引號不安全。解析式 `「([^」]+)」` 遇到內容本身含 `「…」` 時，會在內層第一個 `」` 提前結束；只要被截出的前綴正規化後滿 10 字且存在快照，就會回報成功，後半段完全沒驗。`≥10` 只擋短引句，不擋這種前綴偽通過。異型巢狀 `『…』` 可用，但 spec 沒有限制 quote 禁止同型巢狀引號，也沒要求直接比對 JSON 字串。  
severity: major  
blocking: 是；判準：逐字引句是唯一 raw-finding 定位鍵，現設計存在可重現的假陽性，會讓錯誤映射通過。  
引句:「把單句包成一行 `引句:「…」` 當 rtext 餵入即可重用,零改動共用原語」  
file: `scripts/lumos:11445`  
file: `scripts/lumos:11453`

5. `--from-pitfalls` 的算術形狀接得上，但治理形狀沒有「照抄」。現行實作由工具從 claims 的 `source` 自動形成 finder，並由 `file:line` 自動形成 key；之後才把 `keys` append 到 `parsed`。fold 則同時人工提供 seat、quote、id、全集和完整性，沒有相當於 collector 的權威來源。故可複用的只有 `_capture_counts_from_finders([[id…],…])` 最後一段，不能據此推出收割、完整性與 provenance 也已解決。  
severity: major  
blocking: 是；判準：設計以錯誤的 prior-art 等價關係省略了必要的解析、對帳及錯誤處理合約。  
引句:「本案照同一形狀加 `--from-fold <rN-fold.json>`,每席=一個 finder、key=去重後的發現 id」  
file: `scripts/lumos:4841`  
file: `scripts/lumos:4856`

6. 多對多與缺席情況會直接改變數字，不能留到 D1 才處理。一席同一 quote 歸兩個 id，會產生兩個 distinct findings，各自得到一票；同一 id 在同席多條 quote 則被 `_capture_counts_from_finders` 席內去重，只算一票；跨席不同引句歸同 id 可正常算多席；clean 席若以空陣列存在，會增加 finder 數但不改 counts；漏掉整席則完全無警告，且與 clean 席不可區分。Spec 目前只禁止同席同 quote 重複，既不禁止 `(quote,id)` 重複，也不裁定一條 raw finding 是否能拆成多 id。  
severity: major  
blocking: 是；判準：合法輸入可在未違反 schema 下膨脹 distinct finding 數，或把漏席偽裝成無資料，破壞指標語意。  
引句:「一席一條發現被歸到多個 id、或一個 id 跨席引句不同段」  
file: `scripts/lumos:4436`  
file: `scripts/lumos:4442`

7. fold 與 dispatch 不是 seat-check 的重複功能，但目前會形成未對帳的第二套席位清單。seat-check 只檢查單份報告是否觸及 dispatch 的 materials、引句是否出界；它不檢查 fold 是否涵蓋全部 dispatch seat，也不檢查 seat 名稱、round、report、snapshot 的一一對應。fold schema 又只有 `<席名>`，沒有 report/snapshot 路徑或 dispatch identity，因此別名、漏席、重複席、拿錯輪快照都無法可靠辨認。正確邊界應是 fold 直接以 dispatch 為 roster/provenance 權威，而非另建自由文字 seat map。  
severity: major  
blocking: 是；判準：席位完整性及快照歸屬沒有單一真相來源，會使「被幾席抓到」的席數不可稽核。  
引句:「新留痕檔 `governance/review-reports/<編號>/rN-fold.json`」  
file: `scripts/lumos:12000`  
file: `~/.claude/skills/lumos-design-loop/SKILL.md:20`

8. 投入與唯一消費者不相稱：現行離線儀器只讀 `.canary-log.jsonl.capture_counts`，而且該數字已明定為 advisory；兩個需要 id→引句鏈的母案均已停。新方案卻要求每輪人工逐席逐條 coding，再手動把輸出貼回帳，新增成本恰落在最容易斷糧的編排者熱路徑。應先用一個真實輪量測製作時間及錯漏率，並要求有明確消費者承諾；否則先做離線試算器或抽樣研究，比永久改流程更符合現有價值。  
severity: major  
blocking: 否；判準：不必然導致錯誤實作，但在唯一消費者只是 advisory 覆蓋率儀器時，尚無足夠成本效益證據。  
引句:「若 10 輪後仍無人重開母案,本案的價值只剩「覆蓋率量測不斷炊」」  
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_席間覆蓋率離線量測.md:40`  
file: `scripts/lumos:4872`

最嚴重 severity: blocker；blocking 7 條。
tokens used
55,405