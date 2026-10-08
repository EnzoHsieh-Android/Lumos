severity: major

## Finding 1 — 登記與停止狀態無法跨工作樹形成單一事實

severity: major

blocking: 是

引句:「每案首輪與收尾時讀此表；編排者用既有 intake 和五格表記結果，不新增候選表、領號器或跨工作樹鎖。」

引句:「每輪開始與交接接手時先讀本計劃停止狀態；已停止就不再執行試行步驟。」

具體場景：

1. 會談 A、B 位於不同 worktree，同時讀到第 2 格「待登記」，且都看不到對方尚未提交的 intake。
2. 兩者各自接手不同的合格工作，以不同 loop id 登記並派出首輪。
3. 現有工具只按完整 loop id 查帳；不同 id 不會檢查是否競逐同一試行格、同一工作或同一樣本序號。  
   file: `scripts/lumos:10698`  
   file: `scripts/lumos:10714`
4. 事後無論保留哪案，都會違反 S1：兩案都已依首輪 intake 完成登記，而已登記案不能事後換掉。
5. 同樣地，若 A 在自己的 worktree 標記停止，B 下一輪讀到的是自己分支上的舊計劃，仍可繼續試行。安裝版 skill 已存在不同步的實例，證明「讀本地副本」不能當全域停止訊號。  
   file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:22`

現行 reference 也明說這是人工試行、沒有新增機械閘，因此沒有其他守衛補上此競速。  
file: `skills/lumos-code-loop/reference.md:124`

最小修正：

在首輪派工前增加一個所有 worktree 都能看到的唯一授權紀錄，至少綁定 `{序號、工作、loop id、基準提交、編排者、授權時間}`；停止紀錄也寫入同一權威來源並優先於登記。若不建鎖，則要求人明確核發不可重複的登記 token，intake 必須引用該 token；拿不到或核對不到時只走普通 code-loop。不要讓各 worktree 的計劃副本自行決定領號或停止。

## Finding 2 — 「首次派工時間」在派工前寫入，且分散於兩檔，無法可靠代表實際開始

severity: major

blocking: 是

引句:「首輪 intake 同時記接手與首次派工時間；」

引句:「時間落點：首次派工前在本計劃該案逐案紀錄寫帶時區的開始時間；暫停、恢復、最終問閘或中止時當場追加事件時間。」

具體場景：

1. 10:00 先在計劃寫「開始時間」。
2. 10:02 寫 intake，之後因席位啟動失敗或程序中斷，直到 10:25 才真正派出第一席；也可能完全沒有派出。
3. 總耗時定義是「首次派工到問閘／中止」，但計劃中的時間是派工前時間，intake 又另存一個首次派工時間。兩值沒有共同事件 id，也沒有規則指定衝突時信哪一個。
4. 若在兩次寫入間中斷，會留下「有開始事件但無 intake」，或「已有登記但從未派工」的半完成狀態；目前只規定缺值填未知，未規定如何辨識、恢復或結算這類狀態。
5. `canary record --intake` 只保存 intake 的路徑與雜湊，沒有綁定計劃中的時間事件或真實派工成功。  
   file: `scripts/lumos:8431`  
   file: `scripts/lumos:8455`

第 1 案已實際發生「精確首派時刻未打點、總耗時未知」，所以這不是純假設；新版雖要求先記事，仍未把「準備派工」與「派工成功」分開。  
file: `governance/review-reports/review-repair-pilot-decouple-slim/r1-snapshot.md:125`

最小修正：

明定三個不同事件：

- `claimed_at`：登記完成，可在派工前寫，不作為耗時起點。
- `first_dispatch_succeeded_at`：席位啟動成功後立即追加，這才是總耗時唯一的起點。
- `ended_at`：正式問閘或中止。

計劃與 intake 以同一事件 id 互相引用；只有一邊存在、時間倒序或派工沒有成功憑證時，該項固定記未知，不從較早的準備時間推算。若已登記但從未成功派工，另標 `aborted-before-dispatch`，仍可依 S1 占名額，但不能產生虛假的審查耗時。

## 已讀、無 finding

- frontmatter、試行前提、PRIOR-ART、總體 RETIRE-IF。
- S2：根因合併、壞例／好例、失敗路徑與未驗處置。
- S3：同例前後版來源分類及不改嚴重度。
- S4：原席驗原問題、新席掃差異、完整凍結材料、三輪上限。
- S5 除上述時間事件外：intake 入帳後不改、缺值未知、escape 與 14 日共同觀測窗。
- 收斂性診斷、多入口資料表、落點與退場條件。
- 改道資格與 pending design gate：目前 `review-repair-pilot-decouple-slim` 確為零筆記帳，`loop status --disposal` 回傳 rc=1；圖譜也正確維持 pending。  
  file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:16`  
  file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:24`
- 歷史第 1 案四輪 FAIL、樣本外儀器 r3 FAIL／例外 r4 PASS 的分離，沒有用後者覆蓋前者。  
  file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:28`
- 效果未知、歷史對照、根因去重、14 日曝光期及不得推導因果。
- 實務隱患。
- 回退保留 intake、證據與原 code-loop 判定的原則；除 Finding 1 的跨 worktree 停止可見性外，未見其他問題。
- 審計修正紀錄。
- 第 1 案逐案時序、例外第 4 輪授權、紅綠證據、過大審材限制及最終 FAIL。

最高等級：major；blocking count: 2
