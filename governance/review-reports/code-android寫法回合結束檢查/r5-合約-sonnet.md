severity: major

第四輪合約席 F2、F3 重做後都修好了。F1 的放行理由我也看過,可以接受。這輪找到 1 條 major、3 條 minor。實驗全在 `git clone --shared` 的臨時複本做,都在前景或通知後收齊,repo 沒有被改動,臨時目錄已刪。

**先交代上一輪核對結果**
- **F2 找改動邊界**:在主程式與鉤子兩份 `_wt_changed_nofilter` 同步改壞,四個 r4wt 測試都會紅。
  - `<` 改 `<=`:`t_r4wt_racy_equal_mtime` 紅。
  - 去掉大小比對:`t_r4wt_same_time_size_diff` 紅。
  - 去掉雜湊行數檢查:`t_r4wt_hash_count_mismatch` 紅。
  - 拿掉 `len(old) == 1`:`t_r4wt_twin_deletes` 紅。
  - 另外,拿掉結尾 CR 判斷,`t_r4wt_cr_name` 紅。
- **F3 計劃的〈依據來源〉**:新增五列和改三列都與程式對得上。
  - `_GIT_UNTRUSTED_FIXED` 三項是 `core.fsmonitor`、`core.hooksPath`、`diff.external`,與鉤子那份只差 `core.hooksPath`。
  - `_lint_wt_filter_args` 確實已不存在。
  - 引用的 git 官方原文,本機 `git help` 查得到。
  - 「18 條/major 8」我重數 r4 七份席報告,數字吻合。
  - 家節點新加的 `[test:…]` 名稱全部存在。
- **F1 放行**:字串拼接這類間接 PATH 查找,要刻意這樣寫才繞得到,屬威脅模型排除的刻意偽造。
- **其他守衛與改壞實驗**:五支鉤子各自拿掉 `is_absolute()`,`t_r4hook_relative_lumos` 五支都紅。`t_r4note_*` 與 `t_r4imp_shared_shape` 抽查 6 種改壞全紅。以下結果也全紅:
  - `_impact_line_delta` 的 NUL 判斷、加號行、總量累計、`_impact_diff_seed_ok` 過濾。
  - `_impact_wt_nofilter` 取 repo 根、`_lint_wt_toplevel`、`_impact_hunk_query` 的 4000 字上限、已刪檔首行讀取。
  - 含換行檔名的退回只用路徑。
  - 在 `_impact_wt_nofilter` 內加 `status` 或 `diff` 呼叫(會由 clean 過濾器的標記檔測試抓到)。
- **等價改壞(不算 finding)**:`ls-files` 三處的 `--full-name` 拿掉全綠,因為已經 `-C <根>`,這個旗標是冗餘的。每支的 1MB 上限預檢拿掉也全綠,因為後面還有 `len(new) > cap` 與 `old is None` 兩道。

**F1 影響分析不開非一般檔的 `S_ISREG` 守衛沒有測試,改壞全綠且實測會卡死**
引句:「if (st is not None and (not _st.S_ISREG(st.st_mode) or st.st_size > cap)) or (n is not None and n > cap) \」
- 改壞:在 `scripts/lumos` 的 `_impact_wt_nofilter` 拿掉 `not _st.S_ISREG(st.st_mode) or`。
- 指令:`python3.14 scripts/test_lumos.py -k impact_r3` 與 `-k r4imp`,結果 20 過 0 敗、24 過 0 敗,沒紅。
- 實測後果:把已追蹤的 `scripts/f.py` 換成 FIFO,再呼叫 `_impact_wt_nofilter`。
  - 原版回 `{'scripts/f.py': 'scripts/f.py'}`,並把它列進退回只用路徑的清單。
  - 改壞版卡在 `open()`,20 秒後被 alarm 殺掉,收工點名的鉤子會卡到預算耗盡。
- 全 repo 只有幾處別的 `mkfifo` 測試,沒有任何一支針對 `_impact_wt_nofilter` 或 `_wt_changed_nofilter` 的型別變更。
- 這支守衛是這輪重寫那一格才寫進 patch 的,屬關鍵分支沒被釘住。
severity: major
blocking: 是

**F2 含「結尾 CR」的檔名分支,影響分析這一路沒有測試**
引句:「if "\n" in p or p.endswith("\r"):」
- 改壞:拿掉 `or p.endswith("\r")`。
- 指令:`-k r4imp` 與 `-k r4wt_monorepo`,24 過 0 敗,11 過 0 敗,沒紅。
- `t_r4imp_newline_name` 只造含 `\n` 的檔名(對照組拿掉 `\n` 判斷會紅)。CR 這一半沒有案例。
- 實測:改壞後該檔的舊版讀成空,查詢文字只剩新內容 `n = 2`,舊行沒進去,也沒有被列進 `query_path_only`。後果輕,所以只算覆蓋不全。
severity: minor
blocking: 否

**F3 已刪檔「取 HEAD 的模式」只測了 100644**
引句:「mode = ("100755" if st.st_mode & 0o111 else "100644") if st is not None else head_mode.get(p)」
- 改壞:把 `head_mode.get(p)` 換成固定 `"100644"`。
- 指令:`-k r4imp_deleted`、`-k r4imp`、`-k impact_r3`,全綠。
- `t_r4imp_deleted_shebang` 的兩支刪除檔都是 100644,看不出是取 HEAD 還是寫死。
- 失敗場景:簿記目錄裡「已刪、100755、沒有 `#!` 且沒副檔名」的檔,原本因 100755 算程式,改壞後會被當非程式剔除。
severity: minor
blocking: 否

**F4 `--worktree-nofilter` 的說明文字仍寫 difflib,計劃把加減行的順序寫反或寫得模糊**
引句:「收工點名鉤子專用:只准搭 --diff HEAD --sync-check;工作樹改動不跑 git diff(不經內容過濾器),改動內容用 difflib 算」
- 引自現檔 `scripts/lumos:76897`。這行 patch 沒改,但 r4 把算法換成 Counter 相減後它就過期了,和 `_impact_line_delta` 的說明及計劃相反。
- 計劃第 8 條寫「多出來的行全部排在前面」,程式實際是 `["-"…舊版多的] + ["+"…新版多的]`,新增的行排在後面。
- 後果:查詢文字截在 4000 字時,新增的行先被切掉。實測舊版刪 120 行、新增含 `DANGER_NEW` 的 2 行,輸出 4000 字,`"DANGER_NEW" in q` 為 False。
- 單一 hunk 的 `git diff` 也是先刪後加,所以不算退步。多個 hunk 時 git 會保留較前面 hunk 的加號行,Counter 版不會。
severity: minor
blocking: 否

總結:最嚴重是 `_impact_wt_nofilter` 的非一般檔守衛 `S_ISREG` 沒有測試、改壞全綠且實測卡死,會擋 1 條。

**暫存清理**:`/tmp/lumos-seat-work/code-android寫法回合結束檢查/合約-sonnet` 與我自己手跑留下的 `gctl-run-uku9q8j0` 已刪。批次改壞跑紅時另外留下的 `gctl-run-*` 現場,我沒有逐一記路徑。共用的暫存目錄裡有 973 份、近兩小時 87 份,無法證明哪些是我的,依規定沒有批次刪,留給編排者處理。
