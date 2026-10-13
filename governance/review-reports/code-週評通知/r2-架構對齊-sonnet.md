severity: minor

整體上這份 diff 跟專案既有寫法對得齊。python 端沒有引入第二種做法,測試手法也沿用既有的,只有一處通知決策的分工跟 `run_replay` 不同。

## 1. run_probe 的通知決策分工跟 run_replay 的新慣例不同
severity: minor
blocking: 否
引句:「case "$verdict" in 週評通知:是*) notify=1 ;; esac」
file: `governance/autonomous-loop.sh:432-456`(`run_replay`,另見 `governance/autonomous-loop.sh:436` 的註解)
1. 既有寫法:`run_replay` 的註解寫明「LINE 文字在 python 端組好單行、shell 只抽前綴,後續新週期任務照此」。python 印 `MSG:` 行,有這行才通知,shell 用 `sed -n 's/^MSG://p'` 抽出來,訊息整句直接送。`run_exam` 和 `run_nags` 則是在 bash 裡自己組訊息。
2. 這份 diff:python 印 `週評通知:是|否 — 原因`。shell 用 `case` 比對前綴後面的「是」字來決定 `notify`,訊息仍在 bash 組,`MSG="情境探針本週要看:$line${verdict:+;$verdict}(…)"`。diff 註解自稱「同 run_replay 的慣例」。
3. 差在哪:「要不要通知」這個決定是靠比對「是」字,不是「有沒有 `MSG:` 行」。訊息主體也沒有進單元測試網,等於是 `run_replay` 那種做法加 `run_exam` 那種做法的混合。
4. 為什麼只列 minor:`run_probe` 本來就是 bash 組訊息(`run_exam`、`run_nags` 同款),判定句本身是 python 組好整句、shell 沒有拆字串,而且有測試 `t_autoloop_probe_alert_follows_verdict` 蓋住。所以不算第二種做法,也沒有跨層直呼。
歸因:未判定。查證:`grep -n 'MSG:' governance/autonomous-loop.sh` 只有 `run_replay` 用 `MSG:` 前綴協定。

## 其餘對照,沒有不對齊
- **借 lumos 單源函式**:`_load_lumos()` 把原本 `_codex_home_dir` 內聯的 importlib 載入抽出來,`_codex_home_dir` 改用它。`_wilson` 借 `scripts/lumos` 的 `_wilson_interval`(`scripts/lumos:11679`),沒有另寫一份。載不進時用 try/except 退回,跟 `_codex_home_dir` 的做法一致。
- **判分/總結/歷史**:`summarize_results` 加 `ids` 欄位,`history_record` 用 `if "ids" in summary` 守衛。這跟同一函式裡 `env_fps` 的選填欄位寫法一致。
- **歷史讀檔**:`weekly_alert_line` 逐行 `json.loads`,壞行 `except ValueError: continue`,跟 `scripts/scenario_probe.py` 其他讀 jsonl 的寫法一致。
- **fail-open**:`weekly_alert_line` 回 `None` 時 shell 退回 p≠n,這是 `run_probe` 一貫的「有 `|| true` 才不影響 loop」風格。
- **測試**:`t_autoloop_probe_alert_follows_verdict` 用正則把 `run_probe` 從腳本抽出來,配假探針和假 LINE 模組在沙盒跑。既有測試 `scripts/test_lumos.py:45086` 附近已有抽 `run_exam`、`run_probe`、`run_nags`、`run_replay` 的先例。`t_weekly_alert_*` 和 `t_probe_history_records_ids` 的命名與寫法對齊 `t_probe_history_records_env_fps`。

## 修補鏡頭三問
① 修補要解的「判定行講的是上一週」問題,現在由 `weekly_alert_line` 擋住:最後一列要是預設週抽,而且 `rows[-1].get("seed") != seed` 時回 `None`。`t_weekly_alert_fallback_when_thin_history` 裡有缺欄位列的測試。這是看 diff 和測試名得到的,我沒有實際跑這些測試。

② 正常路徑、錯誤路徑和相鄰路徑(非週抽 seed、讀檔失敗、計算出例外)都回 `None`,shell 走 `elif` 退回 p≠n。這個分支結構我讀過,沒有看到走不到的路徑。

③ 本席沒有新發現需要比對修前修後,只有上面那條 minor。

總結:最高等級 minor
