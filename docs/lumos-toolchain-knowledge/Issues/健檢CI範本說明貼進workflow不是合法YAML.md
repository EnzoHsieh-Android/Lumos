---
type: issue
status: open
created: 2026-09-30
updated: 2026-09-30
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-09-30 推送閘接漂移檢查代碼審 r2 外家否決席 F1]健檢(doctor)給消費專案貼的 CI 步驟提示裡,筆記形狀擋與筆記內容審那兩處把說明文字(含共用的 Python 3.14 那句 _CI_PY314_NOTE)直接接在步驟後面、不是 YAML 註解,照整段貼進 workflow 的 steps 底下會解析失敗;存量漂移檢查那處已改成縮排對齊步驟的 # 註解,這兩處還沒改。重現:把筆記內容審那處的步驟字串接在一份 workflow 的 steps: 後面,用 ruby -ryaml 的 YAML.safe_load 解析,報 could not find expected ':';判法可沿用 t_doctor_drift_ci_template_start_fallback 的 _dr_yaml_tail_ok
related:
  - "[[Systems/存量漂移守衛]]"
---
# 健檢CI範本說明貼進workflow不是合法YAML

## 現象

`lumos doctor` 在專案 CI 沒呼叫某道閘時,會印一段「CI 貼這一步」的提示。筆記形狀擋(note-shape)與筆記內容審(note-audit)這兩處的提示,是「步驟本身 + 兩格縮排的括號說明 + 共用的 Python 3.14 說明」接在一起。說明那幾行不是 YAML 註解,縮排又比步驟淺,人照整段貼進 workflow 的 `steps:` 底下,GitHub Actions 讀不了那份 workflow。

存量漂移檢查那處在推送閘接漂移檢查代碼審第二輪(外家否決席 F1)已改:說明與 Python 3.14 那句都寫成縮排對齊步驟、以 `#` 開頭的註解,不接共用的 `_CI_PY314_NOTE`。這兩處不在那次的範圍。

## 要做的

- 這兩處的說明改成跟漂移那處同一種寫法(縮排對齊步驟的 `#` 註解);共用的 `_CI_PY314_NOTE` 換成註解形式或拆掉,`t_ci_runs_python314_and_old_syntax_check` ③ 的計數跟著改。
- 補一條測試:拿 doctor 印出的提示字串,斷言步驟之後每一行都是空行或縮排後的 `#` 註解(標準庫沒有 YAML 解析器),並先證明舊寫法會讓斷言紅。

REVISIT:2026-10-31 還沒改就攤給 Enzo 排
