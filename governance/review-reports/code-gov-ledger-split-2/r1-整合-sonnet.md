severity: minor

## F1 hardlink 或 symlink 的 .gitignore 已含兩行時,每次 init/update 仍印「沒有自動補」警告
severity: minor
blocking: 否
引句:「            return _manual("是硬連結(追加會改到另一個名字的檔)")」
file: `scripts/lumos:21057`(_ensure_docs_gitignore;硬連結與捷徑兩個判斷都排在讀內容、比對 missing 之前)
失敗場景:
1. docs/.gitignore 是指向共用檔的硬連結,共用檔早已含 .governance-local.jsonl 與 .usage-local.jsonl。
2. 跑 lumos update(或 init),_init_additive_setup 呼叫 _ensure_docs_gitignore。
3. 實跑(/tmp/gx):回傳 [],但印出「⚠ docs/.gitignore 是硬連結……沒有自動補本機帳的忽略規則;請自己……加上」。使用者照做是白做,而且每次 update 都再印一次。
4. 修補前這條路無聲。r3 新增的警告需要先讀內容、確認缺行,才有資格叫人手動加。硬連結的內容在 nlink 檢查前讀得到,捷徑只要 git 不讀就確實缺,但硬連結不是。

## F2 doctor 教「跑 lumos update 補忽略規則」,在來源 repo 自身跑 update 不會補
severity: minor
blocking: 否
引句:「"沒被忽略的:帳在 docs/ 的跑一次 lumos update 補忽略規則(它說補不了的照它印的兩行手動加),"」
file: `scripts/lumos:20889`(root == src 的分支只 _reinject_all 後 return 0,不經 _vendor_toolchain,所以不到 _init_additive_setup 的 20835 行)
file: `scripts/lumos:2415`
失敗場景:
1. 在來源 repo(自己當來源的 clone)且根 .gitignore 沒有那兩行(例如別的 worktree 或舊 clone)。
2. doctor 報「本機帳沒被 .gitignore 忽略」,叫人跑 lumos update。
3. update 在 root==src 分支只刷新紀律區塊就回 0,docs/.gitignore 與根 .gitignore 都沒動,下次 doctor 同一行照舊。
4. 本 repo 自己因根 .gitignore 第 12 行已忽略而碰不到,消費專案不受影響;只有來源 repo 的別的 clone 會撞。

## F3 GOV_LOG_NAME 註解說「新碼用」,但同檔仍有約 10 處字面值,含 doctor 同一函式
severity: minor
blocking: 否
引句:「GOV_LOG_NAME = ".governance-log.jsonl"          # 版控帳(新碼用;舊碼的字面值照留)」
file: `scripts/lumos:2357`(同為成長段讀版控帳,仍用字面值;另有 1250、10334、11282、12503、25755、42532、42636、43508)
失敗場景:
1. 之後有人改常數(或照註解以為「新碼」都走常數)去改版控帳檔名。
2. 只有 _gate_event、_append_governance_log、合讀、S18 跟著動;doctor 成長段與全部判定類讀者仍讀舊名。
3. 讀寫分家,判定類讀者讀不到新寫的事件。
這是註解與現況對不上,目前沒有行為錯誤;降級為 minor。

## 已走過沒問題的範圍
- _gov_tail_bytes 改丟 OSError 的呼叫點:`scripts/lumos:2365` 在 doctor 成長段外層 except Exception 內,fail-open 印「跳過」;_gov_metric_events 的兩處呼叫前都有 is_file() 守衛。無漏接。
- 判定類讀者(1250、10334、11282、12503、42532、43508)只讀版控帳,不在 _GOV_LOCAL_PAIRS 的 code-loop、design-loop、fix-check 不受分流影響;_lint_new_autopass_count 數的 lint-new 自動放行也不在名單上。
- _local_ledger_writable 三處呼叫點(`scripts/lumos:1467`、1544、16325)一致;懸空捷徑、管線、資料夾都被擋。
- _BOOKKEEPING_FILES 與 cochange 排除清單都含兩個本機帳檔名。
- scaffold 寫入的忽略清單與 _LOCAL_LOG_IGNORE_LINES 同源。
- _doctor_metric_lines 在 first 為 None 時 continue(不判),與筆記「單獨一筆壞時間不算數、本機帳不在就不判」一致;測試已補第二筆。
- 筆記對照:reversibility-governance-ledger、lumos-cli-read、retrieval-ranking、reference.md 的 gov 列、分流計劃〈做法〉5、6 的「代碼審後現況」括號與程式一致。計劃〈做法〉6 正文仍寫「最舊一筆只看版控帳」,但緊接括號已更正,屬已標註的歷史句,不單列。
- init 路徑的新建 .gitignore(O_EXCL|O_NOFOLLOW)、FileExistsError 轉走既有檔路徑、唯讀與非 UTF-8 的 _manual 路徑,讀過未見矛盾。

整合面共 3 條小問題(警告誤報、update 在來源 repo 補不了、常數註解與現況不符),無阻擋項。
