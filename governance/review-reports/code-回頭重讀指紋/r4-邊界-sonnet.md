severity: minor

整體沒有 major 或 blocker。這輪三項修補我都實跑過,邊界輸入下行為合理。有兩條 minor。

我做了這些驗證:
- 直接呼叫縮排鏈函式,輸入涵蓋 CRLF、tab、全形標點、`#endif`、`fi`、`-->`、`}` 這類純標點行、整檔只有標點、空檔、n=0 純刪除、`\xff\xfe` 非 UTF-8 行。
- 鏈的結果都符合規則。非 ASCII 算有字,有字的頂格行照舊截斷,純標點行跳過。
- 效能:4180 萬位元組、40 萬行、50 層巢狀加 50 段改動,0.43 秒;100 萬行全標點,0.08 秒。逾時已到時回 None,資料為 None 時不誤報。
- 破壞測試(在 `git archive` 出來的副本上做,已清掉 `__pycache__`)。
  - 把跳過集合縮回只有空白:`t_reread_fp_chain_skips_punct_lines`、`t_reread_fp_indent_inline_same`、`t_reread_fp_moved_past_punct_lines` 全紅。
  - 讓祖先核對永不丟停止:forged 測試紅。
  - 拿掉「只核對推主線」的 `hit` 判斷:功能分支 rebase 後強推那條斷言紅。
  - 拿掉 `bp_vs_remote` 裡的全 0 判斷:測試仍綠,但 `_lens_full_sha` 對全 0 本來就回 None,所以那個判斷是冗餘,不是漏洞。
- 完整的 `-k reread_fp` 在對話裡跑超過 2 分鐘,我停了它。副本上跑完是 149 條通過。

已讀,無 finding:
- 純標點判定邊界:全形標點、`*/`、`"""`、`end`、`fi`、`esac`、`-->`、`%}`、只有註解符號的行、CRLF、tab。
- 整段改動全在純標點行上、檔案只有標點、新增檔與純刪除。
- 遠端值全 0(新分支):`rg[0]` 全 0 直接 return。
- 刪除 ref:`pre-push` 在 `_lsha` 全 0 時整段 `continue`,到不了 reread-check。
- 逾時照擋的改動與印出的文字。

severity: minor
blocking: 否 — 只在 git 查詢本身失敗或逾時時多擋,屬寧可多擋,有單次跳過可用。
引句:「if not hit and not err:」
問題:`_note_reread_bp_vs_remote` 的 `err`(`_push_mainlines` 查主線候選失敗)路徑不看被推的是不是主線。只要 `err` 為真,功能分支的推送也會走到下面的 `r = None`,把 `base` 重設成 `bp=None, raw={}, why="git 失敗或逾時"`,整批退回舊版指紋。這輪又把「退回舊版」改成照擋。prepare 記的是新版紀錄,舊版指紋比不到,所以這次推送必擋。
具體失敗情境:推功能分支 `refs/heads/feature`,查 `refs/remotes/origin/HEAD` 之類候選時 git 偶發失敗或逾時。這次對任何有候選筆記的功能分支都擋下,但「核對只管主線」的設計並沒有要擋這種推送。解法是 `err` 時也要先判被推的是不是主線(例如只比 `target` 與 `refs/remotes/<remote>/main|master`),不是就直接 return。
佐證:``scripts/lumos: `scripts/lumos:37635-37668` ``(patch 的 `_note_reread_bp_vs_remote`)。

severity: minor
blocking: 否 — 只會多算、多要求一次重讀,方向是多擋,不是漏擋。
引句:「全是跳過的行(或 n=0)就當成在 s+n 那個位置、無限深」
問題:純標點的改動(例如 `)` 或 `}`)被當成「在 s+n 位置、無限深」,鏈取自上面最近一行有字的行,而那行常比標點行縮排更深。我實測 `x(` 底下是 `1,`,再下一行是只改動的 `)`,鏈變成 `('def f():','if a:','x(','1,')`,比 `)` 自己所在的那一層多一層。同一個呼叫裡鄰近的參數行一被改,這個 `)` 改動的標籤就變,改動和它沒關係。
具體失敗情境:作者只動 `)`,主線改了緊鄰上一行的參數。指紋變了,多要求一次重讀。測試 ⑦ 把這個行為寫成預期,所以這是設計取捨而不是漏洞。若要更貼近,可改成鏈從該標點行自己的縮排往外推。
佐證:``scripts/test_lumos.py: `t_reread_fp_chain_skips_punct_lines` ⑦``(`/tmp/code-回頭重讀指紋-r4-repair-tests.patch`)。

我的暫存目錄已刪(副本與紅時留下的 `gctl-run-*`)。`/var/folders/tc/.../T/` 底下還有 687 份 `gctl-run-*`,多數不是我建的,我沒動。

最高等級 minor,blocking 0 條。
