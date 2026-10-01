severity: major

# 設計審第 1 輪 — 正確性-opus

審材:凍結 spec `r1-snapshot.md`;對照 repo clone 在 `kr-r1-work-正確性-opus/repo`(HEAD 51f83721),直譯器 /opt/homebrew/bin/python3(3.14.6)。
實驗目錄:`kr-r1-work-正確性-opus/exp1`(平台根是同一 repo 的子資料夾)、`exp2`(只更新 covers 的路徑)、`exp3`(非 UTF-8、逃逸)、`exp4`(絕對路徑符號連結);`spec_check.py` 是照 spec〈做法 1〉字面寫的判斷函式模擬器(平台根取法照〈做法 1〉末段)。
另用模擬器對 rtb(`/Users/enzo/rtb-mainwt`,唯讀)實跑:73 條配方中判出 10 條非 ok(Mock-DSP 1 條 hits 4、提案收件口 4 條 hits 0、執行迴圈 5 條 hits 0),跟〈依據〉的 10 條一致;本 repo 唯一一條配方(canary-audit)判 ok,跟〈實務隱患〉一致。

## 各節

- 開頭欄位、白話段:已讀,無 finding。
- 依據:已讀,數字已在 rtb 重算對上;無 finding。
- PRIOR-ART:「同一種圍欄」不成立,見 F1、F4。
- RETIRE-IF / REVISIT:已讀,無 finding。
- 範圍:已讀,無 finding。
- 做法 1:見 F1、F4、F6。
- 做法 2:見 F2、F5。
- 做法 3:見 F6、F7。
- 條款:S1 被 F1、F2 波及(恰好 1 次卻會印提醒);S2/S4 的「設定讀不了」見 F3;S6 見 F8。
- 回退:已讀,無 finding。
- 實務隱患:見 F9。
- 誠實界線:已讀;它只寫了「工作目錄 vs 檢出版本」的差別,沒寫 F1 的「基準目錄不同」。

## F1 判斷函式的「平台根」跟 guard kill 實際用的檔案基準與圍欄不同:平台根是同一 repo 的子資料夾時,兩邊結果正好相反
severity: major
blocking: 是
引句:「這跟 `cmd_guard_kill` 的圍欄同一種判法:平台根底下的符號連結,只要解析後還在根內就照讀。」
file: `scripts/lumos:13240`
file: `scripts/lumos:13267`

1. guard kill 用 `git -C <平台根> worktree add --detach wt` 建隔離工作樹(13240 行),而 git worktree 一定是**整個 repo 的工作樹**,不是平台根那個子資料夾。之後用 `os.path.join(wt, file)` 找檔(13267 行),圍欄也是跟 `wt_real` 比(13248 行)。所以 guard kill 真正的基準是「平台根所在 git repo 的最上層」,不是平台根。只有平台根剛好就是某個 repo 的最上層時(legacy 單根、`root: "."`、或像測試裡 `other/` 自己就是一個 repo),兩者才一樣。
2. spec 寫的是 `realpath(平台根/file)` 要在 `realpath(平台根)` 底下,平台根 = `load_platforms(...)["platforms"][平台]["root"]`。多平台設定裡 `root: "sub"`、而 `sub` 跟專案在同一個 repo 時,兩邊的基準就不同。
3. 實跑(exp1:`{"default_platform":"a","platforms":{"a":{"root":"sub",...}}}`,檔在 `sub/prod.py`):
   - 配方 `--file prod.py`:guard kill 判 `drifted`(「file 開不了: …/wt/prod.py」);照 spec 的判斷函式判 `ok` → kill-add 不提醒、P2 不列,但 guard kill 一跑就斷線——正是這份計劃要抓的狀況,卻漏抓。
   - 配方 `--file sub/prod.py`:guard kill 判 `killed`;照 spec 的判斷函式判 `missing`(找 `sub/sub/prod.py`)→ kill-add 印「guard kill 跑到它時會判 drifted」、P2 每次都列,全是誤報;S1「恰好 1 次時應不印這條提醒」也被違反(guard kill 那邊是恰好 1 次)。
4. 真實環境就有這種設定:`/Users/enzo/mOrangePos/.lumos/config.json` 與 `/Users/enzo/harness/pos-ios/.lumos/config.json` 都有 `"maestro": {"root": ".maestro/"}`,跟主程式在同一個 repo。日後在 maestro 平台宣告配方,P2 會一律給錯答案。legacy 模式下,專案根(docs 的上一層)不是 git 最上層的專案(例如 monorepo 裡的子專案)也一樣。
5. 補充:CLI 說明寫 `--file` 是「相對配方平台 root」(40131 行),跟 guard kill 實際行為本來就不一致;spec 照著說明走,所以跟 guard kill 不一致。spec 要嘛把基準改成「平台根所在 repo 的最上層」(要用 `git rev-parse --show-toplevel` 或往上找 `.git`,這就跟「不碰 git」衝突,要明寫取捨),要嘛在〈誠實界線〉明講兩邊在子資料夾平台會分岔,並把 guard kill 的說明或行為修正排進另案。至少 S5 要加一個「平台根是 repo 子資料夾」的測試格,才會在這裡翻紅。

## F2 只更新 covers 的路徑會拿錯平台來驗:既有配方掛在別的平台、這次沒帶 --platform,就會印出假的提醒
severity: major
blocking: 是
引句:「在配方組好之後、判重迴圈之前跑判斷函式;不是 `ok` 就在標準錯誤印一行」
file: `scripts/lumos:12945`
file: `scripts/lumos:12966`

1. spec 規定判斷函式在「配方組好之後、判重迴圈之前」跑,又說「新增與只更新 `--covers` 兩條路都會經過這一步」。那時候手上只有新組的 `recipe`(12945 行),只有 `platform` 參數有值時才會帶 `platform` 欄。
2. 只更新 covers 的判定(`same_rest`)允許 `--platform` 不帶(`platform is None` 就算相同),而且配方身分 `_kill_recipe_key` 不含平台。所以「既有配方 platform=b,這次只帶 `--covers`、沒帶 `--platform`」會走 `updated` 分支、改的是那條 platform=b 的配方(12966 行)。
3. 實跑(exp2:平台 a 根 `.`、平台 b 根 `other/`,`lib.py` 只在 `other/`):先 `kill-add … --file lib.py --platform b` rc0,再 `kill-add … --file lib.py --covers java-concurrency`(不帶 --platform)→「✓ 只更新了既有配方的 covers」,寫回的配方是 `"platform": "b"`。照 spec 字面,判斷函式拿的是新組的 `recipe`(沒有 platform)→ 用預設平台 a → `./lib.py` 不存在 → `missing` → 印「⚠ 提醒:這條配方的原文在 lib.py …;guard kill 跑到它時會判 drifted」。這是假提醒:guard kill 用 b 的根,判得到恰好 1 次。這也違反 S1「恰好 1 次時應不印這條提醒」。反過來,兩個平台都有同名檔時,也可能拿錯的檔判成 ok,把真的失配蓋掉。
4. 改法:判斷要跑在「實際會寫進去的那條配方」上——新增時是 `recipe`,只更新 covers 時是迴圈裡找到的既有 `r`(用它的 platform)。也就是把判斷挪到判重迴圈**之後**、寫檔之前。挪過去還順便解決另一個小問題:照現在的插入點,遇到重複配方(「已經有了」擋下)或 `kill_recipes` 解析失敗(「擋下:…」)時,會先印「照舊寫入」語氣的提醒、接著又印擋下,前後矛盾。S1 要加一個「只更新 covers、配方掛在非預設平台」的測試格。

## F3 「設定檔讀不了」在程式裡大多不會丟錯:JSON 壞掉時 load_platforms 會自己退回單一設定,S2/S4 照字面寫的測試會翻紅
severity: minor
blocking: 否
引句:「設定檔讀不了:整段印一句」
file: `scripts/lumos:4519`

1. `load_platforms` 遇到 config.json 讀不了或不是合法 JSON 時,只在標準錯誤印「提醒:.lumos/config.json 讀不了(…),先用預設的單一設定跑」,然後 `cfg = {}` 退回 legacy(預設平台名 `csharp-xunit`、根 = 專案根),**不丟例外**(4517–4522 行)。只有語意錯誤(平台 >1 卻沒 default、default 指向不存在的平台、profile 名不認得、某平台不是物件)才丟 `ValueError`。
2. 所以照字面寫 S2/S4 測試的人如果用「把 config.json 寫成壞 JSON」來造「設定讀不了」,kill-add 不會印「沒驗原文」、P2 也不會印「這一段算不出來」,而是照 legacy 驗下去 → 測試紅,實作者會以為自己寫錯。
3. 這個行為跟 guard kill 一致(它也是同一支退回),所以不是錯,而是 spec 的用詞沒定義清楚。改法:把「設定檔讀不了」定義成「`load_platforms` 丟 `ValueError`」,並寫明 JSON 壞掉時會退回單一設定、照驗(跟 guard kill 同樣行為);S2、S4 的測試要用語意錯誤的設定來造。

## F4 平台根內的「絕對路徑符號連結」:spec 判 ok,guard kill 判逃逸
severity: minor
blocking: 否
引句:「`os.path.realpath(平台根/file)` 不在平台根的 realpath 底下 → `outside`(不讀檔)。」
file: `scripts/lumos:13268`

1. 符號連結如果存的是絕對路徑(例如 `prod.py -> /abs/repo/pkg/real.py`),在工作目錄裡解析後落在平台根內 → spec 判 `ok`。在 guard kill 的隔離工作樹裡,同一條連結還是指回**主工作目錄**的絕對路徑,不在 `wt_real` 底下 → guard kill 判 `error`「file 路徑逃逸 worktree(圍欄擋下)」。
2. 實跑(exp4):模擬器判 `('ok', '')`;`guard kill` 判「⚠ error … file 路徑逃逸 worktree(圍欄擋下)」。
3. 情況少見,但它直接打臉 spec「同一種判法」的說法,S5「解析後仍在根內的符號連結應照讀」照字面寫測試也測不到這個分岔。改法:在〈誠實界線〉記一句「絕對路徑的符號連結:本檢查算 ok,guard kill 在沙盒裡會判逃逸」;或在判斷函式裡,對路徑上任一層是絕對路徑連結的情況另外標註。

## F5 提醒的字面寫死了「會判 drifted」,但路徑跑出根外與非 UTF-8 時 guard kill 不是判 drifted
severity: minor
blocking: 否
引句:「guard kill 跑到它時會判 drifted——先照現在的程式改寫原文再宣告」
file: `scripts/lumos:13275`

1. S1 要求「路徑跑出平台根」也印同一行提醒。但 guard kill 遇到逃逸判的是 `error`(「file 路徑逃逸 worktree(圍欄擋下)」),不是 drifted;建議動作「改寫原文」也對不上——該改的是 `file`。
2. 非 UTF-8 的目標檔:spec 判 `missing`,提醒說「會判 drifted」;實際上 guard kill 只接 `OSError`(13275 行),`UnicodeDecodeError` 會讓整支 guard kill 當掉(exp3 實跑:Traceback … `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`),其他配方也都沒有結果。
3. 改法:提醒的後半依狀態分開寫(hits/讀不了 → drifted;outside → 「圍欄擋下」、改 file;非 UTF-8 → 「guard kill 現在會直接當掉」),或乾脆不寫 guard kill 的判定、只寫事實。

## F6 只有 file/old 列為 malformed;配方不是物件、或 platform/invariant 欄型別不對時,呼叫判斷函式之前就會先出錯,整段 P2 被吞掉
severity: minor
blocking: 否
引句:「配方不是物件、或 `file`/`old` 不是字串 → `malformed`。」
file: `scripts/lumos:13372`

1. 照〈做法 1〉末段,呼叫判斷函式**之前**要先用「配方的 `platform` 欄」算出平台根。配方如果是字串或數字(`_kill_read_recipes` 只驗外層是 JSON array),`r.get("platform")` 會先丟 `AttributeError`;`platform` 是 list 時查平台表會丟 `TypeError`(不能當 dict 的鍵);列印時要取「配方 invariant 前 30 字」,`invariant` 是 null 時 `None[:30]` 也丟 `TypeError`(guard kill 自己在 13372 行就是這樣寫的)。
2. 這些例外都會被「整段包在例外保護裡」接住 → 整段 P2 只印「這一段算不出來」,**同一次其他真的失配也全都不列**。S3 要求「格式不對…應列出那條」,這時是紅的。
3. 改法:寫明「先判是不是物件、file/old 是不是字串,再取平台」;`platform` 不是字串或空值時當作沒填(或列 malformed);`invariant` 取前 30 字前先 `str()`。S3 的測試要放一條字串配方、一條 `invariant: null` 的配方,加上一條真正失配的配方,斷言三條都有列出來。

## F7 P2 的平台根必須跟著每條配方自己的平台走;計劃沒說 load_platforms 只讀一次,也沒處理它每次呼叫都在標準錯誤印的提醒
severity: minor
blocking: 否
引句:「根 = `load_platforms(專案根)["platforms"][平台]["root"]`(專案根照 `_repo_root_from_env`,跟 guard kill 同一套)」
file: `scripts/lumos:4547`

1. `load_platforms` 每呼叫一次,只要有平台的根不存在,就印一次「⚠ 平台 '…' 的 root 不存在」(4547 行);JSON 壞掉時也會印一次「提醒:.lumos/config.json 讀不了」。如果照「每條配方跑判斷函式」的寫法,每條配方都重新呼叫一次,73 條配方的 rtb 會在 doctor 的標準錯誤重複印 73 次。
2. 改法:寫明 P2 開頭呼叫一次 `load_platforms`、結果給整段共用;kill-add 也只呼叫一次。

## F8 S6 綁的測試對「輸出不變」沒有觀測,也只有一格會因 kill-add 改擋而翻紅
severity: minor
blocking: 否
引句:「[S6] 既有 `cmd_guard_kill` 與 `cmd_guard_kill_add` 的判定、輸出與回傳碼除了多一行提醒之外應不變 [test:t_guard_kill_rc_precedence]」
file: `scripts/test_lumos.py:20177`

1. `t_guard_kill_rc_precedence` 只檢查 `guard kill` 的回傳碼,不看 kill-add 的回傳碼,也不看任何一邊的輸出文字。
2. 拿一個壞實作試:kill-add 遇到失配就擋、不寫入。四格裡,「drifted→rc2」會因為「沒有任何突變配方可跑」而照樣 rc2,繼續綠;「survived 勝 drifted→rc1」只剩 survived 那條,也照樣 rc1,繼續綠;只有「弱證據不蓋過 drifted→rc2」會翻紅。另一個壞實作:提醒印到標準輸出、或 kill-add 成功訊息被改掉 → 四格全綠。
3. 「判定與回傳碼」的主要部分 S1 自己的測試蓋得到,所以不阻擋;但 S6 宣稱的「輸出不變」目前沒有任何測試在看。改法:S6 改綁(或加綁)一支新測試,比對失配宣告前後 kill-add 的標準輸出逐字相同、標準錯誤恰好多一行 ⚠;或把 S6 的字面縮成「回傳碼」。

## F9 大檔隱患的量級寫錯:rtb 現在有 73 條配方,不是十幾條
severity: minor
blocking: 否
引句:「工具鏈與 rtb 現況各十幾條配方,量級可忽略」
file: `scripts/lumos:12850`

1. 在 `/Users/enzo/rtb-mainwt` 上用 `_kill_read_recipes` 實讀,7 篇節點(全是 system / doing,P2 都不會跳過)共 73 條配方,其中 `execution.py`、`inbox_store.py` 各被讀十幾次。
2. 結論(量級可忽略)多半還是成立,但數字錯了,日後回頭看「doctor 多花多少時間」的人會拿錯基準。改法:改成實際數字,或寫「實作時量」;順便可以寫明同一支檔在一次 doctor 裡只讀一次(依路徑快取)。

最高等級:major;blocking 共 2 條
