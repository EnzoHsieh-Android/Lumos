severity: major

# r1 資安-sonnet 報告

## F1 印給人照貼的修法指令,把筆記路徑與卷證目錄名原樣拼進 shell 指令
severity: major
blocking: 是
引句:「base = f"lumos drift fix {node} {line} --kind {kind}"」
file: `scripts/lumos:27570`
file: `scripts/lumos:27854`
攻擊路徑:
1. 誰:對消費專案送 PR / 分支的外部投稿者。入口:提交一篇檔名含 shell 元字元的筆記,例如 `Issues/a$(touch pwned).md`(git 允許這種檔名;`;`、反引號、`$()` 都可),內容是能被判成 c2/c3 的發現(open Issue 連到已收尾計劃)。
2. 受害者拉下該分支、跑 `git push`(pre-push 的 drift check)或 `lumos drift scan` / doctor Z 段。這些都走 `_drift_print_hints`,最後呼叫 `_drift_fix_hint`,把 `path` 去掉 `.md` 後不加引號拼進「lumos drift fix <節點> <行號> ...」印出。`_esc_clean` 只換控制字元,不處理 shell 元字元。
3. 送什麼進來:含 `$(...)` 或 `;` 的檔名。拿到什麼:受害者(或會照貼提示指令的 AI session,本專案的主要讀者)照貼那行,shell 展開 `$(...)`,執行攻擊者的命令,也就是在受害者機器上執行任意碼。
4. 第二個入口,同一類:c4 的 `_drift_c4_print` 把 `--new "{ev['template']}"` 放進雙引號印出。template 含 `governance/review-reports/<目錄名>`,目錄名由攻擊者的 PR 決定(用計劃名比對挑出來),目錄名含 `$(...)` 或反引號,在雙引號裡照樣展開。
重現(只到「印出的指令含未跳脫的注入」,沒做到貼進 shell 執行):
`python3 -c` 載入 scripts/lumos 後呼叫 `_drift_fix_hint("c2","Issues/a$(touch pwned).md",3)`,實際輸出:
`lumos drift fix Issues/a$(touch pwned) 3 --kind c2 --close --status done --reason "<為什麼算解決,附提交或測試>"`
`;` 的例子輸出 `lumos drift fix Verif/x;id 3 --kind c3 --status <...>`,貼進 shell 會被切成兩條指令。
限制:需要受害者照貼才觸發,不是零互動。所以能被利用,但排在有人手動執行之後。
修法方向:提示指令裡的節點用 `shlex.quote`,或檔名含非 `[\w./-]` 與 CJK 字元的節點不印指令、改印「檔名不安全,請手動處理」。c4 的 template 同樣要 quote。

## F2 c4 證據頁與成功訊息把路徑原樣印到終端,沒經 `_esc_clean`
severity: minor
blocking: 否
引句:「print(f"{cx['rel']} 第 {cx['line']} 行(c4 前提寫「還沒提交」)的證據——只列出、不寫檔:")」
file: `scripts/lumos:27847`
file: `scripts/lumos:9730`
攻擊路徑:誰:PR 投稿者。入口:筆記檔名(或卷證目錄名)含 ESC 序列或 C1 控制碼(git 允許)。送:那篇筆記出現 c4 發現,受害者跑 `lumos drift fix <節點> <行> --kind c4`。拿到:`_drift_c4_print` 以及成功行 `✓ drift fix ...{rel}`、`_drift_fix_c4` 的提示行,都直接 print 原檔名與卷證目錄名,ANSI 逃逸碼直接進終端,可清屏、改標題、偽造輸出。同檔的 `_drift_fix_preview`、`_drift_print_findings` 已用 `_esc_clean`,這幾處漏了,是同族不一致。縱深防禦類。

## 已看,無(逐類)
1. 不可信輸入流到危險操作:
   - 命令注入:全部 subprocess 都是 argv 陣列(`_lens_git`、`_plan_first_commit`),沒有 `shell=True`,git 路徑參數前都有 `--`。除 F1/F2 外已看,無。
   - 路徑穿越:`_drift_fix_target` 與 `_drift_fix_by` 要求「路徑.md」必須在 `env.notes` 裡,`--by` 也是,不會流到 repo 外。
   - 正則:`--old` 用 `str.find`,不進 regex。
   - 寫回筆記注入 frontmatter:`--reason` 與 `--old/--new` 只擋 `\n`、`\r`。`--new` 可帶 U+2028、U+0085、`\x0b` 這類 `str.splitlines()` 會切開的分隔字元,只要讀取端在別處用 `splitlines`,就能把一行拆成兩行偽造欄位或合約行。這個要靠操作者自己下參數才進得來,攻擊者沒有入口,不成立,不列 finding。
   - 反序列化:只用 `json.loads`,沒有 pickle、yaml.load、eval。
2. 權限:帳檔 `governance/drift-fixes.jsonl` 走 `_drift_ledger_path_err`(逐層不是符號連結、resolve 後在 repo 內、硬連結數為 1),攻擊者無法用符號連結讓 append 寫到 repo 外或 `.git/hooks`。筆記本體用 `_write_lf` 的 tmp 加 `os.replace`,會替換掉符號連結本身、不寫入連結目標;符號連結目錄下的筆記不在 `git ls-files` 中,乾淨檢查會擋。已看,無。
3. 密鑰與個資:修復帳記的是筆記前後行與檔路徑,沒有環境變數與憑證;記錄不新增機敏資訊。已看,無。
4. 加密:sha256 只用來判斷「檔案內容是否等於工具自己上次寫的」,不是防惡意篡改用的認證。攻擊者要偽造 `after_sha256` 需要能改帳檔,且效果只是放寬本機未提交檢查,沒有提權。已看,無。
5. 執行邊界:`LUMOS_DRIFT_FIX_FAULT` 這個測試接縫由環境變數控制,值 `ledger` 會跳過寫帳。有能力設環境變數的人本來就能執行任意碼,不算攻擊面。沒有新 hook、沒有寫使用者全域設定、沒有執行不可信位置的檔。已看,無。
6. 行動端:不適用,已看,無。
7. 新依賴:無。

最高等級:major
