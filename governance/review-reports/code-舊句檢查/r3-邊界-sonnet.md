severity: minor

審查範圍:第 2 輪修正(b1e63672..89884251)。在 `git clone --shared` 出來的臨時目錄實跑,直譯器 3.14。凍結 patch 檔不在 repo 裡,我用同一個範圍自己重出 diff 對照。

## F1 表態指令的「路徑不可照貼」判準只擋 Cf 與非 UTF-8,含 tab、換行、ESC、U+0085 的路徑照樣印出一條貼了會找不到檔的指令
severity: minor
blocking: 否
引句:「if kind == "m1" and _drift_c4_show_name(path) != path:」
佐證行:file: `scripts/lumos:28185`(`_drift_c4_show_name` 只換 Cf 與非 UTF-8);file: `scripts/lumos:9783`(`_drift_print_hints` 印出前過 `_esc_clean`,控制字元換成空格)
1. 輸入:圖譜裡一篇檔名帶 tab 的筆記 `Systems/tab\tnote.md`,第 8 行寫 `呼叫 gone_func_zz`,起點定義了 `gone_func_zz`、終點刪掉。
2. 走到:`_drift_fix_hint` 的新守衛。`_drift_c4_show_name("Systems/tab\tnote.md")` 等於原字串,守衛不成立,照樣組出 `lumos drift ack`。印出時 `_esc_clean` 把 tab 換成空格。
3. 實跑 `lumos drift check --diff`,輸出:`lumos drift ack 'Systems/tab note' 8 --kind m1 --name=gone_func_zz --reason "<為什麼照留>"`。路徑已不是真檔名,照貼會報找不到筆記。
4. 同樣的結果:`\n`、`\x1b`、`\x85` 都印成空格;U+2028 原樣印出(`_esc_clean` 不處理 Zl/Zp)。實測 `_drift_fix_hint("m1", p, 3, ["foo_bar"])` 對這些路徑都印指令,只有 U+202E、U+200B、非 UTF-8 三種走「不印可照貼」那條。
5. 這正是第 2 輪要修的「印出來的樣子跟實際檔名不同、照貼也找不到」,只修了報上來的 Cf 與 non-UTF-8 兩種輸入,Cc、C1、Zl、Zp 沒收。後果只是提示誤導,沒有繞過。最小修法:判準改成「印出前後經 `_esc_clean` 與 `_drift_c4_show_name` 之後跟原路徑不同」。

## F2 跟消失名稱完全無關的一條超長行,會讓 block 模式整批擋下,而且沒有表態路可走
severity: minor
blocking: 否
引句:「return bool(handle) or res["state"] in _DRIFT_M1_UNKNOWN or bool(res.get("long_lines"))」
佐證行:file: `scripts/lumos:29196`(`_drift_m1_scan_note` 遇超長行只計數、不看行裡有沒有提到任何消失名稱)
1. 輸入:`drift_check.old_sentence=block`;某篇筆記(非撤除節)有一行 20001 字、內容跟這次消失的名稱毫無關係;這次推送刪了任一個函式。
2. 實跑邊界:該行 19999 字、20000 字 → rc 0、「筆記裡沒有還在講的」;20001 字 → rc 1,「擋下:…有 1 行太長沒看」,結論行與逃生提示都印出。
3. 這一項擋下沒有 `drift ack` 可用(表態綁名稱集合,超長行沒有名稱可綁),只有拆短那一行、把開關改 warn、或 `LUMOS_SKIP_DRIFT_CHECK=1`。只要那條長行留在庫裡,之後每一次刪了任何名稱的推送都被擋,跟這次刪了什麼無關。
4. 目前 repo 自己的圖譜沒有超過 20000 字的行(實測 awk 為 0),所以現況不觸發;消費專案貼進大段 JSON 或日誌的筆記會觸發。warn 預設下只是多印一行提醒。定位 minor:是第 2 輪資安席「沒看完照判不了」的直接後果,誤擋範圍比必要的大;若要收斂,只在該行含任一消失名稱(或名稱集合很小時逐個 `in` 檢查)時才算判不了。

## 逐項實跑結果(沒找到問題的輸入,供收貨端對照)
- 既有 `~/.cache`:0755、0700 過;0775、0777、0770、1777 判不可信,`_mkdir_trusted_under_home` 回 False 且沒在底下建任何東西;`~/.cache` 是捷徑、`~/.cache/lumos` 是檔或捷徑都回 False、沒建出新層。不存在時 umask 022、002、000、077、277 下三層都是 0700 且通過檢查。
- HOME:不存在、唯讀(0500)、空字串(Path.home() 變 `/`,非 root 建不了)都回 False 不丟例外;HOME 是捷徑、帶尾斜線、是相對路徑都通過。
- 從 `cmd_drift_check` 入口端到端:`~/.cache` 為 0777、`drift-m1` 位置是 FIFO、HOME 唯讀,三種都 rc 0、結論行照印,沒卡住、沒丟例外。
- 留痕檔 `ledger-miss.jsonl`:是一般檔追加成功;無讀端 FIFO、有讀端 FIFO(不卡住,回 False)、目錄、指向檔的捷徑、指向 /dev/null 的捷徑、唯讀檔都回 False,耗時 0.0 秒。硬連結到自己的檔會追加寫入(同一使用者的檔,不算洞)。
- 單行上限:19999、20000 字都掃,20001 字才計 long_lines(邊界正確)。
- 時間:1500 個名稱、150 個近 2 萬字的行、每行都命中,全跑 5.8 秒;一行的比對約 0.04 秒,截止時間檢查點間距沒有失控。
- doctor 輸出:gate 與 old_sentence 各 12 種值(缺、block、warn、off、大小寫錯、空字串、0、false、true、list、dict、尾隨空白)全組合、JSON 壞、非 UTF-8、根是陣列、`drift_check` 是 null 或陣列,都沒丟例外;old_sentence 一行獨立、gate 一行不再被過濾。設定檔壞掉時兩行都講「讀不成 JSON」,重複但不誤導。

## 圖譜鏡頭逐條判定
- Systems/lumos-cli-read(search 濾網合約)、bound-tests-gate(綁定測試逐支真跑)、guard-kill(rc 優先序與 --json 純度)、design-loop(處置閘第五步):這次 diff 只動舊句檢查、`_trusted_private_dir` 與 `_mkdir_trusted_under_home` 家目錄快取層、doctor 一行,沒碰 search 濾網、bound-tests 的判定、guard kill、處置閘。不影響。
- Systems/授權與歸屬:沒碰 `_VENDORED_TOOLKIT` 與授權檔;不影響。
- Systems/測試假綠形態:第 2 輪新增的測試沒重跑;我實跑的翻紅方向見上,F1 的翻紅釘(檢查改用 Cc 路徑)目前沒被任何測試涵蓋。
- Systems/lumos-cli-lifecycle:re-inject 與 sentinel 不在這次改動內;不影響。
- `_mkdir_private_layer` 是共用的,vault-lock、dispatch-lens、bound-filter 新建目錄從 0755 變 0700:實測在 `~/.cache` 是 0755、0700 時都通過檢查,既有目錄的判準沒有變(第 1 輪放寬已撤回),所以對已存在的目錄行為不變,只影響第一次建立的權限。

最高等級:minor
