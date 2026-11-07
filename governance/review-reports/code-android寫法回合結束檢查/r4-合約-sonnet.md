severity: major

第三輪合約席 F1 到 F4 都重做過了,現在全部會翻紅。這輪找到 1 條 major 和 2 條 minor。實驗全在 `git clone --shared` 的臨時複本做,主程式與鉤子兩份 `_wt_changed_nofilter` 同步改壞,且在前景跑完;臨時目錄已刪。

**第三輪 F1 到 F4 重做結果**
- F1(重複定義 `_trusted_lumos`):在 `stop-lint-hook.py` 插第二個定義,`-k hooks_never_run` 變成 50 過 1 敗,會紅。
- 同一支測試另外改壞八種也都紅:`which("lumos")` 直呼、`from shutil import which as _w`、`getattr` 加字串拼接、註解寫函式名、從 `_hookshared` 匯入、decorator 蓋掉、變數賦值繞過、在 `check-graph-sync.py` 與 `lumos-entry-hook.py` 巢狀或 lambda 改綁。
- F2:`1e999` 的案例已補(`t_lwt_r3_small_fixes`)。
- F3:兩個 not-checked 出口各自明寫 `deliberate`,案例已補(`t_lwt_r3_unchecked_kind_one_place`)。
- F4:`t_hook_pure_probe_r1_scope` 已加 `imp_sibling` 案例。

**F1 逐字複本守衛擋不住「變數間接」的 PATH 查找**
引句:「_lits = [n.lineno for n in _outside if isinstance(n, (_ast.List, _ast.Tuple))」
- 改壞:在 `stop-lint-hook.py` 的 `lumos = _trusted_lumos()` 後面加 `_nm = "lum" + "os"` 與 `subprocess.run([_nm, "x"])`。
- 指令:`python3.14 scripts/test_lumos.py -k hooks_never_run`
- 結果:`51 passed, 0 failed`,沒紅。
- 原因:守衛只抓字面常數 `"lumos"` 直接放在 List 或 Tuple 裡,字串拼接或先指定給別的變數就繞過,Python 照樣從 PATH 找 `lumos`。
- 這個缺口要刻意寫才繞得到,屬單人信任模型下的縱深題。
severity: minor
blocking: 否

**F2 找改動函式的關鍵判斷改壞後測試仍綠**
引句:「elif idx_ns is not None and s.st_mtime_ns < idx_ns and stamp.get(p) == (s.st_mtime_ns, s.st_size & 0xFFFFFFFF):」
- 四處改壞都全綠,涵蓋 `-k lwt_`、`lint_new`、`sync_nudge`、`cgs`。
  - `<` 改成 `<=`(時間戳相等時 git 視為 racy,必須算雜湊)。
  - 去掉大小比對,只比時間。
  - 引句:「if got is None or len(sums) != len(ask):」改成只判 `got is None`。
  - 引句:「if old and len(old) == 1 and (res.get(old[0]) or [None])[0] == "D":」拿掉 `len(old) == 1`,同內容的刪除檔有多個時也會硬配成改名。
- 原因:`t_lwt_r3_racy_stat` 只用「未來時間」的檔,測不到「時間剛好等於索引時間」。也沒有案例造出「時間相同、大小不同」的檔,或讓 `hash-object` 輸出行數對不上。改名也沒有「兩個同內容刪除檔」的案例。
- 錯了的後果:該算雜湊的檔被當成沒動,收工點名漏點檔(少查);改名誤配則會把新檔當成改名而拿錯基準。
- 對照:`racy` 整個條件拿掉會紅,所以守衛整體有效,只是這幾個邊界沒釘。`conflict`(UU)改壞則被 `t_lint_new_worktree` 抓到。
- `t_lwt_r1_term_int_cleanup` 在四路並行時會誤紅,單跑通過,屬負載造成的雜訊,與這些改壞無關。
severity: major
blocking: 是

**F3 計劃的〈依據來源〉沒更新,舊列與程式行為相反**
引句:「| 宣告檔乾淨判法 | git status 的 `--ignored=matching` |」
- 這輪沒有新增任何〈依據來源〉列:`r4-repair-丁.patch` 與整份 `r4-repair.patch` 都沒有 `+|` 開頭的行,`grep -c "hash-object --no-filters"` 在該表也是 0。
- 同表另有三處已過期:
  - 引句:「| 查狀態時關掉內容過濾器(代碼審 r1) |」指向的 `_lint_wt_filter_args` 在 r2 就已移除。
  - 「不信任 repo 的 git 參數只有一份(代碼審 r2)」仍寫「clean、process、子 repo 過濾器四條……帶參數後都不執行」,而 `_git_untrusted_c` 現在只剩固定三項。
  - 計劃第 71 行 WHY 仍寫「檔集仍以工作樹狀態為底(`git status`)」。
- 程式現況見 `scripts/lumos:40227` 的 `_lint_wt_unready`,宣告檔乾淨改走 `_wt_changed_nofilter` 加 `ls-files -o -i`;`scripts/lumos:41256` 是 `_LINT_WT_FSIZE_SLACK`,`scripts/lumos:41324` 是 `_lint_run_and_parse`。
- 缺的新列至少有:`hash-object --no-filters`、`ls-files -s`、`RLIMIT_FSIZE`。這違反「機制依據收尾前寫進〈依據來源〉」的規矩。
severity: major
blocking: 是

**抽查其他項(沒標 finding)**
- `_lint_spawn` 寫入 `fail_info["unresolved"]`,但全 repo 沒有讀它的地方。工具被拒時,使用者看到的只是「原因不明」或「沒裝」,拒絕原因(PATH 空項、相對路徑)沒有浮到表面。這只是少了診斷,不影響行為。
- difflib 版 `_impact_wt_nofilter` 會丟掉以 `++` 或 `--` 開頭的內容行。舊的 `git diff` 路徑有同樣行為(`scripts/lumos:67421` 附近),所以不是退步,不標。
- 「未解析工具 → `unchecked_kind` 為 `failed`」的說法與程式一致:`env-unavailable` 在 `_lint_new_wt_json` 會落到 `failed`。
- 沒跑的項目:`_lint_wt_resolve_tool`、`RLIMIT_FSIZE`、`_lint_wt_unready` 的 `returncode == 1` 分支、三支鉤子 stdin 的改壞實驗。上一輪合約席已做過,我沒有重做,對應測試都在現行綠燈中。

總結:最嚴重是 `_wt_changed_nofilter` 的時間、大小、雜湊行數與改名配對邊界改壞後測試仍綠,以及計劃〈依據來源〉缺新列且有過期列,會擋 2 條。
