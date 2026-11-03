severity: major

我讀的是 r1-code.patch,再對照 `/Users/enzo/harness/lumos-redbase-realrun` 的 HEAD(bcd9a1703,已含這批改動)。以下行號都是這個版本的 `scripts/lumos`。

## 問 1:分層與依賴方向

**對齊的部分**
- 規格閘叫比對工具內部,先例本來就有:`_redbase_parse_file` 叫 `_tg_has_long_line`、`_tg_functions`(14338、14340),`_redbase_prev_doc` 叫 `_tg_rb_doc`(14479)。新的 `_redbase_attach` 叫 `_tg_ledger_ignored`(14512)跟這些一致。
- 推送前補平台走 `_spec_gate_push_fill`(15603)。它走 `_spec_gate_items` 和 `resolve_test_refs`,吃 `_spec_gate_push_stale` 已經讀好的計劃文字與條款綁定。沒有另掃正文,沒有繞過條款解析。

**不對齊**
- doctor 直接叫比對工具的內部函式。`run_doctor`(1997 起)原本沒有任何 `_tg_` 呼叫,只叫 `_vault_repo_root` 和 `_spec_gate_latest_*`。
- 鄰居 `_local_ledger_doctor_msgs`(1752)同樣在問「帳檔有沒有被 git 忽略」。它放在帳檔區,直接用 `_lens_git`。
- 新的 `_tg_ledger_ignored`(49866)放在比對工具區、掛 `_tg_` 前綴,doctor 卻跨過去叫它。它的 docstring 自己寫「比對工具、規格閘、doctor 共用這一支」,既然三層共用,位置與前綴就該在共用層。

severity: major
引句:「_st, _rule = _tg_ledger_ignored(_rr, rel=_gl) if _gl else ("unknown", "")」
file: `scripts/lumos:2923`(定義在 `scripts/lumos:49866`,鄰居見 `scripts/lumos:1752`)

## 問 2:命名與錯誤處理

**對齊的部分**
- `_tg_ledger_ignored` 的 git 失敗處理跟鄰居同一個樣子:用 `_lens_git_dl`(49471、49827 的同區用法),`-q` 的回傳碼只認 0 或 1,逾時、不在 repo、其他回傳碼都回 "unknown"。這跟 `_redbase_target_why`(14435)和 `_local_ledger_doctor_msgs`(1764)判 0/1 的寫法一致。
- 身分字沿用 `_tg_rb_bad` 的固定字寫法:`ident="pending"`、`"orphan"`,跟既有的 `ident="deleted"`(49892)同款。
- `_auto_escape` 的用法沒變,也用 `except Exception` 包住(fail-open)。
- 拿 `why` 字串當判斷依據,`_redbase_attach` 的 `x[1] == "判綠"` 已有先例。

**不對齊(都是 minor,結構是對的)**

severity: minor
引句:「except (ValueError, OSError) as _e:」
doctor 新段只接窄的例外。同一個函式裡的鄰居本機帳那段,以及其他 fail-open 段落,都是 `except Exception as _e:` 加 `ok(...跳過(fail-open:...))`。
file: `scripts/lumos:2933`(鄰居 `scripts/lumos:2921` 起的本機帳段落)

severity: minor
引句:「bad_plat.append(_esc_clean(str(getattr(e, "prefix", "") or t), 60))」
推送前接「前綴沒定義」時,接的是寬的 `ValueError`,再用 `getattr` 猜 `prefix`。鄰居都接專屬的 `_TestRefPrefixError`,直接用 `e.prefix`。
file: `scripts/lumos:16006`(鄰居 `scripts/lumos:69433`、`scripts/lumos:2428`)

severity: minor
引句:「print(f"[spec-gate] ⚠ 治理帳被 git 忽略,這筆留痕進不了提交」
這是整支 `[spec-gate]` 行首唯一帶 ⚠ 的一行,而且走 stdout。講同一類後果(留痕進不了帳、乾淨 clone 找不到)的鄰居不帶 ⚠,走 stderr。
file: `scripts/lumos:14514`(鄰居 `scripts/lumos:14238`、`scripts/lumos:14355`)

## 問 3:第二種做法

**不對齊**

severity: major
引句:「"env_missing_re": _AGP_DEVICE_MISSING_RE,」
「依輸出文字判這個測試 profile 的狀態」的正規式,鄰居都放在 `_RAN_EVIDENCE`(68525,以 profile 為鍵,有 `re`、`count_re`)。`_spec_gate_judge_items` 同一個迴圈裡先讀 `_ran_count(per_prof(plat), tail)`(查 `_RAN_EVIDENCE`),下一行再讀 `TEST_PROFILES` 的新欄位。
同類東西於是散在兩張表。`TEST_PROFILES` 原有欄位都是目錄、副檔名、方法名切法、提示字句,沒有一個是輸出比對。
diff 的註解說明了為什麼不放 `_RAN_EVIDENCE`:那張表的讀者會取 `spec["re"]`,只放一個欄位會崩。理由成立,但以後要加新的環境缺失樣式時,接手的人要猜放哪一張。
file: `scripts/lumos:6181`、`scripts/lumos:6196`、`scripts/lumos:14961`(對照 `scripts/lumos:68525`、`scripts/lumos:68573`)

severity: minor
引句:「return _rg_split_args_stripped(s, stripped)」
`_rg_split_args` 現在有兩套切法:原本的字元深度計數,以及新的 `_rg_bracket_map` 配對。後者沒有處理 `angle`,傳了 `angle=True` 也被靜默忽略。
`_rg_bracket_map` 的 docstring(48035)已經警告「配括號的規則兩支要一起改,有測試綁住」。新路徑不在那個等價測試的範圍內。
file: `scripts/lumos:48049`、`scripts/lumos:48073`

**⚠ 判不準,交編排者(不計入條數)**
- 規格閘留痕記平台的格式。
  - 新做法是 `tests` 一律寫「平台:名字」,讀的時候走 `_split_test_ref`。跟 `[test:平台:名字]`、處置帳的 `test:<平台>:<名>`(`_dispositions_split_test`,69420 起)是同一種格式。
  - 同一批紅燈版功能的鄰居 `_redbase_note_green`(14346)卻用 `tests`(給人看的名字)加 `items`(`[平台, 名字]` 成對,判定用)。
  - 兩邊本身就不一致,不硬判。
- `_tg_ledger_ignored` 是第三處問 `git check-ignore` 的程式。`_redbase_parse_file`(14325)和 `_redbase_target_why`(14435)是內嵌寫法,沒有共用函式,diff 也沒把它們改成用新函式。這是鄰居自己重複,不算 diff 引入第二種做法。
- 測試 fixture:`_mp_repo` 是從頭建的多平台規格閘 fixture。`_ig_repo` 和 `_ig_sg_repo` 分別建在 `_tqg_repo` 和 `_rb_sg_repo` 之上,沒問題。倉庫裡原本沒有多平台的規格閘 fixture,而 `_rb_sg_repo` 與 `_mk_spec_gate_repo` 本來就各抄一份底稿,所以不硬判。命名(`_mp_`、`_ig_`、`t_`、`[S1]` 標籤)跟鄰居一致。

不對齊共 6 條(2 條 major、4 條 minor)
