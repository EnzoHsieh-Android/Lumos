severity: major

## ①提示注入

### S1 放行清單印出時,AI 寫的理由、規則、檔名沒清過,可遮掉「AI 放的」標記或偽造整行
severity: minor
blocking: 否 — 要 AI 刻意構造輸入才會發生,而且「其中 N 條是 AI 放的」那行計數仍照印。
引句:「print(f"  {k}  {it.get('file', '')} [{it.get('rule', '')}] — {it.get('reason', '')}{_ai}")」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:37865`(對照已清過的提示在 `scripts/lumos:37873` 的 `_lint_waive_origin`)
- 攻擊路徑:
  - 誰:照常操作的 AI。
  - 從哪:`lumos lint-waive <指紋> --note "<含換行或 ESC 序列的字串>"`,`--rule`、`--file` 同理。
  - 送什麼:理由裡放 `\x1b[8m`(隱藏文字)或 `\n  <指紋>  Other.kt [tq/x] — …`。
  - 拿到什麼:人拿來決定要不要 `--ack --all` 的 `lumos lint-waive --list` 輸出被改寫。
    - `(AI 放的,還沒人看過)` 標記被隱藏。
    - 或多出一行偽造的放行。
- 修補只把問人那段提示換成 `_out_clean`。同一批欄位在 `--list` 和放行成功那行(`——{note}`)仍原樣印出。
- 重現,兩版輸出相同:
  - `python3.14 lumos_after lint-waive aaaa1111bbbb2222 --rule tq/skip-added --file FooTest.kt --note $'真的是大型測試資料不是作弊\033[8m' --repo r5 </dev/null`
  - 接著 `lint-waive --list --repo r5 </dev/null | cat -v`:輸出 `^[[8m(AI …還沒人看過)`。
  - 理由改成 `$'…\n  cccc3333dddd4444  Other.kt [tq/x] — 假的一筆'` 時,`--list` 多出一行偽造的放行,AI 標記跟在那一行後面。
- 歸因:有證據的原有漏查。`lumos_before` 與 `lumos_after` 的 `--list` 行為相同(`ea1e0b8` 的 `_lint_waive_show` 已有 `_ai` 標記且原樣印出),修補沒讓它變好也沒變壞。
  - 前版取得:`git -C /Users/enzo/harness/lumos-tq-android show ea1e0b8a6ce2b05a6715ad59f628c36c6ae7d18b:scripts/lumos > lumos_before`

## ②讀寫與執行越界
已看,無。
- 新增與修改的程式只讀 git(`diff --raw -z --no-ext-diff --no-textconv`、`cat-file`、`grep`),參數都是完整提交編號。
- 沒有執行被審 repo 內檔案的新路徑,也沒有新的下載來源。
- 公開檔掃描:
  - 新增行裡沒有信箱、金鑰字樣、`/Users/` 路徑。
  - 套件名只有 `com.example.pos` 這個代稱。
  - 考場去識別化目錄(`governance/eval/results/`)沒有私有類別名、測試名,只有 `SameTest`、`Q` 這類合成名。
- 擋下訊息裡的檔名與原因確認走 `_out_clean`(換行、ESC、U+2028/2029、雙向字元都清掉),放行指令用 `shlex.quote`。
  - 檔名或測試名偽造不出獨立的「接下來」行或指令行,只能在同一行中段塞字。
  - 這屬於外來文字回顯,依威脅模型放行。

## ③非刻意、一步就能繞過的守衛

### S2 `LUMOS_SKIP_LINT_NEW` 設成任何非空值(含 `0`、`false`)都整道關閘,終端沒有任何提示
severity: major
blocking: 是 — 殘留或誤設的環境變數無聲關掉含作弊比對在內的整道閘,同族的鄰居都只認 `1`。
引句:「skip_env = bool(os.environ.get("LUMOS_SKIP_LINT_NEW"))」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:38950`
- 攻擊路徑:
  - 誰:使用者本人,或照常操作的 AI。
  - 從哪:shell 設定檔、`.envrc` 或 CI 環境殘留 `LUMOS_SKIP_LINT_NEW=0`(本意是「不跳過」),或 AI 照字面理解設成 `=false`。
  - 送什麼:一次帶作弊提交的 `git push`。
  - 拿到什麼:`_lint_new_verdict` 回 `status: off`、`blocked: False`。
    - 終端不印任何訊息:`_cl_say_lint_ok` 對 off 不輸出,`warnings` 為空。
    - 只在有候選時寫一筆治理帳。
- 鄰居慣例對照:同檔 `LUMOS_SKIP_NOTE_SHAPE`、`LUMOS_SKIP_ROOM_GUARD`、`LUMOS_SKIP_NOTE_AUDIT`、`LUMOS_SKIP_BOUND_TESTS`、`LUMOS_SKIP_DRIFT_CHECK` 都是 `== "1"`。`scripts/lumos:50720` 的註解明寫「設成 0 表示不略過」。
- 重現(`r7` 是含一條斷言變弱作弊的小 repo):
  - `LUMOS_SKIP_LINT_NEW=0 python3.14 -I call_verdict.py lumos_after r7 main..feat`
  - 輸出:`status: off | blocked: False | events: [('skipped-env','關閘時作弊比對有 1 條候選沒判')]`。
  - `=false`、`=1` 結果相同。
  - 未設變數時輸出 `status: blocked | blocked: True`。
- 歸因:有證據的原有漏查。`ea1e0b8` 與 `22cc667` 的判斷式相同,主線版本也是 `if os.environ.get("LUMOS_SKIP_LINT_NEW"):`。這次新增的 `_lint_new_off` 沿用它,所以作弊比對也被它關掉。
  - 查證:`grep -n 'LUMOS_SKIP_LINT_NEW' lumos_before lumos_after`,兩版同一行(38950)。

### S3 單行超過 2 萬字的檔整支不解析,同檔作弊只剩一條通用的 `tq/too-large`
severity: minor
blocking: 否 — 守衛仍會擋(要放行一條),且既有的 `tq/unparsable`(檔裡含 NUL)本來就有同樣的整檔遮蔽效果。
引句:「elif _tg_has_long_line(b) or _tg_has_long_line(h):」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49148`
- 攻擊路徑:
  - 誰:照常操作的 AI。
  - 從哪:在測試檔加一行超過 2 萬字的字串或註解。
  - 送什麼:同一個提交裡同檔還有跳過、斷言變弱之類的改動。
  - 拿到什麼:原本逐條列出的候選被壓成一條 `tq/too-large`。
    - 訊息只寫「人工看這支檔的改動」,不說內容。
    - 放行紀錄不留是哪幾種作弊。
    - 放一條就放掉整檔。
- 不需要刻意:base 端本來就有大型內嵌資料(內嵌 JSON、base64 之類)的測試檔,之後每次改動都只剩通用候選,逐條偵測永久失效。
- 重現:
  - `r1`:測試檔含 `@Ignore`、斷言變弱兩處,再加一行 20001 字的註解。
    - `lumos_before test-guard` → `['tq/skip-added','tq/assert-weakened','tq/assert-weakened']`
    - `lumos_after test-guard` → `['tq/too-large']`
  - `r7`:base 端含 25000 字的內嵌字串,之後把 `assertEquals` 改成 `assertTrue(true)`。
    - before → `tq/assert-weakened`
    - after → 只有 `tq/too-large`
  - 對照:在註解放一個 NUL,兩版都只回 `['tq/unparsable']`,所以「整檔通用候選」不是新能力,是這次擴大了非刻意的觸發面。
- 建議:長行不是不解析整檔,而是先截斷或剔除超長行再比,並在逐條候選之外另列 too-large 提醒。
- 歸因:有證據的修復回歸(`ea1e0b8` 會逐條列出,`22cc667` 變成一條)。
  - 查證:`python3.14 lumos_before test-guard --repo r7 --diff main..feat` 對照 `lumos_after`。

### S4 遠端沒有 main/master 追蹤 ref 時,退回本機 main,本機尚未推出的作弊提交被算成已在主線
severity: minor
blocking: 否 — 要求遠端追蹤 ref 缺席,那次推的是分支而不是 main;CI 與之後推 main 時仍會比對,也比修補前窄。
引句:「or _lens_default_base(root, tip=head, include_local=True, deadline=deadline)」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49123`
- 攻擊路徑:
  - 誰:使用者本人,或照常操作的 AI。
  - 從哪:設了 remote 但從沒 fetch(或 `origin/main` 追蹤 ref 被刪、single-branch clone)的 repo。作弊提交先落在本機 `main`,再從它切 `feat`。
  - 送什麼:`git push -u origin feat`。起點是空樹,`_tg_start` 退到本機 main。
  - 拿到什麼:本機 main 上的作弊提交被排除在比對範圍外,回報 0 條候選。
- 其他情境已看:
  - 遠端 main 存在但過期:範圍變大,更嚴。
  - 遠端 main 存在、本機 main 領先:修補後正確抓到(見下)。
- 重現(`r4`,用 `git update-ref` 模擬遠端追蹤 ref):
  - `origin/main` = base、本機 main 多一個斷言變弱提交:
    - before:0 條。
    - after:1 條 `tq/assert-weakened`(修補有效)。
  - 刪掉 `refs/remotes/origin/main` 後:兩版都是 0 條,範圍從本機 main 起算。
- 歸因:有證據的原有漏查。這個退回路徑兩版相同;修補只修好「遠端 main 存在」的情況。
  - 查證:`python3.14 lumos_before test-guard --repo r4 --diff 4b825dc642cb6eb9a060e54bf8d69288fbee4904..feat`,對照 `lumos_after`。

### S5 assume 的條件換行寫時,條件被改成永遠跳過不會被列
severity: minor
blocking: 否 — 要改條件本身(刻意);換行寫法被判成「同一條已存在」,屬近似判讀的天花板,且不在「抓不到」清單裡。
引句:「hits.setdefault(("tq/skip-added", who, "跳過:" + _tg_norm(line)), []).append((path, i))」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:48841`
- 攻擊路徑:
  - 誰:照常操作的 AI(格式化工具常把長條件拆成多行)。
  - 從哪:把 `assumeTrue(\n  BuildConfig.DEBUG\n)` 的條件那一行改成 `false`。
  - 送什麼:該行只剩 `assumeTrue(`,與改動前的身分(整行)相同。
  - 拿到什麼:既有的 assume 被改成永遠跳過,0 條候選。身分只帶 `assumeTrue(` 這一行,條件不在裡面。
- 重現(`r2`):
  - 多行版把 `BuildConfig.DEBUG` 換成 `false`:兩版都 0 條。
  - 單行 `assumeTrue(false)`:before 0 條,after 1 條 `tq/skip-added`。
  - 也就是修補只補了單行寫法。
- 歸因:有證據的原有漏查(多行寫法兩版都漏)。

### S6 修飾詞改動被排除在註記比較之外,JUnit 5 的 `@Test` 加 `private` 或 `static` 照樣 0 條候選
severity: minor
blocking: 否 — 要刻意加修飾詞;兩版都不報,不是修補造成的。
引句:「pre = _TG_MODIFIERS.sub("", pre)」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:48504`
- 攻擊路徑:
  - 誰:照常操作的 AI。
  - 從哪:對 Jupiter 的 `@Test void a()` 改成 `private void a()` 或 `static void a()`。
  - 送什麼:簽名、本體、註記不變,只有可見度或靜態修飾詞改變。
  - 拿到什麼:該測試不再被當成測試執行(Jupiter 的探測規則;我沒有實際跑 Gradle,屬推論),守衛 0 條候選。
- 修補把 `public/private/static/abstract…` 全數從註記比較中剔除,明文宣告這類改動「不算註記有變」。這讓這條靜默路徑被正式寫死;公開的「抓不到」清單也沒列它。
- 重現(`r3`):`private`、`static` 兩版都是 `作弊候選 0 條`。
- 歸因:有證據的原有漏查。before 沒剔除修飾詞也一樣 0 條,因為註記變了不會觸發任何規則。

### S7 `failOnPassedAfterRetry = true` 寫在區塊註解裡,就能讓「開啟重試」不被列
severity: minor
blocking: 否 — 要刻意放一行假的設定;修補把 `//` 行註解排除了,但 `/* … */` 與其他檔的設定仍算數。
引句:「return any(pat.search(ln.split("//", 1)[0]) for ln in r.stdout.splitlines())」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49114`
- 攻擊路徑:
  - 誰:照常操作的 AI。
  - 從哪:建置檔新增 `maxRetries.set(3)`,同檔加一行 `/* failOnPassedAfterRetry = true */`。
  - 送什麼:`_tg_retry_ok` 在終點版掃到「有建置檔設了 true」。
  - 拿到什麼:重試放寬不被列。
- 重現(`r6`):
  - 只加 `maxRetries.set(3)`:1 條 `tq/build-config`。
  - 再加那行區塊註解:0 條。
- 歸因:有證據的原有漏查。before 的 `git grep -E` 連 `//` 註解都算數,修補只收窄了一半。

---
已查三類、共 7 條。最重的 1 條(關閘環境變數 `=0`)可直接重現無聲關閘,其餘 6 條都是縱深防禦。實驗檔留在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/資安-sonnet/`,等編排者收貨後刪除。
