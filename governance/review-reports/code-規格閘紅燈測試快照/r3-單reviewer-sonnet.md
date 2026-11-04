severity: major

我把修補後的 `0fcc214af` 和修補前的 `c627b3874` 各載成模組,用臨時 git repo 逐案對跑。獨立案例腳本放在 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet/t1.py` 到 `t8.py`,用法是 `python3.14 tN.py before|after`。我沒讀 r1、r2 的席報告與 `r2-behavior-cases.md`,案例都是自己造的。

跑 `python3.14 scripts/test_lumos.py -k redbase` 的結果是 119 passed、0 failed。

### F1 孤兒檔與被刪的紅燈版排在鏈尾,不照時間先後,真正的改弱被誤報或漏報
severity: major
blocking: 是 — 孤兒檔、被刪檔和留痕併存時,步驟說明是錯的,真正的「預期值被改」候選消失,放行說明裡的那條候選後,改弱就沒人報了
引句:「metas.append((tok, n, None, f"{head}:{n}"))」
file:line:`scripts/lumos:49738-49746`(`_tg_rb_metas` 把孤兒檔、被刪檔接在有留痕的紅燈版之後);`scripts/lumos:49915` 附近 `_tg_rb_chain` 依 `snaps` 的 append 順序兩兩比。

失敗場景:規格閘依序判紅兩次。第一次是 `TODO()` 骨架(SPEC-b…01),第二次是 `assertEquals(900, …)`(SPEC-b…02)。合併時第一次的留痕行被弄丟,檔還在,於是成了孤兒檔。推送版把 900 改成 800。
- `metas` 先放有留痕的 SPEC-02,再放孤兒 SPEC-01,所以鏈變成 `[02(900), 01(骨架)]`。
- 實際比的是 02→01,這是一步反向比較,造出「斷言 1→0」的假候選。
- 01→推送版(骨架→800)沒有命中。
- 真正的 900→800 沒有被獨立列出。

沒有留痕的孤兒彼此之間,順序是 `ch`(`git diff --raw`)的路徑字典序。token 是 `SPEC-`+`token_hex(4)`(`scripts/lumos:14184`),字典序和時間無關,所以結果取決於亂數:
- 骨架那份字典序在前時,鏈是 `[00000001(骨架), ffffffff(900)]`,正確列出「預期值被改」。
- 骨架那份字典序在後時,鏈反過來,只列出錯誤的「斷言變少」,真正的 900→800 漏報。

被刪的檔按 `git log` 由新到舊排,也不照創建時間。

覆蓋缺口:新補的孤兒檔與被刪檔測試都只有單檔,沒有「留痕檔與孤兒、被刪檔併存」或「兩個孤兒」的案例。

重現(`t2.py` 的 B1 與 `t6.py`):
- `python3.14 t2.py before`:列 unreadable(孤兒檔),加上「SPEC-b0000002 → 推送版:同一支測試的預期值被改了」。
- `python3.14 t2.py after`:列 unreadable,另一條 weakened 寫的是「SPEC-b0000002 → 第 2 份紅燈版:斷言變少…(斷言 1→0)」,「預期值被改」那條消失。
- `python3.14 t6.py after`:兩種 token 順序,一個報對,一個只報錯的那條。

證據表:
- claim:有孤兒檔時,歷次紅燈版應照時間先後比,真正的改弱要列出。
- input:骨架(SPEC-b…01,孤兒)加 900(SPEC-b…02,有留痕),推送版是 800。
- expected:有一條「SPEC-02 → 推送版,預期值被改」。
- case_source:自造(`t2.py` B1),`t6.py` 是兩個孤兒的字典序對照。
- before:`rules=[unreadable, weakened(SPEC-02→推送版 預期值被改)]`。
- after:`[unreadable, weakened(SPEC-02→第2份 斷言變少)]`,沒有 02→推送版。
- comparison:同輸入,修前報對、修後報錯,且漏掉真實改弱。
- 歸因:有證據的修復回歸(B1 混合案例,修前正確、修後錯)。兩個孤兒的字典序隨機是修補新引入的順序缺口,修前根本不比孤兒。

### F2 刪檔偵測被改名配對繞過,測試只釘純刪除
severity: minor
blocking: 否 — 要在同一個提交刪舊檔、同時新增相近的紅燈版才繞得過,正常流程走不到,放行後也不損資料
引句:「"log", "--format=%x00%H", "--name-only", "--diff-filter=D", f"{base}..{head}"」
file:line:`scripts/lumos:49687`(`_tg_rb_deleted`)

失敗場景:同一個提交刪掉 SPEC-1,又新增內容相近的 SPEC-2(紅燈版 JSON 內嵌整份測試檔,相似度很容易超過 50%)。`git log` 預設做改名偵測,把它顯示成 `R100 SPEC-1 → SPEC-2`,`--diff-filter=D` 不列。SPEC-1 的刪除偵測不到,它的內容不進比對,也沒有「被刪」候選。

覆蓋缺口:我把 `_tg_rb_deleted` 的「還活著」過濾整段拿掉(`alive` 那兩行改成 `return out`),`-k redbase_unreadable` 仍然 27 passed,所以「刪了又加回」沒有測試守。測試只有「純刪除」一種。

另外,`_lens_git` 逾時(預設 20 秒)或回傳非 0 時,`_tg_rb_deleted` 靜默回 `[]`,這跟其他讀取失敗會列候選或回錯誤的作法不一致。我沒造出逾時,這一條只是讀碼所得。

重現(`t5.py`):
- `python3.14 t5.py after`:`deleted: []`。
- `git log --name-status` 輸出 `R100 SPEC-d0000001.json → SPEC-d0000002.json`。
- `python3.14 t5.py before` 沒有 `_tg_rb_deleted`,函式不存在。

證據表:
- claim:這條分支刪過的紅燈版都應列出。
- input:同一提交 `git rm` 舊檔、新增相近的新檔。
- expected:列「被刪」候選。
- case_source:自造(`t5.py`)。
- before:函式不存在,孤兒檔也不比,等於沒偵測。
- after:`[]`,沒偵測到。
- comparison:修補只覆蓋純刪除。
- 歸因:有證據的原有漏查(修補沒覆蓋到)。修法方向是加 `--no-renames`。

### F3 「被刪」候選的指紋含提交編號,rebase 或 amend 後放行失效
severity: minor
blocking: 否 — 只是要重新放行一次
引句:「這支紅燈版檔在這條分支的提交 {sha[:12]} 被刪了」
file:line:`scripts/lumos:49745`;`_tg_cand` 的指紋用 `rule, file, ident, nth`(`scripts/lumos:49333`),而 `ident` 是 `{tok}\x00{file}\x00{reason}`,reason 含 `sha[:12]`。

失敗場景:對「被刪」候選用 `lint-waive` 放行。之後 `git pull --rebase` 或 `git commit --amend`,刪檔提交的編號變了,指紋就變了,放行失效,又被擋一次。

重現(`t3.py`):`python3.14 t3.py after` 輸出 `True ['1e581167f1fd2cfe'] ['0e86b4ca1b5d3061']`。amend 只改了提交說明,內容完全沒變,指紋卻不同。

證據表:
- claim:同一件事放行一次就該穩定。
- input:同內容,只改提交編號。
- expected:指紋相同。
- case_source:自造(`t3.py`)。
- before:沒有這條候選。
- after:兩個不同指紋。
- comparison:指紋隨提交編號變。
- 歸因:有證據的修復回歸(新引入的候選)。

### F4 刪掉主線已有的舊紅燈版會被當成這條分支的竄改,而且留痕還在時同一個檔列兩條
severity: minor
blocking: 否 — 候選可放行,但訊息誤導
引句:「alive = _nodehome_cat_sizes(root, [f"{head}:{p}" for _c, p in out]) or [None] * len(out)」
file:line:`scripts/lumos:49685-49703`(`_tg_rb_deleted` 沒限制「這條分支自己加的檔」);`scripts/lumos:49743-49746`(被刪檔無條件進 `metas`)。

失敗場景 A:主線已經有舊計劃的紅燈版,這條分支 `git rm` 它(計劃「回退」節本身就建議各專案 `git rm -r governance/redbase/`)。比對工具對每個被刪的檔列一條 `tq/redbase-unreadable`「請從上一版還原」,並載入內容,最多可到 200 MB 總量上限。修前沒有這些候選。

失敗場景 B:紅燈版檔被刪、留痕行還在。留痕那一條寫「推送版沒有這支紅燈版檔:被刪了」,被刪偵測又寫一條「在提交 xxx 被刪了」,同一個檔兩條 unreadable,要放行兩次(`t7.py`)。

重現:
- `python3.14 t1.py after`:主線檔被分支刪掉,多出一條 unreadable。
- `python3.14 t1.py before`:零候選。
- `python3.14 t7.py after`:同一個檔 2 條 unreadable,外加 1 條 weakened。

證據表:
- claim:只該針對這條分支自己的紅燈版刪除發出警告。
- input:主線已有的紅燈版,在分支被 `git rm`。
- expected:不列(或至少只列一條)。
- case_source:自造(`t1.py`、`t7.py`)。
- before:`[]`。
- after:`[unreadable]`;`t7` 為 2 條 unreadable 加 1 條 weakened。
- comparison:修補新增了誤擋面和重複候選。
- 歸因:有證據的修復回歸(新功能)。計劃沒明寫「主線的舊檔不算」,讀碼只能說兩種讀法都說得通,這也是我把它列 minor 的原因。

### F5 同一條候選自相矛盾:標題說「沒辦法比」,內文說「已照內容比」
severity: minor
blocking: 否 — 措辭矛盾,內文把處理講清楚了
引句:「不要刪這支檔,已照它的內容比」
file:line:`scripts/lumos:49329`(`_TG_WHY["tq/redbase-unreadable"]` 開頭固定是「規格閘紅燈版讀不到、沒提交或被改過,沒辦法比」),`scripts/lumos:49742`(孤兒檔)與 `49745`(被刪檔)的 extra 又寫「已照它的內容比」。

訊息實際長這樣:「規格閘紅燈版讀不到、沒提交或被改過,沒辦法比(…已照它的內容比)」。這兩種情況的 `verify` 文字(`scripts/lumos:49329`)也沒有講「找回留痕」。

重現:`python3.14 t2.py after` 或 `t7.py after`,看 unreadable 那行。

歸因:有證據的修復回歸(新增分支的文字和共用標題衝突);修前孤兒檔確實沒比,標題當時是對的。

## 三問

1. **原問題修復效果的行為證據**
   - 新檔改名後改 expected:修前 `['tq/redbase-unmatched']`,修後 `['tq/redbase-weakened']`(`t8.py`)。
   - 孤兒檔:修前只列 unreadable、訊息叫人刪檔,也不比;修後列「找回、不要刪」並照內容比,單檔時能報出改弱(`t2.py` B1、`t6.py`)。
   - 被刪的檔:純刪除時修後能列出,並用刪掉前的內容比出改弱(`t7.py`)。
   - 其餘修補(推的不是頂端不看工作目錄、補讀額度扣除、跨平台判綠、`_lens_fork_point`、check-ignore 走 `_lens_git`)我只用測試套件 119 passed 為證,沒另造案例,也沒對每項做 mutation。

2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 正常路徑、補讀路徑和寫入端抽出的共用函式仍成立。
   - 錯誤路徑問題在 F1、F2、F4:順序、改名配對、主線舊檔。
   - 相鄰路徑問題是 `_tg_rb_deleted` 的靜默失敗(逾時、非 0 回 `[]`),見 F2 補充,只是讀碼,沒造出。

3. **新發現的同一案例在修前、修後各是什麼**

   | 案例 | 修前 | 修後 |
   |---|---|---|
   | F1(`t2.py` B1) | 孤兒 unreadable + 正確的 weakened(預期值被改) | 孤兒 unreadable + 錯的 weakened(斷言變少),真實的消失 |
   | F4 場景 A(`t1.py`) | 零候選 | 多一條 unreadable |
   | F2(`t5.py`) | 函式不存在 | `deleted: []`,刪除未偵測 |
   | F3(`t3.py`) | 沒有這條候選 | 指紋隨提交編號變 |

## 圖譜鏡頭

沒有牽連節點被破壞,逐組判斷如下。
- `lumos-cli-read` 的 search 排除 superseded 這條合約、`guard-kill` 的 rc 優先序與 `--json` 純度、`lumos-cli-lifecycle` 的 re-inject 位元組保留、`design-loop` 的處置閘:這次改的是 `_tg_*`、`_redbase_*`、`_lens_fork_point` 一帶,沒有改到這些函式的路徑,未見破壞。
- `測試假綠形態` 的「還原翻紅釘要配前置斷言」:新測試的「推的不是頂端」「補讀三趟」都有 `★前置★`;孤兒、被刪那兩個案例用訊息斷言當現場證明。
- 但我做的 mutation 顯示 `_tg_rb_deleted` 的「還活著」過濾拿掉後測試仍綠,等於這一段缺前置與翻紅釘(F2)。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`、`test-guard`:`test-guard.md` 的新 WHY(孤兒檔照內容比、訊息不叫人刪檔)和程式一致,只是沒寫鏈序的限制(F1)。
- `check-t-sentinel` 等只列名的節點:改動沒有牽連到它們。

## S1–S11 核對

- **S1**:寫入端的修補只有 `_lens_fork_point` 與 `_lens_git`,引句「`fork = _lens_fork_point(rr, head)`」,測試通過,成立。
- **S2**:鏈比對本體沒動,引句「`for c in _tg_fn_cands(tp, k, cur, prev, ck)`」(`_tg_rb_chain`),成立。
- **S3**:有留痕的紅燈版仍照治理帳行序。孤兒檔與被刪檔沒有可靠順序,見 F1,不完整。
- **S4**:孤兒檔現在照內容比,見引句「`metas.append((tok, n, None, f"{head}:{n}"))`」;被刪檔會列但有 F2、F3、F4 的缺口。「讀不到的列 unreadable」仍成立:補讀把 UNREADABLE 當空檔後,指向目錄的紅燈版會列 unmatched(`t8.py`),git 讀取失敗會回錯誤,沒有漏報。
- **S5**:引句「`b, h = ("" if b == "UNREADABLE" else b), ("" if h == "UNREADABLE" else h)`」。改名後改 expected 現在列 weakened(`t8.py`),檔案兩端都沒有時仍列 unmatched。成立。
- **S6**:跨平台判綠過的反向測試用 `_redbase_cap_reason` 直接驗,斷言會對錯誤翻紅,成立。
- **S7**:沒動治理帳與紅燈版時行為不變,`absent_unchanged` 通過。多出一個 `git log` 子程序,不影響候選。成立。
- **S8、S9**:未動,測試通過。
- **S10**:引句「`if head != _lens_full_sha(root, "HEAD"): return set()`」(`_tg_rb_pending`)。被刪檔偵測只讀 git 歷史,沒有拿工作目錄內容來比,仍照終點判。成立。
- **S11**:簿記豁免未動,測試通過。

驗了什麼:修補的 repair 與 preserve 案例都有跑過,成功與失敗路徑已分開報告。沒驗:Java 路徑、`git log` 逾時、大量被刪檔的記憶體峰值(只讀碼,沒量測)。

最嚴重等級為 major,blocking 共 1 條(F1)。
