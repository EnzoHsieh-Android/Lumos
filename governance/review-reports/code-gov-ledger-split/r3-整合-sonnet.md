severity: minor

## F1 doctor 教的「跑 lumos update」對捷徑 .gitignore 是死路,提醒永遠消不掉
severity: minor
blocking: 否
引句:「                      "沒被忽略的:帳在 docs/ 的跑一次 lumos update 補忽略規則,其他佈局在帳檔同一層的 .gitignore 加上檔名;"」
佐證 file: `scripts/lumos:2415`(提醒文字)、`scripts/lumos:21056`(docstring 說「doctor 的本機帳提醒會叫人自己加」,但提醒第一句叫人跑 update,沒叫人自己加)、`scripts/lumos:21075`(捷徑 / 硬連結 / 非一般檔案一律 `return []`,不印任何一句)
失敗場景:
1. 消費專案的 `docs/.gitignore` 是指向別處的捷徑(例如 dotfiles 共用一份)。
2. 使用者看到 doctor 的「本機帳 .governance-local.jsonl 沒被 .gitignore 忽略」,照字面跑 `lumos update`。
3. update 經 `_init_additive_setup` 進 `_ensure_docs_gitignore`,走到 `gi.is_symlink()` 就靜默 `return []`:沒補、沒印、沒說原因。
4. 再跑 doctor,同一行提醒原樣再出現;使用者不知道 update 其實是故意不動。
5. 就算使用者照提醒後半句「在帳檔同一層的 .gitignore 加上檔名」手動加到捷徑指向的檔,git 也不認:臨時目錄實測 `docs/.gitignore -> ../real-ignore` 內容含 `.governance-local.jsonl`,`git check-ignore -q docs/.governance-local.jsonl` 回 1,並印 `unable to access 'docs/.gitignore': Too many levels of symbolic links`(git 2.43.0 不讀捷徑形式的 .gitignore)。所以兩條修法都無效,真正有效的是把捷徑換成一般檔或改寫根 `.gitignore`/`.git/info/exclude`,文字沒教。
最小重現:上面第 5 步那組指令。硬連結、唯讀、非 UTF-8 三種「不動」的情況手動加行有效,只有捷徑是死路;只是 soft 提醒、不擋,所以 minor。
判斷:提醒文字要分流(update 不動的情況改教「改寫根 .gitignore 或 .git/info/exclude」),或讓 `_ensure_docs_gitignore` 在不動時印一句原因。

## F2 計劃筆記與註解仍留著「最舊一筆」「只看版控帳」的舊句,跟 r2 後的程式相反
severity: minor
blocking: 否
引句:「治理帳檔尾只讀一遍、所有度量共用;不判:讀到的最舊一筆不早於 N 週前(暖機或檔尾被截)、[since:] 不滿 N 週、閘目前是 off。」
佐證 file: `scripts/lumos:3974`(`_doctor_metric_lines` docstring:程式現在取「第一筆」,不是最舊一筆,且依閘+種類看本機帳或版控帳)
佐證 file: `docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:75`(〈做法〉6 正文仍寫「暖機護欄用的『最舊一筆』照舊只看版控帳(避免本機帳的時間讓護欄提早放行)」,程式現況是走本機名單的組合只看本機帳第一筆;後面括號補了「r1 改掉」,但正文句沒刪,字面相反)
佐證 file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:20`(PITFALL 的修法寫「看本機帳最舊一筆」,r2 後是「帳裡第一筆、不取最小值」;`:26` 的 FLOW 與 d3 仍說治理帳 findings「僅 --ci append .governance-log.jsonl」,但 check-* warned、doctor-run 現在寫本機帳)
失敗場景:
1. 三個月後接手的人要查「為什麼本機帳不在時 S18 不判」,先讀計劃〈做法〉6 正文,得到「只看版控帳」。
2. 他照這句去改 `_doctor_metric_lines`(把 `first` 一律設成版控帳 oldest),重新引入 r1 已修的「本機帳不在時走本機帳的閘數成零筆、誤報該撤」。
3. 或看 docstring 的「最舊一筆」,以為一筆寫壞的極早時間就能讓護欄失效,而 r2 專門改成取第一筆擋這件事,他可能把它「修回」取最小值。
圖譜裡 FLOW/正文屬線索,程式為準,但這兩句直接與程式相反,而程式碼為準的讀者只會在動手前才發現。

## 已走過沒問題的範圍
- `_gov_tail_bytes`、`cmd_gov` 的 `load`、`_gov_ledger_rows_by_time` 的 `is_file()` 守門:呼叫點(`scripts/lumos:2360`、`:3946`、`:8310`、`:2993`)都通;doctor 帳增速段遇管線回 `(b"", 0)` 會走「沒有異常加速」,不崩。
- `_gov_ts` 內部擋時間出界;兩個呼叫端(合讀排序鍵、度量事件)都不再需要外包 try。
- `_usage_log` 不跟捷徑寫;`_BOOKKEEPING_FILES`(`scripts/lumos:24371`)與 cochange 排除清單(`:36703`)都含新舊檔名;`scripts/hooks/`、`governance/autonomous_loop/replay_weekly.py`、`scripts/test_autonomous_loop.py` 只讀版控帳且讀的是 code-loop/design-loop,不受分流影響。
- `_ensure_docs_gitignore`:鎖(`_vault_write_lock(docs_dir)`)內讀後追加、O_EXCL 新建、懸空捷徑走 `is_symlink()` 不被當成「不存在」而去 O_EXCL 建檔(會 EEXIST 被 OSError 吞掉,結果一致);CRLF 與缺尾換行的追加邏輯與測試對得上。
- 根 `.gitignore` 兩行與 `git check-ignore` 從 docs/ 目錄執行的相對路徑解析相容。
- `lumos-cli-read`、`retrieval-ranking` 兩篇的使用紀錄帳檔名已同步。

整合面沒有會當場壞掉的呼叫點,只有一條無效的 doctor 修法與兩處與程式相反的舊說明,都屬小問題。
