severity: clean

## 逐類檢查

1 不可信輸入流到危險操作:已看,無。這輪改動集中在 `_notes_status_flipped` / `_note_flipped_one` / `_note_status_seq` / `_note_history_states` / `_utf8_ok`、`_drift_tree_env` 的逾時算法、`_drift_config` 回傳形狀、`_guard_formal_line` 的測試名比對、`_drift_c3_hit` 的空連結判斷、doctor 的開關提醒文字。所有讀檔仍走既有的 `_ns_git` / `_nodehome_cat_blobs` / `_lens_git`,三者都用 `subprocess.run(["git", ...])` 傳 list 給 args(`_lens_git` 定義在 scripts/lumos:30402 附近,`_nodehome_cat_blobs` 在 23063 附近),沒有 `shell=True`、沒有字串拼接組指令,不會因路徑或分支名帶特殊字元被注入;這輪 diff 沒有新增任何 subprocess/shell 呼叫。

2 登入與權限:已看,無新增。`.lumos/config.json` 的 `drift_check.gate` 讀的是被推送頂端提交裡的設定,推送者確實可以在同一個提交把 gate 改成 off 放過自己——但這是既有行為,這輪 diff 只把 `_drift_config` 從回 2 個值改成回 3 個值(多一個 `explicit`),沒有新增或修改這條讀取邏輯,而且該風險已經在 `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md` 用 `RULE:[since:2026-09-28]` 記載並給了 retire 條件,屬於已知且已裁定的設計取捨,不是這輪引入的洞。

3 密鑰與個資:已看,無。改動沒有碰到任何 log/print 新增內容涉及憑證或個資;新增的 print(doctor 開關提醒 `src = "(.lumos/config.json 的 drift_check.gate)" if explicit else "(沒寫設定,這是預設值)"`)只是講設定來源,不含使用者資料。

4 加密與傳輸:已看,無。這輪沒有碰網路、TLS 或加解密相關程式碼。

5 執行邊界:已看,無。`_drift_tree_env` 的逾時算法改成 `left = 60 if deadline is None else max(1, deadline - _t.monotonic())`,`max(1, ...)` 保底 1 秒,不會傳負數或 0 給 `_nodehome_cat_blobs` 造成非預期行為(這屬正確性/資源議題,非資安攻擊路徑,不報)。`_guard_formal_line` 把測試名比對從 `any(r == method or r.endswith(":" + method) for r in refs)` 改成 `method in refs`——這是收緊比對(不再猜平台前綴),不會放寬任何邊界,沒有引入可被利用的匹配漏洞。

6 行動端:已看,無。這輪沒有觸及任何行動端(iOS/Android/Flutter)程式碼。

新依賴:已看,無。diff 內只看到 stdlib `import time as _t`(在 `_drift_tree_env`、`_note_flipped_one`/`_note_status_seq` 的區域函式內),沒有新增第三方套件。

## 逐 hunk 補充說明(非獨立 finding,供對照)

- `_note_history_states` 新增的 `_utf8_ok` 用 `b.decode("utf-8-sig")` 純檢查解碼是否成功、不執行內容,不是反序列化(python-idioms R18 不適用):
  引句:「def _utf8_ok(b):\n    try:\n        b.decode("utf-8-sig")」
  file: `scripts/lumos:229-234`(clone-ns 工作樹行號,對照凍結 diff 第 229-234 行新增區塊)
  已看,無 finding——純字串解碼檢查,沒有 eval/pickle/yaml.load 等危險反序列化路徑。

- `_drift_config` 讀 `.lumos/config.json` 一律走 `json.loads`(scripts/lumos 既有函式,這輪只改回傳形狀),沒有改成 `eval`/`exec` 或不安全的 yaml 載入,R18 不適用。

## 總結

最高等級 clean,blocking 0 條。
