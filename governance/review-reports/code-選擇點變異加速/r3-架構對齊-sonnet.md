severity: clean

我在 `/tmp/lumos-seat-work/code-選擇點變異加速/架構對齊-sonnet/` 沒有建任何 worktree,也沒有檔案要清。派工詞裡的鎖檔 `…baf3be87….json.warming` 在這台機器上不存在,所以沒有鎖要處理。

## 已驗主張

引句:「m._kill_run = lambda cmd, run_dir, cap, **_kw: (0, "", 2.0, False)」

引句:「mg.remaining = lambda rem=rem: rem」

引句:「m._CHOICE_MERGE_UNIT_SECS = 0.5」

引句:「PITFALL:第一個訊號落在看完停止旗標之後、合併程序登記之前,回呼收不到、合併呼叫跑完整段」

## 三問

**1. 分層與依賴方向:對齊。**
- 這份修補只動三類檔:計劃筆記、`Systems/guard-kill.md` 的摘要行、`scripts/test_lumos.py` 與簽章基準檔。沒有正式程式碼改動,所以沒有跨層直呼。
- 新測試 `t_choice_kill_merge_budget_edge` 直接呼叫 `m._kill_merge_singles`。鄰居 `t_choice_kill_merge_edges` 同樣直接呼叫 `m._kill_merge_ready`、`m._choice_merge_classify` 這類內部函式。
- 新測試的做法跟鄰居一樣:
  - 先 `import types`,再用 `types.SimpleNamespace` 造最小物件。`scripts/test_lumos.py:147352` 附近有同樣寫法。
  - 剩餘時限用 `mg.remaining = lambda rem=rem: rem` 固定。`scripts/test_lumos.py:147352` 是同一個寫法,連 `for rem, ok in ((…),(…))` 的卡線迴圈形狀也相同。

**2. 命名與錯誤處理:對齊。**
- 新測試取名 `t_choice_kill_merge_*`,docstring 以 `[代碼審 code-選擇點變異加速 r2 …]` 開頭並附「翻紅釘」,跟同族測試一致。
- 斷言一律走 `check("r2 邊界 #1 …", cond, detail)`,跟既有 `r1 邊界 #4` 等同格式。
- 清理用 try/finally。

**3. 第二種做法:沒有。**
- **換掉模組函式:**
  - `orig = m._kill_run` 搭配 finally 還原,這是本檔通篇的做法。
  - 同型的 `orig = m._…` 有數十處,例如 `scripts/test_lumos.py:10047`、`:28734`、`:30495`。
  - 沒有引入 `mock.patch` 之類另一套做法。
- **換掉模組屬性:**
  - 端到端新增段落用 `saved = m._CHOICE_MERGE_UNIT_SECS`,設值後在 finally 還原。
  - 同一組測試 `t_choice_kill_merge_budget_reestimate` 已有同款寫法(`scripts/test_lumos.py:147170`、`:147196`)。
- **假 Gradle 與時限:**
  - 假 Gradle 沿用既有的 `_ckm_repo(2, {"__msleep__": {"1": 6}})`。這個 `__msleep__` 行為鍵在加速前的 r1 測試(`scripts/test_lumos.py:147284`)就有了,不是新發明。
  - 端到端呼叫沿用 `_ckm_inproc` 加 `_ckm_time.monotonic() + 3`。
  - 邊界測試直接換掉 `_kill_run`、不真睡,跟 `t_choice_kill_merge_edges` 的做法一致。
- **筆記摘要行:**
  - 一條 PITFALL 拆成三條,每條都有 `[出處:][根因:][修法:][test:]`。
  - 同一行掛多個 `[test:x][test:y]` 在其他計劃裡本來就有,例如 `探針隔離與清理收斂_計劃.md` 就有 7 處。
  - 計劃 S4、S6、S7、S9、S19、S20 的多測試綁法與此相同。
  - 簽章檔的 `note` 欄沿用既有格式。

不對齊共 0 條,其中 major 0 條。

## 未驗範圍

我只比對寫法,沒有跑測試,也沒有跑兩版重現。依派工詞的鏡頭分工,正確性與行為證據由其他席負責,這裡不附兩版查證的行為結果。

總結:最高嚴重度 clean
