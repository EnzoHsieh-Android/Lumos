severity: minor

審查範圍:凍結 patch 的 `scripts/lumos` 與 `scripts/test_lumos.py`。結論是結構跟鄰居一致,沒有第二種做法、沒有跨層直呼,只有 4 條命名、寫法上的小偏差。

## 1. 分層與依賴方向:對齊

- 新欄位的登記跟第一、二段同一條路。
  - `_GOV_FIELD_TYPES` 同樣用 `dict.fromkeys(..., (dict,))` 加一行註解,跟 `merge_kind`、`merge_unclean`、`merge_off` 那行同形。
  - 對照:`scripts/lumos:18462` 一帶。
- 事件欄位只經 `_choice_event_extra`(`scripts/lumos:78816`)寫,由 `_ChoiceKillRun` 的逐壞法那筆帳呼叫,跟 `merge_kind`、`single_runs` 同路。
- run 那筆的 `merge_trips`、`merge_reopen` 加在 `_choice_kill_report` 的既有 `rx.update(...)`,同樣用 `getattr(mg, ..., None) or {}`,跟 `merge_unclean`、`merge_off` 同形。
- 新狀態(`cool`、`trips`、`reopen`、`whys`)放在 `_KillMerge`,docstring 也補了「第三段計劃加」。
- 半開邏輯放在 `_kill_merge_iter`(迴圈)與 `_kill_merge_breaker`(結果交斷路器),沒有跨進 `cmd_guard_kill`。

## 2. 命名與錯誤處理:大致對齊,有 3 條小偏差

**對齊的部分**
- 標準錯誤印字:新增的「恢復合併」一行用 `print(f"⚠ {_kill_esc(plat)}:…", file=sys.stderr)`,跟 `scripts/lumos:28947` 與 `scripts/lumos:29138` 同形。
- 帳欄缺欄讀法:`gov` 的 `ck` 投影缺欄一律讀成 `or {}`,跟 `merge_kind`、`merge_unclean` 同形。
- 測試:新測試用既有的 `_ckm_repo`、`_ckm_run_many`、`_ckm_phase`、`_ck_gov`,翻紅釘與判準來源的 docstring 句式也跟 `t_choice_kill_merge_event_fields`(`scripts/test_lumos.py:147831`)一致。

**不對齊 1:`merge_why` 寫入條件跟鄰居不同**

patch 裡 `_choice_event_extra` 對 `merge_why` 用 `if merge_why:`(真值判斷),而且逐值截斷。鄰居用 `if merge_kind is not None:` 加 `dict(...)`(`scripts/lumos:78823`),也沒有截斷。

引句:「    if merge_why:   # {平台: 快篩沒跑乾淨的原因},只列沒跑乾淨的平台,沒有就不帶(第三段計劃做法 4)」

`_choice_event_extra` 的 docstring 也只講了 `merge_kind`、`single_runs`,沒補 `merge_why`。這是缺欄與空值的語意差異,結構是對的。

severity: minor
blocking: 否

**不對齊 2:斷路器的「冷卻計數」擁有者拆在兩個函式**

鄰居的 `streak` 只在 `_kill_merge_breaker` 裡加、歸零、判門檻。新的 `cool` 在 `_kill_merge_iter` 累加與歸零(`mg.cool[c.plat] = 0`),在 `_kill_merge_breaker` 跳開時又歸零。同一個計數器分散在兩處改。另外 `tripped`(布林)與 `trips`(次數)並存,patch 註解自己寫「tripped 留給既有讀者」,等於同一件事兩套記法。`reopen` 是動詞單數卻存次數,跟 `trips`、`unclean`、`kinds` 這類名詞複數不同形。

引句:「            mg.cool[c.plat] = 0」

severity: minor
blocking: 否

**不對齊 3:恢復提示用 ⚠ 前綴**

`⚠` 在鄰居全是「降級、不合併」的警示。新增的是「恢復」的好消息,卻也用 `⚠`。前綴沿用了,但語意跟鄰居不同。判不準這算不算不一致,標 ⚠。

引句:「            print(f"⚠ {_kill_esc(plat)}:試探快篩跑乾淨了,恢復合併", file=sys.stderr)」

severity: minor
blocking: 否

## 3. 第二種做法:沒有引入,只有 1 條小重複

**不對齊 4:`_ckm_gov_ck` 是第四份「攔 `_render_gov_choice` 讀 gov 的 `ck` 投影」**

既有做法是在測試裡 inline 寫:換掉 `m._render_gov_choice`、`chdir`、`redirect`、跑 `m.cmd_gov(..., stats=True)`、還原。這段已經 inline 出現三次:`scripts/test_lumos.py:146968`、`scripts/test_lumos.py:147891` 與同一帶。新的 `_ckm_gov_ck` 做的是同一件事,只是包成 helper,沒有回頭換掉前三份。做法本身沒變,不算另一套計數,但同一段寫法現在有 helper 與 inline 兩種形狀,而且新 helper 只有一個測試在用。

引句:「    m._render_gov_choice = lambda rows: seen.extend(rows)」

severity: minor
blocking: 否

計數方面沒有另開一套。`merge_trips`、`merge_reopen` 沿用「以平台為鍵的字典」,跟 `merge_unclean` 同形。

不對齊共 4 條,其中 major 0 條
