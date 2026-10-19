severity: minor

**架構對齊審查(第 3 輪,修補差異 r3-repair-lumos.patch,修後 342cf099)**

先講結論:上一輪架構席的要求這輪都做到了,修補沒有新增 major。有 4 條 minor。對照時我把 342cf099 的 `scripts/lumos` 取出放在 scratchpad,下面的行號都出自那一份。

**上一輪要求的核對**
- 差異清單改用 `_nodehome_changed_vs_disk`:本輪修補範圍外,沒動到,我也沒有重驗。
- 三指令預設範圍一致:`cmd_cochange_check` 現在用 `diff_range is None` 分流,跟 home check、note-shape 同一條。`--diff ""` 回 rc2。已對齊。
- 共用判斷收成一份:`_planned_ref_tokens` 在內部去掉結尾斜線,refcheck 與 doctor P 段兩個呼叫端的重複正規化都拿掉了。`_excluded_line` 內部先數冒號,lint、判門、推送前重判門三處一起受保護。`_dirty_non_bookkeeping` 讓 `cmd_loop_fix_check` 與規格閘補跑紅的警告共用同一段,不再各抄一份。
- `_spec_gate_status_at` 讀起點版本:起點改用 `_range_base`(`scripts/lumos:9979`),讀檔仍走 `_note_text_at_rev`(`scripts/lumos:22768`)。同檔的 `_pq_push_remind`(`scripts/lumos:9069`)、`_sc_churn`(`scripts/lumos:9477`)也都用 `_range_base`,所以沒有新增第二種讀版本的做法。
- 留痕不裁的理由:`_spec_gate_latest_merged` 的 docstring 寫明三個呼叫端各自處理 None 的理由(推送閘擋下、規格閘重跑當沒有、doctor 只做統計)。已做到。
- doctor S14 合讀:改成先判 `_sg_merged is None` 並印一句「只看本機審查帳」,已做到。

**一、分層與依賴方向**

沒有跨層直呼。新碼都放在鄰居相同的層,呼叫方向跟以前一樣。有一處放置位置跟鄰居不同:

severity: minor
blocking: 否
引句:「def _dirty_non_bookkeeping(rr, untracked=False):」
- `_dirty_non_bookkeeping` 被修正關卡(`cmd_loop_fix_check`)和規格閘(`_spec_gate_low_not_red`)兩個不同主題共用。它卻放在 `_summary_add_locked` 後面,夾在摘要寫入那組函式中間(`scripts/lumos:22993` 附近)。同一個目的的鄰居 `_fix_git_z`(`scripts/lumos:15093`)放在修正關卡區塊。
- 專案裡已經有 `_porcelain_z_paths`(`scripts/lumos:54638`),專門處理 `git status -z` 改名時會吐兩個片段的情形,註解還寫明「一律切 [3:] 會砍壞舊路徑」。新 helper 沿用舊碼的 `x[3:]`,等於 porcelain 路徑解析有兩套。這是搬舊碼,不是新寫。
- 兩邊的 `--untracked-files` 也不同:新 helper 的 untracked=True 用 `normal`,`scripts/lumos:54667` 用 `-uall`。`normal` 會把未追蹤目錄折成一行,判斷「有沒有髒」夠用,但路徑清單不精確。
- 判不準算不算 major,標 ⚠ 交編排者。我偏向 minor:是同一個解析邏輯長在兩處,不是新做法。

**二、命名與錯誤處理**

severity: minor
blocking: 否
引句:「def _is_git_worktree(root):」
- `_is_git_worktree` 是新 helper,用 `_lens_git(root, "rev-parse", "--is-inside-work-tree")`。`cmd_note_shape`(`scripts/lumos:37239`)已經 inline 寫了同一條判斷,那邊把 `r is None` 一律當「不是 git」。兩處對 None 的語意不同:新的分成 True / False / None,舊的把 None 併進「不是」。
- 新的語意在 `_summary_write_shape_check` 裡有理由(git 跑不起來不能當作非 git 專案放行)。但舊處沒有改成呼叫新 helper,所以同一個問題有兩種寫法。

severity: minor
blocking: 否
引句:「return ("擋下:" + err if not err.startswith("擋下") else err), []」
- 這行靠字串開頭判斷要不要補「擋下:」前綴。鄰居的做法是來源直接產生完整形狀的訊息,例如同函式下方的 `"擋下:" + msg + ";檔案沒動。…"`,以及 `cmd_cochange_check` 的 `"擋下:--diff …"`。
- `_drift_fix_shape_err` 的另一個呼叫端(`scripts/lumos:44129`)拿到的是不帶「擋下:」的訊息,走自己的錯誤輸出路徑。同一個函式的回傳,兩個呼叫端的前綴約定不同。

severity: minor
blocking: 否
引句:「print(f"提醒(note_shape.gate 是 warn,不擋):{msg}", file=sys.stderr)」
- warn 模式的提醒通道分裂了。`_drift_fix_shape_err` 在 warn 時自己印到 stderr 並回 None。`_summary_write_shape_check` 的格子檢查提醒仍然走 `warns` 回傳清單,由呼叫端印。
- 同一個命令裡,形狀提醒走 stderr,格子提醒走回傳值。上一版是兩者都進 `warns`。
- `_note_shape_config(cfg)` 也在 `_drift_fix_shape_err` 和 `_summary_write_shape_check` 各讀一次。總開關 off 的判斷因此在兩處重複。

此外 `_spec_gate_status_at` 有一處輕微不一致,也算進這一問。`_pq_push_remind` 會先處理左端空的範圍(`..b` 補成 `HEAD..b`),`_spec_gate_status_at` 沒有。`..b` 時 `_range_base` 回 None,得到的結果是「當成不是 done」,照嚴的判。結果是安全的,只是兩處對 `..b` 的處理不同。

**三、第二種做法**

沒有 major。新引入的 helper 都能對上既有同類:
- `_ref_word_looks_like_path` 借用既有的 `_drift_looks_like_ext`(`scripts/lumos:42248`),沒有另寫副檔名判準。
- `_ns_neg_clause_break` 的 Unicode 分類判斷,跟 `unicodedata.category` 的既有用法一致。
- `_ns_neg_cond_paired` 跟 `_ns_neg_cond_open` 同形,都用 `_REVISIT_MARK_RE.sub` 處理開頭。
- 此外有兩處第二種做法的傾向,已記在第一問和第二問:porcelain 解析兩套,git 工作目錄判斷兩套。兩者都屬於重複實作的程度,因此都標 minor。

不對齊共 4 條,其中 major 0 條。
