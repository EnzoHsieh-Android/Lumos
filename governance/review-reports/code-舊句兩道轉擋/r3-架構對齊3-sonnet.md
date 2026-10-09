severity: major

我只讀了 `r3-repair-lumos.patch`、`r3-repair-tests.patch`、`r3-repair-binding.json`,對照都在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/架構對齊3-sonnet/repo`(停在 59f8f92b)。沒讀 r1、r2 的檔和上輪席報告,也沒碰原工作目錄。

## A1 工作目錄紀錄走訪只擋最後一層符號連結,沒走專案共用的逐層守衛
severity: major
blocking: 是

- **修補寫法:** 修補把兩份走訪合成 `_note_reread_wt_verdicts`,docstring 宣稱「走訪工作目錄的紀錄資料夾只有這一份」。它判資料夾安不安全只用 `d.is_dir() and not d.is_symlink()`,只看最後一層。
- **既有對照:** 專案裡「逐層擋符號連結,加解析後要在 repo 內」已有唯一共用實作 `_repo_path_unsafe`。
  - 位置:`scripts/lumos:34047`。docstring 寫「只有這一份」。
  - 讀端也在用:`_retro_path_unsafe`(`scripts/lumos:13527`,docstring 明講「讀端、寫端、提示共用一個答案」,註解記著上一個迴圈的架構對齊席發現「自寫版只看資料夾本身,上層是捷徑就放行」);`_drift_ledger_path_err`(`scripts/lumos:38181`)也是。
  - 同一份紀錄的寫端 `_note_audit_write_verdict` 走 `_note_audit_safe_dir`,內部呼叫同一個共用守衛。
  - 結果:寫端會擋上層符號連結,讀端不擋,方向和 `_drift_ledger_path_err` 說的「讀寫同一條規則」相反。
- **我跑的實驗:** 臨時 repo 裡把 `governance` 做成指到 repo 外的符號連結,外面放一份合規紀錄。`_note_reread_wt_verdicts(root)` 照樣回出那份(含 `provenance_ok: True`),同一個路徑丟給 `_repo_path_unsafe(root, "governance/reread-verdicts", dirs=True)` 卻回 `('symlink', …/governance)`。
- **影響範圍:** 讀端結果只影響「記得提交」的提示、prepare 略過哪幾篇、`drift ack` 寫進表態的 verdicts 證據,check 只認已提交的樹。範圍有限,但這是第二種做法。
- **測試缺口:** 新測試 `t_reread_wt_records_guarded` 的 `dir-link` 組只造「資料夾本身是連結」,沒有上層是連結那組。
- 引句:「files = sorted(d.iterdir()) if d.is_dir() and not d.is_symlink() else []」
- 歸因:有證據的原有漏查。`git show 88322e46:scripts/lumos` 的 `_note_reread_uncommitted`(34875 行)與 `_drift_ack_reread_verdicts`(37980 行)兩份都是同一個最後一層寫法;59f8f92b 合併時照搬,沒換成共用守衛。

## A2 讀 JSON 遇到巢狀太深的處理另起一個包裝,沒用專案慣用的就地寫法,同源設定檔的兄弟閘也沒跟上
severity: minor
blocking: 否

- **修補寫法:** 修補新增 `_note_reread_json`,把 `RecursionError` 轉成 `ValueError("巢狀太深")` 再讓呼叫端只接 `ValueError`。
- **既有對照:** 專案慣例是在呼叫點就地寫 `except (ValueError, RecursionError)`,有 `scripts/lumos:12732`(`_fix_check_config`)、`scripts/lumos:26588`(`_node_flavor_of`)、`scripts/lumos:45779`(`_json_at_ref`)等多處。
- **兄弟閘的落差:** 回頭重讀的設定讀取 `_note_reread_config` 的 docstring 說鍵名與值域「同」`_note_audit_config`。同一份 `.lumos/config.json`,兄弟閘還是只接 `(ValueError, UnicodeDecodeError)`。
  - 位置:`_note_audit_config` 在 `scripts/lumos:33342`,`_drift_config_text_parts` 在 `scripts/lumos:39137`。
  - 實測:對 13 萬層陣列,兩支都丟 `RecursionError`,`_note_reread_config` 與 `_note_shape_config` 則回預設。
  - 推送前這幾道閘讀同一份設定,所以只有回頭重讀這道是穩的。
- 引句:「raise ValueError("巢狀太深") from None」
- 歸因:包裝本身是修補新增;兄弟閘讀設定沒接 `RecursionError` 是有證據的原有漏查,兩版同樣如此,也不是這份修補改壞的。

## A3 新的提交指令產生器直接用 shlex,沒用專案現成的「印給人貼的指令」引號函式
severity: minor
blocking: 否

- **修補寫法:** `_note_reread_add_cmd` 自己 `import shlex` 再逐檔 `shlex.quote`。
- **既有對照:** `_sh_quote`(`scripts/lumos:446`)的 docstring 就是「印給人照貼的指令裡的一個參數加 shell 引號」。`_drift_sh`(`scripts/lumos:38239`)也是建在它上面。
- **行為:** 檔名受 `_NOTE_REREAD_VERDICT_NAME_RE` 限制,兩者輸出相同,所以只是同一件事多一條路。同區的 `_note_reread_cmdline`(`scripts/lumos:35040`)本來也是直接 shlex,所以這是沿用該區既有的第二種寫法。
- 引句:「" ".join(shlex.quote(f"{_NOTE_REREAD_VERDICT_DIR}/{n}") for n in sorted(names))」
- 歸因:有證據的原有漏查(同區 `_note_reread_cmdline` 在兩版都直接用 shlex);`_note_reread_add_cmd` 是修補新增的,延續同一個寫法。

## A4 測試用整個換掉 `sys.modules["json"]` 來造遞迴爆掉,沒有先例
severity: minor
blocking: 否

- **修補寫法:** `t_reread_wt_records_guarded` 的 ③ 組把 `sys.modules["json"]` 換成一個 `loads` 一律丟 `RecursionError` 的替身,靠被測函式內部的 `import json as _j` 才生效。
- **既有對照:** 同檔造這種情況的慣例是真的造超深巢狀輸入(`scripts/test_lumos.py:37769`、`41410`、`41427`),或是換掉被測模組的屬性,例如前面看到的 `m._ns_slots_violations = _boom`。整檔找不到換 `sys.modules` 的先例。
- **補充:** 同一支測試已有用 13 萬層真實輸入的 `deep` 組,替身只多了「不看機器」的保險。它綁死函式內部 import 的寫法,以後 `_note_reread_json` 若改成模組層級 `json`,替身會悄悄失效,③ 組變成空殼。
- 引句:「sys.modules["json"] = _Deep()」
- 歸因:修補新增。

## 沒找到問題、核對過的範圍

- **`_gate_event_fit` 改成多鍵,其他呼叫端沒變:**
  - 只有兩個其他呼叫端,都傳單一字串鍵:筆記形狀擋放寬帳 `scripts/lumos:33224`(`"pairs"`),舊句檢查 `_drift_m1_fit` 在 `scripts/lumos:40186`(`"rows"`)。
  - 我把 88322e46 與 59f8f92b 兩版的 `_gate_event_fit` 載進同一程序,對兩種鍵、0 到 80 筆、各種長度、帶不帶 `nodes_cap=20` 隨機跑 300 組,輸出完全相同。
  - `keys[0]` 寫的旗標在單鍵時等於原本的 `list_key + "_truncated"`。
  - `_gate_event_fit_drop` 與原本的「有清單且超過才二分」邏輯一致。
- **帳的白名單沒動:**
  - `_GOV_LOCAL_PAIRS`(`scripts/lumos:1366` 起)的 `("note-reread", reminded/covered/none)` 沒變,`skipped`、`blocked` 照舊進版控帳。
  - 我沒找到讀 note-reread 事件 `note` 字串的消費端(`來源 ci;`、「路徑=指紋」清單都沒人解析),所以清單改放 `layer1_fps` 不會破壞既有讀者。
  - 帳的 `head_sha` 一律記被推頂端、判不了的 skipped 也帶 `state`,跟 `_drift_m1_ledger`(`scripts/lumos:40221`)的寫法一致。
- **`_note_reread_uncommitted` 回傳型態從 set 改成 dict:** 全部呼叫端(`_note_reread_prepare_todo`、`_note_reread_wip_left`、`_note_reread_print_layer1`)都已同步,沒有殘留的集合運算。
- **測試隔離併進 `_isolate_environment`:** 與同函式內 `pop("CODEX_HOME")`、`pop("CLAUDE_CONFIG_DIR")` 的寫法同一類,位置在設 `LUMOS_SKIP_CLAUDE_PLUGIN` 之前,對齊既有慣例。我沒逐支檢查其他測試是否倚賴從外面繼承任何 `LUMOS_SKIP_*`,依據是修補自己的聲明,沒獨立驗證。
- **沒核對的範圍:** 沒讀 `r3-repair-docs.patch`,沒跑任何測試(尤其沒跑 `t_reread_wt_records_guarded` 與新的 ledger 掃描測試),沒驗 `scripts/hooks/pre-push` 對新 `--gate` 的接線。

## 固定席節點逐條

- `Systems/reversibility-governance-ledger`(帶 RISK):這份 diff 動了帳的寫入長度控制和欄位(新增 `layer1_fps`,`note` 不再帶清單),沒動帳檔路徑、本機帳白名單或 gov 彙整的來源。不影響。
- `Systems/guard-kill` 兩條合約(rc 優先序、`--json` 恰一行):diff 沒碰 guard kill。不影響。
- `Systems/lumos-cli-read` 的 search 排除 superseded:沒碰 search。不影響。
- `Systems/lumos-cli-lifecycle` 的 re-inject 不動 sentinel 外內容:沒碰 re-inject。不影響。
- `Issues/code-loop守衛main-direct盲區`、`Systems/存量漂移守衛`、`Systems/筆記內容閘`:diff 沒改 `scripts/hooks/pre-push`。`drift ack --kind reread` 的讀取改走新共用函式,行為差異就是 A1 那一條。
- 其他「超出上限只列名」的節點:我沒讀內容,不能表態。

最高等級:major
