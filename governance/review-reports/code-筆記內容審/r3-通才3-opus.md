severity: major

席名:通才3-opus(第 3 輪,審 r3-delta.patch)

我做了什麼:逐 hunk 讀完差異。在自己 cp -R 的複本(scratchpad/r3o/mc/base)裡把九處修正各改回去一次,跑 `-k note_audit_code_review_r2`。另外寫了三支探針:decision-amend 的改名、CI 工作項目切分函式、doctor 端到端。探針都在 scratchpad/r3o/。repo 本身沒有動。

翻紅結果:八處改回去後回歸會紅(三道「終點找不到」、150 處提醒、第二層 doctor、括號形狀、跟工作目錄比、沒加進 git 的條件)。只有一處改回去照樣綠:第一層 doctor 改回看整份設定。細節見 F4。

## F1 用 Obsidian 改名後跑 git add -u 或 git commit -a,decision-amend 認不出改名,會改掉已經推上去的決策
severity: major
blocking: 是 — 違反 S12「應跟著改名找遠端追蹤參照上的舊路徑……有就拒絕」;已推的決策被改掉,工具還印「還沒推上去」
引句:「if (tracked is None or tracked.returncode != 0) and gone is not None and gone.stdout.strip():」
佐證:
- file: `scripts/lumos:24902`
- file: `scripts/lumos:24917`
- file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:126`

失敗場景:
- 這次修正把「還沒加進 git 就拒絕」收窄了:只有在「索引裡有檔、磁碟上不見」(`ls-files --deleted`)時才拒絕。
- 改名偵測則用 `git diff -M <遠端參照> -- <圖譜夾>` 跟工作目錄比。這個比法只看得到索引裡有的檔,沒加進 git 的新檔不在比對裡。
- 所以只要舊路徑已經從索引拿掉、新檔還沒加進 git,兩道都放行。常見的走法有三種:在 Obsidian 或 Finder 改名後
  - 跑 `git add -u`(只暫存修改與刪除,不收新檔),或
  - 跑 `git commit -a`(一樣不收新檔),或
  - `git rm` 舊檔。
- 接下來會發生:
  1. `gone` 是空的,不拒絕;
  2. diff 裡只有舊檔的 D,沒有改名配對,於是 `old = rels`(新路徑);
  3. 讀 `ref:新路徑` 讀不到,就當成遠端沒有這條決策;
  4. 已推的 d1 被改掉。
- 這正是 r2 通才席那條要防的疏忽(用檔案總管或 Obsidian 改名),只是後面接的 git 動作換成最常見的 `add -u` 或 `commit -a`。

最小重現:
指令:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r3o/amend_probe.py`

探針做的事:用測試裡的 `_na_repo` 建專案,推到裸遠端,改名 D.md→New.md,接著各跑一次 `git add -u` 與 `git commit -a`,再對 New 跑 decision-amend。

輸出:
```
add-u status: D  docs/kg-knowledge/Systems/D.md | ?? docs/kg-knowledge/Systems/New.md
add-u rc= 0 ✓ decision-amend Systems/New.md d1.context 改好了(這條決策還沒推上去)
add-u file now: ['    context: 偷改已推的決策']
commit-a status: ?? docs/kg-knowledge/Systems/New.md
commit-a rc= 0 ✓ decision-amend Systems/New.md d1.context 改好了(這條決策還沒推上去)
commit-a file now: ['    context: 偷改已推的決策']
```

修法方向:判「沒加進 git」時,別看「索引裡有、磁碟上沒有」,改看「遠端參照上有、工作目錄沒有」。也就是 `git diff --diff-filter=D --name-only <ref> -- <圖譜夾>` 有東西、而且這篇還沒加進 git,就拒絕。另一個做法是用暫時的索引檔(GIT_INDEX_FILE 複本)對這篇 `add -N`,再跑 -M,讓沒加進 git 的新檔也參加改名配對。回歸 ② 應該加上 `add -u` 與 `commit -a` 這兩種走法。

## F2 CI 工作項目切分函式碰到帶行尾註解的 YAML 就被騙過,r2 那條洞重新出現;jobs: 行帶註解時整份不查,比修正前更安靜
severity: major
blocking: 是 — 淺層 clone 時兩層檢查都跳過,設計上唯一的補償就是 doctor 這句提醒;它沉默,CI 後盾就每次都悄悄沒跑
引句:「m = re.match(r"^(\s+)([\w.-]+):\s*$", ln)」
佐證:
- file: `scripts/lumos:24978`
- file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:186`

失敗場景(都是合法的 GitHub Actions YAML):
- A(r2 那條洞原樣重現):工作項目名後面帶行尾註解,例如 `  full:   # needs full history`。
  1. 這行不符合 `:\s*$`,不算新的工作項目,整段被併進前一個工作項目 `audit` 的內容。
  2. `full` 的 `fetch-depth: 0` 因此被算在 `audit` 頭上。
  3. `audit` 呼叫了 note-shape、自己卻是淺層 clone,函式回 `[]`,doctor 不唸。
- B(比修正前更差):`jobs:  # all jobs`。
  1. 整行不符合另一句 `if re.match(r"^jobs:\s*$", ln):`,`in_jobs` 一直是 False,整份回 `[]`。
  2. 修正前是看整份有沒有 `fetch-depth: 0`,這份完全沒有,會唸;修正後不唸了。
- C:工作項目名加了引號(`"audit":`,合法 YAML)。
  1. 沒有任何工作項目名被認出來;第一個 `    steps:` 被當成名叫 steps 的工作項目。
  2. 後面每個工作項目的 `steps:` 都用同一個 key 蓋掉前面的,只剩最後一個工作項目被檢查。

最小重現 1:切分函式
指令:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r3o/ci_probe.py`

探針用 SourceFileLoader 載入 scripts/lumos,對每種 YAML 直接呼叫 `_ci_jobs_calling_without_full_history`。輸出:
```
A_job_trailing_comment []
B_jobs_trailing_comment []
C_quoted_names []
D_plain_ok_control [('D_plain_ok_control.yml', 'audit')]
```
D 是對照組:跟 A 一樣、只是沒有註解,就唸得出來。

最小重現 2:doctor 端到端
指令:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r3o/doc_probe.py`

輸出:
```
B_jobs_comment_no_depth -> []
   old-rule would nag fetch-depth: True
```

修法方向:比對之前先拿掉行尾的 ` #…` 註解(不在引號裡的那種);工作項目名也要收有引號的 key。或者改成只認 `jobs:` 下面第一層縮排的 key,用「縮排等於第一個子行」來定這一層,不要求那行一定要以冒號結尾。回歸補 A、B、C 三種形狀。

## F3 note-shape 那步被註解掉時,doctor 現在一句都不唸(修正前會唸 fetch-depth)
severity: minor
blocking: 否 — 只是 doctor 的提醒不見了,不影響任何閘的判定
引句:「elif _ci_jobs_calling_without_full_history(ymls, "note-shape --diff"):」
佐證:file: `scripts/lumos:24022`

失敗場景:
- 第一層 doctor 前面那句「沒呼叫」是拿「沒濾掉註解」的整份文字比對的;這次換上的共用函式卻會濾掉整行註解。
- 如果 CI 裡的 note-shape 那步整行被註解掉(`# - run: python3 scripts/lumos note-shape --diff …`):
  1. 「沒呼叫」那句看到註解裡的字,以為有呼叫,不唸;
  2. elif 那句濾掉註解後,找不到任何呼叫的工作項目,也不唸。
- 修正前 elif 看的是整份文字,至少會唸「沒抓完整歷史」。r1 已經把第二層的「沒呼叫」改成跳過註解(計劃第 203 行「doctor 檢查 CI 跳過註解」),第一層這句沒有一起改。這次改 elif 時換成濾註解的判法,兩句之間就出現了空檔。

重現(`doc_probe.py` 的 G 案例):
```
G_commented_out_step -> []
   old-rule would nag fetch-depth: True
```

## F4 新回歸沒守到第一層 doctor 的接線;③ 的「audit」斷言等於沒驗;PITFALL 行綁這支測試的說法過頭
severity: minor
blocking: 否 — 測試涵蓋不足,不是現在就會做錯事
引句:「m._ci_jobs_calling_without_full_history([wf / "ci.yml"], "note-shape --diff") == [("ci.yml", "audit")], "")」
佐證:
- file: `scripts/test_lumos.py:48776`
- file: `scripts/test_lumos.py:48871`
- file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:33`

失敗場景:
- 翻紅實驗:把 `_note_shape_doctor_lines` 的 elif 改回 `elif "fetch-depth: 0" not in body:`,跑 `-k note_audit_code_review_r2`,結果「21 passed, 0 failed」。
  - ③b 只直接呼叫共用函式,沒走到第一層 doctor 真正用它的那一行。
  - 另外兩支呼叫 `_note_shape_doctor_lines` 的測試(上面兩個行號),用的 workflow 都只有 `name: x`,也走不到這個分支。
- 筆記內容閘那行 PITFALL 寫「doctor 看 CI……要看呼叫那一步的同一個工作項目」,並綁了 `[test:t_note_audit_code_review_r2_regressions]`。實際上這支測試守不住第一層那一半。
- ③ 的斷言是 `"fetch-depth: 0" in l and "audit" in l`。訊息本身就含「note-audit check」,所以就算把後面列工作項目名的 `+ "、".join(...)` 拿掉,這條照樣綠——它沒驗到「講出是哪個工作項目」。

修法方向:
- 補一條走 `_note_shape_doctor_lines(..., ci=True)` 的斷言:full 與 audit 兩個工作項目,只有 full 抓完整歷史,要唸。
- ③ 改成斷言訊息裡有 `ci.yml 的 audit`。

## F5 改用共用的全 0 常數後,不再認得 64 個 0,SHA-256 專案刪分支會從跳過變成 rc2
severity: minor
blocking: 否 — GitHub 不支援 SHA-256;推送前掛鉤只把 rc1 當擋;第二層也還沒接線
引句:「if re.fullmatch(r"0{40}|0{64}", b):」
佐證:
- file: `scripts/lumos:29142`(`_ZERO_SHA_RE = re.compile(r"0{40}")`)
- file: `scripts/lumos:29112`(`_LENS_SHA_RE` 同時收 40 位與 64 位,可見工具有意支援 SHA-256)

失敗場景:
- 在 `git init --object-format=sha256` 的專案裡,範圍終點是 64 個 0(刪分支)。
- 修正前:note-audit 印「範圍終點是全 0(刪除分支)」,rc0。
- 修正後:note-audit、note-shape、home check 三道都印「擋下:……終點在本機找不到——範圍寫錯了?」,rc2。
- 推送前掛鉤判刪分支用的 `_ZERO` 也只有 40 個 0(file: `scripts/hooks/pre-push:33`),所以 SHA-256 專案的刪分支推送會把 64 個 0 當終點傳進來。
- 計劃第 194 行說「全 0 判法改用共用常數」,實際上把第二層原本有的 64 位支援弄丟了。

實測(本輪版本對照修正前的 `a72a0e2e~1`):
```
note-audit rc=2   (新)
OLD note-audit rc=0  筆記內容審:範圍終點是全 0(刪除分支),沒有要審的東西
```

修法方向:把共用常數改成 `0{40}|0{64}`。

## 看過、沒有發現問題的部分

- decision-amend 的欄位形狀判定:空值、同層縮排清單、`[` `{` 開頭、`|` `>` 多行、一般文字加續行,判法都跟 `parse_decisions` 的讀法相容。改壞後回歸都會紅。
- 150 處截斷:截斷只發生在單篇超過一批的那條路上;record 比對的是「每一處的上下文指紋」這整份排序過的清單(file: `scripts/lumos:24760`),150 對 160 不相等,輕的判定確實收不下,跟說明一致。
- rc2 對推送前掛鉤的影響:掛鉤只把 rc1 當擋,推送前的終點一定是本機提交。CI 用的是 `github.sha`,也一定找得到。所以正常使用不會因為 rc2 誤紅。

總結:最嚴重 major;blocking 共 2 條(F1、F2)
