# code-delguard r1-spec(sonnet spec-conformance 對答案席,無餌)
條款對照:S1 抽取/兩檔信心/三件套/cap+top/型別排序/落點 d1/fail-open/deadline/stdout/quotePath/誤報帳零寫入/效能合併計時=做了;合約候選五條全有測試釘(第5條隱式)。
縮水 findings:
## C1 S1 邊界輸入四項(initial commit/binary/CJK path/標頭行)無斷言 ## C2 檔案搬移 -M 無測試 ## C3 escaping metachar 無 fixture ## C4 partial hunk stage 無測試 ## C5 S2 縮排重排會誤判純連結(潛在功能落差:notesmd-cli 重排縮排→誤發假同步嫌疑)+無測試 引句:「若一次 diff 只重新縮排既有的 verified_by/related 列表項」 ## C6 S2 觸發合取 negative 分支無測試
## C7(誠實性)Verification 節點數字對 b478a8e 已過期:實測 47 條(非43)/全量 2480(非2463)——delguard 要防的失守形狀自身重演
多做:lockfile 排除(合理)/timeout 參數(合理)。偏離句誠實度:三點全核實準確。
max severity: medium(對映 minor-major 間,編排者採 major 級處置縮水 C5/C7)
