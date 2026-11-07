severity: clean

我讀了 `r3-snapshot.patch` 和 `r3-repair.patch`,拿 check.py 的 `main_rows`、`catalog_problems`、`main()`,以及 test_lumos.py 裡其他 `t_kt_catalog_*` 和函式內 import 的寫法對照。沒有找到跟既有做法不一樣的地方。

## 1. 分層與依賴方向
沒有不對齊。
- `catalog_unverified` 讀表走 `main_rows(text)`,沒有另寫一套切欄位的邏輯。這跟 `catalog_problems` 把 `main_rows` 當主表唯一讀法一致。佐證:`configs/ast-grep/kotlin-android/check.py:561`。
- 提醒只在 `main()` 兩個輸出分支各呼叫一次 `_print_unverified()`。數字不進 `catalog_problems`,退出碼仍照 `probs` 和 `problems` 算,依賴方向沒變。佐證:`check.py:818`、`check.py:838`。
- `--json` 分支保持純 JSON,提醒只放在文字分支。這個例外在計劃和測試 ⑧ 都有寫,沒有打破 `--json` 的輸出契約。佐證:`check.py:832`。
- 測試用 `m = _ktpack()` 取得模組,再用 `m.check = lambda ...` 替換並在 `finally` 還原。這跟同檔其他 `t_kt_catalog_*` 的寫法相同。佐證:`scripts/test_lumos.py:128517`。

## 2. 命名與錯誤處理
沒有不對齊。
- 常數 `_VERIFIED_RE`、`_UNVERIFIED_SHOW` 和私有函式 `_print_unverified` 用底線開頭。公開函式 `catalog_unverified` 跟 `catalog_problems`、`main_rows` 同族命名。
- 上一輪修補把欄位取成 `name, src = c[1], c[11]` 的具名變數,比鄰居直接寫 `c[n]` 更清楚,不算第二種做法。
- 測試函式內 `import io, contextlib, json` 沿用同檔慣例。同檔有 142 處函式內的 `import json`,例如 `scripts/test_lumos.py:13955`、`:14382`,所以不算新寫法。
- ⑧ 用 `try: json.loads ... except ValueError: js = None` 再由 `check()` 判定,不另外 raise,跟測試檔裡用 `check(label, cond, detail)` 的風格一致。

## 3. 第二種做法
沒有找到。
- 沒有自創工具函式,讀表、輸出捕捉(`io.StringIO` 加 `contextlib.redirect_stdout`)、替換(`m.check = ...` 後還原)都沿用既有寫法。佐證:`scripts/test_lumos.py:10057`。
- `_VERIFIED_RE` 的 `\u3014`/`\u3015` 跳脫已裁放行,我沒有再列。

不對齊共 0 條,其中 major 0 條
