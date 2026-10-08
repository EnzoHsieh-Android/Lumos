severity: major

# 代碼審 r2 正確性席(opus):漂移修法補強 修正本身

實驗環境:`git clone --shared` 到自己的臨時目錄(HEAD 5e76222d,含 b002ca4a、9a261f20 兩個修正提交),直譯器 /opt/homebrew/bin/python3(3.14)。六支新/改測試在 clone 裡全綠;另做 10 個還原翻紅實驗(見文末),每個都翻紅。

## F1 刪除守衛看改完之後那份內容判斷要不要跳,可是被刪的行屬於改之前那份:lumos update 把專案自己改過的工具檔蓋回安裝版時,專案自己加的名稱整支被跳過
severity: major
blocking: 是
引句:「②工具檔被改過、後來又改回跟安裝清單一模一樣的那次提交,刪掉的名稱不抽(內容就是安裝時那份,本來就該跳)」
file: `scripts/lumos:29598`
file: `scripts/lumos:29413`
file: `scripts/lumos:18058`
file: `scripts/lumos:18069`

1. 修正後跳過集合是 `_vendored_state(root)[0]`,看的是**工作目錄裡改完之後**的內容跟安裝清單對不對得上;但守衛只抽 `-` 行,`-` 行是**改之前那份**(a/ 側)的內容。修正自己在改名那段已經寫明「`-` 行照 a/ 來源路徑」,判內容時卻看 b/ 側,兩邊標準不一致。
2. 會碰到的情形不是少見的手動改回:`lumos update` 走 `_vendor_toolchain`,只要工具檔跟來源不一樣就 `shutil.copy2` 整支蓋掉(`scripts/lumos:18058`),接著 `_vendored_manifest_write` 把清單重寫成新版(`scripts/lumos:18069`)。所以專案只要改過任何一支工具檔(r1 外家否決席重現的正是改過的 `scripts/hooks/pre-push`),下一次 update 以後,那支檔又對得上清單,專案自己加的函式被刪掉這件事就被跳過。圖譜還在講那些名稱,守衛卻不提醒。r1 推翻只比檔名的理由正是這種情形。
3. 最小重現(加進 clone 的 test_lumos.py,用本 patch 新加的 `_dgv_repo`/`_dgv_run`):
   ```
   def t_zz_probe_update_wipes_custom():
       root, hook0 = _dgv_repo()          # HEAD 的 pre-push = hook0 + zzUserGuardFn(專案改過);清單記 hook0
       _nh_file(root, "scripts/hooks/pre-push", hook0)   # 模擬 lumos update 蓋回安裝版
       _nh_git(root, "add", "-A")
       toks, rows, diff, raw = _dgv_run(root)
       check("probe-update", "zzUserGuardFn" in toks, raw)
   ```
   輸出:diff 裡有 `-zzUserGuardFn() { :; }`,結果是 `toks: set() note: tokens=0 hits=0 secs=0.0 vendored-skip=1 files=scripts/hooks/pre-push`,`✗ probe-update`(0 passed, 1 failed)。
4. 計劃〈誠實界線〉②把這種情形講成「改回安裝版、本來就該跳」,這個理由不成立:被刪的行是專案自己寫的,不是工具的。這條也不像那段寫的那麼少見,每次 update 都會碰到。要照 a/ 側判斷,就得看改之前那份(HEAD 的內容對 HEAD 的清單)有沒有原封不動,那樣要跑 git;這條由作者決定怎麼修,但目前的版本會漏報。

## F2 c4 證據頁:同一個卷證目錄在 git 裡和磁碟上名字寫法不同時,修正後會列成兩行,而且兩行都不是「兩者」(修正前是一行「兩者」)
severity: minor
blocking: 否
引句:「兩種來源照原名對(原名不同就各列一行,見 _drift_c4_same_commit)」
file: `scripts/lumos:28008`
file: `scripts/lumos:27980`

1. 「同提交」印的是 git 裡的原名,「計劃名」印的是 `iterdir` 讀到的磁碟原名;`src = {d: "兩者" if d in by_name ...}` 拿這兩種原名逐位元組比。macOS 上 `git init` 會設 `core.precomposeunicode=true`:磁碟上用 NFD 建的目錄,git 存成 NFC,磁碟上還是 NFD。這樣同一個目錄兩邊的名字就對不上。
2. 重現:用 `_df_repo()` 建專案,讓 E.md 跟 NFD 寫法的 `governance/review-reports/done-Café/r1.md` 在同一個提交裡加進來(plan_refs 指 Done_計劃,計劃名對得上),再跑 `drift fix Verification/E 5 --kind c4`。
   - 修正後(HEAD):`['governance/review-reports/done-Café(計劃名)', 'governance/review-reports/done-Caf\xe9(同提交)']`,兩行看起來一模一樣、標的來源不同,「兩者」的第一順位也不見了。
   - 修正前(把 scripts/lumos 換回 b52d6f02):`['governance/review-reports/done-Caf\xe9(兩者)']`,1 passed。
3. docstring 說的「原名不同就各列一行」原本是指 git 裡真的有兩筆不同名字的情形;可是這裡只有一個目錄,只是 git 的寫法和磁碟的寫法不同。在 macOS(APFS 不分正規化)上,兩個 NFC 等價的 git 名字本來就指到同一個目錄。修法方向:兩種來源用 NFC 當比對鍵合併成一行,印的名字取磁碟上那一個。

## F3 註解和計劃說「整支刪掉時來源已不在工作目錄、照抽」,可是 `git rm --cached` 整支移出版控時工作目錄還留著檔,那支檔整支被跳過
severity: minor
blocking: 否
引句:「工具檔改名離開或整支刪掉時,來源已不在工作目錄 → 不算原封不動 → 照抽:寧可多掃,刻意的。」
file: `scripts/lumos:29598`

1. 判斷讀工作目錄、守衛看暫存區。`git rm --cached scripts/lumos` 是把工具檔移出版控的常見做法(移出後改用 .gitignore)。這時暫存區裡整支刪除,工作目錄的檔還在、也跟清單一致,所以被判成原封不動而跳過。
2. 重現:`_dgv_repo(names=("zzVendoredOnlyFn",))` 之後跑 `git rm -q --cached scripts/lumos` 再 `_dgv_run`,輸出 `toks: set() note: ... vendored-skip=1 files=scripts/lumos`。
3. 單看行為,跳掉工具自己的名稱是合理的。問題是程式註解、計劃〈做法〉第 5 節(「工具檔改名離開或整支刪掉時來源已不在工作目錄…照抽」)和〈誠實界線〉(「反方向(…整支刪掉…)一律照抽」)都寫成照抽,跟實際行為對不上。〈誠實界線〉①只列了「暫存的改過、工作目錄一致」這一種不一致的情形,沒列這一種。

## F4 佔位字變體:註解舉的例子和正則的行為相反;括號裡加空白再接字也會被擋
severity: minor
blocking: 否
引句:「只剩閉括號那側,sha 前面不能接英數(git-sha> 之類不算)。」
file: `scripts/lumos:14639`

1. `before = (?<![A-Za-z0-9_])` 只排除前面接英數或底線的情形。`git-sha>` 裡 `sha` 前面是 `-`,所以會被擋。實測 `_SET_COND_SLOT_VARIANTS` 對 `git-sha>` 回 `[('<sha>', 'sha>')]`,連帶 `<git-sha>`、`<commit-sha>`、`Map<K, sha>` 也都被擋。註解的例子說這種不算,兩邊至少有一邊錯。
2. 另一條註解是:「開括號那側後面不能再接字(<sha256>、<卷證目錄>、<SHA-1> 照收)」。但 `\s*(?![\w-])` 會回溯:`<卷證 目錄>` 回 `('<卷證>', '<卷證')`,`<sha 1>` 回 `('<sha>', '<sha')`,也就是中間隔一個空白再接字也會被擋。測試的照收字串裡沒有這種寫法。
3. 我這個鏡頭點名要看的變體都擋到了:`<卷證`、`卷證>`、`＜卷證＞`、`< 卷證 >`、`<SHA>`、`<Sha >`、全形空白。`<sha256>`、`<卷證目錄>`、`<SHA-1>`、`<sha1>`、`commitsha>` 都照收。沒有發現該擋卻沒擋的變體;全形拉丁字 `<ｓｈａ>` 和簡體 `<卷证>` 不擋,這兩種不在宣稱範圍內。

## F5 列不完時給的 git 指令列的比證據頁多:包含已經刪掉的目錄和 review-reports 根目錄底下的檔
severity: minor
blocking: 否
引句:「清單列不完時給人貼的 git 指令:列出完整的卷證目錄」
file: `scripts/lumos:27980`

1. `_drift_c4_same_commit` 要求路徑至少四段、而且目錄現在還在;`_drift_c4_more_cmd` 的 `git show … -- governance/review-reports/ | cut -d/ -f3` 這兩個條件都沒有。
2. 重現:在臨時 repo 的同一個提交裡加 `keep/r1.md`、`gone/r1.md`、`README.md`(都在 governance/review-reports/ 底下),下一個提交刪掉 `gone`。指令輸出 `gone keep README.md`,`_drift_c4_same_commit` 回 `['keep']`。
3. 結果是「另有 N 個沒列出」的 N 和指令列出來的數目對不上,而且人可能挑到已經不存在的 `gone` 填進範本。

## 其他點名項目的查核(沒有發現問題)

1. 改名與各種 diff 檔頭:只看 `diff --git` 後、`@@` 前的 `rename from `;內容行一定以 `+`、`-` 或空白開頭,不會被誤認。以下都用 `_delguard_parse_diff` 實際跑過或對照讀過:純改名(沒有 `@@`,下一個 `diff --git` 會重設 src)、改名加改內容(`-` 行用來源、`+` 行用目的)、新增(沒有 `-` 行,也不記跳過)、刪除(a 和 b 同一條路徑)、二進位(`Binary files` 之後不收)。複製檔頭:指令用 `-M`,就算使用者設 `diff.renames=copies` 也會被 `-M` 蓋掉,不會出現 `copy from`;真的出現時 src=cur,結果跟修正前一樣。檔名需要加引號時(控制字元、`"`),`rename from "…"` 對不上跳過清單,結果是照抽,屬於多掃的方向;工具檔名不會碰到這種情形。
2. 跳過支數:只有真的碰到 `-` 行、而且那支檔不是排除檔也不是 .md,才記來源路徑、去重。只有新增或只碰到檔頭的不算。刪除行沒有任何名稱(例如空行)也算一支,這跟「只數真的有刪除行被跳過的檔」這個宣稱一致。
3. 20 個上限:切片 `[:20]` 用的是排序後的清單;`more = len - 20` 剛好 20 個時不印;查不到 sha 時改用 `ls-files`。都符合宣稱(指令多列的問題見 F5)。
4. c1 只印一次:`one=True` 只缺一種時跟逐句那種一字不差;缺好幾種時用「、」接起來、尾巴只接一次;沒有缺的時候回空清單。settle 的兩處呼叫(`scripts/lumos:12438`、`scripts/lumos:12581`)沒帶 `one`,照舊逐句印。
5. 還原翻紅實驗(在 clone 裡改 scripts/lumos,每次先清 `__pycache__`,跑完還原並用 cmp 確認):M1 `-` 行改看目的路徑 → rename 測試 ③④② 翻紅;M2 第一遍不跳 → ④ 翻紅;M3 一碰到就記 → ③⑤ 翻紅;M4 不認 `rename from` → ③④② 翻紅;M5 c1 拿掉 `one=True` → ② 翻紅;M6 跳過集合改回 `_VENDORED_ALL` → ③⑥⑦ 翻紅;M7 同提交印 NFC → ⑤ 翻紅;M8 上限改 21 → ②④ 翻紅;M9 拿掉 `before` → 變體 ③ 翻紅;M10 拿掉 `(?![\w-])` → 變體 ③ 翻紅。每條新測試都有前置斷言證明真的走到被測的那條路,沒有走不到被測分支的假綠。不過 F1 到 F3 描述的情形沒有任何測試釘住。

## 圖譜鏡頭固定席逐條判定

- Systems/存量漂移守衛(家):c4 證據頁的 WHY 行寫「目錄照原名印,NFC 只當比對鍵」,程式確實這樣做;但同一個目錄 git 和磁碟寫法不同時會列兩行、不標兩者(F2)。那一行沒寫這個情形,不算違反合約,只是筆記少寫了這個副作用。c1 的訊息合約(兩處同一支函式、字樣相同)有維持。
- Systems/bound-tests-gate ★INVARIANT★:這次沒動閘的程式;新條款的 [test:] 都對得到測試索引裡的方法,錨點基準線也跟著測試檔更新。不影響。
- Systems/guard-kill ★INVARIANT★:沒碰 guard kill 的 rc 和 JSON 路徑。不影響。
- Systems/授權與歸屬 ★INVARIANT★:`_VENDORED_TOOLKIT` 和 `_VENDORED_ALL` 的內容沒變,修正只讀它們、沒有加項目;不會把授權檔帶進白名單。不影響。
- Systems/測試假綠形態 ★INVARIANT★:新測試的還原翻紅釘都配了前置斷言。我逐一還原 10 處都翻紅(見上一節第 5 點)。符合。
- Systems/lumos-cli-read ★INVARIANT★:search 沒動。不影響。
- Systems/lumos-cli-lifecycle ★INVARIANT★:reinject 沒動。不影響。
- Systems/design-loop ★INVARIANT★:處置閘沒動。不影響。
- 只列名的節點(pitfalls-code-loop、loop-convergence-recording、lumos-deinit、節點範圍與索引守衛、reversibility-governance-ledger、check-r-guard、cochange-guard、doctor-irreversible-hint、check-t-sentinel、lumos-refcheck、canary-audit、slim-get/install/uninstall、三篇計劃、core-invariant-baseline、judge-severity-gate):這次改的是刪除守衛的解析與跳過集合、c4 證據頁、set 的佔位字檢查、c1 訊息和說明文字。這些節點管的程式都沒被改到;`_vendored_state` 只是被多一處呼叫,本身沒改,推送前分級和每支檔有家的呼叫點不受影響。不影響。

最高等級:major
