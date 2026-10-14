severity: major

## 1. 標記行邊界(做法 1)

severity: major
blocking: 是 — 標記寫歪時靜默退回會談目錄,違反本計劃自己的「不退回」原則
引句:「也不退回會談目錄算(退回會用錯的樹,比沒附更糟)」
問題:正規式只認字面 `LUMOS-REPO:` 且整行以此開頭。下列寫法都不匹配,被當成沒寫:
- 全形冒號 `LUMOS-REPO：`
- 清單前綴 `- LUMOS-REPO:`
- 引用前綴 `> LUMOS-REPO:`
- 反引號包住整行
- 冒號後沒有路徑
做法 5 的「沒寫就照舊用會談目錄」會接手,於是正好走進做法 4 禁止的路徑。
失敗情境:
- 編排者把範本貼成 markdown 清單,寫成 `- LUMOS-REPO: /w/B`,`LUMOS-IMPACT: main..HEAD` 另起一行。
- 掛鉤在會談目錄 A 解讀 `main..HEAD`,算出 A 的牽連節點並附上。
- 席位以為那就是 B 的範圍。
- 現行 `LUMOS-IMPACT:` 寫歪是什麼都不附;新標記寫歪卻會附上錯的樹,後果更差。
- 計劃沒規定「行裡出現 `LUMOS-REPO` 字樣但不合文法」怎麼處理(是否要加第七個代碼,或歸 `repo_not_absolute`)。
- 實測正規式:`LUMOS-REPO：/a` 和 `LUMOS-REPO: `(空)都回 None。
程式佐證:``scripts/hooks/claude/dispatch-lens-hook.py:26-27`` 的既有標記都是 `^…:\s*(\S+)\s*$`,對 `line.strip()` 做 `match`,沒有任何「像標記但不合文法」的告警。

## 2. 路徑字面值:引號、`~`、Windows、尾端斜線、NUL、Unicode 正規化

severity: minor
blocking: 否 — 多數是失敗在安全側(多拒),但判定表沒寫齊
引句:「是絕對路徑(`repo_not_absolute`);`realpath` 之後存在、是資料夾(`repo_missing`)。」
問題:
- 實測結果:
  - `"/a b/c"`:引號被當成路徑一部分,得 `repo_not_absolute`,可接受。
  - `~/x`:同上。
  - `C:\x\y`:同上。
  - 尾端斜線和行尾空白、`\r`:都被正規式與 `realpath` 吃掉,沒問題。
- 計劃沒寫「引號要不要剝」「`~` 要不要展開」。目前只是靠固定句子自己講清楚,但固定句子沒要求寫出期望格式。
- 路徑含 NUL 時,`os.path.realpath` 在 Python 3.14 丟 `ValueError`(實測)。計劃沒規定要 try/except。
- `guard()` 預設 `swallow=False`,例外會往上丟。新碼多了讀檔、`realpath`、`stat`,任一處丟 `OSError`、`ValueError`、`UnicodeDecodeError`,整支掛鉤崩潰、什麼都不附,也沒有 `LUMOS-LENS:` 說明。
- macOS 上 NFD 寫法的路徑(中文或帶重音的資料夾名,LLM 常輸出與磁碟不同的正規化形式):
  - `realpath` 保留輸入形式。
  - `git rev-parse --show-toplevel` 回磁碟形式。
  - 兩者不相等,誤判 `repo_not_root`。
  - 實測 NFD 輸入 `rp==git` 為 False,NFC 為 True。
  - 計劃的「結果要等於 `realpath`」比字串,沒說用什麼比。
具體失敗:使用者的工作樹資料夾名含中文,編排者吐出另一種正規化形式,得到一句「不是 repo 根」,但其實就是根。
程式佐證:``scripts/hooks/claude/_hookevent.py:127-149`` 的 `guard` 在 `swallow=False` 時重新丟出例外。

## 3. 六個代碼的判定順序與互斥:有缺口

severity: major
blocking: 是 — 實作者必須猜
引句:「前四條都過了,才跑 `git -C <路徑> rev-parse --show-toplevel`」
問題:
- 缺口一:最後那次 `git rev-parse` 的失敗模式沒有歸屬。
  - 包括:git 不存在或 OSError、逾時、rc≠0(例如 dubious ownership 或 safe.directory)、輸出空。
  - 六個代碼裡只有「不等於」歸 `repo_not_root`,其餘無定義。
  - 計劃也沒給這次 git 呼叫 timeout。
  - 現有掛鉤的內層預算要求所有子行程都夾在天花板內,卡住的 git(fsmonitor、網路磁碟)會被外層 SIGKILL,連 fail-open 都沒有。
- 缺口二:`gitdir:` 檔讀取的細節沒寫。
  - `gitdir:` 可能是相對路徑(submodule 或 `--relative-paths` 的工作樹),相對於 `.git` 檔所在目錄解,計劃沒說。
  - `commondir` 通常也是相對(`../..`)。
  - `gitdir:` 檔內容壞掉或指向不存在的資料夾,歸哪個代碼沒說。
  - repo 內無任何現成解析碼可借(`grep gitdir:|commondir scripts/lumos` 為空)。
- 缺口三:`repo_not_root` 出現在兩處不同層級(沒有 `.git`;git 回的根不等於),測試必須分別造情境。
  - S2 的「repo 裡的子資料夾」只會在第 2 步就因沒有 `.git` 被擋。
  - 「`.git` 存在但 show-toplevel 不等於 realpath」的分支(例如 `.git` 檔指向別的工作樹、`core.worktree`)沒有任何驗收條款覆蓋。
- 缺口四:`repo_untrusted` 在 `repo_not_lumos` 之前,所以「別人可寫又沒圖譜」只報 untrusted。順序有寫,但互斥條件沒寫。
- 缺口五:`repo_duplicate` 與其他代碼的先後只在做法 1 一句話帶過。重複行裡有一行不合格時報哪個,沒定義。
- 缺口六:兩行路徑完全相同也算重複,這是刻意嗎?範本若已含 `LUMOS-REPO:` 而編排者又加一行,就會被拒。

## 4. 信任檢查範圍與誤殺

severity: major
blocking: 是 — 驗收條款寫的行為,在 CI(Linux)上會讓 S1 先紅不了,威脅模型也有漏洞
引句:「這個資料夾、它的父目錄、它的 git 資料夾(工作樹時連共用的那個)都屬於目前使用者,而且都不是 group/other 可寫(`repo_untrusted`)。」
問題一(誤殺):
- 父目錄「屬於目前使用者」會誤殺 root 擁有、不可寫的父目錄(`/srv`、`/workspace`、`/tmp`)。
- 現有測試夾具用 `tempfile.mkdtemp(prefix="lens-")`,CI 是 `runs-on: ubuntu-latest`,TMPDIR=/tmp(root 擁有、1777),所以每個夾具 repo 都會得 `repo_untrusted`。
- S1 在 Linux CI 上不可能綠,除非夾具先建一層 0700 的自家資料夾。計劃沒寫這個測試前提。
- 單人 macOS 使用者上不會發生,所以只是 CI 與測試設計的問題;但「屬於自己」對父目錄是比「不可被別人寫」更強的條件,計劃沒說明為何。
問題二(漏洞):
- 檢查只看資料夾的 mode,不看資料夾裡的 `config`、`config.worktree`、`hooks/`。
- 資料夾 0755 自己擁有,但 `.git/config` 若是 0666,別人仍可就地改成 `core.fsmonitor=…`,而計劃的目標威脅正是這個。
- 工作樹時 `config.worktree` 也是同樣來源。
- 計劃的〈實務隱患〉只承認「自己擁有但內容不可信」,沒承認「自己擁有的資料夾、別人可寫的設定檔」。
- 問題二在單人威脅模型下風險低,但計劃的 S2、S3 把「group 可寫」當成已覆蓋,檢查範圍與條款字面不符。
程式佐證:``scripts/hooks/claude/dispatch-lens-hook.py:312-329`` 的 `_ok` 只對單一檔案及其父目錄做 mode 與 uid 檢查。計劃也確認它「只收檔案」,新函式要另寫。

## 5. 拒絕路徑會丟掉角色卡與架構段

severity: minor
blocking: 否 — 影響是少附一段,非錯附
引句:「不改去那裡算,也不退回會談目錄算(退回會用錯的樹,比沒附更糟);派工詞附一行 `LUMOS-LENS:` 說明」
問題:
- 現行掛鉤即使圖譜段失敗,也會照附 `role_text` 與 `arch_text`(它們不需要圖譜,見 `_extra_text`)。
- 新的拒絕路徑「不去算」,連 lumos 都不叫,所以有 `LUMOS-ROLE-CARDS: on` 或 `LUMOS-ARCH-TARGET: on` 的席位會被悄悄少掉卡片。
- 說明行只說「沒附固定席節點」,沒說角色卡也沒附。
- 計劃沒決定要不要仍用會談目錄呼叫 lumos 只取角色段。
程式佐證:``dispatch-lens-hook.py:525-531``。

## 6. 與 `LUMOS-IMPACT:`、`LUMOS-SPEC:` 格式不一致的靜默放行

severity: minor
blocking: 否 — 現況就如此,只是新標記放大後果
引句:「跟 `LUMOS-IMPACT:` 或 `LUMOS-SPEC:` 同一份派工詞才有作用」
問題:
- 現行兩個標記寫歪(`\S+` 不匹配,例如範圍含空白)就整段不處理,什麼都不附。
- 新標記的 `(.+?)` 允許空白,但另兩個不允許,三者文法不一致。
- 單獨一行 `LUMOS-REPO:` 沒有 IMPACT 或 SPEC 時被忽略,也沒說明。
- 若沒有其他標記就連重複檢查都不跑。計劃沒寫這是刻意的。
- 若兩個標記並存(IMPACT 和 SPEC),現行是 IMPACT 勝出,SPEC 被忽略。REPO 對誰生效,計劃沒寫。

## 7. 驗收條款能否寫成先紅測試(現有測試怎麼搭)

severity: major
blocking: 是 — S5 沒有綁測試,S3 的搭法與現有測試不相容,必須先決定
引句:「[S5] 當同一份派工詞有兩行 `LUMOS-REPO:` 時,應附 `repo_duplicate` 的說明,不在任何地方算;路徑含空白的 `LUMOS-REPO:` 應照常認得。」
問題:
- S5 沒有 `[test:]`,另外 5 條都有。重複與路徑含空白是新增文法的核心,沒綁測試。
- 現有 `t_dispatch_lens_hook_fail_reason_notice` 用 `patch.object(hm.subprocess, "run", lambda *a, **k: R())`,所有子行程呼叫都回同一個假物件。新掛鉤會多出一次 `git rev-parse` 呼叫,舊式假物件會讓這次呼叫的 stdout 變成 JSON,toplevel 比對必然失敗,測試要改成依 `argv[0]` 與子命令分派的假 `subprocess.run`。
- S3「一支假 git 記錄呼叫」:
  - 掛鉤的 `subprocess.run` 已被 patch 時,不能同時用 PATH 假 git。
  - 兩種做法擇一:patch 並記錄 argv,或用真子行程加 PATH 假 git(像 `t_dispatch_lens_hook_thin_shell` 那樣跑真掛鉤)。
  - 計劃沒決定。若用 patch,「一次 git 都不跑」要驗的是 argv 裡沒有 `git`,而 lumos 的 `dispatch-lens` 呼叫也不能發生。
- S1 要真跑 lumos 才能驗「在另一個 repo 算、附上固定席節點」。`_mk_lens_repo` 已有雛形,但需先解決上面第 4 點的 `/tmp` 父目錄問題。
- 沒有條款覆蓋:`repo_not_root` 的 `git` 呼叫分支(第 3 點缺口三)、NFD/NUL 路徑、拒絕路徑的角色卡行為、設計審的 `LUMOS-SPEC:` 搭配 REPO 被拒。
- S4「行為應與現在相同」已有現成測試 `t_dispatch_lens_hook_fail_reason_notice` 可擴充。
- 「先紅」可行性:S1、S2、S4、S6 都可寫成先紅。S3 取決於上述假 git 搭法。
程式佐證:``scripts/test_lumos.py:42122`` 的 `t_dispatch_lens_hook_fail_reason_notice`、``scripts/test_lumos.py:40158`` 的 `t_dispatch_lens_hook_thin_shell`、``scripts/test_lumos.py:40031`` 的 `_mk_lens_repo`。

## 8. 設計審失敗說明(做法 5 子項)

severity: minor
blocking: 否
引句:「掛鉤的說明行拿掉「只在有範圍時」的條件,另寫一句計劃版的說明。」
問題:
- `_fail_note(r, rng, repo)` 內建 `if rng else None`,範圍與計劃兩條路的 `what` 清理不同(`_SAFE_RANGE_RE` 只適用範圍)。計劃版說明的路徑要用 `_clean_field`,沒寫。
- `_fail_note` 目前不知道 repo 是否來自標記,做法 5 的兩版措辭需要新增參數,簽章會變,現有測試的呼叫路徑要同步。
- 新 lumos 的 `spec_missing`、`spec_outside_repo`、`no_knowledge` 配舊掛鉤時,舊掛鉤的白名單查表不認得,會原樣放行(與現行一致,可接受)。
- 反過來,新掛鉤配舊 lumos 時,設計審失敗還是什麼都不印,說明行不會出現。計劃沒寫這個過渡行為。

## 已讀,無 finding

- 回退節、實務隱患的已排除項:已讀,無 finding。
- 做法 7(Codex 編排不在範圍):已讀,無 finding。
- 做法 8(舊裁定標作廢):已讀,無 finding。
- Windows 路徑:專案是 macOS/Linux,被當成 `repo_not_absolute` 拒絕,無 finding。
- 尾端斜線、行尾空白、`\r`:正規式與 `realpath` 都吃得下。
- 大小寫不敏感檔案系統:實測 `/users/enzo` 與 `/Users/enzo` 比對相等。

最高等級 major,blocking 共 4 條(第 1、3、4、7 條)。
