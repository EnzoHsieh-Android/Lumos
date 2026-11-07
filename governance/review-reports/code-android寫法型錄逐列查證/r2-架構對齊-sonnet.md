severity: minor

## F1 來源欄與名稱欄用裸索引 c[1]、c[11],鄰居先解構成具名變數
severity: minor
blocking: 否
引句:「for rid, c in main_rows(text).items() if "(出處不全)" not in c[1] and not _VERIFIED_RE.search(c[11])」
佐證 file: `configs/ast-grep/kotlin-android/check.py:565`,對照 `configs/ast-grep/kotlin-android/check.py:348`(`name, std, kind, wire, batch, src = c[1], c[3], c[7], c[8], c[9], c[11]`)。
說明:讀表來源是同一個 main_rows,結構一致。差在 `catalog_problems` 先把欄位取成具名變數,新函式直接寫索引,欄位順序變動時要多改一處。

## 問 1 分層與依賴方向
對齊。`catalog_unverified` 放在 `main_rows` 緊鄰下方(`check.py:557-565`),讀表走 `main_rows`,沒有另寫一套讀法。這和圖譜 WHY「主表只有 main_rows 一條讀法」一致。`catalog_unverified` 回傳清單、不併入 `catalog_problems`,印出的事交給 `main()` 呼叫的 `_print_unverified`。依賴方向是 main → _print_unverified → catalog_unverified → main_rows,沒有跨層直呼。上一輪修補把函式從 `check()` 後搬到 `main_rows` 後,位置更貼近鄰居。

標記判準也對齊:`"(出處不全)" not in c[1]` 和 `catalog_problems` 的 `"(出處不全)" not in name`(`check.py:364`)是同一個字面標記。修補把原本的 `"出處不全"` 改成帶括號的標記,屬於對齊,沒有引入新做法。

## 問 2 命名與錯誤處理
大致對齊。
- 常數 `_VERIFIED_RE`、`_UNVERIFIED_SHOW` 沿用 `_MAIN_ROW_RE`、`_BEHAVIOR_RE` 的底線加大寫命名(`check.py:92`、`check.py:522`)。
- 函式 `catalog_unverified` 和 `catalog_problems`、`main_rows` 同樣用小寫蛇形。
- 輸出走 `print` 到 stdout,和 `main()` 其他輸出一致。
- `--json` 路徑不印提醒,不會破壞 JSON 輸出。
- 提醒只印不改退出碼,和 `main()` 現有的回傳規則一致。
- 唯一差異是 F1 的索引寫法。
- `_print_unverified` 是 `check.py` 裡第一個 `_print_*` 輔助函式,鄰居都把 print 直接寫在 `main()`。結構上只抽出一個小函式、讓兩條路徑共用,我判為純風格,不列。

## 問 3 第二種做法
沒有引入第二種做法。
- 讀表:沒有另一套,走 `main_rows`。
- 暫時替換:`t_kt_catalog_unverified_rows` 用 `real_check = m.check; try: m.check = lambda ...; finally: m.check = real_check`,與專案慣用形狀相同。例如 `scripts/test_lumos.py:1271-1276`、`scripts/test_lumos.py:21854-21860`、`scripts/test_lumos.py:22006-22025` 都是 `m.x = fake`、`finally` 還原。
- 輸出捕捉:`contextlib.redirect_stdout` 配 `io.StringIO`,與 `scripts/test_lumos.py:10057`、`scripts/test_lumos.py:20650` 等一致。
- 工具函式:沒有自創。測試的預期值取自造出的五列型錄,不另立工具。

修補(r2-repair.patch)沒有帶進與既有不一樣的寫法。新加的 ⑦ 項用 `m.check` 的 lambda 替換,沿用上述慣用形狀。

不對齊共 1 條,其中 major 0 條
