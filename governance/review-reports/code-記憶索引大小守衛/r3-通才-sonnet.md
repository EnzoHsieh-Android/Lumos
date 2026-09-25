severity: major

## F1 量索引大小時,fstat/read 拋出的 OSError 沒接住,會吃掉同一次開場已經算出來的其他發現
severity: major
blocking: yes

`_index_bytes`(scripts/hooks/claude/memory-sweep.py:386)只在 `os.lstat` 和 `os.open` 兩處包了 `try/except OSError: return None`,中間的 `os.fstat(fd)` 和 `fh.read(...)` 沒有包。改之前的版本是 `p.read_bytes()` 整段包在 `try/except OSError: return None` 裡,任何讀檔失敗(檔案被刪、磁碟 I/O 錯、網路磁碟機逾時)都會靜靜回 None,不影響其他檢查。

引句:「st = os.fstat(fd)」
引句:「raw = fh.read(MAX_BYTES + 1)」
引句:「with os.fdopen(fd, "rb", closefd=False) as fh:」

問題不只是這支函式本身沒接住,呼叫端也沒補這個安全網:`main()`(同檔 934 行起)是先算 `tally`、`crossed`,最後才呼叫 `size_note = index_size_note(here)`,然後才呼叫 `_emit(...)` 把 `tally`/`crossed`/`size_note` 一起印出來。如果 `index_size_note` 在這裡拋出例外,`_emit` 根本不會被呼叫——等於這次開場前面已經抓到的記憶清掃真發現(tally.changed、crossed 等)全部被吞掉,不只是量索引大小這件事失敗。雖然最外層 `if __name__ == "__main__":` 有 `except Exception: sys.exit(0)` 做 fail-open,不會讓 session 掛掉,但「這次開場原本該講的話全部講不出來」是比原設計更大的影響範圍,而且是靜默的,使用者不會知道。

對照:讀真正的記憶檔那條路徑(`_read_own_file`,656 行)雖然內部一樣沒包 `os.fstat`,但它的呼叫端(`read_memories`,約 640 行)有 `try: ... except (OSError, UnicodeDecodeError): tally.broken += 1; ...; continue`,把單一檔案的例外攔在那一篇,不會波及其他檔案或其他檢查。`_index_bytes`/`index_size_note` 這條新路徑複製了讀檔的手法,但沒有複製這層攔截。

重現步驟(已在 exp-r3 跑過,單獨呼叫 index_size_note 可重現例外會往外傳):
```python
import importlib.util, os, tempfile, pathlib
spec = importlib.util.spec_from_file_location("ms", "scripts/hooks/claude/memory-sweep.py")
ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
d = pathlib.Path(tempfile.mkdtemp())
(d / "MEMORY.md").write_text("- [x](y.md) — hi\n", encoding="utf-8")
orig = os.fstat
os.fstat = lambda fd: (_ for _ in ()).throw(OSError(5, "simulated I/O error"))
ms.index_size_note(str(d))   # 拋出 OSError,沒有被接住
os.fstat = orig
```
建議修法:在 `_index_bytes` 的 `try/finally` 外面再包一層 `except OSError: return None`(比照舊版 `p.read_bytes()` 的行為),或在 `main()` 呼叫 `index_size_note` 的地方加一層 try/except,確保這條路徑失敗時不會波及已經算好的 tally/crossed 顯示。

已看,無:`_opened_reason` 加 `max_bytes` 參數後,原本讀記憶檔那個呼叫點(683 行 `_opened_reason(os.fstat(fd), pre)`)用的是預設值 `MAX_BYTES`,行為跟改之前完全一樣,沒有變。`_index_bytes` 呼叫時傳 `max_bytes=None`,只是把單篇上限的判斷關掉、交給 `_index_bytes` 自己在 `if st.st_size > MAX_BYTES` 那行處理,邏輯上跟舊版「量大小只看 stat、不讀內容」的意圖一致,已用 114600 bytes(超過 64KB 單篇讀取上限)與 21/24/25 KB 等多個邊界值實跑驗證過,數字與訊息都正確;25 KB/1024 底的换算(`_INDEX_MAX_BYTES = 25 * 1024`、顯示用 `/1024`、`//1024`)也重跑過,25732 bytes 的案例算出「25.1 KB」「上限 25 KB」,符合預期,沒有 r2 抓到的 1000/1024 混用問題殘留(全檔已無 `/1000` 或 `// 1000` 用法)。fd 沒有漏關:`_index_bytes` 每個提早 return 都在 `try/finally` 裡,`finally: os.close(fd)` 一定會跑,`os.fdopen(fd, ..., closefd=False)` 不會造成重複關閉。符號連結、硬連結、換檔攻擊(檢查與打開之間被換掉)三種情境都用實際測試(t_memory_sweep_index_size 的 ⑤⑦)跑過並確認防護生效。八個測試案例(①–⑧)全部實際跑過都綠(`python3 scripts/test_lumos.py -k memory_sweep_index_size`,8 passed);另外把相關的 74 支 memory_sweep 測試整組跑過也全綠,沒有波及其他行為。測試檔標注的「翻紅釘」逐條拆掉驗證:「改回直接讀檔 → ⑤⑦紅」屬實(已重現);「上限改回 1000 底 → ⑧紅」屬實(已重現,順帶也讓②紅,屬預期內的額外覆蓋);但「拿掉大小檢查 → ②③④⑥紅」這句話對應到 `_index_bytes` 裡 `if st.st_size > MAX_BYTES: return st.st_size, None` 這行時並不成立——實際拿掉這行重跑,8 個案例仍全部綠,因為 `fh.read(MAX_BYTES + 1)` 本來就已經把讀取量上限鎖在 64KB+1,函式最後一行 `(len(raw), None) if len(raw) > MAX_BYTES else (len(raw), raw)` 這個保底判斷會接手把超大檔案判成「只回大小、不回內容」,只是回報的大小會被讀取上限截斷成約 64KB 而不是檔案真正的大小(不影響本次測試斷言,因為測試只檢查文字裡有沒有「遠超過」,沒檢查具體公斤數)。這只是測試文件裡的翻紅釘敘述沒對準真正保護測試通過的那一行,不是功能缺陷,不影響本次判定,但如果之後有人真的把這行早退邏輯整段刪掉並信任這句「翻紅釘」描述去核對覆蓋率,會誤以為测试失去保護。
