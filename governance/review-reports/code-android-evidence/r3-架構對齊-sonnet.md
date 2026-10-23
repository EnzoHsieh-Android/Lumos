severity: major

## 1 範本目錄放了可執行的 .sh,收據重跑腳本繞過 lumos 自己的程式
severity: major
blocking: 是
引句:「+exec python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'」

`scripts/templates/` 原本只有三份純文字範本:`graph-discipline.md`、`note-audit-judge.md`、`note-audit-reread.md`。lumos 用字面路徑常數讀它們,例如 `scripts/lumos:44364` 的 `_NOTE_AUDIT_TEMPLATE` 和 `scripts/lumos:45447` 的 `_NOTE_REREAD_TEMPLATE`,或在 `scripts/lumos:31559` 附近讀進來替換 `{{KG}}`。

新檔 `android-receipt-rerun.sh` 是 mode 100755 的可執行檔,內嵌約 55 行 Python heredoc。沒有任何 lumos 子命令讀它。流程是人照 `skills/lumos-android-evidence/SKILL.md:127` 與 `reference.md:83` 的 `cp` 指示手動複製進收據目錄,再單獨跑。

這帶來三個與既有做法不同的地方:
- 可執行檔放進範本目錄,而這個目錄的既有用途是資料範本。
- 多一條「消費專案手動複製」的分發路徑,不經 lumos 讀取。
- 數字比對、JSON 讀取、rc 與輸出慣例都在腳本裡重寫一套,沒重用 `scripts/lumos` 的 helper,例如 `_secev_num` 在 `scripts/lumos:8554`。

⚠ 判不準的一點:`scripts/` 底下本來就有 `graph-rename.sh` 和 `fetch-notesmd.sh`(`scripts/lumos:31905` 的 `_VENDORED_TOOLKIT`),所以 .sh 本身不算全新。新的是「放進 templates/,而且靠手動複製」。

## 2 新範本沒登記進自裝檔清單,對照既有測試會翻紅
severity: minor
blocking: 否
引句:「+++ b/scripts/templates/android-receipt-rerun.sh」

既有做法是 `scripts/templates/` 底下每支受版控的檔都要列進 `_VENDORED_TREE_FILES`(`scripts/lumos:31915-31927`)。`note-audit-reread.md` 就是這樣加的,旁邊還註明「lumos update 才發得到消費專案」。

快照裡 `scripts/lumos` 沒有動這張表。我在目前樹上確認:`git ls-files scripts/templates` 列出該 .sh,但 `scripts/lumos` 裡完全沒有 `receipt-rerun` 這個字。

`scripts/test_lumos.py:15300`(`t_vendored_file_list_matches_what_install_ships`)要求清單與受版控檔逐檔相等,所以預期會報「少登記」。結構方向對,但漏了鄰居都有做的登記步驟。

## 3 重跑腳本的錯誤輸出不照 rc 2 + stderr「擋下:」慣例
severity: minor
blocking: 否
引句:「+    print('BAD 收據本身:' + ';'.join(problems))」

鄰居慣例是:設定壞了就 `print(f"擋下:{err}", file=sys.stderr); return 2`,例如本 patch 的 `_macrobench_mode` 和 `scripts/lumos:23117`。rc 2 的語意一致。

新腳本也回 2,但訊息走 stdout,開頭是「BAD 收據本身:」。這是獨立腳本,跟 lumos 輸出契約不同。

## 4 以下沒有發現不對齊
severity: minor
blocking: 否
引句:「+        return _secev_num(v) and math.isfinite(v)」

`_macrobench_num` 疊在既有 `_secev_num` 上。`import math` 放在函式內,與 `scripts/lumos:5100`、`:19742` 一致。有限數的判法也和 `scripts/lumos:58320` 同類。這條只是記錄,不算不對齊。

門檻檔那一組同樣對齊鄰居:`_macrobench_thresholds`、`_macrobench_check_thresholds`、`_macrobench_print_thresholds` 的讀檔、回 `(值, 錯誤)` 的方式,和 `_macrobench_config` 一致。放在 `_macrobench_mode` 之前,由 `_macrobench_mode` 呼叫,沒有跨層直呼。錯誤走 `擋下:` + stderr + rc 2。

`_macrobench_read_file` 新增的 `raw` 參數和 `_macrobench_collect` 裡的 `hashlib` 函式內匯入,也和鄰居寫法一致。

## 三問回答

**1 分層與依賴方向**
- macrobench 的新碼分層與鄰居一致:讀檔、判定、輸出三段分開,都在 `_macrobench_mode` 之下。沒有跨層直呼。
- 例外是發現 1 的 .sh:它獨立於 lumos 之外,不被 lumos 呼叫,也不呼叫 lumos。

**2 命名與錯誤處理**
- Python 端的命名(`_macrobench_*`、`MACROBENCH_*`)、rc 2 + `擋下:` + stderr 都對齊,見 `scripts/lumos:39353` 附近。
- 不一致的是發現 3(重跑腳本的輸出)和發現 2(沒登記進清單)。

**3 第二種做法**
- 有一個:發現 1,可執行腳本放在範本目錄、靠手動複製分發,且自帶一套數字比對。
- 測試端沒有新寫法。`t_android_evidence_rerun_refuses_empty` 以 `sp.run(["sh", ...])` 跑 repo 內真檔,用 `GRAPHCTL` 定位路徑;macrobench 的新測試仍用 `_mb_run`(`scripts/test_lumos.py:17552`)。
- 數字檢查沒有另起一套,是疊在 `_secev_num` 上。設定讀取沿用既有的 `.lumos/*.json` 加驗型別的做法。

不對齊共 3 條,其中 major 1 條(發現 4 只是記錄,不計入)。
