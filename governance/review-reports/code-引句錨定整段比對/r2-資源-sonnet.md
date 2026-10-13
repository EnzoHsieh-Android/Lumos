severity: major

1. 比較模式讀檔沒有大小上限,一個大檔就吃掉數 GB 記憶體並拖數分鐘
severity: major
blocking: 是
引句:「            return fp.read_bytes().decode("utf-8")」
file: `scripts/lumos:26709`
- 輸入:帳上某列 `report_path` 指到 repo 內的一個大型一般檔。路徑修補只檢查在 repo 內和是一般檔,沒有檢查大小。
- 實測:我在實驗目錄放了 3GB 的全 NUL 稀疏檔(合法 UTF-8)。`_quote_compare_rules` 跑了 143 秒,峰值 RSS 約 5.5GB,最後把它算成「零引句」。
- 原因:`read_bytes()` 先整檔進記憶體,`decode` 再複製一份,之後 `_quote_norm` 還會再複製。
- 如果是更大的檔,會在 `read_bytes` 丟出 `MemoryError`。`_read` 只接 `OSError`、`UnicodeDecodeError`、`ValueError`,所以例外直接冒出,整份比較表連已算好的計數都不印。
- 這條修補的目的是讓壞帳列不拖垮整份報表,但漏掉了「大」這個維度。
- 建議:先看 `st_size` 並設上限,超過就算「讀不到」。報告和快照都該設。

2. 比較模式 `is_file()` 與 `read_bytes()` 之間被換成管線,整支指令永久卡死(TOCTOU)
severity: minor
blocking: 否
引句:「            if not fp.is_relative_to(root_real) or not fp.is_file():」
file: `scripts/lumos:26706`
- 實測:我在 `Path.is_file` 回傳 True 之後,把 `docs/r.md` 換成 FIFO,再讓 `_quote_compare_rules` 繼續跑。它卡在 `read_bytes()` 的 open,8 秒的 SIGALRM 才殺掉(rc=142)。
- 上一輪補丁的註解寫「管線、裝置檔一律當讀不到」,這只在檢查當下成立。
- 同一個空檔也能把檔換成指向 repo 外的符號連結。`resolve()` 已經跑完,`read_bytes` 會跟著連結走,repo 內限制就被繞過了。內容不會印出,只會被計入計數。
- 威脅模型是單人、依序操作,需要別的程序在毫秒級時間窗內動檔案。所以我只給 minor。
- 若要真擋,用 `os.open(..., O_NONBLOCK|O_NOFOLLOW)` 加 `fstat` 檢查 `S_ISREG`,再用 fd 讀,可以同時解決這條和第 1 條(`fstat` 的大小)。

3. 處置閘讓 MemoryError 往外丟,`loop next` 因此崩潰,沒有結構化輸出
severity: minor
blocking: 否
引句:「                        except MemoryError:      # 資源不足不是判準的錯,照常往外丟」
file: `scripts/lumos:26528`
- 回放(`--golden`):`cmd_loop_replay` 沒有接這個例外,traceback 後 rc=1。判定是紅的,沒有假綠。但週跑看到的是堆疊,不是「邏輯漂移」那條訊息。我沒有直接看到週跑的呼叫點,⚠ 這部分是推論。
- `loop next`:第 15691 行在 `redirect_stdout/stderr` 裡代問處置閘。例外冒出時 `buf` 內已印的診斷全丟掉,呼叫端拿不到 `emit(...)` 的階段輸出,只有 traceback。修補前它會被當成判失敗,最後走 `plant-canary`。
- `_cli()` 只接 `WriteBlocked`,所以沒有任何一層把它轉成可讀的「擋下」。
- 退出碼仍非零,不會誤放行。所以只是可用性問題。
- 對照:`_quote_block_note` 內求另一版判準的那段是 `except Exception`,會把 `MemoryError` 吞成 `kind=unknown`。兩處對 MemoryError 的態度不一致。寫側擋下仍照舊,影響很小。

4. 舊判準對未閉合引號有二次方成本,現在多了一個入口(比較模式)
severity: minor
blocking: 否
引句:「            a = _quote_rows(rtext, stext, rule="legacy")」
file: `scripts/lumos:26741`
- 實測:報告含 20000 個 `引句:「` 且都沒閉合(約 140KB),legacy 判準耗時 4.47 秒,full-span-v1 只要 0.02 秒。
- legacy 函式要求「一字不改」,所以我不要求改它。
- 比較模式要對帳上每份報告各跑一次 legacy。若審查席交回含大量未閉合標籤的報告,整份比較表會變慢,量級跟報告長度的平方成正比。
- 處置閘本來就有同樣的暴露,這裡只是多一條路徑。

已查過、沒問題的地方
- full-span-v1 對深層巢狀(10 萬層)和 5 萬條引句都是線性,0.01 到 0.17 秒。
- 寫側擋下事件寫入失敗:`_gate_event_or_warn` 只印 stderr 警告,不改判定,擋下 rc2 照舊。
- `_quote_block_note` 內 `_sha256_file` 的 `OSError` 有接。
- 引句片段濾掉 Cc/Cf 並排到 note 最後,片段裡偽造的 `report=`、`id=` 不會被讀者先取到。

實驗目錄已刪除,沒有改動 repo。

總結:最高等級 major,blocking 共 1 條
