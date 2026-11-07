severity: minor

## F1 同一個「出處不全」標記,新碼的比對方式跟鄰居不同
severity: minor
blocking: 否
引句:「if "出處不全" not in c[1] and not _VERIFIED_RE.search(c[11])」
file: `configs/ast-grep/kotlin-android/check.py:798`(新碼,不帶括號比對)
file: `configs/ast-grep/kotlin-android/check.py:364`(鄰居:`if "(出處不全)" not in name:`)
file: `configs/ast-grep/kotlin-android/check.py:386`(鄰居:`"(出處不全)" not in c[1]`)
file: `configs/ast-grep/kotlin-android/check.py:390`(鄰居:`"(出處不全)" in c[1]`)
敘述:`catalog_problems` 內三處都認帶全形括號的「(出處不全)」。新函式改認不帶括號的子字串,所以名稱裡只要出現「出處不全」四個字(不一定是標記),這一列就被當成已標。結構正確,只是同一個標記有了兩種判法。

## F2 新常數與函式的放置跟鄰居不同,查證紀錄的括號用法也不同
severity: minor
blocking: 否
引句:「_VERIFIED_RE = re.compile(r"\u3014查證 \d{4}-\d{2}-\d{2}:[^\u3015]*https?://[^\u3015]*\u3015")」
file: `configs/ast-grep/kotlin-android/check.py:790`(新碼,放在 `check()` 之後、`main()` 之前)
file: `configs/ast-grep/kotlin-android/check.py:522`(鄰居:`_BEHAVIOR_RE` 緊貼使用它的 `behavior_value`,在 `main_rows`、`template_problems` 一帶)
file: `configs/ast-grep/kotlin-android/check.py:301`(鄰居:`_src_expand` 的正則直接寫字面 `〕`)
敘述:鄰居把型錄讀取與驗證函式(`main_rows`、`template_problems`、`catalog_problems`)放在一起,新的 `catalog_unverified` 卻放在 `check()` 與 `main()` 之間。鄰居的正則都寫字面全形括號,新碼寫成 `\u3014`、`\u3015` 跳脫。註解說是為了避免 ruff 誤判,但鄰居的字面 `〕` 並沒有造成這個問題。

## 三問

1. **分層與依賴方向:對齊。** `catalog_unverified` 透過 `main_rows(text)` 讀主表(`check.py:534`),沒有另寫一份讀表邏輯。取欄位用 `c[11]`、`c[1]`,與 `catalog_problems` 的 `c[11]`(`check.py:348`)一致。`_print_unverified` 只由 `main()` 呼叫。測試走 `_ktpack()`(`test_lumos.py:126304`)取得模組,與 `t_kt_catalog_batch4_wiring`(`test_lumos.py:128552`)相同。沒有跨層直呼。我也搜過 `scripts/` 與 `.github`,沒有程式解析 `--catalog-only` 的輸出或「型錄問題 N 個」那一行,所以多印一行不會破壞下游。

2. **命名與錯誤處理:大致對齊,有 F1、F2 兩條 minor。** 公開名 `catalog_unverified` 因為測試要呼叫而公開,與 `main_rows`、`behavior_value` 同類(`check.py:534`、`527`);只在檔內用的 `_print_unverified`、`_VERIFIED_RE`、`_UNVERIFIED_SHOW` 都以底線開頭,符合 `t_kt_catalog_private_helpers` 的規定(`test_lumos.py:131608`)。輸出是 `print` 加中文一行,與 `main()` 的 `print(f"型錄問題 {len(probs)} 個")`(`check.py:812`)同款。`--json` 分支沒有加印這一行,所以機器輸出不受影響。這個提醒不進 `catalog_problems`、不改退出碼,與「只提醒」的定位相符。

3. **第二種做法:沒有主表讀法或查證格式的第二套。** 主表仍只走 `main_rows`。新增的 `〔查證 YYYY-MM-DD:網址〕` 沿用型錄已有的格式,例如 2026-11-05 那 140 列 `〔查證 2026-11-05:https://ktor.io/docs/client-timeout.html …〕`,以及 2026-11-06 那 2 列。其中一列帶有 `「…」` 引句,仍符合 `[^〕]*` 的匹配範圍。型錄裡只有一處 `〔查證 日期` 是說明用的文字。測試的造表方式(自造四列型錄,用 `check()` 比對)與 `t_kt_catalog_*` 一致。沒有發現新的工具函式在重複鄰居已有的功能。

不對齊共 2 條,其中 major 0 條
