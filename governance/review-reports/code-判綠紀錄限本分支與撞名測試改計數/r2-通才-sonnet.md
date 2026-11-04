severity: minor

通才席第 2 輪報告。零 blocker、零 major,找到 2 條 minor,都不擋。

我實際用的方法:在 `/tmp/lumos-seat-work/.../通才-sonnet/` 用 `git clone --shared` 取得兩版,逐道改壞再跑測試。另外直接載入兩版的 `scripts/lumos`,對自建的部分複製 repo 呼叫 `_redbase_branch_rows`。

1. 治理帳被忽略的專案若是部分複製(partial clone),判綠過濾整批放棄,本計劃要修的跨分支漏洞在這種專案完全沒修。修前(409ab14)對這種 repo 是正確丟掉別分支的判綠。
引句:「        if i >= _REDBASE_ANC_CAP or repo_kind() == "partial":」
severity: minor
blocking: 否
- **失敗場景**
  - 治理帳被忽略,repo 設了 `extensions.partialClone`(例如 blobless clone,所有 commit 物件都在本機)。
  - 別條分支留下的判綠,其 `head_sha` 在本機存在、但不是目前 HEAD 的祖先,而且紀錄沒有 ref。
  - 走到 `_redbase_on_branch` 的 `repo_kind()=="partial"`,整批 `verdict[sha]=None`,紀錄照留,於是漏到新分支。
- **為什麼可以不整批放棄**
  - 本機已有的 commit 做 `merge-base --is-ancestor` 不會連遠端;只有「提交不存在」才會觸發自動抓取。
  - 可以只對「`cat-file -e` 證實本機有這個提交」的做祖先判斷。
  - 或讓 `_lens_git` 的 `env` 帶 `GIT_NO_LAZY_FETCH=1`(git 2.44 起有,舊版 git 沒有這個環境變數,仍要保留這道判斷)。
- **兩版查證**(自建 partial 設定的 repo,本機有 featA 的提交 c1,HEAD 在 main 上開的 featB,帳裡一筆沒 ref 的判綠 head_sha=c1)
  - 修前 409ab14 載入後呼叫 `_redbase_branch_rows(root,"甲",None,"ignored")`:`rows kept: 0`。
  - 修後 6e10ae5b 同呼叫:印出「1 筆紀錄判不了…照舊算進來」,`rows kept: 1`。
- **文件落差**:計劃〈天花板三〉只列淺複製,部分複製只在做法 1d 提到,天花板清單沒列。
- **歸因**:有證據的修復回歸。修前能濾對,修後放棄。這是 r1 資源席要求「整批不問」的取捨,代價是這類專案漏洞重現。
- **影響範圍**:只在判不了時照舊算進來並印一句,沒有資料損壞。

2. 偵測 HEAD 的路徑(`name` 為空)沒有任何測試守住。計劃〈天花板二〉把「分離 HEAD 時只剩祖先判斷」寫成行為,但它不在驗收條款或測試裡。
引句:「        if isinstance(ref, str) and ref and name and ref != name:」
severity: minor
blocking: 否
- **失敗場景**:有人重構時拿掉 `and name`。分離 HEAD 且紀錄帶 ref 時,`ref != ""` 恆真,該分支寫過的所有判綠都被丟。之後同一支測試判紅,就會把實作後的版本存成紅燈版,「判綠過不存」的保護默默失效。
- **重現**(把該行改成不含 `and name`,在修前與修後兩版各跑一次)
  - 修後 6e10ae5b:`t_spec_gate_redbase_green_other_branch` 10 條、`t_redbase_branch_rows_fallback_keeps` 12 條、`t_spec_gate_redbase_skips_after_green` 6 條、`t_spec_gate_redbase_written_on_red` 35 條,全綠。
  - 修前 409ab14(搭配當時的測試檔):前兩支測試分別 10 條、7 條,全綠。
- **歸因**:有證據的原有漏查。該行與測試缺口在兩版都一樣,修補沒有造成也沒有補上。
- **修法建議**:補一個分離 HEAD 的案例,條款裡寫進分離 HEAD 或沒分支名時只看祖先。

**三問**

1. 原問題的修復效果有何行為證據?
   - 把 d32dbe14 的新測試 `t_redbase_branch_rows_fallback_keeps` 套在 409ab14 的程式碼上:12 條裡 4 條紅。
     - 紅的是「超過上限先問最新的」那條,以及部分複製的三條(連遠端抓取的標記檔被建立)。
     - 同一支測試在 6e10ae5b 是 12 條全綠。
   - 淺複製「rc 1 照留」這條在 409ab14 就綠,不是這次才修好的(409ab14 本來就依淺複製決定留或丟)。
   - 撞名測試:把 `_TitleIndex._join` 的快取整個拿掉(不存、每次重算)。
     - 結果 `t_name_collision_scales` 的「②每種串接只算一次」紅,記下 513 個不同物件。
     - 我擔心只記 `id()` 會因記憶體位址重複使用而漏報,實測沒有:同一支測試會紅。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?
   - 唯一的呼叫端 `_redbase_attach` 已改傳 `ignored=st`;舊的只傳一個參數的呼叫(`t_spec_gate_redbase_written_on_red`)仍綠。
   - 我逐道改壞,測試各自紅:
     - 「提交不存在」改成判不了 → S6 紅。
     - 「rc 1」改成判不了 → S6 紅。
     - 三引號樣式拿掉 → S4 紅。
   - 以下子集全綠:redbase 186、name_collision 22、tq_guard_cli_contract 99、tq_guard_string 31。
3. 新發現的同一案例在修前、修後各是什麼結果?
   - 發現 1:修前丟掉(0 筆),修後留(1 筆),是修復造成的覆蓋範圍縮小。
   - 發現 2:兩版行為與測試覆蓋相同,是原有缺口。

**圖譜鏡頭(固定席)**
- 這份 diff 不碰 `lumos-cli-read`(search 預設排除 superseded)與 `lumos-cli-lifecycle`(re-inject)的 INVARIANT。
- 「測試假綠形態」要求還原翻紅釘配前置斷言:本輪的 `t_name_collision_scales`、`t_redbase_branch_rows_fallback_keeps` 有 ★前置★。
  - `t_spec_gate_redbase_green_other_branch` 的 S6 兩案(同名重開、提交不存在)沒有獨立的前置斷言。
  - 但我把 S6 兩道判斷改壞後該測試確實紅,所以現場成立。
  - 這只是形式缺口,不報 finding。
- `design-loop`、`guard-kill` 的 INVARIANT 不受影響。
- 其餘固定席節點(`pitfalls-code-loop`、`loop-convergence-recording` 等)沒有可對的合約文字,未逐條判。
- 我另外對七篇改動筆記跑 `lumos lint`,各 0 問題。

**已驗與未驗範圍**
- 已驗:`_redbase_on_branch` 各分支(淺複製、部分複製、截止時間、上限、cat-file)、`_redbase_branch_name`、`_TG_CONST_PAT` 三處 fullmatch(S4 之外的 `assertThat`、`assertTrue` 路徑也實測認三引號)、`t_name_collision_scales` 的守衛力度。
- 未驗:Windows 路徑;`git branch -m` 與壓提交後的實際流程(只讀計劃的天花板敘述);同族的 `--short` 用法(e2e 事件在 `scripts/lumos` 約 42109、43650 行)不在本 diff 範圍;真實慢遠端與時鐘倒退。

最嚴重等級是 minor,blocking 共 0 條。
