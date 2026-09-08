severity: blocker
# r1 外家否決席(codex)——棧別提問表態閘


## Findings

### F1｜blocking: 是｜判準：既有合法逃生路徑在新閘下沒有可一致實作的語意
severity: blocker

引句:「tier high 且 diff 命中棧 → 讀當前 sha 的 pass 記錄，逐問核對」

Spec 只定義 `pass --dispositions`，但既有判定把同 SHA 的 `passed`、`skipped` 都視為有效留痕；若新核對放在有效留痕判定後，`skip` 可完全繞過表態，放在之前則 `skip` 永遠因無 dispositions 被擋，破壞明文逃生合約。  
file: `scripts/lumos:20637` 至 `scripts/lumos:20644` 把 `rec_status in ("passed", "skipped")` 直接放行；file: `scripts/hooks/pre-push:209` 至 `scripts/hooks/pre-push:213` 仍把 `code-loop skip --note` 列為高風險推送的正式第二條路。

### F2｜blocking: 是｜判準：照流程操作會本機放行、CI 卻必然讀不到剛寫的表態
severity: blocker

引句:「形狀好就寫進留痕記錄的 `dispositions` 欄與治理帳事件」

`pass` 發生在已提交的 HEAD 上，marker 又被 gitignore；若使用者照 spec 直接 push 而未另 commit 治理帳，pre-push 能讀本機 marker，但 CI 的乾淨 checkout 只能讀舊版 tracked ledger，沒有本次 dispositions。  
file: `scripts/lumos:20122` 至 `scripts/lumos:20139` 明載 CI 沒 marker 時退讀 `docs/.governance-log.jsonl`；file: `governance/.gitignore:10` 排除 `code-loop/`，而 file: `.github/workflows/ci.yml:48` 會在乾淨 checkout 重跑 check，spec 未把「pass 後提交治理帳再 push」納入流程或驗收。

### F3｜blocking: 是｜判準：閘驗證的檔案、Issue、測試設定可能不是實際被推送的 commit
severity: major

引句:「檔案存在且行號在範圍內（借 refcheck 的存在性核對，不驗內容）」

pre-push 可逐 ref 檢查一個非目前 HEAD 的 `_lsha`，但 `_refcheck_scan`、Issue 路徑與測試 discovery 都從目前工作樹讀檔，因此能用只存在於另一個 checkout 版本的證據替被推送 commit 過關。  
file: `scripts/hooks/pre-push:165` 至 `scripts/hooks/pre-push:203` 逐 ref 傳 `--at-sha "$_lsha"`；file: `scripts/lumos:14682`、`scripts/lumos:14692` 直接讀 `repo_root / token`，file: `scripts/lumos:3608` 至 `scripts/lumos:3631` 也直接走訪工作樹，沒有按 `at_sha` 讀 git tree。

### F4｜blocking: 是｜判準：多平台 repo 的合法測試證據會被誤判不存在
severity: major

引句:「用該 repo 的 test profile 跑 `discover_test_methods`，名字要在集合裡」

Spec 指名單次 `discover_test_methods`，它只載入一個 legacy profile；現行多平台合約語意必須先 `load_platforms`，再依平台 root/profile 分別 discovery，否則非預設平台的 `test:<名>` 會假紅。  
file: `scripts/lumos:3597` 至 `scripts/lumos:3603` 顯示直接呼叫只取 `load_test_profile`；file: `scripts/lumos:3358` 至 `scripts/lumos:3409` 定義多平台設定，file: `scripts/lumos:7893` 至 `scripts/lumos:7918` 才是既有正確的逐平台索引路徑。

### F5｜blocking: 是｜判準：問題表調序後，舊答案能被套到另一道問題並通過
severity: major

引句:「鍵對不上命中的問題（少的算缺、多的忽略）」

S3 只要求鍵集合吻合，寫側又只驗 `question` 非空，沒有要求該鍵的 `question` 等於目前問題原文；表的順序一改，`kt-1` 可保留舊問題與舊證據，check 卻把它當成新的第一問已處置。  
file: `scripts/lumos:14763` 至 `scripts/lumos:14810` 顯示序號完全來自可編輯 list 順序；spec 自己宣稱跨版本統計依原文，卻沒有任何驗收條款釘住「鍵、當前原文、存入原文」三者一致。

### F6｜blocking: 是｜判準：同 SHA 的並行 pass 可讓閘讀到非決定性的最後寫入結果
severity: major

引句:「形狀壞 rc2 不寫帳；形狀好就寫進留痕記錄」

同分支兩個 agent 對同一 SHA 同時 pass 時，marker 以普通 `write_text` 覆寫且沒有 lock/atomic replace；兩份不同 dispositions 誰最後完成就取誰，check 可能偶發放行或阻擋。  
file: `scripts/lumos:20170` 至 `scripts/lumos:20178` 直接覆寫固定分支檔；file: `scripts/lumos:20146` 至 `scripts/lumos:20167` 的 CI fallback 同樣只取該分支最後一筆事件，spec 沒有唯一性、合併或衝突拒絕規則。

## 逐節覆核

- Frontmatter／summary：已讀；除 F1–F5 所列合約與執行假設外，無 finding。
- 現況查證：已讀，無 finding；指定 reference 的「建議／工具不驗」與實碼相符。
- 表態的形狀：已讀；F5。
- 閘放哪裡：已讀；F1、F2、F3。
- 錨點怎麼驗：已讀；F3、F4。
- 副產品：已讀，無額外 finding。
- 驗收條款：已讀；S2/S3 未覆蓋 F1、F2、F3、F4、F5，亦未含並行測試 F6。
- 實務隱患—併發：F6。
- 實務隱患—效能：無；問題數量小，若按平台建立一次方法集合，掃描成本有界。
- 實務隱患—資源：無；設計只做短生命週期檔案與 git 讀取，未新增長駐行程、連線或鎖。
- 實務隱患—回滾／不可逆：無；新增欄位與帳列可由後續 commit 還原，未涉及外部不可逆操作。
- 對外送出／金流：已讀，無 finding。
- 既有 pass 記錄：已讀；F1、F2。
- 刻意不做：已讀，無 finding。
- REVISIT：已讀，無 finding。

最嚴重 severity：blocker；blocking 共 6 條。
