severity: major

# mp-r3 繞過席(sonnet)——只掃 blocking 級

圖譜鏡頭(LUMOS-SPEC 節點)我只當背景讀;派工尾端沒有附上額外的合約/事故節點,所以沒有「固定席逐條判」可寫。實驗全在 mktemp 臨時 repo 做,用 importlib 唯讀載入 `scripts/lumos` 並關掉位元碼,沒有動 repo 任何檔。

## F1 退回主線修補的「還原提交」借舊 pass 過關:新條件 3、4 都擋不住
severity: major
blocking: 是 — 沒審過的程式改動(退掉主線安全修補的提交)進了主線,而且 spec 自己宣稱這條路被關上了,該宣稱被實測推翻。

誰:持有分支寫入權的開發者,或被注入指令的 AI agent。
從哪:從已經包含主線頂端 P1 的分支上,加一個 revert 提交 R,把 P1 剛合進來的修補(例如 guard 的安全修正)改回舊版,內容剛好等於主線較早的某個「已審過、有 pass 記錄」的提交 X。X 在 R 的第一母鏈 20 個提交以內(本 repo 的 #28 範圍裡,主線 10-05 的記錄 eeaa6162 就在 5dbb85e0 往回第 17 個,真實可用)。
做什麼:開 PR,合併提交 M = (P1, R)。條件 1 到 4 逐一成立:M 恰好兩個母;第一個母 P1 等於推送範圍起點;P1 是 R 的祖先;`git diff --no-renames --name-only R M` 為空。讀帳讀 R 那棵樹的帳本,找到 head_sha=X 的 pass,再呼叫 `_codeloop_record_valid_ex(紀錄, R, ...)`。這支函式只比 X 與 R 兩端點的樹差異,不看中間提交,所以「改了又改回去」的 R 判成有效。
結果:R 這個從沒被任何審查看過的還原提交整段進了主線,主線的修補被退掉,CI 的高風險閘放行。

實驗(臨時 repo,主線依序是 base → X(舊 guard)→ 帳本記 X pass → 修補 P1 → 分支 R 把 guard.py 改回 X 的內容 → `git merge --no-ff`):

```
cond3: yes            # git merge-base --is-ancestor P1 R
cond4 diff: 0         # git diff --no-renames --name-only R M | wc -l
window: 1             # git rev-list --first-parent -n 20 R | grep -c X
(True, '祖先 1f842e83+簿記豁免(其後 1 檔皆簿記)', False)   # _codeloop_record_valid_ex(repo, X, R)
guard.py | 2 +-       # git diff --stat P1 M:主線的修補被退掉
```

(第一次單獨驗 `_codeloop_record_valid_ex` 也回 `(True, '祖先 20a0033e+簿記豁免(其後 0 檔皆簿記)', False)`。)

spec 的宣稱被推翻:
引句:「要退掉主線的東西只能在分支上另做提交,那個提交會被審」
引句:「主線歷史裡舊合併請求的 pass 之後都動過程式,不會被認」
前者錯在:「另做的提交會被審」只在記錄指向它之後才成立;這裡記錄指向更早的 X,端點比對把還原提交免審。後者錯在:pass 之後動過程式、但最後又改回來的情形,端點樹差異是空的,照樣被認。
file: `scripts/lumos:46538`(`_codeloop_record_valid_ex` 的 `git diff ... rec_sha marker_sha` 只看兩端點)
file: `scripts/lumos:46574`(整批檔都是簿記就判有效)

這是舊判法本來的性質,但舊規則只讀「目標分支最後一筆」記錄,新規則改成「任何分支、20 個提交內、由近到遠逐筆試」,可選的 X 變多,spec 又把「退掉主線的東西」列成已被擋住。修法方向:要求索引裡的記錄 sha 必須在「第一母之外」的那一段(即 `P1..R` 範圍內的提交),或要求 R 與 X 之間的每個提交都不改非簿記檔(逐提交而非端點);只認 P1 之後的紀錄就能同時擋掉這條。

## F2 推送前掛鉤已先改寫新分支首推的起點,spec 的「原始起點」定義與「全零不認」在掛鉤路徑上對不上
severity: minor
blocking: 否 — 沒有造成未審程式進主線;只是掛鉤與 CI 對同一種形狀判得不同,測試案例也可能測不到。

誰:推新分支(首推)的開發者。
從哪:`pp_block_range_for` 在新分支首推(遠端舊值全零、refs/heads/*)時,先呼叫 `push-range` 把範圍起點換成跟主線的分岔點,再把 `起點..終點` 傳給 `code-loop check`。
做什麼:合併提交 M=(主線頂端, 已審分支)首推到新分支,掛鉤傳進來的起點已是主線頂端,等於第一個母,條件 2 成立,放行。CI 只在 main 跑(`branches: [main]`),看到的才是真全零,會判「不認」。
結果:掛鉤放行、CI 不認的分歧只在非 main 的新分支;主線上不會因此放進未審碼,但 spec 的這句與驗收條款 S1「起點全零 應 照舊擋」在掛鉤路徑不可達。
引句:「CI 是 push 事件的前一版,推送前掛鉤是遠端那個分支原本的提交」
file: `scripts/hooks/pre-push:53`(`pp_block_range_for` 先改寫起點)
file: `.github/workflows/ci.yml:5`(`push: branches: [main]`)

## F3 條件 4 的指令沒帶 `-z`,中文簿記路徑會被引號包起來而判成非簿記(多擋,不是繞過)
severity: minor
blocking: 否 — 錯誤方向是多擋,不會放進未審程式。

誰:合併時在簿記資料夾(本 repo 有大量 `governance/replay/code-<中文>/`)有差異的合併者。
從哪:spec 條件 4 寫的是 `git diff --no-renames --name-only 第二個母 目標`,沒有 `-z`,也沒有模式(`--raw`)。
做什麼:實測 `core.quotepath` 預設下輸出 `"governance/replay/code-\344\270\255\346\226\207/verdict.json"`,開頭是引號,`startswith("governance/replay/")` 為 False(臨時 repo 實跑,印出 False)。
結果:合法的簿記差異被當成程式,正常流程被擋;另外 spec 又要求「含簿記資料夾裡的程式檔照算程式」,那一步要模式與首行,光靠 `--name-only` 做不到,實作者只能照 `_codeloop_record_valid_ex` 的 `--raw -z` 寫;spec 應明講用同一支分類函式,避免實作時各寫一套。
引句:「`git diff --no-renames --name-only 第二個母 目標` 裡沒有非簿記檔」
file: `scripts/lumos:46564`(既有判法註解:★-z★ 預設會把中文檔名加引號)

## 查過沒有繞法

- 未審分支擺第一個母、主線頂端擺第二個母的假合併:第一個母不等於起點,條件 2 擋。
  引句:「第一個母等於推送範圍原始起點。」
- 合併時挑分支舊版檔退掉主線後來的修補、改名偵測藏刪檔:條件 3(第一母是第二母祖先)加條件 4(`--no-renames`)擋住。我實測最近五次合併 b0b48b7b、d0b24391、b4637da0、c150ac43、c4f2b0cf 全是「第一母為第二母祖先、`git diff --no-renames --name-only 第二母 合併` 為 0 檔」,所以不會誤擋。
  引句:「最近五次合併(b0b48b7b、d0b24391、b4637da0、c150ac43、c4f2b0cf)全部是這個形狀」
- #28(範圍 d0b24391..b0b48b7b,母 d0b24391、5dbb85e0):條件 1 到 4 成立,afb7115c 在 5dbb85e0 的第一母鏈第 2 個,帳本讀 5dbb85e0 那棵樹有 branch=cap-retro 的 passed 記錄,正常流程不會被擋。
  引句:「#28 的合併提交 b0b48b7b:第一個母 d0b24391 就是那次 CI 的推送範圍起點」
- 在合併提交 M 裡手寫帳本行:帳本讀第二個母的樹,M 新增的行不算。
  引句:「合併提交本身新增的帳本行不算數」
- 第二個母的帳本手寫一筆「指向自己」:提交不可能把自己的雜湊寫進自己的檔案;能做的是指向自己的父提交(先推未審碼 C,再推只加一行帳本的 L),這條可行,但屬帳本沒簽章的既有天花板,舊規則下寫成 branch=main 一樣成立,spec 已明講,不當新 finding。
  引句:「帳本是沒簽章的純文字,在分支上手寫一筆仍能偽造——這在現行規則下寫成 branch=main 也成立,不是新洞」
- 第一母鏈 20 個提交的索引被別的分支記錄撞到:撞到的記錄一律還要過 `_codeloop_record_valid_ex` 的端點樹差異,所以「撞到」本身不會讓未審的內容過;唯一的洞是 F1 的「內容還原」。
  引句:「找 `gate=code-loop`、kind 是 passed/skipped、`head_sha` 落在索引裡的紀錄(不看分支名)」
- 合進來那側頂端是只動簿記檔的提交、簿記檔改變程式行為:名單裡 `governance/anchor-baseline.json`、`governance/drift-acks.jsonl` 會影響別的守衛,但它們已是舊判法的豁免(`_DOCS_ONLY_NEVER` 也把基準線視為守衛),且我沒找到簿記資料夾裡會被執行的路徑(`governance/replay`、`governance/code-loop` 底下 167 個檔都是 json,沒有被程式載入執行);可執行副檔名、模式 100755、`#!` 首行都被 `_codeloop_bookkeeping_code` 當程式。沒有新繞法。
  引句:「判法沿用 `_codeloop_record_valid_ex` 那套」
- 分支 pass 之後 force push 改寫歷史但 head_sha 相同:相同 sha 代表相同提交與相同祖先,改寫歷史必然換 sha,記錄就落到索引外;沒有繞法。
  引句:「以第二個母往回走第一母鏈最多 20 個提交當索引(一次 `git rev-list --first-parent -n 20`)」
- 三個以上的母、淺 clone、全零起點(CI 路徑):都不認。
  引句:「章魚合併(三個以上的母)」

---
最嚴重 severity:major;blocking 條數:1(F1);minor 2 條(F2、F3)為非 blocking。
