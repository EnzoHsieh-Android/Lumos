severity: minor

# 代碼審 r1 正確性席(opus):漂移修法補強

實驗環境:`git clone --shared` 到 scratchpad/opus-r1 與 scratchpad/opus-mut(HEAD b52d6f02),直譯器 /opt/homebrew/bin/python3(3.14)。

先交代整體結論(逐項查過、判「對」的在最後一節):五件事照宣稱在做;`_delguard_parse_diff` 拆三支小函式與拆之前完全同義(下面有差分實驗);相關子集全綠(delguard 102、drift 437、guard_settle 38、set_condition 68、precommit_whitelist 31,0 紅)。只有兩條 minor:一條是 S1 測試對「去重 + 超過 3 個」釘不住,一條是 S1「中文目錄名照原樣」遇到 NFD 目錄名不成立。

## F1 同提交清單的去重與「超過 3 個才提醒」沒有測試釘著,還原後測試照綠

severity: minor
blocking: 否
引句:「if d and d in existing and d not in out:」
佐證:file: `scripts/lumos:27970`
佐證:file: `scripts/lumos:28009`
佐證:file: `scripts/test_lumos.py:53536`

1. 計劃第 1 節要求同提交清單「目錄名先 nfc、去重」,另外要「同提交清單超過 3 個時」才印「可能含別的計劃的卷證」。這兩件事是連在一起的:清單長度就是拿去比 `> 3` 的東西。
2. `t_drift_c4_reports_from_first_commit` 每個卷證目錄只放一支 `r1.md`(`for d in ("code-done", …): _nh_file(root, f"{RR}/{d}/r1.md", …)`),而且只驗了「超過 3 個 → 有提醒」這一邊,沒有驗「3 個以內 → 不提醒」。
3. 我在 opus-mut 做了兩個變異,各跑 `python3 scripts/test_lumos.py -k t_drift_c4_reports_from_first_commit`:
   - 拿掉去重(`if d and d in existing and d not in out:` 改成 `if d and d in existing:`),結果 `8 passed, 0 failed`。
   - 門檻改成有就提醒(`> 3` 改成 `> 0`),結果 `8 passed, 0 failed`。
4. 實際會壞在這裡:一次正常的代碼審,卷證目錄裡通常有很多支檔(快照 patch 加每一席各一份報告)。去重一旦被改壞,只有 1 個卷證目錄的正常提交也會被算成 >3,每一頁 c4 證據都會多印「可能含別的計劃的卷證(整批匯入或壓成一個的提交)」。人看到這句會去懷疑其實正確的清單,可是測試照樣綠。
5. 同一個缺口也碰到 [[Systems/測試假綠形態]] 那條合約(還原翻紅要配前置斷言):這一段根本沒有翻紅釘,現場(一個目錄多支檔、目錄數 ≤3)也沒有被搭出來。

## F2 NFD 寫法的卷證目錄名印出來會變成 NFC,跟條款寫的「照原樣」不符;查出來的原名沒被用到

severity: minor
blocking: 否
引句:「return {nfc(d.name): d.name for d in rr.iterdir() if d.is_dir()}」
佐證:file: `scripts/lumos:27955`
佐證:file: `scripts/lumos:28012`
佐證:file: `docs/lumos-toolchain-knowledge/Projects/漂移修法補強_計劃.md:72`

1. `_drift_c4_existing` 的說明寫它回傳 `{NFC 名: 原名}`,可是呼叫端只用到鍵:`same`、`by_name`、`src` 全是 NFC 名,最後印的是 `governance/review-reports/{_nodehome_show(d)}`,這裡的 d 是 NFC 名。原名算出來了,卻沒有地方用。改之前的程式印的是 `d.name`(磁碟上的原名)。
2. 重現(在 scratchpad/opus-exp 裡,程序內呼叫新版函式):建一個 NFD 寫法的目錄 `code-ガイド`,呼叫 `_drift_c4_existing(rr)`,得到的鍵是 `code-\xe3\x82\xac…`(NFC),值是 `code-\xe3\x82\xab\xe3\x82\x99…`(NFD)。`list(ex)[0] == os.listdir(rr)[0]` 的結果是 `False`,也就是證據頁印出來的名字,跟磁碟上那個目錄的名字位元組不同。
3. 在 macOS 上看不出影響:檔案系統比對不分正規化,git 也會把名字預先轉成 NFC。但在 Linux 的消費專案裡,NFD 目錄名(例如從別台機器帶進來的)印出來的 NFC 路徑,在磁碟上和 git 裡都找不到。人照清單挑一個填進 valid_under,寫進去的就是一條不存在的路徑。
4. 條款 [S1] 寫的是「中文目錄名照原樣」,而測試用的「審查卷證甲」沒有分解形式,NFC 和 NFD 長得一樣,所以測不出這個差別。比對繼續用 NFC 鍵沒有問題,只有印的時候該換回 `existing[d]`。

## 逐項正確性查核(判定為對的部分)

- **c4 兩種來源的收集**:我用真的 git 確認過,`git show -z --name-only --diff-filter=AR --format=` 在根提交、`git mv` 改名進來、`color.ui=always` 這三種情況下,輸出都只有 NUL 分隔的新路徑。改名進來的會列,把 `AR` 改成 `A` 的變異會讓測試翻紅(已驗)。「只留還在的」拿掉,②③翻紅;排序改成只照字母,②翻紅;「兩者/同提交」的標籤寫反,②翻紅;範本改回自動填目錄,新測試的④⑤和既有 c4 測試的②都翻紅;git 查不到時改成回空清單,⑤翻紅(以上都已驗)。
- **查不到第一次提交**:shallow、`_plan_first_commit` 逾時、這篇還沒提交,這三種情況 sha 都是 None,範本走 `_SET_COND_SLOTS[2]`,也就是字面 `<sha>`,「同提交」那段寫「查不到」。測試⑤用還沒提交的 E2 實跑驗過。
- **`lumos set` 的佔位字擋**:只要值裡含有三個字面其中之一就擋(比對分大小寫),`<SHA-1>`、`Map<K,V>`、`<src/lib>` 照收(測試⑤)。值裡沒有新增的兩個字面時,`left` 只可能是空的或只有 `<整項新內容>`,後者的訊息跟改前逐字相同。擋的順序排在空值、多行檢查之前,跟改前一樣。把常數改回只有一個字面、或讓訊息不點名是哪一個,②都翻紅(已驗)。
- **c1 和 settle 共用 `_guard_settle_missing_say`**:settle 兩處呼叫(`scripts/lumos:12438`、`:12578`)都用預設的 say=True,仍然印在標準輸出、回傳碼不變,只有句子換了措辭。repo 裡的測試和文件都沒有斷言舊句子。c1 改回自己的舊句子,③翻紅;settle 改回舊提醒,②翻紅(已驗)。
- **c3 的 `--reason` 在各種組合下**:沒給就照舊(④)。空字串與只有空白:`_drift_fix_args_err` 用的是 `is not None`,判斷前會先 strip,長度 0 就回「要一行、4 到 200 字」,回傳碼 2,檔案不動。前後帶空白的理由也是先 strip 再算長度,寫進去時同樣 strip,兩處口徑一致。含分號:只當一般文字接在行尾「;理由:a;b」,沒有任何地方會再去解析它。`<sha>`、`<卷證>`、`<為什麼…>` 這類佔位字會被 `_drift_fix_c3_args` 擋下,這一道不是多餘的:通用檢查只管長度和單行,拿掉這道③就翻紅(已驗)。三種寫法都有理由的那一段,只在其中一種寫法接理由的變異會翻紅,不 strip 的變異也翻紅,提示句的變異讓⑤翻紅(都已驗)。
- **刪除守衛怎麼判斷消費專案和工具鏈本身**:`_is_toolchain_repo(root)` 看的是 skills/lumos-project-notes/SKILL.md 在不在,跟既有四處用同一個判別鍵。消費專案傳 `_VENDORED_ALL`(全是精確檔名,沒有目錄前綴),所以同一個目錄底下、專案自己的 `scripts/hooks/own_hook.py` 照樣會抽名稱。如果消費專案的工具裝在 monorepo 的子目錄裡,路徑對不上表,就照舊抽,方向是多提醒、不會少提醒。四個變異(一律傳空集合、一律跳過、note 不記、第二遍不跳)各自讓②/③/④/⑤翻紅(已驗)。第一遍的跳過拿掉後測試照綠,但那一遍收集的東西只會被同一支檔的第二遍用到,而第二遍已經整支跳過,所以沒有行為差別,不列為問題。
- **`_delguard_parse_diff` 拆開前後是否同義**:我從 9cc20926 抽出舊函式,跟新函式(不給跳過清單)做差分比對,輸入包括本 repo 最近 400 個非合併提交的 `git show -M` diff(3 種 graph_root),以及 2 萬組隨機拼出來的 diff 片段(檔頭、`--- x` 形狀的 SQL 註解、Binary、vault/.md/排除路徑、`/dev/null` 混著出現)。共 41200 組,`tokens` 與 `vault_diffs` 全部相同,`vendored_skipped` 全部是空的。
- **治理事件 note 的尾巴**:在 scripts/lumos 和 governance/ 底下,找不到任何會解析 delguard note 的程式(`gov` 只拿 gate 和 kind 來折疊),所以多加的 ` vendored-skip=… files=…` 不會弄壞讀帳的地方。

## 圖譜鏡頭固定席逐條判定

- [[Systems/存量漂移守衛]](家):這次新增的 WHY 行和 TEST 清單,跟程式行為對得上。c4 只列證據與範本,卷證一律放佔位字;c3 可以帶 `--reason`。不影響。F1、F2 落在它管的 c4 證據頁。
- [[Systems/bound-tests-gate]] ★INVARIANT★(code-loop check 會逐支真跑綁定測試):這份 diff 沒有動 code-loop check 和固定席的計算,只是多了新的綁定測試,這些測試都綠。不影響。
- [[Systems/guard-kill]] 兩條 ★INVARIANT★(guard kill 的回傳碼優先序、--json 輸出純度):diff 只改了 guard settle 找不到預告句時的提醒字樣(settle 路徑,印在標準輸出),沒有碰 guard kill。FACT 改寫成 WHY 只是筆記形狀的調整。不影響。
- [[Systems/授權與歸屬]] ★INVARIANT★(授權檔永遠不進 `_VENDORED_TOOLKIT`、檔頭要有 SPDX):diff 只讀 `_VENDORED_ALL`,沒有增減表裡的項目。不影響。
- [[Systems/測試假綠形態]] ★INVARIANT★(還原翻紅要配前置斷言):五支新測試都有「現場成立」的前置斷言(S1 的①確認 R/A 狀態,S3 的②③確認前置,S4 的①,S5 的①確認 diff 裡真的有刪除行、檔案真的在清單上),我逐一變異,都真的翻紅。例外是 F1:去重和門檻那一段沒有翻紅釘。
- [[Systems/lumos-cli-read]] ★INVARIANT★(search 排除 superseded)、[[Systems/lumos-cli-lifecycle]] ★INVARIANT★(re-inject 保留 sentinel 以外的內容)、[[Systems/design-loop]] ★INVARIANT★(處置閘第五步):diff 沒有碰 search、re-inject、loop 處置閘的程式。不影響。
- 只列名的那一組(pitfalls-code-loop、loop-convergence-recording、lumos-deinit、節點範圍與索引守衛、reversibility-governance-ledger、check-r-guard、cochange-guard、doctor-irreversible-hint、check-t-sentinel、lumos-refcheck、canary-audit、slim-get/install/uninstall、規格落成可驗收條件、雙向門放行、逃逸自動記、core-invariant-baseline、judge-severity-gate):diff 動到的函式只有 drift fix 的 c1/c3/c4、`_set_conditions_locked`、`_guard_settle_missing_say`、delguard 的解析與記帳,另外還有錨點基準線(測試檔指紋)。lumos-deinit 和 slim 系列共用 `_VENDORED_TOOLKIT`,但這份 diff 只讀不改。其他節點的程式碼路徑都沒有碰到。一律判不影響。

最高等級:minor
