severity: major

## 發現1

severity: major

引句:「def cross_check(files, mem_stems, tally):」

觀察到什麼:

這一輪的處置②(「先數再讀」)只改了 `_list_memory_files()`/`read_memories()` 這一段——先用 `os.scandir` 列檔名、數到 `MAX_SCAN` 就停,超過 `MAX_FILES` 當場記喊聲、只讀排序前 300 篇。docstring 自己講得很清楚,目標是消掉 r8 那個「讀檔太久,喊『結果不完整』之前就被外層 12 秒逾時 SIGKILL,從『不完整但有喊』變成『完全不出聲』」的洞。

但 `main()` 裡在 `sweep()` 之後緊接著跑的 `cross_check(files, {f.stem for f, _ in files}, tally)`,函式簽章完全沒有 `deadline` 參數,內部(`cross_check` / `shadow_copies` / `pointer_problems` / `_claims_near`)也沒有任何一行呼叫 `time.monotonic()` 或檢查預算——它是這支 hook 裡唯一一段**結構性完全不受節流**的路徑,而且就是題目點名要看的「跟圖譜對帳那段」。它的成本不是取決於檔案「數量」(已被 r9 壓到 300 篇),而是取決於檔案「內容大小」:`pointer_problems()` 對每篇檔都跑 `linked = {_stem(n.split("/")[-1]) for n in _LINKED_REF.findall(scan)}`,`scan` 是整份檔案文字(未截斷),`_LINKED_REF.findall` 會把文字裡每一個 `[[...]]` 都配對進一個 list 再收集成 set——所以一篇檔案只要塞滿大量重複的 `[[Systems/foo]]` 這種假連結,配對數量就會隨檔案位元組數線性成長,而且這件事發生在 300 篇讀取上限**之內**的單一篇檔案裡,不會被 `MAX_FILES`/`MAX_SCAN` 攔到。

實測(把 memory-sweep.py 當模組載入,在暫存目錄造一篇合法開頭欄位、body 塞滿重複 `[[Systems/foo]]` 的記憶檔,模擬真正的 hook 執行順序 `read_memories → sweep → cross_check`):

```
file size: 240.0 MB   (單一檔案,body = "[[Systems/foo]] " * 15_000_000)
read_memories=0.05s sweep=0.26s cross_check=15.18s TOTAL=15.49s (outer SIGKILL budget=12s)
```

`read_memories`(這次修的那段)只花 0.05 秒——r9 的處置在這裡確實有效;但 `cross_check` 單獨就吃掉 15.18 秒,整支流程總計 15.49 秒,已經超過這支 hook 在 `scripts/merge-claude-settings.py` 裡真實註冊的逾時(`HOOK_BUDGET["memory-sweep.py"] = 12`,同時是 `--budget 12` 與外層 SIGKILL 時限)。追查 `_hookevent.guard`(`scripts/hooks/claude/_hookevent.py`)只是在 `main()` 外面包一層記帳,並沒有自己用 signal/thread 做內部逾時保護——真正砍它的仍是外層 Claude Code 對子行程的逾時 SIGKILL,檔頭註解自己也承認「繞過 try/except」。

會造成什麼:
在題目給的威脅前提下(攻擊者沒有本機帳號,只需要讓一篇 `.md` 落進記憶目錄,例如靠提示注入讓 Claude 寫一則塞了大量重複假連結的「筆記」),單一篇檔案就能讓整支 SessionStart hook 在還沒跑到 `_emit()`、也就是喊出「這輪只驗了前 300 篇,結果不完整」之前,先被外層 SIGKILL——結果是**完全沒有任何報告印進對話**,連 flood 警告本身都出不來。這正是 r9 兩條處置合起來宣稱已經「結構性歸零」的那個失敗模式(「不完整但有喊」退化成「完全不出聲」),只是觸發路徑從「檔案數量太多」換成「單一檔案裡塞重複連結」,而 r9 的修法完全沒有涵蓋到這第二條路徑。且門檻遠比檔案數量攻擊低很多——不需要製造大量檔案(那需要攻擊者自己付出可觀的建檔時間,實測用 hardlink 灌 50 萬個檔名超過 120 秒都灌不完),只需要一篇幾百 MB、內容高度重複的筆記,這種大小透過幾次對話裡的貼上/累積寫入是完全可行的。

建議怎麼修:
`cross_check()`(以及它呼叫的 `shadow_copies()`/`pointer_problems()`)要接住跟 `sweep()` 共用的同一個 `deadline`,在逐檔迴圈裡比照 `_sweep_one()` 的作法,時間到就記進 `tally.skipped`/`unfinished` 提前跳出,而不是讓它成為整支 hook 唯一沒有時間閘的段落;另外 `_LINKED_REF.findall(scan)`、`_STATUS_WORDS.findall(body)` 這類對「整份檔案原文」做的正則掃描,應該先對 `scan`/`body` 做位元組數上限截斷(例如只取前幾十 KB——合法的人寫筆記不會有一篇幾百 MB),而不是無條件對整份內容跑正則,這樣才能讓「跟圖譜對帳」這段的成本跟檔案位元組數脫鉤,回到跟 `read_memories()` 修完之後一樣「在預算內穩定跑完」的狀態。

## 已確認

- 處置①(拿掉 `file-exists`/`no-file` 整類檢查)確實生效:`CHECKS` 字典裡已無這兩個鍵,`_safe_path`/`_chk_file_exists`/`_ALLOWED_ROOTS` 整支函式都已從檔案移除(`hasattr` 逐一查證皆為 `False`),舊寫法會被 `_block_line` 收成 `?file-exists`/`?no-file`、由 `why_unknown()` 報成「檔案在不在的檢查已經拿掉」,不會靜靜消失也不會被當成新的探測入口;`scripts/test_lumos.py` 的 t_memory_sweep_core ⑮ 三案例與整支子集(46 項)本機重跑全數通過。另外查過目前僅存的五種檢查型別(`pushed`/`not-pushed`/`installed`/`not-installed`/`before`)裡唯一還碰檔案系統的 `installed`(`shutil.which`),參數先過 `_NAME_RE`(`^[A-Za-z0-9._-]{1,64}$`,不含 `/`)白名單,只能查 PATH 目錄下有沒有「這個名字的可執行檔」,無法拿它當任意路徑(如 `~/.ssh/id_rsa`)存不存在的探測器,沒有留下等效的替代洞。
- 處置②要解掉的具體案例(r8 資安席原始情境:記憶目錄灌大量 `.md` 檔,`read_memories()` 讀檔耗時逼近逾時)已經修好:實測目錄裡混入 30 萬個非 `.md` 雜訊檔加真檔,`_list_memory_files()` 全程 0.17 秒;目錄裡放超過 `MAX_FILES` 篇合法 `.md`(用 300+7 篇跑 `scripts/test_lumos.py` ㉒ 案例)時只會打開排序前 300 篇、喊聲在讀檔階段就先記下,不必等到 `sweep()` 才裁切,行為與檔頭註解描述一致。
