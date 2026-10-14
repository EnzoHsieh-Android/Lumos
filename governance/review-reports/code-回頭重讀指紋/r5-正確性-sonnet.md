severity: minor

我只找到一條 finding:批次 diff 切段時,路徑含 ` b/` 的二進位檔、只改權限的檔、空的新增或刪除檔會對不到名字,整支檔退回舊版指紋。實驗用的臨時目錄已刪。

## finding 1:路徑含 ` b/` 的無 `+++` 檔,切段後對不到檔名

severity: minor
blocking: 否 — 失敗時退回 v1(舊版指紋),方向偏保守,不會漏判。代價是這篇筆記在主線前進時又要多重讀一次。
引句:「names = list(_patch_file_changes(head.decode("utf-8", "surrogateescape"), headers=False, lf_only=True))」

問題:`_note_reread_split_diff` 靠 `_patch_file_changes` 從每段檔頭取檔名。沒有 `+++ b/…` 行的段(二進位、只改 mode、空檔新增或刪除)只能從 `diff --git a/X b/X` 那一行用 `rfind(" b/")` 還原檔名。路徑本身含 ` b/` 時(例如目錄叫 `opt b`),這一招會取到最後一個 ` b/` 之後的尾巴。舊版逐檔跑時檔名不參與查找,只取雜湊,所以不受影響。新版把檔名當 `spans` 的鍵,對不到就整段丟掉。

具體失敗情境:
- 輸入:分岔點到頂端之間,`opt b/z.bin` 改成別的二進位內容;候選筆記的 about_code 列了這支檔。
- 結果:`_note_reread_split_diff` 把這段的鍵記成 `z.bin`。`spans` 裡沒有 `opt b/z.bin`,批次裡切不出這支,單支再問一次仍然切不出,`_note_reread_fp_diff` 回 `b""`。
- 接著 `_patch_file_changes` 得到空結果,`_note_reread_fp_file` 回 `(None, "diff 空")`。整篇筆記的 v2 退回 v1。舊版同一支檔的指紋算得出來。

我在臨時 repo 重現過:`opt b/z.bin` 是 MISSING;`x y/z.bin`、`emptynew`、`m.sh`(mode-only)、有 `+++` 的 `opt b/t.txt` 都對得上。`dir b/mode.sh`(mode-only)和 `dir b/empty new`(空檔新增)同樣 MISSING。

佐證:
- file: `scripts/lumos:36601`(`_note_reread_split_diff`,同一個檔名鍵取法)
- file: `scripts/lumos:26033`(`_patch_file_changes`,`rfind(" b/")` 的檔頭取名)

可能的修法:檔名取不到時,改用該段 `diff --git` 行的前半段(`a/X`)與後半段(`b/X`)對稱還原(兩半相同),或直接拿請求的路徑去配這段。

## 已讀,無 finding

- **切開後與單檔 diff 逐位元組相同:** 我用 `git diff` 的批次輸出對照單檔輸出,逐檔比對。檔名含空白、引號、tab、中文,以及刪檔、二進位檔、CRLF 檔、結尾沒換行的檔,全部相同。唯一不同的是上面那條。
- **重複鍵與批次大小:** 同鍵出現兩次的段兩邊都丟掉,再單支重問,行為正確。批次總量與參數長度的上限有擋住。
- **分塊切行:** 我拿舊版 `_note_reread_hunk_nodes` 和新版做差分隨機測試,共 4 萬組:塊大小取 1、3、7、64,檔案內容混入 CR、tab、中文、純標點行和空行。新舊結果差異只出現在「範圍內全是純標點行」,也就是本輪新增的規則。其他情況完全一致。塊邊界只切在 `\n`,所以 CRLF 的 `\r` 和多位元組字元不會被切開。
- **縮排鏈的效能:** 40 萬行加 3000 段改動,新版約 0.5 秒,舊版約 0.34 秒。32 MB 單行檔約 0.02 秒。
- **推主線判定:**
  - `pushed_ref` 在 pre-push 傳的是遠端那一側的 ref,所以 `git push origin feature:main` 會被算成推主線,判定正確。
  - 非 main/master 的預設分支名,靠遠端 HEAD 或 upstream 指到才認得;兩者都沒有時只認固定名。這與設計一致。
  - 刪除主線時 pre-push 的本地 sha 是全 0,會被 hook 跳過;全 0 的遠端舊值也不設 `push_old`。
  - 遠端舊值等於頂端時,`merge-base` 等於頂端,回「在主線上」,走舊版。
  - 強推把主線退回祖先時情況相同。
  - `merge-base` 的回傳碼 0、1、其他三種分得清;`push_old` 在 `fpbase` 快取前設好。
  - prepare 與 check 都在算指紋前呼叫 `_note_reread_push_old`。
- **逾時時的紀錄比對:** `_note_reread_own_fps` 改用整體 deadline 後,指紋這一步逾時也不再讓其他篇的紀錄失效。
- **git 環境:** `main()` 清掉 `GIT_DIFF_OPTS` 和 `GIT_EXTERNAL_DIFF`,並讓 `GIT_GRAFT_FILE` 指向不存在的檔,不影響 `_note_reread_git` 顯式帶的 `--git-dir` 和 `-U3`。
- **資料狀態五問,結論皆無 finding:**
  - 空輸入:`spans` 為空、`n=0`、檔案在範圍結束前就結束,新舊結果一致。
  - 重複:同名段落已處理。
  - 過期或快取:`base["diffs"]` 只留最後一批,缺的重跑,結果不變。
  - 順序:批次取法照指紋實際走的順序。
  - 邊界:塊邊界、純標點範圍、批次上限都測過。

小提醒(不列 finding):批次會把已知「太大」(單邊超過 32 MB)但兩邊合計不到 64 MB 的檔也一起 diff,多花時間和記憶體,但有上限。

最高等級 minor,blocking 0 條。
