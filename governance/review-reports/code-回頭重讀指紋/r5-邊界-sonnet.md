severity: minor

兩條 finding 都不是 major。我只刪了自己建的 `cr-rf5-邊界/`。工作樹 `reread-fp` 沒動,突變實驗都在 `--shared` clone 裡做,已隨資料夾刪掉。

**已讀,無 finding 的部分**
- 分塊切行(`_note_reread_line_blocks`):塊大小 1、2、3、7 下,以含 `\n`、`\r`、UTF-8 多位元組的隨機位元組各 3000 組比對,接起來都與 `data.split(b"\n")` 逐行相同。CRLF、只有 `\r`、結尾有沒有換行都沒錯位。
- 縮排鏈新演算法(`_note_reread_hunk_nodes`):我另寫了一份照註解規則的獨立參考實作,用 4000 組隨機輸入(含純標點行、tab、中文、`\r`、範圍超出檔尾、n=0)比對。0 組不一致。
- 切檔頭(`_note_reread_split_diff`):以下檔名在批次切出的片段,與單獨問 git 的輸出逐位元組相同。
  - 含 ` b/`、`\t`、`"`、換行、反斜線。
  - 結尾空白、`\x01`、NFD 的 `é中`、中文。
  - 檔名內含 `diff --git a/z b/z` 字樣。
  - 一般文字改動、二進位檔。
  - 非 UTF-8 檔名在 macOS 建不出來,沒測到。
- 推主線判定邊界:`refs/heads/main`、`main2`、大小寫的行為符合設計。`main2` 與 `Main` 不在集合內,按功能分支走;遠端名、網址不再參與判定。

severity: minor
blocking: 否 — 只會退回舊版指紋(偏嚴),不會多放行;檔名要同時是「純改權限、空檔或二進位」又含 ` b/` 才觸發
引句:「return (one[0][slice(*one[1][path])] if path in one[1] else b""), None」
問題:`_patch_file_changes` 對沒有 `---`/`+++` 的檔頭(只改權限、新增空檔、二進位),檔名取自 `diff --git` 那行的最後一個 ` b/`。路徑含 ` b/` 時取到錯的名字。舊做法逐檔問 git,名字取錯也照樣用整段輸出算指紋。新做法依名字查 spans,查不到就回 `b""`,算成「diff 空」並退回 v1。
具體失敗情境:
- 檔 `x b/y2` 只改 mode(chmod +x)。實測切出的名字是 `y2`,不是 `x b/y2`,所以該檔從原本有 v2 指紋變成「diff 空」。
- 使用者主線前進後這篇筆記會多一次誤擋。
- 另有未實測的風險:`x b/y2` 的 span 被掛在假名 `y2` 之下。若同名真檔 `y2` 在 `got` 只留最新一批的狀況下被查,可能拿到別支檔的片段。前提很窄:`y2` 不在當批、沒被快取,又被查到。
- 佐證:``file: `scripts/lumos:36495` ``(`_note_reread_fp_diff` 單支重問後回 `b""`)、``file: `scripts/lumos:36559` ``(`_note_reread_split_diff` 以 `_patch_file_changes` 的名字當鍵)
- 修法方向:`len(batch)==1` 或單支重問時,不依名字查 spans,整段輸出直接給這一支用。

severity: minor
blocking: 否 — 守衛行為本身正確,只是測試鬆,屬測試覆蓋缺口
引句:「_NOTE_REREAD_MAINLINE_NAMES = ("main", "master")」
問題:推主線判定的新測試沒釘邊界。我在 clone 裡同時做三處突變:把 `master` 從固定名拿掉、拿掉 `refs/heads/` 前綴檢查、改用 `split("/",2)[-1]` 取名,再清 `__pycache__` 跑 `-k reread_fp`,結果 `180 passed, 0 failed`,突變全存活。
- 沒有測試推 `master`、`refs/tags/main` 或 `main2`。
- 另一個單獨突變(整個判定改成 `if False:`,即所有推送都當推主線)只被 `t_reread_fp_feature_push_lookup_fail_no_block` 的「前置:替身觸發過」紅掉。這條是前置斷言碰巧抓到,沒有直接驗功能分支不改用遠端舊值當分岔點。
- 佐證:``file: `scripts/test_lumos.py` ``(patch 內的 `t_reread_fp_mainline_alias_remote_blocks`、`t_reread_fp_fork_remote_main_uses_old`、`t_reread_fp_feature_push_lookup_fail_no_block`)
- `t_reread_fp_one_diff_for_all_files` 只測空白與中文檔名。引號、tab、換行、純 mode 改動、二進位、`ARGLEN` 分批都沒測。檔名多樣性是我上面手動驗過的,但測試沒釘。

最高等級 minor,blocking 0 條。
