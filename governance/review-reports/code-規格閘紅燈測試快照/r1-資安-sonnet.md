severity: minor

我站在攻擊者那一邊逐行看完 patch,沒有找到能直接利用的洞。三類都只有縱深防禦層級的發現。

## ①提示注入

已看,無。擋下訊息的出口都先過 `_tg_cand` 的 `_out_clean(extra, 300)`,紅燈版 JSON 的 `name`、`clauses`、`key` 因此都清過控制字元、截到單行 300 字。引句:「extra=f"規格閘紅燈版 {last['tok']} 記的 {last['name']}(條款 {clauses}):{reason}")」。

- `tok` 另外清到 40 字。
- 規格閘輸出的測試名走 `_out_clean(n, 120)`。
- 寫進治理帳的 `redbase_skipped` 是 JSON 轉義過的字串,這個 diff 裡沒有地方把它原樣印給 AI。

## ②讀寫越界與執行

### S1 紅燈版內嵌的測試檔路徑沒驗,只驗了紅燈版檔自己的路徑
severity: minor
blocking: 否 — 縱深防禦,要先偽造 sha256 才碰得到(範圍外),我也沒有一步就會走到的路徑
引句:「tpath, key, name, clauses = t.get("path"), t.get("key"), t.get("name"), t.get("clauses")」
file: `scripts/lumos:49600` 一帶的 `_tg_rb_entry`、`_tg_rb_fill`、`_tg_rb_path_ok`
- 誰:寫紅燈版的工具,或手改過紅燈版檔又重算 sha256 的人。
- 從哪裡:`_tg_rb_entry` 取出 `tests[].path`。
- 送什麼:只檢查是非空字串,沒限 `.kt`、`.java`,也沒限制不含換行或 `..`。
- 拿到什麼:`_tg_rb_fill` 會把它拼成 `<rev>:<tpath>` 交給 `git cat-file`。範圍限在 repo 的 git 物件內,拿不到 repo 外的檔。含換行時 `_nodehome_cat_sizes` 回 None,整次比對報「git 讀不出」。這是擋下,不是放行。
- 判定:推論。

### S2 寫入端讀上一份紅燈版時跟隨符號連結,與計劃「不跟符號連結」的說法不一致
severity: minor
blocking: 否 — 要先在治理帳塞一行指向符號連結的偽造留痕(範圍外),而且讀進來的內容不會回顯
引句:「doc = _json.loads((Path(rr) / path).read_bytes().decode("utf-8"))」
file: `scripts/lumos:14371`(`_redbase_branch_state`)
- 誰:能在工作目錄放符號連結並改治理帳的人。
- 從哪裡:規格閘重跑時,`_redbase_branch_state` 對每筆 `branch_rows` 的 `redbase.path` 做 `read_bytes`。
- 送什麼:`governance/redbase/甲/x.json` 是指向 repo 外某個 JSON 檔的符號連結,檔名已通過 `_tg_rb_path_ok`。
- 拿到什麼:`read_bytes` 會跟過去,內容只用來做「本體相同就不存」的比較。這是讀端沒有的符號連結行為。
- 判定:推論。

## ③非刻意、一步就能繞過的守衛

### S3 治理帳與紅燈版檔兩樣都沒進提交時,比對整段靜默略過
severity: minor
blocking: 否 — 計劃已承認「只看紅燈版資料夾的話,漏 git add 走不到偵測」,而兩樣都漏、同時規格閘推送閘又不要求留痕的組合需要較少見的條件
引句:「touched = any(p == GOV_LOG_REL or (p or "").startswith(_RB_DIR) for _st, o, n, _s, _g in ch for p in (o, n))」
file: `scripts/lumos:49595`(`_tg_redbase_cands`)
- 誰:照全域規則「同工作區只加自己的檔、commit 帶路徑」操作的 AI。`docs/.governance-log.jsonl` 常有別的會談的改動,AI 很可能不 stage 它。
- 從哪裡:`git commit -- <測試檔> <實作檔>`,漏掉 `docs/.governance-log.jsonl` 和 `governance/redbase/`。
- 送什麼:這個提交裡新測試的 expected 已經改成實作輸出。
- 拿到什麼:改動清單裡沒有治理帳也沒有紅燈版資料夾,`touched` 為假,`return [], None`。紅燈版比對完全沒跑,也沒印任何提示。
- 我在臨時 repo 實測了四種提交組合:
  - 治理帳加紅燈版檔都提交:列出 `tq/redbase-weakened`。
  - 只提交紅燈版檔:列出 `tq/redbase-unreadable`,原因是孤兒檔。
  - 只提交治理帳:列出 `tq/redbase-unreadable`,原因是被刪了。
  - 兩樣都不提交:`candidates` 為空。
- 是否被別道擋下,我沒有查證:規格閘自己的推送閘缺留痕時會不會擋,不在這份 patch 內。

### S4 紅燈版把整支測試檔固定進提交,連未提交的暫貼秘密也一起帶
severity: minor
blocking: 否 — 計劃〈資安〉那一行已自述,這裡只補成攻擊路徑,且不是新的外洩管道
引句:「files[c["path"]] = c["text"]」
file: `scripts/lumos:14338`(`_redbase_write`)
- 誰:使用者或照常操作的 AI。
- 從哪裡:規格閘在測試檔還沒提交、檔裡暫貼了真實 API key 或本機網址時判紅。
- 送什麼:被判紅的那支測試所在的整支檔(含其他測試與暫貼的秘密)。
- 拿到什麼:秘密被寫進 `governance/redbase/` 的 JSON。就算之後從測試檔刪掉,紅燈版仍留著舊內容。`tq/redbase-unreadable` 的訊息還會叫人 `git add` 那支檔,而 `governance/redbase/` 已列入簿記資料夾,風險掃描和小改動閘都會略過它。
- R16 對應:`.gitignore` 只擋被忽略的檔,擋不到「未被忽略的草稿」。

## 其他已查、無發現

- R18:所有 `subprocess` 都是參數陣列,`git check-ignore` 帶了 `--`,JSON 只用 `json.loads`,`RecursionError` 也接住了。
- 紅燈版檔路徑:讀取前經 `_tg_rb_path_ok` 擋掉 `..`、反斜線、控制字元、空段,並從終點提交的 git blob 讀,不讀工作目錄。
- 寫入端:迴圈編號拼路徑前經 `safe` 消毒,檔名帶隨機 token。測試檔來源用 `resolve().relative_to(rr)` 擋掉符號連結逃出 repo 的情況。
- 守衛失效:改測試名、搬檔、刪測試、同名多載、重跑規格閘仍紅、重跑後轉綠、治理帳列損毀(會變成孤兒檔候選)都落在擋下或照比,沒有靜默放行。
- 範圍外,順手一提:同時改紅燈版檔和治理帳 sha256,或刪掉 `spec-gate-green` 事件,可以洗掉紅燈版(minor,blocking: 否)。

四條都是縱深防禦或已被計劃承認的缺口,沒有可直接利用的洞。
