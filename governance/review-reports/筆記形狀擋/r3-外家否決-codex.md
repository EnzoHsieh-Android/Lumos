severity: major

## F1 喚醒舊引用重新阻擋了明定不追的舊帳
severity: major
blocking: 是 —— 不改，新增程式檔會因上線前、未改動的舊筆記而被擋，違反既有裁定並造成誤擋。
引句:「掃全部筆記裡指向這些新路徑、沒釘版本的行號引用,有就擋」——只能引 spec 原文。
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:33` + 有效決策 d2 明定舊筆記只在有人修改該篇時處理，不做全庫回頭清理。

1. 具體輸入：note-shape 上線前，舊筆記已有 `scripts/future_job.py:12`；當時路徑不存在，因此不是可攔的程式引用。
2. 上線後只新增 `scripts/future_job.py`，完全不改該筆記。
3. S12 要掃全部筆記並擋下；同一份 spec 的 S1 卻宣告未改動舊行不應擋，指定 Issue 的 d2 也要求只有改到該篇才處理。
4. 結果是新增程式碼被歷史舊帳攔住。要同時封住兩步繞法與遵守 d2，喚醒範圍必須限於上線後才寫入的引用，或先正式翻案 d2。

## F2 喚醒條件漏掉既有檔案轉成程式檔
severity: major
blocking: 是 —— 不改，未釘版本的舊引用可在檔案改成可執行程式時直接存活，形成穩定繞過。
引句:「若範圍內新增了程式檔或測試檔,而任何筆記裡有指向它、沒釘版本的行號引用,則應擋下」——只能引 spec 原文。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:25` + 被借用的既有閘明確把捷徑轉一般檔、無副檔名檔新增 shebang 等 `T/M` 變化視為「這次才變成程式檔」。
file: `scripts/lumos:22385` + `_nodehome_code_kind` 只給路徑候選類型；是否因 shebang 成為程式檔仍須讀前後版本內容判斷。
file: `scripts/lumos:22625` + `_nodehome_changes` 保留 `A/M/T/R` 狀態，現有設計能區分新增路徑與既有路徑內容或型態改變。

1. 具體輸入：base 已追蹤無副檔名的 `scripts/runner`，首行不是 shebang；舊筆記已有 `scripts/runner:8`。
2. 後續提交只替 `scripts/runner` 加上 `#!/usr/bin/env python3`。Git 狀態是 `M`，檔案路徑不是新增，但它從這次起成為程式檔。
3. 筆記行沒有改，S1 不查；S12 字面只喚醒「新增了程式檔」的路徑，沒有要求比較前後版本的程式檔集合。
4. 結果是新形成的活動行號引用未被擋下。喚醒條件必須涵蓋「原本不是、終點版本才是程式／測試檔」的 `M/T/R` 路徑，並有對應條款案例。

## F3 規範只改一個範例，官方入口仍教出必被擋的寫法
severity: major
blocking: 是 —— 不改，使用者照官方 skill 指令寫筆記會被新閘穩定攔下，規範與執行器互相否決。
引句:「不然新人照範例寫的第一句就被擋」——只能引 spec 原文。
file: `skills/lumos-project-notes/commands/INDEX.md:43` + 三條核心規矩仍指示：程式碼推得出的內容若要寫，標「以程式碼為準」並加查詢指令。
file: `skills/lumos-project-notes/reference.md:425` + Systems 寫法仍指示現況描述標「以程式碼為準」。

1. spec 只點名修改紀律範本與 `reference.md` 的 FACT 表格範例。
2. 實作者照字面完成後，上述兩處可操作指令仍然存在；它們不是歷史敘述，而是新人入口與 Systems 寫法規則。
3. 具體輸入：使用者照 INDEX 寫入 `FACT:[以程式碼為準] 門檻 180 秒；查:…`，沒有五種來源標記。
4. S3 必定擋下這行。S10 目前只驗表格範例，抓不到這兩個殘留指令；規範掃除範圍與測試都必須擴大。

## F4 加鎖雖已移出，本案的有效決策與後續計劃仍要求加鎖
severity: major
blocking: 是 —— 不改，實作者面對兩組相反的權威指示，可能再次修改所有閘共用寫入器，重引第一輪已否決的高爆炸半徑改動。
引句:「它跟本計劃要擋的東西無關,已移到」——只能引 spec 原文。
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:63` + 仍有效的結構化決策 d7 明寫治理帳加鎖由第一層計劃先做。
file: `docs/lumos-toolchain-knowledge/Projects/筆記不存程式碼推得出的事_計劃.md:23` + 後續計劃仍宣告加鎖已移到本計劃。
file: `docs/lumos-toolchain-knowledge/Projects/筆記不存程式碼推得出的事_計劃.md:65` + 第二層做法仍直接要求修改 `_gate_event` 與 `_codeloop_gov_log` 取得同一把鎖。

1. 本 spec 說加鎖完全移到另一篇 Issue，且本計劃沿用無鎖寫入器。
2. 指定 Issue 的有效決策和指定後續計劃仍把同一工作交給本計劃；後續計劃正文還保留具體實作命令。
3. 實作者若服從有效決策，會把第一輪因影響所有閘而移出的改動重新做進來；若服從本 spec，則留下未履行的有效決策。
4. 移出動作必須同步翻案 d7，並從第二層計劃移除或明確標成已移出的加鎖步驟。

## F5 回退只保留一版空殼，下一版仍會卡死未手改的消費專案
severity: major
blocking: 是 —— 不改，中央工具下一版刪除子指令後，仍保留 CI 呼叫的消費專案會持續紅燈。
引句:「指令直接刪掉會讓它們的 CI 每次都因為找不到子指令而紅;下一個版本再刪」——只能引 spec 原文。
file: `scripts/lumos:16888` + vendored 工具清單只包含 CLI、hooks 與範本，不包含消費專案的 workflow。
file: `scripts/lumos:17158` + `lumos update` 只複製上述固定清單，無法替消費專案移除 CI 裡的 note-shape 呼叫。

1. 具體輸入：消費專案依本 spec 手動在 CI 加入 `note-shape --diff`，之後不再人工編輯 workflow。
2. 回退版本 N 把指令改成回 0 的空殼；版本 N+1 按 spec 刪除指令。
3. 該專案執行 `lumos update` 升到 N+1 時，workflow 不會被更新；下一次 CI 呼叫不存在的子指令並失敗。
4. 消費專案若跳過版本 N 直接升級也會立刻中招。刪除空殼必須綁定可驗證的退場條件；不能只用「下一個版本」當條件。

〈開頭、依據、PRIOR-ART、RETIRE-IF〉已讀,無 finding。

〈範圍與行〉已讀,無 finding。

〈消費專案的 CI〉已讀,無 finding。

〈誠實界線〉已讀,無 finding。

〈審計修正紀錄〉已讀,無 finding。

〈交叉引用〉已讀,所有目標存在,無 finding。

〈Systems/每支檔有家〉已讀；除 F2 的喚醒語意漏接外，預設參數維持既有上線點、合併與抽取行為，無其他 finding。

〈Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋〉已讀；F1、F4 外無其他 finding。

〈Projects/筆記不存程式碼推得出的事_計劃〉已讀；F4 外無其他 finding。

實務隱患逐類核對：

- 守衛面：有；F1 會誤擋舊帳，F2 會放過程式檔型態轉換。
- 規範與版本相容：有；F3、F5 分別造成官方寫法必紅與回退後 CI 卡死。
- 狀態同步／跨計劃所有權：有；F4 的有效決策與兩份計劃互相衝突。
- 資源併發：有；無鎖寫入問題已移到獨立 Issue，本稿降低寫入頻率，除 F4 的所有權殘留外無新增 finding。
- 效能／資源：會掃全圖舊引用並由 doctor 重放遠端歷史；現有審材不足以證成 blocking 失敗，無 finding。
- 對外送出：無；CI fetch 只取得遠端 Git 物件，沒有新增把筆記內容送往第三方判定服務的路徑。
- 不可逆：無；檢查與設定可撤回，持久相容性問題已列 F5。
- 金流、認證、PII、快取、資料庫遷移：無；功能不觸及這些資料或流程。

總結:最嚴重 severity 是 major、blocking 共 5 條。