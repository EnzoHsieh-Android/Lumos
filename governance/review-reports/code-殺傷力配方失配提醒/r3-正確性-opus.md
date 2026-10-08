severity: major

# 代碼審第 3 輪 正確性席(正確性-opus)

審材:`governance/review-reports/code-殺傷力配方失配提醒/r3-delta.patch`(73bc8aff..d219e935)。
實驗在 `--shared` clone(`kcc-r3-work-正確性-opus/repo`,HEAD d219e935)跑,Python 3.14.6、git 2.39.2(Apple)、macOS APFS(暫存資料夾不分大小寫、不分寫法)。
重現腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/kcc-r3-work-正確性-opus/h.py`(沿用 test_lumos 的 `_krc_cell`、`_kr_lum`,每格獨立 repo,同一份配方先給判斷函式、再真跑 `lumos guard kill --json`),`reg.py` 拿第 2 輪版本(73bc8aff)對照。
`t_kill_recipe_check_matches_guard_kill`、`t_kill_recipe_check_fs_and_git` 本機 87/87 全綠。

## F1 old 欄位沒寫、檔是空的:判斷函式判 ok,guard kill 程式出錯(第 2 輪修正引進的退步)
severity: major
blocking: 是
引句:「old = r.get("old", "")」
file: `scripts/lumos:13311`
file: `scripts/lumos:13969`
file: `scripts/lumos:13975`

1. 這輪把「old 沒寫當空字串」寫成跟 guard kill 一樣,但 guard kill 只有數原文那一步用 `r.get("old", "")`;原文恰好一次之後套壞法用的是 `src.replace(r["old"], r["new"], 1)`,old 沒寫在那裡丟 KeyError(13975 行),整支 guard kill 崩潰、整篇的配方都沒結果、kill-log 也沒寫。
2. `"".count("")` 等於 1,所以檔是空的時候,old 沒寫會通過「恰好一次」,接著 new 是字串、還原問得到 → 判 ok。第 2 輪的 `_kill_bad_fields` 原本把 old 沒寫算格式不對,這輪拿掉後沒在「數完原文」之後補回去。
3. 重現(`h.py oldmissing_empty`、`reg.py`):
   ```
   == old 欄位沒寫 + 檔是空的
      judge: ['ok']
      guard kill: rc=1 KeyError: 'old'
   r2 版(73bc8aff): {'status': 'malformed', 'detail': '配方欄位格式不對(old 沒寫或不是字串)', ...}
   r3 版(d219e935): {'status': 'ok', ...}
   doctor:['[P2] 殺傷力配方的原文還對不對得上程式(提醒,不擋)', '  ✓ 殺傷力配方的原文都對得上']
   ```
   對照:old 沒寫、檔不是空的 → judge hits、guard kill drifted(對得上),所以只差在「數完恰好一次之後」那一步。
4. 修法:`n == 1` 之後、判 new 之前加「`"old" not in r` → malformed(guard kill 套壞法時 KeyError)」;對照測試補一格「缺 old 而且檔是空的」。

## F2 配方指到檔案連結:還原只還原連結本身,目標檔留在改壞的狀態;判斷函式兩條都判 ok,guard kill 第二條判 drifted
severity: major
blocking: 是
引句:「if _kill_restorable(ctx, top, file) is False:」
file: `scripts/lumos:13978`
file: `scripts/test_lumos.py:60333`

1. 這輪的 `_kill_restorable` 只問「`git checkout -- <file>` 會不會失敗」。配方 file 是 repo 內的檔案連結(`p.py -> prod.py`)時:guard kill 用 realpath 改的是 `prod.py`,還原卻是 `git checkout -- p.py`,只把連結本身還原,回傳碼 0,`prod.py` 一直是改壞的內容。同組後面的配方讀到的是改壞的檔:原文數不到就假的 drifted,數得到就拿改壞的程式跑 baseline 與突變,結果也不可信。
2. 判斷函式說明把 ok 定義成「原文恰好一次、還原得回去」,這種寫法卻判 ok;計劃 S5 自己也寫了「guard kill 還原檔案連結時目標檔會留在被改壞的狀態」(所以對照測試每格分開 repo),判斷函式卻沒有反映這件事,對照測試那一格還把它釘成 ok。
3. 重現(`h.py symlink2`:同一篇兩條配方,第一條 `file=p.py`(連結到 prod.py)、第二條 `file=prod.py`,原文都是 `LIMIT = 5`):
   ```
   == 連結 p.py→prod.py 先、prod.py 後(同組兩條)
      judge: ['ok', 'ok']
      guard kill: [('survived', ' whole-suite'), ('drifted', 'old 命中 0 次(需恰 1——配方漂移,重寫)')]
   ```
   P2 會說都對得上,guard kill 判出 drifted:正是本功能要預先講的那一類。
4. 這不是本輪新引進的(第 1、2 輪也判 ok),但本輪把還原判斷換成「問 git」,而 git 的回傳碼答不了這題,換了形狀這個洞也還在。修法方向:解析時最後一段經過連結(`rel` 跟 git 正規化後的字面不同、而且中途是 120000 模式)就另給一個狀態(例如「套得上但還原只還原連結、同組後面的配方會讀到改壞的檔,改寫成 `"prod.py"`」);不想新增狀態的話,至少在 P2 印這一類,並把對照測試那格的期望改掉。

## F3 file 的型別檢查排在分平台與 test 白名單前面:說明寫「guard kill 會程式出錯」,實際 guard kill 是乾淨的 error
severity: minor
blocking: 否
引句:「out["detail"] = "配方欄位格式不對(file 不是字串或含 NUL 字元,guard kill 會程式出錯)"」
file: `scripts/lumos:13259`
file: `scripts/lumos:13890`

1. 這輪說明寫「判的順序照 guard kill:分平台 → test 白名單 → 路徑與圍欄 → …」,但 file 的檢查擺在讀平台之前。guard kill 遇到平台不在設定裡、或 test 名不合法,根本走不到用 file 那一步,不會程式出錯。
2. 重現(`h.py order`):
   ```
   == platform zz + file 5
      judge: malformed 配方欄位格式不對(file 不是字串或含 NUL 字元,guard kill 會程式出錯)
      guard kill rc 2 , "detail": "平台 'zz' 不在 config"
   == test a;b + file 含 NUL
      judge: malformed 配方欄位格式不對(file 不是字串或含 NUL 字元,guard kill 會程式出錯)
      guard kill rc 2 ...(test 名不合法那一格,沒有崩潰)
   ```
3. 兩邊都算有問題、P2 都會列,只是原因與「會程式出錯」的說法不對,所以只標 minor。修法:file 的型別與 NUL 檢查挪到 test 白名單之後、`_kill_judge_file` 開頭(platform 不可雜湊那一項維持在最前面,guard kill 分組時就崩潰)。

## F4 別名的比對先組合再轉小寫,不是標準的不分大小寫比對:少數字元會判成 missing,guard kill 卻開得到
severity: minor
blocking: 否
引句:「x = nfc(x) if ni else x」
file: `scripts/lumos:13092`

1. `fold` 是 `casefold(nfc(x))`。Unicode 的標準做法(canonical caseless match)是 `NFD → casefold → 再正規化`;順序不對,遇到「大寫加組合記號」這種字元,兩個在檔案系統上是同一個名字,Python 這邊卻比不出來。
2. 實測:在暫存資料夾逐一建檔、跟大寫、小寫、casefold、NFD、NFKC 各變體比對(U+0020–U+2FFFF),目前寫法有 11 個字元跟 APFS 判得不一樣(全是希臘文帶分音與重音的字,例如 U+0390 `ΐ` 對 `Ϊ́`);改成 `nfc(unicodedata.normalize("NFD", x).casefold())` 後 0 個不一樣(`sweep.py` / `sweep2.py`)。
3. 對照(`h.py greek`,提交裡是 `ΐ.py`、配方寫 `Ϊ́.py`):
   ```
   judge: ['missing']
   guard kill: [('error', 'revert 失敗——後續同組配方作廢防污染')]
   ```
   判斷說「不存在」,guard kill 實際上套了壞法、還原失敗。計劃把這類歸成「Python 的 casefold 跟檔案系統的大小寫表不同的少數字元、不涵蓋」,但量出來的差別不在大小寫表、在比對順序,改一行就沒了;字元罕見,標 minor。

## F5 kill-add 在寫入鎖裡跑的 git 子程序多了兩支,上限秒數加起來超過鎖的 30 秒過期
severity: minor
blocking: 否
引句:「r = subprocess.run(["git", "-C", key, "read-tree", "HEAD"], capture_output=True,」
file: `scripts/lumos:15856`

1. `_KILL_GIT_TIMEOUT = 10` 的註解寫明理由是「kill-add 在筆記庫寫入鎖裡判,鎖 30 秒沒放就會被別人接手」。一條配方原本最多 rev-parse×2 + ls-tree 三支,這輪再加 read-tree、ls-files 兩支,最壞情況是 50 秒(每經過一個工作目錄裡不是連結的連結,還多一支 cat-file)。新測試只驗「每一支都不超過 30 秒」,沒驗加總。
2. 只在 git 每支都慢到接近 10 秒時才會發生(網路檔案系統、大 repo 冷快取),所以標 minor;要收的話可以讓整次判斷共用一個截止時間(剩餘秒數當 timeout),或把判斷挪到拿鎖之前。

## 對過、兩邊判得一樣的(不列 finding)
- 還原判斷:大小寫不同的中間資料夾(`src/x.py` 對 `Src/x.py`)、別名是檔案連結、別名是資料夾連結 → 判斷 unrestorable、guard kill 還原失敗,一致。
- 稀疏檢出:主工作目錄是稀疏、檔在範圍外 → 判斷 missing、guard kill drifted(新工作樹繼承稀疏設定),一致。
- HEAD 是空樹 → missing / drifted,一致。暫存索引在 `core.splitIndex`、`index.sparse`、`feature.manyFiles`、`core.fsmonitor` 下 read-tree 與 ls-files 都正常;回 None 的情況只剩 git 逾時或叫不起來。
- 欄位:platform 是 7(→ noplat / 平台不在 config)、是清單(→ malformed / TypeError)、是 0(→ 走預設);file 沒寫(→ outside / 逃逸);file 含 NUL(→ malformed / ValueError);old 非字串、new 非字串、new 是 null(→ malformed / 程式出錯),都對得上。
- `_kill_fs_fold` 用 `tempfile.mkdtemp()`,guard kill 用 `tempfile.mkdtemp(prefix="lumos-kill-")`,都走 `tempfile.gettempdir()`,同一個 TMPDIR 落在同一個檔案系統;常見特殊字元(ß/ss、ﬁ、ς/σ、K 開爾文、ẞ)的大小寫比對 APFS 跟 casefold 一致。
- 設定檔讀不了:只要有任何配方就回報(⑩b 新格對),跟 guard kill 的「擋下:設定檔讀不了」方向一致。

最高等級:major
