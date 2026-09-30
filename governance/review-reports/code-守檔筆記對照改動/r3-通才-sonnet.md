severity: minor

# 第 3 輪 通才-sonnet 報告:測試有沒有真的守住第 2 輪的修法

方法:在 `--shared` clone 裡把第 2 輪每處修法各自故意改回去(共 22 個改壞版本),只跑對應的測試子集,看翻不翻紅(不跑全套)。未改壞的基線 `-k reread` 122 全綠。新測試沒有碰 `skills/`、`governance/eval/`,消費專案的全套不會因它們變紅。沒有發現修法本身的錯、沒有 blocking。

## 翻紅對照表

| 改壞 | 翻紅的測試 | 結果 |
|---|---|---|
| gov 拿掉 isinstance 物件檢查 | `t_gov_skips_non_object_lines` ①② | 翻紅 |
| `_repo_path_unsafe` 拿掉符號連結層檢查 | `t_note_audit_drift_share_repo_path_guard` ②③ | 翻紅 |
| `_repo_path_unsafe` 拿掉 notdir | 同上 ②③ | 翻紅 |
| `_repo_path_unsafe` 拿掉「解析後跑出 repo」(outside) | 無 | 存活(F1) |
| `_note_audit_safe_dir` 拿掉建好後的再查 | 無 | 存活(F1) |
| 存量漂移帳檔路徑檢查拿掉 outside 分支 | 無 | 存活(F1) |
| Unicode 類別只留 Cc | `t_note_audit_reread_unicode_separator_paths` ①② | 翻紅 |
| 類別拿掉 Cf、拿掉 Zl、拿掉 Zp(各自單獨) | 同上 ①②,三者各自都翻紅 | 翻紅 |
| `_note_reread_show` 不過濾 | 同上 ①② | 翻紅 |
| reread-record 寫帳的訊息路徑不過濾 / 寫帳 nodes 不過濾 / 終端印出不過濾 | 同上 ③,三者各自都翻紅 | 翻紅 |
| prepare 不略過工作目錄裡的紀錄 | `t_note_audit_reread_prepare_skips_uncommitted_records` ①③ | 翻紅 |
| prepare 不講「還沒提交」 | 同上 ①③ | 翻紅 |
| 留痕有效性只看副檔名 | `t_code_loop_bookkeeping_shebang_script_not_exempt` ①③⑤ | 翻紅 |
| 首行改讀磁碟 | 同上 ③④ | 翻紅 |
| 目標版刪掉時不退回讀記錄那一版 | 無 | 存活(F2) |
| 讀不到首行(head 為 None)改成不算程式 | 無 | 存活(F2) |
| 起點那側拿掉 deadline | `t_nodehome_side_deadline_reread_base_side` | 翻紅(起點讀 16 篇、花 4.3 秒) |
| 頂端那側拿掉 deadline | `t_nodehome_side_deadline_reread` ③ | 翻紅 |
| Codex 派法改回雙引號夾內容 | `t_note_audit_reread_prepare_codex_dispatch_stdin` | 翻紅 |

沒有假綠的新測試:每個「修前紅、修後綠」的斷言都確實由字面說的行為驅動(例如 unicode 測試的 ③ 是真的把項目檔頭手改成帶 U+2028、走 reread-record 寫帳、再逐段 splitlines 驗)。

## F1 共用路徑守衛的「解析後跑出 repo」與「建好再查」兩個分支沒有任何測試
severity: minor
blocking: 否
引句:「        return "outside", fp」
佐證行:file: `scripts/lumos:26405`
1. 把 `_repo_path_unsafe` 的 outside 分支整段刪掉、或把 `_note_audit_safe_dir` 建好之後的第二次檢查(註解「建好再查一次(建的途中被換成連結)」那行)改成 `bad = None`,`t_note_audit_drift_share_repo_path_guard` 與 `-k reread_workdir_symlink`、`-k reread_verdict_dir_symlink`、`-k drift_fix_dry_run_lock` 全部仍綠。
2. 為什麼放行:修法本身對(原本兩份守衛都有這兩條、合併後行為沒變),只是缺測試,沒有做出錯的行為;路徑參數目前都是常數(`_NOTE_AUDIT_WORK_DIR` 等),outside 只有含 `..` 的 rel 才走得到,不可由外部輸入觸發。回頭條件:若有呼叫端開始把外部給的路徑傳進來,先補 `_repo_path_unsafe(root, "../x")` 預期 `("outside", …)` 的斷言。

## F2 目標版刪掉時「退回讀記錄那一版首行」的分支測不出有沒有
severity: minor
blocking: 否
引句:「head = blobs[2 * i] if blobs[2 * i] is not None else blobs[2 * i + 1]」
佐證行:file: `scripts/lumos:37997`(`_codeloop_bookkeeping_code` 內;行號為 HEAD 工作樹,凍結 patch 內同一句)
1. 測試 ⑤ 只驗「刪掉的是 #! 腳本 → 不算簿記」。把退回記錄版那一半拿掉(只讀目標版)測試照綠,因為讀不到就保守當程式檔,結果剛好一樣。真正會分辨兩種寫法的是「刪掉的是不含 #! 的一般戳記」:我另寫探針(沒進 repo)確認現行碼回有效(`祖先…簿記豁免`),拿掉退回那半邊則會誤判失效。
2. 同理「讀不到首行一律當程式檔」那個保守方向也沒有測(`head is None` 改成不算程式,全綠)。
3. 為什麼放行:現行行為是對的(探針驗過),拿掉只會變成多擋(誤判留痕失效、要重審),不會放行錯的;屬測試缺口。建議補一條:刪掉 `governance/replay/.weekly-stamp` 後 `_codeloop_record_valid` 仍為有效。

最高等級:minor
