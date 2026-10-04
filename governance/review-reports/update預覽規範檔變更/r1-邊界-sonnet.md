severity: major

固定席:派工尾端沒有附任何合約或事故節點,所以沒有固定席可判。

## F1 預覽結尾教人跑的套用指令丟掉 --source,會套用到另一個版本
severity: major
blocking: 是 不改的話,用 --source 預覽的人照指令套用,裝進專案的是預設來源的另一版,實作者照字面做出的預覽/套用對不上。
引句:「結尾印「確認後跑 `lumos update --no-pull` 套用剛才預覽的版本」」
file: `/home/user/Lumos/scripts/lumos:20495`
`_lumos_src` 的優先序是 --source,其次 $LUMOS_HOME,最後 ~/harness/lumos-toolchain。極端情況:使用者跑 `lumos update --dry-run --source /tmp/src-x`,結尾卻叫他跑不帶 --source 的 `lumos update --no-pull`,實際會讀預設來源。S2、S3 要求預覽與套用一致,這個情境下必然不一致,而且 spec 的四條測試都沒有用 --source。結尾指令必須回放 --source;要不要回放 --allow-stale 也得講。

## F2 拉完來源後預覽仍是舊程式碼在算,和下一次套用用的程式不同
severity: major
⚠
blocking: 是 做法 1 宣稱預覽的就是接下來套用的那一版,但在 lumos 本體就是來源 clone 的常見安裝下這句不成立。
引句:「這樣預覽的就是接下來要套用的那一版。拉的只是工具來源那份 clone,不是專案。」
file: `/home/user/Lumos/scripts/lumos:20859`
預覽行程先 git pull,然後仍用已載入記憶體的舊版 `_VENDORED_TOOLKIT`、`_VENDORED_TREE_FILES`、`_reinject_claude_block` 與 `LUMOS_VERSION` 計算。接著跑 `lumos update --no-pull` 時,若 `lumos` 指向來源 clone(install 建的 symlink 就是這樣),跑的是剛拉下來的新程式。結果是:START 行版本戳(`_START_TEMPLATE.format(version=LUMOS_VERSION)`)、工具檔清單、區塊算法都可能在兩次之間換掉,S2 要求的「與真跑寫進內容一致」在真實用法下不成立。⚠ 我沒有實測這條 symlink 路徑;依據是 `_START_TEMPLATE` 與清單都在行程內以常數取值。spec 要嘛承認這個天花板並寫進預覽結尾,要嘛預覽在拉到新提交時提示「請重跑預覽」。四條測試全用 --no-pull,抓不到這個。

## F3 created 與 appended 兩種狀態沒有任何內容預覽,S2 也沒涵蓋
severity: major
blocking: 是 這個功能存在的理由是讓使用者同意規範檔的改動,最大的一類改動(整段紀律區塊新接上去)卻只印一句話,實作者會做出不達目的的預覽。
引句:「目標檔不存在(會新建)、有檔但沒有區塊(會接上)、區塊標記壞掉(不會自動改)也各講一句。」
file: `/home/user/Lumos/scripts/lumos:20311`
`_reinject_claude_block` 只有 updated 帶 diff,created/appended 回 diff=None,所以照字面實作只會印「會新建」或「會接上」。但 appended 是把約 5KB 的整段區塊寫進使用者既有的 AGENTS.md,而且 AGENTS 檔是插在第一個 # 標題之後(程式註解寫明為了 Codex 32KiB 截斷),CLAUDE.md 則接檔尾。位置、內容使用者都看不到。同一句也漏了「來源範本不存在」這個第五態(見 F4)。S2 的前提只講「來源範本跟現有區塊不同」,只涵蓋 updated;created/appended/broken 沒有任何驗收條款。

## F4 來源沒有範本檔時,預覽與真跑算出不同結果
severity: major
blocking: 是 預覽會說「沒有範本、不會改」,真跑卻用專案裡舊範本改寫規範檔,預覽誤導了同意。
引句:「所以改從來源的範本算。」
file: `/home/user/Lumos/scripts/lumos:20266`
`_vendor_toolchain` 的自癒迴圈遇到 `not s.exists()` 就 continue,專案裡舊的 `scripts/templates/graph-discipline.md` 保留不動,隨後 `_reinject_all` 讀的是專案裡那份舊範本、照常改寫。預覽改讀來源則得到 no_template。反向情況也有:來源有、專案沒有範本時沒問題。spec 沒定義來源缺範本時預覽該走哪條,且專案的舊範本是否存在決定了真跑結果。要寫成「來源缺檔就退回專案現有那份」,並補條款。

## F5 非 UTF-8、無法讀取的目標檔會讓預覽崩潰,回傳碼落在 spec 規定的 0 或 2 之外
severity: major
blocking: 是 spec 的回傳碼只列 0 與 2,預覽碰到非 UTF-8 的 CLAUDE.md 會丟例外退出,而且是在使用者最需要預覽的專案上。
引句:「預覽成功回 0;來源無效、拉不下來照真的 update 的規矩回 2。」
file: `/home/user/Lumos/scripts/lumos:20336`
目標檔讀取是 `raw.decode("utf-8")`,沒有 errors 參數也沒有 try。Big5、UTF-16 的 CLAUDE.md 會 UnicodeDecodeError,目標是目錄或權限不足則是 OSError。真的 update 這時已經把工具檔都換了才炸,屬於既有缺口,但預覽既然把這段拆成「算出新內容」,就必須規定這種檔印什麼、回幾。spec 的回傳碼、做法 3 的四態(新建/接上/壞掉/更新)都沒有「無法解碼」這一態。

## F6 預覽的差異只含區塊,但真跑 updated 會整檔重寫(CRLF、BOM、孤立 CR 全被正規化)
severity: minor
blocking: 否 不影響內容判讀,只是「完整差異」這個詞對 CRLF 專案是不實的。
引句:「所以每個目標檔都印完整差異。」
file: `/home/user/Lumos/scripts/lumos:20336`
讀入時去 BOM、`\r\n`、`\r` 都換成 `\n`,updated 時 `_write_lf` 整檔寫回。Windows 換行專案的 CLAUDE.md 在 updated 時每一行都變,但 `ri.diff` 只有區塊的 unified diff。相反地,區塊內容沒變的 CRLF 檔是 unchanged、不寫檔、不正規化。預覽要嘛加一句「整檔換行會轉成 LF」,要嘛 S2 把「一致」限定為區塊內容。

## F7 工具檔清單在 Windows 換行專案裡會把全部檔列成會換新
severity: minor
blocking: 否 結果與真跑一致,只是訊息噪音大。
引句:「同一種比法(逐位元組比),列出會被換新或新增的檔。」
file: `/home/user/Lumos/scripts/lumos:20897`
`filecmp.cmp(shallow=False)` 逐位元組比,autocrlf 專案的工具檔與來源只差換行就全部不等,預覽會把約 20 檔列為「會換新」,看不出實質變動。vendored.json 指紋反而是換行正規化後比(`_vendored_digest`)。預覽可標「僅換行差異」,也可以只在摘要裡講一句,二擇一寫進 spec。另外只差執行位元(chmod)的檔不會被比出來,真跑也不會補,維持一致。

## F8 「其餘動作只列名」漏列 .lumos/vendored.json 與 docs/.gitignore 的寫入
severity: minor
blocking: 否 專案裡會被動的檔比預覽宣稱的多,影響同意的完整性但不致壞系統。
引句:「補設定骨架與忽略規則、設定 hooks 路徑、同步全域 hooks——這些不改規範檔,列一行「套用時還會做」就好。」
file: `/home/user/Lumos/scripts/lumos:20614`
真跑還會在結尾呼叫 `_vendored_manifest_write` 寫 `.lumos/vendored.json`,這個動作不在這三項裡。另外 `_sync_global_from_project` 動的是 ~/.claude 全域,不是專案;預覽的對象是「專案」,使用者看不到全域也會被改的字樣,應該明確分成專案內與機器全域兩行。

## F9 S1 守不到預覽誤呼叫全域同步,也沒規定怎麼比「每一個檔」
severity: major
blocking: 是 做法 5 的前提是預覽不碰全域 hooks,但驗收只比專案目錄,有人在預覽路徑誤呼叫 `_sync_global_from_project`、`_install_skills` 一類函式,S1 不會翻紅。
引句:「專案工作目錄裡的每一個檔 應 一個位元組都不變,`git config core.hooksPath` 應 不變」
file: `/home/user/Lumos/scripts/lumos:20884`
缺的邊界:(a) 檔案集合要含「新增與刪除」,只比既有檔位元組抓不到新建的 `.lumos/vendored.json`、`docs/.gitignore`;(b) `.git` 內容要明確排除或納入(git 指令會刷新 index);(c) 測試環境的 HOME 要隔離並比對 ~/.claude、~/.agents 前後快照,這是全域寫入唯一能被守的地方;(d) `core.hooksPath` 初值要設成非 lumos 路徑,否則已指向 scripts/hooks 時真跑也不動,測試永遠綠;(e) 只測 --no-pull,帶拉取的路徑沒測,而拉取會對來源做 checkout 與備份,應在 S1 說明「只有來源會被動」。

## F10 S4 的「沒有任何規範檔會變」與版本戳、broken、no_template 的關係沒定義
severity: minor
blocking: 否 但測試寫得出來的前提不明,實作會各自詮釋。
引句:「當沒有任何規範檔會變時,預覽 應 明講「這次 update 不會改規範檔」」
file: `/home/user/Lumos/scripts/lumos:20381`
`_reinject_claude_block` 把 START 行版本戳不同也算 updated,所以每次升版後都會有「區塊內容沒變、只有版本號變」的 updated,這算不算「會變」?全部目標都是 sentinel_broken 時,「不會改」字面為真,卻會掩蓋「其實有壞標記需要處理」,S4 要不要在 broken 時改講別的?no_template 同理。條款要把三態都列進去。另外測試前提要把專案 START 行版本戳設成與 `LUMOS_VERSION` 相同,否則 t_update_dry_run_no_rule_change 在每次升版後自己翻紅。

## F11 來源 repo 自身的預覽:回傳碼與 --no-pull、LUMOS_PROBE 的行為沒講
severity: minor
blocking: 否
引句:「真的 update 在來源 repo 只刷新紀律區塊;`--dry-run` 就只預覽紀律區塊。」
file: `/home/user/Lumos/scripts/lumos:20931`
真的 update 在這條路徑遇到 sentinel_broken 或 no_template 回 2,預覽的回傳碼規則(做法 7)只講 0 與「來源無效、拉不下來」,沒說這種情況。這條路徑不 pull,所以「結尾印教人加 --no-pull」那句在這裡不適用,spec 沒說省略。`_refuse_if_probe("update")` 在 cmd_update 最前面,LUMOS_PROBE=1 時唯讀預覽也會被擋回 2,是否要放行預覽沒定義。S5 的測試前提要求來源 repo 的 CLAUDE.md 與 AGENTS 都已有區塊,否則 created/appended 的預覽也落在這條路徑,需要一條對照。

## 逐類實務隱患補述
- 預覽跟套用對不上:F1、F2、F4 三處成立,spec 只防了「再拉新」。
- 預覽不小心寫檔:唯一寫入點拆分的設計成立,風險落在 F9 的守衛盲區。
- 目標檔邊界:無 AGENTS 檔、AGENTS.override.md 並存、CRLF、BOM、非 UTF-8、broken、no_template 的覆蓋見 F3、F5、F6、F10。已確認 `_agents_target` 在預覽與真跑算法相同。
- 金流、對外送出、不可逆、守衛面:同意 spec 的「已排除」判斷,預覽路徑本身無金流或對外送出;拉取是既有行為。

最嚴重等級為 major,共 6 條 blocking(F1、F2、F3、F4、F5、F9)。
