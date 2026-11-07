severity: minor

我跑了 `python3.14 scripts/test_lumos.py -k kotlin_rulepack`。結果是 48 項通過、0 項失敗。我沒有找到 major 以上的問題,只有一條 minor。

## F1 型錄「通電批次」欄文字與規則實際位置沒有機械對照
severity: minor
blocking: 否
引句:「告警帶寫法=未接(規則在 rules-unwired/:型錄這列出處不全)」
佐證: `configs/ast-grep/kotlin-android/check.py` 的 `catalog_problems`(在 r3-snapshot.patch 第 76 行附近),以及 `checks-catalog.md` 的 8 列(patch 第 1291 到 1439 行)
失敗場景:`catalog_problems` 只檢查規則放對目錄,沒有核對型錄「通電批次」欄是否寫了「未接」。有人把出處不全的規則搬回 `rules-hints/` 時,`catalog_problems` 會報「只准放 rules-unwired/」,所以這個搬動會被擋下。但反過來,有人把型錄文字改回「批一(只有提示級規則,預設不接)」而規則仍在 `rules-unwired/` 時,不會有任何檢查紅燈。這只是文字漂移,不會讓行為出錯。

## 修補驗收
- **SARIF 探針借用閘的解析函式**:`sarif_gate_rule_ids` 呼叫 `lm._lint_run_and_parse`,並以 `c.get("file") and c.get("message")` 過濾。測試的「規則對但沒有檔案位置」案例實測會報 2 條含「樣本」的問題,三種假輸出都被抓到。
- **探針規則先核對目錄**:`by_id.get(rid, {}).get("dir") != want_dir` 會先擋下,不會誤報成 SARIF 壞掉。`break` 只在載入 `scripts/lumos` 失敗時觸發,邏輯正確。
- **review-fp 樣本排除**:`review_ids` 已擴到 `rules-unwired`,測試造了複本實測。複本沒帶 `scripts/lumos`,所以 SARIF 那條會多報一個問題,但測試只篩 `_uid` 的「好例誤報」,不受影響。
- **`.gitkeep` 與空目錄**:全空測試把 4 個目錄都清空,「一條規則都沒讀到」會報。
- **缺 dir 鍵**:`r.get("dir")` 安全,⑤ 案例覆蓋。`message_problems` 對缺 dir 鍵仍用 `r["dir"]`,但那是原本就有的寫法,不在這次改動範圍。
- **還原翻紅釘與前置斷言**:新測試有 `★前置★` 斷言,⑥ 有 `refs and`,對應 ★INVARIANT★「還原翻紅釘要配前置斷言」。

## manifest
分級命中「共享狀態有沒有鎖保護」,指向 `rules-unwired/coroutines.yml` 第 11 行。這是規則文字提到 Mutex,屬併發類題目,在這個 repo 判範圍外,標為誤報。

## 角色卡
- **be-api-compat**:不適用。這次沒有對外 API 欄位改動,規則 id 與 ast-grep 規則內容原樣搬移。
- **be-authz**:不適用。這次沒有新增端點。

## 固定席判定
- **Systems/kotlin規則包**:沒有合約。筆記與計劃的文字和程式對得上。
- **Systems/測試假綠形態 ★INVARIANT★**:符合,見上面「還原翻紅釘與前置斷言」。

總結:最高等級為 minor,blocking 共 0 條
