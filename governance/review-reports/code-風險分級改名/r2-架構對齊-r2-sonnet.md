severity: major

## F1
severity: major
blocking: yes

`_is_code_file`（scripts/lumos:5621-5632，新函式）判斷「沒副檔名的檔首行是不是 #!」時自己重開檔案讀 bytes，跟既有 `_nodehome_required`/`_NodehomeSide.shebang`（scripts/lumos:20832-20853）做的是同一件事、同一段邏輯，卻是第二份實作，沒有共用任何既有的讀取/快取機制。

引句: try:\n        with open(Path(rr) / path, "rb") as f:\n            return f.read(200).split(b"\n", 1)[0].startswith(b"#!")

對照既有實作，同一個「前 200 bytes、取第一行、看是不是 #!」判斷式在 `_nodehome_required` 裡已經有一份：

引句: ok = side.shebang[p] = bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")

兩邊字面上幾乎逐字相同（`f.read(200)` vs `head[:200]`、`.split(b"\n", 1)[0].startswith(b"#!")` 完全一致），差別只在讀取來源——`_nodehome_required` 走 `_NodehomeSide._reader`（能讀 git index/某個 commit/磁碟三種來源，且有跨側快取 `share`/`changed`），`_is_code_file` 直接 `open()` 讀磁碟。就算場景不同（一個要處理 git 索引狀態、一個只需要查目前磁碟上的幾個 diff 路徑，不值得為此建一整套 `_NodehomeSide` 快照），至少「判斷首行是不是 #!」這段純邏輯可以拆成一個共用小函式讓兩邊呼叫,而不是各寫一份——這正是同一份 patch 別處自己寫的規矩（`_plan_system_links` 的docstring：「★全檔唯一的「計劃連到誰」★…代碼審 r1 架構席:別再開第二支平行函式,兩套算法會各自漂」，scripts/lumos:5266-5268，這批只是把訊息改成「風險低」但邏輯沒動）。這支新函式踩了同一批人自己立的規矩：兩套算法以後任一邊改判準（例如排除某類 shebang、放寬讀取位元數）另一邊不會跟著動，會漂。

file: `scripts/lumos:5621`
file: `scripts/lumos:20852`

## F2
severity: major
blocking: yes

`_spec_gate_push_report`（scripts/lumos:5847-5861，新函式）是一支完整重寫「算這個範圍裡風險低計劃候選、跑掃描」的函式——git diff --name-only 找改動檔、算 vrel、call `_spec_gate_push_candidates`、call `_spec_gate_push_scan`——這一整條序列在正下面幾行的既有函式 `_spec_gate_push_check`（scripts/lumos:5863 起）裡已經有一份幾乎一樣的實作。

引句: r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--name-only", git_range, "--"], capture_output=True, text=True, errors="replace")

`_spec_gate_push_check` 裡同一段序列（同樣的 git diff --name-only → vrel → `_spec_gate_push_candidates` → `_spec_gate_push_scan`）本來就存在，函式簽名沒變、邏輯沒被抽成共用子程式,`_spec_gate_push_report` 是整段複製再改參數(quiet=True, manual_only 開關)。更嚴重的是：這支新函式目前在 `scripts/lumos`、`scripts/hooks/pre-push`、`scripts/test_lumos.py` 裡完全沒有任何呼叫端（用 `grep -n "_spec_gate_push_report\b"` 全 repo 只找到它自己的定義那一行）。圖譜節點 `docs/lumos-toolchain-knowledge/Systems/規格閘.md` 寫著它是「給分級用」的東西，但 `_spec_gate_push_check` 裡真正印「改動風險分級:light」的那段（scripts/lumos:5890-5892）用的是自己內部呼叫 `_spec_gate_push_scan` 拿到的 `oks`，並沒有去呼叫 `_spec_gate_push_report`。也就是說這批多刻了一份目前沒人用、跟既有函式重複一半邏輯的候選收集/掃描路徑,以後兩邊各自改會漂,而且現在就是死碼。

file: `scripts/lumos:5847`(定義)
file: `scripts/lumos:5863`(既有同序列邏輯的起點，_spec_gate_push_check)
file: `scripts/lumos:5890`(真正印 light 的地方,呼叫的是 _spec_gate_push_scan 不是 _spec_gate_push_report)

---

對照過的既有寫法（沒發現問題的部分）：
- `_ledger_has_manual_only`（scripts/lumos:22270 附近）雖然在宣告 vault-free 的 pitfalls 檔案裡呼叫了 `find_vault`,但只讀一個 ledger 檔（`.canary-log.jsonl`）做字串子串比對,不建 Env、不解析任何節點,跟 `cmd_delguard_check` 裡 `gr = find_vault(Path(root))`（scripts/lumos:22014）「vault-free repo 找不到就靜默放行」的先例同一種輕量用法；圖譜節點 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 也明確把這支列成「★維持 vault-free★」的既定設計，是上一輪 r1 抓到「Env 載圖譜」之後改出來的收斂版本，不算引入新做法。
- `_spec_gate_push_scan` 新增的 `quiet`/`manual_only` 兩個布林旗標是單一函式擴充既有選擇性行為,跟這支檔案裡其他函式常見的旗標擴充模式（例如 `_ba`/`_fj` 這類 optional flag）一致,不算另開分支寫法。

引句: def _spec_gate_push_scan(env, rr, plans, git_range, quiet=False, manual_only=False):
