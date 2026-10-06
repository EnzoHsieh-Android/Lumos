severity: minor

## F1 — 測試未鎖住合法 surrogateescape 路徑

severity: minor  
blocking: 否  
引句:「不把 surrogateescape 的可編碼路徑一律拒絕」  
file: `scripts/test_lumos.py:34017`

輸入 → POSIX 上的 `materials: ["\udc80"]`，其可還原為原始檔名字節 `0x80`。  
錯誤 → 測試只有不可編碼的 `\ud800`、`\udc00` 反例，沒有可編碼 surrogateescape 正例；若日後改成「拒絕所有 surrogate」，三個新增測試仍會全綠，卻違反計劃明定的相容性。現行實作本身正確。

可運行證據 → 本席記憶體探針得到：

- `\ud800` → `UnicodeEncodeError`
- `\udc00` → `UnicodeEncodeError`
- `\udc80` → `b'\x80'`
- `\udcff` → `b'\xff'`

未執行突變版；「拒絕全部 surrogate 仍通過現有案例」是依測試資料集合直接推論。建議增加至少一個 `\udc80` 正例。

## F2 — 計劃節點留下已過期的實作狀態

severity: minor  
blocking: 否  
引句:「這些是既有裁定的測試背書修正，生產函式仍待正式設計審放行才修改。」  
file: `docs/lumos-toolchain-knowledge/Projects/異常派工單回報輸入錯誤_計劃.md:74`

輸入 → 下一個 session 讀計劃節點判斷功能是否已落地。  
錯誤 → 節點仍說生產函式「待修改」，但 `scripts/lumos:23297`–`23310` 已加入完整驗證；同段還保存席次、finding ID 與報告處置過程，違反本 repo「過程紀錄留在 git／審查卷證，不寫進圖譜」的規則。

可運行證據 → `nl -ba` 同時顯示上述相反狀態；`lumos lint` 為 0 問題，表示這是 lint 抓不到的語意漂移。應刪除或明確改成不會被讀成現況的歷史指標。

## 四條驗收比對

- S1：通過。非物件 dispatch、錯形態 materials 皆進 `ValueError`→rc2，stderr 帶欄位，無觀測 JSON。
- S2：通過。所有項目先完成型別、空值、NUL、`os.fsencode` 驗證，之後才從 `scripts/lumos:23324` 讀材料；不依賴 `assert`，普通與 `-O` 一致。
- S3：通過。缺省、null、空清單維持 vacuous rc0；中文含空白路徑正常。
- S4：通過。合法漏報／越界仍 rc0，ledger 欄位與 append 行為未改。

重複 JSON 名稱仍直接使用 Python `json.loads` 的預設結果，未新增唯一鍵政策。未知 metadata 仍可通過。

## 固定圖譜逐條

- `Systems/design-loop`：計劃為 `.md` 且 S1–S4 均綁測試；既有處置閘 invariant 未受影響。
- `Systems/lumos-cli-read`：search 過濾 invariant 未受影響。
- `Systems/bound-tests-gate`：固定席綁測試執行語意未受影響。
- `Systems/guard-kill`：兩條 rc／JSON 純度 invariant 未受影響。
- `Systems/授權與歸屬`：vendored 白名單與檔頭未改。
- `Systems/測試假綠形態`：真 CLI 與 AST 讀序測試有現場前置斷言；但有 F1 的正向相容性缺口。
- `Systems/lumos-cli-lifecycle`：re-inject byte-equal invariant 未受影響。

資料狀態五問：新舊 dispatch 可互讀；壞輸入不半寫 ledger；衍生 ledger 格式不變；無時間狀態；無不可逆動作。

## 已讀與驗證

- 完整逐 hunk：`r1-source.patch` 180 行。
- 完整逐 hunk：`r1-graph.patch` 233 行。
- `r1-snapshot.patch` 4597 行僅做完整指紋：`6486f72075f68342536b486f3eea14dbaaf51b1223306609946d7347f930`。
- 固定 HEAD：`fd255ce01f23460a622b17312dbdf5448d9cbf67`。
- 定點程式上下文共 412 行。
- 六個 graph patch 節點 `lumos lint` 均為 0 問題。
- 未讀其他席報告、未讀歷史設計報告、未跑全套、未改任何檔案或帳本。
- 角色依使用者指定的 standard 通才席執行；未宣稱 CLI 自動附加角色卡。

最高等級：minor。blocking 數：0。