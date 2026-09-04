# r1 架構對齊審查——主session鏡頭利用率 第一段落地

被審:`governance/review-reports/lens-stage0/r1-snapshot.patch`(對應已提交 `a39741a`)。
唯一工作:判「這份 diff 跟本專案既有做法一不一致」,不找 bug、不評風格。

## 一、分層與依賴方向

`recount.py` 放 `governance/eval/lens-utilization/` 且自己解析逐字稿(不叫任何 hook 的函式、不 subprocess 呼叫 lumos),
這個位置與做法跟既有的同類唯讀重算腳本一致——`governance/eval/seat-coverage/recount.py`、`governance/eval/ablation_lumos_first.py`、
`governance/eval/k1_stop_replay.py` 都是「一個主題一個目錄、讀原始資料源(canary log / 逐字稿)、印分佈、不寫帳」的同一形狀,層級放對了。

`_shebang_is_code` 放在 `scripts/hooks/claude/impact-hook.py` 內部(file: `scripts/hooks/claude/impact-hook.py:87`)也對——本專案的 hook
彼此不互相 import(逐一查過 `dispatch-lens-hook.py`/`ci-status-hook.py`/`lumos-entry-hook.py`/`check-graph-sync.py`/`impact-hook.py` 的
import 區,零跨檔匯入),每支 hook 自成一個獨立可讀單元是既定形態,把它放在呼叫它的那支檔案裡沒有跨層直呼的問題。

但這支函式做的事——擴大「什麼算 code 檔」的定義(無副檔名靠 shebang 也算)——踩進一個已經有機械守衛的地帶:`scripts/test_lumos.py:5500`
的 `t_code_exts_four_lists_agree` 明文釘住「pre-commit / post-commit / check-graph-sync.py / impact-hook.py 這四份 CODE_EXTS 必須一致」,
這條線正是 2026-08-21 體檢 #7 因為漏了一份清單、腳本溜過同步閘的教訓。這次新加的 shebang 判定只進了 impact-hook.py 一處
(file: `scripts/hooks/claude/impact-hook.py:87-100`),`check-graph-sync.py` 的 `find_graph_root`/`is_code_file`(file:
`scripts/hooks/claude/check-graph-sync.py:72,149`)沒有對應變化,也沒有新測試把這個新維度納入一致性檢查——見下 f3。

第二個真正的分層問題出在 `recount.py` 自己重找「vault 在哪」與「怎麼切一段 Bash 指令」,這兩件事本專案都已經有單一實作,
detail 見三(第二種做法),這裡先點出來:它們屬於「跨檔重複的邏輯」,不是「跨層直呼」,所以歸在 f1/f2 判 major,理由見下。

## 二、命名與錯誤處理

`_ttl_mark`(file: `scripts/hooks/claude/impact-hook.py:151`)延續既有 `_ttl_*` 家族命名(`_ttl_marker_path`/`_ttl_lazy_cleanup`/
`_ttl_should_inject`),`mark=` 這個布林旗標名字也直白對得上它控制的動作,跟命名慣例一致,沒有問題。

錯誤處理範圍也對得上這支檔案原本的寬鬆風格:`_shebang_is_code` 把 `is_file()` 和 `open()+read()` 包在同一個 `try/except OSError`
(file: `scripts/hooks/claude/impact-hook.py:87-96`),這跟 `main()` 原本讀 `.lumos/impact.json` 時把 `is_file()` 和讀檔+parse
包在同一個 try 區塊的既有寫法同一種風格,不是新引入的寬鬆度。`recount.py` 的 `repo_paths()` 用 `except Exception: pass` 包住
`subprocess.run(...git worktree list...)`,這跟 `lumos-entry-hook.py` 的 `_repo_root()` 對 `subprocess.run` 同樣用
`except Exception:` 是同一慣例(hook/腳本對外部程序呼叫一律寬抓),不算不一致。

唯一一個命名上比較微妙的地方是 `_ttl_should_inject`(file: `scripts/hooks/claude/impact-hook.py:162`)——函式名字念起來是「該不該注入」
的純查詢,但 `mark=True` 預設仍然帶寫入副作用(query 跟 mutate 混在同一個名字底下)。這次的修法是新增 `mark=False` 讓 main() 繞開副作用,
而不是把「查詢」與「標記」徹底拆成兩支正交函式,是延續這支函式本來就有的舊 wart,不是這次新造的分歧模式——但既然這次特地拆出了
`_ttl_mark` 這支純副作用函式,`_ttl_should_inject` 本身沒有跟著改名或收斂職責,讀起來還是「一個名字兩件事」。列為 minor,不擋。

## 三、第二種做法

`recount.py` 裡有兩處明確重造了本專案已經有單一實作的東西,而不是 import 既有函式——這正是本專案自己反覆強調的紀律
(`governance/eval/ablation_lumos_first.py` 裡有一句「★r1 合約席:判準單一實作來源★……同目錄 retrieval_eval_multiword 早有此教訓
（計分一律 import,兩份實作立刻漂移）」,`k1_stop_replay.py`、`scripts/test_lumos.py` 的 `t_impact_hook_*` 也都用
`importlib`/`SourceFileLoader` 去 import 帶連字號檔名的既有腳本,不是重寫一份)。

1. **Bash 切詞/分段**:`classify_bash()`(file: `governance/eval/lens-utilization/recount.py:78`)自己用正則切分 Bash 指令,
   但 `scripts/hooks/claude/check-graph-sync.py:178` 的 `_segment_command`(切 `&&`/`||`/`;`/`|`)和 `:183` 的 `_tokens_of`
   (`shlex.split`,quote-aware)已經是同一件事的既有單一實作,且是 dispatch 派工詞裡明白點名的對照檔。新寫的正則不吃引號、
   `&` 和 `&&`也不分,行為比既有實作弱,還是兩套獨立邏輯。

2. **vault 定位**:`vault_slug()`(file: `governance/eval/lens-utilization/recount.py:37`)重找「`docs/` 下哪個子目錄是
   `*-knowledge`」,但這件事本專案已經有兩份現成實作——`scripts/lumos:11375` 的 `_vault_in`/`:11391` 的 `find_vault`
   (含 legacy `docs/knowledge` 與 standalone vault root 的判斷)、以及 `scripts/hooks/claude/check-graph-sync.py:72` 的
   `find_graph_root`。這支是第三份,還漏掉前兩份都有的 legacy `docs/knowledge` fallback。

`norm_note()`(file: `governance/eval/lens-utilization/recount.py:46`)用 `docs/{slug}/` 當 key 去找子字串、取後段當
vault-relative 路徑,這個「`docs/{slug}/` 前綴」寫法跟 `scripts/lumos:16675` 既有的 `vault_rel = f"docs/{slugs[0]}/"` 是同一個
既定慣例(只是方向相反,一個是組出路徑、一個是從路徑裡剝出來),不算第二種做法,判定不列為不對齊。

---

### f1

引句:「for seg in re.split(r"[;|&]+", cmd):」

file: `governance/eval/lens-utilization/recount.py:97`(既有實作對照:`scripts/hooks/claude/check-graph-sync.py:178-189`)

severity: major
blocking: 是

### f2

引句:「def vault_slug(repo: Path) -> str | None:」

file: `governance/eval/lens-utilization/recount.py:37`(既有實作對照:`scripts/lumos:11375,11391`、`scripts/hooks/claude/check-graph-sync.py:72`)

severity: major
blocking: 是

### f3

引句:「def _shebang_is_code(abs_path: Path) -> bool:」

file: `scripts/hooks/claude/impact-hook.py:87`(既有守衛對照:`scripts/test_lumos.py:5500` `t_code_exts_four_lists_agree`)

severity: minor
blocking: 否
⚠ 判準不完全機械——這支測試釘的是 CODE_EXTS 副檔名集合逐字相同,沒有明文涵蓋「無副檔名靠 shebang」這個新維度,
所以嚴格說這次改動沒有讓任何既有測試變紅;算不對齊是因為它在同一個「什麼算 code」的概念家族裡,只改了兩個實作點的其中一個。

### f4

引句:「def _ttl_should_inject(session_id: str, file_abs: str, ttl_sec: float, mark: bool = True) -> bool:」

file: `scripts/hooks/claude/impact-hook.py:162`(對照本次新增:`scripts/hooks/claude/impact-hook.py:151` `_ttl_mark`)

severity: minor
blocking: 否

---

不對齊共 4 條,其中 major 2 條。
