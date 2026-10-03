severity: major

# r2 正確性席審查(Sonnet)——回頭條件消失式與生來成立_計劃

審材:/tmp/回頭條件消失式與生來成立-r2.md;對照 repo:scratchpad/rw(唯讀,實驗都在 /tmp/revisitB-r2/exp)。
立場:預設照字面實作會在某個輸入下做錯事。第 1 輪已修的(`-S` 找錯提交、資料夾判消失、反斜線整串轉、列舉訊息漏改三處中的兩處)我核過修法本身成立,不重報;下面只報新稿裡還在的洞。

## 各節判讀

### 範圍、依據、PRIOR-ART、RETIRE-IF、REVISIT
已讀,無 finding。(`t_drift_when_probes_evaluate_and_trigger` 的 ⑨ 確實是「新寫一條終點已經成立的條件式:擋」,依據句屬實。)

### 做法 1(`when-gone` 條件鍵)
見 C2、C6、C7、C8。

### 做法 2(寫下時就已成立)
見 C1、C3、C4、C5、C9。

### 實務隱患、驗收條款、回退、天花板、審計修正紀錄
實務隱患逐類答覆見文末;驗收條款、回退、天花板、審計紀錄已讀,除上列 finding 牽涉的條款外無 finding。

---

**C1 往回查用 `git log -- 路徑` 的預設歷史簡化,遇到自動合併出來的合併提交會把兩條分支的版本交錯排在一起,「這一世」的開頭會停錯**
severity: major
blocking: 是 — 合併提交是日常輸入,照字面實作會對真實存在的筆記印出錯的提交與錯的成立判定
引句:「從被掃的那一版往回,一版一版看這篇筆記,找連續都還有這一條的最早那一版」
1. 位置:做法 2 第 1 點(什麼叫寫下時)加第 2 點(怎麼查,提交清單用 `git log --format=%H <起點> -- <筆記路徑>`)。spec 把清單當成一條線性的版本鏈,逐版往回走、遇到第一個沒有這一條的版本就停。
2. 問題:`git log -- 路徑` 在合併提交「跟每個上一版都不一樣」(兩邊都改過同一篇筆記、自動合併後兩邊都不像)時會保留該合併並同時追兩條分支,輸出是依時間交錯的兩條歷史,不是一條線。這時鏈上相鄰的兩個版本可能分屬不同分支,「連續都還有」的判斷被另一條分支的舊版打斷。spec 沒有講合併提交怎麼走(沒有 `--first-parent`,也沒有說明交錯時怎麼辦)。
3. 具體例子(我在 /tmp/revisitB-r2/exp/m 實跑):c0 建 n.md;分支 feat 的 f1 在 n.md 末尾寫入一行 LINE(當時條件不成立);主線的 m1 在 n.md 開頭加一行 TOP(m1 沒有 LINE);merge 兩邊自動合併,n.md 有 LINE 也有 TOP,跟兩個上一版都不一樣。`git log --format=%h -- n.md` 實際輸出順序是 merge、m1、f1、c0;各版有沒有 LINE 是 1、0、1、0。照字面實作:從 merge 往回,下一版 m1 沒有 LINE,「連續」到此中斷,這一世的開頭被判為 merge;在 merge 的樹上判條件(假設那時條件已因別的提交成立)就標「寫下時就已成立(提交 merge)」。真正的寫下時是 f1,那時條件不成立,正確結果是不標。
4. 查證:實驗輸出如上;`first-parent` 版本只剩 merge、m1、c0,也會把 merge 當開頭,所以光加 `--first-parent` 也沒定義清楚,spec 得明寫「合併提交的版本怎麼對」(例如逐上一版各自追、或明說標到合併為止並進天花板)。file: `scripts/lumos:26179`(`_nodehome_git` 只轉發參數,沒有任何歷史簡化的設定)。

---

**C2 「讀位元組、編成 UTF-8 在位元組裡找」跟既有 `_read` 的實際行為不符:`_read` 存的是遺失性解碼後的文字,非 UTF-8 的檔含非 ASCII 字串會被誤判成「字串已消失」**
severity: major
blocking: 是 — 正是 spec 自己想擋的「誤讀成亂碼也會找不到、讓條件提早成立」,而且判成立會直接擋推送
引句:「否則把字串編成 UTF-8 在位元組裡找,找不到 → 成立」
1. 位置:做法 1 第 2 點(評估,帶字串)。spec 說用既有的 `_read` 讀位元組,內容含 NUL 或 LFS 指標才判不了,其餘「在位元組裡找」。
2. 問題:`_DriftProbeTree._read` 不回位元組,它把每支檔存成 `_drift_decode(b)` 的結果,也就是 `b.decode("utf-8-sig", errors="replace")`;不合法的位元組被換成 U+FFFD。spec 的判不了清單(NUL、LFS、讀不出)抓不到「沒有 NUL 的非 UTF-8 文字檔」(Big5、GBK、Shift_JIS、Latin-1、不含 NUL 的 UTF-16 如純 CJK)。
3. 具體例子:舊專案的 `legacy/報表.py` 是 Big5 編碼,裡面有一行 `# 暫時關閉台北分行`;筆記寫 `REVISIT:[when-gone:legacy/報表.py::台北分行][by:2027-03-31] 分行整併完拿掉這段說明`。檔存在、是一般檔、沒有 NUL、不是 LFS。`_read` 解碼後這段字變成 `\ufffd\ufffd…`,在文字裡找不到 `台北分行` → `one()` 回「找不到 → 成立」。推送時這條新寫的就被點名「條件已經成立」,scan 也列成「條件已經成立,該處理了」,但事實上那段字還在。另一邊,若 spec 真的改成讀位元組找,就得另寫一條不經 `_text` 快取的讀法,但 spec 只說「既有的 `_read`」。
4. 查證:file: `scripts/lumos:32180`(`_drift_decode`:`errors="replace"`);file: `scripts/lumos:32262`、`scripts/lumos:32281`(`_read` 兩個分支都把解碼後的文字放進 `_text`)。

---

**C3 「同一條」只比條件標記,同一篇筆記裡兩行條件標記相同時,後寫的那行會被算到先寫的那行的歷史上**
severity: minor
blocking: 否 — 只會漏標或標錯提交,不影響擋不擋;但正好打在這個功能要抓的「生來就成立」上
引句:「待辦文字、期限改了都還是同一條」
1. 位置:做法 2 第 1 點。spec 把「同一條」定義成同一篇筆記內條件標記一模一樣,沒有講同一版裡有兩行同標記時哪一行是哪一條。
2. 問題:`_probe_lines` 抽出的 `pr["conds"]` 只含(鍵, 值),不含期限與待辦文字;兩行 `[when-file:src/x.py]` 開頭的回頭條件(待辦不同)在歷史上互相不可分辨。
3. 具體例子:c1 寫了行 A `REVISIT:[when-gone:src/x.py::foo][by:2026-06-01] 清 A`(那時 foo 還在,條件不成立);c9 在 foo 已被刪掉之後又寫行 B `REVISIT:[when-gone:src/x.py::foo][by:2026-09-01] 清 B`(生來成立)。掃 HEAD 時對 B 往回查,「連續都還有這個標記」一路到 c1(因為 A 一直在),起點 c1 判不成立 → B 不標。B 正是 spec 想抓的生來成立,卻被漏掉;反過來若 A 寫在 B 之後,A 會被標成 B 的提交。
4. 查證:file: `scripts/lumos:32569`(`_drift_probe_old` 同樣用 `tuple(conds)` 的集合比對,既有行為,推送判定也有同樣的「同一條」模糊,但推送只看起點有沒有,不輸出提交)。

---

**C4 逐版批次讀回的 None 同時代表「那個提交沒有這篇」「超過大小上限」「讀不出」,spec 沒分,也沒列進判不了的原因**
severity: minor
blocking: 否 — 只影響這一個診斷標記的正確性
引句:「每一版的筆記內容用一次批次讀(`_nodehome_cat_blobs_capped`)」
1. 位置:做法 2 第 2 點與第 3 點(判不了的原因清單:還沒提交、淺層 clone、找不到、git 失敗、超過預算、那一版的樹讀不出)。
2. 問題:`_nodehome_cat_blobs_capped` 對「該版沒有這個路徑」「超過 `max_bytes`」「物件不是一般檔」都回 None(同一個值);另外筆記解不開 UTF-8 也沒有出路。spec 的走法是遇到「沒有這一條」就停,所以一個超大的舊版或非 UTF-8 的舊版會被當成「這條在這裡還沒出現」,這一世的開頭停在較新的版本,而 spec 的 `max_bytes` 也沒給。
3. 具體例子:某篇累積很久的大型節點在 c5 曾被貼進一大段資料變成 3MB(超過上限),c6 又瘦身;這條回頭條件在 c2 就有。從 HEAD 往回走到 c5,讀回 None → 視為沒有這一條 → 停在 c6,對 c6 的樹評估(此時條件可能已成立),標出錯的「寫下時就已成立(提交 c6)」。
4. 查證:file: `scripts/lumos:26527`(`_nodehome_cat_blobs_capped`,過大者 `res[i]` 保持 None)、file: `scripts/lumos:26560`(`_nodehome_cat_blobs`:missing/ambiguous 與非 blob 都回 None)。

---

**C5 往回查要用的 git 包裝跟 spec 的描述不符:`_nodehome_git` 沒有 `-c`、沒有逾時參數、也不帶 `--literal-pathspecs`**
severity: minor
blocking: 否 — 同族問題 repo 內別處已有現成寫法(`--literal-pathspecs`),實作時照抄即可,但照 spec 字面做不到也會踩坑
引句:「走 `_nodehome_git`,`-c` 關掉外部差異與文字轉換的既有旗標,`--` 隔開路徑」
1. 位置:做法 2 第 2 點,以及第 5 點「每個 git 呼叫的逾時取『剩餘預算』與既有 20 秒的較小值」。
2. 問題:(a) `_nodehome_git(repo_root, *args)` 只是 `_lens_git(..., binary=True)` 的薄包裝,沒有任何 `-c` 旗標(`git log --format=%H` 本來也不產生差異,這句形同虛設);(b) 它沒有 timeout 參數,固定 20 秒,spec 要求的「取剩餘預算的較小值」要改簽名才做得到,但 spec 沒列;(c) 沒有 `--literal-pathspecs`:筆記檔名含 `[`、`*`、`?` 時 pathspec 會被當萬用字元。
3. 具體例子(實跑 /tmp/revisitB-r2/exp/p):倉庫有 `a[1].md` 與 `a1.md` 兩篇;`git log --format=%s -- 'a[1].md'` 回 d、c(d 是 `a1.md` 的提交),加 `--literal-pathspecs` 才只回 c。筆記 `a[1].md` 的版本鏈混進另一篇的提交,往回查的版本錯位。本 repo 目前沒有這種檔名,消費專案不保證。
4. 查證:file: `scripts/lumos:26179`(`_nodehome_git`)、file: `scripts/lumos:14692`、`scripts/lumos:30786`(同檔別處對 pathspec 一律帶 `--literal-pathspecs`)、file: `scripts/lumos:5549`(`_git_is_shallow` 有 timeout 參數,跟 `_nodehome_git` 不同)。

---

**C6 spec 宣稱的「全部呼叫 `_drift_cond_split`」不是現況,而且列舉鍵、拆值的平行路徑還有幾處沒列**
severity: minor
blocking: 否 — 都是實作會自己撞到的紅測試(S3、S1),不會靜默做錯;但「由同一份算法」的設計宣稱與程式不符
引句:「判定、預讀、點名讀不出的檔、候選篩選、正規化、值驗證全部呼叫它」
1. 位置:做法 1 第 1 點。spec 把 `_drift_cond_split(v, k)` 說成現有六個用途共用的單一算法。
2. 問題:現況只有四個呼叫點(預讀、`unread_for`、`one`、`_drift_probe_cond_candidate`)。正規化(`_probe_norm_value` 對 symbol/test 自己 `rsplit("::", 1)`)、值驗證(`_probe_named_err` 自己 `rsplit`)、路徑警告(`_drift_probe_path_warn` 自己 `rsplit`)都不呼叫它。於是「`gone` 切第一個」不是改一支函式就好;如果實作者照慣例把 `gone` 加進這幾處的 `k in ("symbol","test")`,`Foo::bar` 會被切成路徑 `src/a.py::Foo`、名稱 `bar`(S3 的紅測試會抓到,但 spec 該明講要改哪幾處)。另外這些讀條件鍵的地方也沒列:`_probe_parse` 對 file/symbol/test 先把整個值的反斜線轉斜線(`val.replace("\\","/")`,要讓 `gone` 只轉路徑段得改這裡,spec 只講原則沒講位置);`_DriftProbeTree.prefetch` 只預讀 `k in ("symbol","test")` 的檔,spec 實務隱患說 `when-gone` 帶字串「同帶路徑的 symbol,有預讀」不加就沒有;`_drift_row_unread` 對判不了的行只點名 symbol/test 讀不出的檔,`gone` 判不了時的說明會缺檔名。
3. 具體例子:`[when-gone:src/data.bin::x]`(路徑是二進位檔)→ `one()` 回 None → scan 與推送都說「判不了(git 讀不出程式檔或筆記)」,而不是 spec 做法 1 第 2 點承諾的「when-gone 帶字串時路徑要是一般檔」那句問題;原因是 `one()` 只回 True/False/None,「問題」文字是 `_drift_probe_row_problems` 產的,spec 沒有要它辨 gone。
4. 查證:file: `scripts/lumos:31935`、`scripts/lumos:31943`(`rsplit`)、file: `scripts/lumos:31982`、file: `scripts/lumos:32292`、file: `scripts/lumos:32548`、file: `scripts/lumos:32613`、file: `scripts/lumos:32195`(`_drift_cond_split` 只有 `v` 一個參數)。

---

**C7 〈做法〉1.4 說 `_slot_retire_err` 對 `gone`「照 symbol/test 的規矩要求帶路徑」,跟 S4 的 `[retire:when-gone:src/a.py]` 互相矛盾**
severity: minor
blocking: 否 — 內部不一致,測試會抓
引句:「`_slot_retire_err` 對 `gone` 照 symbol/test 的規矩要求帶路徑(本來就必帶)」
1. 位置:做法 1 第 4 點與驗收條款 S4。
2. 問題:symbol/test 的現行規矩是值裡一定要有 `::`(`"::" not in val` 就報「要帶路徑(路徑::名稱)」)。`gone` 的路徑本來就是第一段、`::字串` 才是選配。照字面把 `gone` 加進 `k in ("symbol","test") and "::" not in val`,S4 的例子 `[retire:when-gone:src/a.py]` 會被擋成「要帶路徑」。括號「本來就必帶」又暗示不用改,兩句互相矛盾。
3. 具體例子:實作者照第一句改 → `lumos lint` 對 `RULE: … [retire:when-gone:src/a.py]` 報錯;照括號句不改 → 符合 S4。
4. 查證:file: `scripts/lumos:3888`。

---

**C8 要同步的「列舉條件鍵」文字不止 spec 列的三處加技能手冊:注入進每個消費專案 CLAUDE.md 的範本與 reference.md 也列了四個鍵**
severity: minor
blocking: 否 — 文件漂移,不影響判定
引句:「技能手冊 `skills/lumos-project-notes/commands/03-寫回圖譜.md` 四種鍵那句補第五種」
1. 位置:做法 1 第 4 點(由同一張表產生、加漂移守衛),以及做法 3 說明與同步。
2. 問題:spec 的守衛只釘 `_probe_value_err`、`_slot_retire_err`、筆記形狀擋「條件怎麼選」三處訊息,加一份技能手冊。實際還有:`scripts/templates/graph-discipline.md` 第 50 行(「`[retire:]` 只收機器式:when-file、when-symbol、when-test、when-status、度量、人裁」,這份會被 reinject 注入每個消費專案的 CLAUDE.md,AGENTS.md 與本 repo CLAUDE.md 也是注入結果);`skills/lumos-project-notes/reference.md` 第 404 行(事件鍵清單)。這兩處不改,消費專案的作者讀到的規矩仍是四個鍵,`[retire:when-gone:…]` 變成沒人知道的寫法。
3. 具體例子:消費專案升級後,CLAUDE.md 注入段仍寫 retire 只收四種;作者照它寫 `人裁`,從不用 `when-gone`。守衛測試因為只比對三處訊息而全綠。
4. 查證:file: `scripts/templates/graph-discipline.md:50`、file: `skills/lumos-project-notes/reference.md:404`、file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:50`。

---

**C9 往回查的成本宣稱只算了帶路徑的條件;不帶路徑的 symbol/test 在每個不同的寫下時提交都要讀整個程式語料,而且「樹與圖譜只建一次」沒說建完何時釋放**
severity: minor
blocking: 否 — 受預算限制,最壞結果是標「判不了」,但效能與記憶體宣稱不實
引句:「成立的條件通常是個位數,吃 scan 既有預算,超過就標判不了」
1. 位置:〈實務隱患〉效能段與做法 2 第 5 點。
2. 問題:`_DriftProbeTree.one` 對不帶路徑的 symbol/test 呼叫 `corpus()`,會批次讀該提交樹上全部程式檔(或測試檔)進 `_text` 快取。每個不同的寫下時提交都建一棵這樣的樹;spec 說「同一個提交的樹與圖譜只建一次」,但沒說用完是否釋放,若為了「只建一次」而保留,記憶體隨不同提交數線性長(每棵一整份程式語料)。同時 `_drift_list` 的內建快取上限是 8 筆就整個清掉,超過 8 個不同提交會重列。「成立的條件通常是個位數」也是未量的宣稱:一個久沒清的消費專案第一次跑 scan,成立的條件可以很多(這個功能就是為此而生)。
3. 具體例子:消費專案有 40 條成立的 `when-symbol:foo`(不帶路徑),寫下時分佈在 25 個不同提交;每個提交讀全部程式檔(假設 8000 支、80MB)→ 25 次批次讀,預算 60 秒多半先耗盡,後面全標「判不了寫下時成不成立(超過預算)」;若快取保留則同時駐留 25 份語料。
4. 查證:file: `scripts/lumos:32334`(`corpus`)、file: `scripts/lumos:32150`(`_drift_list` 上限 8 筆即整個清掉)。

---

## 實務隱患鏡頭:逐類答覆

- 併發:無。往回查與評估只讀 git 物件;唯一例外是工作目錄模式讀磁碟,別的會談同時改檔最多讓一次 scan 看到前後不一致,scan 不是閘也不寫帳。
- 效能:有(C9);另外 `git log -- 路徑` 在歷史很長的倉庫上單次比 spec 量到的 0.05 秒慢,但每次呼叫有 20 秒上限、整體吃預算,最壞是標判不了。推送判定多一種鍵,候選篩選只是比對集合,成本不增(該路徑 `_drift_probe_cond_candidate` 的 `path in touched` 是 O(1);資料夾前綴比對要掃 touched,小)。
- 回滾:無新風險。`when-gone` 回退後變成「不認得的條件鍵」,`_probe_parse` 會設 `bad` 旗標,推送判定與 scan 都略過不評估(file: `scripts/lumos:32461`);已寫入的行只會在 doctor Z 段被數成寫錯的,不擋。
- 誤擋:有(C2:非 UTF-8 檔誤判消失,推送時新寫的條件被當成「已經成立」擋下);另外工作目錄模式的 sparse-checkout 沒拉下來的檔算消失,spec 已列天花板 5,屬已承認。繞過:spec 已寫明可用表態照留,留在表態檔,屬明寫動作,無 finding。
- 重放/歷史正確性:有(C1、C3、C4、C5)。

---
最嚴重 severity:major;blocking 共 2 條(C1、C2)。
