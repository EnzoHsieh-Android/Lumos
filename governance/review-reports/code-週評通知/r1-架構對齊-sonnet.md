severity: minor

整體對得上專案既有寫法,只有一處不對齊,而且不構成第二種做法。

**1. 通知原因文字在 bash 端拆字串組裝,沒有照 run_replay 的「python 組好、shell 抽前綴」做**
severity: minor
blocking: 否
引句:「case "$verdict" in 週評通知:是*) notify=1; why="${verdict#*— }" ;; esac」
file: `governance/autonomous-loop.sh:446-456`
file: `governance/autonomous-loop.sh:431-438`
1. 既有寫法:run_replay 的註解寫明「LINE 文字在 python 端組好單行、shell 只抽前綴」,是刻意立的新慣例。python 印 `MSG:`、`LOG:` 這類前綴行,shell 只用 `sed -n 's/^MSG://p'` 取整行,不拆解內容。
2. 這份 diff:python 端印整行「週評通知:是|否 — 原因」。shell 用 `case` 判斷「是」,再用 `${verdict#*— }` 靠全形破折號切出原因,最後在 bash 裡拼成 `MSG="情境探針本週要看:$line${why:+;原因:$why}(…)"`。
3. 差在哪:
   - 判定交給 python,這一點跟 run_replay 一致。
   - 訊息本文仍在 bash 組,而且 shell 與 python 在「— 」分隔符上有隱含耦合。
   - 最後這段 LINE 發送的 python 片段與 run_exam、run_nags、run_replay 的寫法相同,沒有第二套。
4. 不升 major 的理由:
   - run_probe 原本就是 bash 組訊息(舊的 `MSG="情境探針本週有題沒過:$line(…)"`),是這份 diff 沿用而不是新引入。
   - 往 run_replay 慣例靠的主要缺點是「訊息文字進不了單元測試網」,而 `t_autoloop_probe_alert_follows_verdict` 已用沙盒把 run_probe 抽出來覆蓋了訊息與原因,實質缺口很小。

**對齊的地方**
- `weekly_alert(rows)` 是純函式,回 dict 後由 `weekly_alert_line(history_path, seed)` 轉成單行字串。這跟 `summarize_results` / `history_record` 的純函式加包裝分層一致(`scripts/scenario_probe.py:1196`、`:1308`)。
- 模組層常數 `_WEEK_SEED_RE`、`_ALERT_MIN_WEEKS` 緊貼用到它們的函式,風格跟檔內其他 `_SCEN_*_RE` 常數相同(`scripts/scenario_probe.py:521-528`)。
- `_load_lumos()` 是把原 `_codex_home_dir` 內載入 `scripts/lumos` 的程式原樣抽出,沒有另寫第二套載入。
  - `_codex_home_dir` 與 `_wilson` 都呼叫它,借用的都是 lumos 的底線私有函式,跟既有借 `_codex_home()` 的做法一致。
  - 載入失敗的退路也一致:`_codex_home_dir` 印警告後退預設,`_wilson` 回 None 後退回「有題沒過就通知」。
- `_wilson_interval` 在 `scripts/lumos` 只有定義(`scripts/lumos:11679`)與逃逸帳統計的一個使用處(`:11838`)。這裡的呼叫方式 `w(k, n)` 吃 `(k, n)` 回 `(lo, hi)` 或 None,簽名與回傳都符合,沒有重寫。
- `history_record` 用 `if "ids" in summary:` 條件式追加欄位,跟同函式的 `env_fps`、`arm/runs` 追加方式一致。舊歷史列沒有 `ids` 時,`_repeated_failures` 用 `r.get("ids") or []` 容忍,所以舊列相容。
- 發 LINE 的 python 片段(`line_notify.send(build_report('scenario-probe', …))`、`LINE_TOKEN` 走 env)與 run_exam、run_nags、run_replay 完全同形(`governance/autonomous-loop.sh:407-412`、`:421-427`、`:463-467`)。
- 「|| true」搭配 grep 的防呆寫法(`verdict="$(grep … | tail -1 || true)"`)沿用同函式上方既有 `line=` 的做法。
- 退回舊規則的條件(探針沒印判定行才退回 p≠n)對應 run_replay 的 fail-open 精神,沒有引入新的失敗模式。
- 測試:
  - `_wk`、`_probe_res`、`_load_probe_module("sp_xxx")` 的用法與既有 `t_probe_*` 一致。
  - `t_probe_history_records_ids` 用 patch 假掉 `run_one` 並呼叫 `mod.main()`,沿用 `t_probe_run_one_records_env_fp` 一帶的 mock 風格。
  - 暫存目錄用 `gctl-weekly-` 前綴並在 finally 清掉。
  - `t_autoloop_probe_alert_follows_verdict` 抽出函式、在沙盒用假 LINE 模組跑,這正是共用說明指定的做法,沒有引入新的 shell 測法。

沒有發現跨層直呼或第二種做法(major 以上)。

總結:最高等級 minor
