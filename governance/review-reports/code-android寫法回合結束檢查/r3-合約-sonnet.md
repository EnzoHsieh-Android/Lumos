severity: major

先講結論:r2 合約席 F1–F9 逐條重做,現在都會翻紅,只有 F8 在 R6 又冒出一個小缺口。新找到 1 個 major(信任邊界守衛擋不住重複定義)和 3 個 minor。作者自稱的「55 處改壞 54 處翻紅」我抽查約 55 處改壞,不是在原作者那批上重做,翻紅的我都認,另外找到幾處沒紅。

**r2 F1–F9 重做結果**
- F1:拿掉 `_STATE["pending"]` 補跑後,`r2丁 空窗裡的 SIGTERM 當場補跑` 翻紅(耗時 22.1 秒),補上了。
- F2:拿掉 `filter.{d}.process=` 翻紅 3 條,補上了。
- F3:用別名、`getattr`、裸名 `"lumos"`、註解寫函式名、改成 PATH 掃描、改成從 `_hookshared` 匯入,都翻紅。但重複定義沒擋住,見 F1。
- F4:拿掉預留「另 N 條」那行,掃描翻紅(最長 1547 字)。
- F5:`_unchecked_kind` 三個分支(欄位缺、非物件、timeout)各改壞,都紅。
- F6:`t > 0` 改成 `>= 0` 翻紅。
- F7:`[:120]`、`.`/`..` 判斷、正規式放寬,都紅。
- F8:`imports_shared` 恆真,以及 `shared_ok`、`own_dir_ok` 各拿掉一個條件,共五處都紅。
- F9:`d1` 開頭欄位已改成「同一回合(prompt_id)」。

**F1 信任邊界守衛擋不住重複定義 `_trusted_lumos`**
引句:「_defs = [(n.lineno, n.end_lineno) for n in _ast.walk(_tree) if isinstance(n, _ast.FunctionDef) and n.name == "_trusted_lumos"]」
- 改壞:在 `scripts/hooks/claude/stop-lint-hook.py` 的 `def main(` 前面插入第二個 `def _trusted_lumos(): import shutil; return shutil.which("lumos")`。
- 指令:`python3.14 scripts/test_lumos.py -k hooks_never_run`
- 結果:`46 passed, 0 failed`。
- 原因:`_defs` 把所有同名函式都排除在檢查外。逐字比對只取 `re.search` 的第一個。Python 執行時用的是後定義的那個,等於 PATH 解析又回來,而且 `which("lumos")` 躲在函式裡不會被抓。
- 這是守衛擋不住原本要擋的東西。
severity: major
blocking: 是

**F2 起點時刻的 `math.isfinite` 沒有案例**
引句:「return t if math.isfinite(t) and t > 0 else None」
- 改壞:改成 `return t if t > 0 else None`。
- 指令:`-k r2_turn_start`
- 結果:`7 passed, 0 failed`。
- 原因:案例只有 `"nan"`(`nan > 0` 本來就是假),沒有 `1e999`。JSON 讀出 `inf` 後會變成 `--since inf`,整次回合查不到檔,靜默放行。紀錄檔要被手改才會走到。
severity: minor
blocking: 否

**F3 lint-new 預設 deliberate 那條沒有測試**
引句:「out["unchecked_kind"] = _LINT_WT_DELIBERATE   # 宣告的命令沒帶檔案佔位、或檔路徑都含分隔字元被拿掉:宣告形狀不讓跑,照設計判完了」
- 改壞:把 `_LINT_WT_DELIBERATE` 改成 `_LINT_WT_FAILED`。
- 指令:`-k lwt_`
- 結果:`118 passed, 0 failed`。
- 原因:`_lint_new_classify` 的兩個 not-checked 出口(沒佔位、`sep_emptied`)確實走得到這行,但沒有案例。改壞後這兩種專案每回合都被記成 error。
severity: minor
blocking: 否

**F4 匯入純度探針沒釘「只放共用模組這一支」**
引句:「"imp_only": (common + imp, False), "noimp_importlib": (common + via_importlib, True), "imp_read": (common + imp + rd, True)}」
- 改壞:`shared_ok = p == shared and imports_shared and by_import` 去掉 `p == shared`。
- 指令:`-k hook_pure`、`-k import_is_pure`
- 結果:`9 passed, 0 failed`、`4 passed, 0 failed`。
- 原因:同時匯入共用模組和別的兄弟模組的 hook,兄弟檔也會被放行。探針註解寫「只放這一支」,但沒有案例逼它。
severity: minor
blocking: 否

**補充(未標 finding)**
- 拿掉 SIGINT 的處理器,測試仍綠。作者說明有 `finally`/KeyboardInterrupt 兩層收法,我認同是等價的。但如果 SIGINT 被設成忽略(背景或 nohup),只有處理器會收,目前沒有案例釘住。
- 拿掉 `filter.<d>.clean=` 時,行為層的 clean 測試不翻紅,只有結構測試紅。工作樹模式的 status 實際上沒走到 clean 過濾器,所以守衛只靠結構測試,不算破口。
- 計劃與筆記:審計修正紀錄 r2 的五組敘述和五篇家節點新增的行,與程式行為對得上,沒找到相反的描述。

實驗用的複本已刪。

總結:最嚴重是信任邊界守衛擋不住重複定義 `_trusted_lumos`,會擋 1 條。
