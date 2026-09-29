severity: major

前置欄位與摘要：已讀,無 finding。
現況：已讀,無 finding。
設計：已讀；F1、F2。
驗收條款：已讀；S3 會把 F2 的歷史改寫固化成測試要求。
回退：已讀,無 finding。
實務隱患：已讀；F3，且逐類核對見下。
撤除條件：已讀,無 finding。
誠實界線：已讀,無 finding。
審計修正紀錄：已讀,無 finding。

## F1 五問沒有接上 panel 的席位分流，照方案只改固定範本會灑給所有席
severity: major
blocking: 是 — spec 承諾只交給正確性席，但既有可執行派工說明沒有從固定 §3 prompt 移除其他席正確性段的步驟，照字面改檔會做出相反行為。
引句:「所以 panel 多席時它跟著第 1 點走:哪一席拿到正確性鏡頭就拿到這五問,不會整段複製給每一席。」
file: `skills/lumos-design-loop/templates.md:129` §3 的派工圍欄把正確性寫成固定第 1 點，沒有席位或鏡頭 placeholder。
file: `skills/lumos-design-loop/templates.md:291` §7.7 規定多席是在既有鏡頭之外加立場與姿態，沒有規定非正確性席刪除 §3 第 1 點。
file: `skills/lumos-code-loop/SKILL.md:25` 步驟 2 把 Codex 派工單源指到 §3，下一行只列出 high 的不同席名，沒有將 §3 第 1 點按席位裁切的組裝規則。
具體失敗場景：high 輪派正確性、併發資源、邊界輸入、合約圖譜四席時，編排者依單源複製 §3，再依 §7.7 加各席姿態；四席都收到五個資料狀態問句。資源席與回滾席被迫重做正確性席的題目，原本要靠不同鏡頭取得的獨立覆蓋被稀釋，且直接違反「不會整段複製給每一席」的設計裁定。設計必須在實際派工單源中定義每席如何選取或移除第 1 點，並用 high panel 的派工成品驗收分流。

## F2 把新問句補進歷史區會竄改舊輪次的回放依據
severity: major
blocking: 是 — reference 第二處 framing 明確位於只供舊帳回放的歷史原文；照 spec 同步修改會讓舊審查看起來用過當時不存在的鏡頭。
引句:「代碼審 reference 的 refute framing 兩處各自濃縮了正確性四問,補上五個新子題標頭。」
file: `skills/lumos-code-loop/reference.md:364` 第二份 framing 所在章標明「歷史與停用」，用途只限舊帳回放，不是現行規則。
file: `skills/lumos-code-loop/reference.md:369` 該章再次聲明整段是已停用或已撤回內容的純歷史原文。
file: `skills/lumos-code-loop/reference.md:402` spec 所稱第二處 refute framing 就在這個歷史區內。
具體失敗場景：回放 2026-09-29 以前的一輪 code-loop，調查為何當時漏掉時區或部分寫入缺陷時，歷史段經本案修改後會宣稱舊 reviewer 已收到五問；審計者會把「當時根本沒派這個鏡頭」誤判成「派了但 reviewer 沒抓到」。S3 又要求三處都出現指路或標頭，會把這筆假歷史鎖成綠燈。現行濃縮段可以更新，歷史段必須保持當時原文；S3 也只能驗現行入口，不得要求歷史段同步。

## F3 新增測試實際位於 pre-push 與 CI 的擋推鏈，風險分類把守衛面判成已排除
severity: major
blocking: 是 — spec 明說不碰推送閘且不擋推送，但其指定的 test_lumos.py 失敗會被既有 pre-push 與 CI 直接判紅，這是實際新增守衛面合約。
引句:「新增的漂移守衛只驗範本文字在不在,不擋任何人的推送」
file: `scripts/test_lumos.py:31434` 測試執行器不帶參數會跑全套，新三支測試會進全套。
file: `scripts/test_lumos.py:31613` 測試丟出一般例外會累加 FAIL；只有缺來源產物時拋 _SrcOnly 才記 skip。
file: `scripts/hooks/pre-push:423` 來源 repo 具備 skills 與 test_lumos.py 時，pre-push 會啟動這套測試。
file: `scripts/hooks/pre-push:515` 任一分片有紅就輸出「擋下」並令推送失敗。
file: `.github/workflows/ci.yml:58` CI 也把 test_lumos.py 分片執行，任一工作失敗會令該步失敗。
具體失敗場景：後續維護者刪除或改名「衍生資料」標頭，功能碼與審查流程其餘部分都可運作，但 t_data_state_lens_in_code_template 轉紅；在本來源 repo 的下一次非純文件推送中，全套測試經 pre-push 直接擋下，CI 亦失敗。這正是推送守衛，不是單純觀測。設計必須把本案列為守衛面變更，對擋推範圍、誤報與逃生路徑作風險處置；若真的要求不擋推，就不能把斷言放進會以 FAIL 阻斷的測試套件。

實務隱患逐類核對：
- 金流：不改付款執行碼，已排除。
- 對外送出：不新增實際外呼；只擴寫 reviewer 問句，執行副作用已排除。
- 不可逆：程式碼可由版本控制回退，但 F2 會污染舊帳回放語意；在治理判讀層未排除。
- 守衛面：F3 證實命中；新斷言會由既有 pre-push 與 CI 擋推。
- 注意力稀釋：F1 證實現有派工單源缺少按席裁切，新題會跨席重複。

最嚴重 severity: major；blocking 共 3 條。
