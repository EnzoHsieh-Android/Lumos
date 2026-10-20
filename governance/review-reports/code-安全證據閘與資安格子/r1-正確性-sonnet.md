severity: major

本包沒有 blocker。有 1 條 major(證據解析遇到壞形狀會直接丟 TypeError),另有 3 條 minor。範圍是 r1-lumos-a.patch,即 pre-push 掛鉤、威脅類別表、v2 盤點、格子、證據圍欄與 SARIF 解析等。以下重現都是在 b99f52c8 的 detached worktree 裡,用 `python3.14 -B` 載入 `scripts/lumos` 對單一函式跑的。完整的端到端閘沒有跑。

## 1. 證據圍欄與 SARIF 的壞形狀會讓解析丟 TypeError,整道閘變成 evaluation_error
severity: major
blocking: 是

走到的路徑如下:
- 證據圍欄的 `judgments` 若含不可雜湊的元素(例如 `[["x"]]`),`_secev_ip_review` 的 `all(x in _SECEV_JUDGMENTS for x in j)` 會拿 list 去查 dict,丟 `TypeError: unhashable type`。
- SARIF 的 result 若 `ruleId` 是 dict,`_secev_sarif_hit` 的 `rid not in rules` 會丟 `TypeError`。呼叫端傳進來的是 `set(rules)`。
- SARIF 的 `toolExecutionNotifications` 若是非空 dict 或字串,`_secev_sarif_run` 做 `(… or []) + (… or [])` 會丟 `TypeError`。

這三條都沒有被 `_secev_judge_sarif` 或 `_secev_fence` 接住。`_secev_evaluate` 最外層的 `except Exception` 會把它轉成整道 `evaluation_error`。

壞處有兩個:
- 本來該只讓那一條證據判成 `invalid` 或 `evidence_fence_invalid`,現在是整道閘死掉,其他護欄的判定也一起丟了。
- 例外(`exception`)核可救不了這個代碼,只能靠 `gate_setting=warn` 降級,那會讓整道閘都不擋。

fail-closed 方向是對的,錯在粒度與逃生路。

引句:「        return "judgments 要是非空、不重複、只含已知判斷 id 的陣列"」

最小重現(單元層):
```
it = {"kind":"review","format":"review_record","path":"p","control_id":"c","control_revision":"1","environment":"e",
      "observed_at":"2026-10-20T01:00:00Z","bindings":[],"targets":{},"reviewer":"r","author":"a",
      "reviewer_kind":"ai","judgments":[["x"]],"expires_on":"2026-11-01"}
_secev_item_problem(it)   # TypeError: unhashable type: 'list'
_secev_sarif_facts(b'{"version":"2.1.0","runs":[{"tool":{"driver":{"name":"x"}},"results":[{"ruleId":{"a":1}}]}]}', {"R"})   # TypeError
_secev_sarif_facts(b'...invocations:[{"executionSuccessful":true,"toolExecutionNotifications":{"level":"error"}}]...', {"R"})  # TypeError
```
三條都已實際丟出 TypeError。只重現到函式層,端到端的 evaluation_error 是從 `_secev_evaluate` 的 `except Exception` 讀出來的。

修法方向:`judgments` 先檢查元素是否為 str 再查表;SARIF 的 `rid` 和通知欄位先做型別檢查。

## 2. v2 入口的 `actor_ids` 不擋重複值,格子被重複計算
severity: minor
blocking: 否

`_secinv_inv_surface_v2` 只驗 `actor_ids` 是字串陣列且都在 actors 裡,沒查重。同檔的 `asset_ids` 走 `_secinv_str_list`,有查重。

重現:一個 `http_api` 入口,`actor_ids:["u","u"]`,`inventory_problems` 不報錯。`_seccell_compute` 算出 `count=14, gaps=14`,但 `open` 裡只有 11 個不同的格子 id。重複的格子 id 會多算格數、多出重複的候選題(`_seccell_questions` 逐格輸出)。

引句:「        if not (isinstance(s["actor_ids"], list) and all(_secinv_is_text(x) for x in s["actor_ids"])):」

## 3. `zap_stats` 覆蓋證明把 JSON 的 `true` 當成正整數
severity: minor
blocking: 否

`isinstance(obj.get(k), int) and obj[k] > 0` 對 `True` 成立,因為 `bool` 是 `int` 的子類。`{"stats.auth.success":true,"stats.network.send.success":true,"stats.ascan.urls":true}` 實測回 True。這條覆蓋證明本來就是要擋「沒真的掃到東西」的壞輸入,卻放行了。

引句:「            return all(isinstance(obj.get(k), int) and obj[k] > 0 for k in ("stats.auth.success", "stats.network.send.success",」

## 4. `security list --questions --json` 直接用 `json.dumps` 輸出,繞過跳脫統一規則
severity: minor
blocking: 否

這一支的 JSON 輸出沒有走 `_json_text_escaped`,文字模式有走 `_secinv_show`。題句裡代入了作者可控的 `description`(入口、資產、角色名)。含 U+202E 或 U+2028 的 description 會原樣印到 stdout,而這個輸出會被拿去逐題跑 `question-add`。同檔其他 JSON 路徑都跳脫這類字元。

引句:「        print(json.dumps({"questions": qs, "remaining": more}, ensure_ascii=False, indent=1))」

## pitfalls manifest(2 條)
兩條都是 `scripts/lumos` 的 `open(` 資源類內建提示(行 11110、11167),判誤報。

這兩處在被審 b99f52c8 的真檔裡,我沒有逐行對過,理由來自 patch 的範圍:本包 hunk 裡沒有新增 `open()`,檔案讀取都走 `Path.read_text`、`SecevTree` 或 `dir_fd`。若審查席要確認,請另一席對 11110 與 11167 的 `with` 用法補查。

## 圖譜鏡頭與本案特定鏡頭
- **圖譜鏡頭:** 這次沒附固定席節點,不必逐條答。我看過的 `Projects/安全主張驗收閘_計劃` 的 SARIF 命中定義(note、none、pass 不算命中),與 `_secev_sarif_hit` 的行為一致。
- **fail-closed:**
  - pre-push 的 tag 路徑任何非 0 都擋,是對的。
  - 註記:同檔分支路徑對 rc≠0/1 的非中斷碼是 fail-open(舊慣例),本包沒碰,但 `--security-only` 與分支 `code-loop check` 的容錯不一致。
  - 本包沒有核可鏈驗章、鏈雜湊、到期與撤銷的程式碼,那在別包。
  - 我讀到的 `_secev_consideration_counted`(到期日當天有效、risk_accepted 30 天、`ex < today` 判無效)沒有看到放行壞輸入的路徑。
- **時間:** `_secinv_today()` 是 UTC 日期,台北凌晨 1 點時比本地日期慢一天。這是原有設計,本包沒改,也沒看到新引入的日界線錯誤。`approved_on` 同樣由工具算 UTC。
- **新舊互讀:**
  - v1 塊出現 v2 鍵會被 `_secinv_exact_keys` 擋掉。
  - v1 記錄會多一筆 `missing_field: threat_categories` 的盤點提示,不影響退出碼。
  - `-k seccell`(65 筆)與 `-k sectt`(9 筆)全綠。`-k prepush_cl_reason`(5 筆)全綠。`-k secinv` 與 `-k security_only` 這兩個關鍵字沒有符合的測試名,不算跑過。

最嚴重 severity: major,blocking 共 1 條
