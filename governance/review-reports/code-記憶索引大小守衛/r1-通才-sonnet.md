severity: major

## F1 `index_size_note` 直接讀 MEMORY.md,沒有套用這支檔對其他記憶檔一貫的符號連結/大小防護
severity: major
blocking: yes

引句:「raw = p.read_bytes()」引句:「p = pathlib.Path(here) / "MEMORY.md"」

```
def index_size_note(here):
    """量記憶索引的大小;沒到提醒線回 None。只讀、不寫。"""
    p = pathlib.Path(here) / "MEMORY.md"
    try:
        raw = p.read_bytes()
    except OSError:
        return None
```

這支檔案對「記憶檔」的讀取有非常刻意、經過十幾輪代碼審才收斂的防護鏈(`_read_own_file`):lstat 擋符號連結、O_NOFOLLOW、fstat 比對 inode 防換檔、`MAX_BYTES = 64 * 1024` 硬上限(註解直接寫「r9 資安席 major:一篇 240MB 的檔讓對帳那段跑 15 秒」)。這些防護明確地就是為了「這個目錄底下的檔」而設計的。

新增的 `index_size_note` 讀的正是同一個目錄底下的 `MEMORY.md`(這支檔本身也在 `_list_memory_files` 裡特別提一句「索引檔 MEMORY.md 不算記憶檔」,可見它清楚知道 MEMORY.md 屬於這個目錄的特殊檔),但用的是 `pathlib.Path.read_bytes()`:
- 會跟隨符號連結(其他所有記憶檔讀取路徑都明確拒絕)。
- 沒有任何大小上限——多大都整包讀進記憶體再 `.count(b"\n")`。

實測(在 exp-g 複本裡,不是真 repo):把 `MEMORY.md` 換成指向 1.5MB 檔案的符號連結,`--quiet` 模式照樣把該檔的大小/行數算出來、包成 `additionalContext` 印出去,完全沒有被擋掉、也沒有出現其他記憶檔遇到超過 64KB 時會有的「不讀」訊息:

```
$ ln -sf big.md MEMORY.md   # big.md 1.5MB
$ python3 memory-sweep.py --dir t2 --quiet
{"hookSpecificOutput": {... "additionalContext": "...記憶索引 MEMORY.md 現在 1500.0 KB、1 行...★快被截掉了...★..."}}
```

風險兩塊:
1. **資源**:MEMORY.md 理論上應該一直是 Claude Code 自己維護的小索引檔,但如果它因為任何原因(bug、同步工具、有人手動接了東西)變得很大,這支 hook 會在**每次開場**整包讀進記憶體,而不是像其他檔一樣直接擋掉、報「超過上限不讀」。跟這支檔自己反覆強調的設計原則(先量大小再讀、不要無上限讀)不一致。
2. **符號連結**:如果攻擊者已經能在這個記憶目錄裡放檔案(前提本來就跟污染其他記憶檔一樣高),他可以把 `MEMORY.md` 換成指向任意大檔案的符號連結,讓 hook 讀出並印出該檔的大小/行數(僅限資訊揭露,不含內容,因為訊息文字是寫死的,只有數字會變)——這條路徑是這支檔明確花了好幾輪代碼審才堵掉的洞,新函式完全繞過。

**blocking: yes** 的理由:這不是新洞,而是明確違反同一支檔案裡已經定案、且有多輪審查紀錄的安全慣例(讀記憶目錄下的檔一定要走符號連結防護與大小上限),屬於同類重複發生應該擋下的形狀。建議修法:讓 `index_size_note` 走跟 `_read_own_file` 一樣的 lstat/O_NOFOLLOW/大小上限檢查(或至少共用同一段防護邏輯),超過上限就回報「MEMORY.md 太大量不出來」而不是硬讀。

已看,無:
- **輸出組合(quiet/非 quiet ×有無其他發現)與安全框**。引句:「tail = nxt + ("\n" + size_note if size_note else "")」引句:「_frame_injected(msg) + tail if msg else size_note」。實際跑過以下組合,行為都符合預期:quiet、無其他發現、只有 size_note → JSON 正確包裝,`additionalContext` 就是 size_note(無框,因為 size_note 只含工具自己量出來的數字與寫死文字,不含記憶檔內容,符合 hook信任邊界的「工具寫死的指示放框外」);quiet、有其他發現(`stale`)+ size_note → 發現內容在框內,`nxt` 與 `size_note` 都正確排在框外、且順序是 `nxt` 在前、`size_note` 在後;非 quiet(手動)模式同上兩種組合,框線邏輯一致;`--budget`(走 `_watchdog` 外層子行程)路徑 size_note 正確從子行程轉印出來;`_watchdog` 超時分支呼叫 `_emit(tally, False, quiet, here)`(不帶 size_note)——這是對的,子行程都被砍了,量不到、也不該量。
- **邊界值(80%/95% 門檻、空檔、無結尾換行、非 UTF-8、讀不到、目錄)**。引句:「if max(b_ratio, l_ratio) < 0.8:」引句:「raw.count(b"\n") + (1 if raw and not raw.endswith(b"\n") else 0)」。逐一跑過最壞輸入:剛好 20000 bytes(=80%)→ 出聲(提醒);19999 bytes → 不出聲,邊界正確、沒有差一個位元組;剛好 23750 bytes(=95%)→ 出現「快被截掉了」大聲版,邊界正確;空檔(0 bytes)→ 兩個 ratio 都是 0,回 None,不出聲,不會除以零或拋例外;沒有結尾換行的檔 → 行數計算有把最後一行補回來(`+1`),不會少算一行;非 UTF-8 內容(`b"\xff\xfe" + ...`)→ 全程只用 bytes 操作,不 decode,不會炸 `UnicodeDecodeError`;MEMORY.md 不存在/是目錄/沒有讀取權限 → 全部落在 `except OSError: return None`,不出聲、不炸例外。
- **測試會不會真的對 bug 翻紅**。跑了 `t_memory_sweep_index_size`,四個子案例全過;接著把 `main()` 裡 `size_note = index_size_note(here)` 改成 `size_note = None`(模擬拿掉這個守衛)重跑,②③④三個子案例如預期翻紅(①原本就該不出聲,維持過)。測試檔自己寫的翻紅釘「拿掉大小檢查 → ②③④紅」屬實。另外把整個 memory-sweep 相關測試(`-k memory_sweep`,70 案例)全跑一遍,既有行為(符號連結防護、硬連結、灌水檔上限、看門逾時等)全部維持綠燈,沒有因為這次改動被破壞。
- **圖譜筆記與程式碼是否一致**。`docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md` 新增的 RULE 行(`[since:2026-09-25] [retire:...] [confirmed:2026-09-25] [test:t_memory_sweep_index_size]`)四個欄位都齊,測試名稱與實際新增的測試函式名一致;文件裡引用的「20.8 KB / 95 行」跟目前這台機器真實的 `~/.claude/projects/-Users-enzo-harness-lumos-toolchain/memory/MEMORY.md`(95 行、20824 bytes ≈ 20.8 KB)吻合,不是編出來的數字;「放框外」的設計說明(索引大小的訊息是工具自己量出來的數字加寫死指示)跟程式碼實際行為一致。
