severity: minor

審查範圍:整份 `/tmp/code3-r3.patch`,加上在 repo(提交 1685194c)上實跑的探針。我另在臨時 clone 做了一個拿掉判斷的翻紅實驗,沒有改 repo 任何檔。blocking 級的問題沒找到。`slots_doctor_reminders` 子集 36 筆全過。`-k slots_retire` 和 `-k note_shape` 我只啟動了,交報告時還在背景跑,沒有結果。

**逐項走過的結論(沒有問題的部分)**
- `_note_summary_entries` 實跑結果如下:
  - 同行寫法、雙引號、單引號、`summary:\t`、`summary:RULE:`、值含冒號,行號都對(從 fm_lines 第一行起算是第 2 行)。
  - `>`、`>-`、`|+` 區塊走重組路徑,行號是各自的實體行。
  - 空字串和帶縮排的 `summary:` 不產生條目。
- `_ns_summary_logical` 改成收片段再 join:`" ".join([s, s2, …])` 與舊的逐次 `+= " " + s` 逐字相同。`cont` 的記法和回傳 dict 的插入順序沒變,提交時的「舊行」判定不會因此多擋。
- `_lint_new_config` 舊呼叫端不帶新參數,走原路徑(`p.is_file()` 加 `read_text`)。只有 `from_snapshot=True` 才改走位元組,而且對 BOM 比舊路徑寬鬆。
- `_drift_jsonl_parse` 的其他呼叫端(約 7900、12124、31289、31513 行)都收 list,現在由 `list(...)` 包住,沒有依賴問題。帳增速段和度量段的迴圈內部本來就逐筆處理。
- 推送那支:印出拋例外時,帳照記、rc 不變。記帳拋例外也各自兜住。

---

**R3C1** 測試沒咬住:S16 的 `_esc_clean` 拿掉測試仍全綠
引句:「lines.append(_esc_clean(f"{rel}:{why}:{(slot_parse(t[5:])['core'] or t[5:])[:40]}", _DOCTOR_LINE_MAX))」
severity: minor
blocking: 否 — 只是防回歸缺口,行為本身是對的。
1. 重現:在臨時 clone 把這行改回不包 `_esc_clean` 的 `lines.append(f"…")`,跑 `python3.14 scripts/test_lumos.py -k slots_doctor_reminders`,結果 `36 passed, 0 failed`。
2. 原因:`t_slots_doctor_reminders_r2` 的 ① 用的是乾淨文字,② 只測 S17 和 S18,沒有任何一項給 S16 塞控制字元。
3. 建議:加一條 `RULE:丙\x1b]0;x\x07 …` 逾期的 S16 輸入,斷言輸出不含 `\x1b` 和 `\x07`。

**R3C2** S18 的 fail-open 訊息改印例外全文,沒有清控制字元
引句:「ok(f"度量式撤除條件觀測跳過(fail-open:{_e18})")」
severity: minor
blocking: 否 — 要例外訊息帶出筆記或路徑內容才會觸發,沒有現成路徑。
1. 這個 except 現在把 `str(e)` 直接印出,舊版只印型別名。
2. 同一個 doctor 其他提醒行都過 `_esc_clean`,這一句沒有。
3. 另外 `warn_soft` 在新的 try 裡,若它印到一半拋例外,會同時看到半截警告和 `ok(...)`。
4. 建議:改印 `type(_e18).__name__`,或包 `_esc_clean`。

**R3C3** ⚠ 引號跨行的 summary 與純量接續行仍然漏判(非回歸)
引句:「if not out and isinstance(sm, str) and "\n" not in sm.strip():」
severity: minor
blocking: 否 — 舊版同樣漏,這次只是 docstring 暗示有涵蓋。
1. 實測 `summary: "RULE:a` 換行 `  more [retire:z]"` 時,解析值是 `'"RULE:a'`,條目 `{}`,S16 到 S19 全不判。
2. 實測 `summary: RULE:a` 換行 `  WHY:b` 時,`out` 非空所以不走補單行路徑,只得到 `{4: 'WHY:b'}`,第 3 行的 RULE 不見。
3. 都是罕見寫法。若不處理,請在 `_note_summary_entries` 的 docstring 寫明「跨行引號與純量接續不支援」。

**R3C4** ⚠ 筆記裡的函式清單沒跟上
引句:「治理帳檔尾只讀一遍,跟帳增速那段共用 _gov_tail_bytes 與 _drift_jsonl_parse」
severity: minor
blocking: 否 — 只是文字落後。
1. 這兩段現在讀的是 `_drift_jsonl_iter`。
2. 筆記 `Systems/lumos-cli-read.md` 還寫 `_drift_jsonl_parse`。
3. 程式註解「逐行解析走帳檔共用的 _drift_jsonl_parse(只在 \n 切行…」(約 2055 行)也是同樣的問題。
4. 另外 `_drift_jsonl_iter` 的 docstring 寫「不留整份清單」,但 `decode` 加 `split("\n")` 仍然整份展開成字串清單,省的只有 dict 清單。

---

**圖譜鏡頭**:這次 hook 附的是 `LUMOS-IMPACT: 384f4574..1685194c`,我沒看到固定席的逐條節點清單。以下按這份 diff 實際動到的節點判斷。
- `Systems/lumos-cli-read`:不影響其宣稱的行為。S16 到 S19 共用條目讀法、不計入問題數、`--ci` 不跑 S17 與 S18、S19 照跑,在程式裡都成立。只有 R3C4 的文字落後。
- `Systems/存量漂移守衛`:不影響。「先印後記、印出與記帳各自兜、不改 rc、兜底條數記 null」與程式一致。
- `Issues/撤除條件檢查末輪遺留四項` 與 `Projects/筆記格子寫法與過期檢查_計劃`:不影響。「先印後記」的說法與程式一致;計劃把 [S13] 綁上 `t_slots_doctor_reminders_r2`,測試名存在。

**本案測試鏡頭**:`t_slots_doctor_reminders_r2` 各項是否咬住:
- ① 單行 summary(S16 與 S19):咬住,拿掉補單行路徑會紅。
- ② S17 與 S18 清控制字元:咬住。
- ② 的 S16 項目沒有,見 R3C1。
- ③ 別名查決策:咬住,但這是舊邏輯,不屬於這份 diff。
- ④ S18 fail-open:咬住,測試把 `_doctor_metric_lines` 換成會拋例外的版本,並斷言輸出到 S19。
- ⑤ 檢查的是 `_doctor_cfg_bytes`,這份 diff 沒改它,屬於舊行為。
- ⑥ lint-new 用已讀好的設定:兩項都咬住。

最高嚴重度 minor,blocking 0 條
