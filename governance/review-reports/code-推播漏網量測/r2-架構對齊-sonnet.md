severity: minor

**問一:分層與依賴方向**

對齊。新碼放在 `governance/eval/lens-utilization/recount.py` 這一層(治理量測工具),向下借 `scripts/lumos`(核心 CLI)的開頭欄位解析函式,走的是本專案既有的「SourceFileLoader 借模組」慣例,不是跨層直呼私有介面或用 `sys.path.insert` 改路徑硬 import。同一支檔案裡本來就有 `_load_hook_helpers()`(借 `check-graph-sync.py`)與 `_hook_filter()`(借 `impact-hook.py`)兩個用同一招借模組,`governance/eval/k1_stop_replay.py` 借 `scripts/lumos` 也是同一招,`scripts/test_lumos.py` 的 `_load_lumos_inproc()` 更是連「懶載入+global 快取單例」都同款。呼叫方向維持單向(governance/eval → scripts/lumos,scripts/lumos 不反向依賴 governance),沒有發現循環或跨層直呼。

引句:「p = Path(__file__).resolve().parents[3] / "scripts" / "lumos"」
file: `governance/eval/k1_stop_replay.py:11`

`_make_relater` / `_make_existence` 把原本 `Relater` / `Existence` 兩個 class 改成閉包,命名與寫法對齊 `scripts/lumos` 本體的 `make_resolver(notes, by_stem)` 閉包慣例(回傳內層函式,外層變數當快取狀態,不用 class)。

引句:「def _make_relater(repo: Path, vault: Path, budget: dict | None = None, timeout: float = 60.0):」
file: `scripts/lumos:370`

兩段式 `run_misses`(先掃逐字稿收事件、再叫 impact/git 分類)是把原本只護著 impact 呼叫的預算,擴大成一把總預算讓掃描、impact、git 三處共用;沒有另開一條新的呼叫鏈,`_budget`/`_left` 的命名也跟 `replay_weekly.py` 既有的 `_left()` 同名同義,只是因為要在多個閉包間共享,才把狀態從閉包內的區域變數改成顯式傳遞的 dict——這是既有單預算模式的合理延伸,不是引入新層級。

引句:「def _left(budget) -> float:」
file: `governance/autonomous_loop/replay_weekly.py:75`

不對齊:0 條。

**問二:命名與錯誤處理**

大致對齊,發現兩條輕微不一致。`_read_jsonl` / `_claude_in_repo` / `_codex_meta` 這組共用前奏被 `scan_file`、`scan_codex_file`、`run_misses` 三處呼叫,取代原本兩份幾乎一樣的手刻解析,錯誤處理維持「壞行只跳那行、繼續讀」與既有 `except OSError: return [], 0` 的容錯風格一致;`_atomic_json` 的暫存檔命名（pid 尾碼＋`os.replace`）現在跟 `refresh_labels._atomic_write_json` 同款。

引句:「tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")」
file: `governance/eval/refresh_labels.py:47`

E1
severity: minor
blocking: 否
引句:「def _lumos_mod():」
file: `governance/eval/lens-utilization/recount.py:34`
`_lumos_mod()` 是本檔第三個「借模組」函式,但沒有跟同檔既有的 `_load_hook_helpers()`(34 行,眼前這個新函式緊跟在它後面同一種用途)同一種命名模式(`_load_*`),改用 getter 式的 `_lumos_mod`。功能與借法都對齊,純粹是同檔內兩個做同件事的函式命名風格不統一。

E2
severity: minor
blocking: 否
引句:「log "推播漏網週跑原始:$(echo "$out" | head -1)"」
file: `governance/autonomous-loop.sh:437`
`run_lens_weekly()`(`governance/autonomous-loop.sh:460`)把「記原始 JSON 那行」放在「逐行印 LOG:」之前,而它自己的註解才寫「照 run_replay 的慣例」;但鄰居 `run_replay()` 在 437 行是先跑完 LOG: 迴圈、438 行才記原始 JSON(還特地留註解講這是慣例——「原始 JSON 全文另存一行」)。功能不受影響(fail-open、兩行都會印),但這處日誌順序跟被聲稱要照的慣例本身相反。

**問三:第二種做法**

不對齊:0 條(major)。四個提示的高風險點都收斂成單一做法,沒有把上一輪要收掉的第二種做法換個樣子留下來:

- 切段:拿掉自訂 `_CHAIN_RE`/`_strip_quoted_keep`,`_search_segments` 改成完全借用本檔既有(r1 就已借好的)`_segment_command`/`_safe_tokens`,只多做「引號內佔位字元」與「先逐行再切段」兩步前處理,沒有另開第二條切詞邏輯。

引句:「切段沿用 hook 的 _segment_command(; && || | 都切,管線後段本來就不含 search)、」
file: `scripts/hooks/claude/check-graph-sync.py:290`

- 讀檔前奏:`scan_file`、`scan_codex_file`、`run_misses` 三處原本各自手刻一份 jsonl 讀取+cwd 篩選,現在全部改呼叫同一份 `_read_jsonl`/`_claude_in_repo`/`_codex_meta`,run_misses 的兩段式掃描也是呼叫這三支共用函式,沒有殘留第二套解析。

- 開頭欄位解析:`_about_map` 改成呼叫 `scripts/lumos` 本體的 `split_frontmatter`/`parse_frontmatter`/`as_list`/`strip_quotes`,跟 impact 讀到的是同一份解析邏輯;唯一多出來的「單行 `[a, b]` 再拆一步」是明確標註在借用之上的補丁(本體真的沒收這格式),不是另立一套獨立解析器。

- 預算控制:`_budget`/`_left` 一把總預算同時管掃描階段(`files_unscanned`)、`_make_relater` 的 impact 呼叫(`impact_timeouts`)、`_make_existence` 的 git 呼叫(`git_skipped`),不是三處各自算各自的預算。

不對齊共 2 條,其中 major 0 條,全份最高嚴重度是 minor。
