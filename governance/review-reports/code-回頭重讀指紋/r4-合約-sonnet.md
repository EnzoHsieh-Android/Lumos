severity: minor

我審了文件修補和測試修補,也對照了圖譜工作樹 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/` 裡的程式與 CI 設定。沒有找到 major 以上的問題,只有三條 minor。

先答你特別點名的幾項:

- **「逾時不擋」的舊說法已全部改成照擋。** 計劃〈做法〉5 與 S27、`Systems/筆記內容審.md` 的逾時條目、06 手冊第一層、`scripts/lumos` 的 `_note_reread_blocking` 說明,語意都一致。測試 `t_reread_fp_timeout_blocks` 與 `t_reread_fp_timeout_labels_each` 都斷言不出現「這次不擋」。
- **殘留的「不擋」不是舊說法。** 全 repo 還找得到的幾處,都是別的情境:`scripts/lumos:37773` 的「掛鉤沒帶 --gate,這次不擋」、`舊句兩道轉擋_計劃` 的 S25,以及計劃裡提到「改回照擋」歷史的敘述。`t_reread_fp_timeout_not_blocking` 已不存在,條款改綁新名稱。
- **跳過純標點行與 S20–S22 一致。** 計劃〈做法〉1 寫「只有 ASCII 標點與括號的行,非 ASCII 算有字」,對得上 `_NOTE_REREAD_SKIP`。S20 到 S22 列的測試名都存在,`t_reread_fp_indent_inline_same` 的手算表也含 `#endif`、中文字、tab、`\r`。
- **CI 設定和文件說法對得上。** `ci.yml` 的 note reread 那一步在 push 事件跑、`fetch-depth: 0`、`continue-on-error` 加 `|| true`,所以「只印不擋」成立。
- **WHY 行格式沒問題。** `[出處:][因:][不選:][test:]` 都有。程式 `scripts/lumos:53264` 也是強制設值,和 WHY 的「強制設值而不是 setdefault」一致。
- **REVISIT 行日期格式正確。** 兩條都是 `REVISIT:2026-12-15`。第二條的內容有問題,見下面第一條。

severity: minor
blocking: 否 — 只影響日後回頭看的資料來源,不影響閘的行為
引句:「順便數 CI(來源 ci)列出、但同一個頂端在本機推送前那筆已對照的篇數」
問題:新加的 REVISIT 要數 CI 事件,但 CI 跑的帳不會留下來。`.github/workflows/ci.yml` 沒有上傳 `docs/.governance-log.jsonl`,也沒有提交它。note reread 那一步寫進 runner 本機帳的 `來源 ci` 事件,工作結束就消失。2026-12-15 到期時,能數的只剩 GitHub 的 run log,它有保留期限,而且那一步是 `continue-on-error`,沒人會去看。計劃拿「CI 補驗功能分支」當偽造遠端追蹤 ref 的唯一緩解,但回頭看的條件實際上算不出來。這等於 CLAUDE.md 鐵則 4 說的「寫不出就是該處理」。
具體失敗情境:有人在本機把功能分支的主線追蹤 ref 偽造後推送。CI 重算後會把它列在 run log 裡,但沒人看。到 12-15 數「CI 列出而本機已對照」的篇數時,帳裡一筆 `ci` 來源事件都沒有。數出 0,會被誤判成沒有發生過。
佐證:`scripts/lumos:37942` 的 `來源 {'ci' if _in_ci() else 'hook'}` 只寫進該機器的帳。`.github/workflows/ci.yml:247-264` 沒有任何持久化帳的步驟。

severity: minor
blocking: 否 — 屬於說明放錯家,不影響行為
引句:「在 lumos 主程式入口 `main()` 最前面強制設 `GIT_NO_REPLACE_OBJECTS=1`」
問題:這次新增的兩個行為,只寫在計劃和 06 手冊,沒有寫進程式的家。一個是入口 `main()` 強制設環境變數,一個是 `_note_reread_bp_vs_remote` 推主線時核對分岔點。`Systems/筆記內容審.md`(`_note_reread_*` 的家)沒有提到 `_note_reread_bp_vs_remote`、偽造追蹤 ref、`GIT_NO_REPLACE_OBJECTS` 這幾個詞;`Systems/lumos-cli-lifecycle.md` 的 about_code 列了 `scripts/lumos`,也沒有。那條 WHY 行放在 `Projects/` 計劃裡,計劃收尾後就是歷史。
具體失敗情境:之後有人改 `main()`,或把核對套到功能分支,`lumos impact --file scripts/lumos` 只會推出家節點,看不到「入口必須強制設、不能 setdefault」和「核對只限推主線」這兩條。有人順手把 `os.environ[...] = "1"` 改成 `setdefault`,測試沒有任何文件提示他為什麼不行。
佐證:`grep GIT_NO_REPLACE_OBJECTS docs skills` 只命中計劃一篇。06 手冊只描述了推主線核對這一半。

severity: minor
blocking: 否 — 文字與程式有偏差,但擋與放的方向相同
引句:「推主線時,本機的遠端追蹤 ref 不是遠端那條主線現在的值的祖先(被改過或遠端改寫過)會擋下」
問題:06 手冊說的是「追蹤 ref 不是遠端值的祖先」,程式實際比的是「分岔點 `bp`」。`_note_reread_bp_vs_remote` 對 `old` 做 `merge-base --is-ancestor bp old`,`bp` 是追蹤 ref 與頂端的 merge-base,不是追蹤 ref 本身。計劃〈做法〉3 的寫法(分岔點必須是它的祖先或相等)是對的。測試 `t_reread_fp_forged_tracking_ref_blocks` 的 docstring 也寫成「不是遠端那個值的後代」,和程式的訊息「分岔點 … 不是 … 的祖先」不同。
具體失敗情境:使用者依 06 手冊自查,看到本機追蹤 ref 領先遠端值(例如剛 fetch 完)會以為會被擋,但實際上只看分岔點。反過來,追蹤 ref 被指到遠端值的祖先(更舊的提交)時手冊說會擋,程式卻放行,後果只是指紋多列。
佐證:`scripts/lumos:37635-37680`(`_note_reread_bp_vs_remote`)。

最高等級 minor,blocking 0 條。
