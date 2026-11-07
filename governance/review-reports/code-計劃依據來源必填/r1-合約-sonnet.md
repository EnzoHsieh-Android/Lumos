severity: major

審查摘要:`-k doctor`(597 案)在複本全綠,`warn_soft` 加 cap 沒影響其他呼叫端。作者自稱 37 道改壞全翻紅,我抽 13 道改壞,8 道仍綠(M1–M8 是我自己的實驗編號)。實驗複本與暫存都已用字面絕對路徑刪除。

F1
severity: major
blocking: 是
引句:「    if bad is None:   # 測試跑不了、輕量審也沒擋:那一圈放行;〈依據來源〉照擋」
計劃〈待決問題〉那張表有一列寫明:預期值表那圈因測試索引讀不動而放行時,〈依據來源〉照擋。讀不成文字也擋。這兩個分支沒有任何測試守著。
- 實驗 M3:把那兩行 `bad, oks = [], []` 改成 `return 0`(等於退回改動前的行為),`python3.14 scripts/test_lumos.py -k spec_gate_push_sources` 仍 rc=0 全綠。
- 實驗 M4:把 `bad.append(f"{_SOURCES_PUSH_TAG}{prel}:計劃讀不成文字` 改成不 append,同一指令仍全綠。
- 失敗場景:風險低且有留痕的計劃被改到,同時平台設定檔讀不動(`file:scripts/lumos:16750` 的 `except (ValueError, OSError)` 讓 `idx = False`,`_spec_gate_push_scan` 回 `(None, [])`)。這時缺〈依據來源〉的新計劃會被放行,而計劃明寫要擋。
- `t_spec_gate_push_sources` 也沒有這兩條的斷言。

F2
severity: minor
blocking: 否
引句:「        r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "log", "--reverse", "-M", "--diff-filter=AR",」
健檢的批次首次加入日跟單篇的 `_plan_first_day` 不一致,而計劃與 Systems/規格閘都說「同一個結果」。
- 批次用 `-- <vault>/Projects` 限路徑,從 Projects 外搬進來的檔(例如從 `Inbox/`)在限路徑後只剩一個 A,舊路徑日期接不上。
- 單篇的 `diff-tree -M` 不限路徑,看得到 R,會接上舊日期。
- 實驗:`Inbox/移_計劃.md` 在 2026-01-01 進 git、沒有 created,2026-08-01 `git mv` 進 `Projects/`,生效日設 2026-06-01。
  - `_plan_effective_day` 回 2026-01-01,規格閘的 `_plan_sources_is_new` 回 False,即判舊。
  - `_doctor_plan_sources_lines` 卻列出它,即判新。
- 影響只限健檢提醒(不擋、不計問題數),所以標 minor。

F3
severity: minor
blocking: 否
引句:「            first.setdefault(parts[2], first.get(parts[1], day))」
改名要把舊日期接給新路徑,這件事沒有被任何測試驗到。
- 實驗 M8:把這行改成 `pass`,`-k doctor_plan_sources` 仍綠。
- 原因:`t_doctor_plan_sources_batch_dates` 的改名計劃 `created` 與首次提交日同為 2026-01-01,靠 `created` 就判舊。
- 要驗到這件事,需要 created 早於生效日、首次提交日晚於生效日但仍早於改名日的檔。

F4
severity: minor
blocking: 否
引句:「        if any(not x.startswith(_SOURCES_PUSH_TAG) for x in bad):」
計劃寫「只有〈依據來源〉時最後一行改印〈依據來源〉的補法與範例,不印『把條款的測試做綠』」,測試沒有斷言這一點。
- 實驗 M1:把這行條件改成 `if True:`,`-k spec_gate_push_sources` 仍綠。
- 實驗 M2:把依據來源補法那行改成 `if False:`,同一指令仍綠。
- `t_spec_gate_push_sources` 只檢查標題,沒檢查最後兩行。

F5
severity: minor
blocking: 否
引句:「    echo "推送前規格閘擋下,原因見上面列的每一條。" >&2」
`Systems/bound-tests-gate` 的 WHY 把掛鉤通用文案綁到 `[test:t_spec_gate_push_sources]`,但該測試不跑掛鉤文案。
- 實驗 M13:把文案換回舊句「風險低計劃的條款測試沒全綠」,`-k spec_gate_push_sources` 仍綠。
- 筆記宣稱有測試守,實際沒有;這正是本案要修的誤導文案會悄悄回退的地方。

F6
severity: minor
blocking: 否
引句:「    if len(rows) < 2 or not (len(rows[1][1]) == 3 and all(_EXPECTED_SEP_RE.fullmatch(c) for c in rows[1][1])):」
分隔列檢查、同一節出現兩次的檢查,都沒有斷言。
- 實驗 M5(分隔列檢查改成 `if False:`)與 M6(重複節檢查改成 `if False:`),`-k spec_gate_sources_section` 都仍綠。
- 漏掉分隔列時,第一列資料會被 `rows[2:]` 靜默吞掉。
- 低嚴重度只因為目前沒看到實際壞掉的場景。

已確認有翻紅的實驗:
- M9:doctor 的 `max(days)` 改 `min(days)`。
- M10:推送前不判新舊。
- M11:規格閘不寫 `cells`。
- M12:推送前不寫 `stage`。

總結:最嚴重是推送前那圈在平台設定讀不動或計劃讀不成文字時照擋〈依據來源〉的決定沒有測試守著(F1),會擋 1 條(另 5 條 minor 不擋)。
