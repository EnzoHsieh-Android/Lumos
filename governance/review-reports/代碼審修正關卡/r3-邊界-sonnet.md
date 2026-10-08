severity: major

# r3 邊界-sonnet 報告(鏡頭:邊界與輸入)

實驗環境:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/fg-r3-work-邊界-sonnet/`(`t`、`u`、`v` 是拋棄式小 repo,`repo` 是 negguard 的 shared clone)。

## F1 預算剩餘時間夾住的逾時,在紅樹會被誤算成「逾時算紅」
severity: major
blocking: 是
引句:「每支測試的逾時取「自己的逾時」與「剩下的時間」較小的;用完時還沒跑的測試與項目不跑、這項判不過」
引句:「其中因逾時判紅的(修卡死類的修正,修之前跑不完)照樣算過,輸出標「逾時算紅」」
file: `scripts/lumos:38606`(`_run_bound_tests` 沒有逾時參數,只讀環境變數 `LUMOS_TEST_TIMEOUT`)
file: `scripts/lumos:38626`(`float(env or "180") or 0) or None`:字串 "0" 變成「不限」)
file: `scripts/lumos:38650`(逾時一律回 verdict `red`、detail 「超時(>Ns)」)
1. 實作只能靠改環境變數把「剩下的時間」塞進 `_run_bound_tests`;逾時時它只回 `red`+「超時」,看不出是測試自己的 180 秒到了、還是被預算夾短的。
2. 場景:預算剩 20 秒,紅樹裡一支正常要跑 30 秒的測試(修正拿掉後它其實會綠)被夾成 20 秒逾時 → 判紅 → 「逾時算紅」過 → 先紅那項放行,是放錯。接著第 6 項只看「還沒跑的」,這支已經跑了,若它是最後一支,第 6 項也過,整次回 0。
3. 另一個邊界:剩餘時間若被格式化成 `"0"`(例如 `str(int(0.6))`),`or 0 → None` 變成不限時,在預算幾乎耗盡時反而無上限地跑。
4. 規格沒寫:被預算夾短(夾後逾時 < 自己的逾時)而逾時的測試,必須判「超過總時間、沒驗完」而不能算紅;也沒寫怎麼把逾時傳進 `_run_bound_tests`(簽名要加參數,或就地改環境變數且剩餘值必須大於 0 並保留小數)。
未實測整條,依據是讀碼(上述三處行為已逐行讀過)。

## F2 「簿記檔」定義跟代碼審留痕實際判法不一致,S8 的「只改筆記不印」無法靠沿用單一源達成
severity: major
blocking: 是
引句:「代碼審留痕認定「改了不算改程式」的檔——`_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS` 列的帳本與卷證,加圖譜筆記資料夾。本計劃凡說「程式有沒有改」都照它判,不另訂。」
引句:「事件之後只改了圖譜筆記或帳本時不印」
file: `scripts/lumos:39233`(`_codeloop_record_valid_ex`:只有全部落在 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 才豁免,圖譜筆記資料夾沒列;簿記資料夾底下的程式還要過 `_codeloop_bookkeeping_code`,看檔案模式與 `#!`)
file: `scripts/lumos:6885`(「加筆記資料夾」的版本是小改動閘 `_sc_changed_files` 的 `vrel`,是另一份判準)
實驗(clone 裡,`_codeloop_record_valid`):
```
note only: (False, '記錄 sha 8516d0b9 之後動了代碼(非純簿記增量)')      # 只新增 docs/x-knowledge/Systems/n.md
replay py: (False, '記錄 sha 6fa61590 之後動了代碼(非純簿記增量)')      # 新增 governance/replay/evil.py
```
1. 留痕那支單一源其實不豁免圖譜筆記;「加圖譜筆記資料夾」是從小改動閘借來的。所以「照它判,不另訂」跟「加筆記」互相矛盾:照單一源實作,S8 「只改圖譜筆記不印」會失敗(筆記改動被當程式);另手寫「清單+筆記」就是第二套判準。
2. `loop next` 寫的是 `git diff --no-renames --name-only -z` 再套名單。這種只有路徑的做法會把 `governance/review-reports/` 底下的 `.py`、可執行檔、`#!` 腳本當簿記(靜默),跟 S8 「含 governance/ 底下的程式也印」自己矛盾;要判對需要 `--raw` 取模式並呼叫 `_codeloop_bookkeeping_code`。
3. 圖譜筆記資料夾位置怎麼取沒寫:`_sc_changed_files` 是 `find_vault` 後算相對 repo 根的 `vrel`;多 vault、vault 在 repo 外、沒有 vault 的消費專案(`vrel=None`)各怎麼辦,規格沒說。
4. 重新命名:`loop next` 用 `--no-renames` 沒問題(刪+增各比一次);但第 103 行 `git status --porcelain -z` 的改名條目是 `R  新\0舊\0` 兩個路徑,規格有說兩個都看,這點已讀、可行。

## F3 `fixed` 的檔必須存在於修正後的提交:修正若是刪檔或改名,無法列、紅樹也無法把它復原
severity: major
blocking: 是
引句:「檔案要在修正後的提交裡,函式那段要在那支檔裡出現、前後不接英數字或底線」
引句:「用 git 換,符號連結、執行權限、二進位檔照 git 的規則處理,不會穿過連結寫到工作樹外」
實驗(`t`,`git checkout <base> -- <path>`):
```
new.py (base 沒有):  error: pathspec 'new.py' did not match any file(s) known to git  rc=1
sub/x.py (fixed 已刪、base 有): rc=0,檔案被復原
case.py (只差大小寫): error: pathspec ... rc=1
```
1. 修正本身就是「刪掉有問題的檔/端點」或「改名」時,被刪的舊路徑在修正後的提交不存在,`at` 驗不過;「每組至少一條 fixed 路徑」讓這組永遠過不了。這時紅樹也沒機會把被刪的檔換回 base(它是最該換的)。改名只能列新路徑,紅樹把新檔刪掉,舊路徑仍缺 → 紅是因為整個模組不見,不是修正被拿掉。
2. 規格寫「`base` 沒有那支檔就刪掉」,但字面指令 `git checkout <base> -- <檔>` 在 base 沒有該檔時直接 rc=1 報錯,必須先偵測再 `git rm`/刪檔,規格沒這一步;若實作者照字面把 rc≠0 當「換不了 → 不過」,每一個新增檔的修正都會被擋。
3. 大小寫只差一點:macOS 上檔案系統不分大小寫,`os.path.exists` 會過、`git checkout` 找不到(如上 rc=1),存在性檢查要用 git 的樹,不能用檔案系統。

## F4 路徑直接當 git pathspec 會被當萬用字元,多換回沒列的檔
severity: minor
blocking: 否
引句:「路徑一律用 `-z` 取得、不經 git 的引號跳脫(中文、空白檔名照原樣比)」
實驗(`u`,檔案 `a[1].py`、`a1.py`、`a*.py` 都在 base):
```
git checkout <base> -- 'a[1].py'  →  M a1.py 與 M a[1].py(沒列的 a1.py 也被換回)
git checkout <base> -- 'a*.py'    →  三支全換回
git --literal-pathspecs checkout <base> -- 'a[1].py'  →  只有 a[1].py
```
1. 中文與空白檔名本身沒問題(實測 `中 文 空.py` rc=0 正常),但 `[id].vue`、`[slug]/page.tsx` 這類路由檔名(Next/Nuxt/SvelteKit 常見)與 `*`、`?` 會被當 glob;同目錄剛好有單字元同型檔名時,紅樹會多換回一支沒列的檔,違反「紅樹 = 修正後減掉紀錄列的修正,其他一律不動」。
2. 同理 `at` 若寫成資料夾,`git checkout <base> -- dir` 會成功(實測 rc=0)但不會刪掉修正後新增在裡面的檔;規格只對「base 那邊是資料夾」說判不過,沒說「`fixed` 的 `at` 是資料夾」。D/F 衝突(修正把資料夾換成檔)實測 git 也能換,跟「資料夾換不了 → 不過」不符。
3. `base..修正後 改動` 與存在檢查若也用 pathspec 版的 `git diff -- <path>`,同樣被 glob 影響。規格應寫「所有帶使用者路徑的 git 呼叫加 `--literal-pathspecs`」。

## F5 殘骸清理:要比對的「資料夾名」在哪一層沒寫清楚
severity: minor
blocking: 否
引句:「只認「位在系統暫存資料夾底下、資料夾名以修正關卡前綴開頭」的」
file: `scripts/lumos:14202`(guard kill 現況:`tmp_parent=mkdtemp(prefix=...)`,worktree 路徑是 `tmp_parent/wt`)
1. `git worktree list --porcelain` 列出的是 `<tmp>/<前綴XXXX>/wt`,最後一層叫 `wt`、前綴在上一層;標記檔也是寫在 `tmp_parent`(上一層)。照字面對「worktree 路徑的資料夾名」比前綴會永遠對不上,S10 的清理測試會紅。需要寫成「worktree 的上一層」。
2. 在 `mkdtemp` 之後、`worktree add` 之前被 SIGKILL:資料夾與標記檔都在,但 `git worktree list` 沒有它,掃描只走 worktree 清單所以永遠不清(空資料夾外洩)。
3. 行程編號被重用時規格選「保守當還在」,但標記檔有「建立時間」卻沒拿來設上限;被重用的 pid 讓殘骸永遠不清。
4. 實測:Python 的 `tempfile` 在第一次用過之後就快取暫存根,事後改 `os.environ["TMPDIR"]` 不影響行程內的 `mkdtemp`(輸出 `x-...` 與 `y-...` 都落在 `/var/folders/.../T/`)。所以工作樹仍建在系統暫存下(跟清理規則相符),但「TMPDIR 指到修正關卡自己的暫存資料夾」只對子行程有效;被 SIGKILL 時那個修正關卡自己的 TMPDIR 資料夾(內含測試現場)沒有任何掃描會清它。規格若要它被清,要有同樣的標記與掃描。

## F6 `--record-template` 與 `base` 取得:派工單壞掉或欄位怪時沒規定
severity: minor
blocking: 否
引句:「`base` 從派工單的 `base_commit` 帶入(沒有就留空)」
引句:「可以填任何認得出的寫法(短 sha、分支名),工具一律先轉成 40 碼再用、事件記 40 碼」
1. 只規定「沒有欄位就留空」。派工單不存在、不是合法 JSON、解析過深、頂層不是物件、`base_commit` 是數字/陣列/含空白換行的字串時,樣板該留空並警告,還是失敗?`--record-template` 說「不跑其他先決條件」,壞派工單若丟例外就連樣板都拿不到。2026-10-02 前的所有既有迴圈派工單都沒有 `base_commit`,這是常態不是邊角。
2. `base` 轉 40 碼:`base` 若以 `-` 開頭(`--help`)會被當選項;`A..B` 會印兩行;`HEAD:檔` 解成 blob。需寫成 `git rev-parse --verify --end-of-options "<x>^{commit}"`,且 `--end-of-options` 要求 git ≥ 2.24。
3. `tests` 欄位若寫成字串而不是清單,逐字元迭代會變成一個字一支測試;規格只說 JSON 形狀不對回 2,沒列欄位型別驗證,「紀錄完整」那項也沒有檢查型別。

## F7 設定欄位邊界:`budget_sec`、`link_dirs`
severity: minor
blocking: 否
引句:「0、負數、不是數字都用預設並印一行警告」
引句:「相對 repo 頂的路徑清單,例如 `["node_modules", "ios/Pods"]`」
file: `scripts/lumos:23630`(`_lint_link_deps` 寫法:`src.is_dir() and not link.exists()` 才連,失敗的 `OSError` 靜默略過)
1. `budget_sec`:JSON 讀得進 `NaN`、`Infinity`(實測 `json.loads('{"a":NaN,"b":Infinity,"c":true}')` 都接受);NaN 通過「>0」比較且讓 `remaining<=0` 永遠 False,等於無預算;`true` 被當 1 秒;極小值(0.001)讓第一支測試立刻被夾到逾時。規格只列 0、負數、非數字。
2. `link_dirs`:含 `..` 時 `snap_dir/".."/x` 會在工作樹之外(暫存資料夾的兄弟位置)建連結,不會被收工作樹清掉;絕對路徑經 `Path /` 運算會取代前綴(`link` 變成原路徑本身,「已存在」就略過,無聲不連);指向不存在的資料夾或巢狀的父層缺失時靜默不連,結果是綠樹找不到依賴,輸出只有一般「綠樹判紅」的字樣,規格雖有加提示但沒要求在宣告了卻沒連成時明講。與受版控路徑撞名(例如已入版控的 `Pods/`)會因為 `link.exists()` 而不連,看起來正常;規格沒說這時要不要警告。
3. 實測 `v`:若連結位置上有受版控資料夾且 `fixed` 列了其底下的檔,`git checkout <base> -- deps/m.py` 會把連結換成真資料夾,主工作目錄內容沒被動(`MAINCONTENT` 未變),規格「不會穿過連結寫到工作樹外」這點成立。

## F8 紅樹是「整輪所有 `fixed` 檔一起換回」,不是每組各自
severity: minor
blocking: 否
引句:「把這輪修正紀錄所有 `fixed` 路徑的檔,在紅樹裡用 `git checkout <base> -- <檔>` 換回 `base` 的內容」
1. 同一支檔被兩組各列一次實測無害(重複 `git checkout` rc=0)。但 G1 的測試在紅樹裡也會看到 G2 被換回的檔;G1 的測試若只是因為 G2 那支檔缺了新符號而 ImportError 變紅,「先紅」就過,並沒有證明它守的是 G1 自己的修正。規格把這個取捨當設計接受,但〈實務隱患〉只寫了漏列方向,沒寫「多組互相牽連時紅是假紅」的方向。
2. 規格的「修正動到幾支檔,就要把幾支檔都列成 `fixed`」字面讀會把新增測試的測試檔(例:本 repo 全部測試在單一檔 `scripts/test_lumos.py`)也包含;被列為 `fixed` 的測試檔會被換回 base,新測試因此不存在 → 一律判「選不到」。上一句有「測試、夾具…一律留修正後的版本」,但沒有機械檢查擋「把測試檔列成 fixed」,也沒有提示訊息指向這個常見誤填。

## 沒問題的節
- 〈共用的隔離工作樹〉、〈上線〉、〈回退〉、第 2 步各段:已讀,無 finding(跟本鏡頭相關的輸入邊界沒有新洞)。
- 同一支檔被兩組各列、中文與空白檔名、符號連結(`git checkout` 還原連結本身,不穿過)、絕對路徑與 `..`(git 自己拒絕,rc=128)、空字串路徑(rc=128):實測,行為跟規格預期一致,規格不用改。

最高等級:major,blocking 共 3 條
