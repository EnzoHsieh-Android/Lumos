severity: major

## 審查範圍與方法

讀了 `r1-snapshot.patch`(LUMOS-IMPACT: da6f3958..HEAD),對照 `scripts/lumos` 現有原始碼確認每個 hunk 的上下文,並在 `/tmp` 下開臨時 HOME/repo 做實地實驗(HOME 環境變數指到臨時目錄,沒有動 repo 本身任何檔案,也沒有在 repo 根跑 commit/reset/restore/checkout/stash)。另外跑了 `python3 scripts/test_lumos.py -k never_create_dirs` 與 `-k vault_lock_falls_back` 確認新測試綠燈,並把 `_mkdir_trusted_under_home` 的本體改回「一次 mkdir 整條路徑再檢查」在一份**複製出去的臨時副本**上驗證翻紅釘(不是原 repo)。

先講清楚哪些檢查點我查過、確認沒問題,不放進「發現」清單:
- 家目錄本身是 symlink:設計上允許(`Path.home().resolve()` 只解析這一段),跟既有 `_trusted_private_dir` 行為一致,沒有新增風險。
- 家目錄不存在:第一段 `cur.mkdir(exist_ok=True)`(不帶 parents)會因為上一層不存在而丟 `FileNotFoundError`,被 `except OSError: return False` 接住,安全失敗,不會半途建出東西。
- 空字串段、`..` 這類異常 `rel_segments`:目前四個呼叫點傳的都是寫死的字面字串常數,不是外部輸入,沒有實際可觸發路徑;`_trusted_private_dir` 的比對本身也不是靠 filesystem 解析 `..`(是字串相等比對),就算真傳了 `..` 也只會比對失敗、安全地回 False,不構成繞過。
- 筆記庫寫入鎖退路(`Path(vault) / f".lumos-vault-{key}.lock"`):鎖檔用 `os.open(..., O_CREAT|O_EXCL)` 獨佔建立,檔名雖可預先算出(vault realpath 的 sha256),但預先佔位需要攻擊者已經對筆記庫目錄有寫入權——那已經是比「本機同帳號」更高的信任層級(能直接改筆記內容了),而且就算佔位,`os.rename` 接手陳舊鎖與 `os.replace` 落檔都是對路徑本身操作、不會跟著 symlink 走到別的檔案,沒有找到可利用的額外傷害。
- 武裝目錄新增的 rc 2 訊息:印出來的只有 `d.parent`/`d.parent.parent`(固定在 `~/.cache/lumos/dispatch-lens/armed` 底下的路徑),不含攻擊者可控內容,不構成資訊洩漏。
- 新增測試 `t_never_create_dirs_under_an_untrusted_path`:確認是在真檔案系統上驗(`tempfile.mkdtemp` + `os.symlink` + `victim.iterdir()`),不是只驗回傳值;把 `_mkdir_trusted_under_home` 本體改回一次性 `mkdir(parents=True)` 再檢查後,原本綠燈的斷言 `after == []` 真的翻紅(`受害者目錄多了:['dispatch-lens']`),翻紅釘有效。

## 發現

### 1. 派工鏡頭武裝目錄:新加的逐層檢查沒有覆蓋到最後、最危險的那一層,實測仍會把別人擁有的目錄 chmod 成 0700

`cmd_dispatch_lens_arm` 裡新插入的 `_mkdir_trusted_under_home(".cache", "lumos", "dispatch-lens", "armed")` 只驗到 `armed` 這一層為止;真正會被寫入、被 `chmod` 的最後一層 `d`(`armed/<repo 指紋>`)還是照舊用「先建、先 chmod,再驗」的舊寫法:

引句:「上層被換成指向別處的連結時,別人的目錄裡就會多出一層空資料夾」

這句註解只講「空資料夾殘留」,但實際往下兩行的程式碼在 `d` 這一層做的不只是留空資料夾——是 `d.mkdir(parents=True, exist_ok=True)` 接著立刻 `os.chmod(d, 0o700)`,然後才跑 `_lens_arm_dir_ok(d)` 驗證。也就是說對 `d` 這個路徑而言,診斷本身承認要修的那個「先建再驗」順序問題,原封不動地留在這個呼叫點最後一段。

實測(在 `/tmp/lens_arm_test` 底下,HOME 指向臨時目錄,victim 是另一個臨時目錄):
1. 先確認**持續存在**的惡意 symlink(不靠搶跑)會被最上面 `if d.exists() or d.is_symlink():` 那段擋下(`_lens_arm_dir_ok` 檢查 `d` 本身,擋下印訊息、rc=2,victim 權限與內容都不變)——這條路徑是安全的。
2. 但如果 `d` 在函式一開始檢查時**還不存在**(所以跳過上面那段),等到 `_mkdir_trusted_under_home` 驗完 `armed` 之後、`d.mkdir(parents=True, exist_ok=True)` 真正執行前,被同帳號的另一個行程搶先把 `d` 建成指向一個已存在目錄(victim,使用者自己擁有)的 symlink,實測结果:
   - `d.mkdir(parents=True, exist_ok=True)` **不丟例外**(pathlib 對 `exist_ok=True` 的判斷是 `self.is_dir()`,symlink 指到真目錄時這個判斷為真,所以視為「已存在的目錄」放行,不建立新東西,也不報錯)。
   - 緊接著 `os.chmod(d, 0o700)` **會跟著 symlink 走**,把 victim 目錄的權限從 `0o755` 直接改成 `0o700`。
   - 最後 `_lens_arm_dir_ok(d)` 才驗到 `d` 是 symlink 回傳 False,程式印「建完之後檢查沒過,不寫」並 rc=2——但 chmod 已經生效,回不去了。

重現腳本(在臨時目錄跑,函式片段直接抄自 `scripts/lumos:24544` 與 `24546` 那兩行):
```python
import os
from pathlib import Path
home = Path("/tmp/lens_arm_test/home2"); victim = Path("/tmp/lens_arm_test/victim2")
home.mkdir(parents=True, exist_ok=True); victim.mkdir(parents=True, exist_ok=True)
os.chmod(victim, 0o755)
d = home / ".cache/lumos/dispatch-lens/armed/somerepo"
d.parent.mkdir(parents=True, exist_ok=True)
os.symlink(str(victim), str(d))          # 模擬「armed 驗完之後、d.mkdir 之前」被同帳號搶跑建走的那一刻
print("before:", oct(victim.stat().st_mode))
d.mkdir(parents=True, exist_ok=True)      # 對照 scripts/lumos:24544,不丟例外
os.chmod(d, 0o700)                        # 對照 scripts/lumos:24546,跟著 symlink 走
print("after:", oct(victim.stat().st_mode))   # 0o40755 -> 0o40700
```

`引句:「d.mkdir(parents=True, exist_ok=True)」` 位於 `scripts/lumos:24544`,緊接著的 `os.chmod(d, 0o700)` 位於 `scripts/lumos:24546`,遲來的驗證 `_lens_arm_dir_ok(d)` 在 `scripts/lumos:24551`。

**攻擊者前提**:必須是跟執行 `lumos dispatch-lens --arm` **同一個 OS 帳號**下能跑程式的另一個行程,而且要能在「`_mkdir_trusted_under_home` 驗完 `armed` 通過」到「`d.mkdir`/`os.chmod` 執行」這極窄的兩三個系統呼叫之間贏得競速(例如用 inotify/fswatch 盯著 `armed` 目錄、偵測到 `d` 還不存在就立刻補上 symlink)。**這個前提本身已經誠實地被本檔其他地方揭露為「同帳號搶跑擋不住」的已知邊界**(`_mkdir_trusted_under_home` 自己的 docstring、`_trusted_private_dir` 的「誠實邊界」段都寫了);而且因為 `os.chmod` 只有目標檔案的擁有者(或 root)才能成功,能被 chmod 動到的目錄也只能是攻擊者自己那個帳號本來就擁有的東西——攻擊者不需要靠這個漏洞也能直接 `chmod` 自己的目錄,所以這條路本身沒有讓攻擊者拿到「原本拿不到」的能力。真正值得在意的是:**這支新函式在文件與其他三個呼叫點(vault-lock/lens-cache/bound-filter)都做到「先驗每一層、驗過才建下一層」,唯獨在 `cmd_dispatch_lens_arm` 這個呼叫點,對最後、也是唯一真的會被 `chmod` 的那一層 `d`,實際上沒有套用同一套逐層保護**——保留的是舊寫法,跟其他三處不一致,而且跟這份 diff 自己宣稱「四個寫入點都改用它」的完整性不符。
severity: major
blocking: 是

### 2. `_vault_lock_where` 改用逐層檢查後,「no-dir」這個失敗原因已經不可能再發生,呼叫端與訊息卻還留著死掉的分支

`_vault_lock_where` 原本用一次性 `mkdir` 時,建資料夾失敗(例如唯讀檔案系統、磁碟滿)會回 `("no-dir", str(e))`,呼叫端 `_vault_lock_say`/`_vault_write_lock` 各自有專門分支處理它(印不同的訊息、且「連資料夾都建不起來」時直接不上鎖照寫)。這次改成呼叫 `_mkdir_trusted_under_home` 之後,所有失敗(不管是真的建不起來,還是路徑不可信)全部被壓成同一種 `("untrusted", str(primary.parent))`:

引句:「if why[0] == "no-dir":」(`scripts/lumos:11173`,`_vault_lock_say` 裡的分支)

因為 `_vault_lock_where` 已經不會再產生 `"no-dir"` 這個值(全 repo 搜尋,唯一組出 `_vault_lock_where` 回傳值的地方就是這次改動的那兩個 `if`,兩個都回 `"untrusted"`),`_vault_lock_say` 的 `"no-dir"` 分支與 `_vault_write_lock` 裡「連資料夾都建不起來就沒有退路、照寫」那段(`scripts/lumos:11218` 附近的 `if why and why[0] == "no-dir":`)都變成永遠走不到的死碼。

行為面沒有變壞——新的統一行為是「查不出來就當成不可信、退回筆記庫自己上鎖」,比舊行為(遇到 no-dir 直接不上鎖)更保守、更安全,這點是好事,不是漏洞。問題純粹是**訊息可能誤導**:如果失敗原因其實是磁碟寫滿或家目錄唯讀(不是被換成連結),使用者看到的訊息卻會說「它自己或上層被換成了指向別處的連結、或別人也寫得進去」,叫使用者去 `ls -ld` 檢查一個其實沒有連結問題的路徑,浪費排查時間;而且死碼留著會讓下一個讀者以為 `_vault_lock_where` 還會回 `"no-dir"`,誤判分支覆蓋率。

`引句:「if why and why[0] == "no-dir":」` 位於 `scripts/lumos:11218`。

**攻擊者前提**:不需要攻擊者,這是純粹的正確性/訊息精準度問題,不影響任何安全性質(退路仍然是「不可信就換地方鎖」,不會變成不鎖)。
severity: minor
blocking: 否

## 沒有列入發現的殘留(已由作者誠實揭露,查證屬實)

- `_vault_lock_where`、`_lens_cache_write`、`_bound_tests_filter_probe` 這三處,checks 通過之後緊接著的 `os.chmod(...)`/開檔寫入仍有單一步的同帳號搶跑窗口——這點在 `_trusted_private_dir` 與 `_mkdir_trusted_under_home` 的「誠實邊界」段落都寫了「不得宣稱換掉也擋得住」,查證這句話對這三處是準確、完整的:每處通過檢查後就只剩一步動作,不是好幾步藏著沒講。發現 1 的問題在於 `cmd_dispatch_lens_arm` 這一處揭露的殘留範圍(只講到「空資料夾」)沒有涵蓋到程式碼實際多做的那一步(`chmod`),已經單獨列為發現。
