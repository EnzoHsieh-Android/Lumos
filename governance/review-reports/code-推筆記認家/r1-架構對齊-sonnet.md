severity: major

1. `governance/eval/home_audit.py` 自己寫了一個把「已載入的圖譜(Env)」轉成家對照表輸入形狀的轉接器 `_SideFromEnv`,再繞去呼叫 `_nodehome_homes`;但同一個提交在 `scripts/lumos` 裡已經新增了做同一件事、更直接也有快取的 `_impact_home_map(env)`(供改檔前推筆記熱路徑用)。兩邊都是「Env → 家對照表」,同一個提交內就分岔成兩條轉接路徑,正好撞上這支核心函式自己文件裡警告的那句話。
引句:「homes, _own = m._nodehome_homes(None, _SideFromEnv(env))」
引句:「把 Env 包成 _nodehome_homes 要的形狀(它只讀 .notes 的 type/status/about)」
file: `scripts/lumos:21464`(`_impact_home_map(env)`,同一提交新增,直接吃 `env.notes` 建家對照表,不需要包裝類別)
file: `scripts/lumos:18112`(`_home_map_from_notes` 文件本身寫「兩套算法一定分岔,而分岔時沒有東西會翻紅」)
severity: major
blocking: 是

2. home_audit.py 的文件宣稱「家對照表直接呼叫 lumos 裡那支唯一的算法([S1]),不另寫一份」,但實際上是重新寫了一層轉接器(finding 1),不是零額外程式碼地重用;宣稱與實作有落差,屬於「自造一個已經有的工具函式」的第二種做法,不是單純措辭問題。
引句:「零依賴,家對照表直接呼叫 lumos 裡那支唯一的算法([S1]),不另寫一份」
file: `governance/eval/home_audit.py:77`(`class _SideFromEnv`)
severity: major
blocking: 是

3. `scripts/lumos` 新增的 `_impact_repo_files(repo_root)` 自己用 `subprocess.run(["git", "-C", str(repo_root), "ls-files"], ...)` 直呼 git,沒有走本檔既有的單一 git 呼叫封裝 `_lens_git`(`_nodehome_git` 等既有呼叫點都是透過它)。專案對「同一件事只有一套算法」很在意,這裡是繞過既有封裝、自己重建一份逾時/錯誤處理邏輯。但要註明:同檔案裡本來就存在另一個更早的 `_testmap_git`(20074 行)也是直接 `subprocess.run` 不經 `_lens_git`,所以「git 呼叫不只一套」在這支檔案裡並非這次才出現的新問題,只是這次又多添了一個第三種寫法。判不準是否要當作「新引入」還是「延續既有舊帳」,交編排者裁。
引句:「r = subprocess.run(["git", "-C", str(repo_root), "ls-files"],」
file: `scripts/lumos:22430`(`_lens_git`,專案既有的單一 git 呼叫封裝,`_nodehome_git` 等經由它呼叫)
file: `scripts/lumos:20074`(`_testmap_git`,舊帳:同檔案裡另一個不經 `_lens_git` 的直呼)
⚠ 判不準,交編排者:是這次新引入的第二種做法、還是延續既有舊帳,我判不準。
severity: minor
blocking: 否

4. `scripts/hooks/claude/impact-hook.py` 與 `scripts/hooks/claude/check-graph-sync.py` 的改動只是文字/欄位讀取(新增 `x.get("home")`),命名與「只在 True 時才出現該鍵」的條件鍵慣例跟既有的 `about_hit` 完全一致,沒有引入新做法或跨層直呼。跟給定對照檔 `dispatch-lens-hook.py`、`_hookevent.py`、`ci-status-hook.py`、`lumos-entry-hook.py` 比對,分層(hook 只格式化、判斷邏輯留在 `scripts/lumos`)一致。
severity: clean
blocking: 否

5. `scripts/lumos` 主程式裡的新欄位(`homes` 頂層鍵在 JSON 輸出裡用 `**({"homes": all_homes} if all_homes else {})` 有內容才出現)、新旋鈕 `LUMOS_IMPACT_HOME` 沿用既有 `LUMOS_IMPACT_*` 命名與 `_impact_knob` 讀法、新閘名 `check-s11` 沿用 `check-sN` 序列,都跟既有慣例一致,沒有另一套讀法或另一套命名規則。
severity: clean
blocking: 否

6. `governance/eval/home_audit.py` 用 `importlib.util.spec_from_file_location` + `SourceFileLoader` 把 `scripts/lumos` 當模組動態載入、直呼底層函式,這件事本身在同目錄有先例(`governance/eval/k1_stop_replay.py` 也是同一套寫法載入 `scripts/lumos` 直呼 `_estimate_remaining_defects`),跟風險掃描給的對照檔(`ledger_analysis.py`/`rule_conflict_scan.py`/`build_goldset.py`)寫法不同(那三支不碰 lumos 內部或走 subprocess),但跟同目錄實際存在的另一種先例一致,不算跨層/無先例的新做法。
severity: clean
blocking: 否

總結:比對對照檔 `governance/eval/ledger_analysis.py`、`rule_conflict_scan.py`、`build_goldset.py`、`k1_stop_replay.py`、`scripts/hooks/claude/dispatch-lens-hook.py`、`_hookevent.py`、`ci-status-hook.py`、`lumos-entry-hook.py`,以及 `scripts/lumos` 內既有的 `_nodehome_side`/`_lens_git`/`_impact_home_map`/`_testmap_git`。主要問題集中在 finding 1、2:home_audit.py 沒有重用同一提交裡已經寫好的 `_impact_home_map(env)`,反而自造 `_SideFromEnv` 轉接器繞去 `_nodehome_homes`,在「Env → 家對照表」這件事上開出第二條路,且文件宣稱與實作不符。finding 3 是否算「這次引入的新問題」判不準,列為 ⚠ 交編排者。其餘(hooks 改動、旋鈕/鍵值命名、動態載入模式)皆與既有寫法一致。
