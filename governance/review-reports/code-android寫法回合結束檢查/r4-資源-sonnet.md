severity: major

第三輪資源席 F1(工具輸出不設寫入上限)已修好。新形狀有一個新的 major:收工點名鉤子用的 `_impact_wt_nofilter` 記憶體隨改動檔數線性長大。另有兩個 minor。我沒修改 repo,臨時目錄 `/private/tmp/lumos-seat-work/code-android寫法回合結束檢查/資源-sonnet` 已刪,實驗留下的 `sleep 301` 殘留程序也已清掉。

**前輪核對**
- **第三輪 F1 已修好。** 我用 `_lint_spawn` 搭假工具 `yes` 實跑:輸出停在 68157440 位元組(64MB 讀取上限加 1MB 餘量),約 0.1 秒內被 SIGXFSZ 停掉(退出碼 -25)。上輪是 3 秒長到 3.7GB。
- **50 支大檔情境(縮成 20 支約 850KB,全部有改動)沒有問題。**
  - `_lint_wt_changed` 約 0.13 秒。
  - `_lint_wt_pairs` 約 0.21 秒,常駐約 86MB。
- **`--debug` 時間戳比對有效。**
  - 乾淨的 18339 檔 repo 上不呼叫 `hash-object`,一次約 0.45 秒。
  - 把全部檔案 touch 過後會整個 repo 重新雜湊,約 1.75 秒。方向是多查不漏查;雜湊結果沒回寫索引,所以每次點名都重算,屬可接受的線性成本。

**F1 收工點名影響分析把所有改動檔整份讀進記憶體,而且不分是不是程式碼**
- 失敗場景:一回合改了上千個 1MB 內的資產檔,例如重產 PNG 或 JSON。
  - `_impact_wt_nofilter` 先對所有候選做 `_nodehome_cat_blobs_capped`,沒給 `max_total_bytes`,每支各讀進記憶體。
  - 之後逐支讀工作樹版本、用 difflib 切行比對。
  - 判斷是不是程式碼的 `_impact_diff_seed_ok` 要等這些算完才執行,所以白算。
  - 舊路徑是逐檔跑 `git diff`,常數記憶體。
- 實測(每支 0.9MB,隨機二進位 PNG):

  | 改動檔數 | 耗時 | 常駐記憶體(基線約 45MB) |
  |---|---|---|
  | 30 | 1.5 秒 | 332MB |
  | 60 | 2.8 秒 | 423MB |

  每支約多 3MB。我是依這兩點線性外推:約 600 支會撞到鉤子的 30 秒內層預算,記憶體約 2GB;1000 支以上更高。這個外推沒有直接量過。
- 文字檔也一樣:200 支 735KB 加一行,耗時 2.3 秒,常駐約 537MB。
- 修法方向:先用 `_impact_diff_seed_ok` 濾掉不是程式碼的候選,再讀內容。再給讀取總量上限,超過的退回只用路徑當查詢文字。

引句:「blobs = _nodehome_cat_blobs_capped(repo_root, specs, cap, sizes=sizes, pre=_git_untrusted_c()) if specs else []」
severity: major
blocking: 是

**F2 difflib 在大檔大量改動時很慢,會吃光收工點名的預算**
- 失敗場景:一支約 1MB 的產生檔(幾乎每行都改,或行序被打亂)重產。
- 實測:20 支約 850KB 重度改動共 88.5 秒,約每支 4.4 秒。舊的 `git diff` 是毫秒級。
- `_impact_missing` 的 `subprocess.run` 以 `_inner_budget(default=30)` 為逾時,逾時會殺子程序並回空清單,所以不會卡死。代價是收工點名在這種回合靜默失效,並先吃掉約 30 秒。
- 修法方向:對行數多的檔改用只比行數、或逐行集合差,或超過行數門檻就退回只用路徑當查詢文字。

引句:「lines = [ln for ln in difflib.unified_diff(a, b, lineterm="", n=0) if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]」
severity: minor
blocking: 否

**F3 工具正常結束後留下的子孫程序不會被收,而且已從登記拿掉**
- 失敗場景:被跑的工具自己 fork 出背景程序後正常退出,例如 daemon 型工具。
- 實測:假工具 `fake2.sh` 在背景放 `sleep 301` 後輸出 SARIF 並退出 0。`_lint_run_and_parse` 回 `([], True)`,`sleep 301` 仍活著,屬於獨立的 session 群組,已不在登記裡,收工鉤子也找不到。
- 這段沒在這次 diff 裡改,而且白名單只放 `ast-grep scan`,目前沒有真實工具會這樣,所以只標 minor。
- 這次新加的 `preexec_fn=_lint_wt_fsize_cap()` 路徑下,工具被 SIGXFSZ 停掉時同理,子孫不會被收。
- 修法方向:`communicate` 正常返回後,在 `_lint_wt_unregister` 之前也 `_kill_proc_group(proc)` 一次。

引句:「stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.DEVNULL, preexec_fn=_lint_wt_fsize_cap())」
file: `scripts/lumos`(`_lint_run_and_parse` 的 `proc.communicate` 之後)
severity: minor
blocking: 否

總結:最嚴重是 major(F1 收工點名影響分析把全部改動檔整份讀進記憶體且不分是不是程式碼),會擋 1 條。
