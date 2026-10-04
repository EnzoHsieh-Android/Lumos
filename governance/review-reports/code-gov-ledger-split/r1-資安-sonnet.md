severity: minor

## 類1 不可信輸入流到危險操作
已看,無。新 subprocess 呼叫(git ls-files / check-ignore)用參數列表、無 shell=True;檔名 name 來自程式內常數 _LOCAL_LOG_IGNORE_LINES,不是外部輸入。帳本行用 json.loads 解析,無 pickle/eval。docs_dir 取自 env.vault.parent,不是帳本內容。

## 類2 權限與判定繞過
已看,無可利用路徑(僅縱深項見 F2)。逐項核對:判定類讀者(_codeloop_read_from_ledger、_fix_check_events、_escape_released_loops、dispositions 讀取、lint-new 計數,見 scripts/lumos 內各處)仍只讀 `docs/.governance-log.jsonl`,沒有一個被改成讀本機帳;code-loop、fix-check、design-loop 不在 _GOV_LOCAL_PAIRS 白名單,且 _gov_routes_local 要求 hard 恰為 False、gate/kind 為字串,缺欄位/型別怪異一律回 False 進版控帳(分錯偏向進版控,不偏丟)。本機帳只進統計類讀者(cmd_gov、spec-gate 摘要、doctor 度量),後者不是放行依據。

## 類3 密鑰與個資
已看,無。新增寫進本機帳的欄位與原本寫進版控帳的事件相同(gate/kind/note/nodes/ts/commit),沒有新增環境變數、使用者家目錄路徑或憑證。

## 類4 加密與傳輸
已看,無關。

## 類5 執行邊界
見 F1(縱深,推論)。hook/CI 不會執行不可信位置的檔;本機帳只被讀、被追加,不被執行。

## 類6 行動端
已看,無關。新依賴:無(僅標準庫 subprocess/json/datetime)。

## F1 本機帳與 docs/.gitignore 以 open(...,"a") 追加,未防 symlink
severity: minor
blocking: 否
引句:「        with open(gi, "ab") as f:」
file: `/home/user/Lumos/scripts/lumos:20997`
攻擊路徑(推論,四件不齊):誰=投惡意 PR / 提供惡意範本 repo 的人;入口=repo 內被版控的 symlink `docs/.gitignore` 或 `docs/.governance-local.jsonl`(git 可提交 symlink,且 force-add 可繞過忽略規則)指向 repo 外檔案;送什麼=受害者 clone 後本機執行 `lumos init/update/doctor --ci`;拿到什麼=工具以受害者權限向 symlink 目標追加固定字串(兩行忽略規則)或一行 JSON 事件。追加內容為固定常數或 JSON 開頭 `{"ts"` 的行,攻擊者無法控制成有效的 shell/authorized_keys 內容,所以實質能力僅是往別的檔尾塗髒一行,拿不到執行或外洩。其他既有帳本(.ci-log 等)同樣的寫法早已存在,本次只是增加兩個同型寫點。

## F2 被強制加入版控的本機帳會被統計與度量讀者採信
severity: minor
blocking: 否
引句:「        evs = evs + _gov_metric_events(gll)[0]」
file: `/home/user/Lumos/scripts/lumos:3973`
攻擊路徑(推論,影響限軟提醒):誰=投惡意 PR 的人;入口=PR 內用 `git add -f` 強制提交 `docs/.governance-local.jsonl`(.gitignore 擋不住已提交或 -f 的檔);送什麼=偽造的 check-* / doctor-run 事件行;拿到什麼=CI 或審查者本機跑 `lumos doctor`/`lumos gov` 時,度量型 RULE 的 retire 條件(S18)計數與 spec-gate 紅綠摘要被灌水。這些輸出皆為軟提醒/統計,不是放行推送或代碼審留痕的依據(判定類讀者只讀版控帳,見類2),所以不構成繞過;列為縱深項,因為「本機帳可信」的前提在 CI checkout 裡不成立。

總結:此次分流在判定繞過面上守住了界線(判定類讀者未動、白名單排除審查閘),只留兩個縱深類的 symlink/強制入版控疑慮,無可直接利用的洞。
