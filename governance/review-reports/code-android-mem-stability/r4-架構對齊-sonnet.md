severity: major

這份 diff 在分層、命名、佔位寫法上大多跟鄰居一致。結構上有一處第二種做法,另有兩處輸出或佔位寫法不一致。比對範圍是 scripts/lumos 的 `_macrobench_*` 區段、`android-receipt-rerun.sh`、`android-ui-attribution.sql` 與 `skills/lumos-android-evidence/reference.md`。

**問 1 分層與依賴方向**

lumos 這一側的依賴方向對齊。
- 日期判斷走既有的 `DATE_RE`(`scripts/lumos:28099`)加 `_rule_date`(`scripts/lumos:4296`),取代原本自寫的 `\d{4}-\d{2}-\d{2}` 加 `fromisoformat`。
- 限深用既有的 `_events_depth_ok`(`scripts/lumos:35458`),整數判斷用 `_secev_int`(`scripts/lumos:8559`),字串清洗用 `_esc_clean`(`scripts/lumos:19331`)。
- 判定集中在 `_macrobench_judge_stability`,收集腳本只寫 `stability.json`,職責切得跟鄰居「收集歸腳本、判定歸 lumos」一致。
- 四個新範本檔都登記進 `_VENDORED_TREE_FILES`(`scripts/lumos:31920` 起),註解寫法也跟既有兩行相同。
- 範本直接叫 lumos 命令列(`--check-config`)這點,跟自給自足的 `android-receipt-rerun.sh`(`scripts/templates/android-receipt-rerun.sh:1-12`)不同。判不準:這是呼叫 CLI,不是穿透內部函式,而且設定驗證因此只有一份,我不當成不對齊。

**問 2 命名與錯誤處理**

- 函式前綴 `_macrobench_stab_*`、常數 `MACROBENCH_*`、回「錯誤訊息或 None」的 `_err` 函式,都跟 `_macrobench_threshold_item_err`、`_macrobench_config_fields`(`scripts/lumos:39379`)一樣。
- 常數放在使用處旁邊,跟 `MACROBENCH_THRESHOLD_REQUIRED` 同一做法。
- 回傳碼與訊息跟鄰居一致:設定壞了印「擋下:」、走 stderr、回 2,其餘只提醒回 0。
- 環境變數 `ADB`、`TP` 沒加前綴,跟 `receipt-rerun` 的 `${TP:-trace_processor}` 一樣;測試縮短用的 `LUMOS_STABILITY_*` 有 `LUMOS_` 前綴,跟 `LUMOS_PYTHON` 等一致。
- 以下兩條不對齊。

severity: minor
blocking: 否
引句:「cfg = cfg.replace("__PROCESS__", pkg).replace("__DURATION_MS__", str(int(max_s * 1000)))」
佐證 file: `skills/lumos-android-evidence/reference.md:77`
說明:專案慣例是 `{{NAME}}` 由程式替換、`__NAME__` 給 AI 手動替換。收集腳本用程式替換 `__DURATION_MS__`(只有 pbtxt 用)和 pbtxt 裡的 `__PROCESS__`,佔位寫法跟慣例反了。`__PROCESS__` 在 SQL 範本裡同時要給收據手貼,那邊沿用 `__` 寫法合理;單獨給程式替換的 `__DURATION_MS__` 應寫成 `{{...}}`。
判不準:SQL 範本的 `__PROCESS__` 因為兼用手貼,我只把 pbtxt 的 `__DURATION_MS__` 算進這條。

severity: minor
blocking: 否
引句:「res["stability_unjudged"] = "給了 --stability,但門檻檔裡沒有寫了 check 的條目,記憶體與穩定性沒有東西可判"」
佐證 file: `scripts/lumos:39595`
說明:既有的 `res` 結果字典一開始就把所有鍵先放齊(清單或布林)。新欄位 `stability_unjudged` 只在觸發時才出現,值是字串。JSON 讀取端得用「有沒有這個鍵」判斷,跟鄰居「鍵固定、型別固定」不同。

**問 3 第二種做法**

severity: major
blocking: 是
引句:「os.killpg(p.pid, signal.SIGKILL)」
佐證 file: `scripts/lumos:25519`
說明:`kill_group` 在收集腳本裡重寫了整組殺掉的子程序收尾,而 lumos 已有 `_kill_proc_group`。後者還處理 Windows 沒有 killpg 時退回 `proc.kill()`,新版沒有。
判不準:收集腳本是 heredoc 裡的獨立 Python,不能 import 六萬行的 lumos。這份重複可能是不得已,但它確實是第二套同功能的實作,收尾語意也不一樣(沒有 fallback)。我把它判成第二種做法,是否接受要由作者說明。

其他幾項我確認沒有第二種做法:
- 深度限制、孤立代理字元清洗、日期、整數判斷都重用既有共用函式。
- 簽署欄位把兩種門檻條目與 `test_data` 收成一支 `_macrobench_signed_err`,沒有各寫一套。
- 範本讀檔用 `utf-8-sig`、`exec env ... python3 - <<'PY'` 的包法,跟 `receipt-rerun` 一致。

不對齊共 3 條
