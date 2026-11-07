severity: minor

審查範圍是 `r2-repair-甲.patch`(`scripts/lumos`),乙補丁只看鉤子那半的資源面。我在 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資源-sonnet/` 用 `git clone --shared` 複製 HEAD a1456f8f6,配假 `ast-grep` 實跑,收尾已全部刪除。沒有動 repo,沒有 gctl-run-*。

**第一輪 F1–F4 重跑結果:四條都修好了。**

| 情境 | 第一輪 | 這輪 |
|---|---|---|
| F1:刪 200 個 5MB 已追蹤檔,另加一支新 `.kt` | 約 9 秒、最大常駐 3,984,146,432 位元組(約 4GB) | 1.5 秒、最大常駐 375,439,360 位元組 |
| F1 對照:什麼都不刪 | 1.9 秒(3000 支 `.kt`) | 1.1 秒、376,700,928 位元組 |
| F2:新增 `app/My File.kt`、`app/a missing.kt` | `ValueError`,rc1,沒有 JSON | 正常,狀態 clean、有 JSON |
| F3:`build/gen/` 底下 10 萬支未追蹤 `.kt` | 13.8 秒 | 2.7 秒,回「超過 50 支」 |
| F4:假 `ast-grep` 睡 300 秒,另開一個同群組的 `sleep 301` | SIGINT 留孤兒 | SIGINT 與 SIGTERM 都沒孤兒、`.lumos/` 底下沒有快照目錄殘留、登記檔清空、系統暫存區沒有新 SARIF;`--budget 4` 逾時也乾淨 |

F1 的 375MB 是 lumos 載入後的底線,跟刪除檔無關。

另外量到的成本與一個要注意的現象:
- 列過濾器設定的 `git config` 每個程序只跑一次(有快取),約 0.03 秒。我造了 `filter.lfs.*` 設定去跑,沒壞。
- 被擋的 SIGTERM 遮罩確實會被子程序繼承:SIGTERM 收不掉那個 `sleep`,只有 SIGKILL 收得掉。正常的收尾路徑一律用 SIGKILL,所以不受影響。

**F1 `_lint_wt_blobs` 沒有大小上限,有改動的已追蹤大 `.kt` 仍整份從 HEAD 讀進記憶體,之後才被超大檔規則略過**

這輪只把「刪除檔」改成配對才讀。但改過的追蹤檔(`want.append(p)` 那一路)也是用同一個 `cat-file --batch` 整批讀進 `r.stdout`,再切片複製。要被「超過 60000 行或 5MB」略過的檔,也先讀完才被略過。
- 實測:HEAD 追蹤 40 支約 4.3MB 的 `.kt`(共 174MB),各追加一行。
- 結果:最大常駐 996,409,344 位元組,比底線多約 620MB,約為被讀資料量的 3.6 倍;最後這些檔全被略過。
- 上限:一回合最多 50 支,所以有界。但單檔大小沒有上限,大型產生碼檔案(幾十 MB)會線性放大。
- 既有的帶上限讀法:`scripts/lumos:47093` 的 `_nodehome_cat_blobs_capped` 先問大小、超過上限的不讀。
- 為什麼只算 minor:一回合最多 50 支,實務上要有很多幾十 MB 的追蹤 `.kt` 才會暴衝。

引句:「blobs = _lint_wt_blobs(repo_root, want)」
file: `scripts/lumos:40433`
severity: minor
blocking: 否

**F2 SARIF 輸出改接檔案後,檔案很大時仍整份讀進記憶體再 `json.loads`,沒有任何大小上限;鉤子那邊也把 `--json` 輸出整份收進記憶體**

`_lint_spawn_argv` 把標準輸出接到暫存檔,但 `_lint_run_and_parse` 讀回時仍是 `f.read()` 加整份解析,base 與 head 兩邊各一次。
- 實測:假 `ast-grep` 吐出 600000 條結果。
- 結果:12.2 秒、最大常駐 1,960,853,504 位元組;10 萬條時 2.5 秒、611,663,872 位元組。約 8 倍檔案大小的記憶體。
- 鉤子端:`proc.communicate` 會整份收 `--json` 的 stdout。10 萬條告警時 stdout 是 20,777,945 位元組(約 20MB)。
- 為什麼只算 minor:這條不是這輪新增的,原本 shell 版也是整份讀。一回合最多 50 支、單檔受 5MB 上限約束,實務上很難造出這個量。留作回頭條件。

引句:「stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.DEVNULL)」
file: `scripts/lumos:41190`
severity: minor
blocking: 否

**F3 lint-new 被 SIGKILL 或 SIGHUP 時,暫存 SARIF 留在系統暫存區沒人掃,SIGHUP 另留下工具群組孤兒**

`temps` 登記只靠 SIGTERM 處理器與 `finally` 清,這兩條都不涵蓋 SIGKILL 與 SIGHUP。`.lumos/lintbase-*` 有一天的過期掃除(`_lint_new_clean_stale`),但 `lumos-lint-*.sarif` 沒有。
- 實測 SIGHUP:`lintbase-*` 快照目錄、`lumos-lint-*.sarif` 與 `sleep 301` 的群組都留著,登記檔還留著那個群組編號。
- 實測 SIGKILL:同樣留下暫存 SARIF 與快照目錄,工具群組也還活著。
- 系統暫存區的 `/var/folders/.../T/` 有一個 22:52 的舊 `lumos-lint-*.sarif`,是更早留下的同類殘骸(不是我造的)。
- 範圍:只在手動關終端機或機器強殺時才走到(鉤子只送 SIGTERM 與 SIGKILL,且 SIGTERM 先給 lint-new 時間收尾)。每次一個檔,大小是工具當時已寫出的量。

引句:「_LINT_WT_REG["temps"].add(temp_path)    # 工作樹模式:被 SIGTERM 時處理器照這份刪(os._exit 不跑下面的 finally)」
file: `scripts/lumos:41157`
severity: minor
blocking: 否

總結:最嚴重是 F1(改動過的大 `.kt` 無大小上限、約 3.6 倍記憶體),第一輪 F1–F4 全部修好,新發現 3 條都是 minor,會擋 0 條。
