severity: minor

我拿真實的 web-notes repo(903 篇節點、14714 個追蹤檔、治理帳 20.4MB 共 122696 行、審查帳 4.9MB)和 0beb6d7d 的舊版 `scripts/lumos` 對照實測。

**實測數字**
- `lumos doctor` 全跑:舊版 67.6 秒,新版 70.3 秒(約 +4%)。我用 PATH 替身記下 git 呼叫,舊版 1145 次、新版 1170 次。多出來的是 `git show` +10、`rev-parse` +10、`ls-files` +3、`diff` +1。
- 這 +10 次 `show` 來自「真的帶 `when-file/gone/status` 條件的筆記」,不是每篇筆記都多叫。沒有可判條件的筆記會在 `if not cheap: return []` 直接回,不叫 git。
- 單次 git 約 0.017~0.021 秒。`_drift_probe_tree(root,"disk")` 約 0.34 秒,同一次執行只列一次。
- 子程序都走 `_lens_git`(逾時 20 秒,`subprocess.run` 在逾時或 Ctrl-C 時會收掉 git)。新增的 `show`、`ls-files`、`check-ignore`、`diff` 都有逾時。
- 20MB 治理帳讀一次(`_gov_vc_gate_events("spec-gate")`):0.16 秒,峰值 RSS 32 到 100MB。`_spec_gate_latest_merged` 整個(審查帳加治理帳):0.22 秒,RSS 106MB。
- 把審查帳放大到 112MB、5 萬列,讀一次 0.82 秒、RSS 209MB。帶不帶 `fields` 差不多(175MB 對 209MB),所以 `_spec_gate_low_not_red` 沒帶 `fields` 不構成問題。
- `_lint_born_true` 放 2 萬行條件,0.88 秒、RSS 104MB,在線性範圍內。
- `summary-add --dry-run` 對 20 萬字元的長行,約 1 秒。
- `check-ignore` 一次帶 8000 個路徑沒問題。真正超過 ARG_MAX 時 `_lens_git` 的 `OSError` 會被接住,回空集合,不崩。

**1. `_lint_excluded_lines` 對一行很多空白的「已排除」行會三次方變慢,而 lint 與 doctor 對每篇 project 筆記都會跑它**
severity: minor
blocking: 否
- 輸入:project 筆記的「實務隱患」節裡有一行 `- 已排除：` 後面接 N 個空白再接 `x`(沒有第二個冒號)。
- 路徑:`_lint_excluded_lines` 的預檢 `re.match(r"^已排除\s*[:：]", s)` 通過,接著呼叫 `_excluded_line(ln)`,走 `_EXCLUDED_RE = ^已排除\s*[:：]\s*([^:：]+?)\s*[:：]\s*(.*)$`。懶惰的 `[^:：]+?` 可以吃空白,前後又各有 `\s*`,全部落空時是 O(N³)。
- 實測(直接呼叫 `_lint_excluded_lines(note, text)`):400 個空白 0.12 秒,800 個 0.94 秒,1600 個 7.44 秒。每加倍慢 8 倍,推算 3000 個空白約 50 秒。對照:同長度的 `已排除：aaaa…` 是 0.000 秒,只有空白會觸發。
- `_excluded_line` 本來只在規格閘跑。這次新增的 lint 路徑讓 `lumos lint` 和 doctor 的每篇 project 筆記都會碰到它。修法是把 `[^:：]+?` 改成不含空白的類別,或預檢後先限制行長。
引句:「ex = _excluded_line(ln)」

**2. `_refcheck_scan` 與 doctor P 段在迴圈裡每個 missing 都重建一次「標了新增」集合,變成 O(missing × planned)**
severity: minor
blocking: 否
- 輸入:一份文件有 N 行 `` `scripts/new_i.py` (新增) `` 和 N 行不存在的 `` `scripts/gone_i.py` ``。
- 路徑:`_refcheck_scan` 對每個 `status == "missing"` 的 claim 都現算一次 `{x.rstrip("/") for x in planned}`。doctor 的 `if token.rstrip("/") in {x.rstrip("/") for x in _planned}:` 是同樣的寫法。
- 實測:`lumos refcheck`,N=2000 時新版 1.31 秒、舊版 0.63 秒。N=8000 時新版 9.0 秒、舊版 0.78 秒。成長是平方的,N=16000 約 36 秒。
- 實際筆記不會有幾千條路徑,所以只標 minor。修法是把集合移到迴圈外算一次。
引句:「c["token"].rstrip("/") in {x.rstrip("/") for x in planned}:」

**無 finding,只記錄量到的**
- 推送閘新增的治理帳讀取只在有「活的」計劃(doing,或這次推送改到的 done)時才做,結果快取在 `ctx["sg_gov"]`。`(b)` 出口的 `_nogo_ctx_gov` 另讀一次同一本帳,所以最壞讀兩次,約 0.3 秒、各約 70MB。
- doctor 的 git 呼叫沒有總時限(`_drift_probe_tree` 本有 `deadline` 參數,這裡沒傳)。只有在 git 本身卡住時才會累積成每篇 20 秒的等待,正常機器不成立。
- `_gate_event` 沒帶 `head_sha` 時,`_sp_run_text(["git","rev-parse","HEAD"])` 沒有逾時。這次新增的呼叫端 `_spec_gate_record` 就沒帶,但這是舊 helper,`rev-parse HEAD` 不會實際卡住。

最嚴重 severity:minor,blocking 共 0 條。

我已刪除自己的暫存目錄 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/資源-sonnet`。
