# code-six-fixes r3(末輪)——第 2 輪修法 delta 回歸

審查範圍:`governance/review-reports/code-six-fixes/r3-snapshot.patch`(= commit `2e26432`,已核對兩者內容一致,僅 context 行數不同)。全部在 `/tmp/lumos-r2-check`(`git worktree add --detach 2e26432`)這個乾淨副本裡實跑驗證,未動 repo 任何檔。

## (a) 修復驗收

1. **JSON degraded 寫死 False → 已修對。** 在乾淨副本對 `_delguard_vault_scan` 打 patch 讓它真的因 deadline 截斷返回部分 hits 後,`--json` 印出 `"degraded": true, "reason": "timeout-partial"`;成功/未截斷路徑仍是 `"degraded": false` 且不帶 `reason` 鍵(靠 `**({...} if _partial else {})` 空展開)。
   引句:「"fake_sync": fake, "degraded": _partial, **({"reason": "timeout-partial"} if _partial else {})}, ensure_ascii=False))」
   file: `scripts/lumos:14299-14300`
severity: clean

2. **3.8 相容(去 dict `|`)→ 已修對。** 在 `cmd_dispatch_lens_spec` 整段(17615–17760 行範圍)grep `} |` / `| {` 均 0 命中;新寫法改用三段 `**` 展開,`**` 字典展開語法自 Python 3.5 起就有(PEP 448),不像 `dict.__or__`(PEP 584)要 3.9+,語意上與 repo 別處宣告的「≥3.8」一致。功能面用 `python3 scripts/test_lumos.py -k dispatch_lens` 全綠(56 passed,含專門測「計劃直接連結節點排最前、pinned 資料照樣併進去」的案例),確認不只是語法過關、行為也對。
   引句:「**{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結"」
   file: `scripts/lumos:17702`
severity: clean

## (b) `_deadline_check` 觸發點與「掃完最後一段沒再查」的邊界情況

`_delguard_vault_scan` 有兩個檢查點:外層 `for fn in files` 每檔一次(進檔前),內層每 2000 行一次。兩個點只要 `deadline_check()` 回 True 就會先設 `_trunc["hit"]=True` 再回 True,兩者是同一步——只要函式提前 return,`_trunc["hit"]` 保證已設,這點沒問題。

但**有**你問的那個洞,而且能重現:如果一份筆記行數 < 2000(內層檢查永遠不會在這份檔案裡觸發),進檔前那次檢查又剛好還沒超時,那這一整份檔案不管實際掃多久都不會再被問一次。用一份 1999 行、每行 4000 字的節點檔 + deadline=1ms 實測:elapsed=0.1034s(超時 100 倍),但 `_trunc["hit"]` 全程是 `False`——`cmd_delguard_check` 會把這輪記成 `ok`,`--json` 印 `degraded: false`,即使掃描真的爆了 deadline。

這不是這條 delta 沒碰到的舊洞,而是**换了一種方向的迴歸**:r1 的算法是「函式返回後拿真實 elapsed 跟 deadline 比」,這個算法反而會抓到這個邊界(不管有沒有呼叫 callback,时间过了就是过了),代價是「剛好卡在邊界但其實掃完了」會被錯標成 partial(r2 修的正是這個假陽性)。r2 換成「只信 callback 有沒有被呼叫且回 True」,治好了假陽性,但换来了這個假陰性:最後一段沒有機會被問到,就永遠不會被標記。兩種算法對「介於檢查點之間」的時間都沒有好答案,r2 只是把盲區從「函式尾端」搬到「兩個檢查點之間」,沒有真正補上。
引句:「掃描真的被截斷才算部分結果(delta r2:剛好慢了但掃完不算)」
file: `scripts/lumos:14287`
severity: major
blocking: 否(delguard 全程 fail-open/advisory,不擋 commit;只有治理帳「degraded 比例」這個數字會失真,不影響任何人被錯擋)

## (c) 測試⑤的 0.0001 秒:假綠

在乾淨副本跑 `python3 scripts/test_lumos.py -k delguard_logs`:2 passed,0 failed,全程 0.6s。**但這是假綠**——用 instrumented probe 直接呼叫 `cmd_delguard_check(as_json=True)`(monkeypatch `_delguard_vault_scan`/`_delguard_log_degraded`/`_delguard_log_result` 記軌跡)複現測試同款 0.0001s deadline,結果:`_delguard_vault_scan` **從未被呼叫**,唯一走的是 `_delguard_log_degraded(reason=timeout)`,`--json` 印出 `{"degraded": true, "reason": "timeout"}`——`reason` 是舊有的 `"timeout"`,不是這次修法要驗的 `"timeout-partial"`。

`cmd_delguard_check` 裡從讀 `deadline` 到呼叫 `_delguard_vault_scan` 之間有 **2 個**超時檢查點(`if _over():`,分別在 token 解析後、`_delguard_confidence` 算完後),兩個都是這條 delta 之前就有的舊分支,跟這輪修的 `_trunc`/`_deadline_check` 機制完全無關。0.0001 秒的 deadline 光是跑一次 `git diff --cached` 子行程就必定先觸發這兩個舊檢查點之一,`_delguard_vault_scan` 根本進不去——測試⑤驗的是舊代碼路徑,不是這輪要驗的新代碼路徑。
引句:「r2 = _sp.run([sys.executable, GRAPHCTL, "delguard", "--staged", "--json"], cwd=str(root), capture_output=True, text=True, timeout=120, env=dict(os.environ, LUMOS_DELGUARD_DEADLINE="0.0001"))」
file: `scripts/test_lumos.py:25825`(r3-snapshot.patch 內行號;現 repo 對應舊行 25825)
severity: blocker
blocking: 是(這條測試對外宣稱「驗到了 r1 M2/r2 M 這條修法」,實際上驗證力等於零;下次有人真的把 `_trunc`/`_deadline_check` 邏輯改壞,這條測試依然全綠,等於守衛形同虛設)

⚠ 附帶發現(不算這輪 delta 的一部分,僅供佐證):目前 repo 工作樹 `scripts/test_lumos.py` 有一筆**未 commit** 的修改,已經用「monkeypatch `_delguard_vault_scan` 讓它 sleep 1.2s 再檢查 deadline_check、deadline 設 1.0s」的寫法取代掉這條 0.0001s 版本,且註解原文正是「不能用超小 deadline 去逼(那會在 git diff 後的早期檢查點就走舊的 `_degraded_json` 路,測到的不是這條修法——假綠形態)」——與本節獨立得出的結論一致。但那份修改不在 `r3-snapshot.patch` 裡、也未進任何 commit,不算這輪要驗收的 delta,這裡只當作佐證,不當作(c)已修復的理由。

## (d) JSON 多了 `reason` 鍵:有沒有消費端會炸

grep 全 repo,`--json` 唯一的生產端消費者是 `scripts/hooks/pre-commit`,但它呼叫 delguard **不帶** `--json`(純文字模式),不解析 JSON,不受影響。
引句:「"$CC_PY" "$REPO_ROOT/scripts/lumos" delguard --staged 2>/dev/null || true」
file: `scripts/hooks/pre-commit:57`
測試面(`scripts/test_lumos.py` 13032–13371 行一帶)全部用 `dj.get("degraded")`/`isinstance(dj.get("tokens"), int)` 這種存在性斷言,沒有任何 `set(dj.keys()) == {...}` 這種封閉鍵集檢查,多一個 `reason` 鍵不會讓既有斷言變假。
severity: clean

## 小結

severity: blocker
blocking: 是
引句:「r2 = _sp.run([sys.executable, GRAPHCTL, "delguard", "--staged", "--json"], cwd=str(root), capture_output=True, text=True, timeout=120, env=dict(os.environ, LUMOS_DELGUARD_DEADLINE="0.0001"))」
file: `scripts/test_lumos.py:25825`

production code 本身(①②③④)這輪修得對、可驗、行為也如預期;唯一的 blocker 是測試⑤本身測錯路徑(假綠),另有一條 major/非阻塞的邊界回歸((b))建議一併記錄、找機會補檢查點或改回「返回後比對真實 elapsed」但同時保留「掃完才算」的判準(例如返回值多帶一個「本次是否真的掃到底」旗標,而不是單靠 callback 有沒有被戳到)。

max severity: blocker
