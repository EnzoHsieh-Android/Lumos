# r3 delta 回歸審查(末輪)——check-graph-sync.py / scenario_probe.py

範圍:只看第 2 輪修法的 delta(diff `r3-snapshot.patch`)。方法:實跑重現,不臆測;每條 finding 附從 diff 逐字複製的引句與可重現的驗證。

## (a)(b)(c) 驗收結論(各一行)

- **(a) symlink 指到別處 → 不動目標**:對「`d` 本身是 symlink」這個原重現,修對——實跑 `_stop_block_dir()` 讓 `~/.cache/lumos/stop-block` 是指到 `victim/` 的 symlink,victim 裡的舊檔還在、mode 沒被 chmod、stderr 印停用訊息、不擋。**但同一威脅模型的「上一層目錄是 symlink」沒修到,見下方 finding 1(major)。**
- **(b) ASCII locale 下 block 印不出**:修對。`LANG=C LC_ALL=C PYTHONIOENCODING=ascii` 下實跑整支 hook,stdout 真的送出 `{"decision":"block",...}`(bytes 寫繞過 locale),標記檔留著(名額沒白燒)。
- **(c) 檔名反引號跳出 code span**:修對。直接呼叫 `stop_block_reason(["a`b.py"], ..., {"n`x": ["y`z"]})`,輸出裡的反引號全部配對,檔名段與 mentions 段都套用了新的 `_safe_path`(單引號替換),不會提早收掉 code span。

## Findings

1. **同一威脅模型下,`_stop_dir_ok` 只查葉節點是不是 symlink,父目錄(`~/.cache/lumos`)是 symlink 一樣能繞過——重現:會刪掉別人目錄裡的舊檔。**
   `_stop_dir_ok(d)` 呼叫 `d.is_symlink()`,但 `Path.is_symlink()` 只看路徑最後一段;若 `~/.cache/lumos` 本身是指到別的目錄的 symlink、而 `stop-block` 是那個目錄底下一個真實子目錄,`d.is_symlink()` 回 False,`_stop_dir_ok` 照樣判過關(owner/mode 檢查用的是 `d.stat()`,經過 symlink 解析後看到的是目標目錄的 uid/mode,跟 (a) 修的案例是同一件事,只是攻擊點往上挪一層)。
   實測(HOME 指向臨時目錄,`~/.cache/lumos` → symlink → `attacker_target/`,`attacker_target/stop-block/` 是真實目錄、內含一個 mtime=1(超過 7 天)的檔案 `someones-old-file`):整支 hook 端到端跑完,`someones-old-file` **被刪了**,且在 `attacker_target/stop-block/` 底下留下了本 session 的標記檔 `sess-parentsym`。這正是 (a) 修法要防的同一種傷害(chmod/清理動到不是自己的目錄),只是路徑上多繞一層就繞過了。
   知識圖譜 `Projects/Codex行為精修_計劃.md:128` 記的「標記目錄被換成 symlink(外家 major)」明確只講 `d` 本身被換成 symlink,沒有涵蓋父目錄是 symlink 的情況——不是已知並接受的殘餘風險,是這輪修法沒 cover 到的同類輸入。
   引句:「if d.is_symlink():      # r2 外家:symlink 指到別處=別人的目錄,不信」
   file: `scripts/hooks/claude/check-graph-sync.py:514`
severity: major
blocking: 是

2. **`sys.stdout.buffer` 不存在時的例外路徑**:實測(把 `sys.stdout` 換成沒有 `.buffer` 的 `io.StringIO` 子類直接呼叫 `main()`)——`AttributeError` 被內層 `except Exception` 接住,`mp.unlink()` 把名額退回(事後檢查 `stop-block/` 目錄是空的),`raise` 被外層 `except Exception: pass` 吞掉,照樣落到 `print("\n".join(msg), file=sys.stderr)` 收尾、rc=0。Claude 路徑完全不受影響,因為 `codex_stop_decision` 在 harness≠codex 時第一行就回 False,根本不會進到這段。
   引句:「用 bytes 寫 stdout(不受 locale/ASCII 影響);真寫不出去就把名額退回」
   file: `scripts/hooks/claude/check-graph-sync.py:683`
severity: clean
blocking: 否

3. **`mp.unlink()` 會不會刪到別的 Stop 佔的名額**:標記檔路徑由 `session_id` 決定性算出(`_stop_mark_path`),`_stop_mark_write` 用 `O_EXCL` 保證同一個檔名只有一個行程能建成;例外分支裡重算的 `mp` 是「這次呼叫自己剛建成的那個檔」,不會有第三者把同名檔重新建起來讓 unlink 誤刪(O_EXCL 讓建立本身互斥,不存在的檔不會被搶建)。沒找到可重現的跨行程誤刪路徑。
   引句:「mp.unlink()」
   file: `scripts/hooks/claude/check-graph-sync.py:688`
severity: clean
blocking: 否

4. **`_stop_block_dir()` 新增的 stderr 停用訊息含 `{d}`(家目錄路徑)——會不會進到模型可見通道**:不會。這行只在 `codex_stop_decision` 已經確認 `harness == "codex"` 且往下呼叫 `_stop_mark_write → _stop_mark_path → _stop_block_dir` 時才可能觸發;Claude 路徑(stderr 對模型可見)永遠不會走到這裡,因為 `codex_stop_decision` 一開始就短路回 False。而檔案自己的頂部文件也寫明「stderr 對 Codex 模型是零訊號」——跟這行程式碼要送到的受眾(log/人)一致。
   引句:「lumos 收工擋停停用:標記目錄 {d} 不是自己的 0700 目錄」
   file: `scripts/hooks/claude/check-graph-sync.py:494`
severity: clean
blocking: 否

5. **`_codex_home_dir()` 退回預設與 `scripts/lumos` 的 `_codex_home()` 語意是否一致(含 `CODEX_HOME=""` 邊界)**:一致。兩邊都用 `if env:`(truthy)判斷,`CODEX_HOME` 設成空字串時兩邊都落回 `Path.home() / ".codex"`;呼叫時機也對得上(`mod._codex_home()` 無參數呼叫,例外分支的 fallback 同樣不帶 `home` 參數)。
   引句:「CODEX_HOME 退用預設:{type(e).__name__}」
   file: `scripts/scenario_probe.py:241`
severity: clean
blocking: 否

6. **測試 ⑲⑳㉑ 是否真的會在修法拿掉時翻紅**:三個都會。逐一把對應修法還原成 r1 版本(symlink 檢查拿掉、`_safe_path` 拿掉單引號替換、bytes 寫改回 `print`)後單獨重跑對應的斷言:
   - ⑲(symlink):還原後 `victim` 裡的舊檔被刪、hook 仍舊 chmod 進去,`old.exists()` 回 False,斷言翻紅。
   - ⑳(反引號):還原後 `stop_block_reason` 輸出裡殘留裸反引號(`` `a`b.py` ``、`` `n`x`→`y`z` ``),斷言翻紅。
   - ㉑(ASCII stdout):還原後在 ASCII locale 下 `print()` 對 UnicodeEncodeError 沒有防護,stdout 空、rc 落到例外路徑,且**名額真的白燒**(標記檔留下但沒有輸出)——跟任務描述的原始症狀一致,斷言翻紅。
   三個測試都是有效的回歸守衛,不是空判準。
severity: clean
blocking: 否

## 小結

第 2 輪要修的 (a)(b)(c) 三個原始重現都驗證修對,回歸測試也都能在修法拿掉時翻紅。唯一的新洞是 finding 1:`_stop_dir_ok` 的 symlink 檢查只查了 `d` 這一層,父目錄(`~/.cache/lumos`)是 symlink 時整套信任檢查形同虛設,而且用同一支函式的 `_stop_mark_write` 也會被一起繞過——這正是這輪 review 標題「同一個 fix 只修了審查員給的那個重現、沒修到同類」要抓的那種漏洞,已用端到端重現證實(刪掉了目標目錄裡一個不相干的舊檔)。其餘四項新洞检查(stdout.buffer 缺失、mp.unlink 競態、stderr 家目錄洩漏、`_codex_home_dir` 語意對齊)都驗證乾淨,沒有可重現的問題。

max severity: major
