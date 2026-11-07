severity: major

範圍:`r2-repair-丙.patch`,程式半參考甲、乙、丁。我在兩份 `git clone --shared` 複本裡改壞程式,設 PYTHONDONTWRITEBYTECODE=1,每次清 `__pycache__` 再跑。複本與暫存目錄已用字面絕對路徑刪除。

## r1 F1–F7 重做結果

| r1 條目 | 重做結果 |
|---|---|
| F1 可信來源守衛 | 改成 `which("lumos")` 加註解:2 條斷言翻紅。只剩註解、沒有呼叫:翻紅。從共用模組匯入:翻紅。換成別名呼叫:不紅,見 F3。 |
| F2 50 支上限 | 值改 5、49、52,以及 `>` 改 `>=`:全翻紅。 |
| F3 git 狀態 | 刪 `rebase-apply`、`REBASE_HEAD`、`CHERRY_PICK_HEAD`、`REVERT_HEAD` 各一次:各翻紅。 |
| F4 S13 預算 | 起算點移到判定時、或移到找 repo 根之後:翻紅。 |
| F5 rc 必須是 1 | 拿掉 `rc != 1 or`:翻紅。只拿掉 `rc not in (0, 1)`:仍綠,但最後一道還在擋,屬冗餘。 |
| F6 `.kts` | 鉤子改送、或 lumos 改推:各翻紅。 |
| F7 匯入純度 | 頂層 listdir 自己目錄:翻紅。放寬範圍其他腿沒釘住,見 F8。 |

## 其餘結果

- 我共跑約 94 處改壞,非等價仍綠 19 處,下面 F1–F9 涵蓋。
- 作者說的 46 處 45 處翻紅:丙 patch 沒附逐處表,我沒法逐處核,只能給上面的實測。
- 第 3 點(筆記對程式):依據來源新加 4 列與五篇家節點新加的行,跟程式行為對得上。唯一的矛盾在 F9,另有 F1 的 `[test:]` 綁定名不副實。審計修正紀錄 r1 的「35 條、major 10」與七份席報告核對相符。

F1 `t_slh_r1_spawn_window_term` 沒釘住「登記完補跑」
引句:「check("r1乙 空窗裡收到的 SIGTERM 登記完才處理、lint-new 照樣被收掉", pid is not None and _r1_tool_dead(pid), f"rc={r.returncode} pid={pid}")」
- 改的行:`scripts/hooks/claude/stop-lint-hook.py` 的 `if _STATE["pending"]:` 加 `_on_sigterm(signal.SIGTERM, None)` 兩行,換成 `pass`。
- 指令:`python3.14 scripts/test_lumos.py -k slh_r1_spawn_window_term`。
- 結果:3 passed, 0 failed,沒紅。
- 原因:拿掉補跑後,鉤子無視 SIGTERM,一路等到內層逾時才收 lint-new,所以測試只看「最後 pid 死了」仍過。耗時從 2.8 秒變 24.8 秒,測試分辨不出。
- 失敗場景:空窗裡的 SIGTERM 被吞掉。Claude Code 約 1 到 2 秒後 SIGKILL 鉤子,lint-new 與工具群組變孤兒。
- 筆記 `Systems/回合結束寫法檢查.md` 的 PITFALL 寫 `[test:t_slh_r1_spawn_window_term]`,綁定名不副實。
- 修法:斷言鉤子在遠小於內層時限內結束,並用 rc 或耗時判定。
severity: major
blocking: 是

F2 內容過濾器的 `process=` 這條沒有任何測試釘住
引句:「git("config", f"filter.{drv}.clean", f"touch '{marker}'; cat")」
- 改的行:`scripts/lumos` 的 `_lint_wt_filter_args`,拿掉 `, "-c", f"filter.{d}.process="`。
- 指令:`-k lwt_r1_git_filter_off`。
- 結果:5 passed, 0 failed,沒紅。
- 原因:測試只設 `filter.<名>.clean`,沒有任何案例設 `filter.<名>.process`。
- 實證:我另在獨立 repo 造 `filter.evil.process`。只清 clean 與 required 時,`git status` 照樣執行那支程式,記號檔出現。`process=` 清掉後不執行。
- 失敗場景:`filter.lfs.process` 是 git-lfs 的標準設定。有人拿掉這個 `-c` 後,被打開目錄自帶的 process 過濾器會在收工鉤子裡被執行,測試仍綠。
- 筆記 `Systems/pitfalls-code-loop.md` 寫「clean= process= required=false」並綁 `[test:t_lwt_r1_git_filter_off]`,測試實際只管 clean。
severity: major
blocking: 是

F3 可信來源守衛仍擋不住別名、getattr 與裸名,「真的呼叫」可被丟棄結果的呼叫滿足
引句:「_which = [c.lineno for c in _calls if _fname(c) == "which" and c.args and isinstance(c.args[0], _ast.Constant) and c.args[0].value == "lumos"]」
- 改的行:`stop-lint-hook.py` 的 `lumos = _trusted_lumos()`,三種改法都保留一句 `_ = _trusted_lumos()` 湊「真的呼叫」。
  - `from shutil import which as _wh; lumos = _wh("lumos")`:`-k hooks_never_run_code`,31 passed, 0 failed。
  - `getattr(__import__("shutil"), "which")("lumos")`:31 passed, 0 failed。
  - `lumos = "lumos"`(靠 PATH 解析):31 passed, 0 failed。
- 原因:AST 只認函式名字是 `which`,也沒查 `lumos` 變數是否來自 `_trusted_lumos()` 的回傳。
- 失敗場景:必須刻意閃避才會發生,單人自用的威脅模型下不算常見,所以降為 minor。
- 直接寫 `which("lumos")` 加註解已修好。
severity: minor
blocking: 否

F4 `_reason` 的 1500 字上限與換行放行兩處沒釘住
引句:「check("r1甲 6 條長路徑:整段不超過 1500 字", 0 < len(rs) <= 1500, str(len(rs)))」
- 實驗一:`stop-lint-hook.py` 的 `trial = lines + item + ([more.format(n=left)] if left else [])` 改成 `trial = lines + item`(不預留「另 N 條」那行)。
  - 指令:`-k slh_r1_reason_fits`。
  - 結果:7 passed, 0 failed。
  - 原因:測試的六條長路徑剛好沒落在邊界。最後附上的結尾提示行最多讓整段超出 1500 字約 45 字。
- 實驗二:`_waive_ok` 拿掉 `all(ch.isprintable() for ch in w) and`。
  - 結果:7 passed, 0 failed。
  - 原因:測試只造反引號案例,docstring 與筆記寫的「換行、控制字元整行不印」沒案例。
severity: minor
blocking: 否

F5 吞掉失敗的 `_hookevent.mark` 有四個分支沒釘住
引句:「check("r1乙 rc3 因預算沒跑到 → 記 timeout", one({"lint": {"rc": 3, "stdout": unchecked([{"kind": "budget", "cmd": "x"}])}}) == ["timeout"],」
- 各自改壞後 `-k slh_r1_marks_swallowed` 皆 7 passed:
  - `_unchecked_kind` 的 `{"budget","too-long"}` 拿掉 too-long。
  - 拿掉 `or "env" in kinds`。
  - 非 dict 的 rc3 輸出改回 None。
  - `開不了 lint-new` 的 mark 改 `pass`(整組 `-k slh_r1` 31 passed)。
- 失敗場景:這些分支錯了,`lumos enforcement` 會把該記 error 或 timeout 的事件記成 ok,也就是 r1 邊界席 F2 想堵的靜默失效。覆蓋不全,不是已發生的錯誤。
severity: minor
blocking: 否

F6 `_turn_start` 的「正」沒釘住
引句:「for label, t in (("字串", "abc"), ("清單", [1]), ("inf", "inf")):」
- 改的行:`return t if math.isfinite(t) and t > 0 else None` 拿掉 `and t > 0`。
- 指令:`-k slh_r1_bad_start`。
- 結果:6 passed, 0 failed。
- 失敗場景:起點紀錄的 t 被改成 0 或負數時,`--since` 變成 0,整個工作樹所有改過的檔都算這回合碰過。
severity: minor
blocking: 否

F7 `t_hookshared_r1_mark_shared` 對 `_mark_name` 是循環驗證
引句:「check(f"r1丁 收工點名 {fn} 的名字 = 共用消毒({sid[:12]!r})", (mp is None and want is None) or (mp is not None and mp.name == want),」
- 原因:測試拿 `_stop_mark_path(sid).name` 對 `_mark_name(sid)`,兩邊都走同一個函式,改壞函式本身兩邊一起變,測不出來。
- 實驗(`-k hookshared_r1_mark_shared`,各 20 passed, 0 failed):
  - `_hookshared.py` 的 `n in ("", ".", "..")` 拿掉 `".."`。
  - 長度上限 `[:120]` 改 `[:200]`。
- 失敗場景:會談編號是 `..` 時標記路徑永遠「存在」,擋停被悄悄關掉,正是 r1 正確性席 F3 的原案。
- `.` 與 `/` 的改壞有翻紅;`_claim_mark` 拿掉 O_EXCL,舊測試 `stop_block`、`stop_lint_hook` 會紅。
severity: minor
blocking: 否

F8 匯入純度探針放寬的兩條腿沒釘住
引句:「cases = {"noimp_list": (common + lst, True), "imp_list": (common + imp + lst, True), "noimp_read": (common + rd, True),」
- 實驗,改的行在 `scripts/test_lumos.py` 的 `_HOOK_PURE_PROBE`,指令 `-k hook_pure_probe_r1` 加 `-k handoff_hook_import_is_pure`:
  - `imports_shared` 改成恆為 True:4 passed, 0 failed。
  - `shared_ok` 拿掉 `imports_shared`:4 passed, 0 failed。
  - `shared_ok` 拿掉 `by_import`:4 passed, 0 failed。
  - `own_dir_ok` 拿掉 `imports_shared`:4 passed, 0 failed。
- 原因:只有 `own_dir_ok` 的 `by_import` 一腿有被 `imp_list` 逼紅。缺「匯入了共用模組、頂層碼自己去讀 `_hookshared.py`」與「沒字面匯入但靠 importlib 匯入」兩種案例。
- 這只放行讀共用模組原始碼,沒有寫入或執行,風險低。
severity: minor
blocking: 否

F9 計劃自相矛盾:d1 已改,範圍 2 第 6 條仍說要編排者改
引句:「d1 開頭欄位已在 ede88ffb9 改成同一回合」
- 檔案:`docs/lumos-toolchain-knowledge/Projects/Android寫法回合結束檢查與改檔前推列_計劃.md:113`。
- 該行這輪沒動,仍寫「d1 開頭欄位原文寫的是「同一會談」,要編排者改寫,見〈審計修正紀錄〉」。
- 實際狀態:`ede88ffb9` 是 `a1456f8f6` 的祖先,同檔 `:47` 的 d1 已寫「同一回合(prompt_id)」。
- 失敗場景:下一個 session 讀範圍 2 以為 d1 還錯,白費一輪去改。
severity: minor
blocking: 否

總結:最嚴重是 F1(spawn 空窗補跑的測試分辨不出)與 F2(內容過濾器 `process=` 沒測試),會擋 2 條。

清理說明:`/var/folders/.../T/gctl-run-*` 有約 596 份,內容沒有任何一份帶我的複本路徑,我無法確認哪些是我這場留的,沒有動。
