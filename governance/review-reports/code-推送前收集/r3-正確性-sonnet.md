severity: clean

第三輪修補我沒找到會做出錯行為的問題。我用 `/bin/bash`(3.2.57)實跑了子殼陷阱的行為,其餘靠讀程式。

## 已讀,無 finding

**一、改用 `_pp_kill_jobs` 後各片離開碼收集**
- 實驗:子殼裡先 `trap '_pp_kill_jobs; exit 143' TERM` 和 HUP,再起三片,第一片 1 秒後 `exit 5`,另兩片 `sleep 31`;`_pids` 逐個 `wait`。
- 先結束的那片,`wait` 取回離開碼 5,不會漏。
- 主殼在子殼運作中收到 HUP:主殼的 `jobs -p` 列出子殼並送 TERM,離開碼為 129,`EXIT` 陷阱照跑。
- 子殼的 `jobs -p` 只列還活著的另兩片(實測 `86918`、`86920`),把它們收乾淨;已結束的那片不在清單內,不會誤殺別的行程。
- 子殼的 `EXIT` 陷阱是空的(`trap -p EXIT` 為空)。子殼正常結束或被收掉時不會誤刪主殼的 `$_PP_TMP`。
- 在 `wait` 期間收到 TERM 或 HUP,陷阱會立刻執行,不用等到 `wait` 返回。
- 被收掉的片離開碼是 143 或 137,屬於「非 0 且非 3」,`_bad=1` 判紅,不會被當成 3(選中 0 支)。
- 原本「`&` 起片」與「記 pid」之間的漏收窗口已消失。這是實質改進。

**二、HUP 與 EXIT 陷阱的先後**
- `exit 129` 之後才跑 `EXIT` 陷阱(`impact_done; rm -rf "$_PP_TMP"`)。
- 實測順序是主殼 `MAINEXIT` 在前,子殼收片在後,最後沒有殘留片。
- `rm -rf` 與各片寫 log 的時序競爭只會讓各片寫入失敗,片隨後被殺,沒有副作用。
- 紅時搬出去的 log:`pp_keep_log` 用 `mktemp "${TMPDIR:-/tmp}/lumos-prepush-$2-XXXXXX"` 複製到暫存資料夾之外,並在 `exit 1` 之前完成。`rm -rf` 不會刪到它。
- HUP 中斷時還沒走到印紅,所以不涉及保留 log。
- 收集到的擋下原因放在 `$_PP_TMP`,HUP 中斷時隨目錄一起清掉。本來就不彙總,符合預期。

**三、包組重導向後的錯誤判斷**
- 四處都是 `{ cmd >> "$f"; } 2>/dev/null || X`。`2>/dev/null` 先套在整組,組內開檔失敗的訊息也進 `/dev/null`。
- 失敗時組的離開碼仍是 1,所以 `|| _ok=0`、`|| return 0`、`|| true`、`if { ... } 2>/dev/null && [ -s ]` 都照舊生效。
- `impact_once` 在 `&&` 左邊是複合命令,語意不變。

**四、拿掉 `summary` 欄位**
- 全 repo 搜 `_CODELOOP_BLOCK_KIND_*` 與 `b.get("summary")`,沒有任何讀者。
- 掛鉤只讀 `LUMOS-BLOCKS:` 那行(種類以逗號分隔)再經 `pp_cl_reason` 轉句子,不讀 JSON 的 `summary`。
- 測試端 `t_prepush_cl_reason_table_matches_lumos` 已改為雙向比對 `reason_kind` 集合,並用 `all(sorted(b)==["reason","reason_kind"])` 釘住欄位形狀。

**五、資料狀態五問**
- 新增寫入只有 `_PP_TMP` 下的檔,離開時由 `EXIT` 陷阱統一清,無新增殘留。
- `reason_kind` 的 `"?"` 或空值會落到 `pp_cl_reason` 的 `*)` 通用句,不丟失。
- 舊版 lumos 沒有 `--keep-going` 或沒有 `LUMOS-BLOCKS:` 時,`_cl_n=0`,會走通用句記一筆,符合設計。
- 沒有新增持久狀態、沒有 schema 變動、沒有跨版相容問題。
- 治理帳 `extra.blocks` 仍是種類清單,與拿掉 `summary` 無關。

我沒有逐個驗證 bash 3.2 對大量片同時結束時 `wait` 是否保留所有狀態,只靠常規行為推定沒問題。這部分沒有證據顯示有誤。

最高等級 clean,blocking 0 條。
