C1 [✅] 卸載入口 curl|bash 與裝好後直接跑 `~/.lumos-slim/uninstall.sh` 兩種用法都在檔頭註解列出 | 證據: slim/uninstall.sh:7-9

C2 [✅] main() 內①/①b/②/③/④/⑤各自獨立 if 區塊，皆用 print+bump(n) 記錄，全程無 sys.exit/提前 return 中止流程 | 證據: slim/uninstall.py:214-266(①),268-320(①b),322-361(②),364-413(③),415-422(④呼叫),456-481(⑤)；回歸測試 t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore 實測①拒絕移除仍不擋④還原(scripts/test_lumos.py:16912-16955)

C3 [✅] 先讀 manifest 的 bin_sha256(`_manifest_bin_sha256`)，拿不到才退回 `pkg/scripts/lumos` | 證據: slim/uninstall.py:233-243(`manifest_sha = _manifest_bin_sha256(manifest_path)` → else 分支 `pkg_cli = pkg/"scripts"/"lumos"`)，`_manifest_bin_sha256` 定義於 99-109

C4 [✅] 移除 skill 目錄前用 `.rename(bak)`(mv 語意)非 `rm -rf`，備份落點另移到 `~/.local/share/lumos-slim/backups/`(離開 skills 掃描目錄) | 證據: slim/uninstall.py:353(`skill.rename(bak)`)，334(_bak_root 落點)

C5 [✅] 移除 `~/.lumos-slim` 前檢查 `scripts/lumos` 與 `install.sh` 兩檔皆存在才判定為本包 | 證據: slim/uninstall.py:365(`if (pkg/"scripts"/"lumos").is_file() and (pkg/"install.sh").is_file():`)，不符時印警告+bump(1)於409-411

C6 [✅] 讀 sentinel 區塊，`BACKUP_RE` 抓 FULL-BACKUP 標記；非 NONE 時 base64 解碼還原、NONE 時 restore_text 留空(等於單純挖掉)；install.py 端以 `base64.b64encode(full_text.encode("utf-8"))` 寫入，形成位元組級可逆的編碼往返 | 證據: slim/uninstall.py:145-158(分支邏輯)、73(BACKUP_RE)；slim/install.py:172-173(寫入端 b64encode)

C7 [✅] 還原/挖除後若 `new == ""` 則 `target.unlink()` 整檔刪除 | 證據: slim/uninstall.py:167-169

C8 [✅] 步驟⑤移除 manifest 與空的 `lumos-slim/` 父目錄；唯一資料相依為 bin 未清乾淨時保留 manifest 並印保留原因 | 證據: slim/uninstall.py:456-481(判斷與訊息)，479行印保留原因

C9 [✅] `bin_cleared` 直接查檔案系統實況 `dst_script.exists() or dst_script.is_symlink() or (IS_WIN and (dst_shim.exists() or dst_shim.is_symlink()))`，非分支簿記；shim 檢查確實被 `IS_WIN` 條件包住 | 證據: slim/uninstall.py:451-454(逐字符合)

C10 [✅] manifest `unlink()`(458-463)與父目錄 `rmdir()`(472-477)分屬兩個獨立 try/except；rmdir 失敗只印一句、未呼叫 bump() | 證據: slim/uninstall.py:458-477(對照兩段各自獨立 try block，後者無 bump 呼叫)

C11 [✅] ①b 為與①平行的獨立頂層 `if IS_WIN:` 區塊(非巢狀在①內)；`SHIM_TEXT_RE` 定義於79，比對用 `dst_shim.read_bytes().decode("utf-8")`(非 read_text)於294，不符則拒絕移除並要求 `--force`(314-318) | 證據: slim/uninstall.py:79(regex)，268-320(獨立區塊)，294(read_bytes)，安裝端樣板 slim/install.py:279(`shim_text = f'@echo off\r\n{py_cmd} "%~dp0lumos" %*\r\n'`)兩者對齊

C12 [❌] rc 三段式 0/1/2 大方向與 docstring 一致(39-49)，但 C12 條列的 rc=2 觸發項含「sha256 工具缺失」——這是舊 bash 版行為，Python 版明文聲明用 stdlib hashlib、此失敗模式已不存在(docstring 47-49 自陳「未保留對應分支」)，與 C12 把它列為現行 rc=2 觸發條件之一不符 | 證據: slim/uninstall.py:44-49(docstring 明講此分支未保留)；其餘 rc=1(bin 比對不符/基準缺失/pkg 不像本包)、rc=2(多 sentinel/base64解碼失敗/未捕捉例外)描述屬實，見 141-143,154-156,176-178

C13 [✅] `_restore_claude_md()` 讀寫分開包 try：讀側 `except OSError`(128-130)與 `except UnicodeDecodeError`(131-134)分開接；寫側僅 `except OSError`(176-178)；任一失敗回傳 rc 由 main() bump 彙總，不阻擋步驟⑤ | 證據: slim/uninstall.py:126-134(讀)，166-178(寫)；對應回歸測試 t_slim_uninstall_claude_md_write_failure_does_not_abort_remaining_steps(scripts/test_lumos.py:17206)、t_slim_uninstall_claude_md_read_failure_does_not_abort_remaining_steps(17331)存在

C14 [✅] 舊 bash 版 sha256sum/shasum 判斷邏輯已不存在於現行 uninstall.sh(邏輯已搬空)，Python 版改用 stdlib `hashlib`(58行 import，`_sha256_file`於82-83用`hashlib.sha256`) | 證據: slim/uninstall.py:58-59,82-83；docstring 47-49 明講此為刻意的行為變更

C15 [❌] uninstall.py 承載完整邏輯、uninstall.ps1 具 Invoke-Uninstall/Write-Error -ErrorAction Continue/`$global:LASTEXITCODE = $rc`(非裸 exit)皆屬實；但 uninstall.sh 實際 47 行(43 行非空白)，非主張的「僅 ~30 行」，數量落差達 40-55% | 證據: slim/uninstall.sh 共47行(wc -l)、43行非空(grep -c '.')；slim/uninstall.ps1:16(function Invoke-Uninstall)，23($ErrorActionPreference = "Stop"，函式內第一條可執行陳述式，之前僅 param 宣告與註解)，28(Write-Error ... -ErrorAction Continue)，39-40($rc = ...; $global:LASTEXITCODE = $rc，非裸 exit)

C16 [✅] 全檔僅操作 `~/.local/bin/lumos`、`~/.local/bin/lumos.cmd`、`~/.claude/skills/lumos-project-notes`、`~/.lumos-slim`、`~/.local/share/lumos-slim/manifest.json`(及其 backups/子目錄)、執行目錄下 `CLAUDE.md`；全文搜尋無 settings.json / hooks/ / 其他 skill / 其他專案路徑字樣 | 證據: slim/uninstall.py:185-190(路徑常數)，334/495(backups 路徑)，418(CLAUDE.md via Path.cwd())；508行原始碼自身彙總聲明「未動」清單與此一致

✅12 ❌2 ❓0 ⏭0
