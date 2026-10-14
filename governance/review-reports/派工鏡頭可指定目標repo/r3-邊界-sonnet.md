severity: major

第三輪「邊界可執行」席報告。實驗做在臨時 repo(已刪)。部分結論直接重現過:短十六進位被同名分支搶走、目錄與符號連結被當計劃內容讀進來、標記路徑含空白時不匹配。

## 做法 1:值的形狀

severity: major
blocking: 是 — 計劃宣稱的「無歧義」不成立,同一個值可以解析到別的提交
引句:「只用十六進位,不收分支名」
問題:計劃假設十六進位字串不會被當成分支名。git 解析 `<7 碼>^{commit}` 時,同名的 ref 優先於縮寫 SHA。
具體失敗情境:
- 我在臨時 repo 建一個分支,名字就叫某提交的前 7 碼,指向另一個提交。`rev-parse --verify --quiet <7碼>^{commit}` 回的是分支指向的提交,不是原本那個。
- 設計審因此靜默讀到別的提交裡的計劃。「實務隱患」那段只承認「最壞是指到會談 repo 裡別的提交」,卻說「十六進位才沒有歧義」,兩處矛盾。
- 計劃沒有規定解析後的完整 SHA 必須以輸入為前綴,也沒有規定大小寫:git 接受大寫(實測通過),但現有 `_LENS_SHA_RE` 只收小寫。
- 計劃也沒定義縮寫碰撞(7 碼對應多個物件)時的行為,只會落到 `spec_rev_missing`,說明不準。

佐證:`scripts/lumos:47148`(`_LENS_SHA_RE`)、`scripts/lumos:47386`(`_lens_git`)

severity: major
blocking: 是 — 條款 S3 與 S6 要判斷「值是不是提交編號寫法」,但做法 1 禁止掛鉤解析,兩邊矛盾
引句:「掛鉤自己不解析、不跑 git」
問題:做法 3 要求「值不是提交編號寫法」時加繞法,做法 5 要求「用到提交編號寫法時」才記 `spec_rev`。這兩件事都得有人判斷值的形狀。
具體失敗情境:
- 若掛鉤判,就多一份 7–40 碼的正規式,跟 lumos 端的判法會漂移。
- 若靠 lumos 回報,現有 `_dispatch_lens_fail` 只印 `{"lens_fail": code}`,沒有形狀欄位,成功列也沒有;條款沒說這個欄位叫什麼。
- 判斷點其實有三處,不是兩處:`_dispatch_lens_spec_with_arch` 另外用 `Path(spec_path)` 讀檔。值是 `abc1234:docs/...` 時,它會讀檔失敗並回空 `arch_text`,目標架構段靜默消失。
- 條款 S3 與 S6 的先紅測試寫不出來:不知道該斷言掛鉤判了什麼。

佐證:`scripts/lumos:49137`、`scripts/lumos:48752`、`scripts/hooks/claude/dispatch-lens-hook.py:503`

severity: minor
blocking: 否 — 其餘值形狀在邊界上各有結果,但計劃沒寫期望,只影響測試寫法
引句:「冒號後是 repo 根起算的相對路徑、不以 `/` 開頭」
問題:以下輸入都沒有定義,測試不知道該期望什麼。
- 冒號後是空字串:`rev:` 在 git 裡指向根目錄 tree,會落到「目錄」那條缺口(見下)。
- 多個冒號:`rev:docs/a:b.md` 以第一個冒號切是對的,檔名帶冒號實測可行,但計劃沒說「以第一個冒號切」。
- `./docs/...` 開頭:git 接受(實測 rc 0),字串前綴檢查卻會拒絕。
- 路徑中段的 `./`:git 回 rc 128,所以會落到 `spec_missing`。
- 41 碼以上或 64 碼 SHA-256:正規式 `7–40` 把它們全擋掉,而 `_LENS_SHA_RE` 收 64 碼。
- NFD 路徑:macOS 預設 `core.precomposeunicode=true` 時 `cat-file -e` 通過(實測 rc 0),Linux CI 上會失敗。用 NFD 寫的測試會變成平台相依。

## 做法 2:讀取內容

severity: major
blocking: 是 — 目錄與符號連結會被當成計劃內容靜默讀進來,而 S2 的失敗碼清單是封閉的,沒有對應的代碼
引句:「`cat-file -s` 先查大小,超過 1MB 不讀」
問題:只靠 `cat-file -s` 加 `show` 不能保證讀到的是一般檔案。
具體失敗情境:
- 路徑指目錄:`cat-file -s` 回 288(tree 大小),`show` 印出目錄清單(「tree …」加檔名),整份被當計劃內容。
- 路徑是符號連結:`show` 印出連結目標字串(實測是 `../../../../../etc/hosts`),`cat-file -t` 為 blob,也通過大小檢查。工作樹那條路會 `resolve()` 後擋 repo 外,提交那條路沒有等價的檢查。
- 子模組(gitlink)的 `cat-file -s` 行為計劃也沒寫。
- 二進位檔(含 NUL 或非 UTF-8)用 `errors="replace"` 讀,不會錯,但正則掃出一堆雜訊。
- 修法方向:先 `ls-tree <提交> -- <路徑>` 看 mode 與 type,只收 `100644`/`100755` 的 blob。

severity: major
blocking: 是 — 「同值」的上限不存在,超限時的代碼與回傳碼沒列,S2 寫不出這個案例
引句:「跟工作樹那條路的上限同值;沒有上限就補一個」
問題:`cmd_dispatch_lens_spec` 的工作樹路徑是 `sp.read_text` 直接讀,沒有任何大小上限(我找過程式,沒有)。
- 「同值」沒有可對照的值,「沒有上限就補一個」又只補在提交那條路。
- 工作樹那條路仍不設限,兩條路規則不一致。
- 超過 1MB 回哪個代碼、rc 多少,失敗代碼清單裡沒有(`spec_rev_missing`、`spec_missing`、`spec_outside_repo`、`no_knowledge`)。
- 剛好 1MB(等於或超過)的邊界也沒寫。

severity: major
blocking: 是 — 「相同的檢查」不是現況,測試寫不出該期望什麼
引句:「路徑先做跟工作樹那條路相同的檢查」
問題:工作樹那條路只檢查「解析後在 repo 內」和「是檔案」,沒有「在 `docs/*-knowledge/` 底下」的限制,也沒有逐段擋 `..`(靠 `resolve()` 擋穿越)。
- 因此計劃寫的「相同」與程式不符。
- 提交那條路是新規則,卻說是沿用。
- 若實作者想讓兩條路一致,會誤動工作樹那條路的行為,破壞 S3 的「行為與現在相同」。
- 正規化也沒定義:`docs//x-knowledge/..`、`./docs/...`、反斜線路徑(Windows)用字串檢查還是 `posixpath.normpath`,結果不同。

佐證:`scripts/lumos:48999`、`scripts/lumos:49017`

severity: major
blocking: 是 — 條款說路徑要在 `docs/*-knowledge/` 底下,但實作選哪個 vault 沒定義
引句:「要在 `docs/*-knowledge/` 底下(計劃一定在圖譜裡)」
問題:現況 `vault_rel` 取 `slugs[0]`,也就是會談目錄裡排序第一個的 `docs/*-knowledge`。
- 若 repo 有兩個 knowledge 目錄,提交裡的計劃在 `b-knowledge/`,會通過路徑檢查,但連結的節點與 `lands_in` 卻去 `a-knowledge/` 找。
- `slugs` 取自會談工作樹,提交裡的 vault 可能不同(例如計劃所在分支改過 vault 名)。這時報 `no_knowledge` 還是照常讀?沒有規定。
- 這種情境測不出來,只能靠條款:建議條款規定「用路徑自己的 vault 為準」。

佐證:`scripts/lumos:49033`

## 驗收條款

severity: major
blocking: 是 — S5 的假 `_lens_git` 證明不了「只在會談 repo 跑」
引句:「假的 `_lens_git` 記錄每次呼叫的工作目錄,全部等於會談 repo 根」
問題:有四個破口。
- 它記錄的是參數 `repo_root`,不是真正的工作目錄。
- 第一個呼叫傳的是 `start = Path(repo)`,會談目錄是子目錄時不等於 repo 根。
- 好幾條 git 路徑繞過 `_lens_git`:impact 在子行程跑(新的程序,測試補丁不影響),`_git_commit_exists` 用 `subprocess.run(..., cwd=)`,`_arch_targets_at` 等也各自呼叫。假函式看不到它們。
- 這個性質本身接近恆真:提交編號沒有辦法夾帶目錄,所以不會有「去別的目錄」的路徑可被變異測出。
- 若要真的證明,需要 PATH 前置一個 `git` 外包腳本,記下 `-C` 參數與 `$PWD`,涵蓋子行程。

佐證:`scripts/lumos:6221`、`scripts/lumos:49037`

severity: major
blocking: 是 — S1 的測試層次沒定,照字面搭出來會依機器上裝的 lumos 版本紅綠不定
引句:「掛鉤應在會談目錄算出並附上固定席節點(計劃提到的程式檔與直接連結的節點)」
問題:
- 掛鉤用 `_find_lumos_script` 取可信來源的 lumos(系統安裝或 `LUMOS_HOME`),不是被測 repo 的 `scripts/lumos`。計劃又寫「不換 HOME」。結果是真掛鉤端到端跑的是舊版,提交寫法被當工作樹路徑,回 `spec_missing`。
- 既有掛鉤測試都 patch `subprocess.run`(見 `fire()`),要走 lumos 本體的測試是用 `run(v, "dispatch-lens", "--spec", …)` 或 `cmd_dispatch_lens_spec`。S1 要先定是哪一層。
- 計劃提到的程式檔用 `cat-file -e <提交>:<檔>` 判存在,但 impact 是在會談 HEAD 的圖譜算。檔只在那個提交裡存在時,impact 回空(我跑過不存在的檔:rc 0、全空),結果印「沒牽到任何家」,看起來像鏡頭壞了。夾具裡的程式檔必須也存在於會談目錄,條款才算得出節點。
- 「直接連結的節點」若是同一個 `git worktree`,節點必須存在於會談那棵樹,條款沒說。

佐證:`scripts/hooks/claude/dispatch-lens-hook.py:345`、`scripts/test_lumos.py:40965`、`scripts/test_lumos.py:42122`

severity: major
blocking: 是 — S4 的「主線還沒有」沒有可機械判的定義,也分不出死連結
引句:「只在那個分支上新開、主線還沒有的節點,列名並標「主線還沒有這篇」」
問題:
- 現況節點存在與否是看會談工作樹(`root / vault_rel / node.md`),不是看主線。計劃用詞是「主線」,做法 2 又說「從會談 repo 的圖譜讀」。
- 要分出「分支新開」與「打錯字的死連結」,得用 `cat-file -e <提交>:<vault>/<節點>.md` 判。計劃沒寫,現有程式對不存在的節點是靜默略過。
- 「列名」只有名字沒有內容,內文是否讀提交裡那份也沒寫。
- `lands_in` 走另一條路徑(`_nodehome_landing_sizes`),對分支新開的落點會印「還不存在(要新開)」,跟 S4 的標記互相矛盾。
- S4 的測試在 main 工作樹上跑時,不論實作者選哪種解讀都會通過,測不出差別。

佐證:`scripts/lumos:49056`、`scripts/lumos:48958`

severity: minor
blocking: 否 — 影響記帳可信度,但不影響注入結果
引句:「掛鉤事件 note 在用到提交編號寫法時記 `spec_rev`(成功)或 `spec_rev <失敗代碼>`」
問題:
- `_hookevent.mark(kind, note)` 只接 `ok`、`timeout`、`error` 三種 kind,且只有一個槽,後寫的覆蓋先寫的。
- 失敗時該記 `error` 嗎?使用者打錯提交編號會被算成 hook 錯誤,拉高 enforcement 的錯誤數。
- 同時逾時或鎖狀態未知的情況:note 被 `timeout` 的固定字串蓋掉,`spec_rev` 紀錄丟失。
- 成功時用 `ok` 加 note 是可行的,但 S6 沒寫期望的 kind。

佐證:`scripts/hooks/claude/_hookevent.py:111`、`scripts/hooks/claude/dispatch-lens-hook.py:503`

## 失敗代碼與標記文法

severity: minor
blocking: 否 — 屬實作時會發現並補的缺口
引句:「這三個沿用的代碼在現在的工作樹那條路也印」
問題:
- `spec_missing`、`spec_outside_repo`、`no_knowledge` 現在根本不存在於程式或 hook 的 `LENS_FAIL_REASONS`。「沿用」會讓實作者誤以為只需換名。
- 現況只印 stderr,回傳碼 2(不存在或 repo 外)與 3(沒圖譜),各代碼對應的 rc 計劃沒寫。
- `_lens_git` 逾時或 OSError 回 `None`,「提交存在」檢查遇到 `None` 該報哪個代碼?
- 大小檢查的 `cat-file -s` 同理。
- `_fail_note` 目前以 `if rng` 擋,設計審一律不進,這部分計劃有提(做法 3),但條款 S2 要同時測 lumos 回碼與掛鉤說明行兩層,建議拆成兩條。

severity: minor
blocking: 否 — 屬於標記文法的邊緣,計劃要求「不要靜默」,但這條路仍靜默
引句:「值經 `_clean_field` 消毒後顯示」
問題:`SPEC_RE` 是 `LUMOS-SPEC:\s*(\S+)\s*$`,值中間有空白就整行不匹配。
- 我驗過路徑含空白的 `LUMOS-SPEC: abc1234:docs/a-knowledge/Projects/空 白.md` 回 `None`,掛鉤整個不介入、不印說明行。計劃第 r1 記錄還寫「路徑可以有空白」。
- 值被反引號包起來時匹配成功,但整串含反引號被當作工作樹路徑,回 `spec_missing`。繞法提示卻叫使用者寫一樣的東西。
- 行首加項目符號 `- LUMOS-SPEC:` 同樣不匹配。
- 建議在條款或範本裡明說「路徑不可含空白」,或改正規式。

## 其餘節

- 「回退」「實務隱患」中「還原提交即回到只認工作樹路徑」:已讀,無 finding。
- 「不做」一節:已讀,無 finding。

最高等級 major,blocking 共 9 條(另 3 條 minor 不 blocking)。
